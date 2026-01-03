# alembic/env.py

import asyncio
import os
from logging.config import fileConfig

from sqlalchemy import pool, MetaData
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# ✅ 1. Импортируем ВСЕ модели ДО использования SQLModel.metadata
# Это гарантирует, что все таблицы зарегистрированы
from app.sqlmodels import (
    RecordLabel,
    Person,
    Artist,
    ArtistPerson,
    Album,
    AlbumArtist,
    Track,
    TrackArtist,
    TrackPersonShare,
)
from app.sqlmodels.user import User

# ✅ 2. Импортируем SQLModel ПОСЛЕ моделей
from sqlmodel import SQLModel

# this is the Alembic Config object
config = context.config
fileConfig(config.config_file_name)

# ✅ 3. Создаём target_metadata на основе SQLModel.metadata
target_metadata = MetaData()

# Копируем все таблицы из SQLModel.metadata
for table in SQLModel.metadata.tables.values():
    table.to_metadata(target_metadata)

# Получаем DATABASE_URL из .env
from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в .env")

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    """Run migrations in 'online' mode."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """In this scenario we need to create an Engine
    and associate a connection with the context."""

    connectable = create_async_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online():
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()