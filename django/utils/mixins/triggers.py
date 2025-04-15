import os
from dataclasses import dataclass
from typing import ClassVar, Literal, TypedDict

from utils.collections import compact
from utils.errors import throw
from utils.functional import ensure_is, given
from utils.mixins.base import BaseModel

from django.core.management.commands.makemigrations import \
    Command as OriginalMakeMigrationsCommand
from django.db import connection
from django.db.migrations import Migration, RunSQL
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.writer import MigrationWriter

from .tracks_descendants import TracksDescendants


class TriggerSpec(TypedDict):
    timing: Literal['BEFORE', 'AFTER']
    event: Literal['INSERT', 'DELETE', 'UPDATE', 'INSERT OR DELETE', 'INSERT OR UPDATE', 'DELETE OR UPDATE', 'INSERT OR DELETE OR UPDATE']
    func: str

@dataclass
class Trigger():

    Model: type['Triggerable']
    name: str
    spec: TriggerSpec

    @property
    def table_name(self):
        return self.Model._meta.db_table
    
    @property
    def full_table_name(self):
        return f"public.{self.table_name}"

    @property
    def sql_name(self):
        return f"{self.table_name}_{self.name}"
    
    @property
    def sql_body(self):
        return "CREATE TRIGGER {} {} {} ON {} FOR EACH ROW EXECUTE FUNCTION {}".format(
            self.sql_name,
            self.spec['timing'],
            self.spec['event'],
            self.full_table_name,
            self.spec['func']
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
    
    @dataclass
    class MigrationInfo():
        index: int
        name: str

    @property
    def previous_migration(self):
        app_label = self.Model._meta.app_label
        for migration in reversed(
            sorted(
                MigrationLoader(connection).disk_migrations.values(),
                key=lambda migration: migration.name
            )
        ):
            if migration.app_label == app_label:
                return Trigger.MigrationInfo(
                    index=int(migration.name.split('_')[0]),
                    name=migration.name
                )
        raise ValueError(f"No previous migration found for {app_label}")

    def create_migration(self, existing_body: str | None):
        model_meta = self.Model._meta
        
        app_label = model_meta.app_label
        previous = self.previous_migration

        migration = Migration(
            '_'.join(compact(
                f"{previous.index + 1:04d}",
                existing_body and 'alter',
                'trigger_for',
                model_meta.model_name,
            )),
            app_label
        )
        migration.dependencies = [ ( app_label, previous.name ) ]
        migration.operations = [
            RunSQL(
                sql=self.drop_and(self.sql_body),
                reverse_sql=self.drop_and(existing_body)
            )
        ]
        
        writer = MigrationWriter(migration)
        path = writer.path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(writer.as_string())
        return path

class Triggerable(BaseModel, TracksDescendants):

    class Meta(BaseModel.Meta):
        abstract = True

    trigger_specs: ClassVar[dict[str, TriggerSpec] | None] = None

    @classmethod
    def get_trigger_specs(cls):
        return cls.trigger_specs or throw(
            NotImplementedError(
                f"{cls.__name__} must either define class variable 'trigger_specs' "
                f"or override the classmethod 'get_trigger_specs'."
            )
        )
    
    @classmethod
    def get_triggers(cls):
        return [
            Trigger(
                Model=cls,
                name=trigger_name,
                spec=trigger_spec
            )
            for trigger_name, trigger_spec in cls.get_trigger_specs().items()
        ]
    
class TriggerableMakeMigrationsCommand(OriginalMakeMigrationsCommand):

    def handle(self, *args, **options):
        super().handle(*args, **options)
        self.make_trigger_migrations()

    def make_trigger_migrations(self):
        for Model in Triggerable.get_descendant_classes():
            for trigger in Model.get_triggers():
                trigger.create_migration_if_needed()