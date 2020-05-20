import pytest

from .mocks import MockObject
from controller.controller import Controller
from interactor.account_manager_dto import AccountManagerDto

@pytest.fixture(scope='module')
def use_case_mock():
    mock = MockObject()
    return mock


@pytest.fixture(scope='module')
def test_controller(use_case_mock) -> Controller:
    return Controller(use_case_mock)


@pytest.fixture(scope='function')
def sample_user() -> AccountManagerDto:
    manager = AccountManagerDto()
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
            'aaron@procore.com',
            'aimee@procore.com'
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
    assert validations.user.collaborators == 'aaron@procore.com aimee@procore.com'.split()
    assert validations.user.subscribed == False


    