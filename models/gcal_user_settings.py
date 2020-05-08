from .oauth2_token import Oauth2Token

class GCalUserSettings(Oauth2Token):
    calendar_id: str = ''

    def __init__(self, **token):
        super().__init__(**token)