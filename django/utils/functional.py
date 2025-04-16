from typing import Any, TypeVar, Callable, overload

T = TypeVar('T')
U = TypeVar('U')

def ensure_is(expected_type: type[T], value: Any, error_message = '') -> T:
    if not isinstance(value, expected_type):
        raise TypeError(error_message or f'Expected {value} to be of type {expected_type}, got {type(value)}')
    return value

@overload
def given(value: T | None, func: Callable[[T], U], default: U | Callable[[], U]) -> U:
    '''
    Returns the result of `func(value)` if `value` is truthy, otherwise returns the result of `default()` if `default` is a callable, or `default` itself if it is not.
    '''
    ...

@overload
def given(value: T | None, func: Callable[[T], U]) -> U | None:
    '''
    Returns the result of `func(value)` if `value` is truthy, otherwise returns `None`.
    '''
    ...

def given(
    value: T | None,
    func: Callable[[T], U],
    default: U | Callable[[], U] | None = None
):
    return func(value) if value else default() if callable(default) else default

Returns = Callable[[], T]

Inferable = T | Returns[T]

def infer(inferable: Inferable[T]) -> T:
    return (
        inferable()
        if callable(inferable)
        else inferable
    )
