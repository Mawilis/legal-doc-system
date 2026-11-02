# Legal Firm Tenant Authority and Entitlement Policy

**Policy ID:** WILSY-LEGAL-FIRM-TENANT-AUTHORITY  
**Policy version:** 1.0.0 (engineering baseline)  
**Status:** DESIGN / NON-AUTHORIZING — NOT A PRODUCTION GRANT OR STATUTORY APPOINTMENT  
**Runtime:** Python EOS only  
**Baseline reviewed:** `969bdd12e34ca0195abd0e9028e36d2eb19ca372`

## 1. Purpose and governing rule

This policy defines the separation between tenant ownership, tenant business roles, permission grants, scoped operational authority, professional/statutory authority, and commercial product entitlements for a legal-firm tenant.

The canonical authorization path remains the existing Python EOS tenant authorization composition. This document does not create an alternate authorization engine, grant a permission, issue an entitlement, activate a subscription, or certify a person's professional or statutory standing.

**A tenant owner governs the WILSY tenant. Tenant ownership does not itself make that person a legal practitioner, managing partner, COLP, COFA, MLRO, DPO, trust-account signatory, Sheriff, or authorised matter decision-maker.**

## 2. Existing canonical baseline

The reviewed source already declares the following tenant business roles in `tools/eos/auth/tenant_authority_policy.py`:

- `tenant_owner`
- `tenant_admin`
- `tenant_manager`
- `tenant_auditor`
- Specialist legal, Sheriff/deputy, finance, provider-security, client and workforce roles.

The existing policy is the source of truth for operation eligibility. In particular:

- `tenant_owner` has explicit eligibility for defined profile, membership, business-role, audit, subscription/plan, AI-capacity and billing-intelligence operations.
- `tenant_admin` has a distinct delegated administration profile; it is not interchangeable with ownership.
- `tenant_manager` has a narrower management profile.
- `tenant_auditor` is read-oriented.
- `tenant_owner` is explicitly eligible for the existing `platform_billing_release` operation; this is not a grant of general financial execution.
- The policy's financial-execution operation remains denied for tenant roles.
- The operation-to-permission bindings in `tenant_authorization.py` and canonical permission metadata remain mandatory.
- Business-role eligibility alone is not authorization. The authorization composition also checks principal status, tenant membership, current business-role resolution, canonical permission/operation pairing and an active granting role assignment; workforce-currentness checks apply where policy requires them.

Do not infer a permission from a role name, UI visibility, JWT claim, request field, client-supplied tenant/office identifier or this design document.

## 3. Authority layers (must remain independent)

| Layer | Canonical question | Evidence / enforcement boundary |
|---|---|---|
| Tenant ownership | Who is the legally/contractually recognised owner of this WILSY tenant? | A separately governed ownership record and controlled transfer/recovery process are required; a business-role string is not proof of ownership. |
| Business role | Which tenant business persona is currently assigned to the principal? | Existing tenant business-role authority and current role assignment. |
| Permission | Is this principal allowed to perform this exact operation? | Canonical permission metadata, operation binding, eligibility, active assignment and full tenant authorization decision. |
| Resource scope | Which office, matter, client, document or record may the principal access? | Exact server-derived scope and resource-level policy; tenant membership is not universal matter access. |
| Professional/statutory authority | Is the person currently qualified or appointed for the regulated act? | Independent regulator, court, statutory appointment, Board or other authoritative evidence and currentness verification. |
| Product entitlement | Has this tenant purchased/activated the capability, and is it within limits? | Canonical subscription/product entitlement source, effective period, status, plan and usage limits. |
| Financial execution | Is this exact financial action independently authorised? | Dedicated financial controls and the separate financial authority domain; never inferred from tenant ownership. |

Authorization for a protected operation is conjunctive. A successful tenant IAM decision cannot replace resource scope, professional authority or product entitlement where those are required.

## 4. Role responsibilities

### 4.1 `tenant_owner`

