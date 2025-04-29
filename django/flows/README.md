# Flows App

The Flows app provides asynchronous task processing capabilities for the Unfindables project.

## Task Model

The `Task` abstract model allows you to create awaitable Django models that can be used in async context.

### Features

- Create models that can be awaited in async functions
- Results are stored in Redis for retrieval
- Auto-run behavior can be controlled with the `no_auto_run` flag

### Usage Example

```python
from flows.models import Task

class ScrapeWebsite(Task):
    url = models.URLField()
    result_data = models.JSONField(null=True, blank=True)
    
    async def task_handler(self):
        # Implement your async scraping logic here
        # For example:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                data = await response.json()
                return data
                
# Using the model in async code
async def process_website(url):
    scraper = ScrapeWebsite.objects.create(url=url)
    
    # Option 1: Use as an awaitable
    result = await scraper
    
    # Option 2: Explicitly run the task
    # await scraper.run()
    
    return result
```

### Redis Configuration

The Task model uses Redis for storing task results. It leverages the asyncio support built into the redis-py package (version 4.2.0+). Make sure the following settings are configured in your Django settings:

```python
AWAITABLE_TASK_REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
```

Note: Starting from redis-py 4.2.0, the asyncio Redis client previously provided by the separate aioredis package is now integrated into redis-py. We use `from redis import asyncio as aioredis` to maintain compatibility with code that may have used the standalone aioredis package. 