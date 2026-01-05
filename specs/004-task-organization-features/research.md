# Research: Task Organization Features

**Feature**: 004-task-organization-features
**Date**: 2026-01-05
**Purpose**: Resolve technical unknowns and document decisions for implementation

## Research Topics

### 1. Priority Field Storage

**Decision**: Use string enum ("high", "medium", "low") stored as VARCHAR

**Rationale**:
- Readability in database and API responses
- SQLModel/Pydantic support via `Literal` type constraint
- Simpler than integer mapping (no translation layer needed)
- Flexible for future priority levels if needed

**Alternatives Considered**:
- Integer mapping (1=high, 2=medium, 3=low): Better for sorting but less readable
- Boolean is_urgent: Too limited for 3-level system
- Separate priority table: Over-engineered for simple enum

**Implementation**:
```python
from typing import Literal

PriorityLevel = Literal["high", "medium", "low"]
priority: str = Field(default="medium", description="Priority level")
```

### 2. Tags Storage in PostgreSQL

**Decision**: Use PostgreSQL ARRAY type with `list[str]` in SQLModel

**Rationale**:
- PostgreSQL natively supports array types
- SQLModel/SQLAlchemy handles list[str] → ARRAY(VARCHAR) mapping
- Supports indexing via GIN index for efficient filtering
- Simpler than JSON column or separate tags table

**Alternatives Considered**:
- JSON/JSONB column: More complex querying, less type safety
- Separate tags table (many-to-many): Over-engineered for simple tagging
- Comma-separated string: Poor query performance, harder filtering

**Implementation**:
```python
from sqlalchemy import ARRAY, String
from sqlmodel import Field, Column

tags: list[str] = Field(
    default=[],
    sa_column=Column(ARRAY(String), nullable=False, default=[])
)
```

### 3. Filtering Strategy

**Decision**: Server-side filtering via FastAPI query parameters

**Rationale**:
- User isolation requires server-side filtering (user_id always applied)
- Reduces data transfer for large task lists
- Single source of truth for filter logic
- API contracts clearly define filter capabilities

**Alternatives Considered**:
- Client-side filtering: Cannot enforce isolation, transfers all data
- GraphQL: Over-complex for simple filtering needs
- Separate filter endpoint: Unnecessary when query params suffice

**Implementation**:
```python
@router.get("", response_model=List[TaskRead])
async def list_tasks(
    current_user_id: CurrentUserId,
    session: DbSession,
    status: Optional[str] = Query(None, regex="^(all|pending|completed)$"),
    priority: Optional[str] = Query(None, regex="^(high|medium|low)$"),
    tags: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None, min_length=1, max_length=255),
    sort_by: Optional[str] = Query("created_at", regex="^(created_at|priority|title)$"),
    sort_dir: Optional[str] = Query("desc", regex="^(asc|desc)$"),
) -> List[Task]:
    ...
```

### 4. Search Implementation

**Decision**: PostgreSQL ILIKE for case-insensitive substring matching

**Rationale**:
- Simple, built-in PostgreSQL feature
- Case-insensitive without extra configuration
- Adequate performance for individual user task lists (typically <1000 tasks)
- No additional infrastructure needed

**Alternatives Considered**:
- Full-text search (tsvector): Overkill for simple substring matching
- ElasticSearch: Requires separate service, over-engineered
- Trigram index: Better for fuzzy matching but not required

**Implementation**:
```python
if search:
    search_pattern = f"%{search}%"
    statement = statement.where(
        or_(
            Task.title.ilike(search_pattern),
            Task.description.ilike(search_pattern)
        )
    )
```

### 5. Sorting Implementation

**Decision**: Server-side sorting with ORDER BY clause

**Rationale**:
- Consistent with filtering strategy
- Priority sorting requires custom ordering (high > medium > low)
- Reduces client-side complexity

**Alternatives Considered**:
- Client-side sorting: Less efficient, duplicates logic
- Database views: Over-complex for dynamic sort options

**Implementation**:
```python
# Priority requires CASE expression for custom order
if sort_by == "priority":
    priority_order = case(
        (Task.priority == "high", 1),
        (Task.priority == "medium", 2),
        (Task.priority == "low", 3),
    )
    statement = statement.order_by(
        priority_order.asc() if sort_dir == "asc" else priority_order.desc()
    )
elif sort_by == "title":
    statement = statement.order_by(
        Task.title.asc() if sort_dir == "asc" else Task.title.desc()
    )
else:  # created_at default
    statement = statement.order_by(
        Task.created_at.asc() if sort_dir == "asc" else Task.created_at.desc()
    )
```

