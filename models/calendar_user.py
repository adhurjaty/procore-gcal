from sqlalchemy import *

from .user import User
from .gcal_user_settings import GCalUserSettings
from .base import Base, id_col

class CalendarUser(User):
    __tablename__ = 'collaborators'
    id = Column(ForeignKey('user.id'), primary_key=True)
    gcal_data: GCalUserSettings = GCalUserSettings()

    def __init__(self, **kwargs):
        super().__init__(user_type='collaborator', **kwargs)
