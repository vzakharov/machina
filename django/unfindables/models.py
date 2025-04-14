from django.db import models

from utils.mixins.triggers import Triggerable

class WebSearch(Triggerable):
    query = models.CharField(max_length=255)

    trigger_specs = {
        'on_insert': {
            'timing': 'BEFORE',
            'event': 'INSERT',
            'func': 'some_function_defined_in_supabase'
        }
    }