from functools import lru_cache
from supabase import create_client, Client
from backend.app.core.config import get_config
@lru_cache
def get_supabase_client() -> Client:
    config = get_config()
    
    api_key = (
        config.SUPABASE_KEY.get_secret_value()
        if hasattr(config.SUPABASE_KEY, "get_secret_value")
        else config.SUPABASE_KEY
    )
    
    return create_client(config.SUPABASE_URL, api_key)
