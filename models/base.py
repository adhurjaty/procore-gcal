from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column
from uuid import uuid4

Base = declarative_base()

def id_col():
    return Column(UUID(as_uuid=True), primary_key=True, default=uuid4, 
        unique=True, nullable=False)
