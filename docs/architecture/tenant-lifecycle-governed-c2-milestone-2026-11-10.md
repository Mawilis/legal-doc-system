# WILSY OS — Governed Cross-Tenant Lifecycle C2 Milestone

TITLE: Governed Cross-Tenant Lifecycle C2 Milestone
VERSION: v1.0.1-GOVERNED-C2-AUTHORITY-BOUNDARY-METADATA
AUTHORITY: Wilsy OS Core Governance
EPITOME: Records the Python EOS authority gap and the separate governed milestone required before any global tenant listing, tenant creation, or tenant suspension can be enabled.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/docs/architecture/tenant-lifecycle-governed-c2-milestone-2026-11-10.md
COLLABORATION / OWNERSHIP: Python EOS IAM and Tenant Registry owners; client surfaces consume only the resulting authenticated capability.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: v1.0.1-GOVERNED-C2-AUTHORITY-BOUNDARY-METADATA completes the sovereign artifact header and terminal seal without changing C2 authority or availability.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Repository governance record only; no tenant records, credentials, or production state are accessed.
TENANT BOUNDARY: No global tenant operation is authorized by this record.
AUTHORITY BOUNDARY: Founder, SUPER_ADMIN, presentation roles, `X-Tenant-ID`, and retired Node permissions are insufficient.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution and settlement.
STATUS: RECORDED / NOT ACTIVATED
DATE: 2026-11-10

## Current state

Python EOS remains deny-by-default for cross-tenant lifecycle operations. The tenant router denies global collection listing and tenant creation before registry persistence. Its supported profile operations require the exact authenticated tenant scope. The existing `tenant:lifecycle:archive` capability is not suspension authority.

The current permission and authorization surfaces do not define an explicit principal capability for global tenant-directory reads, tenant creation, or tenant suspension. No capability is inferred from `audit:read`, `SUPER_ADMIN`, Founder identity, UI roles, or a global tenant header.

The client therefore keeps the current authenticated tenant projection and tenant-scoped operations available where their Python EOS capabilities already authorize them. Global listing, create, and suspend controls remain unavailable. The billing client directory and synthetic or browser-recent tenant fallbacks are not authorities.

## Connection map

| Dimension | Current relationship |
|---|---|
| Python routes | `tools/eos/api/tenant_router.py`: collection `GET` and create `POST` fail closed; exact-tenant profile read/update and separately authorized archive are distinct operations. |
| Principal capability | `tools/eos/auth/permission_namespace.py` and `tools/eos/auth/tenant_authorization.py`: no global directory-read, tenant-create, or tenant-suspend capability is currently established. |
| Persistence | `TenantRegistry` is not reached for denied collection listing or creation; this record introduces no schema, collection, index, or migration. |
| Client scope | `client/src/contexts/tenantContext.jsx` retains only the Python EOS authenticated workspace projection; refresh and alias resolution do not fetch arbitrary tenants. |
| Tenant surfaces | TMS, BillingHUD, Founder Dashboard, the legacy SuperAdmin tenant page, TenantSwitcher, and TenantManagementGrid show current scope or C2 availability; none issues a global lifecycle request. |
| Billing | Own-tenant subscription operations use the authenticated workspace scope and existing `subscription:read` / `subscription:manage` contracts. Platform invoice recipient lookup remains unavailable without governed cross-tenant directory authority. |
| Evidence and telemetry | Existing Python EOS authorization and persisted audit contracts remain authoritative. This milestone adds no browser-generated approval, mutation evidence, metric, or audit fact. |
| Configuration and transport | No root fallback, global sentinel, unauthenticated directory request, or new runtime is introduced. Python EOS remains the sole backend runtime. |

## Separate activation gates

Activation requires a future, separately reviewed Python EOS change that satisfies every gate below:

1. Define distinct, least-privilege capabilities for global directory read, tenant creation, and tenant suspension in the canonical Python EOS permission namespace. Do not conflate them with profile update, archive, audit read, or subscription management.
2. Bind each capability to a governed principal authorization rule and an explicit target scope. Prove that UI role labels, Founder identity, and caller-supplied tenant headers cannot create the decision.
3. Specify tenant creation and suspension lifecycle invariants, idempotency, transaction ownership, durable audit evidence, error codes, and recovery behavior before implementation.
4. Implement Python EOS routes and registry operations. Denial must occur before persistence. Cross-tenant absence and conflict responses must not disclose another tenant's existence.
5. Add unit and integration coverage for unauthorized principals, authorized principals, cross-tenant isolation, replay, concurrent lifecycle changes, audit persistence, and failure rollback.
6. Wire client controls only after the EOS contract and capability are proven. Remove every seed, browser-recent, manually selected global target, and legacy endpoint fallback.
7. Run exact-head Python, client, CI, authenticated browser, and real-database gates applicable to the resulting governed change. Local UI or mock tests do not activate C2.

Until those gates are approved and certified, the runtime contract is **C2 NOT AVAILABLE**. This milestone is a recorded boundary, not permission to implement or activate the capability.

## Affected work and disposition

| Surface | Disposition | Reason |
|---|---|---|
| `tools/eos/api/tenant_router.py` | Existing deny-by-default behavior retained | Global list and create lack a governed capability. |
| `tools/eos/auth/permission_namespace.py` | No new permissions added | Capability creation is part of the separate milestone. |
| `client/src/contexts/tenantContext.jsx` | Authenticated current tenant only | Browser directory reads cannot supply cross-tenant authority. |
| `client/src/components/sovereign/Sovereign_TenantManager.jsx` | Current tenant projection and explicit availability | Preserves truthful tenant-scoped visibility. |
| `client/src/components/billing/BillingHUD.jsx` | Own-tenant subscription/client-invoice paths remain scoped; global recipient selection is disabled | No authorized global tenant directory exists. |
| `client/src/services/api/tenantApi.js` | Global list/create/suspend methods reject before transport | Retired Node behavior is not a Python capability. |
| `server/manifest.txt`, migration history, audit evidence, trust artifacts | Retained | Historical and governed evidence is not live tenant authority and remains preserved. |

## Changelog

- **v1.0.1-GOVERNED-C2-AUTHORITY-BOUNDARY-METADATA (2026-11-10):** Completes the sovereign artifact envelope without changing lifecycle authority.
- **v1.0.0-GOVERNED-C2-AUTHORITY-BOUNDARY (2026-11-10):** Records C2 as a separate unactivated governance milestone with explicit capability and certification gates.

## Operational seal

ARTIFACT: docs/architecture/tenant-lifecycle-governed-c2-milestone-2026-11-10.md
VERSION: v1.0.1-GOVERNED-C2-AUTHORITY-BOUNDARY-METADATA
AUTHORITY BOUNDARY: No cross-tenant operation is authorized.
TENANT POSTURE: Current authenticated tenant only until C2 is separately governed.
FAIL-CLOSED POSTURE: Global tenant listing, creation, and suspension remain unavailable.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
END OF WILSY OS SOVEREIGN ARTIFACT
