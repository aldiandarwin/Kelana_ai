"""Session 9: load Markdown, text, and PDF knowledge into knowledge_chunks.

Run from backend/ whenever a document is added or edited:

    ..\\.venv\\Scripts\\python.exe ingest_knowledge.py

The script is idempotent. Each document's rows are deleted before its new rows
are written, so re-running never duplicates a document.
"""

import sys
from pathlib import Path

from pypdf import PdfReader

from database import Base, SessionLocal, engine
from models.knowledge import KnowledgeChunk  # noqa: F401 - registers the table in metadata
from services.bedrock_service import BedrockError, embed_text
from services.knowledge_service import ingest_document

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1] / "knowledge"

# knowledge/README.md documents the folder, it is not a source document itself.
EXCLUDED_FILES = {"README.md"}
SUPPORTED_SUFFIXES = {".md", ".txt", ".pdf"}


def _document_title(text: str, fallback: str) -> str:
    """Return the first Markdown H1 of a document, or its file name."""

    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def _clean_pdf_text(text: str) -> str:
    """Normalise common extraction artifacts without rewriting source facts."""

    return (
        text.replace("\ufffd", " ")
        .replace("\x7f", " ")
        .replace("\x02", " ")
        .replace("\r\n", "\n")
        .strip()
    )


def _read_document(path: Path) -> tuple[str, str]:
    """Return text and title while preserving page provenance for PDFs."""

    if path.suffix.lower() != ".pdf":
        text = path.read_text(encoding="utf-8")
        return text, _document_title(text, path.stem)

    reader = PdfReader(path)
    pages: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = _clean_pdf_text(page.extract_text() or "")
        if text:
            pages.append(f"## PDF page {page_number}\n\n{text}")

    if not pages:
        raise RuntimeError(
            f"No extractable text found in {path.name}. OCR the PDF before ingestion."
        )

    metadata_title = ""
    if reader.metadata and reader.metadata.title:
        metadata_title = str(reader.metadata.title).strip()
    title = metadata_title or path.stem.replace("-", " ").title()
    return "\n\n".join(pages), title


def _embeddings_available() -> bool:
    """Probe the embedding model once so the run reports which path it took."""

    try:
        embed_text("knowledge base readiness probe")
        return True
    except BedrockError as error:
        print("Embedding model unavailable, falling back to lexical retrieval.")
        print(f"  reason: {error}")
        return False


def ingest() -> None:
    """Ingest every supported document in knowledge/ and print the evidence."""

    if not KNOWLEDGE_DIR.is_dir():
        raise RuntimeError(f"Knowledge folder not found: {KNOWLEDGE_DIR}")

    documents = sorted(
        path
        for path in KNOWLEDGE_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in SUPPORTED_SUFFIXES
        and path.name not in EXCLUDED_FILES
    )
    if not documents:
        raise RuntimeError(f"No supported documents found in {KNOWLEDGE_DIR}")

    Base.metadata.create_all(bind=engine)

    with_embeddings = _embeddings_available()

    db = SessionLocal()
    try:
        total_chunks = 0
        for path in documents:
            text, title = _read_document(path)
            written = ingest_document(
                db,
                document_name=path.name,
                document_title=title,
                text=text,
                with_embeddings=with_embeddings,
            )
            total_chunks += written
            print(f"  {path.name:<32} {written:>3} chunk(s)")

        stored = db.query(KnowledgeChunk).count()
        embedded = (
            db.query(KnowledgeChunk).filter(KnowledgeChunk.embedding.isnot(None)).count()
        )
    finally:
        db.close()

    mode = "semantic (Titan embeddings)" if with_embeddings else "lexical (no embeddings)"
    print(
        f"Session 9 ingestion complete. {len(documents)} document(s), "
        f"{total_chunks} chunk(s) written."
    )
    print(f"retrieval_mode={mode}")
    print(f"rows_in_table={stored}")
    print(f"rows_with_embedding={embedded}")

    if stored != total_chunks:
        print(
            "WARNING: the table holds rows for documents no longer in knowledge/. "
            "Delete them, or restore the missing files.",
            file=sys.stderr,
        )


if __name__ == "__main__":
    ingest()
