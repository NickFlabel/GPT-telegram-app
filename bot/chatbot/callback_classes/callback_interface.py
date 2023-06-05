from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes
from ..data_api import User, DataAPI, Conversation, UserConversations, Message, BotAnswer
import json

with open('messages.json', 'r') as f:
    MESSAGES = json.load(f)

class CallbackInterface(ABC):
    MESSAGES = MESSAGES


    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self.update = update
        self.context = context

    @classmethod
    def get_callback_function(cls):

        async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await cls(update, context).handle()

        return callback

    @abstractmethod
    async def handle(self):
        pass


class DataApiMixin(ABC):
    user_api = User
    message_api = Message
    conversation_api = Conversation
    user_conversations_api = UserConversations
    bot_api = BotAnswer
