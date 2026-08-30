# Session 08 Evidence - Teaching KelanaAI to Know Its Users

## So What?

KelanaAI now treats a trip as private user data. A valid login identifies the
caller, and FastAPI - not the frontend - decides which `user_id` owns every trip.

## Official Acceptance Matrix

| Requirement | Implementation | Observable proof |
|---|---|---|
| View only own trips | `GET /api/v1/trips` filters `Trip.user_id == current_user.id` | Alice test account sees one trip; Bob sees zero |
| Reject cross-user update | Shared ownership guard protects `PUT /api/v1/trips/{id}` | Bob updating Alice's trip returns `403` |
| Reject cross-user delete | Shared ownership guard protects `DELETE /api/v1/trips/{id}` | Bob deleting Alice's trip returns `403` |
| Register + login UI | Responsive `/register` and `/login` pages call Next.js auth Route Handlers | Pages rendered and login reached `/trips` |
| Protected pages | Next.js 16 `proxy.ts` checks the HttpOnly auth cookie | Anonymous `/` returns `307` to `/login?next=%2F` |
| Private trip list UI | Trip service uses authenticated `/api/trips` forwarding | Dashboard rendered only Yogyakarta for the QA owner |
| Profile | `/api/v1/auth/me` returns JWT user plus owned trip count | Profile showed name, email, member date, and one trip |
| Logout | Route Handler expires the HttpOnly cookie | `POST /api/auth/logout` returned `200` with `Max-Age=0` |

## Security Decisions

- Passwords are hashed with bcrypt and `password_hash` is never serialized.
- JWT uses `sub=user_id`, an expiry, and a secret supplied only through `.env`.
- The browser receives JWT only as an `HttpOnly`, `SameSite=Lax` cookie.
- Next.js Route Handlers attach the Bearer token to FastAPI requests server-side.
- Create-trip payloads do not accept ownership; the backend assigns `user_id`.
- Detail and AI generation are protected in addition to the homework's CRUD checks.
- `401` means no valid identity; an existing trip with a different owner returns `403`.

## Database Migration Evidence

The idempotent `backend/migrate_session_8.py` migration was run against the local
PostgreSQL database:

```text
Session 8 migration complete. Preserved 9 pre-auth trip(s).
tables=trips,users
trip_columns=...,user_id:False
foreign_keys=fk_trips_user_id_users
trips=9
trips_without_owner=0
```

No pre-auth trip was deleted. Existing trips belong to a disabled internal
`Legacy Import` account and therefore cannot leak into a newly registered user's
history.

## Automated Verification

```text
python -m unittest discover -s tests -v  -> 10 tests passed
npm run lint                             -> passed
npx tsc --noEmit --incremental false     -> passed
npm run build                            -> passed (Next.js 16.3.2)
git diff --check                         -> passed
```

The backend integration suite uses two users and an in-memory database. It tests
registration, login, profile, missing-token `401`, list isolation, backend-set
ownership, duplicate email, invalid password, and cross-user `403` for detail,
update, delete, and generation.

## Live API Proof

```json
{
  "bob_register": 201,
  "bob_visible_trips": 0,
  "cross_user_put": 403,
  "cross_user_delete": 403,
  "anonymous_list": 401
}
```

## Browser QA

- Desktop login, private trip dashboard, detail, ownership rejection, and profile rendered correctly.
- Mobile viewport `390x844` showed stacked controls and no horizontal overflow.
- The protected homepage kept all four planner fields visible on mobile.
- Browser console produced no warnings or errors.
- A local QA account and one Yogyakarta trip were added for visual verification;
  this PostgreSQL data is not committed to Git.

## Release Plan

- Target commit message: `Protect CRUD endpoints to respect user ownership`
- Target tag: `session-8`
- Final local and remote refs are verified after publication and reported separately.
