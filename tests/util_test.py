import json
import os
import pytest
from pathlib import Path

import util.utils as utils

objects_path = os.path.join(Path(os.path.realpath(__file__)).parent, 'objects')


def load_json(filename):
    path = os.path.join(objects_path, filename)
    with open(path, 'r') as f:
        return json.load(f)


def test_sign_verify_token():
    token = 'something'

    signed = utils.get_signed_token(token)
    assert utils.verify_token(token, signed)
    assert not utils.verify_token('token', signed)
