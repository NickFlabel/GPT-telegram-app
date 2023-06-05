from telegram import Update
from telegram.ext import ContextTypes
from .callback_interface import CallbackInterface, DataApiMixin
from ..utils import NewCoversation, CurrentConversation, user_checker_decorator
from ..buttons import ButtonBuilder
import asyncio
from typing import Literal
from telegram import InlineKeyboardMarkup


class Start(CallbackInterface, DataApiMixin):

    @user_checker_decorator(with_message=True)
    async def handle(self):
            await self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=self.MESSAGES['start']['message'])


class MessageCallback(CallbackInterface, DataApiMixin):
    tasks = []

    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        super().__init__(update, context)
        self.current_conversation = CurrentConversation(self.conversation_api, self.user_conversations_api, self.update, self.context)
        self.new_conversation = NewCoversation(self.user_conversations_api, self.update, self.context)
     
    @user_checker_decorator(with_message=False)
    async def handle(self):
        if self._check_new_conversation():
            await self._create_new_conversation()
        else:
            await self._process_message()

    def _check_new_conversation(self) -> bool:
        return self.new_conversation.get_new_conversation_is_being_created()
    
    async def _create_new_conversation(self):
        self._reset_tasks()
        self.tasks.append(asyncio.create_task(self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=self.MESSAGES['conversation']['creating'])))
        self.tasks.append(asyncio.create_task(self.new_conversation.create_new_conversation()))
        await asyncio.gather(*self.tasks)
        conversation = self.tasks[1].result()
        if conversation:
            await self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=self.MESSAGES['conversation']['created'])
            self.current_conversation.set_current_conversation(conversation['id'])
        self.new_conversation.set_new_conversation_is_being_created(False)

    async def _process_message(self):
        self._reset_tasks()
        self._send_acknolegment_message()
        await self._get_conversation()
        save_user_message = asyncio.create_task(self._save_message(self.update.message.text, 'user'))
        answer = await self._get_answer_from_chatbot()
        await save_user_message
        self.tasks.append(asyncio.create_task(self._save_message(answer, 'assistant')))
        self._send_answer_to_user(answer=answer)
        await asyncio.gather(*self.tasks)

    def _send_acknolegment_message(self):
        self.tasks.append(asyncio.create_task(self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=self.MESSAGES['message']['acknolegment'])))

    async def _get_conversation(self):
        self.current_conversation_id = await self.current_conversation.get_or_create_current_conversation()
        self.conversation_messages = await self.message_api(self.update, self.context).get(self.current_conversation_id)
        self.conversation_messages.append({'content': self.update.message.text, 'role': 'user'})
        if not self.conversation_messages:
            await self._server_error()

    async def _get_answer_from_chatbot(self):
        return await self.bot_api(self.update, self.context).post(messages=self.conversation_messages)

    async def _save_message(self, message: str, role: Literal['user', 'assistant']):
        await self.message_api(self.update, self.context).post(message=message, role=role)

    def _send_answer_to_user(self, answer: str):
        self.tasks.append(asyncio.create_task(self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=answer)))

    def _reset_tasks(self):
        self.tasks = []

    async def _server_error(self):
        await self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=self.MESSAGES['server']['error'])

class ConversationHandler(CallbackInterface, DataApiMixin):

    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        super().__init__(update, context)
        self.tasks = []
        self.list_of_conversation_buttons = []
        self.conversations = None
        self.current_conversation = CurrentConversation(self.conversation_api, self.user_conversations_api, self.update, self.context)
        self.new_conversation = NewCoversation(self.user_conversations_api, self.update, self.context)

    async def _get_conversations(self):
        return await self.user_conversations_api(self.update, self.context).get()
    
    def _get_current_conversation(self):
        return self.current_conversation.get_current_conversation()

    def _get_message_text(self):
        current_conversation = self._get_current_conversation()
        if current_conversation:
            return f'{self.MESSAGES["conversation"]["current_conversation_found"]}' + str(current_conversation)
        else:
            return self.MESSAGES['conversation']['no_current_conversation']
        
    def _get_new_conversation_button(self):
        return ButtonBuilder(name=None, id=None).build_conversation_create_button()
    
    def _build_conversation_buttons(self):
        for conversation in self.conversations.result():
            name = f"{conversation['id']}: {conversation['name']}"
            self.list_of_conversation_buttons.append([ButtonBuilder(name, conversation['id']).build_conversation_choice_button()])
    
    async def handle(self):
        self.conversations = asyncio.create_task(self._get_conversations())
        new_conversation_button = self._get_new_conversation_button()
        self.tasks.append(asyncio.create_task(self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=self.MESSAGES['conversation']['create_new_conversation'], reply_markup=InlineKeyboardMarkup([[new_conversation_button]]))))
        message_text = self._get_message_text()
        self.tasks.append(asyncio.create_task(self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=message_text)))
        await asyncio.gather(*self.tasks, self.conversations)
        self._build_conversation_buttons()
        await self.context.bot.send_message(chat_id=self.update.effective_chat.id, text=self.MESSAGES['conversation']['dialog_choice'], reply_markup=InlineKeyboardMarkup(self.list_of_conversation_buttons))



