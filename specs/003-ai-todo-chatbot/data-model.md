# Data Model: AI-Powered Todo Chatbot (MCP Architecture)

**Feature**: 003-ai-todo-chatbot
**Date**: 2025-12-29 (Updated)
**Spec**: [spec.md](./spec.md)

## Overview

This document defines the data entities for the AI chatbot feature with MCP architecture. Per updated spec requirements (FR-023 to FR-025), chat history MUST be persisted to the database.

## Entity Relationship Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                       Backend (PostgreSQL via Neon)                       │
│                                                                           │
│  ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐ │
│  │      User       │ 1   * │  Conversation   │ 1   * │    Message      │ │
│  │   (Better Auth) │───────│   (NEW)         │───────│    (NEW)        │ │
│  └─────────────────┘       └─────────────────┘       └─────────────────┘ │
│          │                                                                │
│          │ 1                                                              │
│          │   *                                                            │
│          ▼                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐ │
│  │                        Task (existing)                               │ │
│  │  id | title | description | is_completed | user_id | created_at     │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘
```

## Entity Definitions

### 1. Conversation (NEW - Database Persisted)

Represents a chat session persisted to the database.

```python
# backend/app/models/conversation.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Conversation(SQLModel, table=True):
    """Represents a chat conversation session."""
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, max_length=255)
    title: Optional[str] = Field(default=None, max_length=255)  # Auto-generated from first message
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

**Attributes**:
| Field | Type | Description |
|-------|------|-------------|
| id | int | Primary key, auto-increment |
| user_id | str | Foreign key to Better Auth user |
| title | str? | Optional conversation title (auto-generated) |
| created_at | datetime | When conversation started |
| updated_at | datetime | Last message timestamp |

### 2. Message (NEW - Database Persisted)

Represents a single message in a conversation.

```python
# backend/app/models/message.py
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Message(SQLModel, table=True):
    """Represents a chat message."""
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    conversation_id: int = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True, max_length=255)
    role: str = Field(max_length=20)  # 'user' | 'assistant'
    content: str = Field()  # Message text content
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Attributes**:
| Field | Type | Description |
|-------|------|-------------|
| id | int | Primary key, auto-increment |
| conversation_id | int | Foreign key to conversation |
| user_id | str | Redundant for query efficiency |
| role | str | 'user' or 'assistant' |
| content | str | Message text content |
| created_at | datetime | When message was sent |

### 3. Task (Existing - No Changes)

The existing Task entity from Phase II remains unchanged.

```python
# From backend/app/models.py (existing)
class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    is_completed: bool = Field(default=False)
    user_id: str = Field(index=True, max_length=255)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
```

## MCP Tool Schemas (Updated with user_id)

All MCP tools require `user_id` as the first parameter for data isolation.

### add_task

```json
{
  "name": "add_task",
  "description": "Add a new task to the user's todo list",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "The authenticated user's ID (required for isolation)"
      },
      "title": {
        "type": "string",
        "description": "Task title (1-255 characters)",
        "minLength": 1,
        "maxLength": 255
      },
      "description": {
        "type": "string",
        "description": "Optional task description (max 1000 characters)",
        "maxLength": 1000
      }
    },
    "required": ["user_id", "title"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "task_id": { "type": "integer" },
      "status": { "type": "string", "enum": ["created"] },
      "title": { "type": "string" }
    }
  }
}
```

### list_tasks

```json
{
  "name": "list_tasks",
  "description": "List all tasks for the specified user",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "The authenticated user's ID"
      },
      "status": {
        "type": "string",
        "enum": ["all", "pending", "completed"],
        "default": "all",
        "description": "Filter tasks by completion status"
      }
    },
    "required": ["user_id"]
  },
  "outputSchema": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "id": { "type": "integer" },
        "title": { "type": "string" },
        "description": { "type": "string", "nullable": true },
        "completed": { "type": "boolean" }
      }
    }
  }
}
```

### complete_task

```json
{
  "name": "complete_task",
  "description": "Mark a task as complete",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "The authenticated user's ID"
      },
      "task_id": {
        "type": "integer",
        "description": "The task ID to mark complete"
      }
    },
    "required": ["user_id", "task_id"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "task_id": { "type": "integer" },
      "status": { "type": "string", "enum": ["completed"] },
      "title": { "type": "string" }
    }
  }
}
```

### delete_task

```json
{
  "name": "delete_task",
  "description": "Delete a task from the user's list",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "The authenticated user's ID"
      },
      "task_id": {
        "type": "integer",
        "description": "The task ID to delete"
      }
    },
    "required": ["user_id", "task_id"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "task_id": { "type": "integer" },
      "status": { "type": "string", "enum": ["deleted"] },
      "title": { "type": "string" }
    }
  }
}
```

### update_task

```json
{
  "name": "update_task",
  "description": "Update a task's title or description",
  "inputSchema": {
    "type": "object",
    "properties": {
      "user_id": {
        "type": "string",
        "description": "The authenticated user's ID"
      },
      "task_id": {
        "type": "integer",
        "description": "The task ID to update"
      },
      "title": {
        "type": "string",
        "description": "New title for the task",
        "minLength": 1,
        "maxLength": 255
      },
      "description": {
        "type": "string",
        "description": "New description for the task",
        "maxLength": 1000
      }
    },
    "required": ["user_id", "task_id"]
  },
  "outputSchema": {
    "type": "object",
    "properties": {
      "task_id": { "type": "integer" },
      "status": { "type": "string", "enum": ["updated"] },
      "title": { "type": "string" }
    }
  }
}
```

## Database Migration

New tables required for conversation persistence:

```sql
-- Create conversations table
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Create messages table
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
```

## State Management

### Conversation Lifecycle

| Event | Action |
|-------|--------|
| First Message | Create new Conversation, save Message |
| User Message | Save Message (role='user') |
| AI Response | Save Message (role='assistant') |
| Page Load | Load recent Conversation for user |
| Page Unmount | Conversation persists (can resume) |

### Frontend State

```typescript
interface ChatState {
  conversationId: number | null;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}
```

## Data Validation Rules

### User ID Validation
- Required in all MCP tool calls
- Must match authenticated user's session
- Tools MUST validate user_id ownership

### Task ID Validation
- Must be a positive integer
- Must belong to the specified user_id
- Return error if not found or not owned

### Message Content
- Required, cannot be empty
- No length limit (but reasonable for chat)
- Stored as TEXT in PostgreSQL
