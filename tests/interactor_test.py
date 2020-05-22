import pytest
from copy import deepcopy
from datetime import datetime
import json
import os
from pathlib import Path

from .test_util import load_json
from .mocks import MockObject
from interactor.change_order import ChangeOrder
from interactor.person import Person
from interactor.rfi import Rfi
from interactor.submittal import Submittal
from interactor.use_case_interactor import UseCaseInteracor
from interactor.account_manager_dto import AccountManagerDto
from interactor.account_manager_response import AccountManagerResponse
from interactor.user_dto import UserDto
from interactor.rfi import Rfi
from models.account_manager import AccountManager
from models.calendar_user import CalendarUser
from models.oauth2_token import Oauth2Token


objects_path = os.path.join(Path(os.path.realpath(__file__)).parent, 'objects')


@pytest.fixture(scope='function')
def sample_rfi():
    rfi = Rfi()
    rfi.update_from_dict(load_json('rfi.json'))
    return rfi


@pytest.fixture(scope='function')
def sample_submittal():
    submittal = Submittal()
    submittal.update_from_dict(load_json('submittal.json'))
    return submittal


@pytest.fixture(scope='module')
def presenter_mock():
    mock = MockObject()
    return mock


@pytest.fixture(scope='module')
def db_mock():
    mock = MockObject()
    return mock


@pytest.fixture(scope='module')
def test_interactor(presenter_mock, db_mock):
    interactor = UseCaseInteracor(presenter_mock, db_mock)
    return interactor


@pytest.fixture(scope='function')
def sample_user():
    manager = AccountManager()
    manager.id = 55
    manager.email = 'adhurjaty@gmail.com'
    manager.full_name = 'Anil Dhurjaty'
    manager.project_id = 12345
    return manager


@pytest.fixture(scope='function')
def sample_collaborators():
    collab0 = CalendarUser()
    collab0.id = 'id1'
    collab0.email = 'aaron@procore.com'
    collab0.full_name = 'Aaron'
    collab1 = CalendarUser()
    collab1.id = 'id2'
    collab1.email = 'aimee@procore.com'
    collab1.full_name = 'Aimee'
    return [collab0, collab1]


@pytest.fixture(scope='function')
def sample_token():
    return Oauth2Token(access_token='access', refresh_token='refresh',
        token_type='Bearer', expires_at=999)


@pytest.fixture(scope='function')
def input_manager(sample_token):
    manager = AccountManagerDto(AccountManager())
    manager.full_name='Anil Dhurjaty'
    manager.email='adhurjaty@example.com'
    manager.id = '22'

    manager.collaborators = [Person(full_name='Aaron', email='aaron@procore.com'),
        Person(full_name='Aimee', email='aimee@procore.com')]
    manager.procore_data = sample_token
    manager.gcal_data = sample_token
    manager.subscribed = True
    manager.payment_id = 'payment ID'
    manager.temporary = False

    return manager


def test_create_rfi(sample_rfi):
    assert sample_rfi.id == 999
    assert sample_rfi.number == "C-1477"
    assert sample_rfi.title == "Specifications [99 14.44B]"
    assert sample_rfi.location == "1 space"
    assert sample_rfi.description == ''
    assert sample_rfi.due_date == datetime(2017, 1, 18).date()
    assert len(sample_rfi.assignees) == 1
    assert sample_rfi.assignees[0].email == "exampleuser@website.com"
    assert sample_rfi.assignees[0].full_name =='Carl the Contractor'
    assert sample_rfi.rfi_manager.email == "exampleuser@website.com"
    assert sample_rfi.rfi_manager.full_name =='Carl the Contractor'
    assert sample_rfi.schedule_impact == 14
    assert sample_rfi.cost_impact == 12039.55
    assert sample_rfi.cost_code == "Earthwork"
    assert sample_rfi.questions == "Are the items listed on Schedule C acceptable?"
    assert sample_rfi.drawing_number == "107.3D"
    assert sample_rfi.subject == "Specifications [99 14.44B]"
    assert sample_rfi.deleted


def test_create_submittal(sample_submittal):
    assert sample_submittal.number == "118"
    assert sample_submittal.title == "Smiths - Teardown & Assembly Bldg"
    assert sample_submittal.location == "1 space"
    assert sample_submittal.description == "Thermal Insulation submittal"
    assert sample_submittal.due_date == datetime(2014, 7, 22).date()
    assert sample_submittal.ball_in_court.full_name == 'Carl Contractor' 
    assert sample_submittal.ball_in_court.email == 'exampleuser@website.com' 
    assert sample_submittal.approver.full_name == "Other Contractor"
    assert sample_submittal.approver.email == "otherexampleuser@website.com"
    assert sample_submittal.attachments[0].url == "http://www.example.com/"
    assert sample_submittal.attachments[0].filename == "january_receipt_copy.jpg"
    assert sample_submittal.required_on_site_date == datetime(2016, 11, 28).date()


