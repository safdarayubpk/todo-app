# Feature Specification: AI-Powered Todo Chatbot

**Feature Branch**: `003-ai-todo-chatbot`
**Created**: 2025-12-29
**Updated**: 2025-12-29
**Status**: Draft (Updated for MCP Architecture)
**Input**: User description: "Phase III: AI-Powered Todo Chatbot - Extend the Phase II full-stack multi-user Todo web application by integrating a conversational AI chatbot that enables authenticated users to manage their personal todo lists through natural language interactions."

## Architecture Overview *(mandatory)*

### System Architecture

The chatbot follows a layered architecture where the AI agent communicates with task operations through an **MCP (Model Context Protocol) Server**:

```
┌─────────────────┐     ┌──────────────────────────────────────────────┐     ┌─────────────────┐
│                 │     │              FastAPI Server                   │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │     │                 │
│  ChatKit UI     │────▶│  │         Chat Endpoint                  │  │     │    Neon DB      │
│  (Frontend)     │     │  │  POST /api/chat                        │  │     │  (PostgreSQL)   │
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │
│                 │     │                  │                           │     │  - tasks        │
│                 │     │                  ▼                           │     │  - conversations│
│                 │     │  ┌────────────────────────────────────────┐  │     │  - messages     │
│                 │◀────│  │      OpenAI Agents SDK                 │  │     │                 │
│                 │     │  │      (Agent + Runner)                  │  │     │                 │
│                 │     │  └───────────────┬────────────────────────┘  │     │                 │
│                 │     │                  │                           │     │                 │
│                 │     │                  ▼                           │     │                 │
│                 │     │  ┌────────────────────────────────────────┐  │────▶│                 │
│                 │     │  │         MCP Server                     │  │     │                 │
│                 │     │  │  (Official MCP SDK - Task Tools)       │  │◀────│                 │
│                 │     │  └────────────────────────────────────────┘  │     │                 │
└─────────────────┘     └──────────────────────────────────────────────┘     └─────────────────┘
```

### MCP Server Architecture

The system MUST implement an **MCP Server using the Official MCP SDK** (`mcp` Python package) that exposes task operations as standardized tools. The OpenAI Agents SDK connects to this MCP Server to execute task operations.

**Key Architecture Principles:**
1. **MCP as Tool Layer**: All task operations (CRUD) are exposed as MCP tools, not direct function calls
2. **Protocol-Based Communication**: The AI agent communicates with task tools via the MCP protocol
3. **Stateless Operations**: Both the chat endpoint and MCP tools are stateless; state is persisted to database
4. **User Isolation**: Every MCP tool operation requires user_id and enforces data isolation

### MCP Tools Specification

The MCP Server MUST expose the following 5 tools:

| Tool | Purpose | Parameters | Returns |
|------|---------|------------|---------|
| `add_task` | Create a new task | user_id (required), title (required), description (optional) | task_id, status, title |
| `list_tasks` | Retrieve user's tasks | user_id (required), status (optional: "all", "pending", "completed") | Array of task objects |
| `complete_task` | Mark a task as complete | user_id (required), task_id (required) | task_id, status, title |
| `delete_task` | Remove a task | user_id (required), task_id (required) | task_id, status, title |
| `update_task` | Modify task details | user_id (required), task_id (required), title (optional), description (optional) | task_id, status, title |

### Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | OpenAI ChatKit | Chat UI widget |
| Backend | Python FastAPI | API server |
| AI Framework | OpenAI Agents SDK | Agent logic and runner |
| **Tool Protocol** | **Official MCP SDK** | **Task tools via MCP protocol** |
| ORM | SQLModel | Database operations |
| Database | Neon PostgreSQL | Persistent storage |
| Authentication | Better Auth (JWT) | User identity |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add Task via Natural Language (Priority: P1)

An authenticated user opens the chatbot interface and types "Add a task to buy groceries". The AI understands the intent, creates the task, and confirms the action with a friendly response showing the created task.

**Why this priority**: Adding tasks is the most fundamental operation. If users can create tasks via chat, the core value proposition of natural language task management is proven.

