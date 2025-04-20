from django.db import models

class Trigger(models.Model):

    class Meta:
        managed = False
        db_table = 'information_schema"."triggers'

    trigger_catalog = models.CharField(max_length=255)
    trigger_schema = models.CharField(max_length=255)
    trigger_name = models.CharField(max_length=255, primary_key=True)
    event_manipulation = models.CharField(max_length=32)
    event_object_catalog = models.CharField(max_length=255)
    event_object_schema = models.CharField(max_length=255)
    event_object_table = models.CharField(max_length=255)
    action_order = models.IntegerField()
    action_condition = models.CharField(max_length=1024, null=True)
    action_statement = models.TextField()
    action_orientation = models.CharField(max_length=32)
    action_timing = models.CharField(max_length=32)
    action_reference_old_table = models.CharField(max_length=255, null=True)
    action_reference_new_table = models.CharField(max_length=255, null=True)
    action_reference_old_row = models.CharField(max_length=255, null=True)
    action_reference_new_row = models.CharField(max_length=255, null=True)
    created = models.DateTimeField(null=True)