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
