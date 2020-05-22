import pytest
from copy import deepcopy
import json
import os
from pathlib import Path

from .mocks import MockObject
from .test_util import load_json
from controller.controller import Controller
from interactor.account_manager_dto import AccountManagerDto
from interactor.user_dto import UserDto
from interactor.rfi import Rfi
from models.account_manager import AccountManager
from models.calendar_user import CalendarUser

objects_path = os.path.join(Path(os.path.realpath(__file__)).parent, 'objects')

@pytest.fixture(scope='module')
def use_case_mock():
    mock = MockObject()
    return mock


@pytest.fixture(scope='module')
def test_controller(use_case_mock) -> Controller:
    return Controller(use_case_mock)


@pytest.fixture(scope='function')
def sample_user() -> AccountManagerDto:
    manager = AccountManagerDto(AccountManager())
    manager.id = 55
    manager.email = 'adhurjaty@gmail.com'
    manager.full_name = 'Anil Dhurjaty'
    manager.project_id = 12345
    manager.company_id = 26972
    return manager


def test_get_user_from_token(test_controller, use_case_mock, sample_user):
    use_case_mock.get_user_from_token = lambda token:  sample_user

    user = test_controller.get_user_from_token('access_token')
    assert user.id == 55
    assert user.full_name == 'Anil Dhurjaty'


def test_update_user(test_controller, use_case_mock, sample_user):
    validations = MockObject()
    validations.user = None

    def update(user):
        validations.user = user

    use_case_mock.update_user = update

    sample_user.full_name = 'Other Guy'
    test_controller.update_user(sample_user)

    assert validations.user == sample_user


def test_update_user_with_data(test_controller, use_case_mock, sample_user):
    validations = MockObject()
    validations.user = None

    def update(user):
        validations.user = user

    use_case_mock.update_user = update

    data = {
        'email': 'user@example.com',
        'fullName': 'This User',
        'selectedCalendar': 'calID',
        'eventTypes': [
            {
                'name': 'Submittals',
                'enabled': True
            },
            {
                'name': 'RFIs',
                'enabled': False
            }
        ],
        'collaborators': [
            { 
                'name': 'Aaron',
                'login': 'aaron@procore.com'
            },
            {
                'name': 'Aimee',
                'login': 'aimee@procore.com'
            }
        ],
        'emailSettings': [
            {
                'name': 'Calendar Events',
                'enabled': True
            },
            {
                'name': 'Added Collaborator',
                'enabled': True
            }
        ],
        'subscribed': False
    }

    test_controller.update_user(sample_user, user_data=data)

    assert validations.user == sample_user
    assert validations.user.email == 'user@example.com'
    assert validations.user.full_name == 'This User'
    assert validations.user.gcal_data.calendar_id == 'calID'
    assert validations.user.procore_data.calendar_event_types == {
        'Submittals': True,
        'RFIs': False
    }
    assert validations.user.collaborators[0].full_name == 'Aaron'
    assert validations.user.collaborators[0].email == 'aaron@procore.com'
    assert validations.user.collaborators[1].full_name == 'Aimee'
    assert validations.user.collaborators[1].email == 'aimee@procore.com'
    assert validations.user.subscribed == False


def test_get_users_in_project(test_controller, use_case_mock, sample_user):
    validations = MockObject()
    validations.project_id = 0

    def get_users(pid):
        validations.project_id = pid

    use_case_mock.get_users_in_project = get_users

    test_controller.get_users_in_project(44)

    assert validations.project_id == 44


def test_update_gcal_rfi(test_controller, use_case_mock, sample_user):
    validations = MockObject()
    validations.user = None
    validations.resource_name = ''
    validations.resource_id = ''
    validations.users = None
    validations.event = None

    user1 = deepcopy(sample_user)
    user1.full_name = 'Carl Contractor'
    user1.email = 'this@example.com'
    users = [user1, sample_user]

    def get_users(pid):
        return users

    def get_event(user, **kwargs):
        validations.user = user
        validations.resource_name = kwargs.get('resource_name')
        validations.resource_id = kwargs.get('resource_id')
        return Rfi()

    def update(users, event):
        validations.users = users
        validations.event = event

    use_case_mock.get_users_in_project = get_users
    use_case_mock.get_event = get_event
    use_case_mock.update_gcal = update

    test_controller.update_gcal(project_id='pid', resource_name='RFIs', resource_id='rid')

    assert validations.user == user1
    assert validations.resource_name == 'RFIs'
    assert validations.resource_id == 'rid'
    assert validations.users == users
    assert isinstance(validations.event, Rfi)


def test_init_user(test_controller, use_case_mock, sample_user):
    validations = MockObject()
    validations.user = None
    
    token = {'access_token': 'access_token'}

    def get_user_info(t):
        return sample_user

    def create_user(user):
        validations.user = user
        return user

    use_case_mock.get_procore_user_info = get_user_info
    use_case_mock.create_user = create_user

    user = test_controller.init_user(token)
    
    assert user != None
    assert user == validations.user
    assert user.temporary


def test_delete_manager(test_controller, use_case_mock):
    validations = MockObject
    validations.user_id = ''

    def delete(user_id):
        validations.user_id = user_id

    use_case_mock.delete_manager = delete

    test_controller.delete_manager('44')

    assert validations.user_id == '44'


def test_get_collaborator(test_controller, use_case_mock):
    collab_user = UserDto(CalendarUser())
    collab_user.full_name = 'Anil Dhurjaty'
    collab_user.email = 'anil@example.com'
    use_case_mock.get_collaborator = lambda x: collab_user

    collab = test_controller.get_collaborator('id')

    assert collab.full_name == 'Anil Dhurjaty'
    assert collab.email == 'anil@example.com'


def test_get_manager(test_controller, use_case_mock, sample_user):
    validations = MockObject()
    validations.user = None

    def get(user):
        validations.user = user
        return {'result': 'success'}

    use_case_mock.get_manager_vm = get

    result = test_controller.get_manager(sample_user)

    assert validations.user == sample_user
    assert result['result'] == 'success'
