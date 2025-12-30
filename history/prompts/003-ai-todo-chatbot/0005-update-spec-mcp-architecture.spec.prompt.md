---
id: "0005"
title: "Update Spec with MCP Architecture"
stage: spec
date: 2025-12-29
surface: agent
model: claude-opus-4-5-20251101
feature: 003-ai-todo-chatbot
branch: 003-ai-todo-chatbot
user: safdarayub
command: /sp.specify
labels: ["mcp", "architecture", "spec-update", "phase3"]
links:
  spec: specs/003-ai-todo-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/003-ai-todo-chatbot/spec.md
  - specs/003-ai-todo-chatbot/checklists/requirements.md
tests:
  - Specification quality checklist passed
---

## Prompt

Update the existing 003-ai-todo-chatbot spec to clarify MCP Server requirement. The current implementation uses @function_tool decorators but the hackathon requires building an MCP Server using the Official MCP SDK (mcp Python package). The OpenAI Agents SDK should connect to and use MCP tools for task operations (add_task, list_tasks, complete_task, delete_task, update_task). Update the spec to reflect this MCP-based architecture.

## Response snapshot

Updated spec.md with MCP architecture requirements:

1. **Added Architecture Overview section** with:
   - System architecture diagram showing MCP Server layer
   - MCP Server architecture explanation
   - MCP Tools specification table (5 tools)
   - Technology stack table

2. **Added MCP Server Requirements (FR-016 to FR-022)**:
   - FR-016: Must use Official MCP SDK
   - FR-017: Must expose 5 tools
   - FR-018: User isolation via user_id parameter
   - FR-019: Agent must connect via MCP protocol
   - FR-020: Stateless operations
   - FR-021: Response schema compliance
   - FR-022: In-process MCP Server

3. **Added Conversation Persistence Requirements (FR-023 to FR-025)**:
   - Database persistence for chat history
   - Server restart resume support
   - Message schema definition

4. **Updated Key Entities** for database-persisted Conversation and Message models

5. **Updated Assumptions** with MCP architecture assumptions

6. **Created requirements checklist** - all items passed

## Outcome

- Impact: High - Spec now correctly reflects hackathon MCP requirement
- Tests: Specification quality checklist passed
- Files: 2 files created/updated
- Next prompts: /sp.plan to update implementation plan with MCP architecture
- Reflection: Original spec missed MCP requirement; now aligned with hackathon mandate

## Evaluation notes (flywheel)

- Failure modes observed: Original implementation used @function_tool instead of MCP
- Graders run and results (PASS/FAIL): PASS - Checklist validation complete
- Prompt variant (if applicable): Spec update (not new feature)
- Next experiment (smallest change to try): Run /sp.plan to generate MCP implementation plan
