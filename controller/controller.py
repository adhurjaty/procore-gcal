import json


procore_token_file = 'temp_db/procore_token.json'

class Controller:
    def __init__(self):
        pass

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

    def get_token(self, name=''):
        with open(procore_token_file, 'r') as f:
            token = json.load(f)
        result = {
            'access_token': token['token'],
            'token_type': 'Bearer',
            'refresh_token': token['refresh_token'],
            'expires_at': token['expires_at']
        }
        return result

    def update_token(self, token, refresh_token=None, access_token=None):
        self.save_token(**token)
        
