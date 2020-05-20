from datetime import datetime

from .procore_user_settings import ProcoreUserSettings
from .calendar_user import CalendarUser

class AccountManager(CalendarUser):
    procore_data: ProcoreUserSettings = None
    subscribed: bool = False
    trial_start: datetime = None
    payment_id: str = ''
    project_id: int = -1