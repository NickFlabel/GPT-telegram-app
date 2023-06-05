from typing import Any, Iterable
from aioresponses import aioresponses
from telegram import Update
from telegram.ext import CallbackContext, ContextTypes
from ..data_api import DataAPI
from ..callback_classes.callback_interface import DataApiMixin
import dotenv
import os
import json

dotenv.load_dotenv()
URL_API = os.getenv('DB_API_URL')
GPT_URL = os.getenv('GPT_URL')

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
        self.m.post(GPT_URL, status=status, body=json.dumps(body))
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

    def build_conversation_creation_routine(self):
        URLBuilder(self.m, self.conversation_id, self.user_id
                   ).build_get_conversations_url([], 200
                   ).build_post_conversations_url({"name": "Новый диалог", "id": 1}, 201
                   ).build_get_conversation_url({"name": "Новый диалог", "id": 1}, 200)
        return self

    def build_message_routine_no_current_conversation(self):
        URLBuilder(self.m, self.conversation_id, self.user_id
                   ).build_post_conversations_url({"name": "Новый диалог", "id": 1}, 201
                   ).build_get_messages_url('[]', 200
                   ).build_openai_url({"choices": [{"message": {"content": "test", "role": "assistant"}}]}, 200
                   ).build_post_message_url({"content": "test_request", "role": "user"}, 201
                   ).build_post_message_url({"content": "test_response", "role": "assistant"}, 201
                   ).build_get_conversation_url({"name": "Новый диалог", "id": 1}, 404)
        return self

    def build_message_routine_with_current_conversation(self):
        URLBuilder(self.m, self.conversation_id, self.user_id
                   ).build_get_messages_url([''], 200
                   ).build_openai_url({"choices": [{"message": {"content": "test_response", "role": "assistant"}}]}, 200
                   ).build_post_message_url({"content": "test_request", "role": "user"}, 201
                   ).build_post_message_url({"content": "test_response", "role": "assistant"}, 201
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
    


class DataApiMock(DataAPI):


    get_return = []
    post_return = []
    put_return = []
    delete_return = []
    
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        super().__init__(update, context)
        self.get_index = 0
        self.post_index = 0
        self.put_index = 0
        self.delete_index = 0
        
    async def get(self, *args, **kwargs):
        return_value = self.get_return[self.get_index]
        self.observer.add_call(self.update, self.context, self.__class__.__name__, 'get', return_value, *args, **kwargs)
        self.get_index += 1
        return return_value
    
    async def post(self, *args, **kwargs):
        return_value = self.post_return[self.post_index]
        self.observer.add_call(self.update, self.context, self.__class__.__name__, 'post', return_value, *args, **kwargs)
        self.post_index += 1
        return return_value
    
    async def put(self, *args, **kwargs):
        return_value = self.put_return[self.put_index]
        self.observer.add_call(self.update, self.context, self.__class__.__name__, 'put', return_value, *args, **kwargs)
        self.put_index += 1
        return return_value
    
    async def delete(self, *args, **kwargs):
        return_value = self.delete_return[self.delete_index]
        self.observer.add_call(self.update, self.context, self.__class__.__name__, 'delete', return_value, *args, **kwargs)
        self.delete_index += 1
        return return_value
    
    def _build_url(self):
        return 
    

class TestObserver:

    def __init__(self) -> None:
        self.calls = {}

    def _create_record(self, name: str) -> None:
        self.model = {
            'get': {
                'quantity': 0,
                'calls': []
            },
            'post': {
                'quantity': 0,
                'calls': []
            },
            'put': {
                'quantity': 0,
                'calls': []
            },
            'delete': {
                'quantity': 0,
                'calls': []
            },
        }
        self.calls.setdefault(name, self.model)

    def add_call(self, update: Update, context: ContextTypes.DEFAULT_TYPE, class_name: str, type: str, response: Any, *args, **kwargs):
        self._create_record(class_name)
        self.calls[class_name][type]['quantity'] += 1
        self.calls[class_name][type]['calls'].append({
            'message': update.message.text,
            'args': args,
            'kwargs': kwargs,
            'response': response
        })

    def called_with(self, name: str, method: str, time_called: int, param_name: str, param_value: Any) -> bool:
        return self.calls[name][method]['calls'][time_called - 1][param_name] == param_value


class DataApiMockBuilder:

    def __init__(self, name: str, observer: TestObserver) -> None:
        self.mock = type(f'mock_{name}', (DataApiMock,), {'observer': observer})

    def get_mock(self):
        return self.mock

    def build_get_return(self, value: Iterable[Any]):
        self.mock.get_return = value
        return self
    
    def build_post_return(self, value: Iterable[Any]):
        self.mock.post_return = value
        return self
    
    def build_put_return(self, value: Iterable[Any]):
        self.mock.put_return = value
        return self
    
    def build_delete_return(self, value: Iterable[Any]):
        self.mock.delete_return = value
        return self
    

class DataApiMockDirector:

    def __init__(self) -> None:
        self.observer = TestObserver()
        self.messages = None
        self.conversation = None
        self.user_conversations = None
        self.user = None
        self.chatbot_api = None
    
    def build_messages_api(self, get_value: Iterable[Any], post_value: Iterable[Any], name: str = 'MessagesMock'):
        self.builder = DataApiMockBuilder(name=name, observer=self.observer)
        self.builder.build_get_return(get_value).build_post_return(post_value)
        self.messages = self.builder.get_mock()
        return self
    
    def build_conversation_api(self, get_value: Iterable[Any], delete_value: Iterable[Any], name: str = 'ConversationMock'):
        self.builder = DataApiMockBuilder(name=name, observer=self.observer)
        self.builder.build_get_return(get_value).build_delete_return(delete_value)
        self.conversation = self.builder.get_mock()
        return self
    
    def build_user_conversations_api(self, get_value: Iterable[Any], post_value: Iterable[Any], name: str = 'UserConversationsMock'):
        self.builder = DataApiMockBuilder(name=name, observer=self.observer)
        self.builder.build_get_return(get_value).build_post_return(post_value)
        self.user_conversations = self.builder.get_mock()
        return self

    def build_user_api(self, get_value: Iterable[Any], post_value: Iterable[Any], name: str = 'UserMock'):
        self.builder = DataApiMockBuilder(name=name, observer=self.observer)
        self.builder.build_get_return(get_value).build_post_return(post_value)
        self.user = self.builder.get_mock()
        return self
    
    def build_chatbot_api(self, post_value: Iterable[Any], name: str = 'ChatbotApiMock'):
        self.builder = DataApiMockBuilder(name=name, observer=self.observer)
        self.builder.build_post_return(post_value)
        self.chatbot_api = self.builder.get_mock()
        return self

    def get_mock_api(self):
        return {
            'message_api': self.messages,
            'conversation_api': self.conversation,
            'user_conversations_api': self.user_conversations,
            'user_api': self.user,
            'bot_api': self.chatbot_api
        }
    

def mock_api_classes(monkeypatch, data_api_director: DataApiMockDirector):
    mock_api_dict = data_api_director.get_mock_api()
    monkeypatch.setattr(DataApiMixin, 'user_api', mock_api_dict['user_api'])
    monkeypatch.setattr(DataApiMixin, 'message_api', mock_api_dict['message_api'])
    monkeypatch.setattr(DataApiMixin, 'conversation_api', mock_api_dict['conversation_api'])
    monkeypatch.setattr(DataApiMixin, 'user_conversations_api', mock_api_dict['user_conversations_api'])
    monkeypatch.setattr(DataApiMixin, 'bot_api', mock_api_dict['bot_api'])
