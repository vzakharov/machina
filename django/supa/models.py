from typing import ClassVar, TypedDict, TypeGuard

from utils.functional import tap
from utils.logging import debug, info, warning
from utils.strings import newlines_to_spaces
from utils.typing import none

from django.apps import apps
from django.core.exceptions import AppRegistryNotReady
from django.db import connection, models
from django.db.utils import ProgrammingError

from .types import TriggerEvent, TriggerTiming


class PublicTriggerManager(models.Manager['Trigger']):

    def get_queryset(self):
        return super().get_queryset().filter(trigger_schema='public')

def is_trigger_class(cls: type[models.Model]) -> TypeGuard[type['Trigger']]:
    return cls.__name__ == 'Trigger'

TriggerName = str
class TriggerInfo(TypedDict):
    event: TriggerEvent
    table_name: str
    timing: TriggerTiming
    statement: str
    
TriggerMap = dict[TriggerName, list[TriggerInfo]]


class Trigger(models.Model):

    class Meta:
        managed = False
        db_table = 'information_schema"."triggers'

    objects = PublicTriggerManager() # pyright: ignore[reportAssignmentType]

    trigger_catalog = models.CharField(max_length=255)
    trigger_schema = models.CharField(max_length=255)
    trigger_name = models.CharField(max_length=255, primary_key=True)
    # This is wrong: trigger_name is NOT unique. This is just a hack to make Django happy (otherwise it is looking for an `id` field)
    # But thing is, none of the fields in the view are unique, so ¯\_(ツ)_/¯

    event: 'models.CharField[TriggerEvent]' = (
        models.CharField(max_length=32, db_column='event_manipulation') # pyright: ignore[reportAssignmentType]
    )
    event_object_catalog = models.CharField(max_length=255)
    event_object_schema = models.CharField(max_length=255)
    table_name = models.CharField(max_length=255, db_column='event_object_table')
    action_order = models.IntegerField()
    action_condition = models.CharField(max_length=1024, null=True)
    statement = models.TextField(db_column='action_statement')
    action_orientation = models.CharField(max_length=32)
    timing: 'models.CharField[TriggerTiming]' = (
        models.CharField(max_length=32, db_column='action_timing') # pyright: ignore[reportAssignmentType]
    )
    action_reference_old_table = models.CharField(max_length=255, null=True)
    action_reference_new_table = models.CharField(max_length=255, null=True)
    action_reference_old_row = models.CharField(max_length=255, null=True)
    action_reference_new_row = models.CharField(max_length=255, null=True)
    created = models.DateTimeField(null=True)

    @classmethod
    def create(cls,
        timing: TriggerTiming,
        events: tuple[TriggerEvent, ...],
        Model: type[models.Model],
        statement: str,
        trigger_name = none(TriggerName),
    ):
        cls.update_triggers(cls.prepare(timing, events, Model, statement, trigger_name))

    map: ClassVar[TriggerMap] = {}

    @classmethod
    def update_triggers(cls, map = none(TriggerMap)):
        if not map:
            try:
                apps.check_apps_ready()
            except AppRegistryNotReady:
                raise AppRegistryNotReady('Cannot update triggers before apps are ready')
            map = cls.map
        debug(f'Updating triggers with {map=}')
        for trigger_name, trigger_infos in map.items():

            existing_triggers = cls.objects.filter(trigger_name=trigger_name)
            if existing_triggers.exists():
                if (
                    existing_triggers.count() == len(trigger_infos) 
                    and all(
                        existing_triggers.filter(**trigger_info).exists()
                        for trigger_info in trigger_infos
                    )
                ):
                    debug(f'Triggers for {trigger_name} are up to date')
                    continue
                info(f'Triggers for {trigger_name} are outdated, deleting existing triggers')
                existing_triggers[0].drop()

            try:
                trigger_info = trigger_infos[0]
                events_string = ' OR '.join([
                    trigger_info['event'] for trigger_info in trigger_infos
                ])
                info(f'Creating trigger(s) {trigger_name} for {trigger_info=}')
                with connection.cursor() as cursor:
                    cursor.execute(
                        f"CREATE TRIGGER {trigger_name}"
                        f" {trigger_info['timing']} {events_string}"
                        f" ON public.{trigger_info['table_name']}"
                        f" FOR EACH ROW"
                        f" {trigger_info['statement']}"
                    )
                    new_triggers = list(cls.objects.filter(trigger_name=trigger_name))
                    info('Created {} trigger(s) for {} as {}: {}'.format(
                        len(new_triggers),
                        cls._meta.db_table,
                        new_triggers[0].trigger_name,
                        new_triggers[0].statement
                    ))
            except ProgrammingError as e:
                warning(f'Error creating trigger {trigger_name}, skipping: {e}')

    @classmethod
    def prepare(cls, 
        timing: TriggerTiming,
        events: tuple[TriggerEvent, ...],
        Model: type[models.Model],
        statement: str,
        trigger_name: TriggerName | None,
    ):
        table_name = Model._meta.db_table
        trigger_name = table_name
        suffix = 2
        while trigger_name in cls.map:
            trigger_name = f'{table_name}_{suffix}'
            suffix += 1
        return {
            trigger_name: [
                TriggerInfo(
                    table_name = table_name,
                    timing = timing,
                    event = event,
                    statement = f'EXECUTE FUNCTION {statement}',
                )
                for event in events
            ]
        }
    
    def drop(self, raise_if_missing = False):
        """
        Drops the trigger. Note that, if there are several events configured for the same trigger,
        this will drop all of them. 
        
        Returns the number of triggers dropped.
        """
        with connection.cursor() as cursor:
            cls = self.__class__
            initial_count = cls.objects.count()
            cursor.execute(newlines_to_spaces("""
                DROP TRIGGER {}{} ON {}
            """.format(
                '' if raise_if_missing else 'IF EXISTS ',
                self.trigger_name,
                self.table_name,
            )))
            return tap(
                initial_count - cls.objects.count(),
                lambda count: info(f'Dropped {count} trigger(s) for {self.trigger_name}')
            )
    
    @classmethod
    def grouped_triggers(cls):
        """
        Returns a dictionary of the first trigger for each trigger name mapped to a list of all triggers with the same name.
        """
        return {
            trigger: list(cls.objects.filter(trigger_name=trigger.trigger_name))
            for trigger in cls.objects.distinct('trigger_name')
        }

    @classmethod
    def drop_all(cls):
        return tap(
            sum(
                trigger.drop()
                for trigger in cls.grouped_triggers().keys()
            ),
            lambda count: info(f'Dropped {count} trigger(s) in total')
        )

    @classmethod
    def setup(cls,
        timing: TriggerTiming,
        events: tuple[TriggerEvent, ...],
        statement: str,
        trigger_name = none(str),
    ):
        def decorator(Model: type[models.Model]):
            new_triggers = Trigger.prepare(timing, events, Model, statement, trigger_name)
            cls.map.update(new_triggers)
            debug(f'Setup {new_triggers=} for {Model._meta.db_table}')
            return Model
        return decorator
    
trigger = Trigger.setup # just a shortcut for easier reading/setting