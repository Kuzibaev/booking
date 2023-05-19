import pytest
from fastapi.testclient import TestClient

from app import __version__
from app.core.conf import settings
from app.main import app


def test_version():
    assert __version__ == '0.1.0'


client = TestClient(app=app)


def test_main():
    response = client.get('/ru/api/v1/test')
    assert response.status_code == 200


@pytest.fixture
def get_token():
    post_body = {
        'phone': '+998901234567'
    }
    response = client.post('/en/api/v1/login/', json=post_body)
    return response.json()


@pytest.fixture()
def access_token(get_token):
    token = get_token['token']
    post_body = {
        'token': token,
        'code': settings.DEBUG_SMS_CODE
    }
    response = client.post('/en/api/v1/login/confirm/', json=post_body)
    assert response.status_code == 200
    return response.json()


def test_login(access_token):
    assert get_token['ok'] is True
