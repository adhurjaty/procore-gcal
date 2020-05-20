from .person import Person
from models.gcal_user_settings import GCalUserSettings
from models.calendar_user import CalendarUser

class UserDto(Person):
    id = ''
    temporary: bool = True
    gcal_data = GCalUserSettings()

    def set_gcal_token(self, token: dict):
        self.gcal_data.set_token(**token)

    def from_model(self, user: CalendarUser):
        self.id = user.id
        self.full_name = user.full_name
        self.email = user.email
        self.temporary = user.temporary
        self.gcal_data = user.gcal_data