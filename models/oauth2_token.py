from sqlalchemy import *

from .model import Model
from .base import Base, id_col

class Oauth2Token(Base):
    __tablename__ = "oauth2_tokens"
    id = id_col()
    access_token = Column(String)
    refresh_token = Column(String)
    token_type = Column(String)
    expires_at = Column(Integer)

    def __init__(self, **kwargs):
        self.set_token(**kwargs)

    def get_token(self):
        return {
            'access_token': self.access_token,
            'token_type': self.token_type,
            'refresh_token': self.refresh_token,
            'expires_at': self.expires_at
        }

    def set_token(self, access_token: str = '', refresh_token: str = '', token_type: str = '', 
        expires_at: int = 0, **kwargs):

        self.access_token = access_token
        self.refresh_token = refresh_token
        self.token_type = token_type
        self.expires_at = expires_at

    