**Independent Test**: Can be fully tested by logging in, opening the chatbot, typing "Add a task to [description]", and verifying the task appears in both the chat response and the main task list. Delivers the ability to create tasks without using forms.

**Acceptance Scenarios**:

1. **Given** an authenticated user in the chatbot interface, **When** they type "Add a task to buy milk", **Then** the system creates a new task with title "buy milk" and the bot confirms with "I've added 'buy milk' to your tasks."
2. **Given** an authenticated user in the chatbot interface, **When** they type "Create task: Call dentist tomorrow", **Then** the system creates a task titled "Call dentist tomorrow" and confirms the creation.
3. **Given** an authenticated user in the chatbot interface, **When** they type "Add task" without a description, **Then** the bot asks "What would you like to add to your task list?"

---

### User Story 2 - View Tasks via Natural Language (Priority: P1)

An authenticated user asks the chatbot to show their tasks. The bot retrieves and displays the user's tasks in a clear, formatted list.

**Why this priority**: Viewing tasks is essential for users to understand what they have. Combined with adding tasks, this enables a complete read/write experience.

**Independent Test**: Can be fully tested by logging in, having some tasks, opening the chatbot, and typing "Show my tasks" to see a formatted list. Delivers visibility into the user's task list via conversation.

**Acceptance Scenarios**:

1. **Given** an authenticated user with 3 tasks, **When** they type "Show my tasks", **Then** the bot displays all 3 tasks with their titles and completion status.
2. **Given** an authenticated user with tasks, **When** they type "What's on my todo list?", **Then** the bot displays their tasks in a readable format.
3. **Given** an authenticated user with no tasks, **When** they type "Show my tasks", **Then** the bot responds "You don't have any tasks yet. Would you like to add one?"
4. **Given** an authenticated user with tasks, **When** they type "Show incomplete tasks", **Then** the bot displays only tasks that are not marked as complete.

---

### User Story 3 - Mark Task Complete via Natural Language (Priority: P2)

An authenticated user tells the chatbot to mark a specific task as complete. The bot identifies the task, toggles its status, and confirms the action.

**Why this priority**: Completing tasks is the primary workflow after creating them. This enables users to track progress through conversation.

**Independent Test**: Can be fully tested by having an incomplete task, typing "Mark [task name] as done", and verifying the task status changes in both the chat response and the main task list. Delivers task completion via natural language.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a task "buy milk", **When** they type "Mark buy milk as done", **Then** the bot marks the task complete and confirms "I've marked 'buy milk' as complete."
2. **Given** an authenticated user with a completed task, **When** they type "Mark [task] as incomplete", **Then** the bot toggles the status back and confirms.
3. **Given** an authenticated user with multiple tasks containing similar words, **When** they type "Complete the meeting task", **Then** the bot asks for clarification: "I found multiple tasks with 'meeting'. Which one did you mean?" and lists the options.

---

### User Story 4 - Delete Task via Natural Language (Priority: P2)

An authenticated user asks the chatbot to delete a specific task. The bot identifies the task, removes it, and confirms the deletion.

**Why this priority**: Deleting tasks helps users maintain a clean list. Essential for complete task management but less frequently used than add/view/complete.

**Independent Test**: Can be fully tested by having a task, typing "Delete [task name]", confirming if prompted, and verifying the task is removed from both the chat response and the main task list. Delivers task deletion via conversation.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a task "buy milk", **When** they type "Delete the buy milk task", **Then** the bot confirms "Are you sure you want to delete 'buy milk'?" and upon confirmation, removes the task.
2. **Given** an authenticated user, **When** they confirm task deletion, **Then** the bot responds "Done! I've deleted 'buy milk' from your tasks."
3. **Given** an authenticated user with no matching task, **When** they type "Delete the xyz task", **Then** the bot responds "I couldn't find a task matching 'xyz'. Here are your current tasks:" and lists them.

---

### User Story 5 - Update Task via Natural Language (Priority: P3)

An authenticated user asks the chatbot to update a task's title or description. The bot identifies the task, makes the update, and confirms the change.

**Why this priority**: Updating tasks is useful but less common than other operations. Users typically delete and recreate rather than edit.

