from typing import List

from .user_dto import UserDto
from .person import Person
from .procore_settings_dto import ProcoreSettingsDto
from models.procore_user_settings import ProcoreUserSettings
from models.gcal_user_settings import GCalUserSettings
from models.account_manager import AccountManager
from models.collaborator_user import CollaboratorUser
from models.procore_settings import ProcoreSettings
from models.event_settings import EventSettings
from models.email_settings import EmailSettings


class AccountManagerDto(UserDto):
    parent: AccountManager = None

    def __init__(self, parent: AccountManager):
        super().__init__(parent)

    def set_procore_token(self, token: dict):
        self.procore_data.token = token

    @property
    def procore_data(self):
        return ProcoreSettingsDto(self.parent.procore_data)

    @property
    def collaborators(self):
        return [Person(full_name=c.full_name, email=c.email) 
            for c in self.parent.collaborators]

    def set_collaborators(self, value: List[Person]):
        self.parent.collaborators = \
            [CollaboratorUser(manager=self.parent, full_name=v.full_name, email=v.email)
                for v in value]

    def add_collaborators(self, collabs: List[Person]):
        for c in collabs:
            self.add_collaborator(c)

    def add_collaborator(self, collab: Person):
        self.parent.collaborators.append(
            CollaboratorUser(manager=self.parent, full_name=collab.full_name, 
            email=collab.email))

    def set_event_settings(self, event_settings: List[dict]):
        self.parent.procore_data.calendar_event_types = list(self._set_settings(
            self.parent.procore_data.calendar_event_types, event_settings, EventSettings))

    def set_email_settings(self, email_settings: List[dict]):
        self.parent.procore_data.email_settings = list(self._set_settings(
            self.parent.procore_data.email_settings, email_settings, EmailSettings))

    def _set_settings(self, old_settings: List[ProcoreSettings], new_settings: List[dict], 
        new_fn):

        for s in new_settings:
            existing = next((e for e in old_settings if e.name == s.get('name')), None)
            if existing:
                existing.enabled = s.get('enabled')
                yield existing
            else:
                yield new_fn(**s)
                

                


