import util.utils as utils


def test_sign_verify_token():
    token = 'something'

    signed = utils.get_signed_token(token)
    assert utils.verify_token(token, signed)
    assert not utils.verify_token('token', signed)
