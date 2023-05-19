from ..gpt_api import get_answer_from_gpt_3_5
import pytest
from .fixtures import update, context, urls
from .utils import URLBuilder, URLDirector


@pytest.mark.asyncio
async def test_get_answer_from_gpt_3_5(urls):
    URLBuilder(mocked=urls, user_id=None, conversation_id=None).build_openai_url(body={"choices": [{"message": {"content": "test", "role": "assistant"}}]}, status=200)
    answer = await get_answer_from_gpt_3_5('test', [])
    assert answer == 'test'
    