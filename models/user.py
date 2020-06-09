from sqlalchemy import *
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from uuid import uuid4

from .base import Base, id_col
from .gcal_user_settings import GCalUserSettings

class User(Base):
    __tablename__ = 'users'
    id = id_col()
    email = Column(String)
    full_name = Column(String)
    temporary = Column(Boolean)
    type = Column(String)

    gcal_settings_id = Column(UUID(as_uuid=True), ForeignKey('gcal_user_settings.id'))
    gcal_data = relationship('GCalUserSettings', foreign_keys=[gcal_settings_id])

    __mapper_args__ = {
        'polymorphic_on': type
    }

    def __init__(self, gcal_data=None, email='', full_name='', temporary=True, **kwargs):
        self.email = email
        self.full_name = full_name
        self.temporary = temporary
        self.gcal_data = gcal_data or GCalUserSettings()
        self.gcal_settings_id = gcal_data.id

    
