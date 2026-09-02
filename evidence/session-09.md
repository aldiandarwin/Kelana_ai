# Session 09 Evidence - Teaching KelanaAI to Read Knowledge

## So What?

KelanaAI can now answer document-specific Bangladesh travel questions through a
live Amazon Bedrock-backed local RAG path and show the files used as evidence.
Across five paired questions, RAG stated 24 of 24 expected facts and retrieved
the required source in every case; the same foundation model without retrieval
stated 2 of 24 facts.

This is a verified homework result, not a production-readiness claim. The local
vector-store path is live. The managed Amazon S3 plus Bedrock Knowledge Base
path is implemented but remains unverified because this environment has no IAM
credentials, S3 bucket, Knowledge Base ID, or Data Source ID.

## Acceptance Matrix

| Requirement | Status | Observable proof |
|---|---|---|
| Add 3+ travel documents | Verified | Three official Bangladesh Tourism Board PDFs were added on top of eight baseline documents |
| Make documents retrievable | Verified locally | 11 documents, 127 chunks, 127 embeddings stored in `knowledge_chunks` |
| Synchronise to managed S3 data source | Not verified | Sync script is ready, but managed AWS identifiers and IAM credentials are absent |
| Test 5 new questions | Verified | `knowledge/evaluation-questions.json`, revision `2026-09-02-bangladesh-v2` |
| Questions require the new documents | Verified | Each case declares a Bangladesh PDF as `requires_document`; automated contract tests pass |
| Compare RAG with base model | Verified live | Same model and fixed generation settings; RAG 24/24 versus base 2/24 |
| Record full answers and citations | Verified | `evidence/session-09-rag-vs-base.md` and the PDF report contain all paired responses |
| RAG API and source display | Verified in code and tests | `POST /api/v1/assistant`, Next.js `/assistant`, and `sources[]` |
| Upload group knowledge to Google Drive | Pending external publication | Local source files are ready; the shared folder currently exposes no authenticated upload session |
| Commit, push, tag, submit link | Pending Aldian approval | Target message and tag are listed in Release Plan |

## Bangladesh Knowledge Expansion

All three files were downloaded from Bangladesh Tourism Board publication
infrastructure on 2026-09-02. Exact URLs, hashes, page counts, and attribution
are preserved in `knowledge/bangladesh-sources.json`.

| File | Pages | SHA-256 | Evaluation use |
|---|---:|---|---|
| `bangladesh-tourist-handbook.pdf` | 76 | `F7F94802736536F6F34806A47E9AF58607F03B45C1836A25286B94D1484DDF6F` | Q1-Q2 |
| `bangladesh-sundarbans.pdf` | 8 | `82FFB983FBCE26734027E80977F1B056C3BD21C765FF784CC1D8D44B2001433A` | Q3-Q4 |
| `bangladesh-world-heritage-tour.pdf` | 2 | `BD79FA6C257D6224E36BAFD124B2A3E00A730E5A21D81D1CBC2D48EBD0D72184` | Q5 |

No explicit open-content license was found on the source pages. The files retain
publisher attribution and are included for this educational assignment. Travel
times, permissions, closures, prices, and safety information must be refreshed
from current authorities before real-world use.

## Ingestion Proof

The ingestion path accepts Markdown, text, and PDF files. PDF page markers are
preserved in extracted content so citations can identify the source page.

```text
rows=127 embedded=127 documents=11
bangladesh-sundarbans.pdf: 9 chunks
bangladesh-tourist-handbook.pdf: 67 chunks
bangladesh-world-heritage-tour.pdf: 8 chunks
baseline documents: 43 chunks across 8 files
```

The 127 stored vectors were generated with Amazon Titan Text Embeddings V2.
Generation used Amazon Nova Lite in `ap-southeast-2`.

## Evaluation Contract

The dataset contains five source-bound cases:

1. Khagrachari distance, rivers, and main attraction.
2. Saint Martin's Island status, nickname, and Cheera-Dwip tide behavior.
3. Karamjal permission, official station, and breeding-center function.
4. Kachikhali travel time, alternate name, and forest range.
5. World Heritage Tour day-5 timings, distances, and Bagerhat stops.

The cases are split into three targeted tests, one regression test, and one
holdout test. Each case includes expected facts, accepted strings, severity,
failure category, rationale, and required source file. The immutable dataset
hash for the final run is:

```text
031cc8e6e2a01db877553db3ecbff9a55cd5903ab4d9bf16b4d73d0b0e2ffc9e
```

Both paths used `amazon.nova-lite-v1:0`, temperature `0.0`, and maximum `500`
tokens. The only intended difference was retrieval context.

## Final Comparison

```text
Retrieval mode: local-vector-store
RAG expected facts:       24/24
Base expected facts:       2/24
RAG answers with sources:   5/5
Required source retrieved:  5/5
Complete RAG cases:         5/5
Verdict:                   PASS
```

The base model produced plausible but unsupported substitutions, including a
320 km Khagrachari distance, the wrong rivers, a crocodile breeding center at
Karamjal, and incorrect day-5 itinerary figures. RAG returned the document-bound
values and source filenames.

The first Bangladesh run exposed a retrieval weakness: semantic-only ranking
could place a topically similar but factually wrong chunk above the required
passage. The final ranker combines 60% semantic similarity and 40% lexical
matching across filename, title, and content. The prompt also requires every
sub-question to be answered from the supplied excerpts. This change raised the
measured result from 14/24 to 24/24 while preserving the required-source gate.

## API and Frontend

- `POST /api/v1/assistant` is protected by the existing Session 8 authentication.
- The backend returns `answer`, `grounded`, `mode`, and `sources[]`.
- `sources[]` carries the document name, excerpt, and match score.
- Next.js `/assistant` renders the answer and its source cards.
- Browser code calls the Next.js route handler; AWS credentials remain server-side.
- Questions are bounded to 3-500 characters before any Bedrock call.

The paired evaluation invoked the real Bedrock generation and embedding services.
Endpoint behavior and response shape are covered by the backend suite; production
frontend compilation proves `/assistant` and `/api/assistant` integrate cleanly.

## Automated Verification

```text
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
36 tests passed

npm run lint
passed

npx tsc --noEmit --incremental false
passed

npm run build
passed - Next.js 16.3.2, 14 routes generated
```

The backend suite covers authentication regression, chunking, PDF ingestion,
ranking, prompt construction, dataset contracts, holdout presence, S3 ingestion
status handling, endpoint status paths, and citation shape.

## PDF Deliverable

`output/pdf/session-09-bangladesh-rag-vs-base.pdf` is a nine-page A4 report that
contains the corpus manifest, methodology, scoreboard, all five paired responses,
case-level findings, limitations, source URLs, and reproduction commands.

PDF QA completed:

- valid and unencrypted;
- nine pages, A4;
- all pages rendered to PNG and visually inspected;
- no clipping or overlapping elements found;
- extracted text contains no replacement characters;
- final size: 21,880 bytes.

## AWS Status

Verified live:

- Amazon Titan embedding calls;
- Amazon Nova Lite generation calls;
- local PostgreSQL retrieval store;
- grounded response generation with document citations.

Implemented but not yet verified:

- PDF upload to Amazon S3;
- Bedrock Knowledge Base ingestion job;
- polling until ingestion status `COMPLETE`;
- managed `RetrieveAndGenerate` path.

`backend/sync_knowledge_to_s3.py` fails closed when required configuration is
missing and waits for a terminal ingestion status when configuration exists.
To close the managed path, configure IAM credentials locally plus
`S3_KNOWLEDGE_BUCKET`, `KNOWLEDGE_BASE_ID`, and
`KNOWLEDGE_BASE_DATA_SOURCE_ID`; do not paste credentials into chat or commit
them.

## Security and Limits

- No secret or credential was added to source files.
- `.env` remains local and ignored.
- The comparison is a five-case educational evaluation, not a production SLA.
- Deterministic string matching prevents grader drift but cannot judge nuanced
  paraphrases beyond the accepted variants.
- Local retrieval scans all 127 chunks; a much larger corpus should use a vector
  index such as `pgvector`.

## Release Plan

- Commit message: `Expand Knowledge Base and compare RAG vs base-model answers`
- Tag: `session-9`
- Push target: `origin/main` and `origin/session-9`
- Submission artifact: GitHub link to the resulting commit

Commit, push, and tag remain intentionally pending until Aldian approves the
final staged diff. Google Drive upload also remains pending until an authenticated
write-capable Drive connection is available.