**Independent Test**: Can be fully tested by having a task, typing "Rename [task] to [new name]", and verifying the change in both chat and task list. Delivers task editing via conversation.

**Acceptance Scenarios**:

1. **Given** an authenticated user with a task "buy milk", **When** they type "Change buy milk to buy groceries", **Then** the bot updates the task title and confirms "I've updated 'buy milk' to 'buy groceries'."
2. **Given** an authenticated user with a task, **When** they type "Add description to [task]: [description text]", **Then** the bot adds the description and confirms.

---

### User Story 6 - Seamless Integration with Task List (Priority: P2)

When a user performs any action via the chatbot, the main task list updates in real-time. Similarly, changes made in the standard UI are reflected when the user asks the chatbot about their tasks.

**Why this priority**: Integration ensures consistency. Users should trust that the chatbot and UI show the same data.

**Independent Test**: Can be fully tested by adding a task via chat, switching to the main task view, and verifying the task appears without refresh. Delivers unified task management experience.

**Acceptance Scenarios**:

1. **Given** an authenticated user on the dashboard, **When** they add a task via chatbot, **Then** the task immediately appears in the main task list without page refresh.
2. **Given** an authenticated user who just added a task via the UI, **When** they ask the chatbot "Show my tasks", **Then** the newly added task is included in the response.

---

### User Story 7 - Chat History Persistence (Priority: P3)

The chatbot maintains conversation history during the user's session, allowing them to refer back to previous interactions.

**Why this priority**: Nice-to-have feature that improves user experience but is not critical for core functionality.

**Independent Test**: Can be fully tested by having a conversation with multiple messages, scrolling up, and verifying previous messages are still visible. Delivers conversation context within a session.

**Acceptance Scenarios**:

1. **Given** an authenticated user who has exchanged 5 messages with the chatbot, **When** they scroll up in the chat interface, **Then** all previous messages are visible.
2. **Given** an authenticated user who logs out and logs back in, **When** they open the chatbot, **Then** they start with a fresh conversation (no cross-session persistence required).

---

### Edge Cases

- What happens when the user's input is ambiguous (e.g., "Delete it")? The bot asks for clarification about which task.
- What happens when multiple tasks match the user's description? The bot lists matching tasks and asks the user to be more specific.
- What happens when the AI cannot understand the user's intent? The bot responds with helpful suggestions: "I didn't quite understand that. You can try: 'Add a task', 'Show my tasks', 'Mark [task] as done', or 'Delete [task]'."
- What happens if the backend is temporarily unavailable? The bot displays a user-friendly error: "I'm having trouble connecting right now. Please try again in a moment."
- What happens if a user tries to access another user's tasks? The system enforces user isolation at all levels; the chatbot only ever sees/operates on the authenticated user's tasks.
- What happens with very long task titles in chat? The bot truncates display to reasonable length with "..." while preserving full data.

## Requirements *(mandatory)*

### Functional Requirements

#### Core Chatbot Requirements
- **FR-001**: System MUST provide a chatbot interface accessible only to authenticated users.
- **FR-002**: System MUST interpret natural language commands to add tasks (e.g., "Add task to...", "Create a task for...").
- **FR-003**: System MUST interpret natural language queries to list tasks (e.g., "Show my tasks", "What's on my list?").
- **FR-004**: System MUST interpret natural language commands to complete tasks (e.g., "Mark X as done", "Complete X").
- **FR-005**: System MUST interpret natural language commands to delete tasks (e.g., "Delete X", "Remove X task").
- **FR-006**: System MUST interpret natural language commands to update tasks (e.g., "Rename X to Y", "Change X to Y").
- **FR-007**: System MUST enforce user isolation - chatbot operations only affect the authenticated user's tasks.
- **FR-008**: System MUST handle ambiguous requests by asking clarifying questions.
- **FR-009**: System MUST confirm all destructive actions (delete) before executing.
- **FR-010**: System MUST provide helpful error messages when intent cannot be determined.
- **FR-011**: System MUST synchronize changes between chatbot and standard task list UI in real-time.
- **FR-012**: System MUST maintain chat history within the current user session.
- **FR-013**: System MUST pass the user's authentication context securely to all backend operations.
- **FR-014**: System MUST display the chatbot in an embedded interface within the existing application.
- **FR-015**: System MUST provide a responsive chat interface that works on both desktop and mobile.

