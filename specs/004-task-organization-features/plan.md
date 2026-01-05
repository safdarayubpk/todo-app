# Implementation Plan: Task Organization Features

**Branch**: `004-task-organization-features` | **Date**: 2026-01-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-task-organization-features/spec.md`

## Summary

Extend the Phase III Todo app with intermediate-level organization features: task priorities (high/medium/low), tags (multiple per task), filtering (by status/priority/tags), keyword search, and sorting. All features accessible via web UI and natural language chatbot commands while maintaining strict user isolation.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLModel, Next.js 15, React, OpenAI Agents SDK, MCP SDK
**Storage**: Neon PostgreSQL (extend existing tasks table with priority and tags columns)
**Testing**: Manual UI testing, chatbot command testing, cross-user isolation verification
**Target Platform**: Web (Vercel frontend, HuggingFace Spaces backend)
**Project Type**: Web application (monorepo: frontend + backend)
**Performance Goals**: Filter/search results <500ms, chatbot accuracy 95%+
**Constraints**: Maintain backward compatibility, no breaking changes to existing functionality
**Scale/Scope**: Single user task lists typically <1000 items

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | PASS | spec.md complete with 33 FRs, 6 user stories |
| II. AI-Only Implementation | PASS | All code via Claude Code generation |
| III. Iterative Evolution | PASS | Extends Phase III without breaking existing features |
| IV. Reusability and Modularity | PASS | Extends existing components, new FilterBar reusable |
| V. Security and Isolation | PASS | All filters maintain user_id filtering |
| VI. Cloud-Native Readiness | PASS | No new infrastructure, existing patterns |

**Gate Result**: PASS - Proceed with implementation

## Project Structure

### Documentation (this feature)

```text
specs/004-task-organization-features/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Technical decisions
├── data-model.md        # Entity definitions
├── quickstart.md        # Implementation guide
├── contracts/
│   ├── tasks-api.yaml   # OpenAPI contract
│   └── mcp-tools.md     # MCP tool signatures
└── checklists/
    └── requirements.md  # Spec validation checklist
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── task_model.py       # UPDATE: Add priority, tags fields
│   ├── schemas.py          # UPDATE: Add priority, tags to schemas
│   ├── routes/
│   │   └── tasks.py        # UPDATE: Add filter/sort/search params
│   ├── mcp_server/
│   │   └── server.py       # UPDATE: Extend MCP tools
│   └── chatkit/
│       └── agent.py        # UPDATE: System prompt for organization

frontend/
├── lib/
│   └── api.ts              # UPDATE: Add filter params to taskApi
├── components/
│   ├── ui/
│   │   ├── FilterBar.tsx   # NEW: Combined filter/search/sort controls
│   │   ├── PriorityBadge.tsx  # NEW: Priority visual indicator
│   │   └── TagChip.tsx     # NEW: Tag display chip
│   └── tasks/
│       ├── TaskForm.tsx    # UPDATE: Add priority dropdown, tag input
│       ├── TaskList.tsx    # UPDATE: Integrate FilterBar
│       └── TaskItem.tsx    # UPDATE: Display priority/tags
└── app/
    └── dashboard/
        └── page.tsx        # UPDATE: Filter state management
```

**Structure Decision**: Extend existing web application structure with new UI components and backend route updates. No new services or architectural changes required.

## Complexity Tracking

> No Constitution violations - table left empty

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| - | - | - |

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Priority storage | String enum VARCHAR | Readable, simple, extensible |
| Tags storage | PostgreSQL ARRAY | Native support, GIN indexing |
| Filtering | Server-side query params | Enforces isolation, reduces transfer |
| Search | ILIKE substring | Simple, adequate for <1000 tasks |
| MCP extension | Optional params on existing tools | Backward compatible |
| Frontend state | React useState | Local, no persistence needed |

## Implementation Phases

### Phase 1: Backend Data Model

1. Extend `Task` model with priority and tags fields
2. Update Pydantic schemas with new fields and validation
3. Create/run database migration

### Phase 2: Backend API

1. Add query parameters to GET /tasks endpoint
2. Implement filtering logic (status, priority, tags)
3. Implement search logic (ILIKE on title/description)
4. Implement sorting logic (priority, title, created_at)
5. Add tag management endpoints (POST/DELETE /tasks/{id}/tags)

### Phase 3: MCP Tools

1. Extend add_task with priority and tags parameters
2. Extend list_tasks with filter/sort/search parameters
3. Extend update_task with priority and tag modification
4. Update agent system prompt for natural language parsing

### Phase 4: Frontend Components

1. Create PriorityBadge component
2. Create TagChip component
3. Create FilterBar component (search, filter dropdowns, sort)
4. Create TagInput component for task form

### Phase 5: Frontend Integration

1. Update TaskForm with priority dropdown and tag input
2. Update TaskItem with priority badge and tag display
3. Update TaskList to integrate FilterBar
4. Update dashboard page with filter state management
5. Update api.ts with filter query parameters

### Phase 6: Testing & Polish

1. Manual testing of all filter/sort/search combinations
2. Chatbot testing with natural language queries
3. Cross-user isolation verification
4. Mobile responsive testing
5. Performance verification (<500ms)

## Artifacts Generated

| Artifact | Path | Purpose |
|----------|------|---------|
| research.md | specs/004-.../research.md | Technical decisions |
| data-model.md | specs/004-.../data-model.md | Entity definitions |
| tasks-api.yaml | specs/004-.../contracts/tasks-api.yaml | OpenAPI contract |
| mcp-tools.md | specs/004-.../contracts/mcp-tools.md | MCP signatures |
| quickstart.md | specs/004-.../quickstart.md | Implementation guide |

## Next Steps

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Run `/sp.analyze` to validate artifact consistency
3. Run `/sp.implement` to execute the implementation

## Risks

1. **Database migration on production**: Run migration during low-traffic period
2. **Breaking existing chatbot behavior**: Test backward compatibility thoroughly
3. **Performance with many tags**: Monitor GIN index performance
