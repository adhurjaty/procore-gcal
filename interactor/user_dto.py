from .dto_base import DtoBase
from .person import Person
from models.collaborator_user import CollaboratorUser

class UserDto(DtoBase):
    parent: CollaboratorUser = None

    def __init__(self, parent):
        super().__init__(parent)

    def set_gcal_token(self, token: dict):
        self.gcal_data.set_token(**token)
