"""Session 10 conversation persistence and context reconstruction."""

from sqlalchemy.orm import Session

from models.conversation import Conversation, Message
from services.bedrock_service import BedrockError, generate_conversation_reply

DEFAULT_CONVERSATION_TITLE = "New conversation"
AUTO_TITLE_CHARACTERS = 72


class ConversationServiceError(RuntimeError):
    """Raised when a conversation turn cannot be completed safely."""


def list_messages(db: Session, conversation_id: int) -> list[Message]:
    """Return all messages in stable chronological order."""

    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .all()
    )


def _automatic_title(content: str) -> str:
    """Derive a readable title from the first user message without another AI call."""

    single_line = " ".join(content.split())
    if len(single_line) <= AUTO_TITLE_CHARACTERS:
        return single_line
    return single_line[: AUTO_TITLE_CHARACTERS - 3].rstrip() + "..."


def _history_payload(messages: list[Message]) -> list[dict[str, str]]:
    """Convert database messages to the structured Bedrock Converse shape."""

    return [{"role": message.role, "content": message.content} for message in messages]


def send_message(
    db: Session,
    conversation: Conversation,
    content: str,
) -> tuple[Message, Message]:
    """Persist a user turn, rebuild context, call Bedrock, then persist the reply.

    Both messages commit atomically. If Bedrock fails, the transaction rolls back,
    so reloading the thread never reveals an orphaned user turn.
    """

    had_messages = (
        db.query(Message.id)
        .filter(Message.conversation_id == conversation.id)
        .first()
        is not None
    )

    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=content,
    )
    db.add(user_message)

    if not had_messages and conversation.title == DEFAULT_CONVERSATION_TITLE:
        conversation.title = _automatic_title(content)

    try:
        db.flush()
        history = list_messages(db, conversation.id)
        answer = generate_conversation_reply(_history_payload(history)).strip()
        if not answer:
            raise ConversationServiceError("Amazon Bedrock returned an empty response")

        assistant_message = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=answer,
        )
        db.add(assistant_message)
        db.commit()
    except BedrockError as error:
        db.rollback()
        raise ConversationServiceError(str(error)) from error
    except ConversationServiceError:
        db.rollback()
        raise

    db.refresh(user_message)
    db.refresh(assistant_message)
    db.refresh(conversation)
    return user_message, assistant_message
