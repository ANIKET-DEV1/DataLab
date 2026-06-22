from sqlalchemy.orm import Mapped,mapped_column
import uuid
import enum
from datetime import datetime, date
from typing import List
from decimal import Decimal
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import  func, Text, String, UUID, Integer, ForeignKey, Enum,Boolean

from ..database.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    username: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False
    )
    password: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )
    verified_status:Mapped[bool]=mapped_column(
        Boolean,
        default=False,
        server_default="false",
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=func.now()
    )
    
    # --- RELATIONSHIPS (All perfectly synced) ---
    datasets = relationship(
        "Dataset", 
        back_populates="owner", 
        cascade="all, delete-orphan",
        lazy="selectin"  
    )
    


class Dataset(Base):
    __tablename__ = "datasets"

    id : Mapped[UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
        )

    owner_id: Mapped[UUID]= mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
        )

    original_name: Mapped[str] = mapped_column(String(255), nullable=False)

    file_path: Mapped[str] = mapped_column(String(512), nullable=False)  

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), 
        onupdate=func.now()
    )

    owner = relationship("User", back_populates="datasets")