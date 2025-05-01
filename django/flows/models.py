import abc
import inspect
import json
from asyncio import sleep
from datetime import timedelta
from typing import ClassVar, Coroutine

from utils.django import IsNull
from utils.redis import ASYNC_REDIS
from utils.typing import Readonly

from django.db import models, transaction
from django.db.models.functions import Now
from django.utils import timezone


class Tasklike(models.Model):

    class Meta:
        abstract = True

    HEARBEAT_INTERVAL: ClassVar[timedelta] = timedelta(seconds=4)
    HEARTBEAT_GRACE_PERIOD: ClassVar[timedelta] = timedelta(seconds=4)

    started_at = models.DateTimeField(db_default=Now())
    finished_at = models.DateTimeField(null=True, blank=True)
    last_alive_at = models.DateTimeField(db_default=Now())
    stuck = models.BooleanField(db_default=False, db_index=True)

    is_running: 'models.Field[Readonly, bool]' = models.GeneratedField(
        expression=IsNull('finished_at'),
        output_field=models.BooleanField(),
        db_persist=True,
        db_index=True,
    )

    async def heartbeat(self):
        while self.is_running:
            await sleep(self.HEARBEAT_INTERVAL.total_seconds())
            self.last_alive_at = timezone.now()
            await self.asave(update_fields=['last_alive_at'])


class Tide(Tasklike):
    """
    A tide is a single run of any outstanding tasks, as well as any tasks that are created while it is running. Only one tide can run at a time, hence the constraint.
    """

    class Meta(Tasklike.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['is_running'],
                condition=models.Q(is_running=True),
                name='unique_running_tide'
            )
        ]

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


class Task(Tasklike):

    autorun = models.BooleanField(default=True)

    class Meta(Tasklike.Meta):

        abstract = True
        indexes = [
            models.Index(
                name='task_is_running_idx',
                fields=['uuid'],
                condition=models.Q(is_running=True)
            )
        ]

    @property
    def redis_key(self):
        return f"flows:{self._meta.app_label}.{self._meta.model_name}:{self.pk}"

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
        await ASYNC_REDIS.set(f"{self.redis_key}:result", json.dumps(result))
        await ASYNC_REDIS.publish(f"{self.redis_key}:done", "ok")

    async def _await_result(self):
        pubsub = ASYNC_REDIS.pubsub()
        await pubsub.subscribe(f"{self.redis_key}:done")

        async for message in pubsub.listen():
            if message["type"] == "message":
                raw = await ASYNC_REDIS.get(f"{self.redis_key}:result")
                await pubsub.unsubscribe(f"{self.redis_key}:done")
                return json.loads(raw)

    @abc.abstractmethod
    def handler(self) -> None | Coroutine[None, None, None]:
        pass
