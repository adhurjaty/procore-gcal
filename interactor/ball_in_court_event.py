from typing import List

from .attachment import Attachment
from .person import Person
from .procore_event import ProcoreEvent

class BallInCourtEvent(ProcoreEvent):
    ball_in_court: str = ''
    approver: Person = None
    attachments: List[str] = []

    def update_from_dict(self, values):
        super().update_from_dict(values)

        if self.ball_in_court and len(self.ball_in_court) > 0:
            self.ball_in_court = Person(**self.ball_in_court[0])
        
        approvers = values.get('approvers')
        if approvers and len(approvers) > 0:
            self.approver = Person(**approvers[0].get('user'))

        self.attachments = self.attachments and [Attachment(**a) for a in self.attachments]
