from typing import NoReturn

class BadRequestError(Exception):
    pass

class UnderConstructionError(NotImplementedError):
    pass

class ShouldNotHappenError(Exception):
    """
    This exception should never be raised.
    If it is, it means that there is a bug in the code.
    """
    def __init__(self, message: str):
        super().__init__(message + " (This should never happen)")

def throw(exception: Exception | str) -> NoReturn:
    raise (
        exception
        if isinstance(exception, Exception)
        else BadRequestError(exception)
    )