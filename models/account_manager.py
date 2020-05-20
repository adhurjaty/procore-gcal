from datetime import datetime
from typing import List

from .procore_user_settings import ProcoreUserSettings
from .calendar_user import CalendarUser

class AccountManager(CalendarUser):
    procore_data: ProcoreUserSettings = None
    subscribed: bool = False
    trial_start: datetime = None
    payment_id: str = ''
    project_id: int = -1
    collaborator_ids: List[str] = []

    def __init__(self):
        super().__init__()
        self.table_name = 'AccountManager'