from types import UnionType
from typing import get_args


def literal_values(LiteralType: UnionType) -> list[str]:
    return list(get_args(LiteralType))