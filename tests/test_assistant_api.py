"""Session 9 tests for retrieval and the grounded assistant endpoint.

No test in this file calls Amazon Bedrock. The chunking and ranking functions are
pure, and the endpoint tests patch the two Bedrock entry points. Patching is new
in this repository, and it is here because Session 9 is the first feature whose
happy path cannot be reached without an AWS call.
"""

import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-only-session-9-secret-key-with-ample-length"
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"
# an empty value keeps every test on the local vector store path
os.environ["KNOWLEDGE_BASE_ID"] = ""

BACKEND_PATH = Path(__file__).resolve().parents[1] / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from fastapi.testclient import TestClient  # noqa: E402

from database import Base, SessionLocal, engine  # noqa: E402
from main import app  # noqa: E402
from models.knowledge import KnowledgeChunk  # noqa: E402
from services.bedrock_service import BedrockError  # noqa: E402
from services.knowledge_service import (  # noqa: E402
    build_grounded_prompt,
    chunk_document,
    cosine_similarity,
    ingest_document,
    lexical_similarity,
    search,
)

BAGGAGE_DOCUMENT = """# Sinaptik Travel Baggage Policy

Checked baggage on a regional Asia route is 30 kg per traveller. Cabin baggage is
7 kg. A single piece may never exceed 32 kg on any route.

Excess baggage on a regional Asia route costs IDR 110,000 per kilogram, charged
per leg and payable at the time of booking.
"""

CANCELLATION_DOCUMENT = """# Sinaptik Travel Cancellation Schedule

Cancelling between 29 and 15 days before departure costs 50 per cent of the
package price. Visa fees are never refundable at any point in the schedule.
"""


class ChunkingTests(unittest.TestCase):
    """Pure functions. No database and no AWS."""

    def test_short_document_becomes_one_chunk(self) -> None:
        chunks = chunk_document("# Title\n\nA single short paragraph.")
        self.assertEqual(len(chunks), 1)
        self.assertIn("single short paragraph", chunks[0])

    def test_long_document_is_split_and_keeps_every_paragraph(self) -> None:
        paragraphs = ["Paragraph number " + str(index) + ". " + "word " * 60 for index in range(8)]
        chunks = chunk_document("\n\n".join(paragraphs))

        self.assertGreater(len(chunks), 1)
        joined = " ".join(chunks)
        for index in range(8):
            with self.subTest(paragraph=index):
                self.assertIn("Paragraph number " + str(index), joined)

    def test_consecutive_chunks_overlap(self) -> None:
        paragraphs = ["Paragraph " + str(index) + ". " + "word " * 60 for index in range(6)]
        chunks = chunk_document("\n\n".join(paragraphs))

        self.assertGreater(len(chunks), 1)
        tail = chunks[0][-40:]
        self.assertIn(tail, chunks[1])

    def test_blank_document_produces_no_chunks(self) -> None:
        self.assertEqual(chunk_document("\n\n   \n"), [])


class SimilarityTests(unittest.TestCase):
    """Ranking maths, checked without a model."""

    def test_identical_vectors_score_one(self) -> None:
        self.assertAlmostEqual(cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]), 1.0)

    def test_orthogonal_vectors_score_zero(self) -> None:
        self.assertAlmostEqual(cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0)

    def test_mismatched_or_empty_vectors_score_zero(self) -> None:
        for left, right in ([[], [1.0]], [[1.0, 2.0], [1.0]], [[0.0, 0.0], [1.0, 1.0]]):
            with self.subTest(left=left, right=right):
                self.assertEqual(cosine_similarity(left, right), 0.0)

    def test_lexical_score_prefers_the_passage_that_shares_words(self) -> None:
        question = "What is the excess baggage rate per kilogram?"
        relevant = "Excess baggage costs IDR 110,000 per kilogram on regional routes."
        unrelated = "Cherry blossom season falls in late March and doubles hotel prices."

        self.assertGreater(
            lexical_similarity(question, relevant),
            lexical_similarity(question, unrelated),
        )

    def test_lexical_score_of_an_empty_question_is_zero(self) -> None:
        self.assertEqual(lexical_similarity("the and of", "any passage at all"), 0.0)


