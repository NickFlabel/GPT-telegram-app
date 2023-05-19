from typing import Any
from aioresponses import aioresponses
import dotenv
import os
import json

dotenv.load_dotenv()
URL_API = os.getenv('DB_API_URL')

class URLBuilder:

    def __init__(self, mocked: aioresponses, conversation_id: int, user_id: int) -> None:
        self.m = mocked
        self.conversation_id = conversation_id
        self.user_id = user_id

    def build_get_conversation_url(self, body: dict, status: int):
        self.m.get(f'{URL_API}/users/{self.user_id}/conversations/{self.conversation_id}', status=status, body=json.dumps(body))
        return self
    
    def build_get_conversations_url(self, body: dict, status: int):
        self.m.get(f'{URL_API}/users/{self.user_id}/conversations', status=status, body=json.dumps(body))
        return self
    
    def build_post_conversations_url(self, body: dict, status: int):
        self.m.post(f'{URL_API}/users/{self.user_id}/conversations', status=status, body=json.dumps(body))
        return self

    def build_get_messages_url(self, body: dict, status: int):
        self.m.get(f'{URL_API}/users/{self.user_id}/conversations/{self.conversation_id}/messages', status=status, body=json.dumps(body))
        return self
    
    def build_post_message_url(self, body: dict, status: int):
        self.m.post(f'{URL_API}/users/{self.user_id}/conversations/{self.conversation_id}/messages', status=status, body=json.dumps(body))
        return self
    
    def build_openai_url(self, body: dict, status: int):
        self.m.post('https://api.openai.com/v1/chat/completions', status=status, body=json.dumps(body))
        return self
    
    def build_get_user_url(self, body: dict, status: int):
        self.m.get(f'{URL_API}/users/{self.user_id}', status=status, body=json.dumps(body))
        return self
    
    def build_post_user_url(self, body: dict, status: int):
        self.m.post(f'{URL_API}/users', status=status, body=json.dumps(body))
        return self
    
    def build_delete_conversation_url(self, status: int):
        self.m.delete(f'{URL_API}/users/{self.user_id}/conversations/{self.conversation_id}', status=status)
        return self
    

class URLDirector:

    def __init__(self, mocked: aioresponses, conversation_id: int = None, user_id: int = None) -> None:
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.m = mocked

    def build_message_routine_no_current_conversation(self):
        URLBuilder(self.m, self.conversation_id, self.user_id
                   ).build_post_conversations_url({"name": "Новый диалог", "id": 1}, 201
                   ).build_get_messages_url('[]', 200
                   ).build_openai_url({"choices": [{"message": {"content": "test", "role": "assistant"}}]}, 200
                   ).build_post_message_url({"content": "test", "role": "user"}, 201
                   ).build_post_message_url({"content": "test", "role": "assistant"}, 201
                   ).build_get_conversation_url({"name": "Новый диалог", "id": 1}, 404)
        return self

    def build_message_routine_with_current_conversation(self):
        URLBuilder(self.m, self.conversation_id, self.user_id
                   ).build_get_messages_url('[]', 200
                   ).build_openai_url({"choices": [{"message": {"content": "test", "role": "assistant"}}]}, 200
                   ).build_post_message_url({"content": "test", "role": "user"}, 201
                   ).build_post_message_url({"content": "test", "role": "assistant"}, 201
                   ).build_get_conversation_url({"name": "Новый диалог", "id": 1}, 200)
        return self
    
    def build_user_routine_no_user(self):
        URLBuilder(self.m, self.conversation_id, self.user_id
                   ).build_get_user_url({}, 404
                   ).build_post_user_url({"id": self.user_id, "username": None, "first_name": None, "last_name": None}, 201)
        return self
    
    def build_user_routine_with_user(self):
        URLBuilder(self.m, self.conversation_id, self.user_id
                   ).build_get_user_url({"id": self.user_id, "username": None, "first_name": None, "last_name": None}, 200)
        return self
    