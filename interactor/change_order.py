from typing import List

from .procore_event import ProcoreEvent


class ChangeOrder(ProcoreEvent):
    ball_in_court: str = ''
    approver: str = ''
    attachments: List[str] = []
    