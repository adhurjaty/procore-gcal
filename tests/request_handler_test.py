import pytest
import json
import os
from pathlib import Path
import re

from .mocks import OauthMock, MockObject, OauthResponseMock, ControllerMock
import controller.request_handler as rh
import controller.api_endpoints as endpoints
from interactor.account_manager_dto import AccountManagerDto
from interactor.user_dto import UserDto
from models.account_manager import AccountManager
from models.collaborator_user import CollaboratorUser

objects_path = os.path.join(Path(os.path.realpath(__file__)).parent, 'objects')


def sample_account_mananger():
    manager = AccountManagerDto(AccountManager())
    manager.id = 69
    manager.email = 'sean@example.com'
    manager.full_name = 'Sean Black'
    manager.project_id = 12345
    return manager


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
def gcal_oauth_mock() -> OauthMock:
    oauth_mock = MockObject()
    oauth_mock.gcal = OauthMock()
    rh.oauth = oauth_mock
    return oauth_mock.gcal


@pytest.fixture(scope='module')
def user_controller_mock(controller_mock) -> ControllerMock:
    controller_mock.set_manager(sample_account_mananger())
    
    return controller_mock


@pytest.fixture(scope='module')
def collab_controller_mock(controller_mock) -> ControllerMock:
    collab = UserDto(CollaboratorUser())
    collab.id = 70
    collab.email = 'sean@example.com'
    collab.full_name = 'Sean Black'
    controller_mock.get_collaborator = lambda x: collab
    
    return controller_mock


def test_login(test_client, procore_oauth_mock):
    test_client.get(rh.LOGIN_ROUTE)

    assert procore_oauth_mock.redirect_uri == 'http://localhost/authorize'


def test_authorize_login(test_client, procore_oauth_mock, controller_mock):
    sample_token = {
        'access_token': 'sample access token',
        'refresh_token': 'sample refresh token',
        'token_type': 'Bearer',
        'expires_at': 1000,
        'other_thing': 'asdfsda'
    }
    procore_oauth_mock.set_token(sample_token)

    def get_user(token):
        user = sample_account_mananger()
        user.temporary = True
        return user

    controller_mock.init_user = get_user

    resp = test_client.get(rh.PROCORE_AUTH_ROUTE, follow_redirects=False)

    assert resp.status_code == 302
    assert resp.location == f'{get_front_end_domain(test_client)}/users/69'
    cookie = resp.headers.get('Set-Cookie')
    assert extract_cookie(cookie, 'auth_token') == 'sample access token'


def test_authorize_signup(test_client, procore_oauth_mock, controller_mock):
    validations = MockObject()
    validations.user = None
    
    sample_token = {
        'access_token': 'sample access token',
        'refresh_token': 'sample refresh token',
        'token_type': 'Bearer',
        'expires_at': 1000,
        'other_thing': 'asdfsda'
    }
    procore_oauth_mock.set_token(sample_token)

    def init_user(token):
        user = sample_account_mananger()
        user.id = '42'
        user.email = 'sean@example.com'
        user.full_name = 'Sean Black'
        validations.user = user
        return user

    controller_mock.init_user = init_user

    resp = test_client.get(rh.PROCORE_AUTH_ROUTE, follow_redirects=False)

    assert resp.status_code == 302
    assert resp.location == f'{get_front_end_domain(test_client)}/users/42'
    cookie = resp.headers.get('Set-Cookie')
    assert extract_cookie(cookie, 'auth_token') == 'sample access token'
    assert validations.user.full_name == 'Sean Black'


def test_submittal_webhook(test_client, controller_mock):
    validations = MockObject()
    validations.project_id = 0
    validations.resource_name = ''
    validations.resource_id = ''

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

    def update_gcal(**data):
        validations.project_id = data.get('project_id')
        validations.resource_name = data.get('resource_name')
        validations.resource_id = data.get('resource_id')

    controller_mock.update_gcal = update_gcal

    resp = test_client.post(rh.WEBHOOK_HANDLER_ROUTE, json=webhook_data)

    assert resp.status_code == 200
    assert validations.project_id == 12345
    assert validations.resource_name == 'Submittals'
    assert validations.resource_id == 838383


def test_gcal_login(test_client, user_controller_mock, gcal_oauth_mock):
    test_client.get(f'{rh.GCAL_LOGIN_ROUTE}?auth_token=accesstoken', follow_redirects=False)

    assert gcal_oauth_mock.redirect_uri == f'http://localhost{rh.GCAL_AUTH_ROUTE}'


