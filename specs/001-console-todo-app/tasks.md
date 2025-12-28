# Tasks: Phase I Console Todo App

**Input**: Design documents from `/specs/001-console-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/cli-commands.md

**Tests**: Manual interactive testing only (no automated tests for Phase I as per plan.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, at repository root
- Paths shown below use this structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure

- [x] T001 Create project directory structure per plan.md: src/, src/models/, src/storage/, src/cli/
- [x] T002 Initialize UV project with Python 3.13+ in pyproject.toml
- [x] T003 [P] Create package markers: src/__init__.py, src/models/__init__.py, src/storage/__init__.py, src/cli/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Create Task dataclass with id, title, description, completed fields in src/models/task.py
- [x] T005 Create TaskStore class with internal list and ID counter in src/storage/memory.py
- [x] T006 Implement TaskStore.add() method for creating tasks in src/storage/memory.py
- [x] T007 Implement TaskStore.get() method for finding task by ID in src/storage/memory.py
- [x] T008 Implement TaskStore.list_all() method for returning all tasks in src/storage/memory.py
- [x] T009 Create menu display function with all 6 options in src/cli/menu.py
- [x] T010 Create get_user_choice() function with input validation in src/cli/menu.py
- [x] T011 Create main.py entry point with REPL loop skeleton in src/main.py

**Checkpoint**: Foundation ready - user story implementation can begin

---

## Phase 3: User Story 1 - View Task List (Priority: P1)

**Goal**: Display all tasks with ID, status indicator, and title

**Independent Test**: Launch app, select "list" - see "No tasks found" or formatted task list

### Implementation for User Story 1

- [x] T012 [US1] Create list_tasks handler function in src/cli/handlers.py
- [x] T013 [US1] Implement empty list case with "No tasks found." message in src/cli/handlers.py
- [x] T014 [US1] Implement task display with ID, status ([x]/[ ]), title format in src/cli/handlers.py
- [x] T015 [US1] Add description display (indented) when present in src/cli/handlers.py
- [x] T016 [US1] Wire list_tasks handler to menu choice "2" in src/main.py

**Checkpoint**: User Story 1 complete - can list tasks independently

---

## Phase 4: User Story 2 - Add New Task (Priority: P1)

**Goal**: Create new tasks with title and optional description

**Independent Test**: Select "add", enter title/description, verify task appears in list

### Implementation for User Story 2

- [x] T017 [US2] Create add_task handler function in src/cli/handlers.py
- [x] T018 [US2] Implement title input with empty validation in src/cli/handlers.py
- [x] T019 [US2] Implement optional description input in src/cli/handlers.py
- [x] T020 [US2] Call TaskStore.add() and display confirmation message in src/cli/handlers.py
- [x] T021 [US2] Wire add_task handler to menu choice "1" in src/main.py

**Checkpoint**: User Stories 1 AND 2 complete - can add and view tasks

---

## Phase 5: User Story 3 - Mark Task Complete/Incomplete (Priority: P2)

**Goal**: Toggle completion status of tasks

**Independent Test**: Add task, toggle complete, verify [x] indicator, toggle again, verify [ ]

### Implementation for User Story 3

- [x] T022 [US3] Implement TaskStore.toggle_complete() method in src/storage/memory.py
- [x] T023 [US3] Create toggle_complete handler function in src/cli/handlers.py
- [x] T024 [US3] Implement ID input with validation (numeric, positive, exists) in src/cli/handlers.py
- [x] T025 [US3] Display appropriate confirmation message (marked complete/incomplete) in src/cli/handlers.py
- [x] T026 [US3] Wire toggle_complete handler to menu choice "5" in src/main.py

**Checkpoint**: User Stories 1, 2, AND 3 complete - core todo functionality working

---

## Phase 6: User Story 4 - Update Task Details (Priority: P3)

**Goal**: Modify title and/or description of existing tasks

**Independent Test**: Add task, update title/description, verify changes in list view

### Implementation for User Story 4

- [x] T027 [US4] Implement TaskStore.update() method in src/storage/memory.py
- [x] T028 [US4] Create update_task handler function in src/cli/handlers.py
- [x] T029 [US4] Implement ID input with validation in src/cli/handlers.py
- [x] T030 [US4] Display current title and prompt for new (Enter to keep) in src/cli/handlers.py
- [x] T031 [US4] Validate new title is non-empty if provided in src/cli/handlers.py
- [x] T032 [US4] Display current description and prompt for new in src/cli/handlers.py
- [x] T033 [US4] Wire update_task handler to menu choice "3" in src/main.py

**Checkpoint**: User Stories 1-4 complete

---

## Phase 7: User Story 5 - Delete Task (Priority: P3)

**Goal**: Remove tasks from the list

**Independent Test**: Add task, delete it, verify it no longer appears in list

### Implementation for User Story 5

- [x] T034 [US5] Implement TaskStore.delete() method in src/storage/memory.py
- [x] T035 [US5] Create delete_task handler function in src/cli/handlers.py
- [x] T036 [US5] Implement ID input with validation in src/cli/handlers.py
- [x] T037 [US5] Display confirmation message after deletion in src/cli/handlers.py
- [x] T038 [US5] Wire delete_task handler to menu choice "4" in src/main.py

**Checkpoint**: All 5 user stories complete - full CRUD functionality

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, edge cases, and application polish

- [x] T039 Implement quit handler with "Goodbye!" message in src/main.py
- [x] T040 Add KeyboardInterrupt (Ctrl+C) handling with graceful exit in src/main.py
- [x] T041 Add invalid menu choice error handling in src/main.py
- [x] T042 Create helper function for ID input validation (reuse in US3, US4, US5) in src/cli/menu.py
- [x] T043 Run quickstart.md demo workflow validation (manual testing)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (View List): No dependencies on other stories
  - US2 (Add Task): No dependencies on other stories
  - US3 (Toggle Complete): No dependencies on other stories
  - US4 (Update Task): No dependencies on other stories
  - US5 (Delete Task): No dependencies on other stories
- **Polish (Phase 8)**: Depends on all user stories complete

### User Story Independence

All user stories can be implemented in any order after Foundational phase:

```
Phase 2 Complete
      │
      ├──▶ US1 (View List)      ──┐
      ├──▶ US2 (Add Task)        │
      ├──▶ US3 (Toggle Complete) ├──▶ Phase 8 (Polish)
      ├──▶ US4 (Update Task)     │
      └──▶ US5 (Delete Task)    ──┘
