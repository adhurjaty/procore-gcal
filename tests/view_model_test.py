import pytest
import json
import os
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from .mocks import OauthMock, MockObject, OauthResponseMock, ControllerMock
from .test_util import load_json
from controller.gcal_view_model import GCalViewModel
from controller.procore_view_model import ProcoreViewModel
from controller.web_view_model import WebViewModel
import controller.server_connector as server_connector
import controller.api_endpoints as endpoints
from controller.email_view_model import EmailViewModel
from interactor.account_manager_dto import AccountManagerDto
from interactor.account_manager_response import AccountManagerResponse
from interactor.user_response import UserResponse
from interactor.rfi import Rfi
from interactor.submittal import Submittal
from interactor.change_order import ChangeOrder
from interactor.named_item import NamedItem
from models.account_manager import AccountManager
from models.gcal_user_settings import GCalUserSettings
from models.collaborator_user import CollaboratorUser

objects_path = os.path.join(Path(os.path.realpath(__file__)).parent, 'objects')


def load_json(filename):
    path = os.path.join(objects_path, filename)
    with open(path, 'r') as f:
        return json.load(f)


@pytest.fixture(scope='session', autouse=True)
def define_url_for_webhooks():
    server_connector.url_for_webhooks = 'http://localhost/webhook_handler'


@pytest.fixture()
def oauth_mock() -> OauthMock:
    mock = OauthMock()
    return mock


@pytest.fixture()
def sample_user() -> AccountManagerDto:
    manager = AccountManagerDto(AccountManager())
    manager.id = 69
    manager.email = 'sean@example.com'
    manager.full_name = 'Sean Black'
    manager.project_id = 12345
    manager.gcal_data.calendar_id = 42
    return manager


@pytest.fixture()
def procore_vm(oauth_mock, sample_user) -> ProcoreViewModel:
    vm = ProcoreViewModel(sample_user)
    vm.oauth = oauth_mock
    return vm

@pytest.fixture()
def gcal_vm(oauth_mock, sample_user) -> GCalViewModel:
    vm = GCalViewModel(sample_user)
    vm.oauth = oauth_mock
    return vm

@pytest.fixture(scope='module')
def rfi_event() -> Rfi:
    with open(os.path.join(objects_path, 'rfi.json')) as f:
        contents_dict = json.load(f)
    rfi = Rfi()
    rfi.link = 'https://procore.com/rfi/42'
    rfi.update_from_dict(contents_dict)
    rfi.deleted = False
    return rfi

@pytest.fixture(scope='module')
def submittal_event() -> Submittal:
    with open(os.path.join(objects_path, 'submittal.json')) as f:
        contents_dict = json.load(f)
    submittal = Submittal()
    submittal.link = 'https://procore.com/submittal/42'
    submittal.update_from_dict(contents_dict)
    submittal.deleted = False
    return submittal


@pytest.fixture(scope='module')
def submittal_no_final_event():
    submittal = Submittal()
    submittal.update_from_dict(load_json('new_submittal.json'))
    submittal.link = 'https://procore.com/submittal/42'
    submittal.deleted = False
    return submittal


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
        if uri == endpoints.PROCORE_WEBHOOKS.format(project_id=12345):
            verifications.hook_created = True
            return hook
            
        verifications.triggers.append(json)
    
    oauth_mock.get = get
    oauth_mock.post = post

    sample_user.procore_data.calendar_event_types = [
        {
            'name': 'RFIs',
            'enabled': True
        },
        {
            'name': 'Submittals',
            'enabled': True
        },
        {
            'name': 'Events',
            'enabled': False
        }
    ]

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
        if uri == endpoints.PROCORE_WEBHOOKS.format(project_id=12345):
            return OauthResponseMock([hook])
        if uri == endpoints.PROCORE_TRIGGERS.format(hook_id=43593499, project_id=12345):
            return OauthResponseMock([
                trigger_template(a) for a in 'create update delete'.split()
            ])

    def post(uri, json={}):
        verifications.triggers.append(json)

    oauth_mock.get = get
    oauth_mock.post = post

    sample_user.procore_data.calendar_event_types = [
        {
            'name': 'RFIs',
            'enabled': True
        },
        {
            'name': 'Project Users',
            'enabled': True
        }
    ]

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
        if uri == endpoints.PROCORE_WEBHOOKS.format(project_id=12345):
            return OauthResponseMock([hook])
        if uri == endpoints.PROCORE_TRIGGERS.format(hook_id=43593499, project_id=12345):
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

    sample_user.procore_data.calendar_event_types = [
        {
            'name': 'RFIs',
            'enabled': True
        },
        {
            'name': 'Project Users',
            'enabled': False
        }
    ]

    procore_vm.register_webhooks()

    assert set((d['trigger']['resource_name'], d['trigger']['event_type'])
        for d in verifications.triggers) == {
            ('RFIs', 'create'),
            ('RFIs', 'update'),
            ('RFIs', 'delete')
        }
    assert verifications.deletes == \
        [endpoints.PROCORE_TRIGGER.format(
            hook_id='43593499', 
            trigger_id='231346546',
            project_id=12345)] * 3


