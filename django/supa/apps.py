from django.apps import AppConfig


class SupaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'supa'

    def ready(self):
        from .models import Trigger
        Trigger.update_triggers()
