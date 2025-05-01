import json
from asyncio import gather
from typing import Generic, TypeVar, cast

from asgiref.sync import async_to_sync
from utils.redis import ASYNC_REDIS, REDIS
from utils.typing import Jsonable, none
from redis.asyncio.client import PubSub

from django.db import models

TData = TypeVar("TData", bound=Jsonable)

class PubSubbed(models.Model, Generic[TData]):

    pubsub = none(PubSub)

    def redis_key(self) -> str:
        return f"{self._meta.app_label}.{self._meta.model_name}:{self.pk}"
    
    @property
    def redis_result_key(self) -> str:
        return f"{self.redis_key}:result"
    
    @property
    def redis_done_channel(self) -> str:
        return f"{self.redis_key}:done"
    
    async def set_result(self, result: TData):
        await gather(
            ASYNC_REDIS.set(f"{self.redis_key}:result", json.dumps(result)),
            self.before_publish(result)
        )
        await ASYNC_REDIS.publish(self.redis_done_channel, 'ok')
        return result

    async def before_publish(self, result: TData):
        ...

    async def subscribe(self):
        self.pubsub = ASYNC_REDIS.pubsub()
        await self.pubsub.subscribe(self.redis_done_channel)
        return self.pubsub

    async def wait_for_result(self):
        
        async def get_raw_result():
            pubsub = self.pubsub or await self.subscribe()
            async for message in pubsub.listen():
                if message["type"] == "message":
                    ( raw_result, _ ) = await gather(
                        ASYNC_REDIS.get(self.redis_result_key),
                        pubsub.unsubscribe(self.redis_done_channel)
                    )
                    return raw_result
            raise RuntimeError(f"No message received on channel {self.redis_done_channel}")
        
        return json.loads(
            await ASYNC_REDIS.get(self.redis_result_key)
            or await get_raw_result()
        )
        
    
    @property
    def result(self):
        result = REDIS.get(self.redis_result_key)
        if result is None:
            raise RuntimeError(f"No result for {self.redis_key} yet. Consider awaiting the instance instead.")
        if not isinstance(result, str):
            raise RuntimeError(f"Result for {self.redis_key} is not a string")
        return cast(TData, json.loads(result))
    
    @result.setter
    def result(self, value: TData):
        async_to_sync(self.set_result)(value)

    def __await__(self):
        return self.wait_for_result().__await__()