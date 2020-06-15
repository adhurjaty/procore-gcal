from .email_settings import EmailSettings
from .event_settings import EventSettings

def get_email_settings():
    return [
        EmailSettings(name='Add/Remove Collaborator')
    ]

def get_event_settings():
    return [
        EventSettings(name='RFIs'),
        EventSettings(name='Submittals')
    ]