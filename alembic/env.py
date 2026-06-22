import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine  # Async engine wrapper
from alembic import context

# 1. This is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2. Correct model metadata parsing imports
from backend.app.database.base import Base

from backend.app.models.models import User,Dataset
target_metadata = Base.metadata


# 3. Dynamic Environment Configuration Parsing
from backend.app.core.config import get_config
system = get_config()
# Extracts your secure async connection string
DATABASE_URL = system.DATABASE_URL.get_secret_value()


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
    """Helper context runner to execute migrations inside the connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an Async Engine."""
    # Create an asynchronous engine explicitly bypassing the .ini hardcoded block
    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Since alembic is synchronous internally, we use run_sync to execute our context runner
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Run the asynchronous online migration function inside the running event loop
    asyncio.run(run_migrations_online())