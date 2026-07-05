import os
import uuid
import shutil
import aiofiles
from pathlib import Path
from uuid import UUID
from fastapi import UploadFile, HTTPException, status,Depends
from starlette.concurrency import run_in_threadpool
from backend.app.schemas.dataset import DatasetResponse
from backend.app.service.data_engine import data_engine_preview
from ..models.models import Dataset
from ..models.models import User
from ..models.models import FileType
from ..core.config import get_storage_config
from ..database.session import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import query
from ..router.deps import get_current_user



ALLOWED_EXTENSIONS = {FileType.csv.value, FileType.xlsx.value, FileType.json.value}
MAX_CHUNK = 1024 * 1024  


class DatasetRepository:

    def __init__(self, db: AsyncSession):
        self.db = db
        self.config = get_storage_config()

    
    async def add_dataset(self, file: UploadFile, current_user: User) -> dict:

        parts = (file.filename or "").rsplit(".", 1)
        if len(parts) < 2 or parts[-1].lower() not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        ext = parts[-1].lower()

        content = await file.read()
        file_size_bytes = len(content)

        if current_user.storage_used_bytes + file_size_bytes > current_user.storage_limit_bytes:
            remaining = current_user.storage_limit_bytes - current_user.storage_used_bytes
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Storage full. You have {remaining / 1_048_576:.1f} MB remaining. Delete a dataset first."
            )

        unique_filename = f"{uuid.uuid4()}.{ext}"
        env = self.config["ENV"]

        if env == "DEVELOPMENT":
            file_path = await self._save_local(content, unique_filename, current_user.id)
        else:
            file_path = await self._save_cloud(content, unique_filename, current_user.id)

        try:
            new_dataset = Dataset(
                owner_id=current_user.id,
                original_name=file.filename,
                file_path=file_path,
                file_type=FileType(ext),
                file_size_bytes=file_size_bytes,
            )
            current_user.storage_used_bytes += file_size_bytes

            self.db.add(new_dataset)
            await self.db.commit()
            await self.db.refresh(new_dataset)

        except Exception as e:
            await self._cleanup_on_failure(file_path, env)
            await self.db.rollback()
            raise HTTPException(status_code=500, detail="Failed to save dataset record.")

        return {
            "message": f"'{file.filename}' uploaded successfully.",
            "dataset_id": str(new_dataset.id),
            "original_name": new_dataset.original_name,
            "file_type": ext,
            "file_size_mb": round(file_size_bytes / 1_048_576, 2),
            "storage_used_mb": round(current_user.storage_used_bytes / 1_048_576, 2),
            "storage_limit_mb": round(current_user.storage_limit_bytes / 1_048_576, 2),
        }

    # ── private helpers ──────────────────────────────────────────

    async def _save_local(self, content: bytes, filename: str, user_id: UUID) -> str:
        user_folder = Path(self.config["LOCAL_STORAGE_DIR"]) / str(user_id)
        user_folder.mkdir(parents=True, exist_ok=True)
        target = user_folder / filename

        async with aiofiles.open(target, "wb") as f:
            await f.write(content)

        return str(target)

    # async def _save_cloud(self, content: bytes, filename: str, user_id: UUID) -> str:
        # import boto3, io
        # s3 = boto3.client(
        #     "s3",
        #     endpoint_url=self.config["SUPABASE_URL"],
        #     aws_access_key_id=self.config["SUPABASE_KEY"],
        #     aws_secret_access_key=self.config["SUPABASE_SECRET"],
        # )
        # key = f"{user_id}/{filename}"
        # try:
        #     s3.upload_fileobj(io.BytesIO(content), self.config["SUPABASE_BUCKET"], key)
        # except Exception:
        #     raise HTTPException(status_code=500, detail="Cloud upload failed.")
        # return key

    async def _cleanup_on_failure(self, file_path: str, env: str) -> None:
        if env == "DEVELOPMENT":
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            pass  # add S3 delete here if needed

    async def get_user_datasets(self, user_id: UUID) -> list[DatasetResponse]:
        from sqlalchemy import select
        result = await self.db.execute(
            select(Dataset).where(Dataset.owner_id == user_id)
        )
        datasets = result.scalars().all()
        if not datasets:
            return []
        return [DatasetResponse.model_validate(d) for d in datasets]
    

    async def delete_dataset(self, dataset_id: UUID, current_user: User) -> dict:
        result = await self.db.execute(
            select(Dataset).where(Dataset.id == dataset_id, Dataset.owner_id == current_user.id)
        )
        dataset = result.scalar_one_or_none()

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found.")

        env = self.config["ENV"]
        await self._cleanup_on_failure(dataset.file_path, env)

        current_user.storage_used_bytes -= dataset.file_size_bytes
        await self.db.delete(dataset)
        await self.db.commit()

        return {"message": f"'{dataset.original_name}' deleted. Storage freed."}


    