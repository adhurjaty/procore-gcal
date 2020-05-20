from typing import List

from .user_dto import UserDto
from .person import Person
from models.procore_user_settings import ProcoreUserSettings
from models.gcal_user_settings import GCalUserSettings
from models.account_manager import AccountManager
from models.calendar_user import CalendarUser


class AccountManagerDto(UserDto):
    parent: AccountManager = None
    collaborators: List[Person] = []

    def __init__(self, parent: AccountManager):
        super().__init__(parent)

    def set_procore_token(self, token: dict):
        self.procore_data.set_token(**token)

    def add_collaborators(self, collaborators: List[CalendarUser]):
        self.collaborators = [Person(full_name=c.full_name, email=c.email) 
            for c in collaborators]

    

