from typing import Literal, TypeVar

T = TypeVar('T')

def compact(*items: T | Literal[False] | Literal[''] |None) -> list[T]:
    return [ item for item in items if item ]