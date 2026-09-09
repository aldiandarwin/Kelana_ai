# KelanaAI

KelanaAI is an AI travel assistant built incrementally during MAIN 2026 Phase 2.
Session 3 transforms the console application into a REST API while reusing the
deterministic Recommendation Engine from Session 2 without changing its business
rules. Session 4 adds a persistence layer so trips survive a server restart.
Session 5 adds Amazon Bedrock, so KelanaAI generates an itinerary instead of only
classifying a budget. Session 6 adds the responsive homepage, Session 7 turns the
frontend into a multi-page trip dashboard, and Session 8 makes every trip private
to one authenticated user. Session 9 adds retrieval, so KelanaAI can answer a
factual travel question from trusted documents and name the document it used.
Session 10 adds private conversation history, so a follow-up question can reuse
the earlier turns in the selected chat after a reload.

Session 11 adds cloud-ready backend packaging, idle-connection checks for Neon,
public About/404 pages, accessible route loading, and recoverable error screens.
Vercel and FastAPI Cloud are live with Neon persistence and Bedrock/RAG smoke
checks passing. The production frontend origin is configured and CORS verified.
Human rehearsal and submission gates remain; see the current evidence before recording.

- [Public KelanaAI application](https://kelana-ai-gold.vercel.app)
- [Public backend health](https://kelana-ai-92865e66.fastapicloud.dev/health)

- [Production deployment runbook](docs/session-11-deployment.md)
- [Session 11 verification and remaining gates](evidence/session-11.md)
- [Session 12 demo script and submission checklist](docs/session-12-demo.md)

## Session 3 - REST API with FastAPI

The API exposes three endpoints:

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Return the KelanaAI welcome message |
| `GET` | `/health` | Return the service health status |
| `POST` | `/api/v1/trips` | Calculate daily budget and trip category |

The POST endpoint accepts a validated JSON body containing `destination`, `days`,
and `budget`. The number of days must be greater than zero; invalid request data
returns HTTP `422` before the business logic runs. FastAPI returns valid results as
JSON and generates interactive API documentation automatically.

## Session 4 - PostgreSQL Persistence

Session 3 forgot every trip on restart. Session 4 stores them in PostgreSQL through
SQLAlchemy, and completes the CRUD surface.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/trips` | Calculate, then save the trip and return it with an id |
| `GET` | `/api/v1/trips` | Return every saved trip |
| `GET` | `/api/v1/trips/{trip_id}` | Return one trip, or `404` when the id does not exist |
| `PUT` | `/api/v1/trips/{trip_id}` | Update the budget, recalculate category and daily budget |
| `DELETE` | `/api/v1/trips/{trip_id}` | Remove one trip, or `404` when the id does not exist |

The business rules are not duplicated in the web layer. `PUT` calls the same
`calculate_daily_budget()` and `get_trip_category()` used by `POST`.

## Session 5 - Amazon Bedrock

Sessions 2 to 4 could only ever answer with one of three categories. Session 5 adds
a second path whose output is not limited by a branch count.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/trips/{trip_id}/generate` | Generate an itinerary with Amazon Bedrock, save it, and return it |

The Session 2 rules are not replaced. `category` and `daily_budget` are still
calculated by `trip_service.py`, and generating a recommendation never changes them.
The slides call this `Rules + AI`.

`backend/services/bedrock_service.py` is the only module that imports boto3. It
builds the prompt and calls the Converse API on `amazon.nova-lite-v1:0`.

Two columns were added to `trips`:

- `travel_style`, optional, feeds the prompt and defaults to `General` when empty
- `ai_recommendation`, `Text` rather than `String` because an itinerary has no
  length that can be predicted in advance

Both are nullable, so trips saved in Session 4 remain valid.

### When Bedrock fails

A failed model call returns `502` with a readable message, and the API keeps
serving. It is never allowed to surface as an unhandled `500`.

```json
{
  "detail": "Amazon Bedrock could not generate a recommendation: ..."
}
```

## Session 6 - Next.js Frontend

Session 6 gives the existing API a responsive browser interface. The homepage
uses Next.js, React, TypeScript, and Tailwind CSS. It includes:

- a local destination hero image
- a responsive four-field travel form
- visible loading and friendly error states
- AI recommendations rendered as readable cards
- a mobile layout whose form fields stack vertically
- a footer with navigation links

The backend keeps ownership of business logic, persistence, and Amazon Bedrock.
The browser first calls `POST /api/v1/trips` to validate and save the trip, then
calls `POST /api/v1/trips/{trip_id}/generate` to create the itinerary. FastAPI
allows requests from the Next.js development origin `http://localhost:3000`.

## Session 7 - Trip History Dashboard

Session 7 connects the saved PostgreSQL data to two new Next.js routes:

| Frontend route | Backend call | Purpose |
|---|---|---|
| `/trips` | `GET /api/v1/trips` | Browse every saved trip, newest first |
| `/trips/[id]` | `GET /api/v1/trips/{trip_id}` | Open one complete saved itinerary |

Networking now lives in `frontend/services/tripService.ts`. Pages and reusable
components no longer duplicate API URLs or `fetch()` handling. The homepage still
uses the existing two-step create-and-generate flow, then automatically routes the
user to `/trips` when Bedrock has finished.

The dashboard includes:

- reusable destination cards with an icon, formatted budget, category badge, and
  travel style badge
- `Family`, `Solo`, and `Couple` travel style choices matching the official
  Session 7 homework
- search by destination or travel style
- sorting by latest, oldest, or highest budget
- pagination when more than ten results match
- loading, empty, error, and not-found states
- responsive history and detail layouts

Browsing history and opening a saved trip only read PostgreSQL. Amazon Bedrock is
called only when the user generates a new itinerary.

## Session 8 - JWT Authentication and Trip Ownership

Session 8 separates authentication (who is calling) from authorization (which
trip that caller may access). Passwords are hashed with bcrypt, login returns a
signed JWT, and FastAPI derives `user_id` from that token. The frontend never
sends a user id when it creates a trip.

| Method | Path | Protection |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Public; stores a bcrypt hash, never plain text |
| `POST` | `/api/v1/auth/login` | Public; returns a short-lived Bearer JWT |
| `GET` | `/api/v1/auth/me` | JWT required; returns the current user and trip count |
| `POST` | `/api/v1/trips` | JWT required; backend assigns `user_id` |
| `GET` | `/api/v1/trips` | JWT required; filters by the current `user_id` |
| `GET` | `/api/v1/trips/{trip_id}` | JWT and matching owner required |
| `PUT` | `/api/v1/trips/{trip_id}` | Returns `403` for another user's trip |
| `DELETE` | `/api/v1/trips/{trip_id}` | Returns `403` for another user's trip |
| `POST` | `/api/v1/trips/{trip_id}/generate` | JWT and matching owner required |

Next.js stores the JWT in an `HttpOnly`, `SameSite=Lax` cookie through Route
Handlers. Browser JavaScript cannot read the token. `frontend/proxy.ts` performs
the fast redirect check for `/`, `/trips`, `/trips/[id]`, and `/profile`, while
FastAPI remains the security boundary that validates every token and ownership
decision.

The frontend adds responsive `/login` and `/register` pages, a personalized
header, logout, `/profile`, and private trip list/detail states.

### Upgrade an existing Session 7 database

Run the idempotent migration once from `backend/`:

```powershell
..\.venv\Scripts\python.exe migrate_session_8.py
```

The migration creates `users`, adds `trips.user_id`, preserves pre-auth trips
under a disabled internal `Legacy Import` owner, then enforces `NOT NULL`, an
index, and the foreign key. It does not delete existing trip data.

## Session 9 - Knowledge Base and Grounded Answers

Session 5 gave KelanaAI a model. A model knows what it was trained on, and nothing
about Sinaptik Travel's baggage policy. Session 9 retrieves the relevant passages
from a document set first, and only then asks the model to write.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/assistant` | Answer one travel question from the knowledge base and name the sources used |

The endpoint is protected exactly like the rest of the API. The response carries
`grounded` and `mode` alongside the answer, so the caller can tell a retrieved
answer from a refusal.

```json
{
  "question": "What does excess baggage cost per kilogram on a regional Asia route?",
  "answer": "Excess baggage is charged at IDR 110,000 per kilogram per leg. [Source: sinaptik-travel-policy.md]",
  "sources": [{ "document": "sinaptik-travel-policy.md", "excerpt": "...", "score": 0.7744 }],
  "grounded": true,
  "mode": "local-vector-store"
}
```

### The two retrieval paths

`backend/services/knowledge_service.py` picks a path from configuration, and the
rest of the application cannot tell the difference.

| Path | Active when | What it uses |
|---|---|---|
| `local-vector-store` | `KNOWLEDGE_BASE_ID` is empty | Titan embeddings, vectors in PostgreSQL, hybrid semantic/lexical ranking |
| `bedrock-knowledge-base` | `KNOWLEDGE_BASE_ID` is set | `bedrock-agent-runtime` `RetrieveAndGenerate` |

The local path is the one that runs today, and the reason is a documented AWS
limit rather than a preference. An Amazon Bedrock API key is restricted to Amazon
Bedrock and Amazon Bedrock Runtime actions, and cannot be used with Agents for
Amazon Bedrock or Agents for Amazon Bedrock Runtime operations. `CreateKnowledgeBase`
and `RetrieveAndGenerate` are on the wrong side of that line, and the key cannot
sign an Amazon S3 request at all.

`InvokeModel` is a Bedrock Runtime action, so `amazon.titan-embed-text-v2:0` is
available in `ap-southeast-2` with the key the class hands out. That is what makes
a genuine semantic retriever possible without an AWS account.

`backend/sync_knowledge_to_s3.py` implements the managed path in full. It refuses
to run without IAM credentials and says why, rather than failing obscurely.

### Loading the documents

Source documents live in `knowledge/` and are committed, so a reviewer can read
them next to the answers they produced. Markdown, text, and PDF are supported;
PDF page markers are retained for source citations. Run the ingestion from
`backend/`:

```powershell
..\.venv\Scripts\python.exe ingest_knowledge.py
```

Each document is split on paragraph boundaries into roughly 900 character chunks
with a 150 character overlap, embedded, and written to `knowledge_chunks`. The
script deletes a document's existing rows before writing new ones, so re-running
it after an edit never duplicates anything.

`knowledge_chunks` is a new table, so `Base.metadata.create_all()` builds it. No
migration script is needed, unlike Session 8 which altered an existing table.

### When the documents do not cover the question

Retrieval scores every chunk with a 60% semantic and 40% lexical blend, then
keeps the best four. If the best score falls below the floor in
`knowledge_service.MINIMUM_SCORE`, the model is never called
and the endpoint returns `grounded: false` with an honest refusal. Not calling the
model is the point. A model that is asked will answer, and an answer with no
source behind it is the failure mode retrieval exists to prevent.

### Comparing retrieval against the bare model

```powershell
..\.venv\Scripts\python.exe compare_rag_vs_base.py
```

The five questions in `knowledge/evaluation-questions.json` are each asked twice,
once with retrieval and once without. The result is written to
`evidence/session-09-rag-vs-base.md`.

The final Bangladesh expansion uses three official Bangladesh Tourism Board
PDFs. Across five paired questions, RAG stated 24 of 24 expected facts and
retrieved the required source in every case; the base model stated 2 of 24.
The submission-ready analysis is rendered as
`output/pdf/session-09-bangladesh-rag-vs-base.pdf`.

## Session 10 - Conversation History and Multi-Turn Context

Session 10 stores chat history in two related tables. A conversation belongs to
one authenticated user, and every user or assistant turn belongs to that
conversation.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/api/v1/conversations` | Create a private conversation |
| `GET` | `/api/v1/conversations` | List the current user's conversations |
| `GET` | `/api/v1/conversations/{id}/messages` | Reload one owned conversation and its ordered messages |
| `POST` | `/api/v1/conversations/{id}/messages` | Save a turn, rebuild history, call Bedrock, and save the reply |
| `PATCH` | `/api/v1/conversations/{id}` | Rename an owned conversation |

The frontend route `/chat` includes the homework and challenge behavior: a
conversation sidebar, click-to-reload, automatic appearance of new chats,
editable titles, message timestamps, a typing indicator, and auto-scroll.

The app, rather than Bedrock, owns memory. On every message, FastAPI loads all
ordered turns from PostgreSQL and sends them as structured Converse messages.
The user message and assistant answer commit atomically; if Bedrock fails, the
transaction rolls back so the history cannot contain a misleading orphan turn.

Chat history is private account data. The browser holds the JWT only in the
existing HttpOnly cookie, Next.js attaches it server-side, and FastAPI applies
the same `404`/`403` ownership boundary used by private trips. The conversation
content is sent to Amazon Bedrock in `ap-southeast-2` only to answer the current
turn. Passwords, JWTs, API keys, and other credentials are never included.

### Upgrade an existing Session 9 database

Run the idempotent migration once from `backend/`:

```powershell
..\.venv\Scripts\python.exe migrate_session_10.py
```

It creates `conversations` and `messages` with their foreign keys and indexes.
It does not alter or delete users, trips, knowledge chunks, or earlier evidence.

### Live multi-turn smoke test

After local AWS configuration is available, run this from `backend/`:

```powershell
..\.venv\Scripts\python.exe smoke_session_10.py
```

The script uses an isolated in-memory database and two non-sensitive sample
turns. It passes only when four messages persist in role order and the second,
context-dependent Bedrock answer identifies the city assigned in the first turn.

The lesson deliberately keeps full history for clarity. Long production threads
will eventually need a token budget, recent-turn window, or summary strategy.
Session 10 does not claim that later optimization is implemented.

## Architecture

```text
Browser / Next.js (:3000)
          |
          v
HTTP / FastAPI (:8000)
          |
          v
backend/main.py           FastAPI web and validation layer
          |
          +---> backend/schemas/trip.py    request and response shapes
          +---> backend/schemas/auth.py    auth and profile shapes
          +---> backend/schemas/conversation.py
          |                       conversation and message API shapes
          +---> backend/dependencies/auth.py
          |                       Bearer JWT -> current User
          |
          +---> backend/services/trip_service.py
          |                       Reused Session 2 business rules
          |
          +---> backend/services/bedrock_service.py
          |                       Prompt building, Converse, and embeddings
          |                                |
          |                                v
          |                       Amazon Bedrock -> Nova Lite, Titan Embeddings
          |
          +---> backend/services/knowledge_service.py
          |                       Chunk, rank, and ground the answer
          +---> backend/services/conversation_service.py
          |                       Ordered history and atomic turn persistence
          |
          v
backend/models/trip.py      Trip ORM model
backend/models/user.py      User ORM model; one user owns many trips
backend/models/knowledge.py KnowledgeChunk ORM model; one retrievable passage
backend/models/conversation.py Conversation and Message; private multi-turn history
          |
          v
backend/database.py       engine, SessionLocal, Base
          |
          v
     PostgreSQL
```

- `backend/main.py` owns the HTTP routes, request validation, and JSON responses.
- `backend/schemas/trip.py` defines the Pydantic request and response shapes.
- `backend/services/trip_service.py` remains the source of truth for the reusable
  calculations and category rules.
- `backend/services/bedrock_service.py` is the only module that talks to AWS.
- `backend/services/knowledge_service.py` owns chunking, ranking, and grounding,
  and deliberately imports no boto3 so that rule stays true.
- `backend/services/conversation_service.py` reconstructs ordered context and
  commits each user/assistant turn as one transaction.
- `backend/services/auth_service.py` owns bcrypt hashing and JWT verification.
- `backend/models/trip.py` maps the `Trip` class onto the `trips` table.
- `knowledge/` holds the source documents, committed so answers can be checked
  against them.
- `frontend/app/api/` stores the JWT as an HttpOnly cookie and forwards API calls.
- `backend/database.py` owns the connection pool and the session factory.
- `.venv/` contains local dependencies and is excluded from Git.

## Requirements

- Python 3.13 (also pinned for FastAPI Cloud in `backend/.python-version`)
- Node.js 20.9 or newer
- PostgreSQL 16 or newer, running on `localhost:5432`
- FastAPI
- Uvicorn
- SQLAlchemy
- psycopg2-binary
- python-dotenv
- boto3
- bcrypt
- python-jose with the cryptography backend
- httpx2 for FastAPI integration tests
- An Amazon Bedrock API key, handed out by the instructor. No AWS account, AWS CLI,
  or IAM user is needed.

Create the isolated environment and install dependencies from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The root requirements file forwards to `backend/requirements.txt`, the single
source of dependency versions. `fastapi[standard]` includes the CLI used to
discover the application on FastAPI Cloud. Existing local environments should
rerun the install command after pulling this configuration change.

## Set Up the Database

Create the database once. The installer path below matches PostgreSQL 18 on Windows:

```powershell
& "C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres kelana_ai
```

Then copy the connection template and fill in your own password:

```powershell
Copy-Item .env.example .env
```

`.env` is listed in `.gitignore`. Never commit it. Only `.env.example` belongs in
the repository, and its values are placeholders.

```text
DATABASE_URL=postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/kelana_ai
AWS_BEARER_TOKEN_BEDROCK=YOUR_BEDROCK_API_KEY
AWS_REGION=ap-southeast-2
MODEL_ID=amazon.nova-lite-v1:0
FRONTEND_URL=http://localhost:3000
JWT_SECRET_KEY=GENERATE_A_RANDOM_SECRET_AT_LEAST_32_CHARACTERS
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

Generate a real local JWT secret, then paste the result into `.env`:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Never commit the generated value.

The API key never appears in the source. boto3 reads `AWS_BEARER_TOKEN_BEDROCK`
from the environment after `load_dotenv()` runs.

The `trips` table is created automatically on startup by
`Base.metadata.create_all(bind=engine)`. No manual `CREATE TABLE` is needed.

### Adding the Session 5 columns to an existing database

`create_all()` only creates tables that do not exist yet. It does **not** add a
column to a table that is already there. A database first created in Session 4
therefore needs the two new columns applied by hand:

```sql
ALTER TABLE trips ADD COLUMN IF NOT EXISTS travel_style VARCHAR;
ALTER TABLE trips ADD COLUMN IF NOT EXISTS ai_recommendation TEXT;
```

Dropping the table would also work, and would also delete every trip already
saved. Prefer the `ALTER TABLE` above. A database created fresh after Session 5
needs neither, because `create_all()` builds all nine columns at once.

An existing Session 7 database also needs the Session 8 ownership migration
documented above before the updated API starts.

## Run the API

The course command `uvicorn main:app --reload` expects `backend/` to be the active
directory. From the repository root, run:

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

## FastAPI Cloud Deployment Configuration

The GitHub application directory is **`backend`**, not the repository root and
not `backend/main.py`. The files needed to install and discover the API are in
that directory:

| File or setting | Purpose |
|---|---|
| `backend/requirements.txt` | Self-contained, pinned direct dependencies, including `fastapi[standard]` |
| `backend/.python-version` | Select Python `3.13` instead of the provider's latest default |
| `backend/main.py` | Standard FastAPI CLI discovery finds the `app` object |
| Root `requirements.txt` | Forwards local installs to the same backend manifest |

This uses the provider's supported requirements-file workflow; a `pyproject.toml`
or a Dockerfile is not required. Do not copy a second dependency list into a new
manifest. See [application directories](https://fastapicloud.com/docs/builds-and-deployments/application-directory/)
and [existing-project setup](https://fastapicloud.com/docs/getting-started/existing-project/).

The existing `backend/__init__.py` makes CLI discovery in the full checkout
resolve to `backend.main:app`, with the repository root added to the import path.
The explicit Uvicorn command from `backend/` remains `main:app`. Both load the
same application source; do not remove package files just to change the displayed
import string. The deployment test exercises the CLI's discovered application.

`backend/__init__.py` explicitly adds its own directory to Python's module search
path when loaded as a package. This preserves the course's flat imports in cloud
console-script launches, where the current directory is not implicitly on
`sys.path`. Tests cover both repository-root and backend-directory launches with
Python safe-path mode; no working-directory change or `PYTHONPATH` override is needed.

Before starting the cloud app, configure its Environment Variables from the
names in `.env.example`. In particular, `DATABASE_URL` must be the Neon connection
string with the SSL parameters supplied by Neon. Set a valid Bedrock credential,
`AWS_REGION`, `MODEL_ID`, and a strong `JWT_SECRET_KEY` of at least 32 characters.
The token-lifetime key used by this repo is `ACCESS_TOKEN_EXPIRE_MINUTES`.
Use secret fields for credentials; never commit or publish their values.

The existing startup creates missing tables and inspects the schema, so database
access is needed when the application is imported. A successful image build does
not prove database connectivity, Bedrock access, or that Neon contains the RAG
documents. Those require separate cloud checks. Local `.env` files are ignored
by Git and do not automatically become cloud environment variables.

To verify CLI discovery locally after installing the updated requirements, run
from `backend/`:

```powershell
..\.venv\Scripts\python.exe -m fastapi dev
```

This is a local server command, not a deployment command. For an isolated check
that does not use the configured database or AWS credentials, run the deployment
tests from the repository root:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_deployment_config -v
```

After the changes have been reviewed and approved for commit/push, the GitHub
integration can build the new commit using the existing `backend` setting.
Confirm that the deployment uses that new commit before examining its build and
startup logs. Then test `/health`, `/docs`, authenticated database operations,
RAG, and conversational memory. Point Vercel's server-side `API_URL` to
`https://<backend-host>/api/v1`; set `FRONTEND_URL` to the final Vercel origin.

The original build log showed `Installing Python interpreter` followed by
`No such file or directory (os error 2)` without naming the missing path. These
changes close the observed repository-packaging gaps; they do not by themselves
prove that the provider's image build is fixed. If that same early error remains,
retain the failed build details for provider troubleshooting. The dashboard's
CDN **Purge Cache** button is not a dependency or Python-installation fix.

Full Session 11 deployment/homework and the `session-11` release tag remain
separate acceptance steps; this configuration change is not a completed release.

## Run the Frontend

Keep FastAPI running, then open a second terminal from the repository root:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open `http://localhost:3000`. Next.js Route Handlers call
`http://localhost:8000/api/v1` by default. To point them to another API, create
`frontend/.env.local`:

```text
API_URL=http://localhost:8000/api/v1
```

## Example Request

Login first, then include the token on every protected request:

```text
Authorization: Bearer <access_token>
```

`POST /api/v1/trips`

```json
{
  "destination": "Japan",
  "days": 5,
  "budget": 2000,
  "travel_style": "Solo"
}
```

Expected response:

```json
{
  "id": 1,
  "user_id": 1,
  "destination": "Japan",
  "days": 5,
  "budget": 2000.0,
  "daily_budget": 400.0,
  "category": "Standard",
  "created_at": "2026-08-19T08:00:00Z",
  "travel_style": "Solo",
  "ai_recommendation": null
}
```

The `id` is generated by PostgreSQL. Restart the server, call `GET /api/v1/trips`,
and the record is still there.

`travel_style` is optional in the backend request body, so a three-field body from
Session 4 is still accepted. The Session 7 frontend sends `Family`, `Solo`, or
`Couple`. `ai_recommendation` stays `null` until `/generate` is called.

`POST /api/v1/trips/1/generate`

The request has no body. The trip id in the path is enough, because every detail
the prompt needs is already stored.

```json
{
  "trip_id": 1,
  "destination": "Japan",
  "recommendation": "# 5-Day Itinerary for Japan\n\n## Day 1: Tokyo\n..."
}
```

The call takes a few seconds, because it waits on the model. Calling `GET
/api/v1/trips/1` afterwards shows the same text stored in `ai_recommendation`.

## Business Rules

The API reuses the Session 2 rules:

- Trip category: Backpacker, Standard, or Luxury
- Daily budget: total budget divided by travel days

### Trip Category

| Budget | Category |
|---:|---|
| Less than 1000 | Backpacker |
| 1000 through 3000 | Standard |
| Greater than 3000 | Luxury |

## Run the Tests

From the repository root:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

The suite keeps the Session 2 business-rule coverage and adds an in-memory
Session 8 integration test. It registers two users and proves anonymous requests
return `401`, lists are isolated, frontend-supplied `user_id` is ignored, and
cross-user detail/update/delete/generate requests return `403`.

Session 9 adds chunking, ranking, retrieval, and assistant endpoint tests. None
of them calls AWS. The chunking and similarity functions are pure, and the
endpoint tests patch the Bedrock entry points with `unittest.mock`, which is the
first use of patching in this repository. It is here because Session 9 is the
first feature whose happy path cannot be reached without an AWS call.

Session 10 adds integration tests for authenticated creation/listing, ownership,
ordered reload, two-turn context reconstruction, timestamps, renaming, request
validation, and transaction rollback. `smoke_session_10.py` is the separate,
explicit live Bedrock check; the automated suite never calls AWS.

## Working Directory

The repository uses two working directories, and mixing them is the most common
failure here.

| What you run | Where you run it | Why |
|---|---|---|
| `uvicorn main:app --reload` | inside `backend/` | `main.py` imports `database`, `models`, and `services` as flat modules, matching the course slides |
| `python -m unittest discover -s tests` | repository root | the tests import `backend.services.trip_service` as a package |

## Course Checkpoints

- Session 1: tags `v0.1.0` and `session-1`
- Session 2: commit `Add recommendation engine` and tag `session-2`
- Session 3: commit `Convert KelanaAI into FastAPI` and tag `session-3`
- Session 4: commit `Add PostgreSQL persistence` and tag `session-4`
- Session 5: commit `Enhance AI prompt and save recommendation to database` and tag `session-5`
- Session 6: commit `Improve the homepage styling and layout` and tag `session-6`
- Session 7: commit `Create trip dashboard and enhance trip card components` and
  tag `session-7`
- Session 8: commit `Protect CRUD endpoints to respect user ownership` and
  tag `session-8`
- Session 9 target: commit `Expand Knowledge Base and compare RAG vs base-model answers`
  and tag `session-9`
- Session 10 target: commit `Add conversational memory and improve chat experience`
  and tag `session-10`
