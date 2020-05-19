import arrow

from .ball_in_court_event import BallInCourtEvent


class Submittal(BallInCourtEvent):
    required_on_site_date = None
    submittal_type: str = ''

    def update_from_dict(self, values):
        super().update_from_dict(values)

        self.required_on_site_date = self.required_on_site_date and \
            arrow.get(self.required_on_site_date).datetime.date()
