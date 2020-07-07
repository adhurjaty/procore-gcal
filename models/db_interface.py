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
from util.utils import get_config


config = get_config()
config = {k.lstrip('DB_').lower(): v for k, v in config.items() if k.startswith('DB_')}
engine = create_engine(f'postgresql://{config.get("username")}:{config.get("password")}' + \
    f'@{config.get("host")}:{config.get("port")}/{config.get("name")}')

createSession = sessionmaker(bind=engine)


class DBInterface:
    session = None

    def __init__(self):
        self.session = createSession()

    def update(self, model: Model):
        self.session.commit()

    def insert(self, model):
        self.session.add(model)
        self.session.commit()
    
    def delete(self, model):
        self.session.delete(model)
        self.session.commit()

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

    def get_user_from_email(self, email: str) -> AccountManager:
        user = self.session.query(User)\
            .filter(User.email == email).first()
        if not user:
            return None
        return self.session.query(AccountManager)\
            .filter(AccountManager.id == user.id).first()

    def get_manager_collaborators(self, manager_id: UUID):
        return self.session.query(CollaboratorUser)\
            .filter(CollaboratorUser.manager_id == manager_id).all()
    
    def get_users_from_project_id(self, project_id: int) -> List[AccountManager]:
        return self.session.query(AccountManager)\
            .filter(AccountManager.project_id == project_id and not AccountManager.temporary)\
            .all()

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

    def delete_manager(self, id: UUID):
        self.session.query(CollaboratorUser).filter(CollaboratorUser.manager_id == id).delete()
        self.session.query(AccountManager).filter(AccountManager.id == id).delete()
        self.session.query(User).filter(User.id == id).delete()
        self.session.commit()

    def close(self):
        self.session.close()

