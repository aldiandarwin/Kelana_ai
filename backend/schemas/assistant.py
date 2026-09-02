"""Request and response shapes for the KelanaAI grounded assistant endpoint."""

from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    """Validated JSON body for one travel question."""

    question: str = Field(min_length=3, max_length=500)


class AssistantSource(BaseModel):
    """One retrieved passage, named so the traveller can verify the answer."""

    document: str
    excerpt: str
    # None on the managed Knowledge Base path, which does not return a score
    score: float | None = None


class AssistantResponse(BaseModel):
    """The reply of POST /api/v1/assistant, shaped as the Session 9 lab slide."""

    question: str
    answer: str
    sources: list[AssistantSource]
    # False when nothing scored high enough, so the UI can say so honestly
    grounded: bool
    # which retrieval path answered: local-vector-store or bedrock-knowledge-base
    mode: str
