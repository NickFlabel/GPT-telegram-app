from ..db_api import User, Message, Conversation
import pytest
from .fixtures import update, context, urls
from .utils import URLBuilder, URLDirector

global_user_id = 1234
pytestmark = pytest.mark.parametrize('update', [{'user_id': global_user_id}], indirect=True)

class TestMessage:

    @pytest.mark.asyncio
    async def test_create_message(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_post_message_url({"content": "test", "role": "user"}, 201)
        message = Message('test', 1, global_user_id)
        result = await message.create_message('user')
        assert result == {'content': 'test', 'role': 'user'}

    @pytest.mark.asyncio
    async def test_create_message_error(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_post_message_url({"content": "test", "role": "user"}, 400)
        message = Message('test', 1, global_user_id)
        result = await message.create_message('user')
        assert result == False


class TestUser:

    @pytest.mark.asyncio
    async def test_get_user(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_get_user_url({"id": global_user_id, "username": None, "first_name": None, "last_name": None}, 200)
        user = User(1234)
        result = await user.get_user()
        assert result == {'id': global_user_id, 'username': None, 'first_name': None, 'last_name': None}

    @pytest.mark.asyncio
    async def test_get_user_error(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_get_user_url({"id": global_user_id, "username": None, "first_name": None, "last_name": None}, 400)
        user = User(global_user_id)
        result = await user.get_user()
        assert result == False

    @pytest.mark.asyncio
    async def test_create_user(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_post_user_url({"id": global_user_id, "username": None, "first_name": None, "last_name": None}, 201)
        user = User(global_user_id)
        result = await user.create_user()
        assert result == {'id': global_user_id, 'username': None, 'first_name': None, 'last_name': None}

    @pytest.mark.asyncio
    async def test_create_user_error(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_post_user_url({"id": global_user_id, "username": None, "first_name": None, "last_name": None}, 400)
        user = User(global_user_id)
        result = await user.create_user()
        assert result == False


class TestConversation:

    @pytest.mark.asyncio
    async def test_get_conversations(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_get_conversations_url([{"name": "test", "id": 1}], 200)
        conversation = Conversation(global_user_id)
        result = await conversation.get_conversations()
        assert result == [{'name': 'test', 'id': 1}]

    @pytest.mark.asyncio
    async def test_get_conversations_error(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_get_conversations_url([{"name": "test", "id": 1}], 400)
        conversation = Conversation(global_user_id)
        result = await conversation.get_conversations()
        assert result == False

    @pytest.mark.asyncio
    async def test_check_conversation(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_get_conversation_url({"name": "test", "id": 1}, 200)
        conversation = Conversation(global_user_id)
        result = await conversation.check_conversation_by_id(1)
        assert result == {'name': 'test', 'id': 1}
    
    @pytest.mark.asyncio
    async def test_check_conversation_error(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_get_conversation_url({"name": "test", "id": 1}, 400)
        conversation = Conversation(global_user_id)
        result = await conversation.check_conversation_by_id(1)
        assert result == False

    @pytest.mark.asyncio
    async def test_get_conversation(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_get_messages_url([{"content": "test", "role": "user"}], 200)
        conversation = Conversation(global_user_id)
        result = await conversation.get_conversation(1)
        assert result == [{'content': 'test', 'role': 'user'}]

    @pytest.mark.asyncio
    async def test_get_conversation_error(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_get_messages_url([{"content": "test", "role": "user"}], 400)
        conversation = Conversation(global_user_id)
        result = await conversation.get_conversation(1)
        assert result == False

    @pytest.mark.asyncio
    async def test_create_conversation(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_post_conversations_url({"name": "test", "id": 1}, 201)
        conversation = Conversation(global_user_id)
        result = await conversation.create_conversation('test')
        assert result == {'name': 'test', 'id': 1}

    @pytest.mark.asyncio
    async def test_create_conversation_error(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_post_conversations_url({"name": "test", "id": 1}, 400)
        conversation = Conversation(global_user_id)
        result = await conversation.create_conversation('test')
        assert result == False

    @pytest.mark.asyncio
    async def test_delete_conversation(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_delete_conversation_url(204)
        conversation = Conversation(global_user_id)
        result = await conversation.delete_conversation(1)
        assert result == True

    @pytest.mark.asyncio
    async def test_delete_conversation_error(self, update, context, urls):
        URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_delete_conversation_url(400)
        conversation = Conversation(global_user_id)
        result = await conversation.delete_conversation(1)
        assert result == False