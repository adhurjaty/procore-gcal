from typing import List

from .presenter_interface import PresenterInterface
from .account_manager_dto import AccountManagerDto
from .procore_event import ProcoreEvent
from .user_dto import UserDto
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
        user_dto = AccountManagerDto()
        user_dto.from_model(user)
        user_dto.add_collaborators(collaborators)

        return user_dto

    def update_user(self, user: UserDto) -> UserDto:
        model_user = self._convert_to_model_user(user)
        model_user.save(self.db_int)
        return model_user

    def _convert_to_model_user(self, user: UserDto) -> CalendarUser:
        model_user = CalendarUser()
        if isinstance(user, AccountManagerDto):
            model_user = AccountManager()
            model_user.procore_data = user.procore_data
            model_user.collaborator_ids = self._get_collaborator_ids(
                [c.email for c in user.collaborators]
            )
            model_user.subscribed = user.subscribed
            model_user.payment_id = user.payment_id
        
        model_user.id = user.id
        model_user.email = user.email
        model_user.full_name = user.full_name
        model_user.gcal_data = user.gcal_data
        model_user.temporary = user.temporary

        return model_user

    def _get_collaborator_ids(self, emails: List[str]):
        collabs = self.db_int.get_collaborators_from_emails(emails)
        return [c.id for c in collabs]

    def get_users_in_project(self, project_id: int) -> List[AccountManagerDto]:
        return self.db_int.get_users_from_project_id(project_id)

    def get_event(self, project_id: int = 0, resource_name: str = '', 
        resource_id: int = 0) -> ProcoreEvent:

        return self.presenter.get_event(project_id=project_id, resource_name=resource_name,
            resource_id=resource_id)

    def update_gcal(self, users: List[AccountManagerDto], event: ProcoreEvent):
        def update_cal(user: AccountManagerDto):
            pass

    def get_procore_user_info(self, token: dict):
        pass

    def delete_user(self, user_id: str):
        pass

    def get_collaborator(self, collaborator_id: str) -> UserDto:
        pass
        