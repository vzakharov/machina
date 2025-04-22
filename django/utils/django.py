from types import UnionType
from typing import Any, Callable, TypeGuard, TypeVar, cast

from django.db.migrations.state import StateApps

from utils.typing import literal_values
from utils.logging import debug
from django.db import models


def choices_from_literals(LiteralType: UnionType) -> list[tuple[str, str]]:
    return [(choice, choice) for choice in literal_values(LiteralType)]

TModel = TypeVar('TModel', bound = type[models.Model])

def issubmodel(cls: type[models.Model], model: TModel) -> TypeGuard[TModel]:
    return issubclass(cls, model)

TField = TypeVar('TField', bound = 'models.Field[Any, Any]')

SimpleFloatField = cast('type[models.FloatField[float]]', models.FloatField)

def DynamicField(
    FieldBaseClass: type[TField],
    model_factory: Callable[[], TModel],
    field_factory: Callable[[type[TField], TModel], TField]
):    
    class DynamicField(FieldBaseClass):

        @debug        
        def contribute_to_class(self, cls: type[models.Model], name: str, *args: Any, **kwargs: Any):
            meta = cls._meta
            if meta.abstract or isinstance(meta.apps, StateApps):
                return super().contribute_to_class(cls, name, *args, **kwargs)
            Model = model_factory()
            if not issubmodel(cls, Model):
                raise ValueError(f"Dynamic field must be used on a subclass of {Model.__name__}")
            field = field_factory(FieldBaseClass, cls)
            field.contribute_to_class(cls, name, *args, **kwargs)
    
    return cast(TField, DynamicField())