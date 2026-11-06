# EOS Global Authentication and Commercial Workspace Context Contract

Date: 2026-11-03
Status: Integration contract; implementation and end-to-end certification outstanding.

## 1. Purpose

Define one EOS-owned journey from global identity to an authenticated, selected workspace, then attach a separately derived commercial-capability projection so the workspace can accurately describe the tenant's purchased plan, bundled modules, value-added services and AI entitlements.

This contract does not authorize a commercial entitlement, create a subscription, grant IAM permissions, or enable an AI provider. It composes current evidence owned by the existing authorities.

## 2. Authentication state machine

The public journey is a strict state machine. Each state has one narrowly scoped capability and cannot be skipped by browser-supplied identifiers.

1. `GLOBAL_CREDENTIALS_REQUIRED`: accept normalized email and password. Apply the existing failure-only email and direct-peer throttle before verification. Authenticate only against the tenant-neutral `PrincipalCredentialRepository` and exact ACTIVE `PrincipalAuthority`. Return one generic failure for unknown email, wrong password and inactive principal.
2. `MEMBERSHIP_SELECTION_REQUIRED`: after successful password verification, issue a short-lived, one-time, digest-persisted selection challenge. Return only the authenticated principal's bounded ACTIVE membership choices. Revalidate canonical ACTIVE tenants and list each ACTIVE business capacity separately. Do not return permissions or infer a default tenant/capacity.
3. `CAPACITY_SELECTION_REQUIRED`: require explicit canonical tenant ID and exact business-capacity identifier. Consume the selection challenge and re-read principal, credential revision, ACTIVE membership, canonical tenant and ACTIVE capacity inside one caller-owned transaction. Issue a second short-lived, one-time MFA challenge bound to the exact principal, tenant, membership revision, capacity, capacity revision and EOS workspace.
4. `MFA_REQUIRED`: verify the enrolled factor using the principal-scoped MFA authority. The challenge is not proof that MFA succeeded. Never accept a browser-provided MFA-enabled flag, secret, tenant role or revision as evidence.
5. `SESSION_ISSUANCE_PENDING`: after factor verification, consume the MFA challenge and revalidate every bound revision inside the same transaction used for durable session issuance. Bind the session and refresh authority to principal, credential revision, tenant, membership revision, business capacity, capacity revision and workspace. Commit factor-currentness evidence and session state atomically. Any mismatch aborts the whole transaction.
6. `WORKSPACE_READY`: issue only the normal access/refresh material required by the established session contract and return EOS workspace bootstrap. Every protected request independently checks current principal, credential, membership, capacity and resource IAM authority. Browser state is presentation, not authority.

A principal with no selectable ACTIVE membership cannot enter a tenant workspace. A membership with no ACTIVE capacity is not selectable. Multiple capacities always require an explicit choice. Expired, consumed, replayed, stale, suspended, revoked or unavailable authority fails closed.

## 3. Migration and compatibility

The legacy `AuthRegistry.users` credential path is tenant-bound. Do not switch only the password lookup while MFA, reset, refresh, session issuance or token verification still use that legacy row.

Before cutover, run the existing read-only migration assessor against a controlled snapshot. Migrate only unambiguous rows in an idempotent, caller-owned transaction. Quarantine duplicate email, conflicting hashes, missing principal, inactive tenant/membership/capacity and malformed MFA records. Never merge identities, create memberships, or infer professional authority. Revoke or expire legacy sessions under a separately certified cutover procedure.

No production credential migration is authorized by this contract.

## 4. Commercial context is post-authentication and read-only

After `WORKSPACE_READY`, EOS may attach a `commercialContext` projection to workspace bootstrap. It is a descriptive, current-state snapshot and never part of authentication or IAM admission.

The projection should identify, only when current authoritative evidence supports it:

