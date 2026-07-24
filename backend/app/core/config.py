from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import DirectoryPath, Field, SecretStr
from functools import lru_cache
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent


class AppConfig(BaseSettings):
    app_name: str
    base_url: str
    ENV: str 
    DATABASE_URL: SecretStr
    SUPABASE_URL: str
    SUPABASE_KEY: SecretStr 
    SUPABASE_BUCKET: str = "datasets"
    secret_key: SecretStr
    algorithms: str
    ACCESS_TOKEN_EXPIRE_MINUTE: int
    REDIS_URL: str
    redis_port: int
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class NotificationConfig(BaseSettings):
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    TEMPLATE_FOLDER: DirectoryPath = APP_DIR / "templates/emails"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_config() -> AppConfig:
    return AppConfig()


@lru_cache
def mail_config() -> NotificationConfig:
    return NotificationConfig()


@lru_cache
def get_storage_config() -> dict:
    config = get_config()
    local_storage_path = APP_DIR / "storage"
    
    if config.ENV.upper() == "DEVELOPMENT":
        local_storage_path.mkdir(parents=True, exist_ok=True)  

    return {
        "ENV": config.ENV.upper(),
        "LOCAL_STORAGE_DIR": str(local_storage_path),
        "SUPABASE_URL": config.SUPABASE_URL,
        "SUPABASE_KEY": config.SUPABASE_KEY.get_secret_value(),
        "SUPABASE_BUCKET": config.SUPABASE_BUCKET,
    }