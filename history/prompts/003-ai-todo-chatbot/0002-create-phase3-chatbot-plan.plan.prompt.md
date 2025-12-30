---
id: "0002"
title: "Create Phase III AI Chatbot Implementation Plan"
stage: plan
date: 2025-12-29
surface: agent
model: claude-opus-4-5-20251101
feature: 003-ai-todo-chatbot
branch: 003-ai-todo-chatbot
user: safdarayub
command: /sp.plan
labels: ["phase3", "chatbot", "ai", "mcp", "fastmcp", "vercel-ai-sdk", "planning"]
links:
  spec: specs/003-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-ai-todo-chatbot/research.md
  - specs/003-ai-todo-chatbot/data-model.md
  - specs/003-ai-todo-chatbot/contracts/chat-api.md
  - specs/003-ai-todo-chatbot/contracts/mcp-tools.md
  - specs/003-ai-todo-chatbot/plan.md
  - specs/003-ai-todo-chatbot/quickstart.md
tests:
  - null
---

## Prompt

/sp.plan
Phase III: AI-Powered Todo Chatbot

Objective: Extend the Phase II full-stack multi-user Todo web application by integrating a conversational AI chatbot that enables authenticated users to manage their personal todo lists through natural language interactions.

Architecture sketch:
- Frontend: Embedded chat widget using OpenAI ChatKit (or similar React chat library)
- Agent: OpenAI Agents SDK Python with single-turn or multi-turn conversation handling
- MCP Server: Separate stateless Python server (FastMCP framework) exposing tools that wrap existing FastAPI task endpoints
- Tool Flow: ChatKit → Agents SDK → MCP server tools → existing FastAPI routes → SQLModel/Neon DB

Key integration points:
1. JWT auth token passed from frontend through agent to MCP server for user isolation
2. MCP tools: add_task, list_tasks, mark_complete, delete_task, update_task
3. Real-time sync: changes via chat immediately reflected in main task list

## Response snapshot

Created comprehensive implementation plan for Phase III AI-Powered Todo Chatbot using the **correct required tech stack**:

**Technology Decisions (research.md)**:
- Frontend: **OpenAI ChatKit** (`@openai/chatkit-react`) with `useChatKit` hook
- Backend: **ChatKit Python** (`chatkit`) + **OpenAI Agents SDK** (`agents`)
- AI Integration: OpenAI Agents SDK with `@function_tool` decorators
- Transport: SSE (Server-Sent Events) for streaming responses
- Authentication: Better Auth session → client_secret → user_id isolation

**Architecture**:
- ChatKit widget at `/chat` route using `useChatKit` hook
- Next.js API routes `/api/chatkit/session` and `/api/chatkit/refresh` for auth
- ChatKitServer mounted at `/chatkit` on existing FastAPI backend
- 5 Agent tools: add_task, list_tasks, mark_complete, delete_task, update_task

**Key Artifacts Created/Updated**:
1. `research.md` - Technology research with correct stack (OpenAI ChatKit + Agents SDK)
2. `data-model.md` - UIMessage, ChatSession, tool schemas
3. `contracts/chat-api.md` - ChatKit API contract with session management
4. `contracts/mcp-tools.md` - Tool definitions using @function_tool
5. `plan.md` - Full implementation plan with ChatKit architecture
6. `quickstart.md` - Developer setup guide with correct packages

**Implementation Phases**:
- Phase A: Backend ChatKit Server (4-5 files)
- Phase B: Frontend ChatKit Integration (3-4 files)
- Phase C: Integration & Testing (2 files)
- Phase D: Polish & Demo (1 file)

## Outcome

- ✅ Impact: High - Complete implementation plan for Phase III AI chatbot feature
- 🧪 Tests: N/A - Planning phase
- 📁 Files: 6 created/updated (research.md, data-model.md, 2 contracts, plan.md, quickstart.md)
- 🔁 Next prompts: /sp.tasks to generate implementation task list, then /sp.implement
- 🧠 Reflection: Corrected tech stack to use OpenAI ChatKit + Agents SDK per Phase III requirements

## Evaluation notes (flywheel)

- Failure modes observed: Initial plan used wrong tech stack (Vercel AI SDK), corrected after user feedback
- Graders run and results (PASS/FAIL): PASS - Constitution check passed, correct tech stack applied
- Prompt variant (if applicable): Standard /sp.plan flow with Context7 MCP for documentation lookup
- Next experiment (smallest change to try): Proceed to task generation with /sp.tasks
