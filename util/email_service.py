import yagmail
import logging
import os

from .utils import get_config, secrets_dir


config = get_config()
logger = logging.getLogger('fallback')


class EmailService:
    class __EmailService:
        yag = None

        def __init__(self):
            pass
            # try:
            #     self.yag = yagmail.SMTP(user=config.get('EMAIL_USERNAME'), 
            #         password='foo')
            #         # oauth2_file=os.path.join(secrets_dir, 'Procore-gcal-811fa2f8f4da.json'))
            # except:
            #     pass

        def send_email(self, to=[], subject='', contents=''):
            try:
                self.yag.send(to=to, subject=subject, contents=contents)
            except:
                logger.error('Email failed to send')

    instance = None
    def __init__(self):
        if not EmailService.instance:
            EmailService.instance = EmailService.__EmailService()
            if not EmailService.instance:
                raise Exception('could not instantiate email service')

    def __getattr__(self, name):
        return getattr(self.instance, name)

