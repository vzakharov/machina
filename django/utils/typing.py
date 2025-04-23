from types import UnionType
from typing import Any, Generic, Protocol, TypeVar, get_args


def literal_values(LiteralType: UnionType) -> list[str]:
    return list(get_args(LiteralType))

TType = TypeVar('TType')

def none(type: type[TType]) -> TType | None:
    return None

TClass = TypeVar('TClass', bound=type, contravariant=True)

class ClassMethod(Protocol, Generic[TClass]):
    def __call__(self, cls: TClass, **kwargs: Any) -> None: ...