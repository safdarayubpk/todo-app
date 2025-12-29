# FastAPI Patterns Reference

## JWT Authentication Dependency

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlmodel.ext.asyncio.session import AsyncSession

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    """Extract and validate current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await session.get(User, int(user_id))
    if user is None:
        raise credentials_exception
    return user
```

## Async Database Session

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost/db"

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncSession:
    """Yield async database session."""
    async with async_session() as session:
        yield session
```

## User Isolation Pattern

```python
# Always filter by current_user.id
async def get_user_tasks(
    session: AsyncSession,
    user_id: int
) -> list[Task]:
    """Get tasks belonging to specific user."""
    statement = select(Task).where(Task.user_id == user_id)
    result = await session.exec(statement)
    return result.all()
```

## Error Handling Patterns

```python
# 404 Not Found
def get_or_404(item, detail: str = "Item not found"):
    if item is None:
        raise HTTPException(status_code=404, detail=detail)
    return item

# 403 Forbidden (ownership check)
def check_ownership(item, user_id: int):
    if item.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
```

## Response Status Codes

| Operation | Success Code | Description |
|-----------|--------------|-------------|
| GET (list) | 200 OK | Return list of items |
| GET (single) | 200 OK | Return single item |
| POST | 201 Created | Item created |
| PUT/PATCH | 200 OK | Item updated |
| DELETE | 204 No Content | Item deleted |

## Pagination Pattern

```python
from fastapi import Query

@router.get("/tasks", response_model=list[TaskRead])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """List tasks with pagination."""
    statement = (
        select(Task)
        .where(Task.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()
```
