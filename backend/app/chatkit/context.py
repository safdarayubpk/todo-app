"""Request context handler for ChatKit authentication.

Provides JWT-based session management for user isolation in chat operations.
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, Request


# Get secret key from environment
CHATKIT_SECRET_KEY = os.getenv("CHATKIT_SECRET_KEY", "default-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 1


@dataclass
class RequestContext:
    """Context for a chat request containing user information."""

    user_id: str

    def __post_init__(self):
        if not self.user_id:
            raise ValueError("user_id is required")


def create_client_secret(user_id: str) -> str:
    """Create a signed JWT client_secret for ChatKit authentication.

    Args:
        user_id: The authenticated user's ID

    Returns:
        Signed JWT token containing user_id
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(hours=TOKEN_EXPIRY_HOURS),
        "iss": "todoapp-chatkit",
    }
    return jwt.encode(payload, CHATKIT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def validate_client_secret(token: str) -> str | None:
    """Validate a client_secret JWT and extract user_id.

    Args:
        token: The JWT token to validate

    Returns:
        The user_id if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            CHATKIT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM],
            options={"require": ["sub", "exp", "iat"]},
        )
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_context_from_request(request: Request) -> RequestContext:
    """Extract RequestContext from a FastAPI request.

    Validates the Authorization header and creates a RequestContext.

    Args:
        request: The incoming FastAPI request

    Returns:
        RequestContext with user_id

    Raises:
        HTTPException: If authorization is missing or invalid
    """
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header. Expected: Bearer <token>"
        )

    token = auth_header.replace("Bearer ", "")
    user_id = validate_client_secret(token)

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired client secret"
        )

    return RequestContext(user_id=user_id)
