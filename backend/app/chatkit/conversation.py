"""Conversation service for chat history persistence.

Provides functions to create conversations, save messages, and retrieve
conversation history for users.
"""

from datetime import datetime
from typing import Optional

from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Conversation, Message


def utc_now() -> datetime:
    """Return current UTC datetime (naive for PostgreSQL TIMESTAMP)."""
    return datetime.utcnow()


async def create_conversation(
    session: AsyncSession,
    user_id: str,
    title: Optional[str] = None
) -> Conversation:
    """Create a new conversation for a user.

    Args:
        session: Database session
        user_id: The user's ID
        title: Optional title for the conversation

    Returns:
        The created Conversation object
    """
    conversation = Conversation(
        user_id=user_id,
        title=title,
    )
    session.add(conversation)
    await session.flush()
    await session.refresh(conversation)
    return conversation


async def get_or_create_conversation(
    session: AsyncSession,
    user_id: str,
    conversation_id: Optional[int] = None
) -> Conversation:
    """Get an existing conversation or create a new one.

    If conversation_id is provided, fetches that conversation (validating user ownership).
    Otherwise, gets the most recent conversation for the user or creates a new one.

    Args:
        session: Database session
        user_id: The user's ID
        conversation_id: Optional specific conversation ID

    Returns:
        The Conversation object
    """
    if conversation_id:
        # Fetch specific conversation with user validation
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        result = await session.execute(statement)
        conversation = result.scalar_one_or_none()
        if conversation:
            return conversation

    # Get most recent conversation for user
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())  # type: ignore
        .limit(1)
    )
    result = await session.execute(statement)
    conversation = result.scalar_one_or_none()

    if conversation:
        return conversation

    # Create new conversation
    return await create_conversation(session, user_id)


async def save_message(
    session: AsyncSession,
    conversation_id: int,
    user_id: str,
    role: str,
    content: str
) -> Message:
    """Save a message to a conversation.

    Also updates the conversation's updated_at timestamp.

    Args:
        session: Database session
        conversation_id: The conversation ID
        user_id: The user's ID (for query efficiency)
        role: Message role ('user' or 'assistant')
        content: Message text content

    Returns:
        The created Message object
    """
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content,
    )
    session.add(message)

    # Update conversation's updated_at
    statement = select(Conversation).where(Conversation.id == conversation_id)
    result = await session.execute(statement)
    conversation = result.scalar_one_or_none()
    if conversation:
        conversation.updated_at = utc_now()

        # Auto-generate title from first user message if not set
        if not conversation.title and role == "user":
            # Use first 50 chars of the message as title
            conversation.title = content[:50] + ("..." if len(content) > 50 else "")

    await session.flush()
    await session.refresh(message)
    return message


async def get_conversation_messages(
    session: AsyncSession,
    user_id: str,
    conversation_id: Optional[int] = None,
    limit: int = 50
) -> list[Message]:
    """Get messages from a conversation.

    Args:
        session: Database session
        user_id: The user's ID (for security validation)
        conversation_id: Optional specific conversation ID
        limit: Maximum number of messages to return (default 50)

    Returns:
        List of Message objects, ordered by creation time (oldest first)
    """
    # Build query
    if conversation_id:
        statement = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id
            )
            .order_by(Message.created_at.asc())  # type: ignore
            .limit(limit)
        )
    else:
        # Get messages from the most recent conversation
        subquery = (
            select(Conversation.id)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())  # type: ignore
            .limit(1)
        )
        statement = (
            select(Message)
            .where(
                Message.user_id == user_id,
                Message.conversation_id.in_(subquery)  # type: ignore
            )
            .order_by(Message.created_at.asc())  # type: ignore
            .limit(limit)
        )

    result = await session.execute(statement)
    return list(result.scalars().all())


async def get_recent_conversations(
    session: AsyncSession,
    user_id: str,
    limit: int = 10
) -> list[Conversation]:
    """Get recent conversations for a user.

    Args:
        session: Database session
        user_id: The user's ID
        limit: Maximum number of conversations to return

    Returns:
        List of Conversation objects, ordered by most recent first
    """
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())  # type: ignore
        .limit(limit)
    )
    result = await session.execute(statement)
    return list(result.scalars().all())
