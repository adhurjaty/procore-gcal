from typing import List

from .presenter_interface import PresenterInterface
from .account_manager_dto import AccountManagerDto
from .procore_event import ProcoreEvent
from .user_dto import UserDto
from models.db_interface import DBInterface

class UseCaseInteracor:
    presenter: PresenterInterface = None
    db_int: DBInterface = None

    def __init__(self, presenter: PresenterInterface, db_int: DBInterface):
        self.presenter = presenter
        self.db_int = db_int

    def get_user_from_token(self, token: str) -> AccountManagerDto:
        user = db_int.get_user_from_token(token)
        user_dto = AccountManagerDto()
        user_dto.from_model(user)

        return user_dto

    def update_user(self, user: AccountManagerDto) -> AccountManagerDto:
        pass

    def get_users_in_project(self, project_id: int) -> List[AccountManagerDto]:
        pass

    def get_event(self, project_id: int = 0, resource_name: str = '', 
        resource_id: int = 0) -> ProcoreEvent:

        pass

    def update_gcal(self, users: List[AccountManagerDto], event: ProcoreEvent):
        pass

    def get_procore_user_info(self, token: dict):
        pass

    def delete_user(self, user_id: str):
        pass

    def get_collaborator(self, collaborator_id: str) -> UserDto:
        pass
        