from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from ..core.config import get_config

settings = get_config()
db_url = settings.DATABASE_URL.get_secret_value()
if "localhost" in db_url or "127.0.0.1" in db_url or "@db" in db_url:
    connect_args = {}
else:
    connect_args = {"ssl": True}

engine = create_async_engine(db_url,
                             connect_args=connect_args)


AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass