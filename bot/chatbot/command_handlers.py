import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import aiohttp
import asyncio
import dotenv
import os
from .gpt_api import get_answer_from_gpt_3_5
from .db_api import User, Message, Conversation 
from .utils import CurrentConversation, user_checker_decorator, check_creating_conversation, get_callback_data, NewCoversation
from .buttons import ButtonBuilder
from .callback_handlers import callback_options

dotenv.load_dotenv()

DB_API_URL = os.getenv('DB_API_URL')
with open('messages.json', 'r') as f:
    MESSAGES = json.load(f)


@user_checker_decorator(with_message=True)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=MESSAGES['start']['message'])


@user_checker_decorator(with_message=False)
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if NewCoversation.get_new_conversation_is_being_created(context):
        tasks = []
        tasks.append(asyncio.create_task(update.message.reply_text(MESSAGES['conversation']['creating'])))
        tasks.append(asyncio.create_task(Conversation(update.effective_user.id).create_conversation(conversation_name=update.message.text)))
        await asyncio.gather(*tasks)
        conversation = tasks[1].result()
        if conversation:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=MESSAGES['conversation']['created'])
            context.user_data['current_conversation'] = conversation['id']
        context.user_data['is_creating_conversation'] = False
        return
    current_conversation = await CurrentConversation(update, context).get_or_create_current_conversation()
    conversation = await Conversation(update.effective_user.id).get_conversation(current_conversation)
    save_message = asyncio.create_task(Message(update.message.text, current_conversation, update.effective_user.id).create_message(role='user'))
    get_answer_from_gpt_3_5_task = asyncio.create_task(get_answer_from_gpt_3_5(update.message.text, conversation))
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Получаем ответ от GPT-3.5...')
    await get_answer_from_gpt_3_5_task
    message_answer = get_answer_from_gpt_3_5_task.result()
    save_message_answer = asyncio.create_task(Message(message_answer, current_conversation, update.effective_user.id).create_message(role='assistant'))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_answer)
    await save_message_answer
    await save_message
    if not save_message.result() or not save_message_answer.result():
        context.bot.send_message(chat_id=update.effective_chat.id, text='Произошла ошибка при сохранении данных в базу данных. Ваш диалог не сохранен.')


async def get_conversations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conversations = asyncio.create_task(Conversation(update.effective_user.id).get_conversations())
    new_conversation_button = ButtonBuilder(name=None, id=None).build_conversation_create_button()
    new_conversation_button_message = asyncio.create_task(context.bot.send_message(chat_id=update.effective_chat.id, text='Создать диалог:', reply_markup=InlineKeyboardMarkup([[new_conversation_button]])))
    current_conversation = CurrentConversation(update, context).get_current_conversation()
    if current_conversation:
        text = f'Текущий диалог: {current_conversation}'
    else:
        text = 'У вас нет текущего диалога.'
    current_conversation_message = asyncio.create_task(context.bot.send_message(chat_id=update.effective_chat.id, text=text))
    await asyncio.gather(conversations, new_conversation_button_message, current_conversation_message)
    if conversations.result():
        list_of_conversations = []
        for conversation in conversations.result():
            name = f"{conversation['id']}: {conversation['name']}"
            list_of_conversations.append([ButtonBuilder(name, conversation['id']).build_conversation_choice_button()])
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите диалог:', reply_markup=InlineKeyboardMarkup(list_of_conversations))


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = get_callback_data(update)
    await callback_options[query['action']](update, context, query['id'], conversation_name=query.get('name', None))


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """Для того, чтобы начать диалог достаточно просто отправить сообщение. Тем не менее, система предусматривает наличие более одного диалога. Для того, чтобы получить доступ к своим диалогам, введите команду /conversations"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)