The owner is a distinct ownership/commercial-governance persona, not a universal administrator. The existing matrix explicitly denies `tenant_owner` both `role_grant` and `role_revoke`; role assignment is not an owner wildcard. The exact eligibility of every administrative operation must be read from the canonical matrix rather than inferred from role names. The owner profile is intended for:

- Tenant profile and permitted lifecycle governance.
- Tenant membership oversight and permitted membership administration.
- Business-role governance within the exact existing delegation policy.
- Tenant audit and governance visibility.
- Subscription and plan administration within canonical commercial operations.
- Visibility into the tenant's product entitlements, usage and billing evidence where separately permissioned.
- Ownership-specific commercial decisions only where an exact canonical operation and permission binding exist.

The owner role does **not** imply unrestricted access to all client matters, confidential HR records, trust-account funds, privileged legal advice, provider credentials, another tenant, or any statutory workflow.

### 4.2 `tenant_admin`

A delegated tenant administrator may perform only the administration operations explicitly eligible and permission-bound to that role. The reviewed tests explicitly deny `tenant_admin` `lifecycle_archive`; do not infer that it can grant/revoke roles or perform other operations unless the canonical eligibility and permission-binding maps say so. It is not the legal or contractual owner and must not inherit ownership transfer, owner-only commercial liability or owner-only controls by analogy.

### 4.3 `tenant_manager`

A manager receives only the narrower operational and commercial operations explicitly mapped to the manager role. It is not a synonym for managing partner.

### 4.4 `tenant_auditor`

An auditor receives read-only governance/audit visibility where explicitly mapped. No mutation, role assignment, commercial commitment, matter execution or financial execution is implied.

### 4.5 Specialist legal-firm personas

Roles such as `tenant_legal_partner`, `tenant_legal_attorney`, `tenant_legal_paralegal`, `tenant_legal_secretary`, `tenant_legal_finance`, `tenant_sheriff` and `tenant_deputy` remain separate specialist personas. Their operation eligibility is not inherited by `tenant_owner` or `tenant_admin`.

Human titles such as Managing Partner, Office Manager, Practice Manager, COLP, COFA, MLRO and DPO must be represented by their appropriate governed appointment/operating-model evidence. A descriptive catalogue item or role label alone is not proof of appointment or qualification.

## 5. Permission design rules

1. Use exact operation identifiers and canonical permission strings. No wildcard owner permission.
2. Preserve the existing `BUSINESS_ROLE_OPERATION_PERMISSIONS`, operation eligibility map, permission namespace and `_BINDINGS` as the canonical policy surfaces; change them only through separately tested, versioned changes.
3. Never implement a special-case owner bypass in a router, dependency, service or repository.
4. Never let a browser/client choose its own tenant, principal, office, matter or authority scope.
5. Require an active principal, active tenant membership, current business-role authority, eligible role, exact permission-operation match and active granting role assignment.
6. Apply workforce-currentness requirements where the existing authorization policy says they apply.
7. Apply office/matter/client/document scope and any statutory/professional evidence checks after tenant IAM, not as substitutes for it.
8. Explicit deny, revoked assignment, stale evidence, unknown permission, unknown operation, unavailable authority source or ambiguous scope must fail closed.
9. Preserve caller-owned Mongo transaction boundaries for registry-backed authority/currentness reads; the policy layer must not silently start, commit, abort or retry caller transactions.
10. Keep financial execution denied in tenant IAM. Commercial subscription administration and financial execution are different capabilities.

## 6. Product entitlements

Entitlements are tenant/product facts, not roles or permissions.

An entitlement decision must identify at least:

- Exact tenant and product/capability identifier.
- Source subscription/contract and plan reference.
- Entitlement status and revision.
- Effective-from and effective-until instants.
- Applicable quantity, seat, storage, API, usage or feature limits.
- Current consumption and enforcement period where metered.
- Suspension, cancellation, expiry and supersession state.
- Evidence/provenance reference and fingerprint.

A role may be eligible to administer a subscription without the tenant possessing the product. A tenant may possess a product entitlement while an individual principal lacks permission to use or administer it. Both checks must pass when both are required.

