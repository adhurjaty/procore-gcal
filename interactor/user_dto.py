from models.gcal_user_settings import GCalUserSettings

class UserDto:
    id = ''
    full_name = ''
    email = ''
    temporary: bool = True

    gcal_data = GCalUserSettings()

    def set_gcal_token(self, token: dict):
        self.gcal_data.set_token(**token)