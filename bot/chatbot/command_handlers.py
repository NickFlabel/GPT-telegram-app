import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import aiohttp
import asyncio
import dotenv
import os
from .data_api import User, Message, Conversation 
from .utils import CurrentConversation, user_checker_decorator, check_creating_conversation, get_callback_data, NewCoversation
from .buttons import ButtonBuilder
from .callback_handlers import callback_options

dotenv.load_dotenv()

DB_API_URL = os.getenv('DB_API_URL')
with open('messages.json', 'r') as f:
    MESSAGES = json.load(f)


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = get_callback_data(update)
    await callback_options[query['action']](update, context, query['id'], conversation_name=query.get('name', None))


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """Для того, чтобы начать диалог достаточно просто отправить сообщение. Тем не менее, система предусматривает наличие более одного диалога. Для того, чтобы получить доступ к своим диалогам, введите команду /conversations"""
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)