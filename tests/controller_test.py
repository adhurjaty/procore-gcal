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


@pytest.fixture(scope='module')
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
    