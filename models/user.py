from .model import Model

class User(Model):
    email: str = ''
    full_name: str = ''
    temporary: bool = True