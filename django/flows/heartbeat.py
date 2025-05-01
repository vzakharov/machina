import asyncio
from asyncio import create_task, sleep
from datetime import timedelta
from typing import ClassVar

from utils.typing import Readonly, none

from django.db import models
from django.db.models.functions import Now
from django.utils import timezone


class Heartbeatable(models.Model):

    class Meta:
        abstract = True

    HEARBEAT_INTERVAL: ClassVar[timedelta] = timedelta(seconds=4)
    HEARTBEAT_GRACE_PERIOD: ClassVar[timedelta] = timedelta(seconds=4)
  
    is_running: 'models.Field[Readonly, bool]'

    latest_heartbeat = models.DateTimeField(db_default=Now())
    heartbeat_task = none(asyncio.Task[None])

    async def heartbeat(self):
        while self.is_running:
            await sleep(self.HEARBEAT_INTERVAL.total_seconds())
            self.latest_heartbeat = timezone.now()
            await self.asave(update_fields=['last_alive_at'])
    
    def start_heartbeat(self):
        if not self.heartbeat_task or self.heartbeat_task.done():
            self.heartbeat_task = create_task(self.heartbeat())
        return self.heartbeat_task
    
    def stop_heartbeat(self):
        if self.heartbeat_task and not self.heartbeat_task.done():
            self.heartbeat_task.cancel()
            self.heartbeat_task = None