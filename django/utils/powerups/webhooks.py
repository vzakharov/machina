import os
from dataclasses import dataclass
import re
from typing import Generic, TypedDict, TypeVar

from utils.functional import ensure_is
from utils.powerups.base import WithIntId

from django.db import models

from utils.powerups.triggers import TriggerEvent, trigger

TWebhookTargetName = TypeVar('TWebhookTargetName', bound=str)

class Generish(Generic[TWebhookTargetName]):
    pass

class WebhookTargetBase(Generish[TWebhookTargetName], models.Model, WithIntId):

    class Meta:
        abstract = True

# pyright: reportAssignmentType = false
    name: 'models.CharField[TWebhookTargetName]' = models.CharField(max_length=255)
    url = models.URLField()
    version = models.IntegerField(default=1)

    env_prefix = 'WEBHOOK_TARGET_'

    class EnvMatch(TypedDict):
        name: str
        url: str

    @classmethod
    def match_env(cls, key: str) -> EnvMatch | None:
        if key.startswith(cls.env_prefix):
            return {
                'name': key[len(cls.env_prefix):].lower(),
                'url': ensure_is(str, os.getenv(key), f'{key} must be set to a valid URL')
            }
        return None

    @classmethod
    def load_from_envs(cls):
        cls.objects.exclude(id__in=[
            cls.objects.get_or_create(**match)[0].id
            for key in os.environ
            if (match := cls.match_env(key))
        ]).delete()


FUNCTION_TEMPLATE = """
supabase_functions.http_request(
    (SELECT url FROM public.{table_name} WHERE name = '{target_name}'),
    'POST',
    '{{{{"Content-Type":"application/json"}}}}',
    '{{{{}}}}',
    '1000'
)"""

@dataclass
class WebhookHandler(Generic[TWebhookTargetName]):

    TargetModel: type[WebhookTargetBase[TWebhookTargetName]]

    def post_process_sql(self, sql: str):
        return re.sub(r'\n\s*', '', sql)

    def get_function_sql(self, name: TWebhookTargetName):
        return self.post_process_sql(
            FUNCTION_TEMPLATE.format(
                table_name=self.TargetModel._meta.db_table,
                target_name=name
            )
        )

    def __call__(self, name: TWebhookTargetName, after: TriggerEvent = 'INSERT OR DELETE OR UPDATE'):

        return trigger(
            func=self.get_function_sql(name),
            timing='AFTER',
            event=after,
            name=name
        )
