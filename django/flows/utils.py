from utils.errors import ShouldNotHappenError
from utils.typing import MaybeAsyncFunction, aint_async_function, is_async_function


async def call_as_async(
    func: MaybeAsyncFunction[TJsonable]
):
    if is_async_function(func):
        result = await func()
    elif aint_async_function(func):
        result = func()
    else:
        raise ShouldNotHappenError(f"{func} is neither async nor sync")
    return result