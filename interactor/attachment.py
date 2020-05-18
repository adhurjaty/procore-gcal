class Attachment:
    url: str = ''
    filename: str = ''

    def __init__(self, url='', filename='', **kwargs):
        self.url = url
        self.filename = filename
        