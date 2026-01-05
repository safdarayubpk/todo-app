# Tasks: Task Organization Features

**Input**: Design documents from `/specs/004-task-organization-features/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/

**Tests**: Not explicitly requested in spec - tests excluded (manual testing via quickstart.md)

**Organization**: Tasks grouped by user story to enable independent implementation and testing

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US6)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`
- **Frontend**: `frontend/`

---

## Phase 1: Setup (Database Migration)

**Purpose**: Extend database schema with priority and tags columns

- [ ] T001 Run database migration to add priority and tags columns to tasks table (see data-model.md migration SQL)

**Checkpoint**: Database schema updated - existing tasks have default priority="medium" and tags=[]

---

## Phase 2: Foundational (Backend Model & Schema Updates)

**Purpose**: Core model changes that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T002 Update Task model with priority field in backend/app/task_model.py
- [ ] T003 [P] Update Task model with tags field (PostgreSQL ARRAY) in backend/app/task_model.py
- [ ] T004 Update TaskCreate schema with priority and tags fields in backend/app/schemas.py
- [ ] T005 [P] Update TaskUpdate schema with priority and tags fields in backend/app/schemas.py
- [ ] T006 [P] Update TaskRead schema with priority and tags fields in backend/app/schemas.py
- [ ] T007 Add tag normalization validator to schemas in backend/app/schemas.py

**Checkpoint**: Foundation ready - backend models and schemas support priority/tags

---

## Phase 3: User Story 1 - Set Task Priority (Priority: P1)

**Goal**: Users can assign priority level (high/medium/low) to tasks

**Independent Test**: Create task with priority via UI, verify it displays with visual indicator

### Backend Implementation for US1

- [ ] T008 [US1] Update create_task endpoint to accept priority in backend/app/routes/tasks.py
- [ ] T009 [US1] Update update_task endpoint to accept priority in backend/app/routes/tasks.py

### MCP Implementation for US1

- [ ] T010 [US1] Extend add_task MCP tool with priority parameter in backend/app/mcp_server/server.py
- [ ] T011 [US1] Extend update_task MCP tool with new_priority parameter in backend/app/mcp_server/server.py
- [ ] T012 [US1] Update list_tasks response to include priority field in backend/app/mcp_server/server.py

### Frontend Implementation for US1

- [ ] T013 [P] [US1] Update Task interface with priority field in frontend/lib/api.ts
- [ ] T014 [P] [US1] Update TaskCreate interface with priority field in frontend/lib/api.ts
- [ ] T015 [P] [US1] Create PriorityBadge component in frontend/components/ui/PriorityBadge.tsx
- [ ] T016 [US1] Add priority dropdown to TaskForm in frontend/components/tasks/TaskForm.tsx
- [ ] T017 [US1] Display PriorityBadge in TaskItem in frontend/components/tasks/TaskItem.tsx
- [ ] T018 [US1] Update agent system prompt for priority commands in backend/app/chatkit/agent.py

**Checkpoint**: US1 complete - tasks can be created/updated with priority, displayed in UI, and managed via chatbot

---

## Phase 4: User Story 2 - Add Tags to Tasks (Priority: P1)

**Goal**: Users can add multiple tags to tasks for categorization

**Independent Test**: Create task with tags, add/remove tags on existing task, verify tags display

### Backend Implementation for US2

- [ ] T019 [US2] Update create_task endpoint to accept tags in backend/app/routes/tasks.py
- [ ] T020 [US2] Update update_task endpoint to accept tags in backend/app/routes/tasks.py
- [ ] T021 [P] [US2] Add POST /tasks/{id}/tags endpoint for adding single tag in backend/app/routes/tasks.py
- [ ] T022 [P] [US2] Add DELETE /tasks/{id}/tags endpoint for removing tag in backend/app/routes/tasks.py

### MCP Implementation for US2

- [ ] T023 [US2] Extend add_task MCP tool with tags parameter in backend/app/mcp_server/server.py
- [ ] T024 [US2] Extend update_task MCP tool with add_tags/remove_tags parameters in backend/app/mcp_server/server.py
- [ ] T025 [US2] Update list_tasks response to include tags field in backend/app/mcp_server/server.py

### Frontend Implementation for US2

- [ ] T026 [P] [US2] Update Task interface with tags field in frontend/lib/api.ts
- [ ] T027 [P] [US2] Create TagChip component in frontend/components/ui/TagChip.tsx
- [ ] T028 [P] [US2] Create TagInput component for entering multiple tags in frontend/components/ui/TagInput.tsx
- [ ] T029 [US2] Add TagInput to TaskForm in frontend/components/tasks/TaskForm.tsx
- [ ] T030 [US2] Display tags as TagChips in TaskItem in frontend/components/tasks/TaskItem.tsx
- [ ] T031 [US2] Update agent system prompt for tag commands in backend/app/chatkit/agent.py

