"""Session 9: the KnowledgeChunk ORM model. One retrievable passage per row."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


def _utc_now() -> datetime:
    """Return the current UTC time. Replaces the deprecated datetime.utcnow."""

    return datetime.now(timezone.utc)


class KnowledgeChunk(Base):
    """One chunk of one knowledge base document, with its embedding."""

    __tablename__ = "knowledge_chunks"

    id = Column(Integer, primary_key=True)
    # the file name in knowledge/, which is also what the answer cites as its source
    document_name = Column(String, nullable=False, index=True)
    document_title = Column(String, nullable=False)
    # position inside the document, so a citation can point at the right passage
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    # a JSON array of floats. Nullable, because retrieval falls back to a lexical
    # score when the Bedrock key is not allowed to call the embedding model.
    embedding = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utc_now)
