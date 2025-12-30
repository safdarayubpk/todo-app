# ChatKit API Contract

**Feature**: 003-ai-todo-chatbot
**Date**: 2025-12-29

## Overview

This document defines the API contracts for the OpenAI ChatKit integration. The architecture involves:
1. **Session endpoint** (Next.js): Creates client_secret for ChatKit authentication
2. **ChatKit endpoint** (FastAPI): Handles chat messages via ChatKit Python SDK

## Endpoints

### POST /api/chatkit/session (Next.js)

Creates a new ChatKit session and returns a client_secret for widget authentication.

#### Request

**Headers**:
```
Content-Type: application/json
Cookie: [Better Auth session cookie]
```

**Body**: None required (session info from cookie)

#### Response

**Status**: 200 OK

**Body**:
```json
{
  "client_secret": "ck_secret_abc123..."
}
```

**Schema**:
```typescript
interface SessionResponse {
  /** Client secret token for ChatKit widget authentication */
  client_secret: string;
}
```

#### Error Responses

**401 Unauthorized**:
```json
{
  "error": "Authentication required",
  "code": "UNAUTHORIZED"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Failed to create session",
  "code": "SESSION_ERROR"
}
```

---

### POST /api/chatkit/refresh (Next.js)

Refreshes an existing ChatKit session token.

#### Request

**Headers**:
```
Content-Type: application/json
Cookie: [Better Auth session cookie]
```

**Body**:
```json
{
  "token": "ck_secret_abc123..."
}
```

#### Response

**Status**: 200 OK

**Body**:
```json
{
  "client_secret": "ck_secret_new456..."
}
```

#### Error Responses

**401 Unauthorized** (session expired):
```json
{
  "error": "Session expired",
  "code": "SESSION_EXPIRED"
}
```

---

### POST /chatkit (FastAPI)

Main ChatKit endpoint that processes chat messages and streams responses. This endpoint is consumed directly by the ChatKit widget, not called manually.

#### Request

The ChatKit widget automatically sends requests in ChatKit protocol format.

**Headers**:
```
Content-Type: application/json
Authorization: Bearer <client_secret>
```

**Body** (ChatKit protocol - handled by widget):
```json
{
  "thread_id": "thread_abc123",
  "message": {
    "role": "user",
    "content": "Add a task to buy groceries"
  }
}
```

#### Response

**Status**: 200 OK

**Headers**:
```
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

**SSE Event Stream** (ChatKit protocol):
```text
event: thread.message.delta
data: {"content": "I've "}

event: thread.message.delta
data: {"content": "added "}

event: thread.message.delta
data: {"content": "'buy groceries' to your tasks."}

event: thread.message.completed
data: {"message_id": "msg_123"}

event: thread.run.completed
data: {"thread_id": "thread_abc123"}
```

#### Error Responses

**401 Unauthorized**:
```json
{
  "error": "Invalid client secret"
}
```

**500 Internal Server Error**:
```json
{
  "error": "Chat service unavailable"
}
```

---

## Client Usage Example

### React with useChatKit Hook

```typescript
'use client';

import { ChatKit, useChatKit } from '@openai/chatkit-react';
import { useRouter } from 'next/navigation';

export function TodoChatWidget() {
  const router = useRouter();

  const { control } = useChatKit({
    api: {
      // Called when widget needs authentication
      async getClientSecret(existingToken) {
        // Try to refresh existing token
        if (existingToken) {
          const res = await fetch('/api/chatkit/refresh', {
            method: 'POST',
            body: JSON.stringify({ token: existingToken }),
            headers: { 'Content-Type': 'application/json' },
          });
          if (res.ok) {
            return (await res.json()).client_secret;
          }
          // Token refresh failed, create new session
        }

        // Create new session
        const res = await fetch('/api/chatkit/session', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        });

        if (!res.ok) {
          // Not authenticated, redirect to login
          router.push('/login');
          throw new Error('Authentication required');
        }

        return (await res.json()).client_secret;
      },
    },

    // UI Configuration
    theme: 'light',
    locale: 'en',

    // Start screen with suggestions
    startScreen: {
      greeting: 'Hi! I can help you manage your tasks.',
      prompts: [
        { label: 'Show tasks', prompt: 'Show my tasks', icon: 'list' },
        { label: 'Add task', prompt: 'Add a task to ', icon: 'plus' },
      ],
    },

    // Handle client-side tool calls
    onClientTool: async ({ name, params }) => {
      if (name === 'refresh_task_list') {
        window.dispatchEvent(new CustomEvent('refresh-tasks'));
        return { refreshed: true };
      }
    },

    // Event handlers
    onReady: () => console.log('ChatKit ready'),
    onError: ({ error }) => console.error('ChatKit error:', error),
    onResponseStart: () => console.log('Response started'),
    onResponseEnd: () => console.log('Response ended'),
  });

  return <ChatKit control={control} className="h-[600px] w-full" />;
}
```

### Server-Side Implementation (FastAPI)

```python
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from chatkit.server import ChatKitServer, StreamingResult
from chatkit.types import ThreadMetadata, UserMessageItem
from typing import AsyncIterator

from .agent import task_agent
from .context import RequestContext, validate_client_secret

app = FastAPI()

class TodoChatKitServer(ChatKitServer[RequestContext]):
    async def respond(
        self,
        thread: ThreadMetadata,
        input_user_message: UserMessageItem | None,
        context: RequestContext,
    ) -> AsyncIterator:
        from agents import Runner
        from chatkit.agents import AgentContext

        agent_context = AgentContext(request_context=context)
        result = Runner.run_streamed(
            task_agent,
            input_user_message.content if input_user_message else "",
            context=agent_context
        )
        async for event in result:
            yield event

# Initialize server
server = TodoChatKitServer(store=None)  # No persistent store needed

@app.post("/chatkit")
async def chatkit_endpoint(request: Request) -> Response:
    # Extract and validate client secret
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(401, "Invalid authorization")

    client_secret = auth_header.replace("Bearer ", "")
    user_id = validate_client_secret(client_secret)
    if not user_id:
        raise HTTPException(401, "Invalid client secret")

    # Create request context with user info
    context = RequestContext(user_id=user_id)

    # Process with ChatKit server
    result = await server.process(await request.body(), context)

    if isinstance(result, StreamingResult):
        return StreamingResponse(result, media_type="text/event-stream")

    return Response(content=result.json, media_type="application/json")
```

---

## Session Management

### Client Secret Format

The client_secret is a signed JWT containing:

```json
{
  "sub": "user_abc123",
  "iat": 1703836800,
  "exp": 1703840400,
  "iss": "todoapp"
}
```

### Session Lifecycle

| Event | Action |
|-------|--------|
| User opens /chat | Widget calls getClientSecret() |
| No existing token | Frontend calls POST /api/chatkit/session |
| Existing token | Frontend calls POST /api/chatkit/refresh |
| Token valid | Widget connects to /chatkit |
| Token expired | Frontend creates new session |
| User logs out | Clear stored token |

---

## Rate Limiting

| Tier | Messages/min | Tokens/day |
|------|--------------|------------|
| Free | 10 | 10,000 |
| Standard | 60 | 100,000 |

Rate limits are per user, enforced at the /chatkit endpoint.

---

## Security Considerations

1. **Authentication**: All requests validated via Better Auth session or client_secret
2. **User Isolation**: user_id embedded in client_secret, validated on every request
3. **Token Expiry**: Client secrets expire after 1 hour
4. **HTTPS Only**: All endpoints require HTTPS in production
5. **CORS**: Configured for frontend domain only
