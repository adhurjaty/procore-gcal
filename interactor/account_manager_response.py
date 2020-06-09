from typing import List

from .user_response import UserResponse
from .named_item import NamedItem
from models.account_manager import AccountManager
from models.collaborator_user import CollaboratorUser

class AccountManagerResponse(UserResponse):
    collaborators: List[UserResponse] = []
    calendars: List[NamedItem] = []
    projects: List[NamedItem] = []

    def __init__(self, parent):
        super().__init__(parent)

    def set_collaborators(self, collaborators: List[CollaboratorUser]):
        self.collaborators = [UserResponse(c) for c in collaborators]

    def set_procore_token(self, token: dict):
        self.procore_data.set_token(**token)