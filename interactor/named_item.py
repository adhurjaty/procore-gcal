class NamedItem():
    id = None
    name: str = ''

    def __init__(self, id='', name=''):
        self.id = id
        self.name = name

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }