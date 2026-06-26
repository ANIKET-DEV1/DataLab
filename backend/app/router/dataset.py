from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, status
from fastapi.responses import JSONResponse

from ..database.session import AsyncSession, get_db
from ..models.models import User
from ..repository.dataset import DatasetRepository
from .deps import get_current_user   # adjust to your auth dep


router = APIRouter(prefix="/datasets", tags=["datasets"])


def get_repo(db: AsyncSession = Depends(get_db)) -> DatasetRepository:
    return DatasetRepository(db)


# ── Upload ────────────────────────────────────────────────────────────────────

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    repo: DatasetRepository = Depends(get_repo),
):
    """Upload a CSV, XLSX, or PDF dataset for the authenticated user."""
    return await repo.add_dataset(file, current_user)


# ── List ──────────────────────────────────────────────────────────────────────

@router.get("/", status_code=status.HTTP_200_OK)
async def list_datasets(
    current_user: User = Depends(get_current_user),
    repo: DatasetRepository = Depends(get_repo),
):
    """Return all datasets owned by the authenticated user."""
    datasets = await repo.get_user_datasets(current_user.id)
    return [
        {
            "dataset_id": str(ds.id),
            "original_name": ds.original_name,
            "file_type": ds.file_type.value,
            "file_size_mb": round(ds.file_size_bytes / 1_048_576, 2),
        }
        for ds in datasets
    ]


# ── Delete ────────────────────────────────────────────────────────────────────

@router.delete("/{dataset_id}", status_code=status.HTTP_200_OK)
async def delete_dataset(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: DatasetRepository = Depends(get_repo),
):
    """Delete a dataset by ID (owner only)."""
    return await repo.delete_dataset(dataset_id, current_user)