---
name: sqlmodel-schema-designer
description: This skill should be used when the user needs to design, generate, or modify SQLModel database models, tables, relationships, indexes, or migration patterns. Triggers automatically for requests involving "create model", "database schema", "add table", "define relationship", "Neon PostgreSQL integration", "user-task relationships", or evolving from in-memory to persistent storage in the Todo app.
allowed-tools: Read, Write, Grep, Bash
---

# SQLModel Schema Designer

Design and generate clean, scalable SQLModel database models following project constitution and Spec-Driven Development principles.

## Quick Start

Generate a model using the script:

```bash
python3 .claude/skills/sqlmodel-schema-designer/scripts/generate_model.py <ModelName> --output-dir backend/app/models
```

Or copy templates from `assets/` and customize manually.

## Design Rules

Apply these rules when designing SQLModel schemas:

- Use SQLModel (combining SQLAlchemy + Pydantic) for all models
- Inherit from `SQLModel` with `table=True` for database tables
- Include primary key: `id: Optional[int] = Field(default=None, primary_key=True)`
- For multi-user: Add `user_id: int` with `ForeignKey` and `index=True`
- Use appropriate field types (`str`, `bool`, `Optional[str]`, `datetime`)
- Add indexes for frequently queried fields (`user_id`, `is_completed`)
- Use plural table names (`tasks`, `users`, `projects`)
- Include relationship definitions with `back_populates`
- Add timestamps: `created_at`, `updated_at`

## Schema Patterns

| Pattern | Use Case |
|---------|----------|
| Base/Create/Read/Update | Separate schemas for different operations |
| User isolation | Filter by `user_id` foreign key |
| Soft delete | Add `deleted_at: Optional[datetime]` |
| Timestamps | `created_at`, `updated_at` with `default_factory` |

## Common Models

| Model | Fields |
|-------|--------|
| User | id, email, username, hashed_password, is_active, created_at |
| Task | id, title, description, is_completed, user_id (FK), created_at, updated_at |
| Project | id, name, description, user_id (FK), created_at |

## Output Format

Output complete code files with full relative paths:
- `backend/app/models/{model}.py` - Model definition
- `backend/app/database.py` - Engine and session setup (if needed)

## Additional Resources

### Reference Files

Consult for detailed patterns and code examples:
- **`references/model-patterns.md`** - Inheritance, relationships, indexes, validators
- **`references/database-setup.md`** - Async engine, session, Neon PostgreSQL config

### Template Files

Copy and customize from `assets/`:
- **`assets/base_model.py`** - Base model with timestamps
- **`assets/user_model.py`** - User model template
- **`assets/task_model.py`** - Task model with user relationship
- **`assets/database.py`** - Async database setup template

### Scripts

- **`scripts/generate_model.py`** - Model scaffolding generator

## Constraints

- Reference the global constitution for performance and security
- Do not add features outside the current spec
- Keep models focused and normalized
