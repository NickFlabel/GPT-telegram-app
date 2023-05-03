from fastapi.testclient import TestClient
from .db import get_test_db, get_db, Base, test_engine
from .testing_utils import TestUser, TestMessage, TestConversation
import pytest

from .app import app

app.dependency_overrides[get_db] = get_test_db


@pytest.fixture(scope='module')
def client():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield TestClient(app)


def test_create_user(client):
    response = client.post('/users', json={'id': 1, 'username': 'test_user'})
    assert response.status_code == 201
    assert response.json() == {'id': 1, 'username': 'test_user', 'first_name': None, 'last_name': None}


def test_get_user(client):
    user = TestUser(id=2, username='test_user').create_test_user()
    response = client.get('/users/2')
    assert response.status_code == 200
    assert response.json() == {'id': user.get_user_id(), 'username': user.get_username(), 'first_name': 'test', 'last_name': 'test'}


def test_get_user_not_found(client):
    response = client.get('/users/3')
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}


def test_create_user_already_exists(client):
    response = client.post('/users', json={'id': 1, 'username': 'test_user'})
    assert response.status_code == 400
    assert response.json() == {'detail': 'User already exists'}


def test_create_conversation(client):
    user = TestUser(id=100, username='test_user').create_test_user()
    response = client.post(f'/users/{user.get_user_id()}/conversations', json={'name': 'test_conversation'})
    assert response.status_code == 201
    assert response.json() == {'id': 1, 'name': 'test_conversation'}


def test_get_conversations(client):
    user = TestUser(id=101, username='test_user').create_test_user()
    conversation = TestConversation(user_id=user.get_user_id(), name='test_conversation').create_test_conversation()
    response = client.get(f'/users/{user.get_user_id()}/conversations')
    assert response.status_code == 200
    assert response.json() == [{'id': conversation.get_conversation_id(), 'name': 'test_conversation'}]


def test_get_conversation(client):
    user = TestUser(id=102, username='test_user').create_test_user()
    conversation = TestConversation(user_id=user.get_user_id(), name='test_conversation').create_test_conversation()
    response = client.get(f'/users/{user.get_user_id()}/conversations/{conversation.get_conversation_id()}')
    assert response.status_code == 200
    assert response.json() == {'id': conversation.get_conversation_id(), 'name': 'test_conversation'}


def test_get_conversation_not_found(client):
    user = TestUser(id=103, username='test_user').create_test_user()
    response = client.get(f'/users/{user.get_user_id()}/conversations/1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Conversation not found'}


def test_get_conversation_user_not_found(client):
    response = client.get('/users/104/conversations/1')
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}


def test_create_conversation_user_not_found(client):
    response = client.post('/users/105/conversations', json={'name': 'test_conversation'})
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}


def test_create_message(client):
    user = TestUser(id=106, username='test_user').create_test_user()
    conversation = TestConversation(user_id=user.get_user_id(), name='test_conversation').create_test_conversation()
    response = client.post(f'/users/{user.get_user_id()}/conversations/{conversation.get_conversation_id()}/messages', json={'content': 'test_message', 'role': 'test'})
    assert response.status_code == 201
    assert response.json() == {'content': 'test_message', 'role': 'test'}


def test_get_messages(client):
    user = TestUser(id=107, username='test_user').create_test_user()
    conversation = TestConversation(user_id=user.get_user_id(), name='test_conversation').create_test_conversation()
    message = TestMessage(conversation_id=conversation.get_conversation_id(), content='test_message', role='test').create_test_message()
    response = client.get(f'/users/{user.get_user_id()}/conversations/{conversation.get_conversation_id()}/messages')
    assert response.status_code == 200
    assert response.json() == [{'content': message.get_content(), 'role': message.get_role()}]