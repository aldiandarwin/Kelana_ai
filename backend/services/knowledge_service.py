"""Session 9: Retrieval-Augmented Generation over the KelanaAI knowledge base.

RAG is two flows that run at different times. Ingestion reads a document, splits
it, embeds each piece, and stores it. Query embeds the question, ranks the stored
pieces, and hands the best ones to the model as context.

This module owns both flows and imports no boto3. Every AWS call goes through
bedrock_service, which stays the only module that knows the SDK exists.
"""

import json
import math
import os
import re

from sqlalchemy.orm import Session

from models.knowledge import KnowledgeChunk
from services.bedrock_service import (
    BedrockError,
    embed_text,
    generate_answer,
    retrieve_and_generate,
)

# a chunk large enough to answer a question on its own, small enough that the
# embedding still points at one topic instead of averaging three
CHUNK_TARGET_CHARACTERS = 900
CHUNK_OVERLAP_CHARACTERS = 150

# how many passages are put in front of the model
TOP_K = 4

# Semantic search handles paraphrases; lexical overlap protects exact names,
# numbers, and source-specific wording that travel guide questions depend on.
SEMANTIC_WEIGHT = 0.60
LEXICAL_WEIGHT = 0.40

# below this the best match is treated as no match, so the answer says so
# instead of grounding itself in something unrelated
MINIMUM_SCORE = 0.20

STOP_WORDS = frozenset(
    """a an and are as at be by do does for from how i in is it its of on or that
    the to what when where which who why will with you your""".split()
)


class KnowledgeBaseError(RuntimeError):
    """Raised when retrieval cannot produce an answer, so the web layer can reply 502."""


def chunk_document(text: str) -> list[str]:
    """Split one document into overlapping passages, preferring paragraph breaks.

    Splitting on blank lines keeps a heading with the text under it. The overlap
    stops a fact that straddles a boundary from being lost by both neighbours.
    """

    paragraphs = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]

    chunks: list[str] = []
    current = ""

    for paragraph in paragraphs:
        if current and len(current) + len(paragraph) + 2 > CHUNK_TARGET_CHARACTERS:
            chunks.append(current)
            # carry the tail of the finished chunk into the next one
            current = current[-CHUNK_OVERLAP_CHARACTERS:] + "\n\n" + paragraph
        else:
            current = current + "\n\n" + paragraph if current else paragraph

    if current:
        chunks.append(current)

    return chunks


