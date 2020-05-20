from models.calendar_user import CalendarUser

class UserResponse(object):
    parent: CalendarUser = None

    def __init__(self, parent):
        self.parent = parent

    def set_gcal_token(self, token: dict):
        self.gcal_data.set_token(**token)

    def __getattr__(self, name):
        try:
            return getattr(self.parent, name)
        except AttributeError as e:
            raise AttributeError(f'{self.parent.__class__} has not attribute {name}')