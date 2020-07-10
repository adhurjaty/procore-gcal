from .mocks import MockObject
import util.utils as utils
import util.app_logger as al


def test_sign_verify_token():
    token = 'something'

    signed = utils.get_signed_token(token)
    assert utils.verify_token(token, signed)
    assert not utils.verify_token('token', signed)


def test_logger_correct_type():
    assert isinstance(al.get_logger(), al.AppLogger)


def test_logger_error_send_email():
    validations = MockObject()
    validations.contents = {}

    def send_email(contents):
        validations.contents = contents

    al.config = {
        'EMAIL_USERNAME': 'foo@example.com',
        'EMAIL_PASSWORD': 'LKASDJFLK'
    }

    logger = al.get_logger()
    logger.emailer = MockObject()
    logger.emailer.send_email = send_email
    
    logger.error('this error', stacktrace='my stack')
    
    assert validations.contents == {
        'to': 'foo@example.com',
        'subject': 'PROCORE CALENDAR APP ERROR',
        'contents': f'message: this error\nstack trace: my stack'
    }
