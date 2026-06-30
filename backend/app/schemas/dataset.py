from pydantic import BaseModel, Field, SecretStr
import uuid
from uuid import UUID
from fastapi import HTTPException,status
from datetime import datetime
from ..models.models import Dataset,FileType
class BaseSchema(BaseModel):
    model_config = {"from_attributes": True}

class Dataset(BaseModel):
    original_name: str = Field(...,min_length=2, nullable=False)
    file_type:FileType=Field(...)
    
class DatasetResponse(BaseSchema):
    id: UUID
    original_name: str 
    file_path:str
    file_type:FileType
    file_size_bytes:int
    last_accessed_at:datetime
    created_at:datetime

class StorageStatusResponse(BaseModel):
    storage_used_bytes: int
    storage_limit_bytes: int
    storage_used_mb: float
    storage_remaining_mb: float
    percentage_used: float