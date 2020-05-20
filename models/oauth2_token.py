from datetime import datetime

from .model import Model

class Oauth2Token(Model):
    access_token: str = ''
    refresh_token: str = ''
    token_type: str = ''
    expires_at: datetime

    def __init__(self, access_token: str = '', refresh_token: str = '', token_type: str = '', 
        expires_at: int = 0, **kwargs):

        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_at = expires_at

    def get_token(self):
        return {
            'access_token': self.access_token,
            'token_type': self.token_type,
            'refresh_token': self.refresh_token,
            'expires_at': self.expires_at
        }

    