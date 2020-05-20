from .person import Person
from models.calendar_user import CalendarUser

class UserDto(object):
    parent: CalendarUser = None

    def __init__(self, parent):
        self.parent = parent

    def set_gcal_token(self, token: dict):
        self.gcal_data.set_token(**token)

    def from_model(self, user: CalendarUser):
        self.id = user.id
        self.full_name = user.full_name
        self.email = user.email
        self.temporary = user.temporary
        self.gcal_data = user.gcal_data

    def __getattr__(self, name):
        try:
            return getattr(self.parent, name)
        except AttributeError as e:
            raise AttributeError(f'{self.parent.__class__} has not attribute {name}')