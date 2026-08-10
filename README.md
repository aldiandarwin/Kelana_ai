# KelanaAI

KelanaAI is an AI travel assistant built incrementally during MAIN 2026 Phase 2.
Session 1 establishes the product foundation through a Python console application.

## Session 1 - Trip Summary Generator

The console application asks for:

- Destination
- Country
- Number of days
- Budget
- Currency
- Travel month

It converts `days` to an integer, converts `budget` to a float, and prints a
structured trip summary through `print_trip_summary()`.

## Project Structure

```text
Kelana_ai/
|-- README.md
|-- backend/
|   `-- main.py
`-- frontend/
    `-- .gitkeep
```

The `frontend/` directory is reserved for the Next.js application introduced in
a later session.

## Requirements

- Python 3.12 or newer

## Run the Application

From the repository root:

```bash
python backend/main.py
```

Enter the requested trip information when prompted.

## Session 1 Evidence Target

- Console application runs end-to-end.
- The six required inputs appear in the output.
- Initial commit message: `Create initial KelanaAI console app`.
- Product release tag: `v0.1.0`.
- Course checkpoint tag: `session-1`.
