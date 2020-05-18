from datetime import datetime


class ProcoreEvent:
    number: str = ''
    title: str = ''
    description: str = ''
    link: str = ''
    location: str = ''
    due_date = None

    def update_from_dict(self, values):
        for key, val in ((k, v) for k, v in values.items() if hasattr(self, k)):
            setattr(self, key, val)
