# Session 11 Evidence - Deployment Preparation

## So What?

The repository now contains the missing backend build inputs and Session 11 UX
polish. **Local checks pass; public deployment and Session 12 submission are not
complete.** Do not present these checks as a successful FastAPI Cloud build or a
Neon/Bedrock production integration test.

Verification date: **9 September 2026 (WIB)**.
Repository: `https://github.com/aldiandarwin/Kelana_ai`.
Starting commit: `f932a8a16e914be73528ed2978b5b2730f5cdf07`.
The pre-publication remote check found `main` and `session-10` at that same commit;
`session-11` did not exist. Aldian approved the 21-file preparation checkpoint with
message `Prepare KelanaAI for cloud deployment`. This document records the checks
before that commit; use Git history and the provider's deployed commit for the
subsequent publication/build result.

## Acceptance matrix

| Requirement | Status | Evidence / limitation |
|---|---|---|
| Correct backend application directory | Screenshot verified | Aldian's FastAPI Cloud setting is `backend` |
| Backend dependency manifest | Verified locally | Self-contained pinned `backend/requirements.txt`; root forwards to it |
| Python version and CLI discovery | Verified locally | Python 3.13, actual FastAPI CLI discovers `backend.main:app` from a full checkout |
| Fresh dependency installation | Passed | New isolated virtualenv installed canonical manifest; `pip check` reported no broken requirements |
| Backend regression tests | Passed: 49/49 | SQLite-isolated tests, no real AWS calls or production DB writes |
| PostgreSQL idle connection configuration | Unit verified | `pool_pre_ping=True` and `connect_timeout=10`; no live Neon connectivity claim |
| Custom application icon | Verified locally | Existing `/icon.svg` returns HTTP 200 |
| Public About page | Verified locally | `/about` returns 200; author, features, architecture and AI/privacy caveats visible without login |
| Better 404 page | Verified locally | Unknown public path returns 404 and stays on the recovery page without an auth redirect |
| Error/500 experience | Component verified | Route/global/trips error fallbacks conceal error details and invoke the installed Next.js `retry` callback; real production failure not induced |
| Loading screen | Component verified | Global route loading has live status, busy state, reduced-motion support; existing generation/chat loading retained |
| Responsive new pages | Browser verified locally | About and 404 reviewed at default desktop and 390x844 viewport; mobile client/scroll widths both 375px (scrollbar excluded), no horizontal overflow |
| Frontend regression checks | Passed: 7/7 + lint | Built-in Node tests run real TS/TSX leaf components with framework navigation stubs |
| Production frontend build | Passed locally | Next.js 16.3.2 production build and TypeScript succeeded |
| Authentication boundary | Verified locally | `/trips` and `/chat` return 307 without a cookie; API conversations returns 401; browser trip navigation goes to login |
| Deployment instructions | Written | `docs/session-11-deployment.md` plus README links |
| FastAPI Cloud new build and startup | Pending | Login verified; environment correction saved; approved code publication will trigger the next build |
| Neon connection and schema | Partially verified | Console query succeeded for `kelanaai-db`; no base tables in `public` at inspection time; app persistence/RAG remain unverified |
| Vercel public end-to-end flow | Pending | Public frontend URL/env/deployed commit not yet verified |
| Actual phone and classmate beta test | Pending human validation | Browser resizing is not a substitute for a classmate's real feedback |
| Session 11 commit/tag | Pending approval and release checks | Do not move Session 10 tag |
| Session 12 video, Drive access and LMS submission | Pending | Demo script exists; no recording or submission evidence yet |

## Reproducible local checks

With the updated requirements installed, run from repository root:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_deployment_config -v
```

The actual full-suite run used the fresh test environment at
`tmp/session-11-build-check-056980e1/`, with dotenv disabled, in-memory SQLite,
and dummy test-only JWT/AWS values. It ran `unittest.defaultTestLoader.discover('tests')`:
49 tests, OK, 12.486 seconds. It did not modify the active local `.venv`.

From `frontend/`:

```powershell
npm run test:session11
npm run lint
npm run build
```

Frontend test summary: 7 passed, 0 failed. Lint exited 0. Production build exited
0, compiled all routes including `/about`, `/_not-found`, and the API Route Handlers.
QA used the production server on `127.0.0.1:3100`; it did not replace port 3000.

HTTP checks: `/about` 200; `/session-11-missing-page` 404; `/trips` 307; `/chat` 307;
`/api/conversations` 401; `/icon.svg` 200. The browser visibly confirmed the
unauthenticated About page, custom 404, and `/login?next=%2Ftrips` redirect.

An initial test expected `main:app` from CLI discovery; the real CLI returned
`backend.main:app` because `backend/__init__.py` makes it a package. The test and
documentation were corrected to validate the discovered application, and the
complete suite was rerun. No package file was removed to force an import name.

## Build failure diagnosis: known vs unknown

Known: the supplied build log fails near Python installation with
`No such file or directory (os error 2)` and does not identify the missing path.
The repository previously lacked a dependency manifest and Python version pin
inside the configured backend directory. Those packaging gaps are now addressed.

Unknown: whether the provider's next image build succeeds. This is not evidence
that Neon credentials were wrong, nor proof that packaging was the only cause.
Docker's Linux engine was unavailable locally, so the provider's Linux build
has not been reproduced.

## Security and remaining external gates

- `.env`, `.env.production`, frontend local env files and QA intermediates are
  ignored by Git. No real cloud credentials were added to the change set.
- Local database credentials were not changed. The approved cloud change renamed
  existing environment keys only; no password value was changed or copied.
- Aldian completed login to Vercel, FastAPI Cloud and Neon. All three dashboards
  were inspected successfully after the initial expired login was resolved.
- Vercel's unsubmitted import form initially selected FastAPI with root `./`.
  The draft now selects Next.js and `frontend`, with server-side
  `API_URL=https://kelana-ai-92865e66.fastapicloud.dev/api/v1` for Production and
  Preview. Eleven auto-detected empty backend variable entries were removed only
  from that draft. No project deployment was submitted.
- The original FastAPI Cloud key `DATABASE_URL` pointed to localhost, while the
  valid Neon connection was under the unused key `database_url_neon`. With Aldian's
  explicit approval, the former was renamed `DATABASE_URL_LOCAL_BACKUP` and the
  latter `DATABASE_URL`. Save Only was used before the code push. Reload confirmed
  the active key targets the Neon pooler and `kelanaai-db` with `sslmode=require`;
  the unused backup still targets localhost. No credential values are recorded here.
- A read-only Neon query against `information_schema.tables` succeeded and found
  no public base tables in `kelanaai-db`. Once the build and active connection
  setting are corrected, startup can create the application's missing tables;
  knowledge ingestion and real end-to-end checks are still required.
- An AST index refresh (`graphify update .`) was blocked by the execution safety
  reviewer over possible external code transmission. It was not bypassed; graph
  freshness is unverified and is not needed to claim the test results above.
- Before release: publish the approved preparation checkpoint, build the new commit, verify
  Neon/Bedrock, ingest the public reference documents into the confirmed target,
  deploy Vercel and complete the public acceptance checklist.

The implementation followed the brief-to-build workflow: preserve existing
architecture and scope, add missing deployment/UX pieces, and keep local versus
production proof separate. No recording, Drive sharing or LMS submission is claimed.
