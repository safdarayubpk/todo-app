"""Synchronous database session helper for MCP tools.

MCP Server runs in a subprocess with stdio transport, so we need synchronous
database operations. This module provides a sync session for MCP tools.
"""

import os
from contextlib import contextmanager
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlmodel import SQLModel

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Convert to sync URL (psycopg2)
sync_url = DATABASE_URL
if sync_url.startswith("postgresql+asyncpg://"):
    sync_url = sync_url.replace("postgresql+asyncpg://", "postgresql://", 1)
elif sync_url.startswith("postgres://"):
    sync_url = sync_url.replace("postgres://", "postgresql://", 1)

# Remove sslmode from URL and add it to connect_args
clean_url = sync_url.split("?")[0]

# Create synchronous engine for MCP Server
engine = create_engine(
    clean_url,
    echo=False,  # Set to True for debugging
    connect_args={"sslmode": "require"},
    # Connection pool settings for Neon PostgreSQL (serverless)
    pool_pre_ping=True,  # Test connection before using
    pool_recycle=280,  # Recycle connections before Neon timeout
    pool_size=3,  # Smaller pool for subprocess
    max_overflow=5,
)

# Synchronous session factory
SyncSession = sessionmaker(
    engine,
    class_=Session,
    expire_on_commit=False,
)


@contextmanager
def get_sync_session() -> Generator[Session, None, None]:
    """Get a synchronous database session for MCP tools."""
    session = SyncSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
