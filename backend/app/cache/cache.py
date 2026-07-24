import io
import os
from pathlib import Path
import aiofiles
import pandas as pd
from cachetools import TTLCache
from starlette.concurrency import run_in_threadpool

from ..core.config import get_config, APP_DIR
from ..core.supabase import get_supabase_client


df_ram_cache = TTLCache(maxsize=20, ttl=900)

DISK_CACHE_DIR = APP_DIR / "storage" 
DISK_CACHE_DIR.mkdir(parents=True, exist_ok=True)


class DatasetCacheService:
    @staticmethod
    async def get_dataframe(file_path: str, file_type: str) -> pd.DataFrame:
        config = get_config()

        if config.ENV.upper() == "DEVELOPMENT":
            df = await run_in_threadpool(DatasetCacheService._read_df_from_disk, file_path, file_type)
            df_ram_cache[file_path] = df
            return df

       
        safe_filename = file_path.replace("/", "_")
        local_cached_path = DISK_CACHE_DIR / safe_filename

        if not local_cached_path.exists():
            supabase = get_supabase_client()
            def sync_download():
                return supabase.storage.from_(config.SUPABASE_BUCKET).download(file_path)

            file_bytes = await run_in_threadpool(sync_download)

        buffer = io.BytesIO(file_bytes)
        df = await run_in_threadpool(DatasetCacheService._parse_buffer, buffer, file_type)

        
        df_ram_cache[file_path] = df
        return df
    
    @staticmethod
    def invalidate(file_path: str) -> None:
        if file_path in df_ram_cache:
            del df_ram_cache[file_path]

    @staticmethod
    def _read_df_from_disk(path: str, file_type: str) -> pd.DataFrame:
        ext = file_type.lower()
        if ext == "csv":
            return pd.read_csv(path)
        elif ext in ("xlsx", "xls"):
            return pd.read_excel(path)
        elif ext == "json":
            return pd.read_json(path)
        raise ValueError(f"Unsupported file format: {file_type}")

    @staticmethod
    def _parse_buffer(buffer: io.BytesIO, file_type: str) -> pd.DataFrame:
        ext = file_type.lower()
        if ext == "csv":
            return pd.read_csv(buffer)
        elif ext in ("xlsx", "xls"):
            return pd.read_excel(buffer)
        elif ext == "json":
            return pd.read_json(buffer)
        
        raise ValueError(f"Unsupported file format: {file_type}")

    @staticmethod
    def update_cache(file_path: str, new_df: pd.DataFrame) -> None:
        df_ram_cache[file_path] = new_df