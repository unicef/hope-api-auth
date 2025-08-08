import sys
from pathlib import Path

import pytest
import os

from pytest_factoryboy import register

from .factories import APITokenFactory, UserFactory, SuperUserFactory, SuperUserAPITokenFactory


here = Path(__file__).parent
DEMOAPP_PATH = here / "demoapp"
sys.path.insert(0, str(here / "../src"))
sys.path.insert(0, str(DEMOAPP_PATH))


def pytest_configure(config):
    os.environ["DEBUG"] = "False"
    os.environ.update(DJANGO_SETTINGS_MODULE="demo.settings")

    import django

    django.setup()


@pytest.fixture
def app(django_app_factory):
    django_app = django_app_factory(csrf_checks=False)
    admin_user = SuperUserFactory(username="superuser")
    django_app.set_user(admin_user)
    django_app._user = admin_user
    return django_app


register(UserFactory)
register(SuperUserFactory)
register(APITokenFactory)
register(SuperUserAPITokenFactory, "superuser_api_token")
