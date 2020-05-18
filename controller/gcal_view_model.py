from authlib.integrations.requests_client import OAuth2Session
from typing import List

from .api_endpoints import *


RESROUCE_ID_PREFIX = 'Procore resource ID: '


class GCalEvent:
    summary: str = ''
    start: str = ''
    end: str = ''
    description: str = ''
    location: str = ''
    attendees: List[dict] = []
    procore_data = None
    send_update: bool = False
    deleted: bool = False

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


class GCalViewModel:
    oauth: OAuth2Session = None
    event: GCalEvent = None
    user = None

    def __init__(self, user, procore_event):
        self.oauth = OAuth2Session(token=user.gcal_data.access_token,
            update_token=self.update_token)
        self.user = user
        self.event = self.convert_procore_event(procore_event)

    def update_token(self, token):
        self.user.set_gcal_token(token)

    def convert_procore_event(self, procore_event):
        pass

    def send(self):
        existing_event = self.find_existing_event(self.event.procore_data.resource_id)

        if not existing_event:
            if not self.event.deleted:
                self.create_event()
            return

        if self.event.deleted:
            self.delete_event(existing_event)
            return

        self.update_event(existing_event)
        
    def find_existing_event(self, resource_id: str) -> dict:
        resp = self.oauth.get(self.events_endpoint(), 
            q=f'{RESROUCE_ID_PREFIX}{resource_id}')
        return resp and resp.json()

    def create_event(self):
        self.oauth.post(GCAL_EVENTS, json=self.event.to_dict())
        
    def update_event(self, existing_event):
        self.oauth.put()

    def events_endpoint(self) -> str:
        return GCAL_EVENTS.format(calendar_id=self.user.gcal.calendar_id)

    def event_endpoint(self, event_id) -> str:
        return GCAL_EVENT.format(calendar_id=self.user.gcal.calendar_id,
            event_id=event_id)