### 6. Tag Normalization

**Decision**: Normalize to lowercase on input, store lowercase

**Rationale**:
- Consistent filtering (user enters "Work", "work", or "WORK" all match)
- Simpler than case-insensitive comparisons everywhere
- Display original casing not required (per spec assumptions)

**Alternatives Considered**:
- Store as-entered, compare case-insensitively: More complex queries
- Store both original and normalized: Unnecessary complexity

**Implementation**:
```python
# In schema validation
tags: list[str] = Field(default=[])

# In API/service layer
normalized_tags = [tag.strip().lower() for tag in tags if tag.strip()]
```

### 7. MCP Tool Extension Strategy

**Decision**: Extend existing tools with optional parameters

**Rationale**:
- Preserves backward compatibility
- Simpler than creating new tools
- Agent prompt already knows existing tool signatures
- New parameters are optional, existing calls work unchanged

**Alternatives Considered**:
- New tools (add_task_with_priority, filter_tasks): Duplicates functionality
- Breaking changes to existing tools: May break existing agent behavior

**Implementation**:
```python
@mcp.tool()
def add_task(
    user_id: str,
    title: str,
    description: str | None = None,
    priority: str = "medium",  # NEW optional param
    tags: list[str] | None = None,  # NEW optional param
) -> dict:
    ...

@mcp.tool()
def list_tasks(
    user_id: str,
    status: str = "all",
    priority: str | None = None,  # NEW optional param
    tags: list[str] | None = None,  # NEW optional param
    search: str | None = None,  # NEW optional param
    sort_by: str = "created_at",  # NEW optional param
    sort_dir: str = "desc",  # NEW optional param
) -> list[dict]:
    ...
```

### 8. Frontend State Management

**Decision**: React useState for filter/sort state in dashboard component

**Rationale**:
- Filter/sort state is local to dashboard view
- No need to persist across sessions (per spec)
- Simple, no additional dependencies
- URL query params not required (no deep linking to filtered views)

**Alternatives Considered**:
- URL search params: Useful for sharing filtered views, but not required
- Zustand/Redux: Overkill for local UI state
- React Context: Not needed, state is single-component

**Implementation**:
```typescript
const [filters, setFilters] = useState({
  status: "all",
  priority: null as string | null,
  tags: [] as string[],
  search: "",
  sortBy: "created_at",
  sortDir: "desc",
});
```

### 9. Database Migration Strategy

**Decision**: Non-destructive column additions with defaults

**Rationale**:
- Existing tasks continue to work (default priority="medium", tags=[])
- No data loss or migration complexity
- Gradual rollout possible

**Implementation**:
```sql
-- Alembic migration or direct SQL
ALTER TABLE tasks
ADD COLUMN priority VARCHAR(10) DEFAULT 'medium' NOT NULL,
ADD COLUMN tags VARCHAR[] DEFAULT '{}' NOT NULL;

-- Optional: GIN index for tag array queries
CREATE INDEX idx_tasks_tags ON tasks USING GIN (tags);
```

### 10. UI Component Strategy

**Decision**: Extend existing TaskForm and TaskList components

**Rationale**:
- Maintains component cohesion
- Reuses existing styling and patterns
- Minimizes new component creation

**New Components Needed**:
- `TagInput.tsx`: Multi-tag input with chips (for TaskForm)
- `FilterBar.tsx`: Combined filter/search/sort controls (for TaskList)
- `PriorityBadge.tsx`: Visual priority indicator (for TaskItem)
- `TagChip.tsx`: Individual tag display (for TaskItem)

## Summary

All technical unknowns have been resolved with clear decisions, rationales, and implementation approaches. The design:

1. **Extends existing architecture** rather than introducing new patterns
2. **Uses PostgreSQL native features** (ARRAY, ILIKE) for performance
3. **Maintains server-side filtering** for security and isolation
4. **Preserves backward compatibility** in both API and MCP tools
5. **Keeps UI state simple** with React hooks

No [NEEDS CLARIFICATION] items remain.
