import pytest

import controller.request_handler as rh
from .mocks import OauthMock, MockObject, OauthResponseMock
from interactor.account_manager_dto import AccountManagerDto

@pytest.fixture(scope='module')
def test_client():
    app = rh.app

    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


@pytest.fixture(scope='module')
def procore_oauth_mock():
    oauth_mock = MockObject()
    oauth_mock.procore = OauthMock()
    rh.oauth = oauth_mock
    return oauth_mock.procore


@pytest.fixture(scope='module')
def controller_mock():
    mock_controller = MockObject()
    rh.controller = mock_controller
    mock_controller.update_user = lambda u: {}
    mock_controller.create_user = lambda u: {}

    return mock_controller


def test_hello_world(test_client):
    response = test_client.get('/')
    
    assert response.status_code == 200
    assert response.data == b'Hello world!'


def test_login(test_client, procore_oauth_mock):
    test_client.get('/login')

    assert procore_oauth_mock.redirect_uri == 'http://localhost/authorize'


def test_register(test_client, procore_oauth_mock):
    test_client.get('/register')

    assert procore_oauth_mock.redirect_uri == 'http://localhost/authorize?new_user=True'


def test_authorize_login(test_client, procore_oauth_mock, controller_mock):
    sample_token = {
        'access_token': 'sample access token',
        'refresh_token': 'sample refresh token',
        'token_type': 'Bearer',
        'expires_at': 1000,
        'other_thing': 'asdfsda'
    }
    procore_oauth_mock.set_token(sample_token)
    procore_oauth_mock.get = lambda endpoint: OauthResponseMock({
        'id': 42,
        'login': 'sean@example.com',
        'name': 'Sean Black'
    })

    manager = AccountManagerDto()
    manager.id = 69
    def get_manager(**user):
        manager.email = user['login']
        manager.full_name = user['name']
        return manager

    controller_mock.get_account_manager = get_manager

    resp = test_client.get('/authorize')

    assert manager.procore_token.access_token == 'sample access token'
    assert manager.procore_token.refresh_token == 'sample refresh token'
    assert manager.procore_token.token_type == 'Bearer'
    assert manager.procore_token.expires_at == 1000
    assert resp.json == {
        'result': 'success'
    }


def test_authorize_login_no_user(test_client, procore_oauth_mock, controller_mock):
    sample_token = {
        'access_token': 'sample access token',
        'refresh_token': 'sample refresh token',
        'token_type': 'Bearer',
        'expires_at': 1000,
        'other_thing': 'asdfsda'
    }
    procore_oauth_mock.set_token(sample_token)
    procore_oauth_mock.get = lambda endpoint: OauthResponseMock({
        'id': 42,
        'login': 'sean@example.com',
        'name': 'Sean Black'
    })

    controller_mock.get_account_manager = lambda **_: None

    resp = test_client.get('/authorize')

    assert resp.status_code == 401
    assert resp.json == {
        'result': 'error',
        'error': 'User does not exist'
    }
