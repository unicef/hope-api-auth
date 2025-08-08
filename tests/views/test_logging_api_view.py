from collections.abc import Callable
from unittest.mock import Mock, patch

import pytest
from django.core.handlers.wsgi import WSGIRequest
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate

from hope_api_auth.models import APILogEntry, APIToken, GrantClass
from hope_api_auth.views import LoggingAPIView

ALL_HTTP_METHODS = "GET", "POST", "PUT", "DELETE"
NOT_LOGGED_HTTP_METHODS = tuple(set(ALL_HTTP_METHODS) - set(LoggingAPIView.log_http_methods))

LOGGED_STATUSES = status.HTTP_200_OK, status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR
NOT_LOGGED_STATUSES = status.HTTP_301_MOVED_PERMANENTLY, status.HTTP_302_FOUND

TEST_PATH = "/api/test/"


@pytest.fixture
def http_method_name(request) -> str:
    if hasattr(request, "param"):
        return request.param
    return "POST"


@pytest.fixture
def http_status_code(request) -> int:
    if hasattr(request, "param"):
        return request.param
    return status.HTTP_200_OK


@pytest.fixture
def http_request(http_method_name: str, superuser_api_token: APIToken) -> WSGIRequest:
    factory = APIRequestFactory()
    request = getattr(factory, http_method_name.lower())(TEST_PATH)
    force_authenticate(request, token=superuser_api_token, user=superuser_api_token.user)
    return request


@pytest.fixture
def http_method_handler_mock(http_status_code: int) -> Mock:
    return Mock(return_value=Response(status=http_status_code))


@pytest.fixture
def test_view(http_method_handler_mock: Mock) -> Callable:
    class TestView(LoggingAPIView):
        def __getattr__(self, item) -> Callable:
            if item.upper() in ALL_HTTP_METHODS:
                return http_method_handler_mock
            raise AttributeError

    return TestView.as_view()


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("http_status_code", LOGGED_STATUSES, indirect=True)
@pytest.mark.parametrize("http_method_name", LoggingAPIView.log_http_methods, indirect=True)
def test_dispatch_methods_logged(
    http_request: WSGIRequest,
    test_view: Callable,
    superuser_api_token: APIToken,
    http_status_code: int,
    http_method_name: str,
) -> None:
    test_view(http_request)

    log_entry = APILogEntry.objects.first()
    assert log_entry.token == superuser_api_token
    assert log_entry.method == http_method_name
    assert log_entry.status_code == http_status_code
    assert log_entry.url == TEST_PATH


@pytest.mark.parametrize("http_status_code", LOGGED_STATUSES, indirect=True)
@pytest.mark.parametrize("http_method_name", NOT_LOGGED_HTTP_METHODS, indirect=True)
def test_dispatch_methods_not_logged_methods(http_request: WSGIRequest, test_view: Callable) -> None:
    test_view(http_request)

    assert not APILogEntry.objects.first()


@pytest.mark.parametrize("http_status_code", NOT_LOGGED_STATUSES, indirect=True)
@pytest.mark.parametrize("http_method_name", LoggingAPIView.log_http_methods, indirect=True)
def test_dispatch_methods_not_logged_statuses(http_request: WSGIRequest, test_view: Callable) -> None:
    test_view(http_request)

    assert not APILogEntry.objects.first()


@pytest.mark.parametrize(
    ("permission", "expected_error_message"),
    [
        (perm := GrantClass.API_READ_ONLY, f"{PermissionDenied.default_detail} {perm.name}"),
        (None, f"{PermissionDenied.default_detail} "),
    ],
)
@patch("hope_api_auth.views.super")
def test_handle_exception_permission_denied(
    super_mock: Mock, permission: GrantClass | None, expected_error_message: str
) -> None:
    view = LoggingAPIView()
    view.permission = permission

    view.handle_exception(PermissionDenied())

    super_handle_exception_mock = super_mock.return_value.handle_exception
    super_handle_exception_mock.assert_called_once()

    exception = super_handle_exception_mock.call_args.args[0]
    assert exception.detail == expected_error_message
    assert exception.status_code == status.HTTP_403_FORBIDDEN


@patch("hope_api_auth.views.super")
def test_handle_exception_not_permission_denied(super_mock: Mock) -> None:
    LoggingAPIView().handle_exception(exception := Exception())

    super_handle_exception_mock = super_mock.return_value.handle_exception
    super_handle_exception_mock.assert_called_once()
    exception_arg = super_handle_exception_mock.call_args.args[0]
    assert exception_arg is exception
