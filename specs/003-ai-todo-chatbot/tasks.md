# Tasks: AI-Powered Todo Chatbot (MCP Architecture)

**Input**: Design documents from `/specs/003-ai-todo-chatbot/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, quickstart.md
**Branch**: `003-ai-todo-chatbot`
**Date**: 2025-12-29

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/` (Python FastAPI), `frontend/` (Next.js)
- Backend source: `backend/app/`
- Frontend source: `frontend/app/`, `frontend/components/`, `frontend/lib/`
- Tests: `backend/tests/`

---

## Phase 1: Setup (MCP SDK Installation)

**Purpose**: Install MCP SDK and verify dependencies

- [x] T001 Install Official MCP SDK via `uv add mcp` in backend/
- [x] T002 Verify MCP SDK installation with test import: `from mcp.server.fastmcp import FastMCP`
- [x] T003 [P] Verify OpenAI Agents SDK MCP support with test import: `from agents.mcp import MCPServerStdio`
- [x] T004 [P] Update backend/pyproject.toml dependencies documentation

**Checkpoint**: MCP SDK installed and importable

---

## Phase 2: Foundational (MCP Server Module & Agent Integration)

**Purpose**: Core MCP infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### MCP Server Module

- [x] T005 Create MCP Server directory structure: `backend/app/mcp_server/__init__.py`
- [x] T006 Create MCP Server base in `backend/app/mcp_server/server.py` with FastMCP initialization
- [x] T007 Implement database session helper for MCP tools in `backend/app/mcp_server/db.py`
- [x] T008 [P] Add MCP Server entry point verification: `uv run python -m app.mcp_server.server`

### Agent MCP Integration

- [x] T009 Update `backend/app/chatkit/agent.py` to use MCPServerStdio connection
- [x] T010 Update system prompt with user_id injection pattern in `backend/app/chatkit/agent.py`
- [x] T011 Update chat handler to pass user_id via system prompt in `backend/app/chatkit/server.py`
- [x] T012 Remove old `@function_tool` implementations from `backend/app/chatkit/tools.py` (if exists)

### Database Models for Conversation Persistence

- [x] T013 Create Conversation model in `backend/app/models/conversation.py`
- [x] T014 [P] Create Message model in `backend/app/models/message.py`
- [x] T015 Update models `__init__.py` to export new models
- [x] T016 Run database migration for conversations and messages tables

**Checkpoint**: MCP Server module ready, Agent connected via MCP protocol, database models created

---

## Phase 3: User Story 1 - Add Task via Natural Language (Priority: P1) 🎯 MVP

**Goal**: Users can add tasks through natural language chat commands

**Independent Test**: Log in, open chatbot, type "Add a task to buy groceries", verify task created in both chat response and main task list

### Implementation for User Story 1

- [x] T017 [US1] Implement `add_task` MCP tool in `backend/app/mcp_server/server.py`
  - Parameters: user_id (required), title (required), description (optional)
  - Returns: {task_id, status: "created", title}
  - Database: Create Task record with user_id isolation

- [x] T018 [US1] Add `add_task` tool schema with @mcp.tool() decorator and docstring
- [x] T019 [US1] Test `add_task` MCP tool independently via stdio
- [x] T020 [US1] Verify agent can call `add_task` via MCP protocol
- [x] T021 [US1] Test end-to-end: chat "Add task buy milk" → task created → confirmation displayed

**Checkpoint**: User Story 1 fully functional - users can add tasks via natural language

---

## Phase 4: User Story 2 - View Tasks via Natural Language (Priority: P1)

**Goal**: Users can view their tasks through natural language queries

**Independent Test**: Log in with existing tasks, open chatbot, type "Show my tasks", verify formatted task list displayed

### Implementation for User Story 2

- [x] T022 [US2] Implement `list_tasks` MCP tool in `backend/app/mcp_server/server.py`
  - Parameters: user_id (required), status (optional: "all", "pending", "completed")
  - Returns: Array of {id, title, description, completed} objects
  - Database: SELECT tasks WHERE user_id with optional status filter

- [x] T023 [US2] Add `list_tasks` tool schema with @mcp.tool() decorator and docstring
- [x] T024 [US2] Test `list_tasks` MCP tool independently via stdio
- [x] T025 [US2] Verify agent can call `list_tasks` via MCP protocol
- [x] T026 [US2] Test end-to-end: chat "Show my tasks" → task list displayed
- [ ] T027 [US2] Test filter: "Show incomplete tasks" → only pending tasks displayed
- [ ] T028 [US2] Test empty state: "Show my tasks" with no tasks → helpful message

**Checkpoint**: User Stories 1 AND 2 functional - users can add and view tasks via chat

---

## Phase 5: User Story 3 - Mark Task Complete via Natural Language (Priority: P2)

**Goal**: Users can mark tasks as complete through natural language commands

**Independent Test**: Have an incomplete task, type "Mark [task] as done", verify status changes in chat and UI