def test_update_gcal_token(test_client, gcal_oauth_mock, user_controller_mock):
    verifications = MockObject()
    verifications.user = None

    sample_token = {
        'access_token': 'sample access token',
        'refresh_token': 'sample refresh token',
        'token_type': 'Bearer',
        'expires_at': 1000,
    }

    gcal_oauth_mock.authorize_access_token = lambda: sample_token

    def on_update(user):
        verifications.user = user

    user_controller_mock.update_user = on_update

    test_client.get(rh.GCAL_AUTH_ROUTE, query_string={'state': 'blah'})

    assert verifications.user.gcal_data.token.access_token == 'sample access token'
    assert verifications.user.gcal_data.token.refresh_token == 'sample refresh token'
    assert verifications.user == user_controller_mock.manager


def test_update_collab_gcal_token(test_client, gcal_oauth_mock, collab_controller_mock):
    verifications = MockObject()
    verifications.user = None

    sample_token = {
        'access_token': 'sample access token',
        'refresh_token': 'sample refresh token',
        'token_type': 'Bearer',
        'expires_at': 1000,
    }

    gcal_oauth_mock.authorize_access_token = lambda: sample_token

    def on_update(user):
        verifications.user = user

    collab_controller_mock.update_user = on_update

    test_client.get(rh.GCAL_AUTH_ROUTE, query_string={'collaborator_id': '70'})

    assert verifications.user.gcal_data.token.access_token == 'sample access token'
    assert verifications.user.gcal_data.token.refresh_token == 'sample refresh token'
    assert verifications.user == collab_controller_mock.get_collaborator(70)


def test_update_gcal_error(test_client, gcal_oauth_mock, user_controller_mock):
    verifications = MockObject()
    verifications.user = None

    sample_token = {
        'access_token': 'sample access token',
        'refresh_token': 'sample refresh token',
        'token_type': 'Bearer',
        'expires_at': 1000,
    }

    gcal_oauth_mock.authorize_access_token = lambda: sample_token

    def on_update(user):
        verifications.user = user

    user_controller_mock.update_user = on_update

    resp = test_client.get(rh.GCAL_AUTH_ROUTE)

    assert resp.status_code == 400
    assert resp.json['message'] == 'Malformed redirect URL'


def test_update_user(test_client, user_controller_mock):
    verifications = MockObject()
    verifications.user = None
    verifications.user_data = None

    test_data = {
        'id': 69,
        'fullName': 'Anil Dhurjaty'
    }

    def test_update(user, data):
        verifications.user = user
        verifications.data = data

    user_controller_mock.update_user = test_update 

    test_client.patch('/users/69', json=test_data, 
        headers={'Authorization': 'Bearer token'})

    assert verifications.user == user_controller_mock.manager
    assert verifications.data == test_data


def test_delete_user(test_client, user_controller_mock):
    verifications = MockObject()
    verifications.user_id = None

    def test_delete(user_id):
        verifications.user_id = user_id

    user_controller_mock.delete_user = test_delete 

    test_client.delete('/users/69', headers={'Authorization': 'Bearer token'})

    assert verifications.user_id == '69'


def test_update_user_not_logged_in(test_client, controller_mock):
    verifications = MockObject()
    verifications.user = None
    verifications.user_data = None

    test_data = {
        'id': 69,
        'fullName': 'Anil Dhurjaty'
    }

    def test_update(user, data):
        verifications.user = user
        verifications.data = data

    user_controller_mock.update_user = test_update 

    resp = test_client.patch('/users/69', json=test_data)

    assert resp.status_code == 401


def test_get_account_manager(test_client, user_controller_mock):
    validations = MockObject()
    validations.user = None
    
    def get_manager(user):
        validations.user = user
        return {'test': 'succeed'}
        
    user_controller_mock.get_manager = get_manager

    resp = test_client.get('/users/44', 
        headers={'Authorization': 'Bearer token'})

    assert resp.status_code == 200
    assert resp.json['test'] == 'succeed'
    assert validations.user == user_controller_mock.manager
    

def get_front_end_domain(client):
    return client.application.config.get('FRONT_END_DOMAIN')


def extract_cookie(text, key):
    matches = re.findall(key + r'="(.*?)";', text)
    return matches and matches[0]
