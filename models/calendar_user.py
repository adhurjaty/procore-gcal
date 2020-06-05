from sqlalchemy import *
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .user import User
from .gcal_user_settings import GCalUserSettings
from .base import Base, id_col

class CalendarUser(User):
    __tablename__ = 'collaborators'
    id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    gcal_settings_id = Column(UUID(as_uuid=True), ForeignKey('gcal_user_settings.id'))
    gcal_data = relationship('GCalUserSettings', foreign_keys=[gcal_settings_id])

    def __init__(self, gcal_data=None, **kwargs):
        super().__init__(**kwargs)
        self.gcal_data = gcal_data or GCalUserSettings()
        self.gcal_settings_id = gcal_data.id
