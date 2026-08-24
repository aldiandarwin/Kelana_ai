# Session 6 Evidence - Giving KelanaAI a Face

## So What?

KelanaAI now has a responsive Next.js homepage that lets a user create a trip
and receive an Amazon Bedrock itinerary without using Swagger or Postman.

## Source of Truth

- Official material: `06 Giving KelanaAI a Face.pdf`
- Homework: Improve the Homepage
- Required: Tailwind styling, destination hero image, responsive form, footer,
  commit, push, and tag `session-6`

## Delivered

- Next.js 16.3.2, React 19.2.8, TypeScript, and Tailwind CSS frontend
- local destination hero image with responsive cropping
- four-field trip form: destination, days, budget, and travel style
- two-step API flow:
  1. `POST /api/v1/trips`
  2. `POST /api/v1/trips/{trip_id}/generate`
- FastAPI CORS support for `http://localhost:3000`
- loading spinner while Amazon Bedrock is generating
- friendly network/API error state with a retry action
- AI Markdown transformed into readable itinerary cards
- footer with copyright and internal navigation links

## Verification

### Automated checks

| Check | Result |
|---|---|
| `npx eslint app` | PASS |
| `npm run build` | PASS |
| `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` | PASS - 6 tests |
| `git diff --check` | PASS |
| `npm audit` during install | PASS - 0 vulnerabilities |

### Live happy path

Test input:

- Destination: Labuan Bajo
- Days: 5
- Budget: USD 2,000
- Travel style: Culture & nature

Observed:

- CORS preflight `OPTIONS /api/v1/trips` returned `200`
- `POST /api/v1/trips` returned `200`
- local PostgreSQL created trip `id=6`
- `POST /api/v1/trips/6/generate` returned `200`
- five daily itinerary cards rendered in the browser

### Live failure path

FastAPI was stopped, then the form was submitted again.

Observed:

- the page stayed usable
- the loading state ended
- a friendly message explained that the travel service could not be reached
- a `Try again` action was available

### Responsive visual QA

| Viewport | Result |
|---|---|
| Desktop, 1264 x 712 | PASS - hero, navigation, four-column form, and content hierarchy rendered correctly |
| Mobile, 390 x 844 | PASS - hero crop remained readable, form stacked vertically, no horizontal clipping, footer stacked cleanly |

## Git Checkpoint

- Candidate commit message: `Improve the homepage styling and layout`
- Candidate tag: `session-6`
- Commit, push, and tag push require Aldian's approval.

## Residual Notes

- The synthetic happy-path test left trip `id=6` in the local PostgreSQL
  database. It is not repository data.
- End-to-end use still requires PostgreSQL, the FastAPI server, and valid local
  Amazon Bedrock credentials.
