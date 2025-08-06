from datetime import date, timedelta

import pytest
from django.utils import timezone
from rest_framework.exceptions import AuthenticationFailed

from hope_api_auth.auth import LoggingTokenAuthentication, INVALID_TOKEN, USER_INACTIVE_OR_DELETED
from hope_api_auth.models import APIToken

pytestmark = pytest.mark.django_db

NOW = timezone.now()
TODAY = NOW.date()
ONE_DAY = timedelta(days=1)
YESTERDAY = TODAY - ONE_DAY
BEFORE_YESTERDAY = YESTERDAY - ONE_DAY
TOMORROW = TODAY + ONE_DAY
AFTER_TOMORROW = TOMORROW + ONE_DAY


@pytest.fixture
def current_date() -> date:
    return date.today()


@pytest.mark.parametrize(
    ("valid_from", "valid_to"),
    [
        pytest.param(YESTERDAY, TOMORROW, id="valid_to set"),
        pytest.param(YESTERDAY, None, id="valid_to not set"),
    ],
)
def test_authenticate_credentials_success(
    api_token: APIToken,
    valid_from: date,
    valid_to: date | None,
) -> None:
    api_token.valid_from = valid_from
    api_token.valid_to = valid_to
    api_token.save()
    authentication = LoggingTokenAuthentication()

    user, token = authentication.authenticate_credentials(api_token.key)

    assert user == api_token.user
    assert token == api_token


@pytest.mark.parametrize(
    ("valid_from", "valid_to"),
    [
        pytest.param(BEFORE_YESTERDAY, YESTERDAY, id="expired"),
        pytest.param(TOMORROW, AFTER_TOMORROW, id="not active yet"),
        pytest.param(TOMORROW, None, id="not active yet with no valid_to"),
    ],
)
def test_authenticate_credentials_not_active_yet_or_already_expired(
    api_token: APIToken,
    valid_from: date,
    valid_to: date | None,
) -> None:
    api_token.valid_from = valid_from
    api_token.valid_to = valid_to
    api_token.save()
    authentication = LoggingTokenAuthentication()

    with pytest.raises(AuthenticationFailed, match=INVALID_TOKEN):
        authentication.authenticate_credentials(api_token.key)


def test_authenticate_credentials_inactive_user(api_token: APIToken) -> None:
    api_token.user.is_active = False
    api_token.user.save()
    authentication = LoggingTokenAuthentication()

    with pytest.raises(AuthenticationFailed, match=USER_INACTIVE_OR_DELETED):
        authentication.authenticate_credentials(api_token.key)
