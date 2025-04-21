# from typing import Literal

from typing import Literal
from djapa.webhooks import WebhookDecorator
from utils.powerups.base import BaseModel
# from utils.powerups.webhooks import WebhookHandler, WebhookTargetBase

from django.db import models


WebhookTargetName = Literal["django", "nextjs"]

class Webhook(WebhookDecorator[WebhookTargetName]):
    pass

webhook = Webhook()

@webhook('django', 'DELETE')
class WebSearch(BaseModel):
    query = models.CharField(max_length=255)