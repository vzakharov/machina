from functools import wraps
import logging
from typing import Any, Callable, TypeVar, cast, overload

logger = logging.getLogger(__name__)

TFunction = TypeVar('TFunction', bound=Callable[..., Any])

def possibly_decorator(applier: Callable[[str], None], prefix: str):

    @overload
    def apply(string_or_function: TFunction) -> TFunction:
        ...

    @overload
    def apply(string_or_function: str) -> None:
        ...

    def apply(string_or_function: str | TFunction) -> TFunction | None:
        if callable(string_or_function):
            func = string_or_function
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any):
                applier(f'{prefix}: Calling {func=} with {args=} & {kwargs=}')
                result = func(*args, **kwargs)
                applier(f'{prefix}: Result for {func=} is {result=}')
                return result
            return cast(TFunction, wrapper)
        return applier(string_or_function)
    return apply

info = possibly_decorator(logger.info, 'INFO')
debug = possibly_decorator(logger.debug, 'DEBUG')
warning = possibly_decorator(logger.warning, 'WARNING')
error = possibly_decorator(logger.error, 'ERROR')
critical = possibly_decorator(logger.critical, 'CRITICAL')
