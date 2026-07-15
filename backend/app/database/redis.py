import redis
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
    socket_timeout=0.2,          
    socket_connect_timeout=0.2,  
    retry_on_timeout=False
)

#Mail handler
async def mail_send(email) -> bool:
    redis_email = f"email:{email}"
    return await _redis_client.set(redis_email, "true", ex=18000)

async def is_mail_send(email) -> bool:
    redis_key = f"email:{email}"
    return await _redis_client.exists(redis_key)

async def mail_work_done(email) -> bool:
    redis_key = f"email:{email}"
    return await _redis_client.delete(redis_key)