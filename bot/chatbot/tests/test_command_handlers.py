from ..command_handlers import start, message
import pytest
from unittest import mock
import dotenv
import os
from aioresponses import aioresponses
from .fixtures import update, context, urls
import json
from .utils import URLDirector

global_user_id = 1234
pytestmark = pytest.mark.parametrize('update', [{'user_id': global_user_id}], indirect=True)

dotenv.load_dotenv()
URL_API = os.getenv('DB_API_URL')
API_KEY = os.getenv('OPEN_AI_KEY')

with open('messages.json', 'r') as f:
    MESSAGES = json.load(f)

class TestStart:
    
    @pytest.mark.asyncio
    async def test_start_user_is_not_created(self, update, context, urls):
        URLDirector(urls, user_id=global_user_id, conversation_id=None).build_user_routine_no_user()
        result = await start(update, context)
        assert result == None
        assert context.bot.send_message.call_count == 2
        assert context.bot.send_message.call_args_list[0][1]['text'] == MESSAGES['user']['creating']

    @pytest.mark.asyncio
    async def test_start_user_is_created(self, update, context, urls):
        URLDirector(urls, user_id=global_user_id, conversation_id=None).build_user_routine_with_user()
        result = await start(update, context)
        assert result == None
        assert context.bot.send_message.call_count == 2
        assert context.bot.send_message.call_args_list[0][1]['text'] == MESSAGES['user']['found']


class TestMessage:
    
    pass
