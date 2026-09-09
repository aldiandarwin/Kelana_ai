# Session 11 Evidence - Public Deployment Verification

## So What?

**Vercel and FastAPI Cloud are live on the same commit.** Neon persistence,
Bedrock generation, conversational memory and document retrieval have now been
exercised through the public Next.js proxy: 27 integration checks passed, followed
by 5/5 frozen Bangladesh cases (24/24 expected strings, correct source in each).
Final CORS configuration is now applied and verified. Authenticated browser
rehearsal, actual-phone/classmate validation and Session 12 video/submission
are still incomplete.

Verification date: **9 September 2026 (WIB)**.
Repository: `https://github.com/aldiandarwin/Kelana_ai`.
Starting commit: `f932a8a16e914be73528ed2978b5b2730f5cdf07`.
The approved 21-file preparation checkpoint was committed and pushed as
`08ba4b9dc934f4afb62648ae23ef9205630d5c03`, message
`Prepare KelanaAI for cloud deployment`. Fetch confirmed local HEAD and
`origin/main` match (0 ahead / 0 behind), and `session-10` remains at the starting
commit. The approved five-file startup follow-up was then committed and pushed as
`bf3719f262b3cc710d58bc6c34c764c296394fc5`, message
`Fix backend imports for FastAPI Cloud startup`. Fetch verified HEAD equals
`origin/main`, divergence 0/0. `session-11` has not been created.

## Acceptance matrix

| Requirement | Status | Evidence / limitation |
|---|---|---|
| Correct backend application directory | Screenshot verified | Aldian's FastAPI Cloud setting is `backend` |
| Backend dependency manifest | Verified locally | Self-contained pinned `backend/requirements.txt`; root forwards to it |
| Python version and CLI discovery | Verified locally | Python 3.13, actual FastAPI CLI discovers `backend.main:app` from a full checkout |
| Fresh dependency installation | Passed | New isolated virtualenv installed canonical manifest; `pip check` reported no broken requirements |
| Backend regression tests | Passed: 50/50 (follow-up local) | Original preparation had 49 tests; the added safe-path test covers both root and backend-directory CLI startup |
| PostgreSQL idle connection configuration | Unit verified; Neon live queries passed | `pool_pre_ping=True` and `connect_timeout=10`; a long-idle production recovery scenario was not induced |
| Custom application icon | Verified locally | Existing `/icon.svg` returns HTTP 200 |
| Public About page | Verified locally | `/about` returns 200; author, features, architecture and AI/privacy caveats visible without login |
| Better 404 page | Verified locally | Unknown public path returns 404 and stays on the recovery page without an auth redirect |
| Error/500 experience | Component verified | Route/global/trips error fallbacks conceal error details and invoke the installed Next.js `retry` callback; real production failure not induced |
| Loading screen | Component verified | Global route loading has live status, busy state, reduced-motion support; existing generation/chat loading retained |
| Responsive new pages | Browser verified locally | About and 404 reviewed at default desktop and 390x844 viewport; mobile client/scroll widths both 375px (scrollbar excluded), no horizontal overflow |
| Frontend regression checks | Passed: 7/7 + lint | Built-in Node tests run real TS/TSX leaf components with framework navigation stubs |
| Production frontend build | Passed locally | Next.js 16.3.2 production build and TypeScript succeeded |
| Authentication boundary | Verified locally and through public proxy | Login/logout, secure HttpOnly SameSite=Lax cookie, anonymous 401 and cross-owner trip/conversation 403 passed |
| Deployment instructions | Written | `docs/session-11-deployment.md` plus README links |
| FastAPI Cloud new build and startup | Ready / Live | Follow-up `bf3719f`; public health 200, Swagger 200, anonymous conversations 401 |
| Neon connection and schema | Verified | Five tables created; production trip/message persistence; 11 documents, 127 chunks and 127 embeddings |
| Vercel public integration | Passed: 27/27 | Real HTTP requests through Vercel proxy; not a substitute for all authenticated browser UX checks |
| Bangladesh RAG replay | Passed: 5/5 sampled cases | 24/24 fixture facts and required sources; see `session-11-public-rag.json`; not a general quality guarantee |
| Backend frontend-origin configuration | Applied and verified | Approved FRONTEND_URL; deployment b0fa6c9e Ready/Live; Vercel preflight 200, unrelated origin 400 |
| Actual phone and classmate beta test | Pending human validation | Browser resizing is not a substitute for a classmate's real feedback |
| Verification evidence publication / Session 11 tag | Evidence commit/push approved; tag pending release checks | Publication message: Verify production deployment and RAG integration; do not move Session 10 tag |
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

