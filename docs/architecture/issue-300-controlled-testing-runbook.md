# Issue #300 — Controlled ownership-lifecycle testing runbook

**Release class:** Controlled engineering QA only  
**Production ownership activation:** DENY — independent governance decisions remain unresolved  
**Tenant genesis / transfer / recovery writes:** Not enabled for production  
**Data:** Synthetic tenant, entity, principal and decision references only

## Purpose

This runbook certifies the deny-only ownership lifecycle foundation and its transaction boundaries. It does not appoint an issuer, establish a trust root, approve legal evidence, authorize a recovery adjudicator, or issue positive production ownership evidence.

## Two-phase execution rule

All external verification must complete before opening the MongoDB transaction:

1. Verify owner proposal with `prepare_proposal`; persist only its opaque prepared receipt with `propose` inside the caller transaction.
2. Verify successor acceptance with `prepare_acceptance`; persist only its opaque prepared receipt with `accept` inside the caller transaction.
3. Run ownership evidence preflight with `prepare_finalization`; re-read proposal and acceptance, re-check scope/currentness/current-owner IAM and commit through `finalize` inside the caller transaction.
4. The lifecycle command exposes the same boundary: `prepare(request)` performs independent verification outside Mongo; `execute(..., evidence=...)` performs mutable-authority revalidation and the append inside the caller-owned transaction.

Prepared proposal and acceptance receipts are opaque, verifier-issued values. Passing the public proof dataclasses directly to persistence methods is rejected. No transaction is started, committed, or aborted by these domain services.

## Trust-root emergency revocation

- Revocation requires a separately injected independent governance verifier. Missing verifier means `TRUST_ROOT_REVOCATION_AUTHORITY_UNAVAILABLE`.
- `prepare_revocation` verifies the institutional revocation before a Mongo transaction is opened.
- `revoke` appends the verified revocation event in the caller-owned transaction; it never edits or deletes the enrolled root.
- Revocation is bound to exact root reference, public-key fingerprint, key ID, key revision and issuer/recovery purpose scope.
- Key rotation appends a strictly higher key revision under the same trust-root reference and issuer/purpose scope; the public-key fingerprint and key ID may change. Currentness selects the newest valid revision, while prior revisions remain available for historical verification.
- A revocation cannot be backdated, replayed, self-approved by the issuer, or applied to another key revision.
- Currentness checks fail closed on malformed revocation records. Historical checks before a future effective instant remain historically valid; current checks at/after the effective instant deny.

## Local/CI certification

Use only a disposable MongoDB replica set created by the repository certification workflow. The workflow requires `WILSY_ISSUE_300_REAL_MONGO_URI`, accepts loopback hosts with an explicit port, verifies replica-set name `wilsyVendorCertRS`, creates a unique synthetic database per test, and drops it during teardown.

Focused commands (run from repository root):

```bash
python -m compileall -q tools/eos/auth tests/unit tests/integration
pyright tools/eos/auth/tenant_ownership_verifier.py tools/eos/auth/tenant_ownership_evidence_registry.py tools/eos/auth/tenant_ownership_lifecycle_command.py tools/eos/auth/tenant_ownership_trust_root_registry.py tools/eos/auth/tenant_ownership_transfer_protocol.py tools/eos/api/tenant_router.py
pytest -q tests/unit/test_tenant_ownership_verifier.py tests/unit/test_tenant_ownership_evidence_registry.py tests/unit/test_tenant_ownership_lifecycle_command.py tests/unit/test_tenant_ownership_trust_root_registry.py tests/unit/test_tenant_ownership_transfer_protocol.py tests/unit/test_tenant_ownership_provider_composition.py tests/unit/test_tenant_ownership_evidence_validation.py tests/unit/test_tenant_ownership_provider_ports.py
pytest -q tests/integration/test_tenant_ownership_evidence_registry_real_mongo.py tests/integration/test_tenant_ownership_governance_transfer_real_mongo.py tests/integration/test_tenant_ownership_provider_composition_real_mongo.py tests/integration/test_tenant_ownership_recovery_replay_real_mongo.py tests/integration/test_tenant_router_get_archive_real_mongo.py
```

The GitHub Actions Issue #300 certification workflow is the authoritative CI path and must pass on the exact proposed commit. Do not point these tests at a shared, staging, or production database.

## Required negative assertions

- Missing issuer/recovery authority always denies with `OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE`.
- Missing trust-root revocation verifier denies; no fallback key or environment toggle is permitted.
- A forged public transfer proof cannot be persisted without its opaque prepared receipt.
- Proposal, acceptance and finalization provider checks occur outside Mongo transactions.
- Transactional persistence rechecks exact tenant/entity/principal/proposal scope, expiry, current owner, current IAM and expected revision.
- Abort leaves no partial proposal, acceptance, ownership event or revocation event.
- Duplicate decisions, proposals, acceptances, commands and revocations are replay/conflict denied.
- No test fixture or fake verifier is configured in a production composition.

## Controlled testing release gate

A merge of the engineering changes enables CI certification on `main`; it does not enable positive ownership operations. QA may test the surrounding application, tenant profile and deny-only ownership responses using synthetic data. An authenticated own-tenant client can read `GET /api/tenants/{tenant_id}/ownership/readiness`; it performs no Mongo access or writes and returns `status=DENY`, `reason=OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE`, and `positive_operations_enabled=false`. The endpoint enforces the same exact `X-Tenant-ID` to path binding as the tenant profile read route. Any test that requires a successful ownership genesis, transfer or recovery must use an isolated fake-authority test fixture and a disposable database, never production configuration.

Production activation remains blocked until all six independently attributable governance decisions in `issue-300-governance-approval-intake.md` are supplied and independently verified, followed by production-adapter, rotation, revocation, outage and rollback certification.
