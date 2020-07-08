import base64
import logging
import os
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from email.mime.text import MIMEText

from .utils import get_config, secrets_dir


config = get_config()
logger = logging.getLogger('fallback')


class EmailService:
    class __EmailService:
        service = None
        from_addr = ''

        def __init__(self):
            self.from_addr = config.get('EMAIL_FROM')
            self.service = self._service_account_login()

        def _service_account_login(self):
            SCOPES = ['https://www.googleapis.com/auth/gmail.send']
            SERVICE_ACCOUNT_FILE = os.path.join(secrets_dir, 'service-key.json')

            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            delegated_credentials = credentials.create_delegated(self.from_addr)
            service = build('gmail', 'v1', credentials=delegated_credentials)
            return service

        def send_email(self, to=[], subject='', contents='', cc=[], bcc=[]):
            msg = MIMEText(contents)
            msg['from'] = self.from_addr
            msg['to'] = to
            msg['subject'] = subject
            msg['cc'] = ', '.join(cc)
            msg['bcc'] = ', '.join(bcc)
            try:
                message = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')}
                message_to_send = self.service.users().messages().send(
                    userId=self.from_addr, body=message).execute()
            except Exception as e:
                logger.error('Email failed to send')

    instance = None
    def __init__(self):
        if not EmailService.instance:
            EmailService.instance = EmailService.__EmailService()

    def __getattr__(self, name):
        return getattr(self.instance, name)

