import inspect
from types import UnionType
from typing import Any, Callable, Coroutine, Generic, Literal, Protocol, TypeGuard, TypeVar, get_args

from utils.errors import ShouldNotHappenError



def literal_values(LiteralType: UnionType) -> list[str]:
    return list(get_args(LiteralType))

TType = TypeVar('TType')

def none(type: type[TType]) -> TType | None:
    return None

TClass = TypeVar('TClass', bound=type, contravariant=True)

class ClassMethod(Protocol, Generic[TClass]):
    def __call__(self, cls: TClass, **kwargs: Any) -> None: ...

Readonly = Literal['THIS IS A READONLY FIELD']

JsonableObject = dict[str, 'Jsonable']
Jsonable = str | int | float | bool | None | JsonableObject | list['Jsonable']

TJsonable = TypeVar('TJsonable', bound=Jsonable)

MaybeAsyncFunction = Callable[[], TJsonable | Coroutine[Any, Any, TJsonable]]

def is_async_function(
    func: MaybeAsyncFunction[TJsonable]
) -> TypeGuard[Callable[[], Coroutine[Any, Any, TJsonable]]]:
    return inspect.iscoroutinefunction(func)

def is_sync_function(
    func: MaybeAsyncFunction[TJsonable]
) -> TypeGuard[Callable[[], TJsonable]]:
    return not is_async_function(func)

async def run_as_async(
    func: MaybeAsyncFunction[TJsonable]
):
    if is_async_function(func):
        result = await func()
    elif is_sync_function(func):
        result = func()
    else:
        raise ShouldNotHappenError(f"{func} is neither async nor sync")
    return result