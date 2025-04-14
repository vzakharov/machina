from typing import ClassVar, TypeVar, cast

TTracksDescendants = TypeVar("TTracksDescendants", bound="TracksDescendants")

class TracksDescendants():
    _descendant_classes: ClassVar[set[type['TracksDescendants']]] = set()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls._descendant_classes = set()

        for ancestor in cls.__mro__[1:]:
            if issubclass(ancestor, TracksDescendants):
                ancestor._descendant_classes.add(cls)

    @classmethod
    def get_descendant_classes(cls: type[TTracksDescendants]):
        return cast(set[type[TTracksDescendants]], cls._descendant_classes)