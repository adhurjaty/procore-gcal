from typing import List

from .user_dto import UserDto
from .person import Person
from models.procore_user_settings import ProcoreUserSettings
from models.gcal_user_settings import GCalUserSettings
from models.account_manager import AccountManager
from models.calendar_user import CalendarUser


class AccountManagerDto(UserDto):
    project_id: str = ''
    procore_data = ProcoreUserSettings()
    collaborators: List[Person] = []
    subscribed: bool = False
    payment_id: str = ''

    def set_procore_token(self, token: dict):
        self.procore_data.set_token(**token)

    def from_model(self, user: AccountManager):
        super().from_model(user)
        self.project_id = user.project_id
        self.procore_data = user.procore_data
        self.subscribed = user.subscribed
        self.email = user.email
        self.full_name = user.full_name

    def add_collaborators(self, collaborators: List[CalendarUser]):
        self.collaborators = [Person(full_name=c.full_name, email=c.email) 
            for c in collaborators]

