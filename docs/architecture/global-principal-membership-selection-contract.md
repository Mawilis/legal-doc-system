# Global Principal and Tenant Membership Selection Contract

Date: 2026-11-03
Status: Architecture contract plus read-only membership projection implemented; global credential migration and HTTP/session integration outstanding.

## 1. Non-negotiable identity model

WILSY OS must distinguish three scopes:

1. **Global principal** — one human/service identity, independent of any tenant.
2. **Tenant membership** — a durable, independently revocable relationship between that principal and one canonical tenant.
3. **Tenant business capacity** — one or more independently revisioned business roles held by that principal within that tenant. Each selected capacity resolves to one EOS workspace; authorization remains separately evaluated per operation.

A tenant alias/domain is a discovery hint only. It is not a principal identifier, membership proof, business role, permission, or session.

## 2. Target authentication sequence

1. Resolve the entered tenant alias/domain through EOS TenantRegistry. Return a bounded tenant identity projection only.
2. Authenticate the global principal against one canonical global credential record. Do not search or infer the person's membership from tenant user-directory records.
3. Resolve the ACTIVE PrincipalAuthority for that global principal.
4. Enumerate only that principal's memberships through a bounded, deterministic, cursor-paginated repository query. Never enumerate all tenants or users.
5. For each selectable membership, revalidate the exact canonical ACTIVE tenant and all current business capacities. Do not expose suspended/revoked memberships as selectable choices.
6. Require the person to select one exact tenant membership and, where multiple active capacities exist, one exact business capacity. A tenant discovery hint may preselect a matching choice but cannot bypass membership validation.
7. Re-read the selected principal, membership, tenant and business capacity inside the session-issuance transaction. Bind the issued ACCESS session to their exact IDs and revisions.
8. Complete MFA against the global principal credential/factor. Successful factor verification and session issuance must be atomic under the existing caller-owned transaction pattern.
9. On every protected request, verify token purpose, global principal status and credential revision; tenant admission and resource IAM remain independently enforced by EOS. Membership/capacity revision changes must invalidate or narrow the selected session before protected work proceeds.
10. Return the workspace contract from EOS. The browser renders only the returned workspace identifier and never maps roles or tenant IDs to authority.

## 3. Canonical persistence target

Introduce a global credential authority (proposed collection: `principal_credentials`) with a unique normalized-email key and unique principal key. It owns the password verifier, credential revision, explicit MFA-enrollment state and credential lifecycle. The MFA secret remains in a separately protected principal-scoped factor store and is never copied into this record. It must not contain tenant_id, tenant roles, tenant permissions or workspace selection.

Existing `users` rows must not be silently merged or treated as global credentials. They currently combine email/password hash/MFA state with one `tenantId`, and `AuthRegistry.get_user_by_email` assumes a single result. Before cutover:

- inventory exact existing rows by normalized email and durable user/principal ID;
- compare duplicate email rows and password/MFA state without exporting secret values;
- match every row to exactly one ACTIVE PrincipalAuthority;
- match every selectable tenant to an already-existing ACTIVE TenantMembership and ACTIVE TenantBusinessRole;
- quarantine duplicate, conflicting, orphaned or malformed records for governed reconciliation;
- migrate only unambiguous credentials in a caller-owned, idempotent transaction;
- preserve credential revision monotonicity and revoke/expire sessions issued under the old tenant-bound credential contract;
- switch login, MFA, recovery, reset, refresh, token verification and session revocation together;
- remove tenant-bound password hashes only after all consumers have moved and a rollback/cutover certification passes.

No migration creates PrincipalAuthority, TenantMembership, business capacity, authorization RoleAssignment, or legal practice authority.

## 3A. Global credential persistence primitive added in this branch

- Added `PrincipalCredential` as a tenant-neutral immutable credential snapshot containing only `principal_id`, normalized email, bcrypt password verifier, monotonic credential revision and an explicit MFA-enrollment boolean.
- Added `PrincipalCredentialRepository` with unique principal/email index definitions, exact lookups, duplicate rejection and compare-and-swap password verifier revision updates.
- Added `authenticate_global_principal`, which verifies the tenant-neutral credential against an exact ACTIVE PrincipalAuthority and returns only global principal identity, credential revision and MFA enrollment state. It returns no tenant, membership, business role, permission, workspace or session. Unknown-email attempts perform bcrypt-equivalent work; rate limiting and generic public HTTP failures remain caller responsibilities.
- The new credential schema contains no tenant ID, membership, business role, permission, workspace, raw MFA secret or financial fields.
- Unit tests cover schema boundaries, normalized email lookup, principal/email uniqueness, credential revision CAS, malformed verifier rejection and caller-session forwarding.
- Added `.github/workflows/global-principal-membership-certification.yml` to compile and execute the focused principal-credential, migration-assessment, membership-repository and membership-projection unit tests on relevant pull-request changes.