def test_create_rfi_event(gcal_vm: GCalViewModel, oauth_mock: OauthMock, rfi_event: Rfi):
    validations = MockObject()
    validations.q_endpoint = ''
    validations.q = ''
    validations.create_endpoint = ''
    validations.event = None

    def oauth_get(endpoint, **query):
        parts = endpoint.split('?')
        validations.q_endpoint = parts[0]
        validations.q = parts[1].strip('q=')
        return None

    def oauth_post(endpoint, json=None):
        validations.create_endpoint = endpoint
        validations.event = json

    oauth_mock.get = oauth_get
    oauth_mock.post = oauth_post

    gcal_vm.set_rfi_event(rfi_event)

    with open(os.path.join(objects_path, 'rfi_description.txt'), 'r') as f:
        body = f.read()
    assert validations.q_endpoint == '/calendars/42/events'
    assert validations.q == 'https%3A%2F%2Fprocore.com%2Frfi%2F42'
    assert validations.create_endpoint == '/calendars/42/events'
    assert validations.event.get('summary') == 'RFI #C-1477 - Specifications [99 14.44B]'
    assert validations.event.get('location') == '1 space'
    assert validations.event.get('description') == body
    assert validations.event.get('start') == {
        'date': '2017-01-18'
    }
    assert validations.event.get('end') == {
        'date': '2017-01-18'
    }


def test_create_submittal_event(gcal_vm: GCalViewModel, oauth_mock: OauthMock, 
    submittal_event: Submittal):

    validations = MockObject()
    validations.q_endpoint = ''
    validations.qs = []
    validations.create_endpoint = ''
    validations.events = []

    def oauth_get(endpoint):
        parts = endpoint.split('?')
        validations.q_endpoint = parts[0]
        q = parts[1].strip('q=')
        validations.qs.append(q)
        return None

    def oauth_post(endpoint, json=None):
        validations.create_endpoint = endpoint
        validations.events.append(json)

    oauth_mock.get = oauth_get
    oauth_mock.post = oauth_post

    gcal_vm.set_submittal_events(submittal_event)

    with open(os.path.join(objects_path, 'submittal_description_on_site.txt'), 'r') as f:
        body_on_site = f.read()
    with open(os.path.join(objects_path, 'submittal_description_final.txt'), 'r') as f:
        body_final = f.read()
    assert validations.q_endpoint == '/calendars/42/events'
    assert set(validations.qs) == {'https%3A%2F%2Fprocore.com%2Fsubmittal%2F42+Submittal+Type%3A+On+Site',
        'https%3A%2F%2Fprocore.com%2Fsubmittal%2F42+Submittal+Type%3A+Final'}
    assert validations.create_endpoint == '/calendars/42/events'
    assert set(e.get('summary') for e in validations.events) == \
        {'Submittal #118 - Smiths - Teardown & Assembly Bldg On Site',
        'Submittal #118 - Smiths - Teardown & Assembly Bldg Final'}
    on_site_sub = next((e for e in validations.events if 'On Site' in e.get('summary')), None)
    final_sub = next((e for e in validations.events if 'Final' in e.get('summary')), None)
    assert on_site_sub.get('description') == body_on_site 
    assert final_sub.get('description') == body_final
    assert on_site_sub.get('start') == {'date': '2016-11-28'}
    assert on_site_sub.get('end') == {'date': '2016-11-28'}
    assert final_sub.get('start') == {'date': '2014-07-22'}
    assert final_sub.get('end') == {'date': '2014-07-22'}
    for event in validations.events:
        assert event.get('location') == '1 space'


