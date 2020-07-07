import arrow
from copy import deepcopy
from enum import Enum
import inflect
import os
import json
from pathlib import Path
from typing import List
from urllib.parse import urlencode

from .api_endpoints import *
from .oauth_session_wrapper import OauthSessionWrapper
from interactor.user_response import UserResponse
from interactor.attachment import Attachment
from interactor.person import Person
from interactor.rfi import Rfi
from interactor.submittal import Submittal
from interactor.change_order import ChangeOrder
from interactor.procore_event import ProcoreEvent
from util.utils import parallel_for


RESROUCE_ID_PREFIX = 'Procore resource ID: '
p_engine = inflect.engine()


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
    oauth: OauthSessionWrapper = None
    user: UserResponse = None
    view_mode: ViewMode = ViewMode.PLAIN_TEXT
    base_url: str = ''

    def __init__(self, user: UserResponse, view_mode=None):
        self.oauth = OauthSessionWrapper('gcal',
            token=user.gcal_data.token.get_token(),
            update_token=self.update_token)
        self.user = user
        self.view_mode = view_mode or self.view_mode

    def set_rfi_event(self, rfi: Rfi):
        title = f'RFI #{rfi.number} - {rfi.title}'
        self.set_event(rfi, title)

    def set_submittal_events(self, submittal: Submittal):
        def split_submittal():
            for is_on_site in [True, False]:
                status_str = 'On Site' if is_on_site else 'Final'
                temp_submittal = deepcopy(submittal)
                temp_submittal.submittal_type = status_str
                temp_submittal.due_date = submittal.required_on_site_date \
                    if is_on_site else submittal.due_date
                if not temp_submittal.due_date:
                    continue
                yield temp_submittal

        def set_submittal_event(sub: Submittal):
            title = f'Submittal #{submittal.number} - {submittal.title} {sub.submittal_type}'
            self.set_event(sub, title)

        parallel_for(set_submittal_event, split_submittal())

    def set_event(self, event: ProcoreEvent, title: str):
        existing_event = self._find_existing_event(event, title)
        if existing_event and event.deleted:
            self.delete_event(existing_event)
        if event.deleted:
            return

        cal_event = self.build_event(event, title)
        if existing_event:
            self.update_event(existing_event, cal_event)
        else:
            self.create_event(cal_event)
        
    def build_event(self, procore_event: ProcoreEvent, title: str):
        gcal_event = GCalEvent()
        gcal_event.summary = title
        gcal_event.location = procore_event.location
        gcal_event.start = self.format_date(procore_event.due_date)
        gcal_event.end = gcal_event.start
        gcal_event.attachments = hasattr(procore_event, 'attachments') and [self.render_attachment(a) 
            for a in procore_event.attachments]
        gcal_event.description = self.render_description(procore_event)
        return gcal_event

    def format_date(self, date) -> dict:
        date_str = arrow.get(date).format('YYYY-MM-DD')
        return {'date': date_str}

    def render_attachment(self, attachment: Attachment) -> str:
        return attachment.filename

    def render_description(self, event):
        if self.view_mode == ViewMode.PLAIN_TEXT:
            return self.render_plain_text_description(event)
        if self.view_mode == ViewMode.HTML:
            return self.render_html_description(event)
        raise Exception('Invalid view mode')

    def render_plain_text_description(self, event: ProcoreEvent):
        text = event.link + '\n\n'
        text += hasattr(event, 'description') and event.description and \
            f'Description: {event.description}\n' or ''
        text += hasattr(event, 'submittal_type') and f'Submittal Type: {event.submittal_type}\n' or ''
        text += hasattr(event, 'assignees') and f'Assignees: {self.render_people(event.assignees)}\n' or ''
        text += hasattr(event, 'ball_in_court') and f'Assignee: {self.render_person(event.ball_in_court)}\n' or ''
        text += hasattr(event, 'approver') and event.approver \
            and f'Approver: {self.render_person(event.approver)}\n' or ''
        text += hasattr(event, 'rfi_manager') and event.rfi_manager \
            and f'RFI Manager: {self.render_person(event.rfi_manager)}\n' or ''
        text += hasattr(event, 'schedule_impact') and event.schedule_impact \
            and (f'Schedule Impact: {event.schedule_impact}' + \
            f' {p_engine.plural("day", event.schedule_impact)}\n') or ''
        text += hasattr(event, 'cost_impact') and f'Cost Impact: ${event.cost_impact}\n' or ''
        text += hasattr(event, 'cost_code') and f'Cost Code: {event.cost_code}\n' or ''
        text += hasattr(event, 'questions') and f'Questions: {event.questions}\n' or ''
        text += hasattr(event, 'drawing_number') and f'Drawing Number: {event.drawing_number}\n' or ''
        return text.strip()

    def render_people(self, people: List[Person]):
        return ', '.join(self.render_person(p) for p in people)

    def render_person(self, person: Person):
        return f'{person.full_name} <{person.email}>'

    def update_token(self, token, **kwargs):
        self.user.gcal_data.set_token(token)
        self.oauth.token = token

    def _find_existing_event(self, event: ProcoreEvent, title: str) -> dict:
        identifier = self._get_event_id(event, title)
        query_url = f'{self._events_endpoint()}?{urlencode({"q": identifier})}'
        resp = self.oauth.get(query_url)
        items = resp and resp.json().get('items')
        return items and items[0]

    def _get_event_id(self, event: ProcoreEvent, title: str) -> str:
        sub_type = ''
        if isinstance(event, Submittal):
            sub_type = f' Submittal Type: {event.submittal_type}'

        if event.link:
            return event.link + sub_type
        return title

    def create_event(self, event: GCalEvent):
        self.oauth.post(self._events_endpoint(), json=event.to_dict())

    def delete_event(self, gcal_event: GCalEvent):
        self.oauth.delete(self._event_endpoint(gcal_event.get('id')))
        
    def update_event(self, existing_event: dict, event: GCalEvent):
        self.oauth.patch(self._event_endpoint(existing_event.get('id')), 
            json=event.to_dict())

    def _events_endpoint(self) -> str:
        return GCAL_EVENTS.format(calendar_id=self.user.gcal_data.calendar_id)

    def _event_endpoint(self, event_id) -> str:
        return GCAL_EVENT.format(calendar_id=self.user.gcal_data.calendar_id,
            event_id=event_id)

    def get_calendars(self) -> List[dict]:
        resp = self.oauth.get(GCAL_CALENDARS)
        if not resp or not resp.json().get('items'):
            raise Exception('Cannot find calendars from Google')
        calendars = resp.json()['items']
        for c in calendars:
            c.update(name=c.get('summary'))
        return calendars
