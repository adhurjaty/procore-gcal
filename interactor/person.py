class Person:
    full_name: str = ''
    email: str = ''

    def __init__(self, full_name='', email='', login='', name='', **kwargs):
        self.full_name = full_name or name
        self.email = email or login