from models.procore_user_settings import ProcoreUserSettings
from models.gcal_user_settings import GCalUserSettings

if __name__ == '__main__':
    ProcoreUserSettings(access_token='blah', refresh_token='blee', token_type='Bearer', 
        expires_at=1500)
    GCalUserSettings(calendar_id='something', access_token='blah', refresh_token='blee', 
        token_type='Bearer', expires_at=1500)

    
