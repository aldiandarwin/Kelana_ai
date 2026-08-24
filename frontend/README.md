# KelanaAI Frontend

The Session 6 frontend gives the existing FastAPI, PostgreSQL, and Amazon Bedrock
stack a responsive web interface. It uses Next.js, React, TypeScript, and Tailwind
CSS.

## Run locally

Start the FastAPI backend on `http://localhost:8000`, then run:

```powershell
npm install
npm run dev
```

Open `http://localhost:3000`.

The frontend defaults to `http://localhost:8000`. To use another backend, create
`.env.local` and set:

```text
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Request flow

1. `POST /api/v1/trips` validates and stores the trip.
2. `POST /api/v1/trips/{trip_id}/generate` asks Amazon Bedrock for the itinerary.
3. React displays the saved trip summary and recommendation.

The browser never calls Amazon Bedrock directly.
