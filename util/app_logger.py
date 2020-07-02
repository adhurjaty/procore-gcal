import logging

from .utils import get_config
from .email_service import EmailService


config = get_config()


class AppLogger(logging.Logger):
    emailer = EmailService()

    def error(self, msg, *args, stacktrace='', **kwargs):
        super().error(msg, *args, **kwargs)
        self.emailer.send_email(self._error_email(msg, stacktrace))

    def _error_email(self, msg: str, stacktrace: str) -> dict:
        return {
            'to': config.get('EMAIL_USERNAME'),
            'subject': 'PROCORE CALENDAR APP ERROR',
            'contents': f'message: {msg}\nstack trace: {stacktrace}'
        }


logging.setLoggerClass(AppLogger)
logging.basicConfig()

logger = logging.getLogger(__name__)