**Repository inventory result (baseline commit):** WILSY already has the D22B1 immutable tenant/product entitlement domain (`tools/eos/saas/domain/tenant_product_entitlement.py`), D22B2 append-only/current-pointer registry (`tools/eos/saas/entitlement/tenant_product_entitlement_registry.py`), D22B3 subscription-bound composer (`tools/eos/saas/entitlement/tenant_product_entitlement_composer.py`) and a positive issuance orchestrator. The domain's lifecycle states are `PENDING_SOURCE`, `ACTIVE`, `SUSPENDED` and `REVOKED`; an ACTIVE entitlement is tenant/product availability evidence, not principal permission or route admission. The composer correlates exact tenant scope, canonical product catalogue identity, subscription registry truth and subscription-term policy inside a caller-owned transaction. The issuance operation is already bound as `tenant_product_entitlement_issue` → `tenant_product_entitlement:issue`; eligibility is limited to `tenant_owner`, `tenant_admin` and `tenant_manager`, while the static granting authorization role is `ENTERPRISE_ADMIN`. Existing tests certify this authorization substrate and explicitly distinguish issuance authority from issuance itself. WILSY AI and Tenant Branding remain separate VAS authorities.\n\n**Do not duplicate this entitlement infrastructure.** The next implementation must inspect every product-gated consumer and preserve the existing D22B5 plus commercial-context conjunction through established orchestration boundaries. The reviewed entitlement domain itself does not encode generic seat/storage/API usage counters or an independent effective-until field; derive term eligibility from canonical subscription truth and do not invent additional fields without a product/contract requirement. D22B5's availability projection alone reads the D22B2 current entitlement and maps `ACTIVE` to available. However, the existing `legal_commercial_context_projection.py` performs a second, same-session conjunction with `SubscriptionRegistry.list_entities`, requiring exactly one ACTIVE subscription containing `legal.core` whenever the entitlement is ACTIVE; it rejects entitlement/subscription disagreement and multiple active subscriptions. The authenticated `/commercial-context` route uses this conjunction. Thus this is not a blanket entitlement currentness defect across all Legal workspace admission: the narrower D22B5 projection remains descriptive only and must not be used as the sole commercial-currentness proof where subscription status is material. Inspect every consumer and retain the stronger conjunction for admission/commercial decisions.

## 7. Ownership lifecycle and separation of duties

A future ownership lifecycle must support initial verified ownership, controlled transfer, recovery, suspension where contractually appropriate, and immutable audit history.

Minimum invariants:

- No user may make themselves owner by submitting `tenant_owner`, a role claim, email match or browser payload.
- Ownership transfer requires an independently authenticated and authorized transfer command, exact tenant scope, explicit acceptance by the successor where applicable, and durable append-only evidence.
- The transfer command must not allow the current owner to erase or rewrite its history.
- Recovery must use a separately governed process and must not be an ordinary `tenant_admin` privilege.
- Removing or suspending an owner must not silently leave a tenant ownerless; use a governed recovery/transfer state.
- The ownership record and the active `tenant_owner` business-role assignment must reconcile. A mismatch blocks ownership-only operations.
- Owner status does not bypass dual control or separation-of-duties rules for high-consequence actions.

This document does not assert that these ownership lifecycle controls already exist. They are implementation requirements to be verified against the repository before enabling owner-only operations that depend on ownership proof.

## 8. Protected domains that ownership must not override

The following always retain independent authority and scope:

- Legal practitioner admission, current professional standing and matter-specific authorization.
- Client identity, engagement, mandate, representation, conflicts and ethical walls.
- COLP/COFA/MLRO/DPO appointments and restricted HR information.
- Trust-account mandates, signatories, reconciliations, payments and financial execution.
- Sheriff Ministerial appointment, area allocation, Board approval, Fidelity Fund Certificate, insurance, identity binding, office scope and service authority.
- Court filing, service completion, evidence certification and legal execution.
- Cross-tenant isolation and restricted client/matter confidentiality.

