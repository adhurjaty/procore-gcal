from models.oauth2_token import Oauth2Token


class AccountManagerDto:
    id = ''
    full_name = ''
    email = ''
    procore_token = None

    def change_procore_token(self, token):
        self.procore_token = Oauth2Token(**token)
        
