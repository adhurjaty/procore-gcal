import json
from interactor.account_manager_dto import AccountManagerDto

procore_token_file = 'temp_db/procore_token.json'




class Controller:
    rfis = []
    def __init__(self):
        self.manager = AccountManagerDto()
        self.manager.id = 55
        self.manager.email = 'adhurjaty@gmail.com'
        self.manager.full_name = 'Anil Dhurjaty'
        self.manager.project_id = 12345
        self.manager.company_id = 26972

    def save_token(self, access_token=None, refresh_token=None, token_type=None, 
        expires_at=None, **kwargs):
        
        # temporary implementation
        contents = {
            'token': access_token,
            'refresh_token': refresh_token,
            'token_type': token_type,
            'expires_at': expires_at
        }
        with open(procore_token_file, 'w') as f:
            json.dump(contents, f)

    def get_token(self, email):
        with open(procore_token_file, 'r') as f:
            token = json.load(f)
        result = {
            'access_token': token['token'],
            'token_type': 'Bearer',
            'refresh_token': token['refresh_token'],
            'expires_at': token['expires_at']
        }
        return result

    def update_token(self, email, token, refresh_token=None, access_token=None):
        self.save_token(**token)

    def get_account_manager(self, login: str):
        return self.manager

    def get_user_from_token(self, token):
        return self.manager

    def update_user(self, user):
        self.manager = user

    def get_users_in_project(self, project_id):
        return [self.manager]

    def update_gcal(self, users, event_object):
        pass