def test_create_submittal_event_no_final(gcal_vm: GCalViewModel, oauth_mock: OauthMock, 
    submittal_no_final_event: Submittal):

    validations = MockObject()
    validations.q_endpoint = ''
    validations.qs = []
    validations.create_endpoint = ''
    validations.events = []

    def oauth_get(endpoint):
        parts = endpoint.split('?')
        validations.q_endpoint = parts[0]
        q = parts[1].strip('q=')
        validations.qs.append(q)
        return None

    def oauth_post(endpoint, json=None):
        validations.create_endpoint = endpoint
        validations.events.append(json)

    oauth_mock.get = oauth_get
    oauth_mock.post = oauth_post

    gcal_vm.set_submittal_events(submittal_no_final_event)

    assert len(validations.events) == 1
    assert validations.events[0]['summary'] == 'Submittal #3 - this new submittal On Site'


def test_delete_existing_rfi_event(gcal_vm: GCalViewModel, oauth_mock: OauthMock, rfi_event: Rfi):
    validations = MockObject()
    validations.q_endpoint = ''
    validations.q = ''
    validations.delete_endpoint = ''
    validations.create_endpoint = ''
    validations.event = None

    def oauth_get(endpoint):
        parts = endpoint.split('?')
        validations.q_endpoint = parts[0]
        validations.q = parts[1].strip('q=')
        return OauthResponseMock({
            'items': [{'id': 'unique_id'}]
        })

    def oauth_delete(endpoint):
        validations.delete_endpoint = endpoint

    def oauth_post(endpoint, json=None):
        validations.create_endpoint = endpoint
        validations.event = json

    rfi_event.deleted = True

    oauth_mock.get = oauth_get
    oauth_mock.delete = oauth_delete
    oauth_mock.post = oauth_post

    gcal_vm.set_rfi_event(rfi_event)

    assert validations.q_endpoint == '/calendars/42/events'
    assert validations.q == 'https%3A%2F%2Fprocore.com%2Frfi%2F42'
    assert validations.delete_endpoint == '/calendars/42/events/unique_id'
    assert validations.create_endpoint == ''
    assert validations.event == None

def test_update_existing_rfi_event(gcal_vm: GCalViewModel, oauth_mock: OauthMock, rfi_event: Rfi):
    validations = MockObject()
    validations.q_endpoint = ''
    validations.q = ''
    validations.patch_endpoint = ''
    validations.create_endpoint = ''
    validations.event = None

    def oauth_get(endpoint):
        parts = endpoint.split('?')
        validations.q_endpoint = parts[0]
        validations.q = parts[1].strip('q=')
        return OauthResponseMock({
            'items': [{'id': 'unique_id'}]
        })

    def oauth_patch(endpoint, json=None):
        validations.patch_endpoint = endpoint
        validations.event = json

    def oauth_post(endpoint, json=None):
        validations.create_endpoint = endpoint

    rfi_event.deleted = False

    oauth_mock.get = oauth_get
    oauth_mock.patch = oauth_patch
    oauth_mock.post = oauth_post

    gcal_vm.set_rfi_event(rfi_event)

    assert validations.q_endpoint == '/calendars/42/events'
    assert validations.q == 'https%3A%2F%2Fprocore.com%2Frfi%2F42'
    assert validations.patch_endpoint == '/calendars/42/events/unique_id'
    assert validations.create_endpoint == ''
    assert validations.event != None


def test_get_user_info(oauth_mock, procore_vm):
    def get(endpoint):
        if endpoint == endpoints.PROCORE_GET_USER:
            return OauthResponseMock({
                "id": 42,
                "login": "adhurjaty",
                "name": "Anil Dhurjaty"
            })
        

    oauth_mock.get = get

    user_info = procore_vm.get_user_info()

    assert user_info.get('login') == 'adhurjaty'
    assert user_info.get('name') == 'Anil Dhurjaty'


def test_get_company_ids(oauth_mock, procore_vm):
    def get(endpoint):
        if endpoint == endpoints.PROCORE_COMPANIES:
            return OauthResponseMock([
                {
                    "id": 1,
                    "name": "ABC Drywall",
                    "is_active": True
                },
                {
                    "id": 2,
                    "name": "DEF Flooring",
                    "is_active": True
                }
            ])

    oauth_mock.get = get

    company_ids = procore_vm.get_company_ids()

    assert company_ids == [1, 2]

