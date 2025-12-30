# Demo Script: AI-Powered Todo Chatbot

**Feature**: 003-ai-todo-chatbot
**Date**: 2025-12-29

## Prerequisites

1. Backend running on http://localhost:8000
2. Frontend running on http://localhost:3000
3. Valid OpenAI API key configured
4. Test user account created

## Setup

1. Log in to the application with test credentials
2. Navigate to http://localhost:3000/dashboard
3. Note the "Chat Assistant" button in the header
4. Click "Chat Assistant" to open /chat

## Demo Interactions (6+ required for SC-008)

### Interaction 1: Greeting and Capabilities

**User**: "What can you help me with?"

**Expected Response**: Bot explains its capabilities:
- Adding tasks
- Viewing tasks
- Marking tasks complete/incomplete
- Deleting tasks
- Updating tasks

---

### Interaction 2: Add a Task

**User**: "Add a task to prepare demo presentation"

**Expected Response**:
- Bot confirms task creation
- Shows task details (ID, title)
- Example: "I've added 'prepare demo presentation' to your tasks. (ID: 123)"

**Verification**: Task appears in dashboard task list (may need to refresh)

---

### Interaction 3: Add Another Task

**User**: "Create task: Review meeting notes, Description: From Monday's standup"

**Expected Response**:
- Task created with both title and description
- Confirmation message

---

### Interaction 4: List Tasks

**User**: "Show my tasks"

**Expected Response**:
- Formatted list of all tasks
- Shows completion status (○ for incomplete, ✓ for complete)
- Includes task IDs
- Example:
  ```
  Here are your tasks:
  ○ prepare demo presentation (ID: 123)
  ○ Review meeting notes (ID: 124)
  ```

---

### Interaction 5: Mark Complete

**User**: "Mark the presentation task as done"

**Expected Response**:
- Task marked complete
- Confirmation with checkmark
- Example: "Done! I've marked 'prepare demo presentation' as complete. ✓"

**Verification**: Dashboard shows task with completed styling

---

### Interaction 6: List Incomplete Tasks

**User**: "Show incomplete tasks"

**Expected Response**:
- Only incomplete tasks shown
- Example:
  ```
  Here are your incomplete tasks:
  ○ Review meeting notes (ID: 124)
  ```

---

### Interaction 7: Delete with Confirmation

**User**: "Delete the meeting notes task"

**Expected Response (Step 1)**:
- Bot asks for confirmation
- Example: "I found 'Review meeting notes' (ID: 124). Are you sure you want to delete it? This cannot be undone."

**User**: "Yes, delete it"

**Expected Response (Step 2)**:
- Task deleted
- Confirmation message
- Example: "Task 'Review meeting notes' has been deleted."

---

### Interaction 8: Handle Ambiguity

**User**: "Complete it"

**Expected Response**:
- Bot asks for clarification (no context)
- May list available tasks
- Example: "Which task would you like to complete?"

---

### Interaction 9: Update Task

**User**: "Rename the presentation task to finalize demo slides"

**Expected Response**:
- Task title updated
- Shows old and new title
- Example: "I've updated 'prepare demo presentation' to 'finalize demo slides'."

---

## Verification Checklist

### Core Functionality
- [ ] All 5 CRUD operations work (add, list, mark complete, delete, update)
- [ ] Responses stream in real-time (visible typing effect)
- [ ] Delete requires confirmation before execution

### User Isolation
- [ ] Log in as different user
- [ ] Cannot see previous user's tasks
- [ ] Tasks are isolated between users

### Real-time Sync
- [ ] Add task via chat → appears in dashboard
- [ ] Mark complete via chat → dashboard updates
- [ ] Delete via chat → removed from dashboard

### Error Handling
- [ ] Invalid commands show helpful suggestions
- [ ] Backend errors show user-friendly messages
- [ ] Authentication errors redirect to login

### Mobile Responsiveness
- [ ] Open /chat on mobile viewport (320px)
- [ ] Chat interface is fully usable
- [ ] Input keyboard doesn't break layout

## Success Criteria Mapping

| Criteria | Demo Step |
|----------|-----------|
| SC-001: Add task < 5s | Interaction 2 |
| SC-002: 90% command accuracy | Interactions 1-9 |
| SC-003: Clarification for multiple matches | Interaction 8 |
| SC-004: Sync < 2s | After any mutation |
| SC-005: User isolation | Verification checklist |
| SC-006: Mobile 320px | Mobile responsiveness |
| SC-007: Helpful feedback < 1s | Throughout |
| SC-008: 5+ interactions | 9 interactions shown |
| SC-009: Chat history visible | Scroll up during demo |
| SC-010: Graceful error handling | Error handling section |

## Notes

- First response may take longer due to cold start
- OpenAI rate limits may apply for heavy usage
- Stream speed depends on network and OpenAI response time
