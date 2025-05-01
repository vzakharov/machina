import abc
import asyncio
from asyncio import create_task, sleep
from datetime import timedelta
from typing import ClassVar, TypeVar

from django_q.tasks import async_task
from utils.django import IsNull
from utils.powerups.pubsub import PubSubbed
from utils.powerups.typed import Typed
from utils.typing import (Jsonable, Readonly, is_async_function,
                          is_sync_function, none)

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
    succeeded = models.BooleanField(db_default=False, db_index=True, null=True)
    
    is_running: 'models.Field[Readonly, bool]' = models.GeneratedField( # pyright: ignore[reportAttributeAccessIssue]
        expression=IsNull('finished_at'),
        output_field=models.BooleanField(),
        db_persist=True,
        db_index=True,
    )

    heartbeat_task = none(asyncio.Task[None])

    async def heartbeat(self):
        while self.is_running:
            await sleep(self.HEARBEAT_INTERVAL.total_seconds())
            self.last_alive_at = timezone.now()
            await self.asave(update_fields=['last_alive_at'])
    
    def start_heartbeat(self):
        if not self.heartbeat_task or self.heartbeat_task.done():
            self.heartbeat_task = create_task(self.heartbeat())
        return self.heartbeat_task
    
    def stop_heartbeat(self):
        if self.heartbeat_task and not self.heartbeat_task.done():
            self.heartbeat_task.cancel()
            self.heartbeat_task = None

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

TTaskResult = TypeVar('TTaskResult', bound=Jsonable)

class Task(Tasklike, Typed[TTaskResult], PubSubbed[TTaskResult]):

    autorun = models.BooleanField(default=True)

    DO_NOT_QUEUE: ClassVar[bool] = False

    class Meta(Tasklike.Meta):

        abstract = True
        indexes = [
            models.Index(
                name='%(app_label)s_%(model_name)s_is_running_idx',
                fields=['uuid'],
                condition=models.Q(is_running=True)
            )
        ]

    async def run(self):
        """Explicitly trigger task execution."""
        await self.subscribe()
        
        self.start_heartbeat()
        
        try:
            if is_async_function(self.handler):
                result = await self.set_result(await self.handler())
            else:
                async_task(django_q_handler, self, sync=self.DO_NOT_QUEUE)
                result = await self
            return result
        finally:
            self.stop_heartbeat()

    async def save_result(self, result: TTaskResult):
        self.data = result
        self.finished_at = timezone.now()
        await self.asave()

    async def load_result(self):
        match self.succeeded:
            case True:
                return ( True, self.data )
            case False:
                raise RuntimeError("Task failed")
            case None:
                return ( False, None )

    @abc.abstractmethod
    async def handler(self) -> TTaskResult:
        raise NotImplementedError("The handler must be implemented by each subclass of Task")

def django_q_handler(task: Task[TTaskResult]):
    if not is_sync_function(task.handler):
        raise RuntimeError("Django Q task handler must be a sync function")
    task.result = task.handler()