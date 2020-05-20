from models.calendar_user import CalendarUser

class UserResponse(object):
    parent: CalendarUser = None

    def __init__(self, parent):
        self.parent = parent