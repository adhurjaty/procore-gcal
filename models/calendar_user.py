from .user import User
from .gcal_user_settings import GCalUserSettings

class CalendarUser(User):
    gcal_data: GCalUserSettings = None
