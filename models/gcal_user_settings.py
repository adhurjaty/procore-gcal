from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import *

from .base import Base, id_col
from .oauth2_token import Oauth2Token

class GCalUserSettings(Base):
    __tablename__ = "gcal_user_settings"
    id = id_col()
    calendar_id = Column(String)
    token_id = Column(UUID(as_uuid=True), ForeignKey('oauth2_tokens.id'))
    token = relationship("Oauth2Token", foreign_keys=[token_id])

    def __init__(self, calendar_id='', **token):
        self.calendar_id = calendar_id
        self.token = Oauth2Token()
        self.set_token(token)

    def set_token(self, token: dict):
        self.token.set_token(**token)