from sqlalchemy import *
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .user import User
from .gcal_user_settings import GCalUserSettings

class CollaboratorUser(User):
    __tablename__ = 'collaborators'
    id = Column(UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey('account_managers.id'))
    manager = relationship("AccountManager", backref='collaborators', 
        foreign_keys=[manager_id])

    # manager = relationship("AccountManager", back_populates='collaborators', 
    #     foreign_keys=[manager_id])

    __mapper_args__ = {
        'polymorphic_identity': 'collaborator'
    }

    def __init__(self, manager=None, **kwargs):
        super().__init__(**kwargs)
        self.manager = manager
        