The next cloud deployment, `b9d0b7d2-64a1-44d5-8cea-1a52a5cb26a2`, built commit
`08ba4b9` and reached Verifying Readiness. Runtime logs then identified a separate
startup failure in `/app/backend/main.py:18`: `ModuleNotFoundError: No module named
'database'`. The runtime installed Python 3.13.15 on Linux; the early interpreter
installation error did not recur on this attempt. The public `/health` probe
still returned 404, so the backend was not serving traffic.

### Startup compatibility follow-up

The initial local test used `python -c` from `backend/`, which implicitly exposes
the working directory on `sys.path`. FastAPI's console entrypoint discovers
`backend.main:app` and adds its package parent, but cannot rely on that implicit
backend path. The exact missing-database error was reproduced locally with `-P`
from both `backend/` and repository root, before applying the fix.

`backend/__init__.py` now adds its absolute directory once when loaded as a package.
This is a compatibility shim for the existing flat course imports, not a broad
package refactor. It leaves the working directory, local CLI commands, credentials,
schemas and route behavior unchanged.

After the fix: all 50 backend tests passed in 14.161 seconds, including both safe-
path startup cases. A separate smoke test launched the actual installed
`fastapi.exe run main.py` console executable on a temporary localhost port: health
returned 200 and anonymous conversations returned 401. It used in-memory SQLite
and dummy credentials; the temporary server was stopped afterward. No real
Bedrock request or Neon write was performed by these tests.

The approved follow-up is now published and passed cloud readiness. Docker's
Linux engine was unavailable locally; the provider's actual Linux deployment,
not the Windows unit tests alone, supplies the cloud startup evidence below.

## Public deployment and integration proof

- FastAPI Cloud deployment: `59fc52c7-6f8e-4a12-b3fb-1bc28648f244`, Ready and Live.
- Backend: `https://kelana-ai-92865e66.fastapicloud.dev`.
- Vercel deployment: `5m8h6XWJxdfJjJi2HGUeGpWZwJWC`, Ready, production.
- Frontend: `https://kelana-ai-gold.vercel.app`.
- Both dashboards show commit `bf3719f262b3cc710d58bc6c34c764c296394fc5`.
- Vercel uses Next.js, root `frontend`, server-side `API_URL` pointing to the
  actual FastAPI Cloud `/api/v1`. No backend credentials were copied to Vercel.

Neon console and a direct read-only query confirmed `kelanaai-db` on production.
Startup created `users`, `trips`, `knowledge_chunks`, `conversations`, `messages`.
An explicit zero-row guard preceded ingestion. The existing script loaded the
repository's 11 guides/course fixtures with Titan embeddings. A fresh query
confirmed 11 distinct documents / 127 chunks / 127 non-null embeddings. No local
users, trips, or conversations were transferred, and `.env` was not changed.

HTTP integration run `20260909T083050` used two synthetic QA accounts, trip 1 and
conversation 1. All 27 checks passed:

| Checks | Observed |
|---|---|
| Public About / unknown page / icon / anonymous conversations | 200 / 404 / 200 / 401 |
| Two accounts: register and login | 201 / 200 for each |
| Auth cookie and profile | Secure, HttpOnly, SameSite=Lax; profile 200 |
| Invalid trip with zero days | 422 |
| Save trip, generate real Bedrock itinerary, reload saved result | 200; recommendation persisted |
| Create chat and two real Bedrock turns | 201 then 200 / 200 |
| Reload chat | 200; four messages with creation timestamps |
| RAG API and source-bearing response | 200; grounded true with sources |
| Second account reading first account's trip and conversation | 403 / 403 |
| Logout, anonymous access, relogin, load history | 200 / 401 / 200 / 200 |

Memory input: `Saya ingin ke Bangladesh selama 3 hari. Saya vegetarian dan tidak
makan ikan. Ingat preferensi ini untuk perjalanan ini.` The follow-up asked for
the earlier food preference and duration. The actual reply retained `Vegetarian`,
`Tidak makan ikan`, and `3 hari`. This verifies this conversation, not memory across
different conversations or RAG inside Chat.

Browser inspection separately confirmed the public About and custom 404 pages.
About was visually checked at desktop and 390x844: client/scroll width both 375px
(excluding scrollbar), with no horizontal overflow. Authenticated chat scrolling,
typing animation and title interactions still need a production browser rehearsal.

### AI quality boundary and frozen replay

The initial ad-hoc RAG probe asked which "two heritage areas" the World Heritage
Tour combines. Its reply was: `The World Heritage Tour takes 12 nights and 13 days.
It combines the heritage areas of Dhaka and Paharpur.` The supplied excerpt supports
the duration and lists multiple places; it does not establish that two-area claim.
This is an unsupported assertion, despite `grounded=true`. The question also had
an unverified premise. Preserve this exploratory finding; it is not a golden case.