#### MCP Server Requirements (Architecture Mandate)
- **FR-016**: System MUST implement an MCP Server using the **Official MCP SDK** (`mcp` Python package).
- **FR-017**: The MCP Server MUST expose exactly 5 tools: `add_task`, `list_tasks`, `complete_task`, `delete_task`, `update_task`.
- **FR-018**: Each MCP tool MUST accept `user_id` as a required parameter to enforce user isolation.
- **FR-019**: The OpenAI Agents SDK MUST connect to the MCP Server to execute task operations (not direct function calls).
- **FR-020**: MCP tools MUST be stateless - all state persisted to database.
- **FR-021**: MCP tool responses MUST follow the schema defined in the Architecture section (task_id, status, title/array).
- **FR-022**: The MCP Server MUST run within the FastAPI backend process (in-process, not separate service).

#### Conversation Persistence Requirements
- **FR-023**: System MUST persist conversation history to database (not in-memory only).
- **FR-024**: System MUST support resuming conversations after server restart.
- **FR-025**: Each message MUST be stored with: conversation_id, role (user/assistant), content, timestamp.

### Key Entities

- **Conversation**: Represents a chat session persisted to database. Attributes: id, user_id, created_at, updated_at. One user can have multiple conversations.
- **Message**: Represents a single message in a conversation. Attributes: id, conversation_id, user_id, role (user/assistant), content, created_at. Stored in database for persistence.
- **Task** (existing): Reuses existing Task entity from Phase II. No modifications required.
- **MCP Tool Call**: Represents an invocation of an MCP tool by the agent. Not persisted; exists only during request processing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can add a task via natural language in under 5 seconds from typing to confirmation.
- **SC-002**: The chatbot correctly interprets at least 90% of standard task commands (add, view, complete, delete, update).
- **SC-003**: When multiple tasks match a query, the chatbot asks for clarification 100% of the time instead of guessing.
- **SC-004**: Changes made via chatbot appear in the standard task list within 2 seconds without manual refresh.
- **SC-005**: Two different users can demonstrate completely isolated chatbot interactions (one user cannot see or modify another's tasks via chat).
- **SC-006**: The chatbot interface is fully functional on mobile devices with screen widths down to 320px.
- **SC-007**: Users receive helpful feedback for unrecognized commands within 1 second.
- **SC-008**: Live demo shows at least 5 different natural language interactions working correctly.
- **SC-009**: Chat history remains visible and scrollable throughout the user's session.
- **SC-010**: The chatbot gracefully handles backend errors with user-friendly messages.

## Assumptions

- Users have access to an OpenAI API key or the application will use a shared API key configured as an environment variable.
- The existing JWT authentication from Phase II will be leveraged to identify users for the chatbot.
- The AI model will be configured with appropriate system prompts to focus on task management only.
- Natural language processing will handle common variations but not every possible phrasing.
- The chatbot will use English language only.
- Response latency depends on external AI service performance; the system will show loading indicators during processing.

### MCP Architecture Assumptions
- The Official MCP SDK (`mcp` Python package from PyPI) will be used to implement the MCP Server.
- The MCP Server will run in-process with FastAPI (stdio transport or direct integration), not as a separate networked service.
- The OpenAI Agents SDK supports MCP tool integration (via `mcp_servers` parameter or equivalent).
- MCP tools will have direct database access for task operations (same connection pool as FastAPI).
- The MCP protocol overhead is acceptable for the chatbot use case (sub-second latency).

## Out of Scope

- Voice input or speech-to-text functionality
- Multi-language support (e.g., Urdu)
- Standalone chatbot deployment (must be embedded in existing app)
- Advanced task features (due dates, priorities, reminders, recurring tasks)
- Containerization, Kubernetes, Helm, or Dapr (reserved for Phases IV/V)
- Event-driven architecture with Kafka
- Proactive notifications or reminders from the chatbot
- Image or file attachments in chat
- Separate MCP Server process (MCP runs in-process with FastAPI)
- External MCP client connections (MCP is internal to the backend only)
