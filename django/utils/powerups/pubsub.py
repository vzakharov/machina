from asyncio import gather
import json
from typing import Generic, TypeVar

from django.db import models

from utils.redis import ASYNC_REDIS
from utils.typing import Jsonable

TData = TypeVar("TData", bound=Jsonable)

class PubSubbed(models.Model, Generic[TData]):
    
    def redis_key(self) -> str:
        return f"{self._meta.app_label}.{self._meta.model_name}:{self.pk}"

    async def set_result(self, result: TData):
        await gather(
            ASYNC_REDIS.set(f"{self.redis_key}:result", json.dumps(result)),
            self.before_publish(result)
        )
        await ASYNC_REDIS.publish(f"{self.redis_key}:done", '')

    async def before_publish(self, result: TData):
        ...

    async def get_result(self):
        pubsub = ASYNC_REDIS.pubsub()
        channel = f"{self.redis_key}:done"
        await pubsub.subscribe(channel)
        async for message in pubsub.listen():
            if message["type"] == "message":
                ( raw_result, _ ) = await gather(
                    ASYNC_REDIS.get(f"{self.redis_key}:result"),
                    pubsub.unsubscribe(channel)
                )
                return json.loads(raw_result)
        raise RuntimeError(f"No message received on channel {channel}")
    
    def __await__(self):
        return self.get_result().__await__()