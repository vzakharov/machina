from abc import ABC
from typing import ClassVar, Generic, TypeVar

TRegistrable = TypeVar("TRegistrable", bound="Registrable")

class Registrable(ABC, Generic[TRegistrable]):
    registry: ClassVar[set[TRegistrable]] = set()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.registry = set()

        for ancestor in cls.__mro__[1:]:
            if issubclass(ancestor, Registrable):
                ancestor.registry.add(cls)