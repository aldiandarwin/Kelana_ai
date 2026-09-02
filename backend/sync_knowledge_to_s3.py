"""Session 9: upload knowledge/ to Amazon S3 and start a Knowledge Base ingestion job.

This is the managed path the Session 9 slides teach, written in boto3 instead of
the AWS CLI so it runs from the same virtualenv as the rest of the backend:

    ..\\.venv\\Scripts\\python.exe sync_knowledge_to_s3.py

It will not run with the Bedrock API key handed out in class, and that is not a
bug in this script.

AWS documents at bedrock/latest/userguide/api-keys-use.html that an Amazon
Bedrock API key is limited to Amazon Bedrock and Amazon Bedrock Runtime actions,
and cannot be used with Agents for Amazon Bedrock or Agents for Amazon Bedrock
Runtime operations. CreateKnowledgeBase and StartIngestionJob are Agents for
Amazon Bedrock operations. Amazon S3 is a different service entirely, and the
bearer token cannot sign a request to it at all.

So this script needs real IAM credentials. It checks for them first and explains
itself rather than failing with an opaque AWS error. Until they exist, KelanaAI
retrieves through the local vector store in knowledge_service.py, which uses only
Bedrock Runtime actions that the class key does permit.
"""

import os
import sys
import time
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError
from dotenv import load_dotenv

load_dotenv()

REPO_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = REPO_ROOT / "knowledge"

CONTENT_TYPES = {
    ".md": "text/markdown",
    ".txt": "text/plain",
    ".pdf": "application/pdf",
}
INGESTION_TERMINAL_STATES = {"COMPLETE", "FAILED", "STOPPED"}


def _require(name: str) -> str:
    """Read a required setting from .env, or explain exactly what is missing."""

    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(
            f"{name} is not set in .env. The managed Knowledge Base path needs "
            "KNOWLEDGE_BASE_ID, KNOWLEDGE_BASE_DATA_SOURCE_ID, and S3_KNOWLEDGE_BUCKET."
        )
    return value


def _has_iam_credentials() -> bool:
    """Return True when boto3 can find credentials that are not the Bedrock bearer token."""

    return boto3.session.Session().get_credentials() is not None


def _wait_for_ingestion(
    agent,
    knowledge_base_id: str,
    data_source_id: str,
    ingestion_job_id: str,
    timeout_seconds: int = 900,
    poll_seconds: int = 5,
) -> str:
    """Wait until Bedrock has indexed the upload, or fail with evidence."""

    deadline = time.monotonic() + timeout_seconds
    last_status = ""

    while time.monotonic() < deadline:
        response = agent.get_ingestion_job(
            knowledgeBaseId=knowledge_base_id,
            dataSourceId=data_source_id,
            ingestionJobId=ingestion_job_id,
        )
        ingestion = response["ingestionJob"]
        status = ingestion["status"]
        if status != last_status:
            print(f"  ingestion_status={status}")
            last_status = status

        if status in INGESTION_TERMINAL_STATES:
            if status != "COMPLETE":
                reasons = ingestion.get("failureReasons", [])
                raise RuntimeError(
                    f"Knowledge Base ingestion ended as {status}: "
                    + ("; ".join(reasons) or "AWS returned no failure reason")
                )
            return status

        time.sleep(poll_seconds)

    raise TimeoutError(
        f"Knowledge Base ingestion did not finish within {timeout_seconds} seconds."
    )


def sync() -> None:
    """Upload every knowledge document to S3, then trigger a Knowledge Base sync."""

    if not _has_iam_credentials():
        print(
            "No IAM credentials found. The Amazon Bedrock API key in .env cannot "
            "reach Amazon S3 or Agents for Amazon Bedrock, so this script stops here.",
            file=sys.stderr,
        )
        print(
            "See bedrock/latest/userguide/api-keys-use.html. KelanaAI keeps working "
            "through the local vector store in the meantime.",
            file=sys.stderr,
        )
        raise SystemExit(2)

    bucket = _require("S3_KNOWLEDGE_BUCKET")
    knowledge_base_id = _require("KNOWLEDGE_BASE_ID")
    data_source_id = _require("KNOWLEDGE_BASE_DATA_SOURCE_ID")
    region = os.getenv("AWS_REGION")

    documents = sorted(
        path
        for path in KNOWLEDGE_DIR.iterdir()
        if path.is_file() and path.suffix in CONTENT_TYPES and path.name != "README.md"
    )
    if not documents:
        raise RuntimeError(f"No uploadable documents found in {KNOWLEDGE_DIR}")

    s3 = boto3.client("s3", region_name=region)
    agent = boto3.client("bedrock-agent", region_name=region)

    try:
        for path in documents:
            key = "travel-guides/" + path.name
            s3.upload_file(
                str(path),
                bucket,
                key,
                ExtraArgs={"ContentType": CONTENT_TYPES[path.suffix]},
            )
            print(f"  uploaded s3://{bucket}/{key}")

        job = agent.start_ingestion_job(
            knowledgeBaseId=knowledge_base_id,
            dataSourceId=data_source_id,
            description="KelanaAI Session 9 knowledge base sync",
        )
        ingestion_job_id = job["ingestionJob"]["ingestionJobId"]
        final_status = _wait_for_ingestion(
            agent,
            knowledge_base_id,
            data_source_id,
            ingestion_job_id,
        )
    except NoCredentialsError as error:
        raise RuntimeError(f"AWS rejected the credentials: {error}") from error
    except (BotoCoreError, ClientError) as error:
        raise RuntimeError(f"AWS refused the sync: {error}") from error

    print(f"Session 9 S3 sync complete. {len(documents)} document(s) uploaded.")
    print(f"bucket={bucket}")
    print(f"knowledge_base_id={knowledge_base_id}")
    print(f"ingestion_job_id={ingestion_job_id}")
    print(f"ingestion_status={final_status}")
    print(
        "Set KNOWLEDGE_BASE_ID in .env and restart the API to move retrieval onto "
        "the managed path."
    )


if __name__ == "__main__":
    sync()
