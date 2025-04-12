from abc import ABC
from dataclasses import dataclass
from typing import ClassVar, Literal

from utils.errors import throw
from .tracks_descendants import TracksDescendants

@dataclass
class Trigger:
    timing: Literal['before', 'after']
    event: Literal['save', 'delete']
    func: str

class Triggerable(TracksDescendants, ABC):

    triggers: ClassVar[list[Trigger] | None] = None

    @classmethod
    def get_triggers(cls) -> list[Trigger]:
        return cls.triggers or throw(
            NotImplementedError(
                f"{cls.__name__} must either define class variable 'triggers' "
                f"or override the classmethod 'get_triggers'."
            )
        )