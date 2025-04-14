from typing import Literal, TypeVar

T = TypeVar('T')
U = TypeVar('U')
def compact(*items: T | Literal[False] | Literal[''] |None) -> list[T]:
    return [ item for item in items if item ]

def empty_list(type: type[T]) -> list[T]:
    return []

def empty_dict(key_type: type[T], value_type: type[U]) -> dict[T, U]:
    return {}

def empty_set(type: type[T]) -> set[T]:
    return set()