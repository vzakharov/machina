from typing import Generic, TypeVar

from utils.env import get_required_env

from .models import trigger
from .types import TriggerEvent

TTargetName = TypeVar('TTargetName', bound=str)

class WebhookDecorator(Generic[TTargetName]):
    
    def __call__(self, name: TTargetName, *events: TriggerEvent):
        return trigger(
            timing='AFTER',
            events=events or ('INSERT', 'DELETE', 'UPDATE'), # default to all events
            statement=(
                f"supabase_functions.http_request("
                f"'{get_required_env(f'WEBHOOK_TARGET_{name.upper()}')}',"
                f" 'POST',"
                f" '{{{{\"Content-Type\":\"application/json\"}}}}',"
                f" '{{{{}}}}', '1000')"
            )
        )
    
webhook = WebhookDecorator[str]() # the simplest case if you don't want to type the target name