```

However, **recommended order** is P1 → P2 → P3 for practical testing:
- US2 (Add) enables testing US1 (List)
- US1 + US2 enable testing US3, US4, US5

### Within Each Phase

- Tasks within Setup can run in parallel (different files)
- Foundational tasks must be sequential (dependencies between storage operations)
- Within each user story: Sequential order as numbered

### Parallel Opportunities

```bash
# Phase 1: All setup tasks in parallel
T001: Create directory structure
T002: Initialize UV project (parallel with T003)
T003: Create package markers (parallel with T002)

# Phase 2: Sequential (dependencies)
T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011

# User Stories: Can run in parallel if team capacity allows
US1 Team: T012 → T013 → T014 → T015 → T016
US2 Team: T017 → T018 → T019 → T020 → T021
# etc.
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 4: User Story 2 (Add Task) - need tasks to view
4. Complete Phase 3: User Story 1 (View Task List)
5. **STOP and VALIDATE**: Test add + list independently
6. Demo: Add tasks, list them

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US2 + US1 → MVP: Add and View (Demo!)
3. Add US3 → Toggle completion (Demo!)
4. Add US4 → Update tasks (Demo!)
5. Add US5 → Delete tasks (Demo!)
6. Polish → Production ready

### File Creation Order

```
1. pyproject.toml
2. src/__init__.py, src/models/__init__.py, src/storage/__init__.py, src/cli/__init__.py
3. src/models/task.py
4. src/storage/memory.py
5. src/cli/menu.py
6. src/cli/handlers.py
7. src/main.py
```

---

## Task Summary

| Phase | Tasks | Story | Status |
|-------|-------|-------|--------|
| 1. Setup | T001-T003 (3) | - | ✅ Complete |
| 2. Foundational | T004-T011 (8) | - | ✅ Complete |
| 3. View List | T012-T016 (5) | US1 | ✅ Complete |
| 4. Add Task | T017-T021 (5) | US2 | ✅ Complete |
| 5. Toggle Complete | T022-T026 (5) | US3 | ✅ Complete |
| 6. Update Task | T027-T033 (7) | US4 | ✅ Complete |
| 7. Delete Task | T034-T038 (5) | US5 | ✅ Complete |
| 8. Polish | T039-T043 (5) | - | ✅ Complete |
| **Total** | **43 tasks** | **5 stories** | **✅ All Complete** |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each phase or logical group
- Stop at any checkpoint to validate story independently
- All file paths are relative to repository root
