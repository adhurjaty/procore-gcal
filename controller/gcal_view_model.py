from authlib.integrations.requests_client import OAuth2Session
from typing import List


class GCalViewModel:
    oauth: OAuth2Session = None

    def __init__(self, user):
        self.oauth = OAuth2Session(token=user.gcal_token.token,
            update_token=self.update_token)
        self.user = user

    def update_token(self, token):
        self.user.set_gcal_token(token)

    def send(self, procore_event):
        existing_event = self.find_existing_event(**procore_event)
        gcal_event = self.convert_procore_event(procore_event)

        if not existing_event and not procore_event.deleted:
            self.create_event(gcal_event)

        if procore_event.deleted:
            self.delete_event(existing_event)
            return

        
        


    def convert_procore_event(self, procore_event) -> GCalEvent:
        event = GCalEvent()
        # TODO: do stuff
        return event


class GCalEvent:
    summary: str = ''
    start: str = ''
    end: str = ''
    description: str = ''
    location: str = ''
    attendees: List[dict] = []
    procore_data = None
    send_update: bool = False

    def to_dict(self):
        return {
            'summary': self.summary,
            'start': self.start,
            'end': self.end,
            'description': self.description,
            'location': self.location,
            'attendees': self.attendees,
            'procore_data': '',
            'send_update': self.send_update,
        }

