from .person import Person
from models.collaborator_user import CollaboratorUser

class UserDto(object):
    parent: CollaboratorUser = None

    def __init__(self, parent):
        self.parent = parent

    def set_gcal_token(self, token: dict):
        self.gcal_data.set_token(**token)

    def __getattr__(self, name):
        try:
            return getattr(self.parent, name)
        except AttributeError as e:
            raise AttributeError(f'{self.parent.__class__} has no attribute {name}')

    def __setattr__(self, name, value):
        if self.parent and hasattr(self.parent, name):
            setattr(self.parent, name, value)
        else:
            super().__setattr__(name, value)
