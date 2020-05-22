from typing import List, Set

from util.utils import parallel_for
from .presenter_interface import PresenterInterface
from .account_manager_dto import AccountManagerDto
from .account_manager_response import AccountManagerResponse
from .user_response import UserResponse
from .procore_event import ProcoreEvent
from .user_dto import UserDto
from .person import Person
from models.db_interface import DBInterface
from models.calendar_user import CalendarUser
from models.account_manager import AccountManager

class UseCaseInteracor:
    presenter: PresenterInterface = None
    db_int: DBInterface = None

    def __init__(self, presenter: PresenterInterface, db_int: DBInterface):
        self.presenter = presenter
        self.db_int = db_int

    def get_user_from_token(self, token: str) -> AccountManagerDto:
        user = self.db_int.get_user_from_token(token)
        collaborators = self.db_int.get_user_collaborators(user)
        user_dto = AccountManagerDto(user)
        user_dto.add_collaborators(collaborators)

        return user_dto

    def get_manager_vm(self, user: AccountManagerDto):
        resp_user = AccountManagerResponse(user.parent)
        resp_user.collaborators =  self._get_collaborators(user.collaborators)
        resp_user.calendars = self.db_int.get_calendars(resp_user)
        resp_user.projects = self.db_int.get_projects(resp_user)
        return self.presenter.get_manager_vm(resp_user)

    def _get_collaborators(self, collaborators: List[Person]) -> List[UserResponse]:
        emails = [c.email for c in collaborators]
        return [UserResponse(c) for c in self.db_int.get_collaborators_from_emails(emails)]
    
    def update_user(self, user: UserDto) -> UserDto:
        model_user = user.parent
        if isinstance(user, AccountManagerDto):
            model_user.collaborator_ids = self._get_or_create_collaborators(user.collaborators)
            self._remove_old_collaborators(user.id, model_user.collaborator_ids)

        model_user.save(self.db_int)
        return model_user

    def _get_or_create_collaborators(self, collaborators: List[Person]) -> List[str]:
        emails = [c.email for c in collaborators]
        db_collabs = self.db_int.get_collaborators_from_emails(emails)
        existing_emails = set(c.email for c in db_collabs)
        not_existing_emails = set(emails).difference(existing_emails)
        db_collabs += self._create_collaborators(not_existing_emails)

        return [c.id for c in db_collabs]

    def _create_collaborators(self, emails: Set[str]) -> List[CalendarUser]:
        return parallel_for(self._create_collaborator, emails)

    def _create_collaborator(self, email: str) -> CalendarUser:
        new_collab = CalendarUser()
        new_collab.email = email
        new_collab.temporary = True
        new_collab.save(self.db_int)
        # TODO: send email notification
        return new_collab

    def _remove_old_collaborators(self, user_id: str, collaborator_ids: List[str]):
        existing_user = self.db_int.get_manager(user_id)
        ids_to_remove = set(existing_user.collaborator_ids).difference(collaborator_ids)
        parallel_for(lambda id: self.db_int.delete(CalendarUser().table_name, id),
            ids_to_remove)

    def _get_collaborator_ids(self, emails: List[str]):
        collabs = self.db_int.get_collaborators_from_emails(emails)
        return [c.id for c in collabs]

    def get_users_in_project(self, project_id: int) -> List[AccountManagerDto]:
        return self.db_int.get_users_from_project_id(project_id)

    def get_event(self, user: UserDto, resource_name: str = '', 
        resource_id: int = 0) -> ProcoreEvent:

        return self.presenter.get_procore_event(user, resource_name=resource_name,
            resource_id=resource_id)

    def update_gcal(self, users: List[AccountManagerDto], event: ProcoreEvent):
        def update_cal(user: AccountManagerDto):
            user_response = AccountManagerResponse(user.parent)
            self.presenter.update_gcal(user_response, event)

        parallel_for(update_cal, users)

    def get_procore_user_info(self, token: dict):
        return self.presenter.get_user_info(token)

    def delete_manager(self, user_id: str):
        self.db_int.delete_manager(user_id)

    def get_collaborator(self, collaborator_id: str) -> UserDto:
        return self.db_int.get_collaborator(collaborator_id)
        