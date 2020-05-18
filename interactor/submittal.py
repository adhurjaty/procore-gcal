import arrow
from typing import List

from .attachment import Attachment
from .person import Person
from .procore_event import ProcoreEvent


class Submittal(ProcoreEvent):
    ball_in_court: str = ''
    approver: str = ''
    attachments: List[str] = []
    required_on_site_date = None

    def update_from_dict(self, values):
        super().update_from_dict(values)

        if self.ball_in_court and len(self.ball_in_court) > 0:
            self.ball_in_court = Person(**self.ball_in_court[0])
        
        approvers = values.get('approvers')
        if approvers and len(approvers) > 0:
            self.approver = Person(**approvers[0].get('user'))

        self.attachments = self.attachments and [Attachment(**a) for a in self.attachments]
        self.required_on_site_date = self.required_on_site_date and \
            arrow.get(self.required_on_site_date).datetime.date()
