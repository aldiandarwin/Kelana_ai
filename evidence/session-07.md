# Session 7 Evidence - Connecting KelanaAI's Brain and Face

## So What?

KelanaAI is now a multi-page application. Users can create a trip, browse all
saved itineraries, and reopen one detail page without asking Amazon Bedrock to
generate the same recommendation again.

## Source of Truth

- Official material: `07 Connecting KelanaAI's Brain and Face.pdf`
- Core lab: `/` -> `/trips` -> `/trips/[id]`
- Challenge: search by destination or travel style, plus trip sorting
- Homework: destination icon, formatted budget, category badge, travel style
  badge, and optional pagination
- Official homework travel styles: `Family`, `Solo`, and `Couple`

## Delivered

- shared `frontend/services/tripService.ts` for all trip API calls
- shared TypeScript trip contracts in `frontend/types/trip.ts`
- reusable header, footer, `TripCard`, dashboard, and itinerary components
- `/trips` history route backed by `GET /api/v1/trips`
- `/trips/[id]` dynamic route backed by `GET /api/v1/trips/{id}`
- homepage redirect to `/trips` after create + Bedrock generation succeeds
- newest-first API ordering
- search, three sort modes, and ten-item pagination
- loading, empty, error, pending-itinerary, and not-found states
- `NEXT_PUBLIC_API_URL` and `FRONTEND_URL` environment templates

## Verification

### Automated checks

| Check | Result |
|---|---|
| `npm run lint` | PASS |
| `npx tsc --noEmit --incremental false` | PASS |
| `npm run build` | PASS |
| `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` | PASS - 6 tests |
| `git diff --check` | PASS |

The production build identified `/trips` and `/trips/[id]` as dynamic,
server-rendered routes.

### Live backend and route checks

| Check | Result |
|---|---|
| `GET /health` | PASS - `{"status":"OK"}` |
| `POST /api/v1/trips` | PASS - all nine response fields returned for `Bandung / 4 days / USD 1,600 / Solo` |
| derived payload fields | PASS - `daily_budget=400`, `category=Standard`, `ai_recommendation=null` |
| `GET /api/v1/trips` | PASS - 8 saved trips after the payload check |
| newest-first ordering | PASS - trip `id=10` appeared first |
| `GET /api/v1/trips/10` | PASS - every persisted value matched the POST response |
| `/trips` server response | PASS - title, search, and latest destination present |
| `/trips/10` server response | PASS - full metadata and pending-itinerary state present |
| `/trips/999999` UI | PASS - custom not-found copy present |

### Live end-to-end generation

Browser input:

- destination: Yogyakarta
- days: 3
- total budget: USD 900
- travel style: Culture & nature

Observed:

- `POST /api/v1/trips` created trip `id=9`
- `POST /api/v1/trips/9/generate` saved the Bedrock recommendation
- the homepage automatically navigated to `/trips`
- Yogyakarta appeared first with `AI itinerary ready`
- `/trips/9` rendered six readable itinerary sections

### Failure path

FastAPI was stopped before navigating back to `/trips`. The mobile UI displayed
the friendly `Trip history is unavailable` state. After FastAPI restarted, the
`Try again` action issued a fresh request and restored all seven cards.

### Visual QA

| Viewport / behavior | Result |
|---|---|
| Desktop dashboard | PASS - hero, controls, multi-column cards, badges, and spacing rendered cleanly |
| Mobile dashboard, 390 x 844 | PASS - navigation, hero, controls, and cards stack without horizontal clipping |
| Mobile detail, 390 x 844 | PASS - metadata stacks and itinerary remains readable |
| Official travel styles | PASS - homepage offers only `Family`, `Solo`, and `Couple` |
| Trip card homework fields | PASS - Bandung card showed icon, `USD 1,600`, `Standard`, and `Solo` |
| Badge styling | PASS - category and travel-style badges used distinct computed colors |
| Search `Japan` | PASS - one matching card |
| Sort `Highest budget` | PASS - Japan at USD 5,000 moved to the first position |
| Card navigation | PASS - card opened the matching dynamic detail route |
| Markdown variance | PASS - `###` to `######` subsections render without raw heading marks |

## Git Checkpoint

- Approved commit message: `Create trip dashboard and enhance trip card components`
- Approved tag: `session-7`
- Aldian approved the commit, push, and tag push on 27 August 2026.
