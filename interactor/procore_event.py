import arrow
from datetime import datetime


class ProcoreEvent:
    number: str = ''
    title: str = ''
    description: str = ''
    link: str = ''
    location: str = ''
    due_date: datetime = None

    def update_from_dict(self, values):
        for key, val in ((k, v) for k, v in values.items() if hasattr(self, k)):
            if key == 'due_date':
                self.due_date = arrow.get(val).datetime.date()
                continue
            setattr(self, key, val)

