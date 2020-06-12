from datetime import datetime
from sqlalchemy import *
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from typing import List

from .procore_user_settings import ProcoreUserSettings
from .user import User

class AccountManager(User):
    __tablename__ = 'account_managers'
    id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    subscribed = Column(Boolean())
    trial_start = Column(DateTime())
    payment_id = Column(String())
    project_id = Column(Integer())
    # collaborators = relationship('CollaboratorUser')
    procore_settings_id = Column(UUID(as_uuid=True), ForeignKey('procore_user_settings.id'))
    procore_data = relationship('ProcoreUserSettings', foreign_keys=[procore_settings_id])

    __mapper_args__ = {
        'polymorphic_identity': 'account_manager'
    }

    def __init__(self, procore_data=None, subscribed=False, trial_start=None, 
        payment_id='', project_id=None, collaborators=[], **kwargs):
        
        super().__init__(**kwargs)
        self.procore_data = procore_data or ProcoreUserSettings()
        self.procore_settings_id = self.procore_data.id
        self.subscribed = subscribed
        self.trial_start = trial_start or \
            (not subscribed and not self.temporary and datetime.now()) or None
        self.payment_id = payment_id
        self.project_id = project_id
        self.collaborators = collaborators
