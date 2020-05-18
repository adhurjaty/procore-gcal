from authlib.integrations.requests_client import OAuth2Session
from typing import List
from enum import Enum

from .api_endpoints import *


RESROUCE_ID_PREFIX = 'Procore resource ID: '


class EventType(Enum):
    RFI = 0
    SUBMITTAL = 1
    CHANGE_ORDER = 2


class GCalEvent:
    summary: str = ''
    location: str = ''
    description: str = ''
    start: str = ''
    end: str = ''
    attendees: List[dict] = []
    attachments : List[str] = []
    send_update: bool = True

    def to_dict(self):
        return {
            'summary': self.summary,
            'description': self.description,
            'location': self.location,
            'start': self.start,
            'end': self.end,
            'attachments': self.attachments,
            'attendees': self.attendees,
            'sendUpdates': 'all' if self.send_update else 'none',
        }


class GCalViewModel:
    oauth: OAuth2Session = None
    user = None

    def __init__(self, user, procore_event):
        self.oauth = OAuth2Session(token=user.gcal_data.access_token,
            update_token=self.update_token)
        self.user = user

    def set_event(self, event):
        existing_event = self.find_existing_event(event.procore_data.resource_id)
        if existing_event and event.deleted:
            self.delete_event(existing_event)
        
        cal_event = self.build_event(event, all_day=True)
        if existing_event:
            self.update_event(existing_event.get('id'), cal_event)
        else:
            self.create_event(cal_event)

    def build_event(self, event):
        pass

    def create_title(self, event):
        if event.type == 'rfi':
            pass
        if event.type == 'submittals':
            pass

    def create_submittal_events(self, submittal):
        pass

    def create_change_order_event(self, change_order):
        pass    

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

