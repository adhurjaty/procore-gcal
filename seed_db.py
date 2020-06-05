from models.procore_user_settings import ProcoreUserSettings
from models.gcal_user_settings import GCalUserSettings
from models.email_settings import EmailSettings
from models.event_settings import EventSettings
from models.db_interface import DBInterface

if __name__ == '__main__':
    db_int = DBInterface()

    events = [
        EventSettings(name='RFIs'),
        EventSettings(name='Submittals')
    ]
    emails = [
        EmailSettings(name='All Events', enabled=True)
    ]
    ps = ProcoreUserSettings(emails_settings=emails, calendar_event_types=events, 
        access_token='blah', refresh_token='blee', token_type='Bearer', expires_at=1500)
    gs = GCalUserSettings(calendar_id='something', access_token='blue', refresh_token='blee', 
        token_type='Bearer', expires_at=1500)

    for event in events:
        db_int.insert(event)
    for email in emails:
        db_int.insert(email)

    db_int.insert(ps)
    db_int.insert(gs)

    db_int.commit()

    db_int.delete(gs)
    db_int.delete(ps)
    for email in emails:
        db_int.delete(email)
    for event in events:
        db_int.delete(event)

    db_int.commit()
