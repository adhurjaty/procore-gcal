from models.oauth2_token import Oauth2Token


class AccountManagerDto:
    id: str = ''
    full_name: str = ''
    email: str = ''
    procore_token: Oauth2Token = None
    gcal_token: Oauth2Token = None

    def set_procore_token(self, token: dict):
        self.procore_token = Oauth2Token(**token)
        
    def set_gcal_token(self, token: dict):
        self.gcal_token = Oauth2Token(**token)
