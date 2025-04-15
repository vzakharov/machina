from typing import NoReturn

class BadRequestError(Exception):
    pass

class UnderConstructionError(NotImplementedError):
    pass

def throw(exception: Exception | str) -> NoReturn:
    raise (
        exception
        if isinstance(exception, Exception)
        else BadRequestError(exception)
    )