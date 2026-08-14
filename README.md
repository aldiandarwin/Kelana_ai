# KelanaAI

KelanaAI is an AI travel assistant built incrementally during MAIN 2026 Phase 2.
Session 3 transforms the console application into a REST API while reusing the
deterministic Recommendation Engine from Session 2 without changing its business
rules.

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

## Architecture

```text
HTTP client / Swagger UI
          |
          v
backend/main.py           FastAPI web and validation layer
          |
          v
backend/services/trip_service.py
                          Reused Session 2 business rules
```

- `backend/main.py` owns the HTTP routes, request validation, and JSON responses.
- `backend/services/trip_service.py` remains the source of truth for the reusable
  calculations and category rules.
- `.venv/` contains local dependencies and is excluded from Git.

## Requirements

- Python 3.12 or newer
- FastAPI
- Uvicorn

Create the isolated environment and install dependencies from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

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
  "destination": "Japan",
  "days": 5,
  "budget": 2000.0,
  "daily_budget": 400.0,
  "category": "Standard"
}
```

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
as before the web layer was added.

## Course Checkpoints

- Session 1: tags `v0.1.0` and `session-1`
- Session 2: commit `Add recommendation engine` and tag `session-2`
- Session 3 target: commit `Convert KelanaAI into FastAPI` and tag `session-3`
