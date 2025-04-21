import os
from typing import Generic, TypeVar

from utils.strings import newlines_to_spaces

from .models import trigger
from .types import TriggerEvent

TTargetName = TypeVar('TTargetName', bound=str)

class WebhookDecorator(Generic[TTargetName]):
    
    def __call__(self, name: TTargetName, *events: TriggerEvent):
        return trigger(
            timing='AFTER',
            events=events or ('INSERT',),
            statement=newlines_to_spaces(f"""
                supabase_functions.http_request(
                    '{os.getenv(f'WEBHOOK_TARGET_{name.upper()}')}',
                    'POST',
                    '{{{{"Content-Type":"application/json"}}}}',
                    '{{{{}}}}',
                    '1000'
            )"""),
        )