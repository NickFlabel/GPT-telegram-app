from telegram import Update
from .db_api import Conversation
from telegram.ext import ContextTypes
from .db_api import User, Message, Conversation
from typing import List, Awaitable, Optional
import asyncio
import json

with open('messages.json', 'r') as f:
    MESSAGES = json.load(f)


def get_user_data(update: Update) -> dict:
    user = update.effective_user
    if user:
        return {
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
        }
    else:
        return None

def user_checker_decorator(with_message: bool = False):
    def user_checker(func):
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user = await User(**get_user_data(update)).get_user()
            if user:
                if with_message:
                    await context.bot.send_message(chat_id=update.effective_chat.id, text=MESSAGES['user']['found'])
            else:
                user = User(**get_user_data(update)).create_user()
                message = context.bot.send_message(chat_id=update.effective_chat.id, text=MESSAGES['user']['creating'])
                await user
                await message
            return await func(update, context, *args, **kwargs)
        return wrapper
    return user_checker


def check_creating_conversation(context: ContextTypes.DEFAULT_TYPE) -> bool:
    return context.user_data.get('is_creating_conversation', False)


def get_callback_data(update: Update) -> dict:
    data = update.callback_query.data.split('_')
    return {
        'action': data[0],
        'name': data[1],
        'id': int(data[2]) if data[2] != 'None' else None,
    }


class CurrentConversation:

    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.update = update
        self.context = context

    def get_current_conversation(self):
        return self.context.user_data.get('current_conversation')
    
    def set_current_conversation(self, conversation_id: int):
        self.context.user_data['current_conversation'] = conversation_id

    async def _check_current_conversation(self):
        return await Conversation(self.update.effective_user.id).check_conversation_by_id(self.get_current_conversation())

    async def get_or_create_current_conversation(self) -> id:
        if self.get_current_conversation() and await self._check_current_conversation():
            return self.get_current_conversation()
        else:
            conversation = await Conversation(self.update.effective_user.id).create_conversation()
            self.set_current_conversation(conversation['id'])
            return conversation['id']


class NewCoversation:
    
    @staticmethod
    def get_new_conversation_is_being_created(context: ContextTypes.DEFAULT_TYPE) -> bool:
        return context.user_data.get('is_creating_conversation', False)

    @staticmethod
    def set_new_conversation_is_being_created(self, context: ContextTypes.DEFAULT_TYPE, value: bool):
        context.user_data['is_creating_conversation'] = value

    @staticmethod
    async def create_new_conversation(self, user_id: int, message: str) -> Awaitable[bool]:
        result = await Conversation(user_id).create_conversation(conversation_name=message)
        return result
    
