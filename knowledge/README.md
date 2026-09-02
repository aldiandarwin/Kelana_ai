# KelanaAI Knowledge Base

Files in this folder are sources for Retrieval-Augmented Generation.
`backend/ingest_knowledge.py` extracts Markdown, text, and PDF content, splits it
into chunks, and stores the chunks in `knowledge_chunks`. It uses Amazon Titan
Text Embeddings V2 when the credential permits that model and reports an explicit
lexical fallback otherwise. `POST /api/v1/assistant` retrieves before Amazon
Bedrock writes the answer.

## Baseline and Bangladesh expansion

Session 9's lab asks for four travel documents. The homework then asks for three
or more additional documents and five questions that require the new material.
The repository keeps both groups so the word "expand" is observable.

| Set | Documents |
|---|---|
| Pre-expansion corpus | `visa-japan.md`, `tokyo-attractions.md`, `packing-checklist.md`, `travel-insurance-basics.md`, `sinaptik-travel-policy.md`, `sinaptik-insurance-tiers.md`, `south-korea-travel-guide.md`, `singapore-visa-guide.md` |
| Bangladesh homework expansion | `bangladesh-tourist-handbook.pdf`, `bangladesh-sundarbans.pdf`, `bangladesh-world-heritage-tour.pdf` |

All three Bangladesh files are official Bangladesh Tourism Board publications.
Their original URLs, page counts, access date, and SHA-256 hashes are frozen in
`bangladesh-sources.json`.

| Document | Pages | Evaluation focus |
|---|---:|---|
| Bangladesh Tourist Hand Book | 76 | Khagrachari and Saint Martin's Island |
| Sundarbans | 8 | Karamjal and Kachikhali |
| World Heritage Tour - 12 Nights, 13 Days | 2 | Day 5 Bagerhat and Mongla itinerary |

The five cases in `evaluation-questions.json` draw only on this expansion.
`backend/compare_rag_vs_base.py` asks every question twice - first with
retrieval and then with the same foundation model without documents - and writes
the case-level evidence to `evidence/session-09-rag-vs-base.md`.

## Provenance and freshness

The PDFs are source evidence, not guaranteed-current operational travel advice.
Questions and answers deliberately say "according to the document." Verify
current entry permission, transport schedules, closures, and safety guidance
with the relevant authority before travelling.

The source pages do not state an open-content licence. The repository preserves
publisher attribution and uses the files for this educational assignment.

## Ingestion paths

Local reproducible path:

```powershell
cd backend
..\.venv\Scripts\python.exe ingest_knowledge.py
```

Managed AWS path, when IAM credentials plus the real bucket, Knowledge Base ID,
and data source ID are available:

```powershell
cd backend
..\.venv\Scripts\python.exe sync_knowledge_to_s3.py
```

The managed script uploads every supported source to `travel-guides/`, starts
an ingestion job, and waits for terminal status `COMPLETE`. A started job is
not reported as a successful sync.

Ingestion is idempotent. Re-running replaces a document's stored chunks instead
of duplicating them.
