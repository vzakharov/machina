from types import UnionType

from utils.typing import literal_values


def choices_from_literals(LiteralType: UnionType) -> list[tuple[str, str]]:
    return [(choice, choice) for choice in literal_values(LiteralType)]
