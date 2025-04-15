from typing import Literal

from utils.powerups.base import BaseModel
from utils.powerups.webhooks import WebhookHandler, WebhookTargetBase

from django.db import models

WebhookTargetName = Literal["django", "nextjs"]

class WebhookTarget(WebhookTargetBase[WebhookTargetName]):
    pass

webhook = WebhookHandler(WebhookTarget)

@webhook('django')
class WebSearch(BaseModel):
    query = models.CharField(max_length=255)