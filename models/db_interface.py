from typing import List

from .account_manager import AccountManager
from .model import Model

class DBInterface:
    
    def update(self, table_name: str, model: Model):
        pass

    def get_users_from_project_id(self, project_id: int) -> List[AccountManager]:
        user = AccountManager()
        user.email = 'adhurjaty@gmail.com'
        