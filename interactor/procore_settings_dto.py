from .dto_base import DtoBase
from models.procore_user_settings import ProcoreUserSettings
from models.email_settings import EmailSettings
from models.event_settings import EventSettings


class ProcoreSettingsDto(DtoBase):
    def __init__(self, parent: ProcoreUserSettings):
        super().__init__(parent)

    @property
    def email_settings(self):
        return self._settings_to_dict(self.parent.email_settings or {})

    def _settings_to_dict(self, settings):
        return {s.name[0]: s.enabled for s in settings}

    @email_settings.setter
    def email_settings(self, values):
        self.parent.email_settings = [EmailSettings(**v) for v in values]

    @property
    def calendar_event_types(self):
        return self._settings_to_dict(self.parent.calendar_event_types or {})

    @calendar_event_types.setter
    def calendar_event_types(self, values):
        self.parent.calendar_event_types = [EventSettings(**v) for v in values]
