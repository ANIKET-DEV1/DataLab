# Dependices like get user and all.
from datetime import timezone
from pathlib import Path
from fastapi import Depends, HTTPException, Request, status

from ..security.jwt_handler import verify_token
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.session import get_db
from pathlib import Path

from ..models.models import User,Dataset
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials missing"
        )

    token_data = await verify_token(token)

    try:
        user_uuid = uuid.UUID(str(token_data.user_id))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier structure"
        )

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if user.logged_out_at:
        db_logout_time = int(user.logged_out_at.replace(tzinfo=timezone.utc).timestamp())
        
        if token_data.time < db_logout_time:
            raise HTTPException(status_code=401, detail="This session was manually ended.")
        
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists"
        )
        
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Dataset not found or you do not have permission to access it."
            )
            
        return dataset

  
APP_DIR = Path(__file__).resolve().parent.parent.parent.parent
