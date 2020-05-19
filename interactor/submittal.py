import arrow

from .ball_in_court_event import BallInCourtEvent


class Submittal(BallInCourtEvent):
    required_on_site_date = None
    submittal_type: str = ''

    def update_from_dict(self, values):
        super().update_from_dict(values)

        self.required_on_site_date = self.required_on_site_date and \
            arrow.get(self.required_on_site_date).datetime.date()

    def copy(self):
        dup = Submittal()
        dup.id = self.id
        dup.number = self.number
        dup.title = self.title
        dup.description = self.description
        dup.link = self.link
        dup.location = self.location
        dup.due_date = self.due_date
        dup.deleted = self.deleted
        dup.ball_in_court = self.ball_in_court
        dup.approver = self.approver
        dup.attachments = self.attachments
        dup.required_on_site_date = self.required_on_site_date
        dup.submittal_type = self.submittal_type
        return dup
