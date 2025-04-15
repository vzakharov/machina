from typing import Literal, TypeVar

T = TypeVar('T')
U = TypeVar('U')
Compactable = T | Literal[False, '', 0, None]

def compact(*items: Compactable[T]) -> list[T]:
    return [ item for item in items if item ]

def empty_list(type: type[T]) -> list[T]:
    return []

def empty_dict(key_type: type[T], value_type: type[U]) -> dict[T, U]:
    return {}

def empty_set(type: type[T]) -> set[T]:
    return set()