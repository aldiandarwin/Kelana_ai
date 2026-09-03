"""Session 10 integration tests for private, persistent multi-turn conversations.

Amazon Bedrock is patched in every API happy/failure path. The assertions focus
on the application's responsibility: ownership, ordered persistence, complete
history reconstruction, validation, and atomic rollback.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-only-session-10-secret-key-with-ample-length"
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"

BACKEND_PATH = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from fastapi.testclient import TestClient  # noqa: E402

from database import Base, SessionLocal, engine  # noqa: E402
from main import app  # noqa: E402
from models.conversation import Conversation, Message  # noqa: E402
from services.bedrock_service import BedrockError  # noqa: E402


class ConversationApiTests(unittest.TestCase):
    def setUp(self) -> None:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)

    def register_and_login(self, name: str, email: str) -> dict[str, str]:
        register = self.client.post(
            "/api/v1/auth/register",
            json={"name": name, "email": email, "password": "Password123!"},
        )
        self.assertEqual(register.status_code, 201, register.text)

        login = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "Password123!"},
        )
        self.assertEqual(login.status_code, 200, login.text)
        return {"Authorization": f"Bearer {login.json()['access_token']}"}

    def create_conversation(
        self,
        headers: dict[str, str],
        title: str | None = None,
    ) -> int:
        response = self.client.post(
            "/api/v1/conversations",
            headers=headers,
            json={"title": title} if title else None,
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()["conversation_id"]

    def test_all_conversation_operations_require_authentication(self) -> None:
        self.assertEqual(self.client.get("/api/v1/conversations").status_code, 401)
        self.assertEqual(self.client.post("/api/v1/conversations").status_code, 401)
        self.assertEqual(
            self.client.get("/api/v1/conversations/1/messages").status_code,
            401,
        )
        self.assertEqual(
            self.client.post(
                "/api/v1/conversations/1/messages",
                json={"content": "Hello"},
            ).status_code,
            401,
        )
        self.assertEqual(
            self.client.patch(
                "/api/v1/conversations/1",
                json={"title": "Private trip"},
            ).status_code,
            401,
        )

    def test_create_and_list_are_isolated_to_the_current_user(self) -> None:
        alice_headers = self.register_and_login("Alice", "alice@example.com")
        bob_headers = self.register_and_login("Bob", "bob@example.com")

        alice_id = self.create_conversation(alice_headers, "Japan family trip")
        bob_id = self.create_conversation(bob_headers, "Bangladesh coast")

        alice_list = self.client.get(
            "/api/v1/conversations", headers=alice_headers
        )
        bob_list = self.client.get("/api/v1/conversations", headers=bob_headers)

        self.assertEqual(alice_list.status_code, 200, alice_list.text)
        self.assertEqual([item["id"] for item in alice_list.json()], [alice_id])
        self.assertEqual([item["id"] for item in bob_list.json()], [bob_id])
        self.assertEqual(alice_list.json()[0]["title"], "Japan family trip")
        self.assertIsNotNone(alice_list.json()[0]["created_at"])

    def test_second_turn_reconstructs_the_complete_ordered_history(self) -> None:
        headers = self.register_and_login("Alice", "alice@example.com")
        conversation_id = self.create_conversation(headers)

        with patch(
            "services.conversation_service.generate_conversation_reply",
            side_effect=[
                "Day 1 is Tokyo and Day 2 is Kyoto.",
                "On Day 2, visit Fushimi Inari early, then explore Gion.",
            ],
        ) as generate:
            first = self.client.post(
                f"/api/v1/conversations/{conversation_id}/messages",
                headers=headers,
                json={"content": "Plan two days in Japan."},
            )
            second = self.client.post(
                f"/api/v1/conversations/{conversation_id}/messages",
                headers=headers,
                json={"content": "What should we do on Day 2?"},
            )

        self.assertEqual(first.status_code, 200, first.text)
        self.assertEqual(second.status_code, 200, second.text)
        self.assertEqual(first.json()["title"], "Plan two days in Japan.")
        self.assertEqual(generate.call_count, 2)
        self.assertEqual(
            generate.call_args_list[0].args[0],
            [{"role": "user", "content": "Plan two days in Japan."}],
        )
        self.assertEqual(
            generate.call_args_list[1].args[0],
            [
                {"role": "user", "content": "Plan two days in Japan."},
                {
                    "role": "assistant",
                    "content": "Day 1 is Tokyo and Day 2 is Kyoto.",
                },
                {"role": "user", "content": "What should we do on Day 2?"},
            ],
        )

        reloaded = self.client.get(
            f"/api/v1/conversations/{conversation_id}/messages",
            headers=headers,
        )
        self.assertEqual(reloaded.status_code, 200, reloaded.text)
        messages = reloaded.json()["messages"]
        self.assertEqual(
            [message["role"] for message in messages],
            ["user", "assistant", "user", "assistant"],
        )
        self.assertTrue(all(message["created_at"] for message in messages))
        self.assertEqual(
            messages[-1]["content"],
            "On Day 2, visit Fushimi Inari early, then explore Gion.",
        )

    def test_rename_updates_the_sidebar_title(self) -> None:
        headers = self.register_and_login("Alice", "alice@example.com")
        conversation_id = self.create_conversation(headers)

        renamed = self.client.patch(
            f"/api/v1/conversations/{conversation_id}",
            headers=headers,
            json={"title": "  Japan   family itinerary  "},
        )

        self.assertEqual(renamed.status_code, 200, renamed.text)
        self.assertEqual(renamed.json()["title"], "Japan family itinerary")
        listed = self.client.get("/api/v1/conversations", headers=headers)
        self.assertEqual(listed.json()[0]["title"], "Japan family itinerary")

    def test_cross_user_access_is_forbidden_and_missing_is_not_found(self) -> None:
        alice_headers = self.register_and_login("Alice", "alice@example.com")
        bob_headers = self.register_and_login("Bob", "bob@example.com")
        conversation_id = self.create_conversation(alice_headers)

        self.assertEqual(
            self.client.get(
                f"/api/v1/conversations/{conversation_id}/messages",
                headers=bob_headers,
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.post(
                f"/api/v1/conversations/{conversation_id}/messages",
                headers=bob_headers,
                json={"content": "Read another user's history"},
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.patch(
                f"/api/v1/conversations/{conversation_id}",
                headers=bob_headers,
                json={"title": "Stolen"},
            ).status_code,
            403,
        )
        self.assertEqual(
            self.client.get(
                "/api/v1/conversations/999999/messages", headers=alice_headers
            ).status_code,
            404,
        )

    def test_bedrock_failure_rolls_back_user_message_and_automatic_title(self) -> None:
        headers = self.register_and_login("Alice", "alice@example.com")
        conversation_id = self.create_conversation(headers)

        with patch(
            "services.conversation_service.generate_conversation_reply",
            side_effect=BedrockError("throttled"),
        ):
            response = self.client.post(
                f"/api/v1/conversations/{conversation_id}/messages",
                headers=headers,
                json={"content": "Plan a weekend in Dhaka"},
            )

        self.assertEqual(response.status_code, 502, response.text)
        self.assertIn("Amazon Bedrock", response.json()["detail"])

        db = SessionLocal()
        try:
            conversation = db.get(Conversation, conversation_id)
            self.assertIsNotNone(conversation)
            self.assertEqual(conversation.title, "New conversation")
            self.assertEqual(
                db.query(Message)
                .filter(Message.conversation_id == conversation_id)
                .count(),
                0,
            )
        finally:
            db.close()

    def test_blank_and_oversized_messages_are_rejected_before_bedrock(self) -> None:
        headers = self.register_and_login("Alice", "alice@example.com")
        conversation_id = self.create_conversation(headers)

        with patch(
            "services.conversation_service.generate_conversation_reply"
        ) as generate:
            blank = self.client.post(
                f"/api/v1/conversations/{conversation_id}/messages",
                headers=headers,
                json={"content": "   "},
            )
            oversized = self.client.post(
                f"/api/v1/conversations/{conversation_id}/messages",
                headers=headers,
                json={"content": "x" * 4001},
            )

        self.assertEqual(blank.status_code, 422, blank.text)
        self.assertEqual(oversized.status_code, 422, oversized.text)
        generate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
