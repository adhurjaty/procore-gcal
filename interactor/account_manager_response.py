from typing import List

from .user_response import UserResponse
from .named_item import NamedItem
from models.account_manager import AccountManager
from models.collaborator_user import CollaboratorUser

class AccountManagerResponse(UserResponse):
    calendars: List[NamedItem] = []
    projects: List[NamedItem] = []

    def __init__(self, parent: AccountManager):
        super().__init__(parent)

    @property
    def collaborators(self):
        return [UserResponse(c) for c in self.parent.collaborators]

    @collaborators.setter
    def collaborators(self, collabs: List[UserResponse]):
        self.parent.collaborators = [r.parent for r in collabs]

    def set_procore_token(self, token: dict):
        self.procore_data.set_token(**token)