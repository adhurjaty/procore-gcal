
from sqlalchemy import *
from uuid import uuid4

from .base import Base, id_col

class User(Base):
    __tablename__ = 'users'
    id = id_col()
    email = Column(String)
    full_name = Column(String)
    temporary = Column(Boolean)
    type = Column(String)

    __mapper_args__ = {
        'polymorphic_on': type
    }

    def __init__(self, id=None, email='', full_name='', temporary=True, **kwargs):
        self.id = id or uuid4()
        self.email = email
        self.full_name = full_name
        self.temporary = temporary
        self.user_type = user_type

    
