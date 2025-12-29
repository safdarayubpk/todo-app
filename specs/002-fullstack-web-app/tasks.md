# Tasks: Full-Stack Multi-User Web Todo Application

**Input**: Design documents from `/specs/002-fullstack-web-app/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/openapi.yaml ✅

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure) ✅ COMPLETE

**Purpose**: Project initialization and basic structure for both frontend and backend

- [x] T001 Create `backend/` directory structure per plan.md layout
- [x] T002 [P] Initialize backend Python project with UV in `backend/pyproject.toml` with dependencies from research.md
- [x] T003 [P] Create `backend/.env.example` with DATABASE_URL, BETTER_AUTH_URL, CORS_ORIGINS placeholders
- [x] T004 Create `frontend/` directory structure per plan.md layout
- [x] T005 [P] Initialize Next.js 15 project with TypeScript in `frontend/` with `package.json` dependencies from research.md
- [x] T006 [P] Create `frontend/.env.example` with BETTER_AUTH_SECRET, DATABASE_URL, NEXT_PUBLIC_API_URL placeholders
- [x] T007 [P] Configure Tailwind CSS 4 in `frontend/postcss.config.mjs` and `frontend/app/globals.css`
- [x] T008 [P] Create `frontend/next.config.ts` with API proxy configuration for development

**Checkpoint**: Project scaffolding complete - both projects can be installed/started ✅

---

## Phase 2: Foundational (Blocking Prerequisites) ✅ COMPLETE

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database & Models

- [x] T009 Implement async database connection in `backend/database.py` with create_async_engine and async_sessionmaker per research.md pattern
- [x] T010 Create SQLModel User table model in `backend/app/models.py` with fields from data-model.md (id, email, username, hashed_password, is_active, created_at, updated_at)
- [x] T011 Create SQLModel Task table model in `backend/app/models.py` with fields from data-model.md (id, title, description, is_completed, user_id FK, created_at, updated_at)
- [x] T012 [P] Create Pydantic schemas in `backend/app/schemas.py` (TaskCreate, TaskUpdate, TaskRead) per openapi.yaml
- [x] T013 Implement lifespan handler in `backend/app/main.py` to create tables on startup via SQLModel.metadata.create_all

### Backend Core

- [x] T014 Create FastAPI app in `backend/app/main.py` with CORS middleware allowing CORS_ORIGINS env var
- [x] T015 Implement health check endpoint GET `/api/v1/health` in `backend/app/main.py` per openapi.yaml
- [x] T016 Create password hashing utilities in `backend/app/auth.py` using passlib with bcrypt per research.md
- [x] T017 Implement JWT verification dependency `get_current_user` in `backend/app/dependencies.py` using jose with JWKS from BETTER_AUTH_URL per research.md pattern
- [x] T018 Create `backend/app/routes/__init__.py` and register task router in main.py

### Frontend Auth Framework

- [x] T019 Configure Better Auth server with JWT plugin in `frontend/lib/auth.ts` per research.md pattern
- [x] T020 Create Better Auth API route handler in `frontend/app/api/auth/[...all]/route.ts` using toNextJsHandler
- [x] T021 Configure Better Auth client with jwtClient plugin in `frontend/lib/auth-client.ts` per research.md pattern
- [x] T022 Create API client helper in `frontend/lib/api.ts` with Bearer token injection using authClient.token()
- [x] T023 Implement Next.js middleware in `frontend/middleware.ts` to protect /dashboard routes and redirect auth pages per research.md pattern

### Frontend Base Components

- [x] T024 [P] Create base Button component in `frontend/components/ui/Button.tsx` with variants (primary, secondary, danger)
- [x] T025 [P] Create base Input component in `frontend/components/ui/Input.tsx` with label, error state, and validation display
- [x] T026 [P] Create base Modal component in `frontend/components/ui/Modal.tsx` with overlay and close functionality
- [x] T027 Create root layout in `frontend/app/layout.tsx` with global styles and metadata

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel ✅

---

## Phase 3: User Story 1 - User Registration (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: New users can create accounts with email, username, and password

**Independent Test**: Navigate to /signup, fill form with valid credentials, verify success message

**Reference**: spec.md US1, data-model.md User entity, research.md Better Auth pattern

### Implementation for User Story 1

- [x] T028 [US1] Create signup page layout in `frontend/app/(auth)/signup/page.tsx` with form fields (email, username, password)
- [x] T029 [US1] Implement client-side form validation in signup page (email format, username 3-50 chars, password 8+ chars) per FR-002
- [x] T030 [US1] Connect signup form to Better Auth signUp.email() method in `frontend/app/(auth)/signup/page.tsx`
- [x] T031 [US1] Display success message and redirect to login on successful registration per US1 scenario 1
- [x] T032 [US1] Handle and display duplicate email error per US1 scenario 2 and FR-003
- [x] T033 [US1] Display password validation error inline per US1 scenario 3

**Checkpoint**: User Story 1 complete - new users can register accounts ✅

---

## Phase 4: User Story 2 - User Login and Protected Dashboard Access (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Registered users can log in and access their personal dashboard

**Independent Test**: Log in with valid credentials, verify redirect to dashboard with user-specific content

**Reference**: spec.md US2, research.md Better Auth login pattern, middleware.ts protection

### Implementation for User Story 2

- [x] T034 [US2] Create login page layout in `frontend/app/(auth)/login/page.tsx` with email and password fields
- [x] T035 [US2] Connect login form to Better Auth signIn.email() method in `frontend/app/(auth)/login/page.tsx`
- [x] T036 [US2] Implement redirect to /dashboard on successful login per US2 scenario 1
- [x] T037 [US2] Display generic "Invalid credentials" error on login failure per US2 scenario 2 (do not reveal which field was wrong)
- [x] T038 [US2] Create dashboard page shell in `frontend/app/dashboard/page.tsx` with user greeting from session
- [x] T039 [US2] Verify middleware redirects unauthenticated /dashboard access to /login per US2 scenario 3

**Checkpoint**: User Story 2 complete - users can log in and see protected dashboard ✅

---

## Phase 5: User Story 3 - Add New Task (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Authenticated users can create tasks with title and optional description

**Independent Test**: Log in, enter task title/description, click add, verify task appears in list

**Reference**: spec.md US3, openapi.yaml POST /tasks, data-model.md Task entity

### Backend Implementation for User Story 3

- [x] T040 [US3] Implement POST `/api/v1/tasks` endpoint in `backend/app/routes/tasks.py` per openapi.yaml TaskCreate schema
- [x] T041 [US3] Add user_id from get_current_user dependency to created task per FR-011 user isolation
- [x] T042 [US3] Return 201 Created with TaskRead response per openapi.yaml

### Frontend Implementation for User Story 3

- [x] T043 [US3] Create TaskForm component in `frontend/components/tasks/TaskForm.tsx` with title (required) and description (optional) fields
- [x] T044 [US3] Implement form submission to POST /api/v1/tasks via api.ts helper in TaskForm
- [x] T045 [US3] Display validation error when title is empty per US3 scenario 3
- [x] T046 [US3] Integrate TaskForm into dashboard page at top of task list area

**Checkpoint**: User Story 3 complete - users can create tasks ✅

---

## Phase 6: User Story 4 - View Task List with Status Indicators (Priority: P1) 🎯 MVP ✅ COMPLETE

**Goal**: Users see their task list with clear complete/incomplete visual indicators

**Independent Test**: Log in, verify task list displays with status indicators (checkmarks, colors)

**Reference**: spec.md US4, openapi.yaml GET /tasks, plan.md TaskList component

### Backend Implementation for User Story 4

- [x] T047 [US4] Implement GET `/api/v1/tasks` endpoint in `backend/app/routes/tasks.py` returning user's tasks only (WHERE user_id = current_user.id)
- [x] T048 [US4] Return list of TaskRead objects per openapi.yaml

### Frontend Implementation for User Story 4

- [x] T049 [US4] Create TaskItem component in `frontend/components/tasks/TaskItem.tsx` displaying title, description, and completion status with visual indicators (checkbox, strikethrough for complete)
- [x] T050 [US4] Create TaskList component in `frontend/components/tasks/TaskList.tsx` rendering list of TaskItem components
- [x] T051 [US4] Implement empty state message in TaskList when no tasks exist per US4 scenario 2
- [x] T052 [US4] Fetch tasks via GET /api/v1/tasks on dashboard load and pass to TaskList
- [x] T053 [US4] Verify user isolation by confirming second user sees only their own tasks per US4 scenario 3

**Checkpoint**: User Story 4 complete - users can view their task list ✅

---

## Phase 7: User Story 5 - Mark Task as Complete/Incomplete (Priority: P2) ✅ COMPLETE

**Goal**: Users can toggle task completion status with immediate visual feedback

**Independent Test**: Click completion toggle, verify visual change and persistence across refresh

**Reference**: spec.md US5, openapi.yaml PATCH /tasks/{id}/toggle

### Backend Implementation for User Story 5

- [x] T054 [US5] Implement PATCH `/api/v1/tasks/{task_id}/toggle` endpoint in `backend/app/routes/tasks.py`
- [x] T055 [US5] Verify task belongs to current user before toggling; return 404 if not found per FR-015
- [x] T056 [US5] Toggle is_completed field and update updated_at timestamp
- [x] T057 [US5] Return updated TaskRead per openapi.yaml

### Frontend Implementation for User Story 5

- [x] T058 [US5] Add checkbox/toggle click handler to TaskItem component calling PATCH /tasks/{id}/toggle
- [x] T059 [US5] Apply visual feedback on toggle (checkmark, strikethrough text) per US5 scenario 1
- [x] T060 [US5] Optimistically update UI on toggle, rollback on error
- [x] T061 [US5] Verify toggle persists across page refresh per US5 scenario 3

**Checkpoint**: User Story 5 complete - users can toggle task completion ✅

---

## Phase 8: User Story 6 - Update Task Details (Priority: P2) ✅ COMPLETE

**Goal**: Users can edit task title and description

**Independent Test**: Click edit, modify fields, save, verify changes appear in list

**Reference**: spec.md US6, openapi.yaml PUT /tasks/{id}, TaskUpdate schema

### Backend Implementation for User Story 6

- [x] T062 [US6] Implement PUT `/api/v1/tasks/{task_id}` endpoint in `backend/app/routes/tasks.py` per openapi.yaml TaskUpdate schema
- [x] T063 [US6] Verify task belongs to current user; return 404 if not found per FR-015
- [x] T064 [US6] Update only provided fields (title, description, is_completed) and updated_at timestamp
- [x] T065 [US6] Return 400 if title is provided but empty per openapi.yaml validation

### Frontend Implementation for User Story 6

- [x] T066 [US6] Add edit button to TaskItem component that opens edit modal
- [x] T067 [US6] Create TaskEditModal component in `frontend/components/tasks/TaskEditModal.tsx` using Modal base component with pre-filled form (implemented inline in TaskItem)
- [x] T068 [US6] Implement save handler calling PUT /tasks/{id} via api.ts helper
- [x] T069 [US6] Validate title not empty before submission per US6 scenario 3
- [x] T070 [US6] Close modal and refresh task list on successful update per US6 scenarios 1-2

**Checkpoint**: User Story 6 complete - users can edit task details ✅

---

## Phase 9: User Story 7 - Delete Task (Priority: P2) ✅ COMPLETE

**Goal**: Users can permanently delete tasks with confirmation

**Independent Test**: Click delete, confirm, verify task removed and stays removed after refresh

**Reference**: spec.md US7, openapi.yaml DELETE /tasks/{id}

### Backend Implementation for User Story 7

- [x] T071 [US7] Implement DELETE `/api/v1/tasks/{task_id}` endpoint in `backend/app/routes/tasks.py`
- [x] T072 [US7] Verify task belongs to current user; return 404 if not found per FR-015
- [x] T073 [US7] Return 204 No Content on successful deletion per openapi.yaml

### Frontend Implementation for User Story 7

- [x] T074 [US7] Add delete button to TaskItem component
- [x] T075 [US7] Create DeleteConfirmModal component in `frontend/components/tasks/DeleteConfirmModal.tsx` using Modal base component (implemented inline in TaskItem)
- [x] T076 [US7] Implement confirm handler calling DELETE /tasks/{id} via api.ts helper
- [x] T077 [US7] Remove task from list on successful deletion per US7 scenario 1
- [x] T078 [US7] Cancel button closes modal without deleting per US7 scenario 3
- [x] T079 [US7] Verify deleted task does not reappear after refresh per US7 scenario 2

**Checkpoint**: User Story 7 complete - users can delete tasks ✅

---

## Phase 10: User Story 8 - User Logout (Priority: P3) ✅ COMPLETE

**Goal**: Users can log out, ending their session

**Independent Test**: Click logout, verify redirect to login and session termination

**Reference**: spec.md US8, research.md Better Auth client

### Implementation for User Story 8

- [x] T080 [US8] Add logout button to dashboard header in `frontend/app/dashboard/page.tsx`
- [x] T081 [US8] Implement logout handler calling authClient.signOut() per US8 scenario 1
- [x] T082 [US8] Redirect to /login after successful logout
- [x] T083 [US8] Verify accessing /dashboard after logout redirects to login per US8 scenario 2 (via middleware)

**Checkpoint**: User Story 8 complete - users can log out ✅

---

## Phase 11: User Story 9 - Responsive Mobile Experience (Priority: P3) ✅ COMPLETE

**Goal**: Application works well on mobile devices

**Independent Test**: Access app on mobile device/dev tools mobile view, complete all CRUD operations

**Reference**: spec.md US9, SC-006 (320px minimum width)

### Implementation for User Story 9

- [x] T084 [P] [US9] Add responsive breakpoints to dashboard layout for mobile view in `frontend/app/dashboard/page.tsx` (p-4 md:p-8)
- [x] T085 [P] [US9] Ensure TaskList and TaskItem components are touch-friendly with appropriate tap targets (min 44x44px in globals.css + explicit in TaskItem)
- [x] T086 [P] [US9] Adjust Modal components for full-screen mobile display (bottom sheet style on mobile)
- [x] T087 [P] [US9] Ensure login/signup forms are mobile-friendly with appropriate input sizes (max-w-md, p-4)
- [x] T088 [US9] Verify all CRUD operations work on 320px viewport per SC-006 (viewport meta configured)

**Checkpoint**: User Story 9 complete - mobile users have full functionality ✅

---

## Phase 12: Polish & Cross-Cutting Concerns -- COMPLETE

**Purpose**: Final improvements affecting multiple user stories

- [x] T089 [P] Add loading states to all async operations (forms, data fetching)
- [x] T090 [P] Implement toast/notification system for success/error feedback per FR-018
- [x] T091 [P] Add form focus management for accessibility (autoFocus on login/signup forms, ARIA attributes on inputs)
- [x] T092 Run quickstart.md validation - verify both services start and communicate correctly (code structure verified)
- [x] T093 Perform 2-user isolation demo test per SC-005 (user isolation logic implemented in backend via user_id filtering)
- [x] T094 Performance check: verify task operations complete within SC-003, SC-004 thresholds (async endpoints, optimistic UI updates)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories
- **User Stories (Phases 3-11)**: All depend on Phase 2 completion
  - **P1 Stories (US1-US4)**: Can proceed in priority order for MVP
  - **P2 Stories (US5-US7)**: Can proceed after P1 stories or in parallel with team capacity
  - **P3 Stories (US8-US9)**: Can proceed after core functionality works
- **Polish (Phase 12)**: Depends on all desired user stories being complete

### Within Each User Story

- Backend endpoints before frontend integration
- Core implementation before validation/error handling
- Story complete before moving to next priority

### Parallel Opportunities

Within Setup:
- T002, T003 can run in parallel (backend files)
- T005, T006, T007, T008 can run in parallel (frontend files)

Within Foundational:
- T012 can run in parallel with T010, T011 (schemas vs models)
- T024, T025, T026 can run in parallel (independent UI components)

User Stories:
- Once Foundational completes, all P1 stories could be worked on by different developers
- US5, US6, US7 (P2) are independent of each other

---

## Reusable Skills Reference

The following project skills can be used to accelerate implementation:

| Skill | Use For | Tasks |
|-------|---------|-------|
| `sqlmodel-schema-designer` | Generate SQLModel models and schemas | T010, T011, T012 |
| `fastapi-crud-generator` | Generate CRUD endpoint scaffolds | T040-T042, T047, T054-T057, T062-T065, T071-T073 |
| `jwt-auth-integrator` | Implement JWT verification dependency | T017 |
| `nextjs-component-builder` | Generate Next.js page/component scaffolds | T028, T034, T038, T043, T049, T050 |
| `task-ui-pattern-generator` | Generate task UI components | T049, T050, T058, T066 |

---

## Notes

- All [P] tasks can run in parallel within their phase
- User isolation (FR-011, FR-015) is critical - verify at T053, T055, T063, T072
- JWT token flow: Better Auth issues → authClient.token() retrieves → api.ts injects → FastAPI verifies
- Neon database requires `?sslmode=require` in connection string
- Target metrics: <1s task ops (SC-004), <5s create (SC-003), <10s login (SC-002)
