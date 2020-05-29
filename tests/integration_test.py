import pytest

from .mocks import MockObject, MockVMFactory, OauthResponseMock
from .test_util import load_json
import controller.request_handler as rh
from controller.controller import Controller
from controller.presenter import Presenter
from controller.vm_factory import VMFactory
from interactor.use_case_interactor import UseCaseInteracor
from models.account_manager import AccountManager


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
def test_use_cases(test_presenter: Presenter, db_mock: MockObject):
    use_cases = UseCaseInteracor(test_presenter, db_mock)
    return use_cases


@pytest.fixture(scope='function')
def test_controller(test_use_cases: UseCaseInteracor):
    cont = Controller(test_use_cases)
    return cont


@pytest.fixture(scope='function')
def test_client(test_controller: Controller):
    app = rh.create_app(test_controller)

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


def test_update_gcal_integration(test_client, mock_oauth, db_mock, sample_user):
    validation = MockObject()
    validation.gcal_endpoint = ''
    validation.procore_endpoint = ''
    validation.json = {}
    
    webhook = load_json('webhook.json')

    def oauth_get(endpoint, q=''):
        if q:
            return None
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

    test_client.post('/api/webhook_handler', json=webhook)

    assert validation.gcal_endpoint == '/calendars/anil_calendar_id/events'
    assert validation.procore_endpoint == '/vapid/projects/12345/rfis/212727'
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
