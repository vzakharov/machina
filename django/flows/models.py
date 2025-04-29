from asyncio import sleep
import inspect
from typing import ClassVar, Coroutine, Literal, NoReturn
from uuid import uuid4
from django.conf import settings
from django.db import models
from django.core.exceptions import ImproperlyConfigured
import json
import abc
from redis import asyncio as aioredis
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.db.models import GeneratedField, Case, When

from utils.typing import Readonly

class Tide(models.Model):
    """
    A tide is a single run of any outstanding tasks, as well as any tasks that are created while it is running. Only one tide can run at a time, hence the constraint.
    """

    HEARBEAT_INTERVAL: ClassVar[timedelta] = timedelta(seconds=4)
    HEARTBEAT_GRACE_PERIOD: ClassVar[timedelta] = timedelta(seconds=4)

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    last_alive_at = models.DateTimeField(auto_now_add=True)
    stuck = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['finished_at'],
                condition=models.Q(finished_at__isnull=True),
                name='unique_unfinished_tide'
            )
        ]

    @property
    def is_running(self):
        return not self.finished_at

    @classmethod
    def ensure(cls):
        """
        Gets the current tide, or creates a new one if there is no current tide or if the current tide got stuck. In the latter case, the current tide is marked as stuck and finished.
        """
        with transaction.atomic():
            tide, _ = cls.objects.select_for_update().get_or_create(finished_at__isnull=True)
            if tide.last_alive_at < timezone.now() - cls.HEARBEAT_INTERVAL - cls.HEARTBEAT_GRACE_PERIOD:
                tide.stuck = True
                tide.finished_at = timezone.now()
                tide.save()
                tide = cls.objects.create()
            return tide
        
    async def heartbeat(self):
        while self.is_running:
            await sleep(self.HEARBEAT_INTERVAL.total_seconds())
            self.last_alive_at = timezone.now()
            await self.asave()

class Task(models.Model):

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    no_auto_run = models.BooleanField(default=False)
    finished_at = models.DateTimeField(null=True, blank=True)
    is_running: models.Field[Readonly, bool] = models.GeneratedField(
        expression=~models.F('finished_at'),
        output_field=models.BooleanField(),
        db_persist=True
    )

    class Meta:
        # abstract = True

        indexes = [
            models.Index(
                name='task_is_running_idx',
                fields=['uuid'],
                condition=models.Q(is_running=True)
            )
        ]

    @property
    def redis_key(self):
        return f"task:{self.pk}"

    def get_redis_url(self):
        url = getattr(settings, "AWAITABLE_TASK_REDIS_URL", None)
        if not url:
            raise ImproperlyConfigured("AWAITABLE_TASK_REDIS_URL not set in settings.")
        return url

    async def run(self):
        """Explicitly trigger task execution."""
        # result = await self.handler()
        if inspect.iscoroutinefunction(self.handler):
            result = await self.handler()
        else:
            result = self.handler()
        await self._set_result(result)

    def __await__(self):
        return self._await_result().__await__()

    async def _set_result(self, result):
        redis = await aioredis.from_url(self.get_redis_url())
        await redis.set(f"{self.redis_key}:result", json.dumps(result))
        await redis.publish(f"{self.redis_key}:done", "ok")

    async def _await_result(self):
        redis = await aioredis.from_url(self.get_redis_url())
        pubsub = redis.pubsub()
        await pubsub.subscribe(f"{self.redis_key}:done")

        async for message in pubsub.listen():
            if message["type"] == "message":
                raw = await redis.get(f"{self.redis_key}:result")
                await pubsub.unsubscribe(f"{self.redis_key}:done")
                return json.loads(raw)

    @abc.abstractmethod
    def handler(self) -> None | Coroutine[None, None, None]:
        pass
