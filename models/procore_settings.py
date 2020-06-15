from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import *

from .base import Base, id_col


class ProcoreSettings(Base):
    __tablename__ = "procore_settings"
    id = id_col()
    name = Column(String)
    enabled = Column(Boolean)
    type = Column(String)

    __mapper_args__ = {
        'polymorphic_on': type
    }

    def __init__(self, name='', enabled=False):
        self.name = name
        self.enabled = enabled

    def to_json(self):
        return {
            'name': self.name,
            'enabled': self.enabled
        }
    