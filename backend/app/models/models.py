import uuid
import enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func, Text, String, Integer, ForeignKey, Boolean, UUID,Enum
from ..database.base import Base

class FileType(str, enum.Enum):
    csv = "csv"
    json = "json"
    xlsx = "xlsx"

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
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False, 
        server_default="false", 
        nullable=False
        )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        server_default="true",
        nullable=False
        )
    storage_used_bytes: Mapped[int] = mapped_column(
        Integer, 
        default=0, 
        server_default="0", 
        nullable=False
        )
    storage_limit_bytes: Mapped[int] = mapped_column(
        Integer,
        default=52428800,
        server_default="52428800", 
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)

    datasets: Mapped[list["Dataset"]] = relationship("Dataset", back_populates="owner", cascade="all, delete-orphan")


class Dataset(Base):
    __tablename__ = "datasets"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    file_type: Mapped[FileType] = mapped_column(
        Enum(FileType, name="file_type_enum", 
             values_callable=lambda x: [e.value for e in x]), 
        nullable=False
    )
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    last_accessed_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="datasets")