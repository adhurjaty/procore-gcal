from typing import List

from .user_dto import UserDto
from .person import Person
from .procore_settings_dto import ProcoreSettingsDto
from models.procore_user_settings import ProcoreUserSettings
from models.gcal_user_settings import GCalUserSettings
from models.account_manager import AccountManager
from models.collaborator_user import CollaboratorUser


class AccountManagerDto(UserDto):
    parent: AccountManager = None
    collaborators: List[Person] = []

    def __init__(self, parent: AccountManager):
        super().__init__(parent)

    def set_procore_token(self, token: dict):
        self.procore_data.set_token(**token)

    def add_collaborators(self, collaborators: List[CollaboratorUser]):
        self.collaborators = [Person(full_name=c.full_name, email=c.email) 
            for c in collaborators]

    @property
    def procore_data(self):
        return ProcoreSettingsDto(self.parent.procore_data)

