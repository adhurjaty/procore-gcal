import pytest

import controller.request_handler as rh


class MockObject:
    def __init__(self):
        pass


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
    oauth_mock.procore = MockObject()
    rh.oauth = oauth_mock
    return oauth_mock.procore


@pytest.fixture(scope='module')
def controller_mock():
    mock_controller = MockObject()
    rh.controller = mock_controller
    return mock_controller


def test_hello_world(test_client):
    response = test_client.get('/')
    
    assert response.status_code == 200
    assert response.data == b'Hello world!'


def test_login(test_client, procore_oauth_mock):
    procore_oauth_mock.result_uri = ''
    def authorize_redirect(uri):
        procore_oauth_mock.result_uri = uri
    procore_oauth_mock.authorize_redirect = authorize_redirect

    test_client.get('/login')

    assert procore_oauth_mock.result_uri == 'http://localhost/authorize'


def test_authorize(test_client, procore_oauth_mock, controller_mock):
    sample_token = {
        'access_token': 'sample access token',
        'refresh_token': 'sample refresh token',
        'token_type': 'Bearer',
        'expires_at': 1000,
        'other_thing': 'asdfsda'
    }
    def get_token():
        return sample_token

    procore_oauth_mock.authorize_access_token = get_token

    def save_token(**token):
        controller_mock.token = token
    controller_mock.save_token = save_token

    test_client.get('/authorize')

    assert controller_mock.token == sample_token
