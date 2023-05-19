import aiohttp
import dotenv
import os
from typing import List, Literal, Dict, Optional

dotenv.load_dotenv()

DB_API_URL = os.getenv('DB_API_URL')


class Message:

    def __init__(self, text: str, conversation_id: int, user_id: int) -> None:
        self.text = text
        self.conversation_id = conversation_id
        self.user_id = user_id

    async def create_message(self, role: Literal['user', 'assistant']):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{DB_API_URL}/users/{self.user_id}/conversations/{self.conversation_id}/messages', json={
                'content': self.text,
                'role': role
            }) as resp:
                await resp.read()
                if resp.status == 201:
                    return await resp.json()
                else:
                    return False
                

class User:

    def __init__(self, user_id: int, first_name: Optional[str] = None, last_name: Optional[str] = None, username: Optional[str] = None) -> None:
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        
    async def get_user(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{DB_API_URL}/users/{self.user_id}') as resp:
                await resp.read()
                if resp.status == 200:
                    return await resp.json()
                else:
                    return False
                
    async def create_user(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{DB_API_URL}/users', json={
                'id': self.user_id,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'username': self.username,
            }) as resp:
                await resp.read()
                if resp.status == 201:
                    return await resp.json()
                else:
                    return False
                

class Conversation:

    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    async def get_conversations(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{DB_API_URL}/users/{self.user_id}/conversations') as resp:
                await resp.read()
                if resp.status == 200:
                    return await resp.json()
                else:
                    return False
                
    async def check_conversation_by_id(self, conversation_id: int):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{DB_API_URL}/users/{self.user_id}/conversations/{conversation_id}') as resp:
                await resp.read()
                if resp.status == 200:
                    return await resp.json()
                else:
                    return False
    
    async def get_conversation(self, conversation_id: int) -> List[Dict[str, str]]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'{DB_API_URL}/users/{self.user_id}/conversations/{conversation_id}/messages') as resp:
                await resp.read()
                if resp.status == 200:
                    return await resp.json()
                else:
                    return False
    
    async def create_conversation(self, conversation_name: str = 'Новый диалог'):
        async with aiohttp.ClientSession() as session:
            async with session.post(f'{DB_API_URL}/users/{self.user_id}/conversations', json={
                'name': conversation_name
            }) as resp:
                await resp.read()
                if resp.status == 201:
                    return await resp.json()
                else:
                    return False
                
    async def delete_conversation(self, conversation_id: int):
        async with aiohttp.ClientSession() as session:
            async with session.delete(f'{DB_API_URL}/users/{self.user_id}/conversations/{conversation_id}') as resp:
                await resp.read()
                if resp.status == 204:
                    return True
                else:
                    return False