The first itinerary test deliberately served integration, not realistic planning:
its submitted budget was 5,000,000 **USD**. Its generated summary also multiplied
1,900 by three after listing three different day budgets. Do not present that
output as verified travel advice or a passed arithmetic-quality test. Use the
900 USD demo input in the rehearsal and check the actual output before recording.

An unchanged production replay then used the existing Session 9 five-case dataset,
not a replacement of the failed exploratory question. All 5 returned 200, 24/24
expected fact strings, and the required document. Full prompts, responses, source
excerpts, latency, model settings and dataset SHA-256 are in
`session-11-public-rag.json`. No prompt/model tuning or new base-model comparison
was performed. Existing split labels are retained; Q5 was already used in Session 9
and is not a fresh holdout. This five-case convenience sample is not a reliability
estimate. Verdict for overall AI quality remains **INCONCLUSIVE**, while the
specified source-bound deployment smoke cases passed.

Three synthetic QA accounts in total (including the frozen replay account) and
their test records remain in Neon; credentials were not printed or committed.
No production data was deleted for cleanup.

### Approved frontend-origin configuration

On 9 September 2026 (around 20:27 WIB), with Aldian's explicit approval, added
`FRONTEND_URL=https://kelana-ai-gold.vercel.app` to FastAPI Cloud and selected
Save and Redeploy. The saved read-only field confirmed the exact value.
Deployment `b0fa6c9e-aa41-4ceb-9598-afc3490a46b2` shows trigger Environment change,
Ready/Live, and the same `bf3719f` application revision. Credentials were unchanged.

Post-redeploy read-only checks:

- OPTIONS `/api/v1/auth/me` from the production Vercel origin: 200 and
  `Access-Control-Allow-Origin: https://kelana-ai-gold.vercel.app`.
- The same OPTIONS request from `https://untrusted-origin.example`: 400,
  `Disallowed CORS origin`. No wildcard permission was introduced.
- Backend `/health` and `/docs`: 200 / 200.
- Vercel `/about` and anonymous `/api/conversations`: 200 / 401.

These checks verify the configuration change; the earlier 27 integration and
5 RAG tests are separately timestamped evidence, not claimed as rerun here.
This documentation-only checkpoint does not change application code or the
frozen RAG result's tested revision. Aldian approved publishing these five
documentation/evidence files with `Verify production deployment and RAG integration`.

### Remaining release actions

1. Aldian creates/logs into a production demo account and completes the browser
   rehearsal, including chat UX. Record actual-phone and classmate feedback.
2. Only tag Session 11 after its remaining gates are checked and Aldian approves
   the tag. Session 12 recording/Drive/LMS are separate.

## Security and remaining external gates

- `.env`, `.env.production`, frontend local env files and QA intermediates are
  ignored by Git. No real cloud credentials were added to the change set.
- Local database credentials were not changed. The approved cloud change renamed
  existing environment keys only; no password value was changed or copied.
- Aldian completed login to Vercel, FastAPI Cloud and Neon. All three dashboards
  were inspected successfully after the initial expired login was resolved.
- Vercel's import form initially selected FastAPI with root `./`.
  The submitted production configuration selects Next.js and `frontend`, with server-side
  `API_URL=https://kelana-ai-92865e66.fastapicloud.dev/api/v1` for Production and
  Preview. Eleven auto-detected empty backend variable entries were removed only
  from that draft. The subsequent deployment is now Ready, as recorded above.
- The original FastAPI Cloud key `DATABASE_URL` pointed to localhost, while the
  valid Neon connection was under the unused key `database_url_neon`. With Aldian's
  explicit approval, the former was renamed `DATABASE_URL_LOCAL_BACKUP` and the
  latter `DATABASE_URL`. Save Only was used before the code push. Reload confirmed
  the active key targets the Neon pooler and `kelanaai-db` with `sslmode=require`;
  the unused backup still targets localhost. No credential values are recorded here.
- The first read-only Neon query found no public base tables. After startup was
  fixed, the same query returned all five application tables. Ingestion and public
  proxy integration have since passed, as recorded above.
- An AST index refresh (`graphify update .`) was blocked by the execution safety
  reviewer over possible external code transmission. It was not bypassed; graph
  freshness is unverified and is not needed to claim the test results above.
- Before the final release tag: complete the remaining human checks. Publication
  of this evidence is approved, but it does not constitute a completed Session 12
  video submission.

The implementation followed the brief-to-build workflow: preserve existing
architecture and scope, add missing deployment/UX pieces, and keep local versus
production proof separate. The AI-output-evaluator evidence-audit guidance kept
the unsupported exploratory answer visible and separated integration success from
general answer-quality claims. No recording, Drive sharing or LMS submission is claimed.
