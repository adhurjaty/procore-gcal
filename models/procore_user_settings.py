from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import *

from .base import Base, id_col
from .oauth2_token import Oauth2Token

email_settings_association = Table(
    'email_association', Base.metadata,
    Column('email_id', UUID(as_uuid=True), ForeignKey('email_settings.id')),
    Column('procore_id', UUID(as_uuid=True), ForeignKey('procore_user_settings.id'))
)

event_settings_association = Table(
    'event_association', Base.metadata,
    Column('event_id', UUID(as_uuid=True), ForeignKey('event_settings.id')),
    Column('procore_id', UUID(as_uuid=True), ForeignKey('procore_user_settings.id'))
)

class ProcoreUserSettings(Base):
    __tablename__ = 'procore_user_settings'
    id = id_col()
    email_settings = relationship("EmailSettings", secondary=email_settings_association)
    calendar_event_types = relationship("EventSettings", secondary=event_settings_association)
    token_id = Column(UUID(as_uuid=True), ForeignKey('oauth2_tokens.id'))
    token = relationship("Oauth2Token", foreign_keys=[token_id])

    def __init__(self, email_settings=[], calendar_event_types=[], **token):
        self.token = Oauth2Token(**token)
        self.email_settings = email_settings
        self.calendar_event_types = calendar_event_types

    def __getattr__(self, name):
        return getattr(self.token, name)
