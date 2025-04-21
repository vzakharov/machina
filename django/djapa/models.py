from typing import Any, TypeGuard

from utils.functional import tap
from utils.logging import info
from utils.strings import newlines_to_spaces
from utils.typing import none

from django.db import connection, models

from .types import TriggerEvent, TriggerTiming


class PublicTriggerManager(models.Manager['Trigger']):

    def get_queryset(self):
        return super().get_queryset().filter(trigger_schema='public')

def is_trigger_class(cls: type[models.Model]) -> TypeGuard[type['Trigger']]:
    return cls.__name__ == 'Trigger'

class TriggerMeta(models.base.ModelBase):
    
    def __new__(mcs, name: Any, bases: Any, attrs: Any):
        cls = super().__new__(mcs, name, bases, attrs)
        if is_trigger_class(cls):
            cls.drop_all()
        return cls

class Trigger(models.Model, metaclass = TriggerMeta):

    class Meta:
        managed = False
        db_table = 'information_schema"."triggers'

    objects = PublicTriggerManager()

    trigger_catalog = models.CharField(max_length=255)
    trigger_schema = models.CharField(max_length=255)
    trigger_name = models.CharField(max_length=255, primary_key=True)
    # This is wrong: trigger_name is NOT unique. This is just a hack to make Django happy (otherwise it is looking for an `id` field)
    # But thing is, none of the fields in the view are unique, so ¯\_(ツ)_/¯

# pyright: reportAssignmentType = false
    event_manipulation: 'models.CharField[TriggerEvent]' = models.CharField(max_length=32)
    event_object_catalog = models.CharField(max_length=255)
    event_object_schema = models.CharField(max_length=255)
    event_object_table = models.CharField(max_length=255)
    action_order = models.IntegerField()
    action_condition = models.CharField(max_length=1024, null=True)
    action_statement = models.TextField()
    action_orientation = models.CharField(max_length=32)
# pyright: reportAssignmentType = false
    action_timing: 'models.CharField[TriggerTiming]' = models.CharField(max_length=32)
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
        trigger_name = none(str),
        table_name = none(str),
    ):
        table_name = Model._meta.db_table
        full_table_name = f"public.{table_name}"
        trigger_name = trigger_name or (
            f'{table_name}_{int(last_trigger.trigger_name.split('_')[-1]) + 1}'
            if ( 
                last_trigger := cls.objects
                    .filter(trigger_name__startswith=f'{table_name}_')
                    .order_by('-trigger_name')
                    .first() 
            ) else f'{table_name}_1'
        )
        events_string = ' OR '.join(events)

        with connection.cursor() as cursor:

            cursor.execute(newlines_to_spaces(f"""
                CREATE TRIGGER {trigger_name}
                {timing} {events_string} ON {full_table_name}
                FOR EACH ROW
                EXECUTE FUNCTION {statement}
            """))


            return tap(
                list(cls.objects.filter(trigger_name=trigger_name)),
                lambda new_triggers: info('Created {} triggers for {} as {}: {}'.format(
                    len(new_triggers),
                    cls._meta.db_table,
                    new_triggers[0].trigger_name,
                    new_triggers[0].action_statement
                ))
            )
    
    def drop(self, raise_if_missing = False):
        with connection.cursor() as cursor:
            cursor.execute(newlines_to_spaces("""
                DROP TRIGGER {}{} ON {}
            """.format(
                '' if raise_if_missing else 'IF EXISTS ',
                self.trigger_name,
                self.event_object_table,
            )))

    @classmethod
    def drop_all(cls):
        triggers = cls.objects.distinct('trigger_name')
        # `.distinct()` because every drop will drop _all_ triggers with the same name (i.e. all of INSERT, UPDATE, DELETE, depending on which events are set)
        count = len(triggers)
        for trigger in triggers:
            trigger.drop()
        info(f'Dropped {count} triggers')

    @classmethod
    def setup(cls,
        timing: TriggerTiming,
        events: tuple[TriggerEvent, ...],
        statement: str,
        trigger_name = none(str),
        table_name = none(str),
    ):
        def decorator(cls: type[models.Model]):
            Trigger.create(timing, events, cls, statement, trigger_name, table_name)
            return cls
        return decorator
    
trigger = Trigger.setup # just a shortcut for easier reading/setting