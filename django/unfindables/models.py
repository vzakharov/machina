# from typing import Literal

from utils.migrations import Migrator
from utils.powerups.base import BaseModel
from utils.powerups.triggers import trigger
# from utils.powerups.webhooks import WebhookHandler, WebhookTargetBase

from django.db import models

from utils.strings import newlines_to_spaces

# WebhookTargetName = Literal["django", "nextjs"]

# class WebhookTarget(WebhookTargetBase[WebhookTargetName]):
#     pass

# webhook = WebhookHandler(WebhookTarget)

# @webhook('django', after='INSERT')

class DjangoWebhookMigrator(Migrator):

    @classmethod
    def get_sql(cls):
        import os

        return newlines_to_spaces("""
            supabase_functions.http_request(
                '{}',
                'POST',
                '{{{{"Content-Type":"application/json"}}}}',
                '{{{{}}}}',
                '1000'
            )
        """).format(
            os.environ['WEBHOOK_TARGET_DJANGO']
        )

@trigger(
    MigratorClass=DjangoWebhookMigrator,
    timing='AFTER',
    event='INSERT',
    name='django'
)
class WebSearch(BaseModel):
    query = models.CharField(max_length=255)