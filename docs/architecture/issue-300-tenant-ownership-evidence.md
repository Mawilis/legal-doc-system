# Issue #300: Tenant ownership evidence boundary

**Status:** blocked pending an independent legal-entity ownership authority
**Reviewed:** 2026-11-02
**Repository baseline:** `8a995b5b235149953a95a831ac42fe031acad926`

## What exists now

- `PrincipalAuthorityRepository` is canonical for global principal status and identity. A `SovereignIdentity` is an authenticated projection; its email, tenant id, roles, permissions, or `verified` tenant metadata do not prove legal-entity ownership.
- `verify_pretenant_bootstrap_authority` admits only deployment-allowlisted principals to request tenant genesis. This proves deployment provisioning authority only.
- `bootstrap_tenant_owner` previously created tenant truth, active membership, `ENTERPRISE_ADMIN`, and the `tenant_owner` business role in one transaction. It did not require independent legal-entity evidence.
- `TenantMembershipRepository` owns the `(principal_id, tenant_id)` membership state. `RoleAssignmentRepository` owns authentication roles. `TenantBusinessRoleRepository` owns business-role state. These records are distinct and none proves corporate ownership.
- `tenant_business_role_delegation_policy.py` has a pure last-owner / ownership-transition policy, but there is no production ownership-transfer command that consumes verified ownership evidence.
- The tenant HTTP POST route is already unavailable pending system authority. `TenantRegistry` itself owns persistence only. The older `WilsySaaSPlatform.provision_enterprise_customer` facade calls a `TenantRegistry.create_tenant` symbol that is absent from the current registry implementation and is not an active canonical genesis path.
- Workforce departure revokes membership, active role assignments, and sessions within its transaction. It does not create or transfer tenant ownership evidence. Ordinary invitation admission creates membership and an authorization role only.

## Safe state implemented

`bootstrap_tenant_owner` still checks deployment-rooted pretenant authority, then denies with `OWNERSHIP_EVIDENCE_AUTHORITY_UNAVAILABLE` before principal lookup, transaction creation, or any tenant-local write. This prevents provisioning permission or caller-supplied claims from being promoted into legal ownership. The existing result type and denial vocabulary remain import-compatible; no successful owner bootstrap is possible in this state.

This is a containment change, not completion of the ownership lifecycle. Tenant creation through the HTTP route remains disabled, and no transfer, recovery, or owner replacement command is exposed.

## Exact external dependency

No configured independent issuer / verifier was found that can establish the legal entity's current authority to bind a natural-person principal to the exact Wilsy tenant. Before owner genesis, transfer, or recovery can be enabled, governance must identify and configure:

1. An authoritative legal-entity ownership or signatory evidence issuer and its trust root, verification keys, issuer scope, validity, and revocation/currentness rules.
2. A canonical evidence contract binding issuer, legal-entity identifier, exact tenant identifier, exact principal identifier, authority type, effective interval, source reference, and cryptographic fingerprint.
3. A verification service that validates issuer provenance, authenticity, currentness, exact scope, and conflicts without treating uploaded documents or self-attestation as verified facts.
4. A separate recovery authority for lost, deceased, disputed, or inaccessible owners, including its evidence source and conflict/adjudication rules.

The repository currently has no selected issuer, trust-root material, accepted legal-entity evidence schema, or independent recovery authority for this purpose. Do not substitute the deployment provisioner allowlist, email-domain matching, JWT claims, an existing owner, or a caller-uploaded document.

## Target architecture and migration boundary

After governance configures the external authority, map and implement the complete lifecycle together:

- Verified immutable legal-entity ownership evidence domain and issuer verifier.
- Tenant-scoped append-only evidence registry and currentness/conflict projection.
- Genesis orchestration that verifies evidence and atomically creates tenant, membership, authorization role, business role, and an ownership event in a caller-owned transaction.
- Transfer orchestration that verifies incoming and outgoing authority, preserves last-owner and conflict rules, and records immutable before/after evidence.
- Recovery orchestration that uses the separately governed recovery authority and cannot infer consent from a lost account or existing role.
- Route / caller integration, authorization, audit evidence, startup indexes, revocation handling, and tenant lifecycle tests.
- Tests for forgery, wrong issuer, wrong entity/principal/tenant, expired/revoked evidence, replay, conflict, concurrency, transfer, recovery, partial-state refusal, tenant isolation, and transaction retry.

Candidate source boundaries to re-evaluate during that implementation are `tools/eos/auth/tenant_owner_bootstrap.py`, `tools/eos/auth/tenant_membership_repository.py`, `tools/eos/auth/role_assignment_repository.py`, `tools/eos/auth/tenant_business_role_repository.py`, `tools/eos/auth/tenant_business_role_delegation_policy.py`, `tools/eos/api/tenant_router.py`, and the new evidence domain/registry/verifier/orchestration modules. This is a discovery list, not approval to modify every file; exact ownership and transaction wiring must be re-proven once the issuer contract exists.

## Verification boundary

The owner-bootstrap real-Mongo certificate requires `WILSY_ISSUE_300_REAL_MONGO_URI`, accepts loopback hosts only, and rejects port 27027. It uses unique synthetic ids and certifies zero tenant, membership, authentication-role, and business-role rows after the blocked command. This certificate does not prove an end-to-end ownership lifecycle or production readiness.
