from dataclasses import dataclass
from typing import Literal, TypeVar

from utils.collections import compact, empty_list
from utils.functional import ensure_is, given
from utils.migrations import MigrationHandler, Migrator

from django.core.management.commands.makemigrations import \
    Command as OriginalMakeMigrationsCommand
from django.db import connection, models

TriggerTiming = Literal['BEFORE', 'AFTER']
TriggerEvent = Literal['INSERT', 'DELETE', 'UPDATE', 'INSERT OR DELETE', 'INSERT OR UPDATE', 'DELETE OR UPDATE', 'INSERT OR DELETE OR UPDATE']

@dataclass
class Trigger():

    Model: type['models.Model']
    MigratorClass: type[Migrator]
    timing: TriggerTiming
    event: TriggerEvent
    name: str | None

    @property
    def table_name(self):
        return self.Model._meta.db_table

    @property
    def full_table_name(self):
        return f"public.{self.table_name}"

    @property
    def sql_name(self):
        return '_'.join(compact(
            self.table_name,
            self.name
        ))
    
    @property
    def sql_body(self):
        return "CREATE TRIGGER {} {} {} ON {} FOR EACH ROW EXECUTE FUNCTION {}".format(
            self.sql_name,
            self.timing,
            self.event,
            self.full_table_name,
            self.MigratorClass.get_sql()
        )
    
    @property
    def existing_body(self):
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT pg_get_triggerdef(oid) FROM pg_trigger WHERE tgname = '{self.sql_name}'")
            return given(cursor.fetchone(), lambda body: ensure_is(str, body[0]))
        
    def create_migration_if_needed(self):
        existing_body = self.existing_body
        if not existing_body or existing_body != self.sql_body:
            self.create_migration(existing_body)

    @property
    def drop_sql(self):
        return "DROP TRIGGER IF EXISTS {} ON {}".format(
            self.sql_name,
            self.full_table_name
        )
    
    def drop_and(self, sql: str | None):
        return ';'.join(compact(self.drop_sql, sql))
    
    def create_migration(self, existing_body: str | None):
        MigrationHandler(
            self.Model,
            MigratorClass   = self.MigratorClass,
            prefixes        = [ existing_body and 'alter', 'trigger_for' ],
            # sql         = self.drop_and(self.sql_body),
            # reverse_sql = self.drop_and(existing_body),
        ).write()

    class MakeMigrations(OriginalMakeMigrationsCommand):

        def handle(self, *args, **options):
            super().handle(*args, **options)
            self.create_trigger_migrations()

        def create_trigger_migrations(self):
            for trigger in all_triggers:
                trigger.create_migration_if_needed()

all_triggers = empty_list(Trigger)

def trigger(MigratorClass: type[Migrator], timing: TriggerTiming, event: TriggerEvent, name: str | None = None):
    T = TypeVar('T', bound=models.Model)
    def decorator(cls: type[T]):
        all_triggers.append(
            Trigger(cls, MigratorClass, timing, event, name)
        )
        return cls
    return decorator