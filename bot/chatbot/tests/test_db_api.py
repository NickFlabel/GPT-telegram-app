from ..data_api import User, Message, Conversation, GetUserIdMixin, GetConversationIdMixin, UserConversations, BotAnswer
import pytest
from unittest import mock
from .fixtures import update, context, urls
from .utils import URLBuilder, URLDirector, URL_API
import logging
import io


global_user_id = 1234
pytestmark = pytest.mark.parametrize('update', [{'user_id': global_user_id}], indirect=True)


class TestGetUserIdMixin:

    class GetUserIdMixinTestClass(GetUserIdMixin):

        def __init__(self, update, context):
            self.update = update
            self.context = context

    def test_get_user_id(self, update, context):
        test_class = self.GetUserIdMixinTestClass(update, context)
        assert test_class._get_user_id() == global_user_id

class TestGetConversationIdMixin:

    class GetConversationIdMixinTestClass(GetConversationIdMixin):

        def __init__(self, update, context):
            self.update = update
            self.context = context

    def test_get_conversation_id(self, update, context):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        test_class = self.GetConversationIdMixinTestClass(update, context)
        assert test_class._get_conversation_id() == conversation_id

    def test_get_conversation_id_error(self, update, context):
        test_class = self.GetConversationIdMixinTestClass(update, context)
        with pytest.raises(KeyError):
            test_class._get_conversation_id()


class TestMessage:

    def test_build_url(self, update, context):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        message = Message(update, context)
        message._build_url()
        assert message.url == f'{URL_API}/users/{global_user_id}/conversations/{conversation_id}/messages'

    @pytest.mark.asyncio
    async def test_get(self, update, context, urls):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        message_text = 'test'
        role = 'user'
        URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_get_messages_url([{"content": message_text, "role": role}], 200)
        message = Message(update, context)
        result = await message.get()
        assert result == [{"content": message_text, "role": role}]

    @pytest.mark.asyncio
    async def test_get_error(self, update, context, urls):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        message_text = 'test'
        role = 'user'
        URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_get_messages_url([{"content": message_text, "role": role}], 400)
        message = Message(update, context)
        result = await message.get()
        assert result == False

    @pytest.mark.asyncio
    async def test_post(self, update, context, urls):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        message_text = 'test'
        role = 'user'
        URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_post_message_url({"content": message_text, "role": role}, 201)
        message = Message(update, context)
        result = await message.post(message=message_text, role=role)
        assert result == {"content": message_text, "role": role}

    @pytest.mark.asyncio
    async def test_post_error(self, update, context, urls):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        message_text = 'test'
        role = 'user'
        URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_post_message_url({"content": message_text, "role": role}, 400)
        message = Message(update, context)
        result = await message.post(message=message_text, role=role)
        assert result == False


class TestUser:
    
    def test_build_url(self, update, context):
        user = User(update, context)
        user._build_url()
        assert user.url == f'{URL_API}/users/{global_user_id}'

    @pytest.mark.asyncio
    async def test_get(self, update, context, urls):
        name = 'test'
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_get_user_url({"username": name}, 200)
        user = User(update, context)
        result = await user.get()
        assert result == {"username": name}

    @pytest.mark.asyncio
    async def test_get_error(self, update, context, urls):
        name = 'test'
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_get_user_url({"username": name}, 400)
        user = User(update, context)
        result = await user.get()
        assert result == False

    @pytest.mark.asyncio
    async def test_post(self, update, context, urls):
        name = 'test'
        update.effective_user.username = name
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_post_user_url({"username": name}, 201)
        user = User(update, context)
        result = await user.post()
        assert result == {"username": name}

    @pytest.mark.asyncio
    async def test_post_error(self, update, context, urls):
        name = 'test'
        update.effective_user.username = name
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_post_user_url({"username": name}, 400)
        user = User(update, context)
        result = await user.post()
        assert result == False


