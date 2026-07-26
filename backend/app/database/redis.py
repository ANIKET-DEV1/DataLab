from redis.asyncio import Redis
import logging
import redis
from redis.exceptions import RedisError  
logger = logging.getLogger("database")
from ..core.config import get_config

system = get_config()

_redis_client = Redis.from_url(
    system.REDIS_URL,
    decode_responses=True,
    socket_timeout=1,             
    socket_connect_timeout=1,
    health_check_interval=30,       
    retry_on_error=[ConnectionError, TimeoutError],
)

#Mail handler
async def mail_send(email) -> bool:
    redis_email = f"datalab_email:{email}"
    return await _redis_client.set(redis_email, "true", ex=18000)

async def is_mail_send(email) -> bool:
    redis_key = f"datalab_email:{email}"
    return await _redis_client.exists(redis_key)

async def mail_work_done(email) -> bool:
    redis_key = f"datalab_email:{email}"
    return await _redis_client.delete(redis_key)