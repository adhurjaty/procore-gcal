import logging

from .utils import get_config
from .email_service import EmailService


config = get_config()


class AppLogger():
    logger = None
    emailer = None

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.emailer = EmailService()

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def error(self, msg, *args, stacktrace='', **kwargs):
        self.logger.error(msg, *args, **kwargs)
        self.emailer.send_email(self._error_email(msg, stacktrace))

    def _error_email(self, msg: str, stacktrace: str) -> dict:
        return {
            'to': config.get('EMAIL_USERNAME'),
            'subject': 'PROCORE CALENDAR APP ERROR',
            'contents': f'message: {msg}\nstack trace: {stacktrace}'
        }


__logger = None

def get_logger():
    global __logger

    if __logger is None:
        __logger = AppLogger()
    return __logger