This repository is intentionally not wired into login or application startup yet. Existing MFA, password reset, refresh, session and access-token currentness paths still depend on the legacy tenant-scoped `users` record. Switching only the login lookup would create inconsistent credential authorities. No production collection/index or credential row has been created by this code change.

- Added `assess_legacy_user_credential`, a read-only migration assessor. It admits only one unique email row with valid credential/MFA shape, an exact ACTIVE global principal, canonical ACTIVE tenant and existing ACTIVE membership. Conflicting/duplicate or incomplete records are quarantined with bounded reason codes; authority outages are surfaced separately.
- Password verifiers are hidden from the credential object's representation to reduce accidental diagnostic disclosure.
- The assessor does not write, merge, create principals, create memberships or assign capacities. It has not been run against production data and no production collection/index or credential row has been created.

## 4. Membership selection projection added in this branch

- `TenantMembershipRepository.list_for_principal` provides a bounded page (maximum 100) sorted by canonical tenant ID, with a continuation cursor and caller-session propagation.
- `build_membership_selection_page` requires an ACTIVE global PrincipalAuthority, resolves only that principal's membership rows, filters non-ACTIVE memberships, revalidates each canonical tenant, and composes every current ACTIVE business capacity from `TenantBusinessRoleRepository.resolve_all`.
- The projection returns tenant IDs, membership revisions, business-role IDs, workspace IDs and business-role revisions. It does not return permissions, credentials, profile secrets, or authorization grants.
- A membership without an ACTIVE business capacity is visible as a non-selectable membership state with an empty capacity list; it is never promoted to a workspace.
- Multiple active capacities are represented separately. No union, highest-role selection or silent default is applied.
- Pagination is per principal and never performs a tenant-wide scan.

This is a read-only service primitive, not yet a public endpoint or complete login journey. It must be wired only after the global credential authority can authenticate a principal independently of a tenant.

## 5. Existing limitations that block end-to-end multi-membership login

- `AuthRegistry.users` still stores `tenantId` alongside password hash and MFA state.
- `AuthRegistry.get_user_by_email` uses `find_one({email})`; it is not a global credential lookup.
- `AuthRegistry.get_credential_revision`, ACCESS issuance and `get_current_identity` currently read credential revision using both tenant_id and principal_id.
- PRE_AUTH/MFA challenge currently carries a tenant selector and the router re-reads the tenant-bound user by email.
- `create_session` binds a tenant-specific user and tenant-bound refresh token. It does not yet accept a selected membership/capacity revision contract.
- Workspace bootstrap currently calls the single-capacity `TenantBusinessRoleRepository.resolve`; it does not yet consume an explicitly selected capacity claim when multiple active capacities exist.
- The existing tenant memberships and multi-capacity business-role repositories are durable foundations, but they do not remove the tenant-bound credential assumption.

No claim of global-principal authentication, multi-membership login, cross-tenant switching, or end-to-end membership selection may be made until these blockers are migrated and certified.

## 6. Certification gates

1. Unit tests for global credential uniqueness, exact principal lookup, revision CAS, factor binding and no tenant fields.
2. Adversarial tests for duplicate email, duplicate principal, inconsistent legacy hashes, suspended principal, inactive membership, stale membership revision, stale capacity revision, ambiguous capacities and cross-tenant selector substitution.
3. Real-Mongo replica-set tests for transaction atomicity, uniqueness, rollback, retry and concurrent selection/revocation.
4. HTTP tests for discovery → credential authentication → membership choices → exact capacity selection → MFA → selected session → EOS workspace bootstrap.
5. Browser E2E tests with at least two principals and a principal with multiple tenant memberships; verify the correct workspace on every login and after revocation/switch.
6. Cutover certification showing old tenant-bound credentials are no longer read by any login/MFA/recovery/token path.
7. Only after the above gates may the legacy credential fields or dependent runtime paths be retired.

## 7. Security invariants

- Discovery is not membership.
- Authentication is not authorization.
- Membership is not business capacity.
- Business capacity is not a permission grant.
- Workspace selection is not an access token.
- A browser-supplied tenant, membership, role, workspace or revision is never authoritative.
- No tenant-wide directory scan, cross-tenant role union, default tenant, default capacity or fabricated membership is permitted.
- Tenant Partner/Owner role equivalence is not inferred. Any parity must be represented by separately approved durable business-role and authorization assignments and independently tested.
