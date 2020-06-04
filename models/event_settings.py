from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import *

from .base import Base, id_col
from .procore_settings import ProcoreSettings


class EventSettings(ProcoreSettings):
    __tablename__ = 'event_settings'
    id = Column(UUID(as_uuid=True), ForeignKey=('procore_settings.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'event'
    }