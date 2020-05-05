import pytest

import controller.request_handler as rh

@pytest.fixture(scope='module')
def test_client():
    app = rh.app

    testing_client = app.test_client()

    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


def test_hello_world(test_client):
    response = test_client.get('/')
    
    assert response.status_code == 200
    assert response.data == 'Hello world!'
