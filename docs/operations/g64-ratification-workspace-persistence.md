# G64 Ratification Workspace — Persistence Contract

**Status:** Draft operational contract. This document does not authorize institutional ratification, access activation, or deployment.

## Runtime surfaces

- `GET /api/legal-operations/g64/ratification-workspace/contract` returns the canonical repository contract text, version, and SHA3-512 fingerprint.
- `POST /api/legal-operations/g64/ratification-workspace/records` records all ten explicit D01–D10 choices and an authenticated click-to-attest event. The caller must provide an `Idempotency-Key`.
- `GET /api/legal-operations/g64/ratification-workspace/records?institution_id=...` returns bounded, tenant-scoped evidence history.

Python EOS derives the tenant and authenticated principal from its existing authorization boundary. The submitted institution identifier is only an evidence label and is always marked `UNVERIFIED_PENDING_INDEPENDENT_VERIFICATION`. The ratifier's institutional authority is also unverified. These routes do not create IAM grants, release content, enforce an ethical wall, or declare ratification complete.

## Required server configuration for repository persistence

Configure these as deployment-owned secrets/configuration, never in source control:

- `G64_REPOSITORY_EXPORT_TOKEN`: dedicated GitHub token with only the repository contents permission needed to create immutable evidence files and a dedicated branch.
- `G64_REPOSITORY_EXPORT_REPOSITORY`: exact `owner/repository` destination.
- `G64_REPOSITORY_EXPORT_BASE_BRANCH`: existing trusted base branch from which the evidence branch may be created.
- `G64_REPOSITORY_EXPORT_BRANCH`: dedicated branch name beginning `g64-evidence/`; it must not equal the base branch.

The publisher writes only to `encryption-evidence/g64-ratification-workspaces/{record_id}.json` on the dedicated evidence branch. It never writes to the base branch, merges, deploys, or treats a Git commit as a signature. Existing artifacts are accepted only when their bytes exactly match the deterministic manifest; divergent reuse of the same record ID fails closed.

If repository configuration or the GitHub API is unavailable, the application record remains durably saved and the API returns `202 Accepted` with repository persistence marked pending. Retrying the exact request with the same idempotency key retries repository publication; changing the payload under the same key returns a conflict.

## Required authorization

The permission namespace now contains separate `legal_operations:g64_ratification_workspace:read` and `legal_operations:g64_ratification_workspace:write` vocabulary. Vocabulary does not grant permission. Canonical IAM role assignment and operation authorization remain required; no static role grant is added here.

## Still not a ratification workflow

Independent verification and second-approval evidence models exist, but they are not yet connected to authenticated API commands and durable persistence. Until those workflows, their independent identity checks, repository publication configuration, adversarial tests, and certification are complete:

- all D01–D10 remain user-selected evidence only;
- click-to-attest is not a cryptographic signature;
- institutional binding and ratifier authority remain unverified;
- no operational access or ethical-wall enforcement may be inferred;
- no merge or deployment is authorized by this draft.
