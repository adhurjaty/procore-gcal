from .user import User
from .gcal_user_settings import GCalUserSettings

class CalendarUser(User):
    gcal_data: GCalUserSettings = GCalUserSettings()

    def __init__(self):
        super().__init__()
        self.table_name = 'Collaborator'
