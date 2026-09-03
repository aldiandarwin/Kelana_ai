"""Validated request and response shapes for Session 10 conversations."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalise_single_line(value: str) -> str:
    return " ".join(value.split())


class ConversationCreateRequest(BaseModel):
    """Optional initial title for a new conversation."""

    title: str = Field(default="New conversation", min_length=1, max_length=256)

    @field_validator("title")
    @classmethod
    def normalise_title(cls, value: str) -> str:
        normalized = _normalise_single_line(value)
        if not normalized:
            raise ValueError("Conversation title cannot be blank")
        return normalized


class ConversationRenameRequest(BaseModel):
    """A meaningful replacement title for the challenge bonus."""

    title: str = Field(min_length=1, max_length=256)

    @field_validator("title")
    @classmethod
    def normalise_title(cls, value: str) -> str:
        normalized = _normalise_single_line(value)
        if not normalized:
            raise ValueError("Conversation title cannot be blank")
        return normalized


class MessageCreateRequest(BaseModel):
    """One user turn submitted to an existing conversation."""

    content: str = Field(min_length=1, max_length=4000)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Message cannot be blank")
        return normalized


class ConversationCreateResponse(BaseModel):
    """The identifier returned by the create endpoint in the lesson."""

    conversation_id: int


class ConversationSummary(BaseModel):
    """One row in the current user's conversation sidebar."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime


class MessageResponse(BaseModel):
    """One persisted chat bubble."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    created_at: datetime


class ConversationDetail(ConversationSummary):
    """A conversation plus every message in chronological order."""

    messages: list[MessageResponse]


class ConversationTurnResponse(BaseModel):
    """The two persisted messages produced by one send operation."""

    conversation_id: int
    title: str
    user_message: MessageResponse
    assistant_message: MessageResponse
