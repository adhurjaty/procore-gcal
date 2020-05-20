from typing import List

from .user_response import UserResponse
from models.account_manager import AccountManager
from models.calendar_user import CalendarUser

class AccountManagerResponse(UserResponse):
    collaborators: List[UserResponse] = []

    def __init__(self, parent):
        super().__init__(parent)

    def set_collaborators(self, collaborators: List[CalendarUser]):
        self.collaborators = [UserResponse(c) for c in collaborators]

    def set_procore_token(self, token: dict):
        self.procore_data.set_token(**token)