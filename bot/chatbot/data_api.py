import aiohttp
import dotenv
import os
from abc import ABC, abstractmethod
from typing import List, Literal, Dict, Optional, List
from telegram import Update
from telegram.ext import CallbackContext
import logging
import json

dotenv.load_dotenv()

DB_API_URL = os.getenv('DB_API_URL')
GPT_URL = os.getenv('GPT_URL')
API_KEY = os.getenv('OPEN_AI_KEY')


class DataAPI(ABC):

    # Could have decoupled the update and context from the class but the scope of the project is small enough to not do so. It is easy to make testable mocks of the update and context objects.
    def __init__(self, update: Update, context: CallbackContext) -> None: 
        self.update = update
        self.context = context

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def post(self):
        pass

    @abstractmethod
    def put(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def _build_url(self):
        pass


class GetUserIdMixin(ABC):

    def _get_user_id(self):
        return self.update.effective_user.id
    

class GetConversationIdMixin(ABC):

    def _get_conversation_id(self, conv_id: int = None):
        if conv_id:
            return conv_id
        current_conversation = self.context.user_data.get('current_conversation')
        if not current_conversation:
            raise KeyError('No current_conversation id found in context.user_data')
        return current_conversation
    

class ResponseErrorHandler:

    def __init__(self, response: aiohttp.ClientResponse) -> None:
        self.response = response

    async def handle(self):
        logging.error(f'Error when calling {self.response.url} with method {self.response.method}. Status code: {self.response.status}. Reason: {self.response.reason}. Content: {await self.response.json()}')
        return False

class Message(DataAPI, GetUserIdMixin, GetConversationIdMixin):
    url_base = DB_API_URL

    async def get(self, conv_id: int = None) -> List[Dict[str, str]]:
        self._build_url(conv_id)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                await resp.read()
                if resp.status == 200:
                    return await resp.json()
                else:
                    return await ResponseErrorHandler(resp).handle()
                
    async def post(self, message: str, role: Literal['user', 'assistant']) -> Dict[str, str]:
        self._build_url()
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json={
                'content': message,
                'role': role
            }) as resp:
                await resp.read()
                if resp.status == 201:
                    return await resp.json()
                else:
                    return await ResponseErrorHandler(resp).handle()

    def put(self):
        pass

    def delete(self):
        pass
                
    def _build_url(self, conv_id: int = None):
        self.url = self.url_base + f'/users/{self._get_user_id()}/conversations/{self._get_conversation_id(conv_id=conv_id)}/messages'


class User(DataAPI, GetUserIdMixin):
    url_base = DB_API_URL

    async def get(self) -> Dict[str, str]:
        self._build_url()
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                await resp.read()
                if resp.status == 200:
                    return await resp.json()
                else:
                    return await ResponseErrorHandler(resp).handle()

    async def post(self) -> Dict[str, str]:
        self.url = self.url_base + '/users'
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json=self._get_user_data()) as resp:
                await resp.read()
                if resp.status == 201:
                    return await resp.json()
                else:
                    return await ResponseErrorHandler(resp).handle()

    def put(self):
        pass

    def delete(self):
        pass

    def _build_url(self):
        self.url = self.url_base + f'/users/{self._get_user_id()}'

    def _get_user_data(self) -> Dict[str, str]:
        return {
            'id': self._get_user_id(),
            'first_name': self.update.effective_user.first_name,
            'last_name': self.update.effective_user.last_name,
            'username': self.update.effective_user.username
        }
                

class Conversation(DataAPI, GetUserIdMixin, GetConversationIdMixin):
    url_base = DB_API_URL

    async def get(self) -> Dict[str, str]:
        self._build_url()
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                await resp.read()
                if resp.status == 200:
                    return await resp.json()
                else:
                    return await ResponseErrorHandler(resp).handle()

    async def post(self):
        pass

    def put(self):
        pass

    async def delete(self, conv_id: int = None) -> bool:
        self._build_url(conv_id)
        async with aiohttp.ClientSession() as session:
            async with session.delete(self.url) as resp:
                await resp.read()
                if resp.status == 204:
                    return True
                else:
                    return await ResponseErrorHandler(resp).handle()

    def _build_url(self, conv_id: int = None):
        self.url = self.url_base + f'/users/{self._get_user_id()}/conversations/{self._get_conversation_id(conv_id=conv_id)}'

    def _get_user_id(self):
        return self.update.effective_user.id
    

class UserConversations(DataAPI, GetUserIdMixin):
    url_base = DB_API_URL

    async def get(self) -> List[Dict[str, str]]:
        self._build_url()
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as resp:
                await resp.read()
                if resp.status == 200:
                    return await resp.json()
                else:
                    return await ResponseErrorHandler(resp).handle()

    async def post(self, name: str) -> Dict[str, str]:
        self._build_url()
        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, json={
                'name': name
            }) as resp:
                await resp.read()
                if resp.status == 201:
                    return await resp.json()
                else:
                    return await ResponseErrorHandler(resp).handle()

    def put(self):
        pass

    def delete(self):
        pass

    def _build_url(self):
        self.url = self.url_base + f'/users/{self._get_user_id()}/conversations'


class BotAnswer(DataAPI):

    def get(self):
        pass

    async def post(self, messages: List[Dict[str, str]]):
        self._build_url()
        headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
        }
        messages.append({'role': 'user', 'content': self._get_message()})
        payload = {
        'model': 'gpt-3.5-turbo',
        'messages': messages
        }
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(self.url,
                                    headers=headers,
                                    json=payload) as resp:
                if resp.status == 200:
                    answer = await resp.text()
                    answer = json.loads(answer)
                    answer = answer['choices'][0]['message']['content']
                    return answer
                else:
                    return await ResponseErrorHandler(resp).handle()


    def put(self):
        pass

    def delete(self):
        pass

    def _build_url(self):
        self.url = GPT_URL

    def _get_message(self):
        return self.update.message.text

    