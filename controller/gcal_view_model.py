import arrow
from authlib.integrations.requests_client import OAuth2Session
from typing import List
from enum import Enum
from util.utils import parallel_for

from .api_endpoints import *
from interactor.attachment import Attachment
from interactor.person import Person
from interactor.rfi import Rfi
from interactor.submittal import Submittal
from interactor.change_order import ChangeOrder
from interactor.procore_event import ProcoreEvent


RESROUCE_ID_PREFIX = 'Procore resource ID: '


class ViewMode(Enum):
    PLAIN_TEXT = 0
    HTML = 1


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
    view_mode: ViewMode = ViewMode.PLAIN_TEXT

    def __init__(self, user, view_mode=None):
        self.oauth = OAuth2Session(token=user.gcal_data.access_token,
            update_token=self.update_token)
        self.user = user
        self.view_mode = view_mode or self.view_mode

    def set_rfi_event(self, rfi: Rfi):
        title = f'RFI #{rfi.number} - {rfi.title}'
        existing_event = self.find_existing_event(title)
        if existing_event and rfi.deleted:
            self.delete_event(existing_event)

        cal_event = self.build_event(rfi)
        if existing_event:
            self.update_event(existing_event.get('id'), cal_event)
        else:
            self.create_event(cal_event)

    def set_submittal_events(self, submittal: Submittal):
        def set_submittal_event(is_on_site: bool):
            status_str = 'On Site' if is_on_site else 'Final'
            title = f'Submittal #{submittal.number} - {submittal.title} {status_str}'
            existing_event = self.find_existing_event(title)
            if existing_event and submittal.deleted:
                self.delete_event(existing_event)

            due_date = submittal.required_on_site_date if is_on_site else submittal.due_date
            cal_event = self.build_event(submittal, override_due_date=due_date)
            if existing_event:
                self.update_event(existing_event.get('id'), cal_event)
            else:
                self.create_event(cal_event)

        parallel_for(set_submittal_event, [True, False])
        

    def build_event(self, procore_event, override_due_date=None):
        gcal_event = GCalEvent()
        gcal_event.summary = self.create_title(procore_event)
        gcal_event.location = procore_event.location
        gcal_event.start = self.format_date(override_due_date or gcal_event.due_date)
        gcal_event.end = gcal_event.start
        gcal_event.attachments = procore_event.attachments and [self.render_attachment(a) 
            for a in procore_event.attachments]
        gcal_event.description = self.render_description(procore_event)


    def format_date(self, date) -> str:
        return arrow.get(date).format('YYYY-MM-DD')

    def render_attachments(self, attachment: Attachment) -> str:
        return attachment.filename

    def render_description(self, event):
        if self.view_mode == ViewMode.PLAIN_TEXT:
            return self.render_plain_text_description(event)
        if self.view_mode == ViewMode.HTML:
            return self.render_html_description(event)
        raise Exception('Invalid view mode')

    def render_plain_text_description(self, event: ProcoreEvent):
        text = ''
        text += event.link + '\n\n'
        text += event.assignees and f'Assignees: {self.render_people(event.assignees)}\n'
        text += event.manager and f'RFI Manger: {self.render_person(event.manger)}\n'
        text += event.schedule_impact and f'Schedule Impact: {event.schedule_impact}\n'
        text += event.cost_impact and f'Cost Impact: {event.cost_impact}\n'
        text += event.cost_code and f'Cost Code: {event.code_code}\n'

    def render_people(self, people: List[Person]):
        return ', '.join(render_person(p) for p in people)

    def render_person(self, person: Person):
        return f'{person.full_name} <{person.email}>'
        
    def create_submittal_events(self, submittal):
        pass

    def create_change_order_event(self, change_order):
        pass    

    def update_token(self, token):
        self.user.set_gcal_token(token)

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

