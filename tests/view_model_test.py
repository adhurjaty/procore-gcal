import pytest
import os
from pathlib import Path

from controller.gcal_view_model import GCalViewModel
from controller.procore_view_model import ProcoreViewModel
import controller.server_connector as server_connector
import controller.api_endpoints as endpoints
from .mocks import OauthMock, MockObject, OauthResponseMock, ControllerMock
from interactor.account_manager_dto import AccountManagerDto

objects_path = os.path.join(Path(os.path.realpath(__file__)).parent, 'objects')


@pytest.fixture(scope='session', autouse=True)
def define_url_for_webhooks():
    server_connector.url_for_webhooks = 'http://localhost/webhook_handler'


@pytest.fixture()
def oauth_mock():
    mock = OauthMock()
    return mock


@pytest.fixture()
def sample_user():
    manager = AccountManagerDto()
    manager.id = 69
    manager.email = 'sean@example.com'
    manager.full_name = 'Sean Black'
    manager.project_id = 12345
    return manager


@pytest.fixture()
def procore_vm(oauth_mock, sample_user):
    vm = ProcoreViewModel(sample_user)
    vm.oauth = oauth_mock
    return vm

@pytest.fixture(scope='module')
def sample_procore_event():
    pass


def test_create_new_webhooks(oauth_mock, sample_user, procore_vm):
    verifications = MockObject()
    verifications.hook_created = False
    verifications.triggers = []

    hook = {
        "id": 43593499,
        "api_version": "v2",
        "destination_url": "http://localhost/webhook_handler",
        "owned_by_company_id": 5358233,
        "owned_by_project_id": 12345,
        "owned_by_user_id": 222,
        "namespace": "procore"
    }

    def get(uri):
        return OauthResponseMock([])

    def post(uri, json={}):
        if uri == endpoints.PROCORE_WEBHOOKS:
            verifications.hook_created = True
            return hook
            
        verifications.triggers.append(json)
    
    oauth_mock.get = get
    oauth_mock.post = post

    sample_user.procore_data.calendar_event_types = {
        'RFIs': True,
        'Submittals': True,
        'Events': False
    }

    procore_vm.register_webhooks()

    assert verifications.hook_created
    assert set((d['trigger']['resource_name'], d['trigger']['event_type'])
        for d in verifications.triggers) == {
            ('RFIs', 'create'),
            ('RFIs', 'update'),
            ('RFIs', 'delete'),
            ('Submittals', 'create'),
            ('Submittals', 'update'),
            ('Submittals', 'delete'),
        }


def test_add_to_existing_webhooks(oauth_mock, sample_user, procore_vm):
    verifications = MockObject()
    verifications.hook_created = False
    verifications.triggers = []

    hook = {
        "id": 43593499,
        "api_version": "v2",
        "destination_url": "http://localhost/webhook_handler",
        "owned_by_company_id": 5358233,
        "owned_by_project_id": 12345,
        "owned_by_user_id": 222,
        "namespace": "procore"
    }

    trigger_template = lambda method: {
        "id": 231346546,
        "webhook_hook_id": 43593499,
        "resource_name": "Project Users",
        "resource_id": 43597433,
        "event_type": method,
        "company_id": 5358233,
        "project_id": 12345,
        "user_id": 42
    }

    def get(uri):
        if uri == endpoints.PROCORE_WEBHOOKS:
            return OauthResponseMock([hook])
        if uri == endpoints.PROCORE_TRIGGERS.format(hook_id=43593499):
            return OauthResponseMock([
                trigger_template(a) for a in 'create update delete'.split()
            ])

    def post(uri, json={}):
        verifications.triggers.append(json)

    oauth_mock.get = get
    oauth_mock.post = post

    sample_user.procore_data.calendar_event_types = {
        'RFIs': True,
        'Project Users': True
    }

    procore_vm.register_webhooks()

    assert set((d['trigger']['resource_name'], d['trigger']['event_type'])
        for d in verifications.triggers) == {
            ('RFIs', 'create'),
            ('RFIs', 'update'),
            ('RFIs', 'delete')
        }

    
def test_add_and_delete_webhooks(oauth_mock, sample_user, procore_vm):
    verifications = MockObject()
    verifications.hook_created = False
    verifications.triggers = []
    verifications.deletes = []

    hook = {
        "id": 43593499,
        "api_version": "v2",
        "destination_url": "http://localhost/webhook_handler",
        "owned_by_company_id": 5358233,
        "owned_by_project_id": 12345,
        "owned_by_user_id": 222,
        "namespace": "procore"
    }

    trigger_template = lambda method: {
        "id": 231346546,
        "webhook_hook_id": 43593499,
        "resource_name": "Project Users",
        "resource_id": 43597433,
        "event_type": method,
        "company_id": 5358233,
        "project_id": 12345,
        "user_id": 42
    }

    def get(uri):
        if uri == endpoints.PROCORE_WEBHOOKS:
            return OauthResponseMock([hook])
        if uri == endpoints.PROCORE_TRIGGERS.format(hook_id=43593499):
            return OauthResponseMock([
                trigger_template(a) for a in 'create update delete'.split()
            ])

    def post(uri, json={}):
        verifications.triggers.append(json)

    def delete(uri):
        verifications.deletes.append(uri)

    oauth_mock.get = get
    oauth_mock.post = post
    oauth_mock.delete = delete

    sample_user.procore_data.calendar_event_types = {
        'RFIs': True,
        'Project Users': False
    }

    procore_vm.register_webhooks()

    assert set((d['trigger']['resource_name'], d['trigger']['event_type'])
        for d in verifications.triggers) == {
            ('RFIs', 'create'),
            ('RFIs', 'update'),
            ('RFIs', 'delete')
        }
    assert verifications.deletes == \
        [endpoints.PROCORE_TRIGGER.format(hook_id='43593499', trigger_id='231346546')] * 3


def test_convert_event(sample_user, sample_procore_event):
    vm = GCalViewModel(sample_user, sample_procore_event)
    gcal_event = {}

    assert vm.event == gcal_event