class TestConversation:
    
    def test_build_url(self, update, context):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        conversation = Conversation(update, context)
        conversation._build_url()
        assert conversation.url == f'{URL_API}/users/{global_user_id}/conversations/{conversation_id}'

    @pytest.mark.asyncio
    async def test_get(self, update, context, urls):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        name = 'test'
        URLBuilder(urls, user_id=global_user_id, conversation_id=conversation_id).build_get_conversation_url({"name": name, "id": conversation_id}, 200)
        conversation = Conversation(update, context)
        result = await conversation.get()
        assert result == {"name": name, "id": conversation_id}

    @pytest.mark.asyncio
    async def test_get_error(self, update, context, urls):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        URLBuilder(urls, user_id=global_user_id, conversation_id=conversation_id).build_get_conversation_url({}, 400)
        conversation = Conversation(update, context)
        result = await conversation.get()
        assert result == False

    @pytest.mark.asyncio
    async def test_delete(self, update, context, urls):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        URLBuilder(urls, user_id=global_user_id, conversation_id=conversation_id).build_delete_conversation_url(204)
        conversation = Conversation(update, context)
        result = await conversation.delete()
        assert result == True

    @pytest.mark.asyncio
    async def test_delete_error(self, update, context, urls):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        URLBuilder(urls, user_id=global_user_id, conversation_id=conversation_id).build_delete_conversation_url(400)
        conversation = Conversation(update, context)
        result = await conversation.delete()
        assert result == False


class TestUserConversations:

    def test_build_url(self, update, context):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        user_conversations = UserConversations(update, context)
        user_conversations._build_url()
        assert user_conversations.url == f'{URL_API}/users/{global_user_id}/conversations'

    @pytest.mark.asyncio
    async def test_get(self, update, context, urls):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        name = 'test'
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_get_conversations_url([{"name": name, "id": conversation_id}], 200)
        user_conversations = UserConversations(update, context)
        result = await user_conversations.get()
        assert result == [{"name": name, "id": conversation_id}]

    @pytest.mark.asyncio
    async def test_get_error(self, update, context, urls):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_get_conversations_url([], 400)
        user_conversations = UserConversations(update, context)
        result = await user_conversations.get()
        assert result == False

    @pytest.mark.asyncio
    async def test_post(self, update, context, urls):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        name = 'test'
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_post_conversations_url({"name": name, "id": conversation_id}, 201)
        user_conversations = UserConversations(update, context)
        result = await user_conversations.post({"name": name, "id": conversation_id})
        assert result == {"name": name, "id": conversation_id}

    @pytest.mark.asyncio
    async def test_post_error(self, update, context, urls):
        conversation_id = 1
        context.user_data['current_conversation'] = conversation_id
        name = 'test'
        URLBuilder(urls, user_id=global_user_id, conversation_id=None).build_post_conversations_url({"name": name, "id": conversation_id}, 400)
        user_conversations = UserConversations(update, context)
        result = await user_conversations.post({"name": name, "id": conversation_id})
        assert result == False


class TestBotAnswer:

    def test_get_message(self, update, context):
        update.message.text = 'test'
        new_answer = BotAnswer(update=update, context=context)
        result = new_answer._get_message()
        assert result == update.message.text

    @pytest.mark.asyncio
    async def test_post(self, update, context, urls):
        messages = []
        URLBuilder(mocked=urls, user_id=None, conversation_id=None).build_openai_url(body={"choices": [{"message": {"content": "test", "role": "assistant"}}]}, status=200)
        answer = await BotAnswer(update=update, context=context).post(messages=messages)
        assert answer == 'test'

    @pytest.mark.asyncio
    async def test_post_fail(self, update, context, urls):
        messages = []
        URLBuilder(mocked=urls, user_id=None, conversation_id=None).build_openai_url(body={}, status=400)
        answer = await BotAnswer(update=update, context=context).post(messages=messages)
        assert answer == False