**Checkpoint**: US2 complete - tasks can have tags added/removed via UI and chatbot

---

## Phase 5: User Story 3 - Filter Tasks (Priority: P2)

**Goal**: Users can filter task list by status, priority, and tags

**Independent Test**: Apply filters individually and combined, verify filtered results

**Depends on**: US1 (priority), US2 (tags)

### Backend Implementation for US3

- [ ] T032 [US3] Add status query parameter to list_tasks endpoint in backend/app/routes/tasks.py
- [ ] T033 [US3] Add priority query parameter to list_tasks endpoint in backend/app/routes/tasks.py
- [ ] T034 [US3] Add tags query parameter (array) to list_tasks endpoint in backend/app/routes/tasks.py
- [ ] T035 [US3] Implement combined filter logic (AND) in list_tasks endpoint in backend/app/routes/tasks.py

### MCP Implementation for US3

- [ ] T036 [US3] Extend list_tasks MCP tool with priority filter parameter in backend/app/mcp_server/server.py
- [ ] T037 [US3] Extend list_tasks MCP tool with tags filter parameter in backend/app/mcp_server/server.py

### Frontend Implementation for US3

- [ ] T038 [P] [US3] Create FilterState type in frontend/lib/api.ts
- [ ] T039 [P] [US3] Update taskApi.list() to accept filter parameters in frontend/lib/api.ts
- [ ] T040 [US3] Create FilterBar component with status/priority/tags dropdowns in frontend/components/ui/FilterBar.tsx
- [ ] T041 [US3] Add filter state management to dashboard in frontend/app/dashboard/page.tsx
- [ ] T042 [US3] Integrate FilterBar into TaskList in frontend/components/tasks/TaskList.tsx
- [ ] T043 [US3] Update agent system prompt for filter queries in backend/app/chatkit/agent.py

**Checkpoint**: US3 complete - users can filter tasks by status/priority/tags via UI and chatbot

---

## Phase 6: User Story 4 - Search Tasks (Priority: P2)

**Goal**: Users can search tasks by keyword in title or description

**Independent Test**: Search for keyword, verify matching tasks appear, clear search

### Backend Implementation for US4

- [ ] T044 [US4] Add search query parameter to list_tasks endpoint in backend/app/routes/tasks.py
- [ ] T045 [US4] Implement ILIKE search on title and description in backend/app/routes/tasks.py

### MCP Implementation for US4

- [ ] T046 [US4] Extend list_tasks MCP tool with search parameter in backend/app/mcp_server/server.py

### Frontend Implementation for US4

- [ ] T047 [US4] Add search input to FilterBar in frontend/components/ui/FilterBar.tsx
- [ ] T048 [US4] Add debounced search state to dashboard in frontend/app/dashboard/page.tsx
- [ ] T049 [US4] Update agent system prompt for search queries in backend/app/chatkit/agent.py

**Checkpoint**: US4 complete - users can search tasks by keyword via UI and chatbot

---

## Phase 7: User Story 5 - Sort Tasks (Priority: P3)

**Goal**: Users can sort task list by priority or title

**Independent Test**: Select sort option, verify task order changes

### Backend Implementation for US5

- [ ] T050 [US5] Add sort_by and sort_dir query parameters to list_tasks endpoint in backend/app/routes/tasks.py
- [ ] T051 [US5] Implement priority sorting with CASE expression in backend/app/routes/tasks.py
- [ ] T052 [US5] Implement title alphabetical sorting in backend/app/routes/tasks.py

### MCP Implementation for US5

- [ ] T053 [US5] Extend list_tasks MCP tool with sort_by and sort_dir parameters in backend/app/mcp_server/server.py

### Frontend Implementation for US5

- [ ] T054 [US5] Add sort dropdown to FilterBar in frontend/components/ui/FilterBar.tsx
- [ ] T055 [US5] Add sort state management to dashboard in frontend/app/dashboard/page.tsx
- [ ] T056 [US5] Update agent system prompt for sort commands in backend/app/chatkit/agent.py

**Checkpoint**: US5 complete - users can sort tasks by priority/title via UI and chatbot

---

## Phase 8: User Story 6 - Natural Language Organization (Priority: P3)

**Goal**: Chatbot understands organization commands (priority, tags, filter, sort)

**Independent Test**: Issue natural language commands, verify correct tool execution

**Depends on**: US1-US5 (all organization features implemented)