class GroundedPromptTests(unittest.TestCase):
    def test_prompt_names_every_source_and_forbids_guessing(self) -> None:
        passages = [
            {"document": "sinaptik-travel-policy.md", "content": "30 kg on regional Asia."},
            {"document": "singapore-visa-guide.md", "content": "Submit the SG Arrival Card."},
        ]
        prompt = build_grounded_prompt("How much baggage?", passages)

        self.assertIn("sinaptik-travel-policy.md", prompt)
        self.assertIn("singapore-visa-guide.md", prompt)
        self.assertIn("Never guess", prompt)
        self.assertIn("every requested sub-question", prompt)
        self.assertIn("How much baggage?", prompt)


class RetrievalTests(unittest.TestCase):
    """Ingestion and search against the in-memory database, with embeddings stubbed."""

    def setUp(self) -> None:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()

    def tearDown(self) -> None:
        self.db.close()

    def test_ingestion_without_embeddings_still_ranks_by_words(self) -> None:
        ingest_document(
            self.db, "sinaptik-travel-policy.md", "Baggage", BAGGAGE_DOCUMENT, False
        )
        ingest_document(
            self.db, "cancellation.md", "Cancellation", CANCELLATION_DOCUMENT, False
        )

        hits = search(self.db, "How much does excess baggage cost per kilogram?")

        self.assertTrue(hits)
        self.assertEqual(hits[0]["document"], "sinaptik-travel-policy.md")
        self.assertIn("110,000", hits[0]["content"])

    def test_reingesting_a_document_replaces_it_instead_of_duplicating(self) -> None:
        first = ingest_document(
            self.db, "sinaptik-travel-policy.md", "Baggage", BAGGAGE_DOCUMENT, False
        )
        second = ingest_document(
            self.db, "sinaptik-travel-policy.md", "Baggage", BAGGAGE_DOCUMENT, False
        )

        self.assertEqual(first, second)
        stored = search(self.db, "baggage", top_k=50)
        self.assertEqual(len(stored), first)

    def test_search_on_an_empty_knowledge_base_returns_nothing(self) -> None:
        self.assertEqual(search(self.db, "anything at all"), [])

    def test_embeddings_are_stored_when_the_model_is_available(self) -> None:
        with patch(
            "services.knowledge_service.embed_text", return_value=[0.1, 0.2, 0.3]
        ) as embed:
            ingest_document(
                self.db, "sinaptik-travel-policy.md", "Baggage", BAGGAGE_DOCUMENT, True
            )

        self.assertTrue(embed.called)
        hits = search(self.db, "baggage", top_k=50)
        self.assertTrue(hits)

    def test_hybrid_ranking_preserves_exact_names_when_semantic_scores_are_close(self) -> None:
        self.db.add_all(
            [
                KnowledgeChunk(
                    document_name="wrong.pdf",
                    document_title="Generic travel",
                    chunk_index=0,
                    content="A general description of hotels and airport transfers.",
                    embedding=json.dumps([1.0, 0.0]),
                ),
                KnowledgeChunk(
                    document_name="bangladesh-tourist-handbook.pdf",
                    document_title="Bangladesh Tourist Hand Book",
                    chunk_index=0,
                    content=(
                        "Khagrachari is 112 km from Chattogram. Chengi, Kasalong, "
                        "and Maini pass through it. Alutila is the main attraction."
                    ),
                    embedding=json.dumps([0.8, 0.6]),
                ),
            ]
        )
        self.db.commit()

        with patch(
            "services.knowledge_service.embed_text", return_value=[1.0, 0.0]
        ):
            hits = search(
                self.db,
                "Which rivers pass through Khagrachari and what is its main attraction?",
            )

        self.assertEqual(hits[0]["document"], "bangladesh-tourist-handbook.pdf")


