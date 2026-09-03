"""Run an isolated two-turn Session 10 smoke test against real Amazon Bedrock.

The script uses an in-memory SQLite database, so it never adds demo users or
messages to the configured KelanaAI database. Only the two non-sensitive sample
turns and the first model answer are sent to Bedrock.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from models.conversation import Conversation, Message
from models.trip import Trip  # noqa: F401 - resolves the User.trips relationship
from models.user import User
from services.conversation_service import list_messages, send_message


def smoke() -> None:
    """Prove database persistence and a context-dependent second Bedrock turn."""

    smoke_engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    smoke_session = sessionmaker(bind=smoke_engine, autoflush=False)
    Base.metadata.create_all(bind=smoke_engine)

    db = smoke_session()
    try:
        user = User(
            name="Session 10 Smoke",
            email="session10-smoke@local.invalid",
            password_hash="not-a-real-login",
        )
        db.add(user)
        db.flush()
        conversation = Conversation(user_id=user.id, title="New conversation")
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        send_message(
            db,
            conversation,
            "Remember this two-day plan: Day 1 is Tokyo and Day 2 is Kyoto. "
            "Confirm briefly.",
        )
        send_message(
            db,
            conversation,
            "Which city did I assign to Day 2? Reply with only the city name.",
        )

        stored = list_messages(db, conversation.id)
        roles = " -> ".join(message.role for message in stored)
        final_answer = stored[-1].content.strip()

        if len(stored) != 4 or roles != "user -> assistant -> user -> assistant":
            raise RuntimeError("The two turns were not persisted in the expected order")
        if "kyoto" not in final_answer.lower():
            raise RuntimeError(
                "The context-dependent answer did not identify Kyoto: " + final_answer
            )

        print("Session 10 live smoke: PASS")
        print("Stored role order: " + roles)
        print("Context-dependent answer: " + final_answer)
    finally:
        db.close()
        smoke_engine.dispose()


if __name__ == "__main__":
    smoke()