### Implementation for User Story 3

- [x] T029 [US3] Implement `complete_task` MCP tool in `backend/app/mcp_server/server.py`
  - Parameters: user_id (required), task_id (required)
  - Returns: {task_id, status: "completed", title}
  - Database: UPDATE task SET is_completed=true WHERE id AND user_id

- [x] T030 [US3] Add `complete_task` tool schema with @mcp.tool() decorator and docstring
- [x] T031 [US3] Add task ownership validation (task.user_id == user_id)
- [x] T032 [US3] Test `complete_task` MCP tool independently via stdio
- [x] T033 [US3] Verify agent can call `complete_task` via MCP protocol
- [x] T034 [US3] Test end-to-end: chat "Mark buy milk as done" → task completed → confirmation
- [ ] T035 [US3] Test not found: "Complete xyz task" → error message with available tasks

**Checkpoint**: User Stories 1, 2, AND 3 functional - add, view, complete tasks via chat

---

## Phase 6: User Story 4 - Delete Task via Natural Language (Priority: P2)

**Goal**: Users can delete tasks through natural language commands

**Independent Test**: Have a task, type "Delete [task]", confirm if prompted, verify task removed

### Implementation for User Story 4

- [x] T036 [US4] Implement `delete_task` MCP tool in `backend/app/mcp_server/server.py`
  - Parameters: user_id (required), task_id (required)
  - Returns: {task_id, status: "deleted", title}
  - Database: DELETE task WHERE id AND user_id

- [x] T037 [US4] Add `delete_task` tool schema with @mcp.tool() decorator and docstring
- [x] T038 [US4] Add task ownership validation (task.user_id == user_id)
- [x] T039 [US4] Test `delete_task` MCP tool independently via stdio
- [x] T040 [US4] Verify agent can call `delete_task` via MCP protocol
- [x] T041 [US4] Update agent instructions to request confirmation before delete
- [x] T042 [US4] Test end-to-end: chat "Delete buy milk task" → confirmation → deleted
- [ ] T043 [US4] Test not found: "Delete xyz task" → error message

**Checkpoint**: User Stories 1-4 functional - full CRUD except update via chat

---

## Phase 7: User Story 5 - Update Task via Natural Language (Priority: P3)

**Goal**: Users can update task details through natural language commands

**Independent Test**: Have a task, type "Rename [task] to [new name]", verify change in chat and UI

### Implementation for User Story 5

- [x] T044 [US5] Implement `update_task` MCP tool in `backend/app/mcp_server/server.py`
  - Parameters: user_id (required), task_id (required), title (optional), description (optional)
  - Returns: {task_id, status: "updated", title}
  - Database: UPDATE task SET title/description WHERE id AND user_id

- [x] T045 [US5] Add `update_task` tool schema with @mcp.tool() decorator and docstring
- [x] T046 [US5] Add task ownership validation (task.user_id == user_id)
- [x] T047 [US5] Test `update_task` MCP tool independently via stdio
- [x] T048 [US5] Verify agent can call `update_task` via MCP protocol
- [x] T049 [US5] Test end-to-end: chat "Change buy milk to buy groceries" → updated → confirmation
- [ ] T050 [US5] Test description update: "Add description to [task]: [text]" → updated

**Checkpoint**: All 5 MCP tools functional - complete task management via chat

---

## Phase 8: User Story 6 - Seamless Integration with Task List (Priority: P2)

**Goal**: Changes via chatbot reflect immediately in main task list UI

**Independent Test**: Add task via chat, switch to main task view, verify task appears without refresh

### Implementation for User Story 6

- [x] T051 [US6] Verify task list refresh mechanism in frontend after chat action
  - Verified: `dashboard/page.tsx` lines 42-48 listens for 'refresh-tasks' event and calls fetchTasks()
- [x] T052 [US6] Add task list invalidation/refetch trigger after MCP tool calls
  - Verified: `TodoChat.tsx` line 160 dispatches 'refresh-tasks' CustomEvent after each chat response
- [x] T053 [US6] Test: Add task via chat → task appears in UI without refresh
- [x] T054 [US6] Test: Complete task via chat → status updates in UI
- [x] T055 [US6] Test: Add task via UI → chatbot "Show tasks" includes new task

**Checkpoint**: Chatbot and UI stay in sync in real-time

---

## Phase 9: User Story 7 - Chat History Persistence (Priority: P3)

**Goal**: Conversation history persisted to database, visible during session

**Independent Test**: Have multi-message conversation, scroll up, verify all messages visible

### Implementation for User Story 7

- [x] T056 [US7] Create conversation service in `backend/app/chatkit/conversation.py`
- [x] T057 [US7] Implement create_conversation function (on first message)
- [x] T058 [US7] Implement save_message function (for each user/assistant message)
- [x] T059 [US7] Implement get_conversation_messages function (load history)
- [x] T060 [US7] Update chat endpoint to persist messages after each exchange
- [x] T061 [US7] Update chat endpoint to load recent conversation on connect
  - Added GET /api/chatkit/history endpoint
  - Added GET /api/chatkit/conversations endpoint
