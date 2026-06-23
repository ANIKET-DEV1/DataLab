from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from sqlalchemy.exc import DataError, IntegrityError, SQLAlchemyError
from ..models import models
from ..schemas import dataset 
from uuid import UUID

# async def add_dataset(db:AsyncSession,dataset:dataset,user_id:UUID):
#     try:
        