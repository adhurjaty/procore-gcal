import json
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List

from .account_manager import AccountManager
from .collaborator_user import CollaboratorUser
from .oauth2_token import Oauth2Token
from .procore_user_settings import ProcoreUserSettings
from .model import Model

secret_path = os.path.join(Path(os.path.realpath(__file__)).parent.parent, 'secrets')
with open(os.path.join(secret_path, 'app.config'), 'r') as f:
    config = json.load(f)
config = {k.lstrip('DB_').lower(): v for k, v in config.items() if k.startswith('DB_')}
engine = create_engine(f'postgresql://{config.get("username")}:{config.get("password")}' + \
    f'@localhost:{config.get("port")}/{config.get("name")}')

class DBInterface:
    conn = None
    
    def __init__(self):
        settings = self._load_db_settings()
        Session = sessionmaker(bind=engine)
        self.session = Session()
        

    def _load_db_settings(self) -> dict:
        with open(os.path.join(secret_path, 'app.config'), 'r') as f:
            return json.load(f)
        
    def update(self, model: Model):
        pass

    def insert(self, model):
        if isinstance(model, AccountManager):
            self._insert_manager(model)
        else:
            self.session.add(model)
        self.session.commit()
    
    def _insert_manager(self, manager: AccountManager):
        self._insert_or_update(manager.procore_data.token)
        self._insert_or_update(manager.procore_data)
        if manager.gcal_data.token.access_token:
            self._insert_or_update(manager.gcal_data.token)
            self._insert_or_update(manager.gcal_data)
        self.session.add(manager)

    def _insert_or_update(self, model):
        if model.id:
            self.update(model)
        else:
            self.insert(model)

    def commit(self):
        self.session.commit()

    def delete(self, model):
        self.session.delete(model)
        self.session.commit()

    def __del__(self):
        self.session.close()

    def get_user_from_token(self, access_token: str) -> AccountManager:
        matching_token: Oauth2Token = self.session.query(Oauth2Token)\
            .filter(Oauth2Token.access_token == access_token).first()
        if not matching_token:
            return None

        data: ProcoreUserSettings = self.session.query(ProcoreUserSettings)\
            .filter(ProcoreUserSettings.token_id == matching_token.id).first()
        manager_result: AccountManager = self.session.query(AccountManager)\
            .filter(AccountManager.procore_settings_id == data.id).first()
        return manager_result

    def _get_manager_info(self, token: dict, cur):
        query = self._manager_base_query('WHERE ot.access_token = %(access_token)s')
        cur.execute(query, {'access_token': token})
        return cur.fetchone()

    def _manager_base_query(self, where_clause: str):
        return f'''SELECT am.*, u.email, u.full_name, ot.access_token, ot.refresh_token, 
            ot.token_type, ot.expires_at, ps.id AS procore_id, cs.calendar_id,
            cot.access_token AS gcal_access_token, cot.refresh_token AS gcal_refresh_token, 
            cot.token_type AS gcal_token_type, cot.expires_at AS gcal_token_type,
            u.temporary
            FROM Oauth2Tokens ot
            INNER JOIN ProcoreSettings ps ON ot.id = ps.token_id
            INNER JOIN AccountManagers am ON am.procore_settings_id = ps.id
            INNER JOIN Users u ON am.user_id = u.id
            INNER JOIN CalendarSettings cs ON cs.id = u.gcal_settings_id
            INNER JOIN Oauth2Tokens cot ON cs.token_id = cot.id
            {where_clause}
        '''

    def _manager_from_result(self, manager_result, cur):
        manager = self._fill_base_manager(AccountManager(), manager_result)
        
        manager.procore_data.calendar_event_types = self._get_calendar_event_settings(
            manager_result['procore_id'], cur)

        manager.procore_data.email_settings = self._get_email_settings(
            manager_result['procore_id'], cur)

        return manager

    def _fill_base_manager(self, manager: AccountManager, manager_result) -> AccountManager:
        manager.id = manager_result['id']
        manager.email = manager_result['email']
        manager.full_name = manager_result['full_name']
        manager.project_id = manager_result['project_id']
        manager.subscribed = manager_result['subscribed']
        manager.trial_start = manager_result['trial_start']
        manager.payment_id = manager_result['payment_id']
        manager.temporary = manager_result['temporary']
        manager.procore_data.set_token(**manager_result)
        manager.gcal_data.calendar_id = manager_result['calendar_id']
        manager.gcal_data.set_token(**{k.lstrip('gcal_'): v 
            for k, v in manager_result if k.startswith('gcal_')})

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
        cur = self.conn.cursor()

        query = self._manager_base_query('WHERE am.project_id = %(project_id)d')
        cur.execute(query, {'project_id': project_id})
        manager_results = cur.fetchall()

        return [self._manager_from_result(result) for result in manager_results]


    def get_user_collaborators(self, user) -> List[CollaboratorUser]:
        cur = self.conn.cursor()
        query = '''SELECT c.id, u.email, u.full_name, ot.access_token, ot.refresh_token,
            ot.token_type, ot.expires_at, cs.calendar_id, u.temporary
            FROM Collaborators c
            INNER JOIN Users u ON u.id = c.user_id
            INNER JOIN CalendarSettings cs ON u.gcal_settings_id = cs.id
            INNER JOIN Oauth2Tokens ot ON ot.id = cs.token_id
            WHERE c.manager_id = %(manager_id)s
        '''
        cur.execute(query, {'manager_id': user.id})
        results = cur.fetchall()

        return [self._fill_collaborator(result) for result in results]

    def _fill_collaborator(self, result):
        user = CollaboratorUser()
        user.id = result['id']
        user.email = result['email']
        user.full_name = result['full_name']
        user.temporary = result['temporary']
        user.gcal_data.set_token(**result)
        user.gcal_data.calendar_id = result['calendar_id']

    def get_collaborators_from_emails(self, emails: List[str]) -> List[CollaboratorUser]:
        return []

    def get_collaborator(self, id: str) -> CollaboratorUser:
        pass

    def delete_manager(self, id: str):
        pass

