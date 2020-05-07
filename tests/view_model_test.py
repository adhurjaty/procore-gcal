import pytest
import os
from pathlib import Path

from controller.gcal_view_model import GCalViewModel
from .mocks import OauthMock, MockObject, OauthResponseMock, ControllerMock

objects_path = os.path.join(Path(os.path.realpath(__file__)).parent, 'objects')


@pytest.fixture(scope='module')
def gcal_oauth_mock():
    mock = OauthMock()
    return mock


@pytest.fixture(scope='module')
def sample_user():
    pass


@pytest.fixture(scope='module')
def sample_procore_event():
    pass


def test_convert_event(sample_user, sample_procore_event):
    vm = GCalViewModel(sample_user, sample_procore_event)
    gcal_event = {}

    assert vm.event == gcal_event
