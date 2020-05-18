from typing import List

from .procore_event import ProcoreEvent


class Submittal(ProcoreEvent):
    ball_in_court: str = ''
    approver: str = ''
    attachments: List[str] = []
    required_on_site_date = None
