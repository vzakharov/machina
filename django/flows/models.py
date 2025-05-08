import abc
from asyncio import create_task
import traceback
from typing import Any, ClassVar, TypedDict, TypeVar

from django_q.tasks import async_task
from utils.django import IsNull
from utils.powerups.pubsub import PubSubbed
from utils.powerups.typed import Typed
from utils.typing import (Jsonable, Readonly, is_async_function,
                          is_sync_function)

from django.db import models, transaction
from django.db.models import Case, When
from django.db.models.functions import Now
from django.utils import timezone

from .heartbeat import Heartbeatable


class ErrorInfo(TypedDict):
    message: str
    traceback: str

class TaskError(Exception):
    def __init__(self, error: ErrorInfo):
        self.error = error

class Taskable(Heartbeatable):

    class Meta(Heartbeatable.Meta):
        abstract = True

    created_at = models.DateTimeField(db_default=Now())
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    stuck = models.BooleanField(db_default=False, db_index=True)
    error: 'models.JSONField[ErrorInfo | None]' = models.JSONField(default=None, null=True)

    is_running = models.GeneratedField( # pyright: ignore[reportAttributeAccessIssue]
        expression=IsNull('finished_at'),
        output_field=models.BooleanField(),
        db_persist=True,
        db_index=True,
    )

    is_pending: 'models.Field[Readonly, bool]' = models.GeneratedField( # pyright: ignore[reportAttributeAccessIssue]
        expression=IsNull('started_at'),
        output_field=models.BooleanField(),
        db_persist=True,
        db_index=True,
    )

    succeeded: 'models.Field[Readonly, bool | None]' = models.GeneratedField( # pyright: ignore[reportAttributeAccessIssue]
        expression=Case(
            When(finished_at__isnull=True, then=None),
            When(error__isnull=True, then=True),
            default=False,
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        db_index=True,
    )

class Tide(Taskable):
    """
    A tide is a single run of any outstanding tasks, as well as any tasks that are created while it is running. Only one tide can run at a time, hence the constraint.
    """

    class Meta(Taskable.Meta):
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
            tide, created = cls.objects.select_for_update().get_or_create(finished_at__isnull=True)
            if created:
                create_task(tide.start())
            else:
                if tide.latest_heartbeat < timezone.now() - cls.HEARBEAT_INTERVAL - cls.HEARTBEAT_GRACE_PERIOD:
                    tide.stuck = True
                    tide.finished_at = timezone.now()
                    tide.save()
                    tide = cls.objects.create()
            return tide
        
    async def start(self):
        for Model in task_models:
            while True:
                with transaction.atomic():
                    task = await Model.objects.filter(is_pending=True).select_for_update().afirst()
                    if task:
                        await task._run()
                    else:
                        break
                await asyncio.sleep(1)

task_models: list[type['Task[Any]']] = []

class Task(Taskable, Typed[TTaskResult], PubSubbed[TTaskResult]):

    autorun = models.BooleanField(default=True)

    DO_NOT_QUEUE: ClassVar[bool] = False

    class Meta(Taskable.Meta, Typed.Meta, PubSubbed.Meta):

        abstract = True
        indexes = [
            models.Index(
                name='%(app_label)s_%(model_name)s_is_running_idx',
                fields=['uuid'],
                condition=models.Q(is_running=True)
            )
        ]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        meta = cls._meta
        if not meta.abstract and issubclass(cls, Task):
            task_models.append(cls)

    async def _run(self):
        """Explicitly trigger task execution."""
        await self.subscribe()
        self.started_at = timezone.now()
        await self.asave()
        self.start_heartbeat()
        
        try:
            if is_async_function(self.handler):
                result = await self.set_result(await self.handler())
            else:
                async_task(django_q_handler, self, sync=self.DO_NOT_QUEUE)
                result = await self
            return result
        except Exception as e:
            self.error = ErrorInfo(
                message=str(e),
                traceback=traceback.format_exc()
            )
            self.finished_at = timezone.now()
            await self.asave()
            raise
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