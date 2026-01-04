"""ChatKit server endpoints for AI chatbot.

Provides:
- /chatkit - Main streaming chat endpoint
- /api/chatkit/session - Session creation endpoint
- /api/chatkit/history - Conversation history endpoint

Uses OpenAI Agents SDK with MCP Server for task operations.
"""

import json
from typing import AsyncIterator, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent

from .agent import AgentContext, get_system_prompt, get_mcp_server
from .context import (
    create_client_secret,
    get_context_from_request,
    RequestContext,
)
from .conversation import (
    get_or_create_conversation,
    save_message,
    get_conversation_messages,
    get_recent_conversations,
)
from app.dependencies import get_current_user_id
from database import async_session


router = APIRouter(tags=["ChatKit"])


class ChatMessage(BaseModel):
    """Incoming chat message from frontend."""

    message: str
    thread_id: str | None = None
    conversation_id: Optional[int] = None


class SessionResponse(BaseModel):
    """Response for session creation."""

    client_secret: str


async def stream_agent_response(
    message: str,
    context: RequestContext,
    conversation_id: Optional[int] = None
) -> AsyncIterator[str]:
    """Stream agent response as Server-Sent Events.

    Persists both user message and assistant response to database.
    Passes conversation history to the agent for context.

    Args:
        message: User's chat message
        context: Request context with user_id
        conversation_id: Optional conversation ID to continue

    Yields:
        SSE formatted events
    """
    user_id = context.user_id
    conv_id = None
    conversation_history = []

    try:
        # Get or create conversation, fetch history, and save user message
        async with async_session() as session:
            conversation = await get_or_create_conversation(
                session, user_id, conversation_id
            )
            conv_id = conversation.id

            # Fetch previous messages for context (before saving current message)
            previous_messages = await get_conversation_messages(
                session, user_id, conv_id, limit=20
            )

            # Convert to format expected by OpenAI Agents SDK
            for msg in previous_messages:
                conversation_history.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Save user message
            await save_message(session, conv_id, user_id, "user", message)
            await session.commit()

        # Add current message to history
        conversation_history.append({
            "role": "user",
            "content": message
        })

        # Send conversation_id in first event
        yield f"data: {json.dumps({'type': 'conversation', 'conversation_id': conv_id})}\n\n"

        # Create MCP server connection
        mcp_server = get_mcp_server()

        # Connect to MCP server and create agent with user-specific prompt
        async with mcp_server as server:
            # Create agent dynamically with user_id in system prompt
            agent = Agent(
                name="TaskAssistant",
                instructions=get_system_prompt(user_id),
                mcp_servers=[server],
            )

            # Run the agent with streaming, passing full conversation history
            result = Runner.run_streamed(
                agent,
                conversation_history,
            )

            full_response = ""

            # Stream the response using the correct pattern from OpenAI Agents SDK
            async for event in result.stream_events():
                # Check for text delta events
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    # event.data.delta is the text string directly
                    delta_text = event.data.delta
                    if delta_text:
                        full_response += delta_text
                        yield f"data: {json.dumps({'type': 'delta', 'content': delta_text})}\n\n"

            # Save assistant response to database
            if full_response and conv_id:
                async with async_session() as session:
                    await save_message(session, conv_id, user_id, "assistant", full_response)
                    await session.commit()

            # Send completion event
            yield f"data: {json.dumps({'type': 'done', 'content': full_response, 'conversation_id': conv_id})}\n\n"

    except Exception as e:
        error_msg = str(e)
        yield f"data: {json.dumps({'type': 'error', 'error': error_msg})}\n\n"


@router.post("/chatkit")
async def chatkit_endpoint(
    request: Request,
    chat_message: ChatMessage,
):
    """Main ChatKit streaming endpoint.

    Processes chat messages and streams AI responses using SSE.
    Messages are persisted to the database for conversation history.

    Headers:
        Authorization: Bearer <client_secret>

    Body:
        message: User's chat message
        conversation_id: Optional conversation ID to continue
        thread_id: Optional thread identifier (deprecated)

    Returns:
        StreamingResponse with SSE events including conversation_id
    """
    # Validate authorization and get context
    context = get_context_from_request(request)

    # Return streaming response
    return StreamingResponse(
        stream_agent_response(
            chat_message.message,
            context,
            chat_message.conversation_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.post("/api/chatkit/session", response_model=SessionResponse)
async def create_chatkit_session(
    request: Request,
):
    """Create a ChatKit session and return client_secret.

    This endpoint validates the Better Auth JWT from the Authorization header
    and creates a ChatKit-specific client_secret for the chat widget.

    Headers:
        Authorization: Bearer <better_auth_jwt>

    Returns:
        SessionResponse with client_secret
    """
    # Extract Better Auth JWT from header
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )

    token = auth_header.replace("Bearer ", "")

    try:
        # Validate Better Auth JWT and get user_id
        # We need to use the same validation as get_current_user_id
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )
        user_id = await get_current_user_id(credentials)

        # Create ChatKit client_secret
        client_secret = create_client_secret(user_id)

        return SessionResponse(client_secret=client_secret)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication: {str(e)}"
        )


