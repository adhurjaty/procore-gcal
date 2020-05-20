from typing import List

from .user_dto import UserDto
from models.procore_user_settings import ProcoreUserSettings
from models.gcal_user_settings import GCalUserSettings


class AccountManagerDto(UserDto):
    project_id: str = ''
    procore_data = ProcoreUserSettings()
    collaborators: List[str] = []
    subscribed: bool = False

    def set_procore_token(self, token: dict):
        self.procore_data.set_token(**token)