class AssistantApiTests(unittest.TestCase):
    def setUp(self) -> None:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.client = TestClient(app)

        db = SessionLocal()
        try:
            ingest_document(
                db, "sinaptik-travel-policy.md", "Baggage", BAGGAGE_DOCUMENT, False
            )
        finally:
            db.close()

    def register(self, name: str, email: str) -> dict[str, object]:
        response = self.client.post(
            "/api/v1/auth/register",
            json={"name": name, "email": email, "password": "Password123!"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def login_headers(self, email: str) -> dict[str, str]:
        response = self.client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "Password123!"},
        )
        self.assertEqual(response.status_code, 200, response.text)
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    def test_assistant_requires_authentication(self) -> None:
        response = self.client.post(
            "/api/v1/assistant", json={"question": "How much baggage?"}
        )
        self.assertEqual(response.status_code, 401, response.text)

    def test_question_shorter_than_the_minimum_is_rejected(self) -> None:
        self.register("Alice", "alice@example.com")
        headers = self.login_headers("alice@example.com")

        response = self.client.post(
            "/api/v1/assistant", json={"question": "hi"}, headers=headers
        )
        self.assertEqual(response.status_code, 422, response.text)

    def test_grounded_answer_names_the_source_document(self) -> None:
        self.register("Alice", "alice@example.com")
        headers = self.login_headers("alice@example.com")

        with patch(
            "services.knowledge_service.generate_answer",
            return_value="Regional Asia allows 30 kg. [Source: sinaptik-travel-policy.md]",
        ):
            response = self.client.post(
                "/api/v1/assistant",
                json={"question": "How much does excess baggage cost per kilogram?"},
                headers=headers,
            )

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertTrue(body["grounded"])
        self.assertEqual(body["mode"], "local-vector-store")
        self.assertTrue(body["sources"])
        self.assertEqual(body["sources"][0]["document"], "sinaptik-travel-policy.md")

    def test_question_outside_the_knowledge_base_is_refused_not_invented(self) -> None:
        self.register("Alice", "alice@example.com")
        headers = self.login_headers("alice@example.com")

        with patch("services.knowledge_service.generate_answer") as generate:
            response = self.client.post(
                "/api/v1/assistant",
                json={"question": "Who won the 1998 world snooker championship?"},
                headers=headers,
            )

        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertFalse(body["grounded"])
        self.assertEqual(body["sources"], [])
        # the model is never asked, so it never gets the chance to invent an answer
        generate.assert_not_called()

    def test_a_bedrock_failure_becomes_502_not_500(self) -> None:
        self.register("Alice", "alice@example.com")
        headers = self.login_headers("alice@example.com")

        with patch(
            "services.knowledge_service.generate_answer",
            side_effect=BedrockError("throttled"),
        ):
            response = self.client.post(
                "/api/v1/assistant",
                json={"question": "How much does excess baggage cost per kilogram?"},
                headers=headers,
            )

        self.assertEqual(response.status_code, 502, response.text)
        self.assertIn("knowledge base", response.json()["detail"])


class EvaluationQuestionsTests(unittest.TestCase):
    """The homework contract itself, checked so a broken questions file cannot ship."""

    def setUp(self) -> None:
        path = Path(__file__).resolve().parents[1] / "knowledge" / "evaluation-questions.json"
        self.payload = json.loads(path.read_text(encoding="utf-8"))
        self.knowledge_dir = path.parent

    def test_there_are_five_questions(self) -> None:
        self.assertEqual(len(self.payload["questions"]), 5)

    def test_every_question_requires_a_document_added_in_the_expansion(self) -> None:
        expansion = {
            "bangladesh-tourist-handbook.pdf",
            "bangladesh-sundarbans.pdf",
            "bangladesh-world-heritage-tour.pdf",
        }
        for question in self.payload["questions"]:
            with self.subTest(question=question["id"]):
                self.assertIn(question["requires_document"], expansion)

    def test_every_required_document_exists_on_disk(self) -> None:
        for question in self.payload["questions"]:
            with self.subTest(question=question["id"]):
                self.assertTrue(
                    (self.knowledge_dir / question["requires_document"]).is_file()
                )

    def test_every_expected_fact_carries_accepted_strings(self) -> None:
        for question in self.payload["questions"]:
            for fact in question["expected_facts"]:
                with self.subTest(question=question["id"], fact=fact["fact"]):
                    self.assertTrue(fact["match"])

    def test_cases_follow_the_eval_dataset_contract(self) -> None:
        required_fields = {
            "case_id",
            "input",
            "expected_behavior",
            "failure_category",
            "severity",
            "split",
            "source",
        }
        allowed_splits = {"targeted", "regression", "holdout"}

        for question in self.payload["questions"]:
            with self.subTest(question=question["id"]):
                self.assertTrue(required_fields.issubset(question))
                self.assertIn(question["split"], allowed_splits)
                self.assertEqual(question["input"]["question"], question["question"])
                self.assertEqual(
                    question["source"]["document"], question["requires_document"]
                )

    def test_dataset_reserves_a_holdout_case(self) -> None:
        splits = {question["split"] for question in self.payload["questions"]}
        self.assertEqual(splits, {"targeted", "regression", "holdout"})


if __name__ == "__main__":
    unittest.main()
