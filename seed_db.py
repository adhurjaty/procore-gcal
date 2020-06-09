from models.procore_user_settings import ProcoreUserSettings
from models.gcal_user_settings import GCalUserSettings
from models.email_settings import EmailSettings
from models.event_settings import EventSettings
from models.db_interface import DBInterface
from models.account_manager import AccountManager
from models.collaborator_user import CollaboratorUser

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
    gs = [
        GCalUserSettings(calendar_id='something', access_token='blue', refresh_token='blee', 
            token_type='Bearer', expires_at=1500),
        GCalUserSettings(calendar_id='else', access_token='asfd', refresh_token='oilkjl', 
            token_type='Bearer', expires_at=1500),
        GCalUserSettings(calendar_id='thisthing', access_token='token', refresh_token='oilkjl', 
            token_type='Bearer', expires_at=1500)
    ]

    user = AccountManager(procore_data=ps,
        payment_id='payme',
        project_id=12345,
        gcal_data=gs[2],
        full_name='Manager Man',
        email='mgr@example.com')

    collabs = [
        CollaboratorUser(manager=user, gcal_data=gs[0], full_name='Collab One', 
            email='collab@example.com'),
        CollaboratorUser(manager=user, gcal_data=gs[1], full_name='Collab Two', 
            email='orator@example.com')
    ]

    for event in events:
        db_int.insert(event)
    for email in emails:
        db_int.insert(email)

    db_int.insert(ps)
    for g in gs:
        db_int.insert(g)

    db_int.insert(user)
    for collab in collabs:
        db_int.insert(collab)

    db_int.commit()

    for collab in collabs:
        db_int.delete(collab)
    db_int.delete(user)
    for g in gs:
        db_int.delete(g)
    db_int.delete(ps)
    for email in emails:
        db_int.delete(email)
    for event in events:
        db_int.delete(event)

    db_int.commit()
