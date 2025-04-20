from types import UnionType
from typing import TypeVar, get_args

def literal_values(LiteralType: UnionType) -> list[str]:
    return list(get_args(LiteralType))

TType = TypeVar('TType')

def none(type: type[TType]) -> TType | None:
    return None