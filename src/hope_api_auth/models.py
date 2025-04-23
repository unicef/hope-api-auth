import swapper
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.authtoken.models import Token

from .fields import ChoiceArrayField


from django.conf import settings
from importlib import import_module
from functools import lru_cache


@lru_cache
def get_grant_class():
    module_path, class_name = settings.API_AUTH_GRANT_CLASS.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, class_name)


GrantClass = get_grant_class()


class AbstractAPIToken(Token):
    allowed_ips = models.CharField(_("IPs"), max_length=200, blank=True, null=True)
    valid_from = models.DateField(default=timezone.now)
    valid_to = models.DateField(blank=True, null=True)
    grants = ChoiceArrayField(models.CharField(max_length=255))

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"Token #{self.pk}"


class APIToken(AbstractAPIToken):
    class Meta:
        swappable = swapper.swappable_setting("hope_api_auth", "APIToken")


class APILogEntry(models.Model):
    token = models.ForeignKey(APIToken, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(default=timezone.now)
    url = models.URLField()
    method = models.CharField(max_length=10)
    status_code = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.token} {self.method} {self.timestamp}"
