import importlib
import pkgutil
from pathlib import Path

from pytest_factoryboy import register

from factory.django import DjangoModelFactory

from .base import (
    AutoRegisterModelFactory,
    factories_registry,
    TAutoRegisterModelFactory,
)
from .user import GroupFactory, SuperUserFactory, UserFactory  # noqa

for _, name, _ in pkgutil.iter_modules([str(Path(__file__).parent)]):
    importlib.import_module(f".{name}", __package__)


django_model_factories = {factory._meta.model: factory for factory in DjangoModelFactory.__subclasses__()}


def get_factory_for_model(
    _model,
) -> type[TAutoRegisterModelFactory] | type[DjangoModelFactory]:
    class Meta:
        model = _model

    bases = (AutoRegisterModelFactory,)
    if _model in factories_registry:
        return factories_registry[_model]  # noqa

    if _model in django_model_factories:
        return django_model_factories[_model]

    return register(type(f"{_model._meta.model_name}AutoCreatedFactory", bases, {"Meta": Meta}))  # noqa
