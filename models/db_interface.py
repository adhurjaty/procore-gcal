import json
import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
from uuid import UUID

from .account_manager import AccountManager
from .collaborator_user import CollaboratorUser
from .oauth2_token import Oauth2Token
from .procore_user_settings import ProcoreUserSettings
from .user import User
from .model import Model

secret_path = os.path.join(Path(os.path.realpath(__file__)).parent.parent, 'secrets')
with open(os.path.join(secret_path, 'app.config'), 'r') as f:
    config = json.load(f)
config = {k.lstrip('DB_').lower(): v for k, v in config.items() if k.startswith('DB_')}
engine = create_engine(f'postgresql://{config.get("username")}:{config.get("password")}' + \
    f'@{config.get("host")}:{config.get("port")}/{config.get("name")}')

createSession = sessionmaker(bind=engine)
session = None

class DBInterface:
    def __init__(self):
        settings = self._load_db_settings()

    def _load_db_settings(self) -> dict:
        with open(os.path.join(secret_path, 'app.config'), 'r') as f:
            return json.load(f)
        
    def update(self, model: Model):
        session.commit()

    def insert(self, model):
        session.add(model)
        session.commit()
    
    # def _insert_manager(self, manager: AccountManager):
    #     self._insert_or_update(manager.procore_data.token)
    #     self._insert_or_update(manager.procore_data)
    #     if manager.gcal_data.token.access_token:
    #         self._insert_or_update(manager.gcal_data.token)
    #         self._insert_or_update(manager.gcal_data)
    #     session.add(manager)

    # def _insert_or_update(self, model):
    #     if model.id:
    #         self.update(model)
    #     else:
    #         self.insert(model)

    def delete(self, model):
        session.delete(model)
        session.commit()

    def get_user_from_token(self, access_token: str) -> AccountManager:
        matching_token: Oauth2Token = session.query(Oauth2Token)\
            .filter(Oauth2Token.access_token == access_token).first()
        if not matching_token:
            return None

        data: ProcoreUserSettings = session.query(ProcoreUserSettings)\
            .filter(ProcoreUserSettings.token_id == matching_token.id).first()
        manager_result: AccountManager = session.query(AccountManager)\
            .filter(AccountManager.procore_settings_id == data.id).first()
        return manager_result

    def get_user_from_email(self, email: str) -> AccountManager:
        user = session.query(User)\
            .filter(User.email == email).first()
        if not user:
            return None
        return session.query(AccountManager)\
            .filter(AccountManager.id == user.id).first()

    def get_manager_collaborators(self, manager_id: UUID):
        return session.query(CollaboratorUser)\
            .filter(CollaboratorUser.manager_id == manager_id).all()
    
    # def _get_calendar_event_settings(self, procore_id: str, cur) -> dict:
    #     query = '''SELECT ces.name, uces.enabled FROM CalendarEventSettings ces
    #         INNER JOIN UserCalendarEventSettings uces ON ces.id = uces.event_id
    #         WHERE uces.procore_id = %(procore_id)s
    #     '''
    #     cur.execute(query, {'procore_id': procore_id})
    #     calendar_settings = cur.fetchall()

    #     return {s['name']: s['enabled'] for s in calendar_settings}

    # def _get_email_settings(self, procore_id: str, cur) -> dict:
    #     query = '''SELECT es.name, ues.enabled FROM EmailSettings es
    #         INNER JOIN UserEmailSettings ues ON es.id = ues.setting_id
    #         WHERE ues.procore_id = %(procore_id)s
    #     '''
    #     cur.execute(query, {'procore_id': procore_id})
    #     email_settings = cur.fetchall()

    #     return {s['name']: s['enabled'] for s in email_settings}

    def get_users_from_project_id(self, project_id: int) -> List[AccountManager]:
        return session.query(AccountManager)\
            .filter(AccountManager.project_id == project_id).all()


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

