import json
import os
from pathlib import Path
import psycopg2
from typing import List

from .account_manager import AccountManager
from .calendar_user import CalendarUser
from .model import Model

secret_path = os.path.join(Path(os.path.realpath(__file__)).parent.parent, 'secrets')

class DBInterface:
    conn = None
    
    def __init__(self):
        settings = self._load_db_settings()
        self.conn = psycopg2.connect(f'dbname={settings.get("DATABASE_NAME")} ' + \
            f'user={settings.get("DATABASE_USER")}')

    def _load_db_settings(self) -> dict:
        with open(os.path.join(secret_path, 'app.config'), 'r') as f:
            return json.load(f)
        
    def update(self, table_name: str, model: Model):
        pass

    def get_user_from_token(self, token: dict) -> AccountManager:
        cur = self.conn.cursor()
        
        manager_result = self._get_manager_info(token, cur)
        manager = self._fill_base_manager(token, AccountManager(), manager_result)
        
        manager.procore_data.calendar_event_types = self._get_calendar_event_settings(
            manager_result['procore_id'], cur)

        manager.procore_data.email_settings = self._get_email_settings(
            manager_result['procore_id'], cur)

        return manager

    def _get_manager_info(self, token: dict, cur):
        query = '''SELECT am.*, u.email, u.full_name, ot.access_token, ot.refresh_token, 
                ot.token_type, ot.expires_at, ps.id AS procore_id 
            FROM Oauth2Tokens ot
            INNER JOIN ProcoreSettings ps ON ot.id = ps.token_id
            INNER JOIN AccountManagers am ON am.procore_settings_id = ps.id
            INNER JOIN Users u ON am.user_id = u.id
            WHERE ot.access_token = %(access_token)s
        '''
        cur.execute(query, {'access_token': token})
        return cur.fetchone()

    def _fill_base_manager(self, token: dict, manager: AccountManager, manager_result) -> AccountManager:
        manager.id = manager_result['id']
        manager.email = manager_result['email']
        manager.full_name = manager_result['full_name']
        manager.project_id = manager_result['project_id']
        manager.subscribed = manager_result['subscribed']
        manager.trial_start = manager_result['trial_start']
        manager.payment_id = manager_result['payment_id']
        manager.temporary = manager_result['temporary']
        manager.procore_data.set_token(**manager_result)

        return manager

    def _get_calendar_event_settings(self, procore_id: str, cur) -> dict:
        query = '''SELECT ces.name, uces.enabled FROM CalendarEventSettings ces
            INNER JOIN UserCalendarEventSettings uces ON ces.id = uces.event_id
            WHERE uces.procore_id = %(procore_id)s
        '''
        cur.execute(query, {'procore_id': procore_id})
        calendar_settings = cur.fetchall()

        return {s['name']: s['enabled'] for s in calendar_settings}

    def _get_email_settings(self, procore_id: str, cur) -> dict:
        query = '''SELECT es.name, ues.enabled FROM EmailSettings es
            INNER JOIN UserEmailSettings ues ON es.id = ues.setting_id
            WHERE ues.procore_id = %(procore_id)s
        '''
        cur.execute(query, {'procore_id': procore_id})
        email_settings = cur.fetchall()

        return {s['name']: s['enabled'] for s in email_settings}

    def get_users_from_project_id(self, project_id: int) -> List[AccountManager]:
        return [self.user]

    def get_user_collaborators(self, user) -> List[CalendarUser]:
        return []

