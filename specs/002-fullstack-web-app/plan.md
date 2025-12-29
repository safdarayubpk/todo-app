# Implementation Plan: Full-Stack Multi-User Web Todo Application

**Branch**: `002-fullstack-web-app` | **Date**: 2025-12-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fullstack-web-app/spec.md`

## Summary

Evolve the Phase I console todo app into a secure, multi-user web application with:
- **Frontend**: Next.js 15+ with App Router, TypeScript, and Tailwind CSS
- **Backend**: FastAPI with async endpoints and SQLModel ORM
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth (frontend) with JWT tokens verified by FastAPI

Key capability: Multiple users can independently manage their own isolated task lists through a responsive web interface.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Better Auth, Next.js 15, Tailwind CSS
**Storage**: Neon PostgreSQL (serverless, async via asyncpg)
**Testing**: Manual E2E testing (demo with two users)
**Target Platform**: Web (desktop + mobile responsive)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: <1s task operations, <10s login/dashboard load
**Constraints**: User isolation at all layers, environment-based secrets
**Scale/Scope**: 2-user demo, 5 screens (login, signup, dashboard + modals)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | spec.md complete, plan.md in progress |
| II. AI-Only Implementation | ✅ PASS | All code via Claude Code |
| III. Iterative Evolution | ✅ PASS | Phase II builds on Phase I |
| IV. Reusability and Modularity | ✅ PASS | Separate frontend/backend, reusable components |
| V. Security and Isolation | ✅ PASS | JWT auth, user_id filtering on all queries |
| VI. Cloud-Native Readiness | ✅ PASS | Stateless API, env-based config, container-ready |

**Tech Stack Compliance**:

| Layer | Constitution Spec | Plan Choice | Status |
|-------|------------------|-------------|--------|
| Frontend | Next.js (App Router) | Next.js 15 App Router | ✅ |
| Backend | FastAPI | FastAPI (async) | ✅ |
| ORM | SQLModel | SQLModel | ✅ |
| Database | Neon PostgreSQL | Neon PostgreSQL | ✅ |
| Auth | Better Auth | Better Auth + JWT | ✅ |
| Python Mgmt | UV | UV | ✅ |

## Project Structure

### Documentation (this feature)

```text
specs/002-fullstack-web-app/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technology research
├── data-model.md        # Entity definitions
├── quickstart.md        # Setup guide
├── contracts/
│   └── openapi.yaml     # API contract
└── tasks.md             # Implementation tasks (via /sp.tasks)
```

### Source Code (repository root)

```text
todoapp/
├── frontend/                    # Next.js 15 App Router
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── signup/
│   │   │       └── page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── api/
│   │   │   └── auth/
│   │   │       └── [...all]/
│   │   │           └── route.ts
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Modal.tsx
│   │   └── tasks/
│   │       ├── TaskItem.tsx
│   │       ├── TaskList.tsx
│   │       ├── TaskForm.tsx
│   │       └── TaskFilters.tsx
│   ├── lib/
│   │   ├── auth.ts              # Server auth config
│   │   ├── auth-client.ts       # Client auth config
│   │   └── api.ts               # API client helpers
│   ├── middleware.ts            # Route protection
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   ├── package.json
│   └── .env.example
│
├── backend/                      # FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # App entry, lifespan
│   │   ├── models.py            # SQLModel table models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── dependencies.py      # Auth dependency (get_current_user)
│   │   └── routes/
│   │       ├── __init__.py
│   │       └── tasks.py         # Task CRUD endpoints
│   ├── database.py              # Async engine, session
│   ├── pyproject.toml
│   └── .env.example
│
├── src/                          # Phase I console app (unchanged)
│   ├── __init__.py
│   ├── main.py
│   └── todo.py
│
├── specs/
├── .specify/
├── CLAUDE.md
└── README.md
```

**Structure Decision**: Web application pattern with separate `frontend/` and `backend/` directories. Phase I `src/` remains untouched. This enables independent development and deployment of each tier.

## Architecture Decisions

### 1. Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Next.js)                       │
├─────────────────────────────────────────────────────────────────┤
│  1. User submits login form                                      │
│  2. Better Auth handles auth → stores session in httpOnly cookie │
│  3. authClient.token() retrieves JWT                             │
│  4. JWT sent to backend in Authorization header                  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                        │
├─────────────────────────────────────────────────────────────────┤
│  5. get_current_user dependency extracts token                   │
│  6. Validates JWT via Better Auth JWKS endpoint                  │
│  7. Loads user from database                                     │
│  8. Injects user into route handler                              │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Data Flow

```
Frontend (React)
    ↓ fetch('/api/v1/tasks', { headers: { Authorization: Bearer ... } })
    ↓
Backend (FastAPI)
    ↓ current_user = Depends(get_current_user)
    ↓ SELECT * FROM tasks WHERE user_id = current_user.id
    ↓
Database (Neon PostgreSQL)
    ↓
Response → Frontend → Render TaskList
```

### 3. User Isolation Strategy

- **Database Level**: All task queries include `WHERE user_id = :user_id`
- **API Level**: `get_current_user` dependency on all task routes
- **Frontend Level**: Middleware redirects unauthenticated users

## Complexity Tracking

> No constitution violations. All choices align with approved tech stack.

| Item | Justification |
|------|---------------|
| JWT + Better Auth | Required by constitution for Phase II+ auth |
| Async SQLModel | Matches constitution ORM choice with Neon async driver |
| Monorepo structure | Simplifies local development, matches constitution layout |

## Related Artifacts

| Artifact | Status | Path |
|----------|--------|------|
| Feature Spec | ✅ Complete | [spec.md](./spec.md) |
| Research | ✅ Complete | [research.md](./research.md) |
| Data Model | ✅ Complete | [data-model.md](./data-model.md) |
| API Contract | ✅ Complete | [contracts/openapi.yaml](./contracts/openapi.yaml) |
| Quickstart | ✅ Complete | [quickstart.md](./quickstart.md) |
| Tasks | ⏳ Pending | Run `/sp.tasks` to generate |

## Next Steps

1. Run `/sp.tasks` to generate implementation task list
2. Run `/sp.analyze` to validate cross-artifact consistency
3. Run `/sp.implement` to begin code generation
