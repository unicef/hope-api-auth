from functools import lru_cache
from typing import Any

import swapper
from django.db.models import Model, Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request


INVALID_TOKEN = "Invalid token."  # noqa: S105
USER_INACTIVE_OR_DELETED = "User inactive or deleted."


@lru_cache
def get_api_token_model() -> type[Model]:
    return swapper.load_model("hope_api_auth", "APIToken")


class LoggingTokenAuthentication(TokenAuthentication):
    keyword = "Token"

    def authenticate_credentials(self, key: str) -> tuple[Any, Model]:
        token_model = get_api_token_model()

        try:
            token = (
                token_model.objects.select_related("user")
                .filter(valid_from__lte=timezone.now())
                .filter(Q(valid_to__gte=timezone.now()) | Q(valid_to__isnull=True))
                .get(key=key)
            )
        except token_model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_(INVALID_TOKEN)) from None

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_(USER_INACTIVE_OR_DELETED))

        return token.user, token


class GrantedPermission(IsAuthenticated):
    def has_permission(self, request: Request, view: Any) -> bool:
        if bool(request.auth):
            if view.permission == "any":
                return True
            if request.user and request.user.is_authenticated and request.user.is_superuser:
                return True
            if view.permission:
                return view.permission.name in request.auth.grants

        return False
