from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import *

from .base import Base, id_col
from .procore_settings import ProcoreSettings


class EmailSettings(ProcoreSettings):
    __tablename__ = 'email_settings'
    id = Column(UUID(as_uuid=True), ForeignKey=('procore_settings.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'email'
    }