For Sheriff operations in particular, `tenant_owner` or `tenant_admin` must never be treated as a Sheriff appointment or office authorization. The existing Sheriff evidence modules explicitly distinguish documentary capture from issuer authentication, currentness, IAM and operational authority.

## 9. Entitlement and role evaluation sequence

For a protected feature, the application should evaluate the following independently and fail closed:

1. Authenticate the principal and resolve current principal status.
2. Resolve exact tenant membership and status.
3. Resolve current tenant business role and active role assignment.
4. Resolve canonical operation-to-permission binding and permission possession.
5. Evaluate the canonical tenant authorization decision.
6. Resolve exact resource scope (office, matter, client, document or other resource).
7. Resolve required professional/statutory authority and currentness.
8. Resolve tenant product entitlement, effective status and applicable limits.
9. Apply any action-specific dual-control, financial or execution gate.
10. Record the authorization/evidence basis required by the operation.

Not every operation requires every layer; the operation policy must declare which layers apply. No layer may be silently inferred from another.

## 10. Implementation sequence and acceptance criteria

### Phase A — inventory and compatibility (required first)

- Inspect the complete current operation/permission maps, permission metadata, role assignment semantics, subscription and product-entitlement registries, and tenant lifecycle/ownership records.
- Identify existing implementations before adding schemas or registries.
- Produce a role × operation × permission matrix from canonical source data, not a separately maintained hand-written list.
- Add tests that freeze current owner/admin/manager/auditor boundaries and prove specialist roles do not inherit owner permissions.
- Confirm exact behavior for owner role assignment, owner-only operations and entitlement issuance before changing any existing mapping.

### Phase B — canonical policy integration

- Add only missing exact operation/permission pairs after Phase A proves they do not already exist.
- Keep role eligibility, permission possession, active assignment and product entitlement as separate checks.
- Version the policy and evidence basis.
- Add negative tests for forged owner claims, inactive membership, revoked role assignment, wrong tenant, wrong permission, wrong resource scope, absent/expired/suspended entitlement and cross-tenant access.

### Phase C — ownership lifecycle

- Implement ownership evidence only if no canonical ownership source already exists.
- Require caller-owned transaction semantics, append-only history, tenant-first indexes, replay/conflict protection and a current pointer derived from history.
- Add transfer/recovery and ownerless-state adversarial tests.

### Phase D — UI and commercial projection

- Render only actions permitted by the canonical authorization decision and active product entitlement.
- UI hiding is not an authorization control; every command/route re-evaluates EOS authority.
- Show entitlement state, limits, renewal and usage without exposing billing secrets or unrelated tenant data.

### Required test cases

- Owner can perform only explicitly eligible and permission-bound tenant operations.
- Admin cannot perform owner-only operations.
- Manager and auditor remain within their respective explicit maps.
- Owner does not gain legal-practitioner, trust-account, Sheriff, HR-restricted, matter-confidentiality or financial-execution authority by inheritance.
- Role eligibility without permission possession denies.
- Permission possession without active role assignment denies.
- Valid role/permission without product entitlement denies a product-gated feature.
- Product entitlement without principal permission denies a protected operation.
- Expired, suspended, cancelled, revoked or wrong-tenant entitlements deny.
- Forged `tenant_owner` request/JWT/client claims do not create ownership or authorization.
- Cross-tenant and out-of-scope resource access deny.
- Replay, duplicate transfer, stale current pointer and concurrent transfer conflicts are detected if an ownership registry is added.

## 11. Release boundary

This is a design and engineering control specification. It is not evidence that every capability above is implemented, that a tenant owner has any statutory status, or that all tests have passed.

Do not advertise or enable a capability until its canonical operation, permission binding, role eligibility, current assignment, resource scope, entitlement (where applicable), route enforcement and adversarial tests are all verified on the same branch head.

**END OF LEGAL FIRM TENANT AUTHORITY AND ENTITLEMENT POLICY**
