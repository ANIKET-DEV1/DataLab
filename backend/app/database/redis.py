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
#logout
async def add_jti_to_blacklist(jti: str):
    return await _redis_client.set(f"blacklist:{jti}", "blacklisted")

async def is_jti_in_blacklist(jti: str) -> bool:
    if not jti:
        return False  
    try:
        return await _redis_client.exists(f"blacklist:{jti}")   
    except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError, redis.exceptions.RedisError) as e:
        logger.error(f"UPSTASH OUTAGE DETECTED: Returning fallback False for JTI check. Details: {e}")
        return False

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