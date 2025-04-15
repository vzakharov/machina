import os
from dataclasses import dataclass
from typing import Generic, TypedDict, TypeVar

from utils.functional import ensure_is
from utils.logging import logger
from utils.migrations import MigrationHandler
from utils.powerups.base import WithIntId
from utils.powerups.triggers import Trigger, TriggerEvent, trigger
from utils.strings import newlines_to_spaces

from django.db import ProgrammingError, models

TWebhookTargetName = TypeVar('TWebhookTargetName', bound=str)

class Generish(Generic[TWebhookTargetName]):
    pass

class Target(TypedDict):
    name: str
    url: str

class WebhookTargetBase(Generish[TWebhookTargetName], models.Model, WithIntId):

    class Meta:
        abstract = True

# pyright: reportAssignmentType = false
    name: 'models.CharField[TWebhookTargetName]' = models.CharField(max_length=255)
    url = models.URLField()
    # version = models.IntegerField(default=1)
    # TODO: add back in

    env_prefix = 'WEBHOOK_TARGET_'


    @classmethod
    def match_env(cls, key: str) -> Target | None:
        if key.startswith(cls.env_prefix):
            return {
                'name': key[len(cls.env_prefix):].lower(),
                'url': ensure_is(str, os.getenv(key), f'{key} must be set to a valid URL')
            }
        return None


    @classmethod
    def get_update_sql(cls, targets: list[Target]):
        table_name = f"public.{cls._meta.db_table}"
        return newlines_to_spaces(f"""
            INSERT INTO {table_name} (name, url)
            VALUES {','.join(
                f"('{target['name']}','{target['url']}')"
                for target in targets
            )}
        """) if targets else f"DELETE FROM {table_name}"
    
    @classmethod
    def env_targets(cls):
        return [
            match for key in os.environ
            if ( match := cls.match_env(key) )
        ]

    @classmethod
    def stored_targets(cls):
        try:
            return [Target(
                name=target.name,
                url=target.url
            ) for target in cls.objects.all()]
        except ProgrammingError as e:
            logger.warning(f'{cls.__name__} table does not exist yet; Apply migrations first')
            raise e
    
    @classmethod
    def MakeMigrations(cls):
    
        class MakeMigrations(Trigger.MakeMigrations):

            def create_trigger_migrations(self):
                if self.migrations_needed():
                    self.create_target_update_migration()
                super().create_trigger_migrations()

            def migrations_needed(self):
                return cls.env_targets() != cls.stored_targets()

            def create_target_update_migration(self):
                stored = cls.stored_targets()
                new = cls.env_targets()
                MigrationHandler(
                    cls,
                    prefixes    = [ 'update' if stored else 'populate' ],
                    sql         = cls.get_update_sql(new),
                    reverse_sql = cls.get_update_sql(stored)
                ).write()

        return MakeMigrations

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
        return newlines_to_spaces(sql)

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
