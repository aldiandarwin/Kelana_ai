# KelanaAI

KelanaAI is an AI travel assistant built incrementally during MAIN 2026 Phase 2.
Session 3 transforms the console application into a REST API while reusing the
deterministic Recommendation Engine from Session 2 without changing its business
rules. Session 4 adds a persistence layer so trips survive a server restart.
Session 5 adds Amazon Bedrock, so KelanaAI generates an itinerary instead of only
classifying a budget.

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
          |
          +---> backend/services/trip_service.py
          |                       Reused Session 2 business rules
          |
          +---> backend/services/bedrock_service.py
          |                       Prompt building and the Converse API call
          |                                |
          |                                v
          |                       Amazon Bedrock -> Amazon Nova Lite
          |
          v
backend/models/trip.py    Trip ORM model
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
- `backend/models/trip.py` maps the `Trip` class onto the `trips` table.
- `backend/database.py` owns the connection pool and the session factory.
- `.venv/` contains local dependencies and is excluded from Git.

## Requirements

- Python 3.12 or newer
- Node.js 20.9 or newer
- PostgreSQL 16 or newer, running on `localhost:5432`
- FastAPI
- Uvicorn
- SQLAlchemy
- psycopg2-binary
- python-dotenv
- boto3
- An Amazon Bedrock API key, handed out by the instructor. No AWS account, AWS CLI,
  or IAM user is needed.

Create the isolated environment and install dependencies from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

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
```

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

## Run the Frontend

Keep FastAPI running, then open a second terminal from the repository root:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open `http://localhost:3000`. The frontend calls
`http://localhost:8000` by default. To point it to another API, create
`frontend/.env.local`:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Example Request

`POST /api/v1/trips`

```json
{
  "destination": "Japan",
  "days": 5,
  "budget": 2000
}
```

Expected response:

```json
{
  "id": 1,
  "destination": "Japan",
  "days": 5,
  "budget": 2000.0,
  "daily_budget": 400.0,
  "category": "Standard",
  "created_at": "2026-08-19T08:00:00Z",
  "travel_style": null,
  "ai_recommendation": null
}
```

The `id` is generated by PostgreSQL. Restart the server, call `GET /api/v1/trips`,
and the record is still there.

`travel_style` is optional in the request body, so a three-field body from Session 4
is still accepted. `ai_recommendation` stays `null` until `/generate` is called.

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

The existing tests verify that the Session 2 business logic still behaves exactly
as before the web layer was added. They need no database, because the business
rules never touch one.

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
