"""SQLModel database models for the Todo application.

This module exports all database models:
- Task: Todo task entity (from Phase II)
- Conversation: Chat conversation session (Phase III)
- Message: Chat message in a conversation (Phase III)
"""

# Import existing Task model from task_model.py
from app.task_model import Task, utc_now

# New models for Phase III
from .conversation import Conversation
from .message import Message

__all__ = ["Task", "Conversation", "Message", "utc_now"]
