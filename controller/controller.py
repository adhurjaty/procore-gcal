import json

from interactor.account_manager_dto import AccountManagerDto
from interactor.user_dto import UserDto
from interactor.use_case_interactor import UseCaseInteracor
from interactor.rfi import Rfi
from interactor.submittal import Submittal
from interactor.change_order import ChangeOrder

procore_token_file = 'temp_db/procore_token.json'

class Controller:
    use_case: UseCaseInteracor = None

    def __init__(self, use_case):
        self.use_case = use_case


    def get_user_from_token(self, token: str) -> AccountManagerDto:
        return self.use_case.get_user_from_token(token)

    def update_user(self, user: UserDto, user_data=None):
        if user_data:
            self._update_user_fields(user, **user_data)
        self.use_case.update_user(user)

    def _update_user_fields(self, user: AccountManagerDto, email='', fullName='', 
        selectedCalendar='', eventTypes=[], collaborators=None, emailSettings=[], 
        isSubscribed='', **kwargs):

        user.email = email or user.email
        user.full_name = fullName or user.full_name
        user.gcal_data.calendar_id = selectedCalendar or user.gcal_data.calendar_id
        user.procore_data.calendar_event_types = {
            t.get('name'): t.get('enabled') for t in eventTypes
        } or user.procore_data.calendar_event_types
        user.collaborators = [c for c in collaborators] if collaborators else user.collaborators
        user.procore_data.email_settings = [s for s in emailSettings] or user.procore_data.email_settings
        user.subscribed = bool(isSubscribed) or user.subscribed

    def get_users_in_project(self, project_id: int):
        return use_case.get_users_in_project(project_id)

    def update_gcal(self, users, resource_name, event_object):
        event = None
        if resource_name == 'RFIs':
            event = Rfi()
            event.update_from_dict(event_object)
        if resource_name == 'Submittals':
            event = Submittal()
            event.update_from_dict(event_object)

        if not event:
            raise Exception('Unsupported resource')

        self.use_case.update_gcal(users, event)

    def init_user(self, token: dict) -> AccountManagerDto:
        user = self.use_case.get_procore_user_info(token)
        if not user:
            raise Exception('Invalid authorization token')
        user.temporary = True

        user = self.use_case.create_user(user)

        return user

    def delete_user(self, user_id):
        self.use_case.delete_user(user_id)

    def get_collaborator(self, collaborator_id):
        return self.use_case.get_collaborator(collaborator_id)