# Non-streaming endpoint for simple testing
@router.post("/api/chatkit/chat")
async def chatkit_simple_endpoint(
    request: Request,
    chat_message: ChatMessage,
):
    """Simple non-streaming chat endpoint for testing.

    Returns the full response at once instead of streaming.
    Messages are persisted to the database for conversation history.
    """
    context = get_context_from_request(request)
    user_id = context.user_id
    conv_id = None
    conversation_history = []

    try:
        # Get or create conversation, fetch history, and save user message
        async with async_session() as session:
            conversation = await get_or_create_conversation(
                session, user_id, chat_message.conversation_id
            )
            conv_id = conversation.id

            # Fetch previous messages for context
            previous_messages = await get_conversation_messages(
                session, user_id, conv_id, limit=20
            )

            # Convert to format expected by OpenAI Agents SDK
            for msg in previous_messages:
                conversation_history.append({
                    "role": msg.role,
                    "content": msg.content
                })

            # Save user message
            await save_message(session, conv_id, user_id, "user", chat_message.message)
            await session.commit()

        # Add current message to history
        conversation_history.append({
            "role": "user",
            "content": chat_message.message
        })

        # Create MCP server connection
        mcp_server = get_mcp_server()

        # Connect to MCP server and create agent with user-specific prompt
        async with mcp_server as server:
            agent = Agent(
                name="TaskAssistant",
                instructions=get_system_prompt(user_id),
                mcp_servers=[server],
            )

            result = await Runner.run(
                agent,
                conversation_history,
            )

            response_text = result.final_output

            # Save assistant response
            if response_text and conv_id:
                async with async_session() as session:
                    await save_message(session, conv_id, user_id, "assistant", response_text)
                    await session.commit()

            return {
                "success": True,
                "response": response_text,
                "conversation_id": conv_id,
            }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


# Conversation history endpoints
class HistoryResponse(BaseModel):
    """Response for conversation history."""

    messages: list[dict]
    conversation_id: Optional[int] = None


class ConversationListResponse(BaseModel):
    """Response for list of conversations."""

    conversations: list[dict]


@router.get("/api/chatkit/history", response_model=HistoryResponse)
async def get_chat_history(
    request: Request,
    conversation_id: Optional[int] = None,
    limit: int = 50,
):
    """Get conversation history.

    Returns messages from the specified conversation or the most recent one.

    Headers:
        Authorization: Bearer <client_secret>

    Query params:
        conversation_id: Optional specific conversation ID
        limit: Maximum messages to return (default 50)

    Returns:
        HistoryResponse with messages array and conversation_id
    """
    context = get_context_from_request(request)
    user_id = context.user_id

    async with async_session() as session:
        messages = await get_conversation_messages(
            session, user_id, conversation_id, limit
        )

        # Get the conversation_id from first message if not specified
        conv_id = conversation_id
        if messages and not conv_id:
            conv_id = messages[0].conversation_id

        return HistoryResponse(
            messages=[
                {
                    "id": str(msg.id),
                    "role": msg.role,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                }
                for msg in messages
            ],
            conversation_id=conv_id,
        )


@router.get("/api/chatkit/conversations", response_model=ConversationListResponse)
async def list_conversations(
    request: Request,
    limit: int = 10,
):
    """List recent conversations for the user.

    Headers:
        Authorization: Bearer <client_secret>

    Query params:
        limit: Maximum conversations to return (default 10)

    Returns:
        ConversationListResponse with conversations array
    """
    context = get_context_from_request(request)
    user_id = context.user_id

    async with async_session() as session:
        conversations = await get_recent_conversations(session, user_id, limit)

        return ConversationListResponse(
            conversations=[
                {
                    "id": conv.id,
                    "title": conv.title or "New conversation",
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat(),
                }
                for conv in conversations
            ]
        )