- **Base plan / tariff:** canonical plan ID, display label, catalogue/version reference, subscription lifecycle state, effective term, renewal/expiry or perpetual status where the source exposes it, and the plan's canonical feature identifiers. Monetary amounts, currency, tax, billing cadence and discounts must come from the authoritative commercial records; never infer price from plan names or UI configuration.
- **Bundled product modules:** each closed-catalogue product descriptor (currently Legal Operations, Billing, CRM and HR) paired with its independently current tenant-product entitlement. A catalogue entry alone is not a purchase. A plan feature alone is not an activated product entitlement.
- **Value-added services:** each VAS must be separately identified and evaluated under its own authority. Tenant Branding and WILSY AI are not generic product-catalogue modules and must not be inferred from a base-plan label.
- **WILSY AI:** show the current AI VAS feature/tier and lifecycle state only when the exact tenant subscription, canonical AI feature, AI commercial policy and WILSY AI entitlement evidence all correlate. AI provider availability, model routing, budgets, usage limits and feature capability remain separate runtime authorities; a commercial badge must not bypass them.
- **Other VAS:** show only services for which a canonical catalogue and current tenant-scoped entitlement/lifecycle authority exist. Unknown VAS identifiers are omitted or surfaced as a bounded unavailable state, never treated as included.
- **Evidence freshness:** include a server-generated observation timestamp and the relevant source revisions/version identifiers. If a required source is unavailable or inconsistent, return a bounded unavailable commercial projection rather than silently reusing stale browser data.

## 5. Commercial authority boundaries

The projection composes existing authorities; it does not replace them:

- `PlanRegistry` owns canonical plan catalogue truth.
- `SubscriptionRegistry` owns tenant subscription lifecycle and verified subscription proof.
- `product_catalogue` owns closed product identity and display metadata only.
- `tenant_product_entitlement` authorities own each tenant's product entitlement lifecycle.
- WILSY AI feature catalogue, AI commercial policy, subscription-to-AI composition and AI entitlement registry own AI-specific commercial identity and entitlement.
- Tenant Branding retains its separate VAS catalogue, subscription and entitlement lifecycle.
- IAM and resource services independently decide who may perform each operation.
- Kennel EOS remains the exclusive financial execution and settlement authority.

The workspace projection must not create/activate/reconcile entitlements, mutate subscriptions, issue invoices, charge payment methods, change tariffs, provision AI providers, or grant permissions.

## 6. Suggested response shape

The transport contract may expose a bounded structure similar to the following; values must be populated from typed authority results, never copied from client claims:

```json
{
  "workspace": {
    "status": "READY",
    "workspaceId": "EOS_RESOLVED_WORKSPACE"
  },
  "commercialContext": {
    "status": "CURRENT",
    "observedAt": "server-generated UTC timestamp",
    "plan": {
      "planId": "canonical-plan-id",
      "label": "catalogue label",
      "subscriptionState": "ACTIVE",
      "term": "source-derived term"
    },
    "bundledModules": [
      {
        "productId": "LEGAL_OPERATIONS",
        "entitlementState": "ACTIVE"
      }
    ],
    "valueAddedServices": [
      {
        "serviceId": "WILSY_AI",
        "tier": "source-derived tier",
        "entitlementState": "ACTIVE"
      }
    ]
  }
}
```

The example is illustrative only. It is not evidence that any tenant owns any listed plan, module or VAS. Do not expose internal proof hashes, payment credentials, provider secrets, raw subscription documents or private commercial evidence.

## 7. Implementation sequence and certification gates

1. Wire global credential authentication and one-time membership-selection challenge into EOS HTTP routes, using existing rate limiting and generic failures.
2. Add a bounded membership-choice endpoint protected by the one-time selection capability; ensure it cannot be used as a reusable directory API.
3. Wire explicit tenant and business-capacity selection to the existing revision-bound MFA challenge.
4. Integrate the principal-scoped factor verifier and atomically issue a membership/capacity-bound session. Do not reuse legacy tenant-bound session claims without a reviewed compatibility contract.
5. Update token verification, refresh, recovery and workspace bootstrap to enforce the global credential and selected-authority revisions.
6. Add a read-only commercial-context composer over the canonical plan, subscription, product-entitlement, AI and Branding authorities. Keep commercial projection failures distinct from authentication failures: an unavailable commercial summary must not fabricate entitlements or broaden access.
7. Add HTTP and real-Mongo replica-set tests for transaction abort/replay, concurrent revocation, credential changes, membership/capacity changes, duplicate identities, MFA failures, session refresh, cross-tenant substitution and commercial-source divergence.
8. Certify browser journeys for one principal with multiple tenants and multiple capacities, plus plan/module/VAS variations. Confirm that changing commercial context never changes IAM authority.

## 8. Non-claims

This contract does not claim the global login path, membership/capacity HTTP endpoints, MFA integration, session migration, commercial-context composer, production data migration, or production rollout is complete. Existing unit and CI certifications remain evidence only for the components they actually execute.
