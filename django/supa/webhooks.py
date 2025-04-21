import os
from typing import Generic, TypeVar

from utils.errors import throw
from utils.strings import newlines_to_spaces

from .models import trigger
from .types import TriggerEvent

TTargetName = TypeVar('TTargetName', bound=str)

class WebhookDecorator(Generic[TTargetName]):
    
    def __call__(self, name: TTargetName, *events: TriggerEvent):
        return trigger(
            timing='AFTER',
            events=events or ('INSERT', 'DELETE', 'UPDATE'), # default to all events
            statement=newlines_to_spaces("""
                supabase_functions.http_request(
                    '{}',
                    'POST',
                    '{{{{"Content-Type":"application/json"}}}}',
                    '{{{{}}}}',
                    '1000'
            )""".format(
                os.getenv(
                    ( env_name := f'WEBHOOK_TARGET_{name.upper()}' )
                ) or throw(f'{env_name} is not set')
            )),
        )
    
webhook = WebhookDecorator[str]() # the simplest case if you don't want to type the target name