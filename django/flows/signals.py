from django.db.models.signals import post_save
from django.dispatch import receiver
import asyncio

def register_task_signals(task_model):
    """
    Register post_save signal for a Task model subclass.
    Call this function for each concrete Task model you create.
    """
    @receiver(post_save, sender=task_model)
    def task_post_save(sender, instance, created, **kwargs): # pyright: ignore[reportUnusedFunction]
        if created and not instance.no_auto_run:
            # Find the running event loop or create a new one
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            # Schedule the task to run
            if loop.is_running():
                asyncio.create_task(instance.run())
            else:
                loop.run_until_complete(instance.run()) 