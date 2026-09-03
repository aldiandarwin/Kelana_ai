r"""Idempotent PostgreSQL migration for Session 10 conversation memory.

Run from backend/ against an existing KelanaAI database:

    ..\.venv\Scripts\python.exe migrate_session_10.py
"""

from sqlalchemy import inspect

from database import Base, engine
from models.conversation import Conversation, Message  # noqa: F401
from models.user import User  # noqa: F401


def migrate() -> None:
    """Create the two new tables without modifying earlier session data."""

    if engine.dialect.name != "postgresql":
        raise RuntimeError("Session 10 migration is intended for PostgreSQL only.")

    Base.metadata.tables["conversations"].create(bind=engine, checkfirst=True)
    Base.metadata.tables["messages"].create(bind=engine, checkfirst=True)

    inspector = inspect(engine)
    conversation_columns = {
        column["name"] for column in inspector.get_columns("conversations")
    }
    message_columns = {column["name"] for column in inspector.get_columns("messages")}
    expected_conversation_columns = {"id", "user_id", "title", "created_at"}
    expected_message_columns = {
        "id",
        "conversation_id",
        "role",
        "content",
        "created_at",
    }
    if not expected_conversation_columns.issubset(conversation_columns):
        raise RuntimeError("The conversations table is missing required columns")
    if not expected_message_columns.issubset(message_columns):
        raise RuntimeError("The messages table is missing required columns")

    print("Session 10 migration complete. conversations and messages are ready.")
    print("conversation_columns=" + ",".join(sorted(conversation_columns)))
    print("message_columns=" + ",".join(sorted(message_columns)))


if __name__ == "__main__":
    migrate()
