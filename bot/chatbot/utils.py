from telegram import Update
from .data_api import Conversation
from telegram.ext import ContextTypes
from .data_api import DataAPI
from typing import List, Awaitable, Optional, Dict
import asyncio
import json
import logging

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
        async def wrapper(self, *args, **kwargs):
            user = await self.user_api(self.update, self.context).get()
            if user:
                if with_message:
                    await self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=self.MESSAGES['user']['found'])
            else:
                user = self.user_api(self.update, self.context).post()
                message = self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=self.MESSAGES['user']['creating'])
                user = await user
                await message
                if not user:
                    await self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=self.MESSAGES['user']['error'])
                    logging.critical(f'Error creating the user. Data: username: {self.update.effective_user.username}')
                    raise ValueError('Error creating the user')
            return await func(self, *args, **kwargs)
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

    def __init__(self, conversation_api: DataAPI, user_conversations_api: DataAPI, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.conversation_api = conversation_api
        self.context = context
        self.update = update
        self.user_conversations_api = user_conversations_api

    def get_current_conversation(self) -> int:
        return self.context.user_data.get('current_conversation')
    
    def set_current_conversation(self, conversation_id: int):
        self.context.user_data['current_conversation'] = conversation_id

    async def _check_current_conversation(self) -> bool:
        return await self.conversation_api(self.update, self.context).get() != False

    async def get_or_create_current_conversation(self) -> int:
        try:
            if self.get_current_conversation() and await self._check_current_conversation():
                return self.get_current_conversation()
        except KeyError as e:
            logging.error(e)

        conversation = await self.user_conversations_api(self.update, self.context).post(name="Новый Диалог")
        self.set_current_conversation(conversation['id'])
        return conversation['id']


class NewCoversation:

    def __init__(self, user_conversations_api: DataAPI, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        self.user_conversations_api = user_conversations_api
        self.context = context
        self.update = update
    
    def get_new_conversation_is_being_created(self) -> bool:
        return self.context.user_data.get('is_creating_conversation', False)

    def set_new_conversation_is_being_created(self, value: bool):
        self.context.user_data['is_creating_conversation'] = value

    async def create_new_conversation(self) -> Awaitable[Dict[str, str]]:
        result = await self.user_conversations_api(self.update, self.context).post(self.update.message.text)
        return result
    