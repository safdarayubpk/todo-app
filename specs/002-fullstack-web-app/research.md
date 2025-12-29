# Research: Full-Stack Multi-User Web Todo Application

**Feature Branch**: `002-fullstack-web-app`
**Created**: 2025-12-28
**Status**: Complete

## Research Summary

This document consolidates findings from researching the key technologies and patterns needed for Phase II implementation.

---

## 1. Better Auth Integration

### Decision: Use Better Auth with JWT Plugin for Next.js

**Rationale**: Better Auth provides a modern, framework-agnostic authentication solution with built-in JWT support. It integrates seamlessly with Next.js App Router and provides JWKS endpoints for external token verification.

**Alternatives Considered**:
- NextAuth.js: More established but heavier, less flexible for custom JWT flows
- Custom JWT implementation: More work, higher risk of security issues
- Auth0: SaaS dependency, overkill for hackathon scope

### Implementation Pattern

```typescript
// lib/auth.ts - Server configuration
import { betterAuth } from "better-auth"
import { jwt } from "better-auth/plugins"

export const auth = betterAuth({
    database: { /* neon adapter */ },
    plugins: [jwt()]
})

// app/api/auth/[...all]/route.ts - API handler
import { auth } from "@/lib/auth"
import { toNextJsHandler } from "better-auth/next-js"
export const { GET, POST } = toNextJsHandler(auth.handler)

// lib/auth-client.ts - Client configuration
import { createAuthClient } from "better-auth/client"
import { jwtClient } from "better-auth/client/plugins"
export const authClient = createAuthClient({
    plugins: [jwtClient()]
})
```

### Token Retrieval for Backend API

```typescript
// Get JWT token for backend API calls
const { data, error } = await authClient.token()
if (data) {
    const response = await fetch('/api/tasks', {
        headers: { 'Authorization': `Bearer ${data.token}` }
    })
}
```

### Next.js Middleware for Route Protection

```typescript
// middleware.ts
import { NextRequest, NextResponse } from "next/server"
import { getSessionCookie } from "better-auth/cookies"

export async function middleware(request: NextRequest) {
    const sessionCookie = getSessionCookie(request)
    const { pathname } = request.nextUrl

    // Redirect authenticated users away from auth pages
    if (sessionCookie && ["/login", "/signup"].includes(pathname)) {
        return NextResponse.redirect(new URL("/dashboard", request.url))
    }

    // Redirect unauthenticated users to login
    if (!sessionCookie && pathname.startsWith("/dashboard")) {
        return NextResponse.redirect(new URL("/login", request.url))
    }

    return NextResponse.next()
}

export const config = {
    matcher: ["/dashboard/:path*", "/login", "/signup"]
}
```

---

## 2. SQLModel with Async PostgreSQL

### Decision: Use SQLModel with asyncpg for Neon PostgreSQL

**Rationale**: SQLModel combines Pydantic validation with SQLAlchemy ORM power. It provides type safety and works seamlessly with FastAPI. Async support via asyncpg enables non-blocking database operations.

**Alternatives Considered**:
- Raw SQLAlchemy: More verbose, lacks Pydantic integration
- Prisma: Not native Python, adds complexity
- Tortoise ORM: Less mature, smaller community

### Database Connection Pattern

```python
# database.py
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")  # postgresql+asyncpg://...

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

### Foreign Key Relationship Pattern

```python
# models.py
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    is_active: bool = Field(default=True)

    tasks: List["Task"] = Relationship(back_populates="user")

class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)

    user_id: int = Field(foreign_key="users.id", index=True)
    user: Optional[User] = Relationship(back_populates="tasks")
```

---

## 3. FastAPI JWT Verification

### Decision: Use jose library with JWKS validation

**Rationale**: The jose library (python-jose or jose) provides robust JWT verification with remote JWKS support, matching Better Auth's JWKS endpoint pattern.

**Alternatives Considered**:
- PyJWT: Simpler but less JWKS support
- authlib: More features but heavier dependency

### JWT Dependency Pattern

```python
# dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

