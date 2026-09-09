# Session 11 - Production Deployment Runbook

## Outcome and release boundary

One application, three hosting responsibilities:

| Service | Responsibility | Repository/configuration |
|---|---|---|
| Vercel | Next.js UI and same-origin API Route Handlers | Root directory `frontend` |
| FastAPI Cloud | Python API, validation, authorization, AI orchestration | Application directory `backend` |
| Neon | PostgreSQL trips, users, document chunks, conversations and messages | Backend `DATABASE_URL`, with Neon SSL parameters |
| Amazon Bedrock | Text generation and optional Titan embeddings | Backend AWS credential and model configuration |

The browser calls Next.js `/api/*`. Next.js forwards the JWT to FastAPI.
FastAPI queries PostgreSQL and calls Bedrock when generation is needed; those
are separate branches, not a mandatory database-then-model chain for every request.
RAG is `/assistant`; conversational memory is `/chat`. Do not describe Chat as
automatically using the document retriever.

Current status is tracked in `evidence/session-11.md`. Local test success is not
a claim that any public deployment is healthy.

## 1. Prepare and publish the reviewed code

- Confirm repo `aldiandarwin/Kelana_ai`, branch `main`, and review the complete diff.
- `backend/requirements.txt` is the canonical manifest; root requirements forwards to it.
- Python is pinned to `3.13` in the application directory; `fastapi[standard]` supplies the CLI.
- Full-checkout CLI discovery resolves `backend.main:app`; explicit Uvicorn from `backend/` uses `main:app`.
- Commit/push only after Aldian approves the scoped files and commit message.
- Existing Session 8/9/10 tags are historical checkpoints: never move them for this deployment.

## 2. Configure Neon and FastAPI Cloud

Use the existing accounts/projects. No paid upgrade is required by this runbook.
The screenshot-confirmed FastAPI Cloud application directory is already `backend`.

Dashboard inspection found a configuration mismatch: `DATABASE_URL` pointed to
localhost, while the valid Neon connection was stored under `database_url_neon`.
This code reads only `DATABASE_URL`. With Aldian's approval, the old local setting
was renamed `DATABASE_URL_LOCAL_BACKUP` and the existing Neon key became
`DATABASE_URL`. Save Only and a reload verified the persisted mapping before the
code push. No password rotation or new database was needed to fix the key name.

| FastAPI Cloud variable | Required value or rule |
|---|---|
| `DATABASE_URL` | Neon PostgreSQL connection string from Connect; retain `sslmode=require` and other supplied parameters |
| `JWT_SECRET_KEY` | Unique random secret, at least 32 characters; mark secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Actual key used by this repository; example `480` |
| `AWS_BEARER_TOKEN_BEDROCK` | Aldian's valid authorized Bedrock API key; mark secret |
| `AWS_REGION` | Region where that key/model works; current local setup uses `ap-southeast-2` |
| `MODEL_ID` | Current implementation uses `amazon.nova-lite-v1:0` |
| `EMBEDDING_MODEL_ID` | `amazon.titan-embed-text-v2:0` for the existing semantic retriever |
| `KNOWLEDGE_BASE_ID` | Leave empty for the existing PostgreSQL retriever |
| `FRONTEND_URL` | Final Vercel origin, e.g. `https://<frontend-host>`, without a path |

Do not copy the instructor's credentials from screenshots. Do not set
`JWT_EXPIRE_MINUTES` expecting it to change the lifetime: that is not this repo's
configuration key. Do not put AWS/database/JWT secrets in Vercel public variables.
FastAPI Cloud hosting region and Bedrock model region are independent settings.

The API creates missing tables at startup and checks `trips.user_id`, so it needs
database access during import. Fresh Neon databases get the current five tables.
An older schema needs the documented migrations; `create_all` does not alter
existing columns. Back up existing data and review the migration target first.
Do not copy local user accounts or private conversation history just for a demo.

After publishing the approved commit, inspect the deployment's exact commit hash,
build log, startup log and public URL. Test `/health` and `/docs`, then actual
authenticated data operations. `/health` alone does not exercise a new database
query or Bedrock call.

### If the build still fails

The supplied log ended at `Installing Python interpreter` with
`No such file or directory (os error 2)`, without a missing filename. Repository
packaging gaps have been repaired, but the exact provider failure is not proven.
If it repeats on the new commit with Python 3.13 selected, retain the deployment
ID, commit hash and full build details for FastAPI Cloud support. Do not randomly
change the Neon password or use CDN `Purge Cache` as a Python build fix.

