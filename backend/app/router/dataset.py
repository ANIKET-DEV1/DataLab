import os
from uuid import UUID
from fastapi import APIRouter, Depends, Request, UploadFile, File, status, Response
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates
from ..database.session import AsyncSession, get_db
from ..models.models import User,Dataset
from ..repository.dataset import DatasetRepository
from starlette.concurrency import run_in_threadpool
from ..dependencies.deps import get_current_user ,get_verified_user_dataset,APP_DIR
from ..schemas.dataset import ColumnWiseClean, DatasetVisualized ,overallclean, renameColumn
from ..service import data_engine
from ..middleware.rate_limiting import limiter
from ..exceptions_handler.handle_expection import DatasetNotFound, ValidationError, DataProcessingError, DataLabExceptionHandler

router = APIRouter(prefix="/datasets", tags=["datasets"])
templates = Jinja2Templates(directory=APP_DIR/"frontend/templates")

def get_repo(db: AsyncSession = Depends(get_db)) -> DatasetRepository:
    return DatasetRepository(db)


# ── Upload ────────────────────────────────────────────────────────────────────

@router.post("/upload", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_dataset(
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    repo: DatasetRepository = Depends(get_repo),
):
    """Upload a CSV, XLSX, or PDF dataset for the authenticated user."""
    return await repo.add_dataset(file, current_user)


# ── List ──────────────────────────────────────────────────────────────────────

@router.get("/list", status_code=status.HTTP_200_OK)
@limiter.limit("60/minute")
async def get_datasets_json(
    request: Request,
    response: Response,
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
@limiter.limit("10/minute")
async def delete_dataset(
    request: Request,
    response: Response,
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
            raise DatasetNotFound("Dataset preview is unavailable.")
        return data
    except DataLabExceptionHandler:
        raise
    except Exception as e:
        raise DataProcessingError(f"Failed to parse dataset preview: {str(e)}")
            
   

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
            raise DatasetNotFound("Dataset visualization data is unavailable.")
        return graph_data
    except DataLabExceptionHandler:
        raise
    except Exception as e:
        raise DataProcessingError(f"Failed to generate dataset visualization: {str(e)}")
     
@router.get("/columns")
async def columns(
    request:Request,
    dataset: Dataset = Depends(get_verified_user_dataset)
):
    try:
        data = await run_in_threadpool(
            data_engine.data_engine_columns,
            dataset=dataset,
        )
        if not data:
            raise DatasetNotFound("Dataset column metadata is unavailable.")
        return data
    except DataLabExceptionHandler:
        raise
    except Exception as e:
        raise DataProcessingError(f"Failed to fetch dataset column details: {str(e)}")
     
@router.post("/column-clean")
@limiter.limit("20/minute")
async def column_clean(
    request:Request,
    response: Response,
    ColumnWiseClean: ColumnWiseClean,
    dataset: Dataset = Depends(get_verified_user_dataset),
    ):
    try:
        data = await run_in_threadpool(
            data_engine.column_wise_clean,
            dataset=dataset,
            payload=ColumnWiseClean
        )
        if not data:
            raise ValidationError("No data returned from column cleaning operation.")
        return data
    except DataLabExceptionHandler:
        raise
    except Exception as e:
        raise DataProcessingError(f"Failed to clean dataset column: {str(e)}")
   
@router.post("/overall-clean")
@limiter.limit("20/minute")
async def apply_on_all(
    request:Request,
    response: Response,
    overall_clean_data: overallclean,
    dataset: Dataset = Depends(get_verified_user_dataset),
):
    try:
        data = await run_in_threadpool(
            data_engine.overall_clean,
            dataset=dataset,
            payload=overall_clean_data
        )
        if not data:
            raise ValidationError("No data returned from overall cleaning operation.")
        return data
    except DataLabExceptionHandler:
        raise
    except Exception as e:
        raise DataProcessingError(f"Failed to apply overall dataset cleaning: {str(e)}")
   
@router.post("/rename-column")
@limiter.limit("20/minute")
async def rename_col(
    request:Request,
    response: Response,
    rename_columns: renameColumn,
    dataset: Dataset = Depends(get_verified_user_dataset),
):
    try:
        data= await run_in_threadpool(
            data_engine.rename_column,
            dataset= dataset,
            payload=rename_columns
        )
        if not data:
            raise ValidationError("No data returned from rename column operation.")
        return data
    except DataLabExceptionHandler:
        raise
    except Exception as e:
        raise DataProcessingError(f"Failed to rename dataset column: {str(e)}")
   
def iterate_file_chunks(file_path: str, chunk_size: int = 4096):
    with open(file_path, mode="rb") as file_like:
        while (chunk := file_like.read(chunk_size)):
            yield chunk

@router.get("/download")
async def download_dataset(
    request:Request,
    dataset: Dataset = Depends(get_verified_user_dataset)
    ):
    
    if not dataset:
        raise DatasetNotFound("Dataset not found")
        
    if not os.path.exists(dataset.file_path):
        raise DatasetNotFound("Physical file missing on server")

    return StreamingResponse(
        iterate_file_chunks(dataset.file_path),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={dataset.original_name}"
        }
    )