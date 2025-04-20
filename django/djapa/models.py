from typing import Literal
from django.db import connection, models

from utils.strings import newlines_to_spaces
from utils.typing import none

TriggerTiming = Literal['BEFORE', 'AFTER']
TriggerEvent = Literal['INSERT', 'DELETE', 'UPDATE']

class Trigger(models.Model):

    class Meta:
        managed = False
        db_table = 'information_schema"."triggers'

    trigger_catalog = models.CharField(max_length=255)
    trigger_schema = models.CharField(max_length=255)
    trigger_name = models.CharField(max_length=255, primary_key=True)
    # This is wrong: trigger_name is NOT unique. This is just a hack to make Django happy (otherwise it is looking for an `id` field)
    # But thing is, none of the fields in the view are unique, so ¯\_(ツ)_/¯

# pyright: reportAssignmentType = false
    event_manipulation: models.CharField[TriggerEvent] = models.CharField(max_length=32)
    event_object_catalog = models.CharField(max_length=255)
    event_object_schema = models.CharField(max_length=255)
    event_object_table = models.CharField(max_length=255)
    action_order = models.IntegerField()
    action_condition = models.CharField(max_length=1024, null=True)
    action_statement = models.TextField()
    action_orientation = models.CharField(max_length=32)
# pyright: reportAssignmentType = false
    action_timing: models.CharField[TriggerTiming] = models.CharField(max_length=32)
    action_reference_old_table = models.CharField(max_length=255, null=True)
    action_reference_new_table = models.CharField(max_length=255, null=True)
    action_reference_old_row = models.CharField(max_length=255, null=True)
    action_reference_new_row = models.CharField(max_length=255, null=True)
    created = models.DateTimeField(null=True)

    @classmethod
    def create(cls,
        timing: TriggerTiming,
        events: list[TriggerEvent],
        Model: type[models.Model],
        statement: str,
        trigger_name = none(str),
        table_name = none(str),
    ):
        """
        Create a new trigger for a model.

        Args:
            timing: The timing of the trigger.
            events: The events that will trigger the trigger.
            Model: The model that the trigger is for.

        Returns:
            List of triggers created (if there were several events, several triggers will be created)
        """
        table_name = table_name or f"public.{Model._meta.db_table}"
        trigger_name = trigger_name or (
            f'{table_name}_{int(last_trigger.trigger_name.split('_')[-1]) + 1}'
            if ( 
                last_trigger := cls.objects
                    .filter(trigger_name__startswith=f'{table_name}_')
                    .order_by('-trigger_name')
                    .first() 
            ) else f'{table_name}_1'
        )

        with connection.cursor() as cursor:

            cursor.execute(newlines_to_spaces(f"""
                CREATE TRIGGER {trigger_name}
                {timing} {events} ON {table_name}
                FOR EACH ROW
                EXECUTE FUNCTION {statement}
            """))

            return list(cls.objects.filter(trigger_name=trigger_name))