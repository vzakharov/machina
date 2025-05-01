import inspect
from typing import Any, Callable


def is_overriden(method: Callable[[], Any]) -> bool:
    if not inspect.ismethod(method):
        raise RuntimeError(f"{method=} is not a method")
    if not ( instance := method.__self__ ):
        raise RuntimeError(f"{method=} is not bound to an instance")
    
    return method.__func__.__name__ in instance.__class__.__dict__
