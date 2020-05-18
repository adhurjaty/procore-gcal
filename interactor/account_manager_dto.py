from typing import List

from models.procore_user_settings import ProcoreUserSettings
from models.gcal_user_settings import GCalUserSettings


class AccountManagerDto:
    id: str = ''
    full_name: str = ''
    email: str = ''
    project_id: str = ''
    procore_data = ProcoreUserSettings()
    gcal_data = GCalUserSettings()
    collaborators = []
    subscribed: bool = False
    temporary: bool = True

    def set_procore_token(self, token: dict):
        self.procore_data.set_token(**token)
        
    def set_gcal_token(self, token: dict):
        self.gcal_data.set_token(**token)