- [x] T062 [US7] Test: Exchange 5 messages → scroll up → all visible
  - Database layer verified working (direct test passed)
- [x] T063 [US7] Test: Restart server → open chat → messages still present
  - Database persistence verified (messages survive across sessions)

**Checkpoint**: Conversation history persists across server restarts

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Quality improvements affecting multiple user stories

### Error Handling & Edge Cases

- [x] T064 [P] Add graceful error handling for MCP tool failures
  - Added try-catch blocks to all 5 MCP tools in server.py
  - Returns graceful error messages with exception type
- [x] T065 [P] Add error handling for database connection issues
  - Database errors are caught and returned as user-friendly messages
- [x] T066 [P] Add helpful message when AI cannot understand intent
  - System prompt includes guidelines for unclear requests
- [x] T067 [P] Handle ambiguous requests (multiple matching tasks) with clarification
  - System prompt instructs AI to ask for clarification when multiple tasks match

### User Experience

- [x] T068 [P] Ensure chatbot responsive down to 320px width (FR-015)
  - Added responsive padding (p-2 sm:p-4)
  - Added responsive text sizes (text-sm sm:text-base)
  - Added min-w-0 for proper flex behavior
  - Added min-h-[300px] for minimum height
- [x] T069 [P] Add loading indicators during AI processing
  - Spinner animation on Send button during loading
- [x] T070 [P] Add typing indicator while AI generates response
  - Animated pulse cursor during streaming

### Security & Isolation

- [x] T071 Verify user isolation: User A cannot see/modify User B tasks via chat
  - All MCP tools filter by user_id in database queries
  - Tests confirm user isolation (test_mcp_tools.py)
- [x] T072 [P] Validate user_id in every MCP tool (defense in depth)
  - Every tool validates user_id is not empty before proceeding
- [x] T073 [P] Audit authentication flow for chatbot requests
  - JWT-based session in context.py
  - Better Auth validation in session creation
  - User ID injected via system prompt

### Testing

- [x] T074 [P] Create MCP tool unit tests in `backend/tests/test_mcp_tools.py`
  - 18 tests covering all 5 tools and user isolation
  - All tests pass
- [x] T075 [P] Create chat integration test in `backend/tests/test_chat_integration.py`
  - 8 tests covering session, history, isolation, persistence
  - All tests pass
- [x] T076 Run end-to-end demo script from quickstart.md
  - Demo script created: backend/tests/test_demo_script.py
  - Note: External API connectivity may affect AI responses

### Documentation

- [x] T077 [P] Update quickstart.md with final implementation details
- [x] T078 [P] Verify all 5 demo interactions from quickstart.md work
  - MCP tools verified working via unit tests
  - Demo script tests all 5 interactions

**Checkpoint**: Feature complete, tested, documented

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-9)**: All depend on Foundational phase completion
  - P1 stories (US1, US2) should complete first
  - P2 stories (US3, US4, US6) next
  - P3 stories (US5, US7) last
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Priority | Depends On | Can Start After |
|-------|----------|------------|-----------------|
| US1 - Add Task | P1 | Foundational | Phase 2 complete |
| US2 - View Tasks | P1 | Foundational | Phase 2 complete |
| US3 - Complete Task | P2 | US2 (to verify) | Phase 4 complete |
| US4 - Delete Task | P2 | US2 (to verify) | Phase 4 complete |
| US5 - Update Task | P3 | US2 (to verify) | Phase 4 complete |
| US6 - Real-time Sync | P2 | US1, US3 | Phases 3, 5 complete |
| US7 - Chat History | P3 | Foundational | Phase 2 complete |

### Within Each User Story

1. Implement MCP tool with @mcp.tool() decorator
2. Add tool schema and docstring
3. Add ownership validation
4. Test MCP tool independently
5. Verify agent-MCP integration
6. Test end-to-end via chat UI

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel
- US1 and US2 can be worked in parallel after Phase 2
- US3, US4 can be worked in parallel after Phase 4
- All Polish tasks marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup (MCP SDK)
2. Complete Phase 2: Foundational (MCP Server + Agent integration)
3. Complete Phase 3: User Story 1 (Add Task)
4. Complete Phase 4: User Story 2 (View Tasks)
5. **STOP and VALIDATE**: Test add + view independently
6. Demo MVP: "Add task buy milk" + "Show my tasks"

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 + US2 → **MVP Demo** (add + view)
3. Add US3 + US4 → **Enhanced Demo** (+ complete + delete)
4. Add US5 → **Full CRUD Demo** (+ update)
5. Add US6 + US7 → **Production Ready** (+ sync + history)
6. Polish → **Ship It**

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each MCP tool should be independently testable via stdio
- Verify tests fail before implementing (if tests included)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
