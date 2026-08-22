"""Session 5: Amazon Bedrock integration for KelanaAI.

This is the only module that knows about boto3. main.py reaches Bedrock through
the two functions below, never through the AWS SDK directly.
"""

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


def generate_itinerary(prompt: str) -> str:
    """Send the prompt to Amazon Bedrock and return the generated itinerary."""

    try:
        # content is a list of blocks, not a plain string
        response = client.converse(
            modelId=os.getenv("MODEL_ID"),
            messages=[
                {
                    "role": "user",
                    "content": [{"text": prompt}],
                }
            ],
        )
    except (BotoCoreError, ClientError) as error:
        # an AWS failure must never escape as a 500 and take the API down with it
        raise BedrockError(str(error)) from error

    return response["output"]["message"]["content"][0]["text"]
