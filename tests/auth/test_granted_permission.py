from unittest.mock import Mock

from hope_api_auth.auth import GrantedPermission


def test_has_permission_no_auth() -> None:
    request = Mock()
    request.auth = None
    permission_checker = GrantedPermission()

    assert not permission_checker.has_permission(request, Mock())


def test_has_permission_view_does_not_have_permission() -> None:
    request = Mock()
    request.user.is_authenticated = True
    request.user.is_superuser = False
    view = Mock()
    view.permission = None
    permission_checker = GrantedPermission()

    assert not permission_checker.has_permission(request, view)


def test_has_permission_view_permission_is_not_in_grants() -> None:
    request = Mock()
    request.user.is_authenticated = True
    request.user.is_superuser = False
    request.auth.grants = []
    view = Mock()
    view.permission.name = "not_in_grants"
    permission_checker = GrantedPermission()

    assert not permission_checker.has_permission(request, view)


def test_has_permission_view_permission_is_any() -> None:
    view = Mock()
    view.permission = "any"
    permission_checker = GrantedPermission()

    assert permission_checker.has_permission(Mock(), view) is True


def test_has_permission_view_user_is_authenticated_and_superuser() -> None:
    request = Mock()
    request.user.is_authenticated = True
    request.user.is_superuser = True
    permission_checker = GrantedPermission()

    assert permission_checker.has_permission(request, Mock()) is True


def test_has_permission_view_permission_in_auth_grants() -> None:
    request = Mock()
    request.user.is_superuser = False
    request.auth.grants = [grant0 := "grant0", "grant1"]
    view = Mock()
    view.permission.name = grant0
    permission_checker = GrantedPermission()

    assert permission_checker.has_permission(request, view) is True
