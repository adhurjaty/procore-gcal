from models.procore_user_settings import ProcoreUserSettings
from models.gcal_user_settings import GCalUserSettings
from models.email_settings import EmailSettings
from models.event_settings import EventSettings

if __name__ == '__main__':
    events = [
        EventSettings(name='RFIs'),
        EventSettings(name='Submittals')
    ]
    emails = [
        EmailSettings(name='All Events', enabled=True)
    ]
    ps = ProcoreUserSettings(emails_settings=emails, calendar_event_types=events, 
        access_token='blah', refresh_token='blee', token_type='Bearer', expires_at=1500)
    gs = GCalUserSettings(calendar_id='something', access_token='blah', refresh_token='blee', 
        token_type='Bearer', expires_at=1500)

    
