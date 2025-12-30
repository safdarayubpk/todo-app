"""FastAPI application entry point."""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_db_and_tables, engine
from app.schemas import HealthResponse

# Import models to register them with SQLModel before creating tables
# All models now exported from app.models package
from app.models import Task, Conversation, Message  # noqa: F401

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler - creates tables on startup."""
    # Startup: Create database tables
    await create_db_and_tables()
    yield
    # Shutdown: Close database connections
    await engine.dispose()


app = FastAPI(
    title="Todo App API",
    description="RESTful API for multi-user task management",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint - returns service health status."""
    return HealthResponse(status="healthy", database="connected")


# Import and include routers
from app.routes import tasks_router
from app.chatkit import chatkit_router

app.include_router(tasks_router, prefix="/api/v1")
app.include_router(chatkit_router)
