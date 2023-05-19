from .. import callback_handlers
from .fixtures import update, context, urls
import pytest
from .utils import URLDirector, URLBuilder
from ..gpt_api import get_answer_from_gpt_3_5

global_user_id = 1234
pytestmark = pytest.mark.parametrize('update', [{'user_id': global_user_id}], indirect=True)

@pytest.mark.asyncio
async def test_callback_handler_conversation_options(context, update):
    await callback_handlers.conversation_options(update, context, 1, conversation_name='test')
    assert context.bot.send_message.call_count == 1

@pytest.mark.asyncio
async def test_delete_conversation(context, update, urls):
    URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_delete_conversation_url(status=204)
    result = await callback_handlers.delete_conversation(update, context, 1)
    assert result == True
    assert context.bot.send_message.call_count == 1

@pytest.mark.asyncio
async def test_delete_conversation_error(context, update, urls):
    URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_delete_conversation_url(status=400)
    result = await callback_handlers.delete_conversation(update, context, 1)
    assert result == False
    assert context.bot.send_message.call_count == 0

@pytest.mark.asyncio
async def test_choose_conversation(context, update):
    await callback_handlers.choose_conversation(update, context, 1)
    assert context.bot.send_message.call_count == 1

@pytest.mark.asyncio
async def test_create_conversation(context, update):
    await callback_handlers.create_conversation(update, context)
    assert context.bot.send_message.call_count == 1
    assert context.user_data['is_creating_conversation'] == True

@pytest.mark.asyncio
async def test_view_conversation(context, update, urls):
    URLBuilder(urls, user_id=global_user_id, conversation_id=1).build_get_messages_url(status=200, body=[{'role': 'user', 'content': 'test'}, {'role': 'assistant', 'content': 'test'}])
    await callback_handlers.view_conversation(update, context, 1)
    assert context.bot.send_message.call_count == 2
