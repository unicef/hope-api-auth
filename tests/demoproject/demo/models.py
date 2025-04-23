from django.contrib.auth.models import AbstractUser
from enum import Enum, auto, unique
from typing import Any


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        app_label = "demo"


@unique
class Grant(Enum):
    def _generate_next_value_(self, start: int, count: int, last_values: list[Any]) -> Any:
        return self

    API_READ_ONLY = auto()
    API_PLAN_UPLOAD = auto()
    API_PLAN_MANAGE = auto()

    @classmethod
    def choices(cls):
        return tuple((member.value, member.name.replace("_", " ").title()) for member in cls)
