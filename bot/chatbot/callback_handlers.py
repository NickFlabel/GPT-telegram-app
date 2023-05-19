from .db_api import Conversation
from telegram.ext import ContextTypes
from telegram import Update
from .buttons import ButtonDirector
from telegram import InlineKeyboardMarkup

async def conversation_options(update: Update, context: ContextTypes.DEFAULT_TYPE, id: int, *args, **kwargs):
    conversation_name = kwargs.get('conversation_name')
    buttons = ButtonDirector(conversation_name, id).build_conversation_options_buttons()
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите действие:', reply_markup=InlineKeyboardMarkup(buttons))

async def delete_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE, id: int, *args, **kwargs):
    result = await Conversation(update.effective_user.id).delete_conversation(id)
    if result:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Диалог с id {id} удален.')
        return True
    else:
        return False

async def choose_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE, id: int, *args, **kwargs):
    context.user_data['current_conversation'] = id
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Диалог с id {id} выбран в качестве активного.')

async def create_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
    context.user_data['is_creating_conversation'] = True
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Введите название диалога:')

async def view_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE, id: int, *args, **kwargs):
    messages = await Conversation(update.effective_user.id).get_conversation(id)
    for message in messages:
        if message['role'] == 'user':
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Вы: {message["content"]}')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Бот: {message["content"]}')


callback_options = {
    'ConversationChoice': choose_conversation,
    'ConversationDelete': delete_conversation,
    'ConversationCreate': create_conversation,
    'ConversationView': view_conversation,
    'ConversationOptions': conversation_options,
}
