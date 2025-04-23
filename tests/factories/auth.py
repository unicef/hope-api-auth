import random
import secrets

from demo.models import Grant
from hope_api_auth.models import APILogEntry, APIToken
from tests.factories import AutoRegisterModelFactory, UserFactory

import factory.fuzzy


def unique_token_key():
    from hope_api_auth.models import APIToken

    while True:
        key = secrets.token_hex(20)
        if not APIToken.objects.filter(key=key).exists():
            return key


class APITokenFactory(AutoRegisterModelFactory):
    key = factory.LazyFunction(unique_token_key)
    user = factory.SubFactory(UserFactory)
    grants = factory.LazyFunction(lambda: [str(g.value) for g in random.sample(list(Grant), k=random.randint(1, 3))])

    class Meta:
        model = APIToken
        django_get_or_create = ("key",)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = kwargs.get("user")
        if user and model_class.objects.filter(user=user).exists():
            return model_class.objects.get(user=user)
        return super()._create(model_class, *args, **kwargs)


class APILogEntryFactory(AutoRegisterModelFactory):
    status_code = factory.fuzzy.FuzzyInteger(low=200, high=599)
    token = factory.SubFactory(APITokenFactory)

    class Meta:
        model = APILogEntry
