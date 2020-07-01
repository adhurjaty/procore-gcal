from datetime import datetime, timedelta
import pytest
import json
import os
from pathlib import Path

from .mocks import MockObject, MockVMFactory, OauthResponseMock
from .test_util import load_json
import controller.request_handler as rh
from controller.controller import Controller
from controller.presenter import Presenter
from controller.vm_factory import VMFactory
from controller.controller_factory import ControllerFactory
from controller.gcal_view_model import GCalViewModel
from interactor.use_case_interactor import UseCaseInteracor
from interactor.rfi import Rfi
from models.account_manager import AccountManager
from models.db_interface import DBInterface

test_path = Path(os.path.realpath(__file__)).parent

@pytest.fixture(scope='function')
def db_mock():
    mock = MockObject()
    return mock


@pytest.fixture(scope='function')
def mock_oauth():
    mock = MockObject()
    return mock


@pytest.fixture(scope='function')
def mock_vm_factory(mock_oauth: MockObject):
    factory = MockVMFactory(mock_oauth)
    return factory


@pytest.fixture(scope='function')
def test_presenter(mock_vm_factory: MockVMFactory):
    presenter = Presenter(mock_vm_factory)
    return presenter

@pytest.fixture(scope='function')
def live_presenter():
    presenter = Presenter(VMFactory())
    return presenter


@pytest.fixture(scope='function')
def test_use_cases(test_presenter: Presenter, db_mock: MockObject):
    use_cases = UseCaseInteracor(test_presenter, db_mock)
    return use_cases


@pytest.fixture(scope='function')
def live_use_cases(live_presenter, db_mock):
    return UseCaseInteracor(live_presenter, db_mock)


@pytest.fixture(scope='function')
def test_controller(test_use_cases: UseCaseInteracor):
    cont = Controller(test_use_cases)
    ControllerFactory.create = lambda: cont
    return cont


@pytest.fixture(scope='function')
def live_controller(live_use_cases):
    return Controller(live_use_cases)


@pytest.fixture(scope='function')
def test_client(test_controller: Controller):
    app = rh.create_app()

    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


@pytest.fixture(scope='function')
def live_client(live_controller):
    app = rh.create_app(live_controller)

    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


@pytest.fixture(scope='function')
def sample_user():
    manager = AccountManager()
    manager.id = 55
    manager.email = 'adhurjaty@gmail.com'
    manager.full_name = 'Anil Dhurjaty'
    manager.project_id = 12345
    manager.gcal_data.calendar_id = 'anil_calendar_id' 
    return manager


@pytest.fixture(scope='function')
def live_user(sample_user):
    sample_user.project_id = 18918
    with open(os.path.join(test_path.parent, 'secrets', 'temp.json'), 'r') as f:
        secrets = json.load(f)
    sample_user.procore_data.token.access_token = secrets['procore_access_token']
    sample_user.procore_data.token.refresh_token = secrets['procore_refresh_token']
    sample_user.procore_data.token.expires_at = secrets['procore_expires_at']
    sample_user.procore_data.token.token_type = 'Bearer'
    sample_user.gcal_data.token.access_token = secrets['gcal_access_token']
    sample_user.gcal_data.token.refresh_token = secrets['gcal_refresh_token']
    sample_user.gcal_data.calendar_id = secrets['calendar_id']
    sample_user.gcal_data.token.expires_at = secrets['gcal_expires_at']
    sample_user.gcal_data.token.token_type = 'Bearer'
    return sample_user


def test_update_gcal_integration(test_client, mock_oauth, db_mock, sample_user):
    validation = MockObject()
    validation.gcal_endpoint = ''
    validation.procore_endpoint = ''
    validation.json = {}
    
    webhook = load_json('webhook.json')

    def oauth_get(endpoint):
        if len(endpoint.split('?')) > 1:
            return
        validation.procore_endpoint = endpoint
        resp = load_json('rfi.json')
        resp['deleted'] = False
        return OauthResponseMock(resp)

    def create_gcal_event(endpoint, json={}):
        validation.gcal_endpoint = endpoint
        validation.json = json

    db_mock.get_users_from_project_id = lambda pid: [sample_user]
    mock_oauth.get = oauth_get
    mock_oauth.post = create_gcal_event

    test_client.post('/webhook_handler', json=webhook)

    assert validation.gcal_endpoint == '/calendars/anil_calendar_id/events'
    assert validation.procore_endpoint == '/vapid/projects/12345/rfis/11787'
    assert validation.json == {
        'summary': 'RFI #C-1477 - Specifications [99 14.44B]', 
        'description': 'Assignees: Carl the Contractor <exampleuser@website.com>\nRFI Manager: Carl the Contractor <exampleuser@website.com>\nSchedule Impact: 14 days\nCost Impact: $12039.55\nCost Code: Earthwork\nQuestions: Are the items listed on Schedule C acceptable?\nDrawing Number: 107.3D', 
        'location': '1 space', 
        'start': {'date': '2017-01-18'}, 
        'end': {'date': '2017-01-18'}, 
        'attachments': False, 
        'attendees': [], 
        'sendUpdates': 'all'
    }


def test_update_existing_rfi():
    db_int = DBInterface()

    user = db_int.get_user_from_email('adhurjaty@gmail.com')
    rfi_resp = load_json('rfi.json')
    due_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M:%S')
    rfi_resp['due_date'] = due_date
    rfi = Rfi().update_from_dict(rfi_resp)
    rfi.deleted = False

    vm = GCalViewModel(user)
    vm.set_rfi_event(rfi)

    rfi.questions = 'this is a new question?'
    vm.set_rfi_event(rfi)

    db_int.close()

# def test_sign_up_user(test_client, mock_oauth, db_mock):

#     db_mock.get_user_from_token = lambda _: None



# def test_live_update_gcal(live_client, db_mock, live_user):
#     webhook = load_json('webhook.json')

#     db_mock.get_users_from_project_id = lambda pid: [live_user]

#     resp = live_client.post('/api/webhook_handler', json=webhook)

#     assert resp.status_code == 200
#     assert True == False


