"""FastAPI dependencies for authentication and database sessions."""

import os
from typing import Annotated

import httpx
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlmodel.ext.asyncio.session import AsyncSession

from database import get_session

load_dotenv()

security = HTTPBearer()

BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")
JWKS_URL = f"{BETTER_AUTH_URL}/api/auth/jwks"

# Cache for JWKS keys
_jwks_cache: dict | None = None


async def get_jwks() -> dict:
    """Fetch JWKS from Better Auth endpoint with caching."""
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(JWKS_URL)
            response.raise_for_status()
            _jwks_cache = response.json()
            return _jwks_cache
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Unable to fetch JWKS: {str(e)}",
            )


def clear_jwks_cache() -> None:
    """Clear the JWKS cache (useful for testing or key rotation)."""
    global _jwks_cache
    _jwks_cache = None


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    """Dependency that validates JWT token and returns the current user ID.

    Args:
        credentials: Bearer token from Authorization header.

    Returns:
        User ID string from Better Auth.

    Raises:
        HTTPException: If token is invalid.
    """
    token = credentials.credentials

    try:
        # Fetch JWKS and verify token
        jwks = await get_jwks()

        # Decode and verify the JWT
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256", "ES256"],
            options={"verify_aud": False},
        )

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Type alias for dependency injection
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
DbSession = Annotated[AsyncSession, Depends(get_session)]