def _tokenize(text: str) -> list[str]:
    """Lowercase words with the most common English stop words removed."""

    words = re.findall(r"[a-z0-9]+", text.lower())
    return [word for word in words if word not in STOP_WORDS and len(word) > 1]


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Return the cosine of the angle between two vectors, or 0.0 when either is empty."""

    if not left or not right or len(left) != len(right):
        return 0.0

    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))

    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0

    return dot / (left_norm * right_norm)


def lexical_similarity(question: str, passage: str) -> float:
    """Score a passage by word overlap, used when no embedding is available.

    This is the fallback that keeps retrieval working if the Bedrock key is not
    allowed to call the embedding model. It finds the same words, not the same
    meaning, so it is weaker. It is never silently better.
    """

    question_words = set(_tokenize(question))
    if not question_words:
        return 0.0

    passage_words = _tokenize(passage)
    if not passage_words:
        return 0.0

    passage_set = set(passage_words)
    overlap = question_words & passage_set

    # reward covering the question, then lightly reward a shorter passage saying it
    coverage = len(overlap) / len(question_words)
    density = len(overlap) / math.sqrt(len(passage_set))

    return coverage * 0.8 + min(density, 1.0) * 0.2


def ingest_document(
    db: Session,
    document_name: str,
    document_title: str,
    text: str,
    with_embeddings: bool = True,
) -> int:
    """Replace every stored chunk of one document and return how many were written.

    Deleting first is what makes this idempotent. Editing a file and re-running
    the script never leaves a stale copy behind.
    """

    db.query(KnowledgeChunk).filter(
        KnowledgeChunk.document_name == document_name
    ).delete(synchronize_session=False)

    chunks = chunk_document(text)

    for position, content in enumerate(chunks):
        embedding = None
        if with_embeddings:
            embedding = json.dumps(embed_text(content))

        db.add(
            KnowledgeChunk(
                document_name=document_name,
                document_title=document_title,
                chunk_index=position,
                content=content,
                embedding=embedding,
            )
        )

    db.commit()
    return len(chunks)


def search(db: Session, question: str, top_k: int = TOP_K) -> list[dict]:
    """Return the highest scoring passages for one question, best first."""

    chunks = db.query(KnowledgeChunk).all()
    if not chunks:
        return []

    # one embedded chunk is enough to prove the semantic path is live
    semantic = any(chunk.embedding for chunk in chunks)

    question_vector: list[float] = []
    if semantic:
        try:
            question_vector = embed_text(question)
        except BedrockError:
            # the question could not be embedded, so rank the same way for every
            # chunk rather than mixing two incomparable scales
            semantic = False

    scored: list[dict] = []
    for chunk in chunks:
        searchable_text = (
            f"{chunk.document_name} {chunk.document_title} {chunk.content}"
        )
        lexical_score = lexical_similarity(question, searchable_text)

        if semantic and chunk.embedding:
            semantic_score = cosine_similarity(
                question_vector, json.loads(chunk.embedding)
            )
            score = (
                semantic_score * SEMANTIC_WEIGHT
                + lexical_score * LEXICAL_WEIGHT
            )
        else:
            score = lexical_score

        scored.append(
            {
                "document": chunk.document_name,
                "title": chunk.document_title,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content,
                "score": round(score, 4),
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]


def build_grounded_prompt(question: str, passages: list[dict]) -> str:
    """Build the prompt that forces the answer to come from the retrieved passages."""

    context = "\n\n".join(
        "[Source: " + passage["document"] + "]\n" + passage["content"]
        for passage in passages
    )

    return (
        "You are the KelanaAI travel assistant.\n"
        "Answer the traveller's question using ONLY the sources below.\n"
        "\n"
        "Rules:\n"
        "- If the sources do not contain the answer, say so plainly. Never guess.\n"
        "- Answer every requested sub-question explicitly; do not omit a field.\n"
        "- Quote exact figures, dates, and limits as they appear in the sources.\n"
        "- Name the source document you used at the end of the answer.\n"
        "- Keep the answer under 200 words.\n"
        "\n"
        "SOURCES\n"
        f"{context}\n"
        "\n"
        f"QUESTION\n{question}\n"
    )


def build_ungrounded_prompt(question: str) -> str:
    """Build the base model prompt, with no retrieval, used only for comparison."""

    return (
        "You are the KelanaAI travel assistant.\n"
        "Answer the traveller's question from your own knowledge.\n"
        "Keep the answer under 200 words.\n"
        "\n"
        f"QUESTION\n{question}\n"
    )


def ask_knowledge_base(db: Session, question: str) -> dict:
    """Answer one question from the knowledge base and report where the answer came from."""

    knowledge_base_id = os.getenv("KNOWLEDGE_BASE_ID", "").strip()

    # the managed path the slides teach, used the moment a KB id and IAM
    # credentials exist. Nothing else in this module changes when it does.
    if knowledge_base_id:
        try:
            result = retrieve_and_generate(question, knowledge_base_id)
        except BedrockError as error:
            raise KnowledgeBaseError(str(error)) from error

        return {
            "answer": result["answer"],
            "sources": result["sources"],
            "grounded": bool(result["sources"]),
            "mode": "bedrock-knowledge-base",
        }

    passages = search(db, question)

    if not passages or passages[0]["score"] < MINIMUM_SCORE:
        return {
            "answer": (
                "I could not find that in the KelanaAI knowledge base. "
                "Ask a travel specialist, or add a document that covers it."
            ),
            "sources": [],
            "grounded": False,
            "mode": "local-vector-store",
        }

    try:
        answer = generate_answer(build_grounded_prompt(question, passages))
    except BedrockError as error:
        raise KnowledgeBaseError(str(error)) from error

    return {
        "answer": answer,
        "sources": [
            {
                "document": passage["document"],
                "excerpt": passage["content"][:400],
                "score": passage["score"],
            }
            for passage in passages
        ],
        "grounded": True,
        "mode": "local-vector-store",
    }


def answer_without_knowledge_base(question: str) -> str:
    """Answer from the foundation model alone. Session 9 homework needs the contrast."""

    try:
        return generate_answer(build_ungrounded_prompt(question))
    except BedrockError as error:
        raise KnowledgeBaseError(str(error)) from error
