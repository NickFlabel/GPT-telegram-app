from ..utils import NewCoversation, CurrentConversation, get_user_data, user_checker_decorator, get_callback_data
from ..data_api import Message, Conversation, UserConversations
import pytest
from .fixtures import update, context, urls
from .utils import URLBuilder, URLDirector, URL_API
import asyncio


class TestNewConversation:
    
    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    def test_new_conversation_get_is_beign_created_false(self, context, update):
        is_created = NewCoversation(UserConversations, update, context).get_new_conversation_is_being_created()
        assert is_created == False

    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    def test_new_conversation_get_is_beign_created_true(self, update, context):
        context.user_data['is_creating_conversation'] = True
        is_created = NewCoversation(UserConversations, update, context).get_new_conversation_is_being_created()
        assert is_created == True


    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    def test_set_new_conversation_is_being_created_true(self, update, context):
        NewCoversation(UserConversations, update, context).set_new_conversation_is_being_created(True)
        assert context.user_data['is_creating_conversation'] == True


    @pytest.mark.asyncio
    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    async def test_new_conversation_create_new_conversation(self, update, context, urls):
        user_id = update.effective_user.id
        URLBuilder(mocked=urls, conversation_id=1, user_id=user_id).build_post_conversations_url(body={"name": "test", "id": 1}, status=201)
        update.message.text = 'test'
        result = await NewCoversation(UserConversations, update, context).create_new_conversation()
        assert result == {'name': 'test', 'id': 1}


    @pytest.mark.asyncio
    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    async def test_new_conversation_create_new_conversation_error(self, update, context, urls):
        user_id = update.effective_user.id
        URLBuilder(mocked=urls, conversation_id=1, user_id=user_id).build_post_conversations_url(body={"name": "test", "id": 1}, status=400)
        update.message.text = 'test'
        result = await NewCoversation(UserConversations, update, context).create_new_conversation()
        assert result == False


class TestCurrentConversation:

    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    def test_get_current_conversation(self, update, context):
        context.user_data['current_conversation'] = 1
        current_conversation = CurrentConversation(Conversation, UserConversations, update, context)
        assert current_conversation.get_current_conversation() == 1

    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    def test_get_current_conversation_none(self, update, context):
        current_conversation = CurrentConversation(Conversation, UserConversations, update, context)
        assert current_conversation.get_current_conversation() == None

    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    def test_set_current_conversation(self, update, context):
        current_conversation = CurrentConversation(Conversation, UserConversations, update, context)
        current_conversation.set_current_conversation(1)
        assert context.user_data['current_conversation'] == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    async def test_check_current_conversation(self, update, urls, context):
        context.user_data['current_conversation'] = 1
        user_id = update.effective_user.id
        URLBuilder(mocked=urls, conversation_id=1, user_id=user_id).build_get_conversation_url(body={"name": "test", "id": 1}, status=200)
        current_conversation = CurrentConversation(Conversation, UserConversations, update, context)
        result = await current_conversation._check_current_conversation()
        assert result == True



class TestUtilFunctions:

    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    def test_get_callback_data(self, update):
        update.callback_query.data = 'test_test_1'
        callback_data = get_callback_data(update)
        assert callback_data == {'action': 'test', 'name': 'test', 'id': 1}
