import json
import os
from pathlib import Path
from typing import List

from .account_manager import AccountManager
from .calendar_user import CalendarUser
from .model import Model

secret_path = os.path.join(Path(os.path.realpath(__file__)).parent.parent, 'secrets')

class DBInterface:
    
    def __init__(self):
        self.user = AccountManager()
        self.user.email = 'adhurjaty@gmail.com'
        self.user.full_name = 'Anil Dhurjaty'
        self.user.project_id = 18918
        
        with open(os.path.join(secret_path, 'temp.json'), 'r') as f:
            secrets = json.load(f)
            
        self.user.procore_data.access_token = secrets['procore_access_token']
        self.user.procore_data.refresh_token = secrets['procore_refresh_token']
        self.user.gcal_data.access_token = secrets['gcal_access_token']
        self.user.gcal_data.refresh_token = secrets['gcal_refresh_token']
        self.user.gcal_data.calendar_id = secrets['calendar_id']
        
    def update(self, table_name: str, model: Model):
        pass

    def get_user_from_token(self, token) -> AccountManager:
        return self.user

    def get_users_from_project_id(self, project_id: int) -> List[AccountManager]:
        return [self.user]

    def get_user_collaborators(self, user) -> List[CalendarUser]:
        return []