- [ ] T057 [US6] Consolidate and finalize agent system prompt with all organization examples in backend/app/chatkit/agent.py
- [ ] T058 [US6] Test chatbot with "add high priority task" command
- [ ] T059 [US6] Test chatbot with "show work tasks" command
- [ ] T060 [US6] Test chatbot with "sort my tasks by priority" command

**Checkpoint**: US6 complete - chatbot fully supports organization commands

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements and validation

- [ ] T061 Add empty state message for filtered results with zero matches in frontend/components/tasks/TaskList.tsx
- [ ] T062 Ensure mobile responsiveness for FilterBar in frontend/components/ui/FilterBar.tsx
- [ ] T063 Verify user isolation - filters only apply to current user's tasks
- [ ] T064 Run quickstart.md validation checklist
- [ ] T065 Verify performance - filter/search results in <500ms

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - run migration first
- **Phase 2 (Foundational)**: Depends on Phase 1 - BLOCKS all user stories
- **Phase 3 (US1 Priority)**: Depends on Phase 2
- **Phase 4 (US2 Tags)**: Depends on Phase 2 - can run in parallel with US1
- **Phase 5 (US3 Filter)**: Depends on US1 + US2 (needs priority and tags to exist)
- **Phase 6 (US4 Search)**: Depends on Phase 2 - can run in parallel with US3
- **Phase 7 (US5 Sort)**: Depends on Phase 2 - can run in parallel with US3/US4
- **Phase 8 (US6 Chatbot)**: Depends on US1-US5 (all features implemented)
- **Phase 9 (Polish)**: Depends on all user stories complete

### User Story Dependencies

```
Phase 1 (Migration)
    ↓
Phase 2 (Foundational)
    ↓
    ├── US1 (Priority) ─────┐
    ├── US2 (Tags) ─────────┼── US3 (Filter) depends on both
    │                       │
    ├── US4 (Search) ───────┘ can run parallel with US3
    └── US5 (Sort) ────────── can run parallel with US3/US4
                   ↓
              US6 (Chatbot NL) - after all organization features
                   ↓
              Phase 9 (Polish)
```

### Parallel Opportunities

**Within Phase 2**:
- T003, T005, T006 can run in parallel (different schema classes)

**Within US1**:
- T013, T014, T015 can run in parallel (different files)

**Within US2**:
- T021, T022 can run in parallel (different endpoints)
- T026, T027, T028 can run in parallel (different files)

**Within US3**:
- T038, T039 can run in parallel (different parts of api.ts)

**Cross-Story Parallelism** (after Phase 2):
- US1 and US2 can run in parallel
- US4 and US5 can run in parallel with US3

---

## Parallel Example: User Story 1

```bash
# After Phase 2 complete, launch US1 parallel tasks:

# Frontend parallel (different files):
Task: T013 "Update Task interface with priority in frontend/lib/api.ts"
Task: T014 "Update TaskCreate interface with priority in frontend/lib/api.ts"
Task: T015 "Create PriorityBadge component in frontend/components/ui/PriorityBadge.tsx"

# Then sequential:
Task: T016 "Add priority dropdown to TaskForm"
Task: T017 "Display PriorityBadge in TaskItem"
Task: T018 "Update agent system prompt for priority"
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Database Migration
2. Complete Phase 2: Foundational (model/schema updates)
3. Complete Phase 3: US1 (Priority)
4. Complete Phase 4: US2 (Tags)
5. **STOP and VALIDATE**: Tasks can have priority and tags - core organization works
6. Deploy/demo if ready

### Full Feature Set

1. Complete MVP (US1 + US2)
2. Add US3 (Filter) - now users can filter by priority/tags
3. Add US4 (Search) - can run parallel with US3
4. Add US5 (Sort) - can run parallel with US3/US4
5. Add US6 (Chatbot NL) - consolidate agent prompts
6. Polish (Phase 9) - edge cases, mobile, validation

### Single Developer Timeline

1. Day 1: Phase 1 + Phase 2 (foundation)
2. Day 2: US1 + US2 (priority + tags)
3. Day 3: US3 + US4 (filter + search)
4. Day 4: US5 + US6 + Polish

---

## Summary

| Phase | User Story | Task Count | Parallelizable |
|-------|-----------|------------|----------------|
| 1 | Setup | 1 | - |
| 2 | Foundational | 6 | 3 |
| 3 | US1 Priority | 11 | 4 |
| 4 | US2 Tags | 13 | 6 |
| 5 | US3 Filter | 12 | 3 |
| 6 | US4 Search | 6 | 0 |
| 7 | US5 Sort | 7 | 0 |
| 8 | US6 Chatbot | 4 | 0 |
| 9 | Polish | 5 | 0 |
| **Total** | | **65** | **16** |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story
- Each user story is independently testable after completion
- Tests not included (manual testing via quickstart.md)
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
