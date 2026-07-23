from pydantic import BaseModel, Field, SecretStr, model_validator
import uuid
from uuid import UUID
from datetime import datetime

from enum import Enum
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

class chart(str, Enum):
    bar = 'bar'
    pie = 'pie'
    hist = 'hist'
    line = 'line'
    scatter = 'scatter'

class DatasetVisualized(BaseModel):
    chart_type:chart 
    x_column:str
    y_column:str | None = None

class CleanStrategy(str, Enum):
    fill_na = 'fill-na'
    drop_na = 'drop-na'

class FillStrategy(str, Enum):
    mean = 'mean'
    mode = 'mode'
    custom = 'custom'  

class ColumnWiseClean(BaseModel):
    column_name: str
    clean_type: CleanStrategy
    fill_type: FillStrategy | None = None
    custom_fill_value: str | None = None

    @model_validator(mode='after')
    def validate_conditional_fill_parameters(self) -> 'ColumnWiseClean':
        if self.clean_type == CleanStrategy.fill_na:
            if not self.fill_type:
                raise ValueError("Validation Error: 'fill_type' is strictly required when 'clean_type' is set to 'fill-na'.")
            
          
            if self.fill_type == FillStrategy.custom and (self.custom_fill_value is None or str(self.custom_fill_value).strip() == ""):
                raise ValueError("Validation Error: You selected a 'custom' fill strategy, but left the custom fill value blank.")
        
        return self

from typing import Optional, Literal

class overallclean(BaseModel):
    clean_type: CleanStrategy
    axis: Optional[Literal[0, 1]] = None
    custom_fill_value: Optional[str] = None

    @model_validator(mode='after')
    def validate_overall_clean_logic(self) -> 'overallclean':
        if self.clean_type == CleanStrategy.fill_na:
            if self.custom_fill_value is None or str(self.custom_fill_value).strip() == "":
                raise ValueError("Validation Error: custom value is strictly required when 'clean_type' is set to 'fill-na'.")
        
        if self.clean_type == CleanStrategy.drop_na:
            if self.axis is None:
                raise ValueError("Validation Error: Axis is strictly required when 'drop-na' Selected.")
        
        return self
    

class renameColumn(BaseModel):
    old_column:str 
    new_name_columns:str 