# KelanaAI

KelanaAI is an AI travel assistant built incrementally during MAIN 2026 Phase 2.
Session 2 adds a deterministic Recommendation Engine and separates business rules
from terminal input and output.

## Session 2 - Recommendation Engine

The console application collects:

- Destination and country
- Number of days
- Total budget and currency
- Travel month

It then derives:

- Trip category: Backpacker, Standard, or Luxury
- Daily budget: total budget divided by travel days
- Travel season: Peak, Holiday, or Regular Season
- A list of recommended places

This session uses explicit Python rules rather than a generative AI model. The same
input produces the same recommendation.

## Architecture

```text
Kelana_ai/
|-- README.md
|-- backend/
|   |-- __init__.py
|   |-- main.py
|   `-- services/
|       |-- __init__.py
|       `-- trip_service.py
|-- frontend/
|   `-- .gitkeep
`-- tests/
    `-- test_trip_service.py
```

- `backend/main.py` owns the presentation layer: keyboard input and terminal output.
- `backend/services/trip_service.py` owns reusable calculations and business rules.

The separation lets Session 3 expose the same service functions through FastAPI
without duplicating the recommendation logic.

## Business Rules

### Trip Category

| Budget | Category |
|---:|---|
| Less than 1000 | Backpacker |
| 1000 through 3000 | Standard |
| Greater than 3000 | Luxury |

### Travel Season

| Month | Season |
|---|---|
| December | Peak Season |
| June | Holiday Season |
| Other months | Regular Season |

## Requirements

- Python 3.12 or newer

No external Python package is required for Session 2.

## Run the Application

From the repository root:

```bash
python backend/main.py
```

Example input:

```text
Destination  : Japan
Country      : Japan
Days         : 5
Budget       : 1500
Currency     : USD
Travel Month : December
```

The output includes `Standard`, `300 USD/Day`, `Peak Season`, and the three
recommended places from the assignment.

## Run the Tests

From the repository root:

```bash
python -m unittest discover -s tests -v
```

The tests cover category boundaries, season rules, daily budget calculation,
zero-day failure behavior, and the recommended places list.

## Course Checkpoints

- Session 1: tags `v0.1.0` and `session-1`
- Session 2 target: commit `Add recommendation engine` and tag `session-2`
