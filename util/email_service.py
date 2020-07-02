import yagmail
import logging

from .utils import get_config


config = get_config()
logger = logging.getLogger('fallback')


class EmailService:
    class __EmailService:
        yag = None

        def __init__(self):
            pass
            # self.yag = yagmail.SMTP(config.get('EMAIL_USERNAME'), 
            #         oauth2_file='')

        def send_email(self, to=[], subject='', contents=''):
            try:
                self.yag.send(to=to, subject=subject, contents=contents)
            except:
                logger.error('Email failed to send')

    instance = None
    def __init__(self):
        if not EmailService.instance:
            EmailService.instance = EmailService.__EmailService()

    def __getattr__(self, name):
        return getattr(self.instance, name)

