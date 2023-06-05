from ...callback_classes.callback_classes import Start, MessageCallback, ConversationHandler
from ...callback_classes.callback_interface import DataApiMixin
from ...utils import CurrentConversation, NewCoversation
import pytest
import dotenv
import os
from aioresponses import aioresponses
from ..fixtures import update, context, urls
import json
from ..utils import URLDirector, URLBuilder, DataApiMockDirector, mock_api_classes
from telegram import InlineKeyboardButton

global_user_id = 1234
pytestmark = pytest.mark.parametrize('update', [{'user_id': global_user_id}], indirect=True)

dotenv.load_dotenv()
URL_API = os.getenv('DB_API_URL')
API_KEY = os.getenv('OPEN_AI_KEY')
GPT_URL = os.getenv('GPT_URL')

with open('messages.json', 'r') as f:
    MESSAGES = json.load(f)

class TestStart:
    
    @pytest.mark.asyncio
    async def test_start_user_is_not_created(self, update, context, monkeypatch):
        director = DataApiMockDirector().build_user_api([False], [True])
        mock_api_classes(monkeypatch, director)
        result = await Start.get_callback_function()(update, context)
        assert result == None
        assert context.bot.send_message.call_count == 2
        assert context.bot.send_message.call_args_list[0][1]['text'] == MESSAGES['user']['creating']
        print(director.observer.calls)

    @pytest.mark.asyncio
    async def test_start_user_is_created(self, update, context, monkeypatch):
        director = DataApiMockDirector().build_user_api([True], [False])
        mock_api_classes(monkeypatch, director)
        result = await Start.get_callback_function()(update, context)
        assert result == None
        assert context.bot.send_message.call_count == 2
        assert context.bot.send_message.call_args_list[0][1]['text'] == MESSAGES['user']['found']


class TestMessage:

    def test_check_new_conversation_no_conversation(self, update, context):
        callback = MessageCallback(update, context)
        assert callback._check_new_conversation() == False

    def test_check_new_conversation_with_conversation(self, update, context):
        context.user_data['is_creating_conversation'] = True
        callback = MessageCallback(update, context)
        assert callback._check_new_conversation() == True

    @pytest.mark.asyncio
    async def test_create_new_conversation(self, update, context, monkeypatch):
        update.message.text = 'test'
        director = DataApiMockDirector().build_user_conversations_api(get_value=[], post_value=[{'id': 1}])
        mock_api_classes(monkeypatch, director)
        message = MessageCallback(update, context)
        await message._create_new_conversation()
        assert context.bot.send_message.call_count == 2
        assert context.bot.send_message.call_args_list[0][1]['text'] == MESSAGES['conversation']['creating']

    @pytest.mark.asyncio
    async def test_send_acknolegment_message(self, update, context):
        MessageCallback(update, context)._send_acknolegment_message()
        assert context.bot.send_message.call_count == 1
        assert context.bot.send_message.call_args_list[0][1]['text'] == MESSAGES['message']['acknolegment']

    @pytest.mark.asyncio
    async def test_get_conversation_no_current_conversation(self, update, context, monkeypatch):
        director = DataApiMockDirector(
                                      ).build_user_conversations_api(get_value=[], post_value=[{'id': 1, 'name': 'Новый Диалог'}]
                                      ).build_messages_api(get_value=[[{'content': 'test', 'role': 'user'}]], post_value=[])
        mock_api_classes(monkeypatch, director)
        message = MessageCallback(update, context)
        await message._get_conversation()
        assert context.bot.send_message.call_count == 0

    @pytest.mark.asyncio
    async def test_process_message(self, update, context, monkeypatch):
        test_conversation_id = 1
        context.user_data['current_conversation'] = test_conversation_id
        update.message.text = 'test_request'
        director = DataApiMockDirector(
                                      ).build_conversation_api(get_value=[{'id': 1}], delete_value=[]
                                      ).build_messages_api(get_value=[[{'content': 'test', 'role': 'user'}]], post_value=[True, True]
                                      ).build_chatbot_api(post_value=['test_answer'])
        mock_api_classes(monkeypatch, director)
        message = MessageCallback(update, context)
        await message._process_message()
        assert context.bot.send_message.call_count == 2
        assert director.observer.called_with('mock_MessagesMock', 'post', 2, 'kwargs', {'message': 'test_answer', 'role': 'assistant'})
        assert director.observer.called_with('mock_MessagesMock', 'post', 1, 'kwargs', {'message': update.message.text, 'role': 'user'})
        assert director.observer.called_with('mock_ChatbotApiMock', 'post', 1, 'kwargs', {'messages': [{'content': 'test', 'role': 'user'}, {'content': update.message.text, 'role': 'user'}]})


class TestConversationHandler:

    def test_init(self, update, context):
        new_conversation_handler = ConversationHandler(update, context)
        assert isinstance(new_conversation_handler.current_conversation, CurrentConversation)
        assert isinstance(new_conversation_handler.new_conversation, NewCoversation)

    @pytest.mark.asyncio
    async def test_get_conversations(self, update, context, monkeypatch):
        user_conversation = [{'content': 'test', 'role': 'test'}]
        director = DataApiMockDirector().build_user_conversations_api([user_conversation], [False])
        mock_api_classes(monkeypatch, director)
        new_conversation_handler = ConversationHandler(update, context)
        assert await new_conversation_handler._get_conversations() == user_conversation

    def test_get_current_conversation(self, update, context):
        test_conversation_id = 1
        context.user_data['current_conversation'] = test_conversation_id
        new_conversation_handler = ConversationHandler(update, context)
        result = new_conversation_handler._get_current_conversation()
        assert result == test_conversation_id

    def test_get_text_no_current_conversation(self, update, context):
        new_conversation_handler = ConversationHandler(update, context)
        text = new_conversation_handler._get_message_text()
        assert text == MESSAGES['conversation']['no_current_conversation']

    def test_get_text_current_conversation(self, update, context): 
        test_conversation_id = 1
        context.user_data['current_conversation'] = test_conversation_id
        new_conversation_handler = ConversationHandler(update, context)
        text = new_conversation_handler._get_message_text()
        assert text == MESSAGES['conversation']['current_conversation_found'] + str(test_conversation_id)

    def test_get_new_conversation_button(self, update, context):
        new_conversation_handler = ConversationHandler(update, context)
        button = new_conversation_handler._get_new_conversation_button()
        assert isinstance(button, InlineKeyboardButton)

    @pytest.mark.asyncio
    async def test_handle(self, update, context, monkeypatch):
        user_conversation = [{'id': '1', 'name': 'test'}]
        director = DataApiMockDirector().build_user_conversations_api([user_conversation], [False])
        mock_api_classes(monkeypatch, director)
        new_conversation_handler = ConversationHandler(update, context)
        await new_conversation_handler.handle()
        assert context.bot.send_message.call_count == 3