import arrow
from datetime import datetime


class ProcoreEvent:
    id: int = -1
    number: str = ''
    title: str = ''
    description: str = ''
    link: str = ''
    location: str = ''
    due_date: datetime = None
    deleted: bool = False

    def update_from_dict(self, values):
        for key, val in ((k, v) for k, v in values.items() if hasattr(self, k)):
            if key == 'due_date' and val:
                self.due_date = arrow.get(val).datetime.date()
                continue
            setattr(self, key, val)

        self.location = self.location and self.location.get('node_name')

