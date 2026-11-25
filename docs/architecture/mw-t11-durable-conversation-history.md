# MW-T11 — Governed Intelligence Dock Conversation Continuity

**VERSION:** v1.0.0-MW-T11-DURABLE-HISTORY-ARCHITECTURE  
**Authority:** WILSY OS Core Governance  
**Date:** 25 November 2026  
**PR:** #419 · Draft  
**Project:** Existing Foundation project; existing MW-T11 remains IN_PROGRESS

## Discovery → map → wire

The current system has ONE Python EOS backend, ONE React Intelligence Dock, and
one existing in-memory conversation engine. No paid AI provider or Node BFF is
required to browse or persist conversation history.

| Capability | Canonical authority | Existing adapter / consumers | Scope |
| --- | --- | --- | --- |
| Global Principal current session | Python EOS global authentication + RequireTenantAuthorization | canonical Axios `api.js` | live principal, selected tenant, capacity |
| Project/task/deadline/dependency truth | Python EOS Projects registry | `/wilsy-ai/reasoning/context` and Projects reads | exact authorized project/task + revisions |
| Task activity/comments | source-owned Python EOS Projects `/tasks/{task_id}/events` and `/comments` | Projects task editor | independent permission; not inferred from chat |
| Conversation transient state | React `wilsyAIConversationHistoryEngine.js` | existing `WilsyOSIntelligenceDock.jsx` | session only when EOS storage denied/unavailable |
| Conversation durable historical records | **Python EOS** `wilsy_ai_reasoning_router.py`, encrypted Mongo | same existing history engine | exact principal + tenant; not work-source authority |
| Model inference and billing | existing Python EOS reasoning / Kennel commercial admission | existing `/wilsy-ai/reasoning` | separately admitted and disabled when provider unavailable |

**Single workflow:** The Dock opens with the current authorized project/task
locator. EOS performs a fresh contextual source read; the client may record
conversation turns, but the saved text never becomes a substitute for current
EOS source verification or a new IAM grant. Navigating Projects → Headquarters
retains same-capacity conversation state. Refresh restores only records EOS
independently admits. Changing account, tenant or business capacity clears
in-memory turns; a later authenticated history GET is scoped to the new session.

## Durable archive API

All endpoints are part of the existing Python EOS `/wilsy-ai` router. They use
the existing `RequireTenantAuthorization` reasoning authority. Nothing
creates a new role, subscription entitlement or paid model command.

| Method | Route | Guarantee |
| --- | --- | --- |
| GET | `/wilsy-ai/history` | no-store; at most 30 owner threads; 30-day expiry; encrypted records decrypted only in EOS |
| PUT | `/wilsy-ai/history/{thread_id}` | strict schema, 80 turns / 64KiB bounded payload, expected revision CAS, no duplicate replay, authenticated owner only |
| DELETE | `/wilsy-ai/history/{thread_id}?expected_revision=N` | explicit owner command, CAS, metadata-only deletion audit, no unverified success |

Thread key: SHA3-256 of (tenant, principal, opaque thread UUID), **not**
a browser-chosen owner selector. Every Mongo find/update/delete includes exact
current tenant and principal. The archive stores AES-256-GCM ciphertext with a
unique nonce, additional authenticated data bound to owner, thread ID and
revision. Titles and conversation bodies remain inside ciphertext. The
metadata-only audit captures actor/scope, operation, revision, time and digest,
never prompt/response content. Audit metadata expires after 365 days; archive
records have 30-day TTL indexes. Physical backup retention is separately
governed by the deployment backup policy, not guaranteed by Mongo TTL alone.

**Data classification:** Historical conversation transcripts are user-visible
past text, not current EOS authorization or a verified task record. Restored
assistant turns are reclassified as
`HISTORICAL_NOT_LIVE_EVIDENCE`. The Dock labels saved turns accordingly.
An AI-provider execution cannot be inferred from an archived assistant role.

## Key admission and local development (no paid cloud)

Python EOS requires `WILSY_AI_HISTORY_KEY_B64` to contain a 32-byte AES key
encoded as standard base64. Missing or malformed keys fail closed with
`WILSY_AI_HISTORY_KEY_UNAVAILABLE`; the React Dock retains session-only work
and explicitly labels it as unsaved.

