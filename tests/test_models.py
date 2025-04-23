import pytest
from tests.factories.auth import APITokenFactory


@pytest.mark.django_db
def test_user():
    token = APITokenFactory()
    assert str(token).startswith("Token")
