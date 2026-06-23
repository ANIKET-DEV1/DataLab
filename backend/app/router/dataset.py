from fastapi import APIRouter, Depends, HTTPException, Query, Request,Response,status
from typing import Annotated
from .deps import get_current_user, get_current_user_with_jti
from ..database.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..repository.user import update_verify_email,update_password
from ..service.authRepo import for_Auth
from ..database.redis import add_jti_to_blacklist
from ..models import models
from ..schemas import dataset
from ..service.dataset_route_handler import for_dataset
from ..utils.email_verification import email_verification
from ..utils.password_reset import password_mail_verification

operation = APIRouter(prefix="/dataset", tags=["dataset"])

@operation.post("/upload")
async def add_dataset(baseObj:Annotated[for_dataset,Depends()], 
                dataset:dataset.Dataset,
                current_user:Annotated[models.User, Depends(get_current_user)]):
    
    data = await baseObj.add_dataset(dataset, current_user.id)
    if not data:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error!")

    return data
    



