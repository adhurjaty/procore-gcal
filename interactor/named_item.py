class NamedItem():
    id = None
    name: str = ''

    def to_json(self):
        return {
            'id': self.id,
            'name': self.name
        }