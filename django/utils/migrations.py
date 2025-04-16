import os
from dataclasses import dataclass
from typing import Generic, TypeVar

from utils.collections import Compactable, compact

from django.db import connection, models
from django.db.migrations import RunPython
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.migration import Migration
from django.db.migrations.writer import MigrationWriter
from django.apps.registry import Apps
from django.db.backends.base.schema import BaseDatabaseSchemaEditor


@dataclass
class MigrationInfo():
    index: int
    name: str

TModel = TypeVar('TModel', bound=models.Model)

# #pyright: reportUndefinedVariable=false, reportUnknownVariableType=false, reportUnknownArgumentType=false
# # because we're using this as a stub to inject into the migration file (uppercases will be replaced with actual values)
# def migrator(fn: Returns[str]):
#     def migrate(apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
#         sql_body = fn()
#         from django.db import connection
#         with connection.cursor() as cursor:
#             cursor.execute(sql_body)
#     return migrate

class Migrator():

    @classmethod
    def get_sql(cls) -> str:
        ...

    @classmethod
    def migrate(cls, apps: Apps, schema_editor: BaseDatabaseSchemaEditor):
        sql = cls.get_sql()
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(sql)

@dataclass
class MigrationHandler(Generic[TModel]):

    Model: type[TModel]
    prefixes: list[Compactable[str]]
    MigratorClass: type[Migrator]
    # reverse_sql: Returns[str]

    @property
    def last_migration(self):
        app_label = self.Model._meta.app_label
        for migration in reversed(
            sorted(
                MigrationLoader(connection).disk_migrations.values(),
                key=lambda migration: migration.name
            )
        ):
            if migration.app_label == app_label:
                return MigrationInfo(
                    index=int(migration.name.split('_')[0]),
                    name=migration.name
                )
        raise ValueError(f"No previous migration found for {app_label}")

    def write(self):
        last = self.last_migration
        meta = self.Model._meta
        migration = Migration(
            '_'.join(compact(
                f"{last.index + 1:04d}",
                *self.prefixes,
                meta.model_name,
            )),
            meta.app_label
        )
        migration.dependencies = [ ( meta.app_label, last.name ) ]
        migration.operations = [
            # RunSQL(
            #     sql=self.sql,
            #     reverse_sql=self.reverse_sql
            # )
            RunPython(
                code=self.MigratorClass.migrate,
                # reverse_code=migrator(self.reverse_sql)
            )
        ]
        writer = MigrationWriter(migration)
        path = writer.path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(writer.as_string())
        return migration