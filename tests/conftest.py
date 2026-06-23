import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from backend.app.models.models import User
from backend.app.database.base import Base 
from backend.app.app import app
from backend.app.database.session import get_db