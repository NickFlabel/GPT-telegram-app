import pytest
from unittest import mock
from aioresponses import aioresponses
import dotenv
import os
import json

dotenv.load_dotenv()
URL_API = os.getenv('DB_API_URL')


@pytest.fixture
def update(request):
    chat_id = request.param.get('chat_id', 12345)
    user_id = request.param.get('user_id', 12345)
    username = request.param.get('username', None)
    first_name = request.param.get('first_name', None)
    last_name = request.param.get('last_name', None)
    update = mock.MagicMock()
    update.effective_chat.id = chat_id
    update.effective_user.id = user_id
    update.effective_user.username = username
    update.effective_user.first_name = first_name
    update.effective_user.last_name = last_name
    update.message.text = 'test'
    return update

@pytest.fixture
def context():
    context = mock.MagicMock()
    context.user_data = {}
    context.bot.send_message = mock.AsyncMock()
    return context


@pytest.fixture
def urls():
    with aioresponses() as mocked:
        yield mocked

