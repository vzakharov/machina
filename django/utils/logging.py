from functools import wraps
import logging
from typing import Any, Callable, TypeVar, cast

logger = logging.getLogger(__name__)

# decorator for function
F = TypeVar('F', bound=Callable[..., Any])

def log(func: F) -> F:
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f'Logger: Calling {func.__name__} with args: {args}, kwargs: {kwargs}')
        result = func(*args, **kwargs)
        logger.debug(f'Logger: Result for {func.__name__}: {result}')
        return result
    return cast(F, wrapper)