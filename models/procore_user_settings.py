from .oauth2_token import Oauth2Token

class ProcoreUserSettings(Oauth2Token):
    email_settings = None
    calendar_event_types: dict = {}
    
    def __init__(self, **token):
        super().__init__(**token)
