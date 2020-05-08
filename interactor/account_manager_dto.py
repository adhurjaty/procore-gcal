from models.procore_user_settings import ProcoreUserSettings
from models.gcal_user_settings import GCalUserSettings


class AccountManagerDto:
    id: str = ''
    full_name: str = ''
    email: str = ''
    project_id: str = ''
    procore_data: Oauth2Token = ProcoreUserSettings()
    gcal_data: Oauth2Token = GCalUserSettings()

    def set_procore_token(self, token: dict):
        self.procore_data.set_token(**token)
        
    def set_gcal_token(self, token: dict):
        self.gcal_data.set_token(**token)
