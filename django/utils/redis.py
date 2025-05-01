import redis.asyncio
from redis import Redis

from django.conf import settings

from utils.functional import ensure_is

REDIS_URL = ensure_is(str, settings.REDIS_URL, "No REDIS_URL found in settings")
REDIS = Redis.from_url(REDIS_URL)
ASYNC_REDIS = redis.asyncio.from_url(REDIS_URL)