def test_get_projects(oauth_mock, procore_vm):
    def get(url):
        endpoint, params = split_url(url)
        if endpoint == endpoints.PROCORE_PROJECTS:
            company_id = params.get('company_id')
            if company_id == '1':
                return OauthResponseMock(load_json('projects1.json'))
            if company_id == '2':
                return OauthResponseMock(load_json('projects2.json'))

    oauth_mock.get = get

    projects = procore_vm.get_projects([1, 2])

    assert projects == [
        {'id': 12732, 'name': 'Other project'},
        {'id': 12731, 'name': 'This project'},
        {'id': 12738, 'name': 'Lakeside Mixed Use'}
    ]


def test_get_event_from_api(oauth_mock, procore_vm):
    validations = MockObject()
    validations.endpoint = ''

    def get(endpoint):
        validations.endpoint = endpoint
        return OauthResponseMock({
            'key': 'value'
        })

    oauth_mock.get = get

    resp = procore_vm.get_event(resource_id=3, resource_name='RFIs')

    assert validations.endpoint == '/vapid/projects/12345/rfis/3'
    assert resp['key'] == 'value'


def test_get_event_invalid_type(oauth_mock, procore_vm):
    validations = MockObject()
    validations.endpoint = ''

    def get(endpoint):
        validations.endpoint = endpoint
        return OauthResponseMock({
            'key': 'value'
        })

    oauth_mock.get = get

    try:
        resp = procore_vm.get_event(resource_id=3, resource_name='Missing')
        assert '' == 'Exception not raised'
    except Exception as e:
        assert str(e) == 'Unsupported resource type'


def test_get_manager_vm():
    parent = AccountManager()
    parent.id = 54
    parent.collaborator_ids = [2, 5, 23]
    parent.email = 'test@example.com'
    parent.full_name = 'Boaty McBoatface'
    parent.gcal_data = GCalUserSettings()
    parent.gcal_data.access_token = 'access token'
    parent.gcal_data.refresh_token = 'refresh token'
    parent.gcal_data.calendar_id = 'asdfg'
    parent.procore_data.calendar_event_types = [
        {
            'name': 'foo',
            'enabled': True
        },
        {
            'name': 'bar',
            'enabled': False
        }
    ]
    parent.procore_data.email_settings = [
        {
            'name': 'baz',
            'enabled': False
        },
        {
            'name': 'other',
            'enabled': False
        }
    ]
    parent.temporary = False
    parent.subscribed = True
    parent.project_id = 77
    
    user = AccountManagerResponse(parent)
    user.calendars = [NamedItem(id='asdfg', name='random'),
        NamedItem(id='iuyo', name='something')]
    user.projects = [NamedItem(id=88, name='p1'), NamedItem(id=77, name='p2')]
    collab = CollaboratorUser()
    collab.id = 23
    collab.full_name = 'Kermit'
    user.collaborators = [UserResponse(collab)]

    vm = WebViewModel()
    resp = vm.show_user(user)

    assert resp == {
        'id': 54,
        'email': 'test@example.com',
        'fullName': 'Boaty McBoatface',
        'calendars': [{
            'id': 'asdfg',
            'name': 'random'
        },
        {
            'id': 'iuyo',
            'name': 'something'
        }],
        'isGcalLoggedIn': True,
        'selectedCalendar': 'asdfg',
        'eventTypes': [{'name': 'foo', 'enabled': True}, {'name': 'bar', 'enabled': False}],
        'collaborators': [{'id': 23, 'name': 'Kermit'}],
        'emailSettings': [{'name': 'baz', 'enabled': False}, 
            {'name': 'other', 'enabled': False}],
        'temporary': False,
        'isSubscribed': True,
        'projectId': 77,
        'projects': [{'id': 88, 'name': 'p1'}, {'id': 77, 'name': 'p2'}],
        'csrfToken':'hj65Uh3paa0/VfCAWG+v0KyeFI2XYdEkNM0zdSM8TpuzT07jQzS0701xVxhupvcky7ups+2KE0vaHtS1Og1QlBNCuhPRbQzIeWPq+uyYY53XdGXosPZCLqFv92Re/NA/V99j6mjGBgtBUhWFCxYRwzVXHgGmGbWY3oRlcDyzqmI='
    }


def test_signup_email_vm(sample_user):
    vm = EmailViewModel(sample_user)
    email_contents = vm.signup_email()

    assert email_contents == {
        'full_name': 'Sean Black',
        'link': 'http://localhost:3000',
        'subject': 'Welcome to Procore Calendar Integrator'
    }


def split_url(url):
    parsed = urlparse(url)
    return parsed.path, {k: v[0] for k, v in parse_qs(parsed.query).items()}