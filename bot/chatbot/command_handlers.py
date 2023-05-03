import json

from telegram import Update
from telegram.ext import ContextTypes
import aiohttp
import asyncio
import dotenv
import os
from gpt_api import get_answer_from_gpt_3_5, get_dalle_image
from db_api import save_prompt, save_response, get_dialog, get_or_create_user

dotenv.load_dotenv()

DB_API_URL = os.getenv('DB_API_URL')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = asyncio.create_task(context.bot.send_message(chat_id=update.effective_chat.id, text='Проверяем пользователя...'))
    user = await get_or_create_user(user_id, update.effective_user.first_name, update.effective_user.last_name, update.effective_user.username)
    name = json.loads(user)['username']
    await message
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Hello, {name}. Для отправки сообщения GPT-3.5 напишите любое сообщение. Для того, чтобы получить свой диалог с GPT, напишите /dialogs')


async def prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = update.message.text
    is_prompt_saved = asyncio.create_task(save_prompt(prompt, update.effective_user.id))
    dialogs = await get_dialog(update.effective_user.id)
    answer = asyncio.create_task(get_answer_from_gpt_3_5(prompt, json.loads(dialogs)))
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Получаем ответ от GPT-3...')
    await answer
    message_answer = answer.result()
    is_response_saved = asyncio.create_task(save_response(message_answer, update.effective_user.id))
    answer = asyncio.create_task(update.message.reply_text(message_answer))
    await is_prompt_saved
    await is_response_saved
    if not is_prompt_saved.result() or not is_response_saved.result():
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Произошла ошибка при сохранении данных в базу данных. Ваш диалог не сохранен.')
    await answer


async def get_dialogs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = asyncio.create_task(context.bot.send_message(chat_id=update.effective_chat.id, text='Получаем диалог...'))
    dialog = asyncio.create_task(get_dialog(user_id))
    await message
    await dialog
    if dialog.result():
        await context.bot.send_message(chat_id=update.effective_chat.id, text=dialog.result())
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Произошла ошибка при получении диалога. Попробуйте позже.')
        