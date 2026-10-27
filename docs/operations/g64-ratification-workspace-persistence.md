# G64 Ratification Workspace — Persistence and Review Contract

**Status:** Draft operational contract. This document describes evidence capture only. It does not authorize institutional ratification, access activation, ethical-wall enforcement, merge, or deployment.

## Authenticated Python EOS routes

All routes are relative to `/api/legal-operations/g64/ratification-workspace`. Python EOS derives tenant and principal identity through the existing tenant authorization boundary; caller-supplied institution identifiers remain unverified evidence labels.

- `GET /contract` — returns the canonical repository contract text, version, and SHA3-512 fingerprint.
- `POST /records` — persists a workspace record and authenticated click-to-attest evidence. Requires `Idempotency-Key`; all ten D01–D10 decisions must be explicitly completed. Exact replay is accepted only for the same principal and payload; changed payload under the same key conflicts.
- `GET /records?institution_id=...&limit=...` — returns bounded history in server-derived tenant scope.
- `POST /records/{record_id}/independent-verification` — appends an eight-check independent verification event. Requires its dedicated verification permission and an idempotency key. The verifier cannot be the ratifier.
- `POST /records/{record_id}/second-approval-policy` — records an evidence-backed decision on whether second approval is required. It cannot be the ratifier or the independent verifier, and its policy evidence must match the verifier's policy finding.
- `POST /records/{record_id}/second-approval` — records a second approval only when a passing independent verification and an evidence-backed policy requiring second approval exist. The approver must be distinct from the ratifier, verifier, and policy decider.
- `GET /records/{record_id}/review-events?institution_id=...&limit=...` — reads bounded review evidence.
- `POST /records/{record_id}/review-events/{event_id}/publish?institution_id=...` — authenticated, idempotent retry for repository persistence of an already-persisted review event. A missing event returns 404; mismatched record fingerprint fails closed.

Canonical permission vocabulary is separate for workspace read/write, independent verification, second-approval policy, and second approval. Defining vocabulary does not grant it: canonical IAM must separately authorize the actual principals. No static role grant is created by this feature.

## Application persistence

Workspace and review evidence use separate append-only Mongo registries, tenant/institution/record/event scope, canonical fingerprints, tamper/conflict detection, idempotent replay, startup indexes, and majority+journal write concern. Writes occur in a caller-owned active transaction. Review events are immutable evidence; they do not mutate the workspace into an authorized or ratified state.

The submitted institution identifier is always marked `UNVERIFIED_PENDING_INDEPENDENT_VERIFICATION`. Ratifier authority is likewise unverified. A click-to-attest event is explicitly `AUTHENTICATED_CLICK_TO_ATTEST_NOT_CRYPTOGRAPHIC_SIGNATURE`.

## Repository evidence persistence

Configure these as deployment-owned secrets/configuration, never in source control:

- `G64_REPOSITORY_EXPORT_TOKEN` — a dedicated GitHub token limited to the destination repository and the minimum Contents read/write permissions needed to create a dedicated branch and immutable evidence files.
- `G64_REPOSITORY_EXPORT_REPOSITORY` — exact `owner/repository` destination.
- `G64_REPOSITORY_EXPORT_BASE_BRANCH` — an existing trusted base branch.
- `G64_REPOSITORY_EXPORT_BRANCH` — dedicated branch beginning `g64-evidence/`; it must differ from the base branch.

The publisher creates the dedicated export branch from the configured base when absent. It writes the workspace manifest to `encryption-evidence/g64-ratification-workspaces/{record_id}.json` and each review event to `encryption-evidence/g64-ratification-workspaces/{record_id}/{event_id}.json`. It never writes evidence to the base branch, merges, deploys, or treats a Git commit as a signature. An existing artifact is accepted only when its bytes exactly match the requested deterministic manifest; a divergent artifact at the same path fails closed.

The application record is durably persisted before repository publication. If configuration is missing or publication fails, the API reports application persistence as `PERSISTED`, repository persistence as pending, provides a content-free error code, and returns `202 Accepted` where applicable. Retrying `POST /records` with the same idempotency key and exact payload retries the workspace export. The dedicated review-event publish route retries review exports without creating a new review event. Repository configuration and a live export have **not** been proven by CI; they must be configured and exercised in the target environment before repository persistence can be claimed operational there.

## Required closure evidence

CI on the PR revision has passed repository integrity, security audit, G64 focused tests and isolated real-Mongo certification, R2A/R2B real-Mongo certification, and retained production gates. These results certify the tested code path; they do not prove target runtime secrets/configuration, actual IAM assignments, external institutional identity, source-document truth, or ratifier authority.

Before any institutional closure:
- verify authoritative institutional and source evidence independently;
- establish the actual institution binding and ratifier authority through attributable trusted sources;
- record the independent verification and evidence-backed second-approval policy;
- obtain and record a distinct second approval when the governing policy requires it;
- configure and exercise repository export in the intended runtime;
- obtain any required institutional/legal approvals outside this software evidence workflow.

D01–D10 remain undecided until the user explicitly chooses them. No evidence submission, repository commit, review finding, or second-approval event grants operational access or marks ratification complete.
