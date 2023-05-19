from ..utils import NewCoversation, CurrentConversation, get_user_data, user_checker_decorator, get_callback_data
import pytest
from .fixtures import update, context, urls
from .utils import URLBuilder, URLDirector, URL_API
import asyncio


class TestNewConversation:
    
    def test_new_conversation_get_is_beign_created_false(self, context):
        is_created = NewCoversation.get_new_conversation_is_being_created(context)
        assert is_created == False


    def test_new_conversation_get_is_beign_created_true(self, context):
        context.user_data['is_creating_conversation'] = True
        is_created = NewCoversation.get_new_conversation_is_being_created(context)
        assert is_created == True


    def test_set_new_conversation_is_being_created_true(self, context):
        NewCoversation.set_new_conversation_is_being_created(context, True)
        assert context.user_data['is_creating_conversation'] == True


    @pytest.mark.asyncio
    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    async def test_new_conversation_create_new_conversation(self, update, urls):
        user_id = update.effective_user.id
        URLBuilder(mocked=urls, conversation_id=1, user_id=user_id).build_post_conversations_url(body={"name": "test", "id": 1}, status=201)
        update.message.text = 'test'
        result = await NewCoversation.create_new_conversation(user_id=user_id, message=update.message.text)
        assert result == {'name': 'test', 'id': 1}


    @pytest.mark.asyncio
    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    async def test_new_conversation_create_new_conversation_error(self, update, urls):
        user_id = update.effective_user.id
        URLBuilder(mocked=urls, conversation_id=1, user_id=user_id).build_post_conversations_url(body={"name": "test", "id": 1}, status=400)
        update.message.text = 'test'
        result = await NewCoversation.create_new_conversation(user_id=user_id, message=update.message.text)
        assert result == False


class TestCurrentConversation:

    def test_get_current_conversation(self, context):
        context.user_data['current_conversation'] = 1
        current_conversation = CurrentConversation(update, context)
        assert current_conversation.get_current_conversation() == 1

    def test_get_current_conversation_none(self, context):
        current_conversation = CurrentConversation(update, context)
        assert current_conversation.get_current_conversation() == None

    def test_set_current_conversation(self, context):
        current_conversation = CurrentConversation(update, context)
        current_conversation.set_current_conversation(1)
        assert context.user_data['current_conversation'] == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    async def test_check_current_conversation(self, update, urls, context):
        context.user_data['current_conversation'] = 1
        user_id = update.effective_user.id
        URLBuilder(mocked=urls, conversation_id=1, user_id=user_id).build_get_conversation_url(body={"name": "test", "id": 1}, status=200)
        current_conversation = CurrentConversation(update, context)
        result = await current_conversation._check_current_conversation()
        assert result == {'name': 'test', 'id': 1}



class TestUtilFunctions:

    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    def test_get_user_data(self, update):
        user_data = get_user_data(update)
        assert user_data == {'user_id': 1234, 'username': None, 'first_name': None, 'last_name': None}

    @pytest.mark.asyncio
    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    @pytest.mark.parametrize('number_of_calls, with_message', [(1, True), (1, False)])
    async def test_user_checker_decorator_without_user(self, update, context, urls, with_message, number_of_calls):
        URLDirector(mocked=urls, user_id=1234).build_user_routine_no_user()
        @user_checker_decorator(with_message=with_message)
        async def test_func(update, context):
            return True
        result =  await test_func(update, context)
        assert result == True
        assert context.bot.send_message.call_count == number_of_calls
        urls.assert_called_with(f'{URL_API}/users/1234', method='GET')
        urls.assert_called_with(f'{URL_API}/users', method='POST', json={"id": 1234, "username": None, "first_name": None, "last_name": None})


    @pytest.mark.asyncio
    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    @pytest.mark.parametrize('number_of_calls, with_message', [(1, True), (0, False)])
    async def test_user_checker_decorator_with_user(self, update, context, urls, number_of_calls, with_message):
        URLDirector(mocked=urls, user_id=1234).build_user_routine_with_user()
        @user_checker_decorator(with_message=with_message)
        async def test_func(update, context):
            return True
        result =  await test_func(update, context)
        assert result == True
        assert context.bot.send_message.call_count == number_of_calls
        urls.assert_called_with(f'{URL_API}/users/1234', method='GET')

    @pytest.mark.parametrize('update', [{'user_id': 1234}], indirect=True)
    def test_get_callback_data(self, update):
        update.callback_query.data = 'test_test_1'
        callback_data = get_callback_data(update)
        assert callback_data == {'action': 'test', 'name': 'test', 'id': 1}
