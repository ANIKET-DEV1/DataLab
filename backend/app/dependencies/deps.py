# Dependices like get user and all.
from datetime import timezone
from pathlib import Path
from fastapi import Depends, Request, status

from ..security.jwt_handler import verify_token
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.session import get_db
from pathlib import Path

from ..models.models import User,Dataset
from ..exceptions_handler.handle_expection import ClientNotAuthorized, UserNotFound, DatasetNotFound

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise ClientNotAuthorized("Authentication credentials missing")

    token_data = await verify_token(token)

    try:
        user_uuid = uuid.UUID(str(token_data.user_id))
    except ValueError:
        raise ClientNotAuthorized("Invalid user identifier structure")

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if user and user.logged_out_at:
        db_logout_time = int(user.logged_out_at.replace(tzinfo=timezone.utc).timestamp())
        
        if token_data.time < db_logout_time:
            raise ClientNotAuthorized("This session was manually ended.")
        
    if user is None:
        raise UserNotFound("User account no longer exists")
        
    return user

async def get_verified_user_dataset(
        dataset_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
        ) -> Dataset:
        
        result = await db.execute(
            select(Dataset).where(
                Dataset.owner_id == current_user.id,
                Dataset.id==dataset_id
                )
        )
        dataset= result.scalar_one_or_none()
        
        if not dataset:
            raise DatasetNotFound("Dataset not found or you do not have permission to access it.")
            
        return dataset

  
APP_DIR = Path(__file__).resolve().parent.parent.parent.parent
