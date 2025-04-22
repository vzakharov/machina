from types import UnionType
from typing import TYPE_CHECKING, Any, Callable, TypeGuard, TypeVar

from django.db.migrations.state import StateApps

from utils.typing import literal_values

from django.db import models


def choices_from_literals(LiteralType: UnionType) -> list[tuple[str, str]]:
    return [(choice, choice) for choice in literal_values(LiteralType)]

TModel = TypeVar('TModel', bound = type[models.Model])

def issubmodel(cls: type[models.Model], model: TModel) -> TypeGuard[TModel]:
    return issubclass(cls, model)


def define_custom_default_field(
    model_factory: Callable[[], TModel],
    default_factory: Callable[[TModel],
    float]
):

    class CustomDefaultField(models.FloatField[float] if TYPE_CHECKING else models.FloatField):

        def contribute_to_class(self, cls: type[models.Model], name: str, *args: Any, **kwargs: Any):
            meta = cls._meta
            if not meta.abstract and not isinstance(meta.apps, StateApps):
                Model = model_factory()
                if not issubmodel(cls, Model):
                    raise ValueError("Custom default field must be used on a subclass of {}".format(Model.__name__))
                self.default = default_factory(cls)
            super().contribute_to_class(cls, name, *args, **kwargs)

        def deconstruct(self, *args: Any, **kwargs: Any):
            name, path, args, kwargs = super().deconstruct(*args, **kwargs)
            kwargs['default'] = self.default
            path = 'django.db.models.FloatField'
            return name, path, args, kwargs

    return CustomDefaultField