"""Async database connection for Neon PostgreSQL."""

import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Ensure we're using asyncpg driver
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# Remove sslmode from URL as asyncpg uses ssl parameter in connect_args
clean_url = DATABASE_URL.split("?")[0]

engine = create_async_engine(
    clean_url,
    echo=True,
    future=True,
    connect_args={"ssl": "require"},
    # Connection pool settings for Neon PostgreSQL (serverless)
    # Neon closes idle connections after ~5 minutes
    pool_pre_ping=True,  # Test connection before using (handles closed connections)
    pool_recycle=280,  # Recycle connections every ~4.5 minutes (before Neon timeout)
    pool_size=5,  # Maintain 5 connections in pool
    max_overflow=10,  # Allow up to 10 additional connections under load
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session."""
    async with async_session() as session:
        yield session


async def create_db_and_tables() -> None:
    """Create all database tables from SQLModel metadata."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
