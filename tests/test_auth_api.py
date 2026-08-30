"""Session 8 integration tests for JWT authentication and trip ownership."""

import os
import sys
import unittest
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-only-session-8-secret-key-with-ample-length"
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"

BACKEND_PATH = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from fastapi.testclient import TestClient  # noqa: E402

from database import Base, engine  # noqa: E402
from main import app  # noqa: E402


class AuthApiTests(unittest.TestCase):
    def setUp(self) -> None:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)

    def register(self, name: str, email: str) -> dict[str, object]:
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "name": name,
                "email": email,
                "password": "Password123!",
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def login_headers(self, email: str) -> dict[str, str]:
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "Password123!"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def create_trip(
        self,
        headers: dict[str, str],
        destination: str,
        attempted_user_id: int | None = None,
    ):
        payload: dict[str, object] = {
            "destination": destination,
            "days": 4,
            "budget": 1600,
            "travel_style": "Solo",
        }
        if attempted_user_id is not None:
            payload["user_id"] = attempted_user_id
        return self.client.post("/api/v1/trips", json=payload, headers=headers)

    def test_trip_endpoints_require_authentication(self) -> None:
        self.assertEqual(self.client.get("/api/v1/trips").status_code, 401)
        self.assertEqual(
            self.client.post(
                "/api/v1/trips",
                json={"destination": "Bali", "days": 3, "budget": 900},
            ).status_code,
            401,
        )

    def test_register_login_and_profile_hide_password_data(self) -> None:
        user = self.register("Alice", "ALICE@example.com")
        self.assertEqual(user["email"], "alice@example.com")
        self.assertNotIn("password", user)
        self.assertNotIn("password_hash", user)

        headers = self.login_headers("alice@example.com")
        profile = self.client.get("/api/v1/auth/me", headers=headers)
        self.assertEqual(profile.status_code, 200, profile.text)
        self.assertEqual(profile.json()["name"], "Alice")
        self.assertEqual(profile.json()["total_trips"], 0)

    def test_duplicate_email_and_wrong_password_are_rejected(self) -> None:
        self.register("Alice", "alice@example.com")
        duplicate = self.client.post(
            "/api/v1/auth/register",
            json={
                "name": "Another Alice",
                "email": "alice@example.com",
                "password": "Password123!",
            },
        )
        self.assertEqual(duplicate.status_code, 409)

        wrong_login = self.client.post(
            "/api/v1/auth/login",
            json={"email": "alice@example.com", "password": "wrong-password"},
        )
        self.assertEqual(wrong_login.status_code, 401)

    def test_ownership_filters_lists_and_rejects_cross_user_access(self) -> None:
        alice = self.register("Alice", "alice@example.com")
        bob = self.register("Bob", "bob@example.com")
        alice_headers = self.login_headers("alice@example.com")
        bob_headers = self.login_headers("bob@example.com")

        alice_trip = self.create_trip(
            alice_headers,
            "Japan",
            attempted_user_id=int(bob["id"]),
        )
        self.assertEqual(alice_trip.status_code, 200, alice_trip.text)
        alice_trip_data = alice_trip.json()
        self.assertEqual(alice_trip_data["user_id"], alice["id"])

        bob_trip = self.create_trip(bob_headers, "Korea")
        self.assertEqual(bob_trip.status_code, 200, bob_trip.text)

        alice_list = self.client.get("/api/v1/trips", headers=alice_headers)
        bob_list = self.client.get("/api/v1/trips", headers=bob_headers)
        self.assertEqual(
            [trip["destination"] for trip in alice_list.json()],
            ["Japan"],
        )
        self.assertEqual(
            [trip["destination"] for trip in bob_list.json()],
            ["Korea"],
        )

        trip_id = alice_trip_data["id"]
        cross_user_requests = [
            self.client.get(f"/api/v1/trips/{trip_id}", headers=bob_headers),
            self.client.put(
                f"/api/v1/trips/{trip_id}",
                json={"budget": 2400},
                headers=bob_headers,
            ),
            self.client.delete(
                f"/api/v1/trips/{trip_id}",
                headers=bob_headers,
            ),
            self.client.post(
                f"/api/v1/trips/{trip_id}/generate",
                headers=bob_headers,
            ),
        ]
        self.assertTrue(
            all(response.status_code == 403 for response in cross_user_requests)
        )

        own_update = self.client.put(
            f"/api/v1/trips/{trip_id}",
            json={"budget": 2400},
            headers=alice_headers,
        )
        self.assertEqual(own_update.status_code, 200, own_update.text)
        self.assertEqual(own_update.json()["budget"], 2400)

        own_delete = self.client.delete(
            f"/api/v1/trips/{trip_id}",
            headers=alice_headers,
        )
        self.assertEqual(own_delete.status_code, 200, own_delete.text)


if __name__ == "__main__":
    unittest.main()