## 3. Populate the production knowledge base

Git deployment sends code, not local PostgreSQL data. A new Neon database has no
reference documents until ingestion or an explicitly scoped data transfer occurs.

1. Use a local full checkout containing `knowledge/`; do not assume files above
   `backend/` are accessible in the provider's runtime shell.
2. Inspect only non-secret target metadata to confirm the intended Neon project,
   branch, database and host. Use an ignored production env file or provider
   environment; never paste connection strings into chat, logs or command history.
3. Query the target before writing:

   ```sql
   SELECT count(DISTINCT document_name) AS documents,
          count(*) AS chunks,
          count(embedding) AS embedded_chunks
   FROM knowledge_chunks;
   ```

4. If the target table is empty, run `ingest_knowledge.py` from `backend/` with
   that verified production environment and the existing public guide documents.
   It calls Bedrock for embeddings and therefore uses the account's inference quota.
   If rows already exist, stop for review/approval: the script replaces rows for
   matching document names. Do not silently overwrite existing production knowledge.
5. Repeat the count query and test a source-bound Bangladesh question on the
   public `/assistant` page. Verify the cited document/excerpt and `grounded` result.
   The last observed local reference was 11 documents / 127 chunks / 127 embeddings;
   that is not evidence of production contents or a permanent required count.

Embeddings are JSON arrays in a PostgreSQL Text column. This implementation does
not require a pgvector extension. If ingestion reports lexical fallback, document
it and resolve embedding access before claiming that semantic retrieval is active.
Do not fill `KNOWLEDGE_BASE_ID` with a made-up ID: it switches the retrieval path.

## 4. Deploy Vercel

1. Import `aldiandarwin/Kelana_ai` into the intended Vercel account/team.
2. Select Next.js, Root Directory `frontend`, production branch `main`.
3. Use the lockfile and normal `npm run build`; match locally tested Node 22.x
   where supported by the project settings. No static export: API routes need a server.
4. Add server-side `API_URL=https://<actual-fastapi-host>/api/v1` in Production.
   Configure Preview separately if it will be used; do not expose credentials there.
5. Deploy, record the public production URL, and set FastAPI Cloud `FRONTEND_URL`
   to that exact origin. Apply/redeploy affected services after env changes.
6. Verify the deployed commit and the tests below on the public Vercel URL.

The JWT cookie remains HttpOnly, Secure in production, and SameSite=Lax. Since
browser traffic goes to the same-origin Next.js proxy, do not change it to
SameSite=None or weaken authentication to make the two hosts work together.
Never leave production `API_URL` pointing to localhost.

## 5. Public acceptance gates

- [ ] Backend public `/health` returns 200 and `/docs` loads.
- [ ] Register a dedicated demo account and log in on Vercel.
- [ ] Create a trip, generate a real Bedrock itinerary, reload and reopen the saved trip.
- [ ] `/assistant` returns a grounded Bangladesh answer with matching sources.
- [ ] `/chat` remembers a first-turn fact in a second turn; reload, reopen and continue.
- [ ] Conversation title, loading/typing indicator, auto-scroll and timestamps work.
- [ ] Logout protects trips/chat; a second account cannot access another account's data.
- [ ] Invalid input or a controlled failure produces a useful response, without secrets.
- [ ] Public About, 404 and icon work. Error fallback and retry are tested in a safe environment.
- [ ] Test on an actual phone and ask a classmate to try the public app; record their real feedback.
- [ ] Review logs, secrets, diff, deployed commit and evidence before the Session 11 release.

After approval and successful release checks, use the course checkpoint message
`Deploy KelanaAI to production` and tag `session-11`. Verify remote commit/tag refs.
The video/Drive/LMS submission is a separate Session 12 gate.

## References

- [FastAPI Cloud application directory](https://fastapicloud.com/docs/builds-and-deployments/application-directory/)
- [FastAPI Cloud existing-project deployment](https://fastapicloud.com/docs/getting-started/existing-project/)
- [Neon and SQLAlchemy](https://neon.com/docs/guides/sqlalchemy)
- [Vercel monorepos](https://vercel.com/docs/monorepos)
- [Vercel environment variables](https://vercel.com/docs/environment-variables)
