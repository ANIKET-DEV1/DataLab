from uuid import UUID
from fastapi import APIRouter, Depends, Request, UploadFile, File, status,HTTPException
from fastapi.templating import Jinja2Templates
from ..database.session import AsyncSession, get_db
from ..models.models import User,Dataset
from ..repository.dataset import DatasetRepository
from starlette.concurrency import run_in_threadpool
from .deps import get_current_user ,get_verified_user_dataset,APP_DIR
from ..schemas.dataset import DatasetVisualized
from ..service import data_engine

router = APIRouter(prefix="/datasets", tags=["datasets"])
templates = Jinja2Templates(directory=APP_DIR/"frontend/templates")

def get_repo(db: AsyncSession = Depends(get_db)) -> DatasetRepository:
    return DatasetRepository(db)


# ── Upload ────────────────────────────────────────────────────────────────────

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    repo: DatasetRepository = Depends(get_repo),
):
    """Upload a CSV, XLSX, or PDF dataset for the authenticated user."""
    return await repo.add_dataset(file, current_user)


# ── List ──────────────────────────────────────────────────────────────────────

@router.get("/list", status_code=status.HTTP_200_OK)
async def get_datasets_json(
    current_user: User = Depends(get_current_user),
    repo: DatasetRepository = Depends(get_repo),
):
    try:
        datasets = await repo.get_user_datasets(current_user.id)
        datasets_data = [d.model_dump(mode='json') for d in datasets]
        response = {
            "datasets": datasets_data,
            "username": current_user.username
        }
        return response
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

@router.get("/view" ,status_code=status.HTTP_200_OK)
async def list_datasets(
    request:Request,
    current_user: User = Depends(get_current_user),
    repo: DatasetRepository = Depends(get_repo),
):
    datasets = await repo.get_user_datasets(current_user.id)
    datasets_dict = [d.model_dump() for d in datasets]
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "data":datasets_dict,
            "username": current_user.username,
            }
    )


@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_dataset(
    dataset_id: UUID,
    current_user: User = Depends(get_current_user),
    repo: DatasetRepository = Depends(get_repo),
):
    return await repo.delete_dataset(dataset_id, current_user)


@router.get("/preview")
async def preview(
    request:Request,
    dataset: Dataset = Depends(get_verified_user_dataset),

):
    try:
        data=await run_in_threadpool(
            data_engine.data_engine_preview,
            dataset=dataset
        )
        if not data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return data
    except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to parse dataset preview: {str(e)}")
            
   

@router.post("/visualize")
async def visualizer(
    request:Request,
    data_visualizer:DatasetVisualized,
    dataset: Dataset = Depends(get_verified_user_dataset)
):
    try:
        graph_data = await run_in_threadpool(
            data_engine.data_engine_visual,
            dataset=dataset,
            payload=data_visualizer
        )
        if not graph_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return graph_data
    except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to parse dataset preview: {str(e)}")
     
@router.get("/columns")
async def columns(
    request:Request,
    dataset: Dataset = Depends(get_verified_user_dataset)
):
    try:
        graph_data = await run_in_threadpool(
            data_engine.data_engine_columns,
            dataset=dataset,
        )
        if not graph_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return graph_data
    except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to parse dataset preview: {str(e)}")
     