# from typing import Literal

from typing import Literal
from supa.webhooks import WebhookDecorator
from utils.powerups.base import BaseModel
# from utils.powerups.webhooks import WebhookHandler, WebhookTargetBase

from django.db import models


WebhookTargetName = Literal["django", "nextjs"]

webhook = WebhookDecorator[WebhookTargetName]()

@webhook('nextjs', 'INSERT')
class WebSearch(BaseModel):
    query = models.CharField(max_length=255)