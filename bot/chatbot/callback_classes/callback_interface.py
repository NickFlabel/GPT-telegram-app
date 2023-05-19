from abc import ABC, abstractmethod
from telegram import Update
from telegram.ext import ContextTypes
import json

with open('messages.json', 'r') as f:
    MESSAGES = json.load(f)

class CallbackInterface(ABC):
    MESSAGES = MESSAGES

    @classmethod
    def get_callback_function(cls):

        async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await cls().handle(update, context)

        return callback

    @abstractmethod
    async def handle(self):
        pass
