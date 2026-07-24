import os # Make sure os is imported up top!
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# 1. This is the Alembic Config object
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from backend.app.database.base import Base
from backend.app.models.models import User, Dataset
target_metadata = Base.metadata

from backend.app.core.config import get_config
system = get_config()

# === 🌟 FIX START: Overwrite localhost with the docker environment URL if inside a container ===
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = system.DATABASE_URL.get_secret_value()

# If it's still pointing to localhost inside docker, gracefully re-route it to the 'db' service container
if "localhost" in DATABASE_URL or "127.0.0.1" in DATABASE_URL:
    # This automatically swaps localhost -> db inside the container
    DATABASE_URL = DATABASE_URL.replace("localhost", "db").replace("127.0.0.1", "db")

# Clean up query params (like cloud sslmode flags) that break local engine connections
if "?" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.split("?")[0]
# === FIX END ===

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an Async Engine."""
    # Use our newly cleaned and fixed global DATABASE_URL variable!
    current_url = DATABASE_URL
    
    if "localhost" in current_url or "127.0.0.1" in current_url or "@db" in current_url or "db" in current_url:
        connect_args = {}
    else:
        connect_args = {"ssl": False}

    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        connect_args=connect_args
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())