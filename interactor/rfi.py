from typing import List

from .person import Person
from .procore_event import ProcoreEvent


class Rfi(ProcoreEvent):
    asignees: List[Person] = []
    rfi_manager: Person = None
    cost_impact: float = 0.0
    cost_code: str = ''
    questions: str = ''
    drawing_number: str = ''

    @property
    def subject(self):
        return self.title

    @property.setter
    def subject(self, value):
        self.title = value
    