A source-only, nonproduction helper is provided:

```bash
cd ~/legal-doc-system
source .venv/bin/activate
source scripts/eos/wilsy_ai_history_local_key.sh
```

Then start/restart Python EOS from **that shell** using the existing approved
Global Principal MFA launcher. Do not echo the key into the chat, Git history,
CI logs or source files. The helper creates (once) a user-private local key
outside the repository, and reuses it on later restarts. Its key is **not**
production KMS; production needs reviewed secret distribution and key rotation.
Do not delete or rotate the local key with live archived development history
unless deliberate unreadability is acceptable.

## Authentication, abuse limits and failure semantics

- Server authenticates every request and verifies current selected tenant,
  principal, role and permission before touching Mongo.
- Client thread IDs are not ACLs. Cross-tenant reads produce an empty owned
  list and foreign revision writes/deletes fail as conflicts without exposing
  the foreign record.
- Unknown write outcome never silently replays transcript writes. Client
  retains a visibly session-only copy until authorized reconciliation.
- A changed tenant/capacity revokes in-flight client writes with a generation
  guard; the refreshed authenticated session must independently GET its own
  history before use.
- No browser localStorage, Node BFF, paid inference or embedding provider
  is a transcript storage authority.
- Delete removes the current encrypted record and appends immutable-style
  metadata-only audit; backup purge/recovery remains a separate operational
  policy.
- Large messages, too many threads, expired records, stale revisions,
  damaged ciphertext, unknown keys and unavailable dependencies fail closed.
- A deleted/expired history record cannot re-grant project access or reopen
  a live task command.

## Verification gates

**Automated** (source committed, execution evidence required):

```bash
python -m pytest -q tests/unit/test_wilsy_ai_encrypted_conversation_history.py
cd client
npx vitest run tests/client/wilsyAIConversationHistoryEngine.test.js
npx vitest run tests/components/intelligence/WilsyOSIntelligenceDock.test.jsx
npm run build
```

**Founder authenticated browser test (development only):**

1. Sync PR #419; source local key; restart the current Python EOS from the
   same shell; retain Vite at localhost:5173. Verify sign-in.
2. Open existing Foundation → MW-T11 → Intelligence Dock; inspect MW-T11.
   Confirm live `IN_PROGRESS`, source revision, canonical due date when
   supplied, and no paid-model POST.
3. Open Conversations. A saved thread must say `Saved in EOS`, not
   `Session only`. Confirm `GET /api/wilsy-ai/history` and
   `PUT /api/wilsy-ai/history/session-...` return 200 with no-store.
   Confirm no prompt bodies in request logs or audit events.
4. Refresh Chrome; same authenticated session must recover the thread from
   EOS. Open it. The label must clearly indicate saved historical text,
   not a fresh source verification. Current task verification must still
   independently use `/wilsy-ai/reasoning/context`.
5. Navigate Projects ↔ Headquarters. Confirm history and selection do not
   disappear. Use a new thread without overwriting the original.
6. Delete one saved thread using the explicit confirmation; independently
   refresh to confirm removal. A mismatched revision must not claim deletion.
7. Repeat under a separately authorized different principal/tenant/capacity:
   no other user's history may be returned. Test missing key and EOS outage:
   the Dock must work session-only, correctly labeled, without reusing saved
   authority or calling a paid model.

**Evidence boundaries:** This document records source implementation and
acceptance requirements, not a claimed live Mac/browser certification. CI
queued, local integrated tests and browser verification must be completed
before marking MW-T11 complete. MW-T12 rollback remains NOT_CERTIFIED;
PR #419 stays Draft; production remains Blocked.

---
ARTIFACT: mw-t11-durable-conversation-history.md  
VERSION: v1.0.0-MW-T11-DURABLE-HISTORY-ARCHITECTURE  
AUTHORITY BOUNDARY: one governed Python EOS history archive, source-owned tasks  
TENANT POSTURE: strict current tenant/principal; no browser grant  
FAIL-CLOSED POSTURE: never infer durable success, live evidence or paid execution  
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively  
END OF WILSY OS SOVEREIGN ARTIFACT
