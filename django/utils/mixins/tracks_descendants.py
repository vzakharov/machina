from abc import ABC
from typing import ClassVar, Generic, TypeVar

TTracksDescendants = TypeVar("TTracksDescendants", bound="TracksDescendants")

class TracksDescendants(ABC, Generic[TTracksDescendants]):
    descendant_classes: ClassVar[set[TTracksDescendants]] = set()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.descendant_classes = set()

        for ancestor in cls.__mro__[1:]:
            if issubclass(ancestor, TracksDescendants):
                ancestor.descendant_classes.add(cls)