def test_create_change_order():
    with open(os.path.join(objects_path, 'change_order.json')) as f:
        contents_dict = json.load(f)
    change_order = ChangeOrder()
    change_order.update_from_dict(contents_dict)

    assert change_order.number == "H-38"
    assert change_order.title == "Additional Time & Materials"
    assert change_order.location == ''
    assert change_order.description == "Additional Time & Materials for October"
    assert change_order.due_date == datetime(2016, 10, 23).date()
    # assert submittal.ball_in_court.full_name == 'Carl Contractor' 
    # assert submittal.ball_in_court.email == 'exampleuser@website.com' 
    # assert submittal.approver.full_name == "Other Contractor"
    # assert submittal.approver.email == "otherexampleuser@website.com"
    # assert submittal.attachments[0].url == "http://www.example.com/"
    # assert submittal.attachments[0].filename == "january_receipt_copy.jpg"


def test_get_user_from_token(test_interactor, db_mock, sample_user, sample_collaborators):
    db_mock.get_user_from_token = lambda t: sample_user
    db_mock.get_user_collaborators = lambda u: sample_collaborators

    user = test_interactor.get_user_from_token('access token')

    assert user.full_name == 'Anil Dhurjaty'
    assert user.id == 55
    assert user.collaborators[0].email == 'aaron@procore.com'
    assert user.collaborators[1].full_name == 'Aimee'


def test_update_manager(test_interactor, db_mock, sample_user, sample_collaborators, 
    input_manager):
    
    validations = MockObject()
    validations.table = ''
    validations.update_user = None
    
    def update(table, model):
        validations.table = table
        validations.update_user = model

    def get_collaborators(emails):
        return [c for c in sample_collaborators if c.email in emails]
    
    db_mock.update = update
    db_mock.get_collaborators_from_emails = get_collaborators

    user = test_interactor.update_user(input_manager)

    assert validations.update_user == user
    assert validations.table == 'AccountManager'
    assert user.collaborator_ids == 'id1 id2'.split()
    assert user.procore_data.access_token == 'access'
    assert user.id == '22'


def test_update_collaborator(test_interactor, db_mock, sample_user, sample_token):
    validations = MockObject()
    validations.table = ''
    validations.update_user = None
    
    input_collab = UserDto(CalendarUser())
    input_collab.full_name='Aaron'
    input_collab.email='aaron@procore.com'
    input_collab.id = '11'
    input_collab.gcal_data = sample_token
    input_collab.temporary = False

    def update(table, model):
        validations.table = table
        validations.update_user = model

    db_mock.update = update

    user = test_interactor.update_user(input_collab)

    assert user == validations.update_user
    assert user.id == '11'
    assert user.gcal_data.access_token == 'access'
    assert not user.temporary
    assert validations.table == 'Collaborator'


def test_get_users_in_project(test_interactor, db_mock):
    users = [AccountManager(), AccountManager()]

    db_mock.get_users_from_project_id = lambda x: users

    db_users = test_interactor.get_users_in_project('pid')

    assert db_users == users


def test_update_gcal(test_interactor, presenter_mock, sample_user):
    validations = MockObject()
    validations.users = []
    validations.events = []

    def update_gcal(user, event):
        validations.users.append(user)
        validations.events.append(event)

    presenter_mock.update_gcal = update_gcal

    user1 = AccountManagerDto(sample_user)
    other_user = deepcopy(sample_user)
    other_user.full_name = 'Blah Black'
    other_user.email = 'bb@example.com'
    user2 = AccountManagerDto(other_user)

    users = [user1, user2]

    event = Rfi()

    test_interactor.update_gcal(users, event)

    assert len(validations.users) == 2
    assert isinstance(validations.users[0], AccountManagerResponse)
    assert [u.parent for u in validations.users] == [u.parent for u in users]
    assert validations.events == [event] * 2


def test_get_procore_user_info(test_interactor, presenter_mock, sample_user):
    validations = MockObject()
    validations.token = {}

    def get_user(token):
        validations.token = token
        return sample_user

    presenter_mock.get_procore_user_info = get_user

    t = {
        'access_token': 'access',
        'refresh_token': 'refresh'
    }

    user = test_interactor.get_procore_user_info(t)

    assert t == validations.token
    assert user == sample_user


def test_delete_manager(test_interactor, db_mock):
    validations = MockObject()
    validations.deleted_id = ''

    def delete(user_id):
        validations.deleted_id = user_id

    db_mock.delete_manager = delete

    test_interactor.delete_manager('55')

    assert validations.deleted_id == '55'


def test_get_collaborator(test_interactor, db_mock, sample_collaborators):
    validations = MockObject()
    validations.cid = ''

    def get_user(cid):
        validations.cid = cid
        return sample_collaborators[0]

    db_mock.get_collaborator = get_user

    user = test_interactor.get_collaborator('44')

    assert validations.cid == '44'
    assert user == sample_collaborators[0]