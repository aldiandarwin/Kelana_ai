# Session 10 Evidence - Teaching KelanaAI to Remember Conversations

## So What?

KelanaAI now stores private conversation history and reconstructs it before each
Amazon Bedrock call. A context-dependent second question was verified live: the
database preserved `user -> assistant -> user -> assistant`, and Bedrock answered
`Kyoto` using information supplied only in the first turn.

## Acceptance Matrix

| Requirement | Status | Observable proof |
|---|---|---|
| Chat interface | Verified | Next.js `/chat` production build succeeds |
| Conversation database | Verified | PostgreSQL migration created `conversations` and `messages` |
| Save user and AI messages | Verified | Integration test reloads four persisted turns in role order |
| Context-aware AI | Verified live | `smoke_session_10.py` second turn answered `Kyoto` from first-turn context |
| Conversation sidebar | Verified | Current user's chats load newest-first and can be selected |
| New chat appears automatically | Verified | Create flow refreshes the sidebar and selects the new record |
| Reload previous messages | Verified | `GET /api/v1/conversations/{id}/messages` plus integration test |
| Rename conversation bonus | Verified | Authenticated `PATCH` endpoint and inline UI |
| Conversation title | Verified | Selected conversation title is rendered in the chat header |
| Auto-scroll on initial load | Verified | Reloading a conversation loads its messages and scrolls the bottom anchor into view |
| Auto-scroll after sending | Verified | Pending and persisted message changes trigger the same bottom-anchor scroll |
| Typing indicator | Verified | Animated dots and `KelanaAI is typing` remain visible during the Bedrock request |
| Timestamp for each message | Verified | Every user and assistant bubble renders its persisted `created_at` value |
| Private ownership | Verified | Anonymous operations return `401`; cross-user operations return `403` |
| Commit and tag | Pending approval | Target message `Add conversational memory and improve chat experience`, tag `session-10` |

## Data Model and Turn Flow

```text
users 1 --- many conversations 1 --- many messages

POST message
  -> verify conversation owner
  -> add user message and flush
  -> load all messages in chronological order
  -> send structured history to Amazon Bedrock
  -> add assistant message
  -> commit both messages atomically
```

`Conversation.title` belongs to the conversation record. The slide diagram
visually places `title` close to the message fields, but the conversation-list
and homework screens use it as thread metadata, so the implementation resolves
that ambiguity at the conversation level.

## API Contract

| Method | Path | Response or behavior |
|---|---|---|
| `POST` | `/api/v1/conversations` | `201 {"conversation_id": <id>}` |
| `GET` | `/api/v1/conversations` | Only the authenticated user's summaries |
| `GET` | `/api/v1/conversations/{id}/messages` | Title plus ordered persisted messages |
| `POST` | `/api/v1/conversations/{id}/messages` | Persisted user and assistant messages |
| `PATCH` | `/api/v1/conversations/{id}` | Normalized renamed summary |

Missing conversations return `404`; an existing conversation owned by another
user returns `403`. Blank and over-4,000-character messages return `422` before
Bedrock is called.

## Persistence and Failure Safety

- `messages.role` is constrained to `user` or `assistant`.
- Foreign keys cascade from users to conversations and conversations to messages.
- Message ordering uses timestamp followed by primary key for stable ties.
- The first user message creates a deterministic title without an extra AI call.
- A Bedrock exception returns `502` and rolls back both the user message and title.
- The migration is idempotent and does not modify prior-session records.

## Live Bedrock Proof

The live smoke test used an in-memory database and non-sensitive sample data. It
did not create a persistent demo account or write into the configured PostgreSQL
database.

```text
Session 10 live smoke: PASS
Stored role order: user -> assistant -> user -> assistant
Context-dependent answer: Kyoto
```

The first turn assigned Tokyo to Day 1 and Kyoto to Day 2. The second turn asked
which city had been assigned to Day 2 without restating it. The answer therefore
depends on the history sent with the second request.

## Automated Verification

```text
.\.venv\Scripts\python.exe -m unittest discover -s tests
43 tests passed

npm run lint
passed

.\node_modules\.bin\tsc.cmd --noEmit
passed

npm run build
passed - Next.js 16.3.2; /chat and /api/conversations generated

..\.venv\Scripts\python.exe migrate_session_10.py
passed - conversations and messages are ready
```

Seven new backend tests cover authentication, current-user list isolation,
two-turn history reconstruction, ordered reload, timestamps, rename, `404`/`403`,
input validation, and atomic rollback. Bedrock is mocked in the automated suite;
the separate smoke script is the explicit real-network proof.

## Browser QA

- Registered and signed in through the real Next.js authentication flow.
- Opened `/chat` as a protected route and confirmed the privacy disclosure.
- Observed the disabled input, pending user bubble, and typing indicator during
  the live Bedrock request.
- Confirmed the first message automatically replaced `New conversation` with a
  readable title in both the header and sidebar.
- Asked a context-dependent second question and received `Kyoto`.
- Reloaded the browser and confirmed all four messages, roles, and timestamps
  returned from PostgreSQL.
- Renamed the thread to `Japan two-day memory test` and confirmed both UI
  surfaces updated.
- Created another conversation and confirmed it appeared and became selected
  without a page refresh.
- At a 762 px narrow viewport, the layout stacked cleanly and reported no
  horizontal overflow (`scrollWidth <= innerWidth`). Browser logs were empty.

The QA flow added one local test account and two conversation records to the
configured development database. They are not source files and are not included
in Git.

## Privacy and Limits

- Conversation text is private account data stored in the local KelanaAI database.
- The selected conversation history is sent to Amazon Bedrock in
  `ap-southeast-2` to generate each response.
- Passwords, password hashes, JWTs, AWS tokens, and credentials are not placed in
  prompts or returned by the conversation API.
- The frontend disclosure under the message box states that messages are saved
  and sent to Bedrock.
- Full history follows the lesson and is appropriate for short homework threads.
  Token-aware trimming or summarization remains a future production improvement.
- Session 10 conversation memory and Session 9 RAG remain separate flows. This
  avoids claiming a combined memory-plus-RAG system that was not required or tested.

## Release Plan

- Commit message: `Add conversational memory and improve chat experience`
- Tag: `session-10`
- Push target: `origin/main` and `origin/session-10`
- Commit, push, and tag remain pending Aldian's approval of the final staged diff.
