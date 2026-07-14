# JWT 
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Request, logger, status, Response
import logging
import redis
from redis.exceptions import ConnectionError, TimeoutError, RedisError
from ..models.models import User
from datetime import datetime, timedelta, timezone
from ..schemas.token import TokenData
from ..core.config import get_config

logger = logging.getLogger("auth_engine")
system = get_config()
SECRET_KEY = system.secret_key.get_secret_value()
ALGORITHM = system.algorithms


def create_access_token(data: dict, expires_delta: timedelta = timedelta(days=7)) -> str:
    now = datetime.now(timezone.utc)
    encoded_jwt = jwt.encode(
        {
            **data,
            'iat': int(now.timestamp()),
            "exp": datetime.now(timezone.utc) + expires_delta
        },
        key=SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt

async def verify_token(token: str) -> TokenData:
    try:  
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        verified:bool | None =payload.get("verified")
        iat: int | None = payload.get("iat")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token or expired session"
            )
        if not verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please verify Email. Check Your Mail"
            )

        return TokenData(user_id=user_id,
                         time=iat)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired session"
        )

def set_auth_cookies(response: Response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,  
        samesite="none", 
        max_age=system.ACCESS_TOKEN_EXPIRE_MINUTE * 60,
    )


# Dependency guard to identify the user based on incoming cookies
