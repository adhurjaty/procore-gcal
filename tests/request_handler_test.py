import pytest
import json
import os
from pathlib import Path

import controller.request_handler as rh
import controller.api_endpoints as endpoints
from .mocks import OauthMock, MockObject, OauthResponseMock, ControllerMock
from interactor.account_manager_dto import AccountManagerDto

objects_path = os.path.join(Path(os.path.realpath(__file__)).parent, 'objects')


@pytest.fixture(scope='module')
def controller_mock() -> ControllerMock:
    mock_controller = ControllerMock()
    rh.controller = mock_controller

    return mock_controller


@pytest.fixture(scope='module')
def test_client(controller_mock):
    app = rh.create_app(controller_mock)

    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


@pytest.fixture(scope='module')
def procore_oauth_mock() -> OauthMock:
    oauth_mock = MockObject()
    oauth_mock.procore = OauthMock()
    rh.oauth = oauth_mock
    return oauth_mock.procore


@pytest.fixture(scope='module')
def user_controller_mock(controller_mock) -> ControllerMock:
    manager = AccountManagerDto()
    manager.id = 69
    manager.email = 'sean@example.com'
    manager.full_name = 'Sean Black'
    manager.project_id = 12345
    controller_mock.set_manager(manager)
    
    return controller_mock
    

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
    manager.email = 'sean@example.com'
    manager.full_name = 'Sean Black'
    controller_mock.set_manager(manager)

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

    resp = test_client.get('/authorize')

    assert resp.status_code == 401
    assert resp.json == {
        'result': 'error',
        'error': 'User does not exist'
    }


def test_authorize_signup(test_client, procore_oauth_mock, controller_mock):
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

    resp = test_client.get('/authorize?new_user=True')

    assert controller_mock.manager.email == 'sean@example.com'
    assert controller_mock.manager.full_name == 'Sean Black'
    assert controller_mock.manager.procore_token.access_token == 'sample access token'
    assert resp.status_code == 200


def test_authorize_signup_existing_user(test_client, procore_oauth_mock, controller_mock):
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
    manager.email = 'sean@example.com'
    manager.full_name = 'Sean Black'
    controller_mock.set_manager(manager)

    resp = test_client.get('/authorize?new_user=True')

    assert resp.status_code == 403
    assert resp.json == {
        'result': 'error',
        'error': 'User already exists'
    }


def test_submittal_webhook(test_client, procore_oauth_mock, controller_mock):
    manager = AccountManagerDto()
    manager.id = 69
    manager.email = 'sean@example.com'
    manager.full_name = 'Sean Black'
    manager.project_id = 12345
    controller_mock.set_manager(manager)

    def get_resource(uri):
        assert uri == '/vapid/projects/12345/submittals/838383'
        with open(os.path.join(objects_path, 'submittal.json'), 'r') as f:
            resp = json.load(f)
        return OauthResponseMock(resp)

    procore_oauth_mock.get = get_resource

    webhook_data = {
        'user_id': 66789,
        'timestamp': 1538866,
        'resource_name': 'Submittals',
        'resource_id': 838383,
        'project_id': 12345,
        'event_type': 'create',
        'company_id': 8796,
        'api_version': 'v2',
        "metadata": {
            "source_user_id": 1245,
            "source_company_id": 891,
            "source_project_id": 123,
            "source_application_id": "242635f69bfc6fb9adax513875a0254a2a123f7bb176x1698d6x169a08f5646d",
            "source_operation_id": "0181c891-8be7-4f99-8c4e-9f12347d6ecd"
        }
    }

    def update_gcal(users, data):
        assert len(users) == 1
        assert data['title'] == "Smiths - Teardown & Assembly Bldg"
        controller_mock.updated_gcal = True

    controller_mock.update_gcal = update_gcal
    controller_mock.get_users_in_project = lambda pid: [AccountManagerDto()]

    resp = test_client.post('/webhook_handler', json=webhook_data)

    assert resp.status_code == 200
    assert controller_mock.updated_gcal

