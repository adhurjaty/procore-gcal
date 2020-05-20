from .model import Model

class User(Model):
    email: str = ''
    full_name: str = ''