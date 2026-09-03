"""Session 5: Amazon Bedrock integration for KelanaAI.

This is the only module that knows about boto3. main.py and knowledge_service.py
reach Bedrock through the functions below, never through the AWS SDK directly.

Session 9 adds embeddings and a second question-answering entry point here for
the same reason, so that the retrieval layer stays free of AWS concerns.

Session 10 adds structured multi-turn Converse messages. The application still
owns memory; Bedrock receives only the history supplied for the current call.
"""

import json
import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from dotenv import load_dotenv

# load .env first so boto3 can read AWS_BEARER_TOKEN_BEDROCK from the environment
load_dotenv()

# bedrock-runtime runs inference; the plain "bedrock" service only manages models
client = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.getenv("AWS_REGION"),
)

# trips saved in Session 4 have no travel style, so the prompt needs a fallback
DEFAULT_TRAVEL_STYLE = "General"

# Session 9: Titan Text Embeddings V2 is supported in ap-southeast-2 and accepts
# 256, 512, or 1024 dimensions. 1024 is the documented default.
DEFAULT_EMBEDDING_MODEL_ID = "amazon.titan-embed-text-v2:0"
EMBEDDING_DIMENSIONS = 1024

# built on first use, not at import, so the test suite never waits on a client
# it does not need. Only the managed Knowledge Base path touches it.
_agent_client = None

CONVERSATION_SYSTEM_PROMPT = (
    "You are KelanaAI, a practical travel-planning assistant. "
    "Use the supplied conversation history to resolve follow-up references. "
    "Do not claim to remember anything outside this conversation. "
    "Answer clearly in Markdown and keep the response under 500 words."
)


class BedrockError(RuntimeError):
    """Raised when Bedrock cannot answer, so the web layer can reply 502 instead of 500."""


def build_prompt(
    destination: str,
    days: int,
    budget: float,
    travel_style: str | None = None,
) -> str:
    """Build the itinerary prompt from the details of one saved trip."""

    return (
        "You are an experienced travel planner.\n"
        f"Create a {days}-day itinerary for {destination}.\n"
        f"Budget: USD {budget:,.0f}\n"
        f"Travel Style: {travel_style or DEFAULT_TRAVEL_STYLE}\n"
        "\n"
        "Break every day into three parts:\n"
        "- Morning: exactly 2 to 3 activities, never more than 3\n"
        "- Afternoon: cultural sites and local experiences\n"
        "- Evening: dinner spots and nightlife\n"
        "\n"
        "Also include:\n"
        "- An estimated daily budget in USD\n"
        "- Local food recommendations\n"
        "- Transportation suggestions\n"
        "- Practical travel tips\n"
        "\n"
        "Format your response as Markdown with headers (##) and bullet lists (-)."
    )


def _converse_messages(
    messages: list[dict],
    *,
    system_prompt: str | None = None,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Send structured messages through Converse and return generated text."""

    inference_config = {}
    if temperature is not None:
        inference_config["temperature"] = temperature
    if max_tokens is not None:
        inference_config["maxTokens"] = max_tokens

    try:
        # content is a list of blocks, not a plain string
        request = {
            "modelId": os.getenv("MODEL_ID"),
            "messages": messages,
        }
        if system_prompt:
            request["system"] = [{"text": system_prompt}]
        if inference_config:
            request["inferenceConfig"] = inference_config

        response = client.converse(
            **request,
        )
    except (BotoCoreError, ClientError) as error:
        # an AWS failure must never escape as a 500 and take the API down with it
        raise BedrockError(str(error)) from error

    return response["output"]["message"]["content"][0]["text"]


def _converse(
    prompt: str,
    *,
    temperature: float | None = None,
    max_tokens: int | None = None,
) -> str:
    """Send one prompt through Converse while preserving older call sites."""

    return _converse_messages(
        [{"role": "user", "content": [{"text": prompt}]}],
        temperature=temperature,
        max_tokens=max_tokens,
    )


def generate_itinerary(prompt: str) -> str:
    """Send the prompt to Amazon Bedrock and return the generated itinerary."""

    return _converse(prompt)


def generate_answer(prompt: str) -> str:
    """Session 9: deterministic settings make paired evaluations comparable."""

    return _converse(prompt, temperature=0.0, max_tokens=500)


def generate_conversation_reply(history: list[dict[str, str]]) -> str:
    """Session 10: answer with the user/assistant turns supplied by the app."""

    messages: list[dict] = []
    for turn in history:
        role = turn.get("role")
        content = turn.get("content", "").strip()
        if role not in {"user", "assistant"} or not content:
            raise BedrockError("Conversation history contains an invalid message")
        messages.append({"role": role, "content": [{"text": content}]})

    if not messages or messages[-1]["role"] != "user":
        raise BedrockError("Conversation history must end with a user message")

    return _converse_messages(
        messages,
        system_prompt=CONVERSATION_SYSTEM_PROMPT,
        temperature=0.2,
        max_tokens=700,
    )


def embed_text(text: str) -> list[float]:
    """Session 9: turn one passage or question into a vector with Titan Text Embeddings V2."""

    model_id = os.getenv("EMBEDDING_MODEL_ID", DEFAULT_EMBEDDING_MODEL_ID)

    try:
        # embeddings use invoke_model, not converse: Converse is for chat models
        response = client.invoke_model(
            body=json.dumps(
                {
                    "inputText": text,
                    "dimensions": EMBEDDING_DIMENSIONS,
                    # normalised vectors make cosine similarity a plain dot product
                    "normalize": True,
                }
            ),
            modelId=model_id,
            accept="application/json",
            contentType="application/json",
        )
    except (BotoCoreError, ClientError) as error:
        raise BedrockError(str(error)) from error

    return json.loads(response["body"].read())["embedding"]


def retrieve_and_generate(question: str, knowledge_base_id: str) -> dict:
    """Session 9: ask a managed Amazon Bedrock Knowledge Base to retrieve, then answer.

    This is the path the slides teach. It needs IAM credentials, because an
    Amazon Bedrock API key does not cover Agents for Amazon Bedrock Runtime
    actions. It stays unused until KNOWLEDGE_BASE_ID is set.
    """

    global _agent_client
    if _agent_client is None:
        # bedrock-agent-runtime, not bedrock-runtime: retrieval is a different service
        _agent_client = boto3.client(
            service_name="bedrock-agent-runtime",
            region_name=os.getenv("AWS_REGION"),
        )

    region = os.getenv("AWS_REGION")
    model_id = os.getenv("MODEL_ID")

    try:
        response = _agent_client.retrieve_and_generate(
            input={"text": question},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": knowledge_base_id,
                    "modelArn": f"arn:aws:bedrock:{region}::foundation-model/{model_id}",
                    "retrievalConfiguration": {
                        # vectorSearchConfiguration, not the slide's managedSearchConfiguration
                        "vectorSearchConfiguration": {"numberOfResults": 4}
                    },
                },
            },
        )
    except (BotoCoreError, ClientError) as error:
        raise BedrockError(str(error)) from error

    sources = []
    for citation in response.get("citations", []):
        for reference in citation.get("retrievedReferences", []):
            uri = reference.get("location", {}).get("s3Location", {}).get("uri", "")
            sources.append(
                {
                    "document": uri.rsplit("/", 1)[-1] or uri,
                    "excerpt": reference.get("content", {}).get("text", "")[:400],
                    "score": None,
                }
            )

    return {"answer": response["output"]["text"], "sources": sources}