security = HTTPBearer()
JWKS_URL = os.getenv("BETTER_AUTH_URL") + "/api/auth/jwks"

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session)
) -> User:
    token = credentials.credentials

    try:
        # Fetch JWKS and verify token
        async with httpx.AsyncClient() as client:
            jwks_response = await client.get(JWKS_URL)
            jwks = jwks_response.json()

        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256", "ES256"],
            options={"verify_aud": False}
        )
        user_id = payload.get("sub")

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Fetch user from database
    user = await session.get(User, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user
```

---

## 4. Neon PostgreSQL Connection

### Decision: Use Neon Serverless with asyncpg driver

**Rationale**: Neon provides serverless PostgreSQL with automatic scaling, ideal for hackathon deployment. Uses standard PostgreSQL wire protocol with SSL required.

**Connection String Format**:
```
postgresql+asyncpg://username:password@ep-xyz.region.neon.tech/dbname?sslmode=require
```

**Environment Variables**:
```env
DATABASE_URL=postgresql+asyncpg://user:pass@ep-xxx.neon.tech/todoapp?sslmode=require
JWT_SECRET_KEY=your-secret-key-here
BETTER_AUTH_SECRET=your-better-auth-secret
BETTER_AUTH_URL=http://localhost:3000
```

---

## 5. Project Structure Decision

### Decision: Monorepo with /frontend and /backend directories

**Rationale**: Keeps frontend and backend code together while maintaining separation of concerns. Enables shared type definitions and simplified local development.

```
todoapp/
├── frontend/                 # Next.js 15+ App Router
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   ├── dashboard/page.tsx
│   │   ├── api/auth/[...all]/route.ts
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/              # Reusable UI components
│   │   └── tasks/           # Task-specific components
│   ├── lib/
│   │   ├── auth.ts          # Server auth config
│   │   └── auth-client.ts   # Client auth config
│   ├── middleware.ts
│   └── package.json
│
├── backend/                  # FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app entry
│   │   ├── models.py        # SQLModel models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── dependencies.py  # Auth dependencies
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py     # Task CRUD routes
│   ├── database.py          # Async engine setup
│   ├── pyproject.toml
│   └── .env.example
│
├── src/                      # Phase I console app (unchanged)
├── specs/
└── CLAUDE.md
```

---

## 6. API Design Decisions

### Decision: RESTful API with /api/v1 prefix

**Base URL**: `http://localhost:8000/api/v1`

**Endpoints**:
| Method | Path | Description |
|--------|------|-------------|
| GET | /tasks | List current user's tasks |
| POST | /tasks | Create new task |
| GET | /tasks/{id} | Get specific task |
| PUT | /tasks/{id} | Update task |
| DELETE | /tasks/{id} | Delete task |
| PATCH | /tasks/{id}/toggle | Toggle completion status |

**User Isolation**: All task queries include `WHERE user_id = current_user.id` filter.

**Error Responses**: Standard HTTP status codes with JSON error bodies.

---

## 7. Password Hashing

### Decision: Use passlib with bcrypt

**Rationale**: Industry standard, compatible with Better Auth's password verification.

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

---

## Dependencies Summary

### Frontend (package.json)
```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "better-auth": "^1.0.0",
    "tailwindcss": "^4.0.0",
    "lucide-react": "^0.400.0"
  }
}
```

### Backend (pyproject.toml)
```toml
[project]
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sqlmodel>=0.0.22",
    "asyncpg>=0.29.0",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "httpx>=0.27.0",
    "python-dotenv>=1.0.0",
]
```

---

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| How does Better Auth issue JWTs? | Via JWT plugin + /api/auth/token endpoint |
| How to verify JWT in FastAPI? | Use jose with remote JWKS from Better Auth |
| Async SQLModel pattern? | Use sqlmodel.ext.asyncio.session with async_sessionmaker |
| Neon connection format? | postgresql+asyncpg://...?sslmode=require |
| Token storage? | Better Auth handles via httpOnly cookies; JWT retrieved via client.token() |
