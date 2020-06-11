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
from models.collaborator_user import CollaboratorUser
from models.account_manager import AccountManager

class UseCaseInteracor:
    presenter: PresenterInterface = None
    db_int: DBInterface = None

    def __init__(self, presenter: PresenterInterface, db_int: DBInterface):
        self.presenter = presenter
        self.db_int = db_int

    def get_user_from_token(self, token: str) -> AccountManagerDto:
        user = self.db_int.get_user_from_token(token)
        user_dto = AccountManagerDto(user)

        return user_dto

    def get_manager_vm(self, user: AccountManagerDto):
        resp_user = AccountManagerResponse(user.parent)
        resp_user.collaborators =  self._get_collaborators(user.collaborators)
        resp_user = self.presenter.set_manager_selections(resp_user)
        return self.presenter.get_manager_vm(resp_user)

    def _get_collaborators(self, collaborators: List[Person]) -> List[UserResponse]:
        emails = [c.email for c in collaborators]
        return [UserResponse(c) for c in self.db_int.get_collaborators_from_emails(emails)]
    
    def update_user(self, user: UserDto) -> UserDto:
        model_user = user.parent
        if isinstance(user, AccountManagerDto):
            self._create_or_remove_collaborators(model_user)

        self.db_int.update(model_user)
        return model_user

    def _create_or_remove_collaborators(self, manager: AccountManager):
        self._remove_collaborators(manager)
        self._create_collaborators([c for c in manager.collaborators if not c.id])
        
    def _remove_collaborators(self, manager: AccountManager):
        all_collabs = self.db_int.get_manager_collaborators(manager.id)
        keep_collab_ids = [c.id for c in manager.collaborators]
        collabs_to_remove = [c for c in all_collabs if c.id and c.id not in keep_collab_ids]
        parallel_for(lambda c: self.db_int.delete(c), collabs_to_remove)

    def _create_collaborators(self, new_collabs: List[CollaboratorUser]):
        parallel_for(lambda c: self.db_int.insert(c), new_collabs)

    def get_users_in_project(self, project_id: int) -> List[AccountManagerDto]:
        return [AccountManagerDto(a) 
            for a in self.db_int.get_users_from_project_id(project_id)]

    def get_event(self, user: UserDto, resource_name: str = '', 
        resource_id: int = 0) -> ProcoreEvent:

        user_resp = UserResponse(user.parent)
        return self.presenter.get_procore_event(user_resp, resource_name=resource_name,
            resource_id=resource_id)

    def update_gcal(self, users: List[AccountManagerDto], event: ProcoreEvent):
        def update_cal(user: AccountManagerDto):
            user_response = AccountManagerResponse(user.parent)
            self.presenter.update_gcal(user_response, event)

        parallel_for(update_cal, users)

    def get_procore_user_info(self, token: dict) -> AccountManagerDto:
        user_dict = self.presenter.get_user_info(token)
        user = AccountManager()
        user.email = user_dict.get('email')
        user.full_name = user_dict.get('name')
        return user

    def delete_manager(self, user_id: str):
        self.db_int.delete_manager(user_id)

    def get_collaborator(self, collaborator_id: str) -> UserDto:
        return self.db_int.get_collaborator(collaborator_id)
        