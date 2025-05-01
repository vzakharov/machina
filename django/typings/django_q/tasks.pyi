from typing import Any, Callable, Literal, TypeVar, TypedDict, Unpack, overload

class AsyncTaskKwargs(TypedDict, total=False):
    task_name: str | None
    broker: str | None
    cluster: str | None
    cached: bool

TCallable = TypeVar('TCallable', bound=Callable[..., Any])

@overload
def async_task(func: TCallable, *args: Any, sync: Literal[True], **kwargs: Unpack[AsyncTaskKwargs]) -> TCallable: ...

@overload
def async_task(func: Callable[..., Any], *args: Any, **kwargs: Unpack[AsyncTaskKwargs]) -> str: ...

@overload
def async_task(func: TCallable, *args: Any, sync: bool, **kwargs: Unpack[AsyncTaskKwargs]) -> TCallable | str: ...