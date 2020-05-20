from datetime import datetime

from .gcal_user_settings import GCalUserSettings
from .procore_user_settings import ProcoreUserSettings
from .user import User

class AccountManager(User):
    procore_data: ProcoreUserSettings = None
    gcal_data: GCalUserSettings = None
    subscribed: bool = False
    trial_start: datetime = None
    payment_id: str = ''
    project_id: int = -1