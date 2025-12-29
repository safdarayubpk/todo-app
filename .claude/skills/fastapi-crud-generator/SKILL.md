---
name: fastapi-crud-generator
description: This skill should be used when the user needs to generate or modify FastAPI CRUD endpoints for resources like tasks, projects, or comments. Triggers on requests involving JWT authentication, current user dependency, user isolation (filter by user_id), SQLModel integration, async operations, proper status codes, and error handling. Activate automatically for any request involving "create API endpoints", "generate CRUD routes", "FastAPI routes", "backend models", or database operations.
allowed-tools: Read, Write, Grep, Bash
---

# FastAPI CRUD Generator

Generate secure, production-ready FastAPI CRUD endpoints following project constitution and Spec-Driven Development principles.

## Quick Start

Generate CRUD for a new resource:

```bash
python .claude/skills/fastapi-crud-generator/scripts/generate_crud.py <resource_name> --output-dir backend/app
```

Or copy templates from `assets/` and customize manually.

## Generation Rules

Apply these rules when generating CRUD endpoints:

- Use `async def` for all endpoints
- Inject `current_user` via JWT dependency (from `backend/auth.py` or similar)
- Filter all queries by `current_user.id` for data isolation
- Use SQLModel for database models and async sessions
- Use Pydantic models for request/response schemas
- Include proper HTTP status codes (201 Created, 404 Not Found, etc.)
- Add meaningful error handling with `HTTPException`
- Include docstrings and type hints
- Follow REST conventions:
  - `GET /resources` - List all
  - `GET /resources/{id}` - Get single
  - `POST /resources` - Create new
  - `PUT /resources/{id}` - Update existing
  - `DELETE /resources/{id}` - Delete

## Output Format

Output complete code files with full relative paths:
- `backend/app/routes/{resource}.py` - CRUD endpoints
- `backend/app/models/{resource}.py` - SQLModel schemas

## Additional Resources

### Reference Files

Consult for detailed patterns and code examples:
- **`references/fastapi-patterns.md`** - JWT auth, async sessions, error handling, pagination
- **`references/sqlmodel-schemas.md`** - Model inheritance, validation, relationships

### Template Files

Copy and customize from `assets/`:
- **`assets/route-template.py`** - Complete CRUD route template with all endpoints
- **`assets/model-template.py`** - SQLModel Base/Create/Read/Update pattern

### Scripts

- **`scripts/generate_crud.py`** - Automated CRUD generator (run with Python)

## Constraints

- Reference the global constitution for code quality standards
- Do not add features outside the current spec
- Keep changes minimal and focused on the requested resource
