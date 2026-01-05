---
id: 002
title: create-plan-task-organization
stage: plan
date: 2026-01-05
surface: agent
model: claude-opus-4-5-20251101
feature: 004-task-organization-features
branch: 004-task-organization-features
user: safdarayub
command: /sp.plan
labels: [plan, architecture, priority, tags, filtering, search, sorting, mcp]
links:
  spec: specs/004-task-organization-features/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-task-organization-features/plan.md
  - specs/004-task-organization-features/research.md
  - specs/004-task-organization-features/data-model.md
  - specs/004-task-organization-features/quickstart.md
  - specs/004-task-organization-features/contracts/tasks-api.yaml
  - specs/004-task-organization-features/contracts/mcp-tools.md
tests:
  - N/A (planning phase)
---

## Prompt

/sp.plan

Intermediate Features Extension

Objective: Implement the Intermediate Level features (priorities, tags, search/filter, sorting) as specified, enhancing the existing Phase III Todo app to provide better organization and usability while extending the chatbot's natural language capabilities.

Architecture sketch:
- Monorepo updates to existing frontend (Next.js) and backend (FastAPI + MCP)
- Database: Extend Task model in SQLModel with priority (str enum: high/medium/low) and tags (JSON list of str)
- Backend: Update API endpoints to accept new fields and support query parameters for filter/sort/search
- Frontend: Add UI controls for priority dropdown, tag input/chips, search bar, filter selects, sort dropdown
- Chatbot: Extend MCP tools to handle new parameters (priority, tags, filter, sort) and parse natural language queries accordingly
- Data flow: UI/Chat → API/MCP → SQLModel → Neon DB
- Isolation: Maintain strict user_id filtering in all new queries

Project layout additions/updates:
- frontend/app/components/TaskForm.tsx - Add priority dropdown and tag input
- frontend/app/components/TaskList.tsx - Add search bar, filter selects, sort dropdown
- frontend/app/components/TagChip.tsx - New for tag display/removal
- frontend/lib/task-api.ts - Update API calls with new params
- backend/app/models.py - Extend Task model with priority and tags
- backend/app/schemas.py - Update Pydantic schemas
- backend/app/routes/tasks.py - Add filter/sort/search to GET endpoints
- backend/mcp_tools.py - Extend MCP tools with new params

Research approach:
- Use built-in mcp-builder skill for extending MCP tools
- Reference SQLModel docs for JSON fields and enum constraints
- Study Next.js patterns for dynamic filtering/sorting

Quality validation:
- All new fields persisted and displayed correctly
- Filters/search/sort update UI in <500ms
- Chatbot handles 95% of standard intermediate queries accurately
- No performance degradation for lists up to 1000 tasks
- Isolation: Filters/search only apply to current user's tasks

Decisions needing documentation:
- Priority: String enum vs integer - chose string for readability
- Tags: PostgreSQL ARRAY vs JSON - chose ARRAY for native support
- Filtering: Server-side for isolation and efficiency
- MCP extension: Optional params on existing tools for backward compatibility

## Response snapshot

Created comprehensive implementation plan for Task Organization Features:

**Phase 0 - Research**: Resolved 10 technical unknowns covering priority storage, tags in PostgreSQL, filtering strategy, search implementation, sorting, tag normalization, MCP extension, frontend state, database migration, and UI components.

**Phase 1 - Design Artifacts**:
- data-model.md: Extended Task entity with priority (VARCHAR) and tags (ARRAY), includes migration SQL
- contracts/tasks-api.yaml: OpenAPI 3.1 spec with filter/sort/search query parameters
- contracts/mcp-tools.md: Extended MCP tool signatures with natural language examples
- quickstart.md: Step-by-step implementation guide

**Key Decisions**:
| Decision | Choice | Rationale |
|----------|--------|-----------|
| Priority storage | String enum VARCHAR | Readable, simple, extensible |
| Tags storage | PostgreSQL ARRAY | Native support, GIN indexing |
| Filtering | Server-side query params | Enforces isolation, reduces transfer |
| Search | ILIKE substring | Simple, adequate for <1000 tasks |
| MCP extension | Optional params on existing tools | Backward compatible |

**Constitution Check**: All 6 principles PASS

**6 Implementation Phases** defined for execution via /sp.tasks

## Outcome

- Impact: Complete architectural plan ready for task generation
- Tests: N/A (planning phase)
- Files: plan.md, research.md, data-model.md, quickstart.md, contracts/
- Next prompts: /sp.tasks to generate implementation tasks, /sp.analyze to validate consistency
- Reflection: Plan maintains backward compatibility while adding substantial new functionality; PostgreSQL ARRAY for tags is cleaner than JSON

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully
- Graders run and results (PASS/FAIL): Constitution check PASS (6/6 principles)
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Proceed to /sp.tasks for implementation breakdown
