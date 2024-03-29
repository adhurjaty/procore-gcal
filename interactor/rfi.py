from typing import List

from .person import Person
from .procore_event import ProcoreEvent


class Rfi(ProcoreEvent):
    assignees: List[Person] = []
    rfi_manager: Person = None
    schedule_impact: int = 0
    cost_impact: float = 0.0
    cost_code: str = ''
    questions: str = ''
    drawing_number: str = ''

    @property
    def subject(self):
        return self.title

    @subject.setter
    def subject(self, value):
        self.title = value

    def update_from_dict(self, values):
        super().update_from_dict(values)
        
        self.assignees = self.assignees and [Person(**a) for a in self.assignees]
        self.rfi_manager = self.rfi_manager and Person(**self.rfi_manager)
        self.schedule_impact = self.schedule_impact and int(self.schedule_impact.get('value') or 0)
        self.cost_impact = self.cost_impact and float(self.cost_impact.get('value') or 0)
        self.cost_code = self.cost_code and self.cost_code.get('name')
        self.questions = self.questions and '\n'.join(q.get('plain_text_body') 
            for q in self.questions)

        return self
    