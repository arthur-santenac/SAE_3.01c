import pytest
from monApp.app import app

@pytest.fixture
def testapp():
    app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False
    })

    yield app

@pytest.fixture
def client(testapp):
    return testapp.test_client()