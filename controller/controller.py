import arrow
import json

from interactor.account_manager_dto import AccountManagerDto
from interactor.user_dto import UserDto
from interactor.use_case_interactor import UseCaseInteracor
from interactor.rfi import Rfi
from interactor.submittal import Submittal
from interactor.change_order import ChangeOrder
from interactor.person import Person
from util.utils import verify_token
from util.app_logger import get_logger


procore_token_file = 'temp_db/procore_token.json'
logger = get_logger()


class Controller:
    use_case: UseCaseInteracor = None

    def __init__(self, use_case):
        self.use_case = use_case

    def get_user_from_token(self, token: str) -> AccountManagerDto:
        return self.use_case.get_user_from_token(token)

    def get_manager(self, user: AccountManagerDto) -> dict:
        return self.use_case.get_manager_vm(user)

    def update_user(self, user: UserDto, user_data=None):
        if user_data:
            self._verify_csrf(user, user_data.get('csrfToken'))
            self._update_user_fields(user, **user_data)

        self.use_case.update_user(user)

    def _verify_csrf(self, user, csrf_token):
        oauth_token = user.procore_data.token.access_token
        if not verify_token(oauth_token, csrf_token or ''):
            raise Exception('Invalid CSRF Token')

    def _update_user_fields(self, user: AccountManagerDto, email='', fullName='', 
        selectedCalendar='', eventTypes=[], collaborators=None, emailSettings=[], 
        isSubscribed='', projectId=None, **kwargs):

        user.email = email or user.email
        user.full_name = fullName or user.full_name
        user.gcal_data.calendar_id = selectedCalendar or user.gcal_data.calendar_id
        if eventTypes:
            user.set_event_settings(eventTypes)
        if emailSettings:
            user.set_email_settings(emailSettings)
        user.set_collaborators([Person(**c) for c in collaborators] 
            if collaborators else user.collaborators)
        user.subscribed = bool(isSubscribed) or user.subscribed
        if not user.subscribed and user.trial_start is None:
            user.trial_start = arrow.utcnow().datetime
        user.project_id = projectId
        
    def get_users_in_project(self, project_id: int):
        return self.use_case.get_users_in_project(project_id)

    def update_gcal(self, project_id, resource_name='', resource_id=''):
        users = self.get_users_in_project(project_id)
        if not users:
            # TODO: add logging here
            return

        event = self.use_case.get_event(users[0], resource_name=resource_name,
            resource_id=resource_id)
        self.use_case.update_gcal(users, event)

    def init_user(self, token: dict) -> AccountManagerDto:
        user = self.use_case.get_procore_user_info(token)
        self.use_case.get_or_create_user(user)

        return user

    def delete_manager(self, user_id):
        self.use_case.delete_manager(user_id)

    def get_collaborator(self, collaborator_id):
        return self.use_case.get_collaborator(collaborator_id)

    def close(self):
        return self.use_case.close()

