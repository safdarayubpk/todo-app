# Quickstart: Task Organization Features

**Feature**: 004-task-organization-features
**Date**: 2026-01-05

## Prerequisites

- Existing Phase III Todo app running
- PostgreSQL database (Neon)
- Backend: FastAPI with SQLModel
- Frontend: Next.js with React
- MCP Server operational

## Implementation Order

### 1. Database Migration (5 min)

Add priority and tags columns to tasks table:

```bash
# Connect to Neon PostgreSQL and run migration
psql $DATABASE_URL -f specs/004-task-organization-features/migration.sql
```

Or via Python:
```python
# In backend/app/database.py or migration script
from sqlalchemy import text

async def migrate_organization_features(engine):
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium' NOT NULL;

            ALTER TABLE tasks
            ADD COLUMN IF NOT EXISTS tags VARCHAR[] DEFAULT '{}' NOT NULL;

            CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks (priority);
            CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks USING GIN (tags);
        """))
```

### 2. Backend Model Updates (10 min)

Update `backend/app/task_model.py`:

```python
from sqlalchemy import ARRAY, String, Column

class Task(SQLModel, table=True):
    # ... existing fields ...
    priority: str = Field(default="medium", max_length=10)
    tags: list[str] = Field(
        default=[],
        sa_column=Column(ARRAY(String), nullable=False, server_default="{}")
    )
```

Update `backend/app/schemas.py`:

```python
from typing import Literal

PriorityLevel = Literal["high", "medium", "low"]

class TaskCreate(BaseModel):
    # ... existing fields ...
    priority: PriorityLevel = Field(default="medium")
    tags: list[str] = Field(default=[])

class TaskRead(BaseModel):
    # ... existing fields ...
    priority: str
    tags: list[str]
```

### 3. Backend API Updates (15 min)

Update `backend/app/routes/tasks.py` to add query parameters:

```python
from typing import Optional, List
from sqlalchemy import case, or_

@router.get("", response_model=List[TaskRead])
async def list_tasks(
    current_user_id: CurrentUserId,
    session: DbSession,
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    tags: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc"),
) -> List[Task]:
    statement = select(Task).where(Task.user_id == current_user_id)

    # Apply filters
    if status == "pending":
        statement = statement.where(Task.is_completed == False)
    elif status == "completed":
        statement = statement.where(Task.is_completed == True)

    if priority:
        statement = statement.where(Task.priority == priority)

    if tags:
        for tag in tags:
            statement = statement.where(Task.tags.contains([tag]))

    if search:
        pattern = f"%{search}%"
        statement = statement.where(
            or_(Task.title.ilike(pattern), Task.description.ilike(pattern))
        )

    # Apply sorting
    # ... sorting logic ...

    result = await session.execute(statement)
    return list(result.scalars().all())
```

### 4. MCP Tools Update (15 min)

Update `backend/app/mcp_server/server.py`:

```python
@mcp.tool()
def add_task(
    user_id: str,
    title: str,
    description: str | None = None,
    priority: str = "medium",
    tags: list[str] | None = None,
) -> dict:
    # Validate priority
    if priority not in ("high", "medium", "low"):
        return {"error": "Priority must be high, medium, or low"}

    # Normalize tags
    normalized_tags = [t.strip().lower() for t in (tags or []) if t.strip()]

    with get_sync_session() as session:
        task = Task(
            title=title,
            description=description,
            priority=priority,
            tags=normalized_tags,
            user_id=user_id.strip(),
        )
        # ... rest of create logic ...

@mcp.tool()
def list_tasks(
    user_id: str,
    status: str = "all",
    priority: str | None = None,
    tags: list[str] | None = None,
    search: str | None = None,
    sort_by: str = "created_at",
    sort_dir: str = "desc",
) -> list[dict]:
    # ... filter/sort implementation ...
```

### 5. Frontend API Client (10 min)

Update `frontend/lib/api.ts`:

```typescript
export interface Task {
  // ... existing fields ...
  priority: "high" | "medium" | "low";
  tags: string[];
}

export interface TaskCreate {
  // ... existing fields ...
  priority?: "high" | "medium" | "low";
  tags?: string[];
}

export interface TaskFilters {
  status?: "all" | "pending" | "completed";
  priority?: "high" | "medium" | "low";
  tags?: string[];
  search?: string;
  sort_by?: "created_at" | "priority" | "title";
  sort_dir?: "asc" | "desc";
}

export const taskApi = {
  list: (filters?: TaskFilters) => {
    const params = new URLSearchParams();
    if (filters?.status) params.set("status", filters.status);
    if (filters?.priority) params.set("priority", filters.priority);
    if (filters?.tags) filters.tags.forEach(t => params.append("tags", t));
    if (filters?.search) params.set("search", filters.search);
    if (filters?.sort_by) params.set("sort_by", filters.sort_by);
    if (filters?.sort_dir) params.set("sort_dir", filters.sort_dir);

    const query = params.toString();
    return apiFetch<Task[]>(`/tasks${query ? `?${query}` : ""}`);
  },
  // ... rest unchanged ...
};
```

### 6. Frontend Components (20 min)

Create `frontend/components/ui/FilterBar.tsx`:
- Priority dropdown
- Tag filter chips
- Search input
- Sort dropdown

Update `frontend/components/tasks/TaskForm.tsx`:
- Add priority select
- Add tag input

Update `frontend/components/tasks/TaskItem.tsx`:
- Display priority badge
- Display tag chips

### 7. Agent Prompt Update (5 min)

Update `backend/app/chatkit/agent.py` system prompt to include organization features guidance.

## Testing Checklist

- [ ] Create task with priority via UI
- [ ] Create task with tags via UI
- [ ] Filter by priority
- [ ] Filter by tags
- [ ] Search by keyword
- [ ] Sort by priority/title
- [ ] Chatbot: "add high priority task"
- [ ] Chatbot: "show work tasks"
- [ ] Chatbot: "sort by priority"
- [ ] Verify user isolation (user A can't see user B's filtered results)

## Verification Commands

```bash
# Backend health check
curl http://localhost:8000/api/v1/health

# Test filter endpoint (with auth)
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/tasks?priority=high&tags=work"

# Test chatbot
# In chat: "show my high priority work tasks sorted by title"
```

## Rollback

If issues occur:
```sql
-- Remove new columns (data loss!)
ALTER TABLE tasks DROP COLUMN IF EXISTS priority;
ALTER TABLE tasks DROP COLUMN IF EXISTS tags;
DROP INDEX IF EXISTS idx_tasks_priority;
DROP INDEX IF EXISTS idx_tasks_tags;
```
