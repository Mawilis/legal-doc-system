# Global Principal → SYSTEM workspace authentication — 2026-11-05

**Scope:** Initial platform workforce login, principal-scoped MFA, SYSTEM session issuance/currentness, refresh and revocation.  
**Branch:** `eos/tenant-discovery-iam-dashboard-roadmap`  
**Authority:** EOS Global Principal, canonical TOTP verifier and System Services workforce/permission authorizer.

## Entry and issuance

1. A principal submits credentials to `POST /auth/global/login`. This route is tenant-neutral and does not accept a tenant selector as authority.
2. EOS authenticates the global principal and verifies that an active TOTP factor exists.
3. When the canonical membership-selection page contains no tenant memberships, EOS does not invent a tenant or create a tenant membership. It asks the current `SystemServicesEosAuthorizer` to prove the exact principal has `system_services:queue:read` through active PLATFORM workforce and permission-possession evidence.
4. Only then does EOS issue a short-lived, opaque `sysmfa_` challenge. The challenge stores only a digest and is bound to principal ID and credential revision.
5. `POST /auth/global/verify-mfa` verifies TOTP using the canonical KMS-backed verifier, consumes the challenge, revalidates the principal/credential/workforce authority, and inserts the SYSTEM session plus refresh token in the same caller-owned Mongo transaction.
6. The access JWT is explicitly marked `principal_scope=SYSTEM`, has the reserved internal scope marker `tenant_id=SYSTEM`, the presentation role `SYSTEM_SERVICES`, and an empty tenant-permission list. No tenant membership, business capacity, tenant ID or tenant permission is created.
7. The browser then calls `GET /system-services/workspace-bootstrap`; only the exact EOS response is persisted as a presentation projection.

## Currentness and lifecycle

- Every SYSTEM access-token request revalidates the durable session, current global-principal status, credential revision, and current SYSTEM queue-read authority in a caller-owned transaction.
- Loss of the platform workforce relationship, permission possession, principal status or credential revision invalidates the session.
- Access tokens expire after 15 minutes. A single-use `sysrefresh_` bearer rotates access and refresh tokens in a caller-owned transaction; refresh expires at the original eight-hour SYSTEM session boundary.
- Logout revokes the session and all refresh tokens for that session in one transaction.
- Challenge, session and refresh-token indexes are created by EOS startup before the SYSTEM session readiness flag is set; startup and shutdown reset readiness fail-closed.

## Browser boundary

The browser supports the initial no-tenant global login → TOTP → SYSTEM workspace bootstrap path. It clears stale tenant transport state before the global login and does not set a tenant header for SYSTEM calls. The UI accepts only the exact EOS workspace authority, SYSTEM scope, matching principal ID and allow-listed capabilities. The browser refreshes SYSTEM tokens before the 15-minute access expiry and does not infer permissions from the presentation role.

## Certification layers

- Unit tests cover tenant-neutral login selection, TOTP route composition, exact SYSTEM token claims/currentness, challenge replay, refresh rotation, logout and browser projection.
- A real-replica-set test covers challenge consumption, session and refresh insertion, refresh rotation/replay rejection, revocation and transaction rollback.
- The Playwright journey covers the browser credential → MFA → workspace-bootstrap presentation flow with isolated mocked HTTP responses. It is a browser contract certificate, not a substitute for the backend route and replica-set certificates.

## Release gates

The canonical TOTP verifier must be available through the configured KMS envelope. No development plaintext fallback is introduced. Platform workforce and SYSTEM permission evidence must be seeded and independently governed. A SYSTEM role label, browser state, tenant header or user-provided permission list cannot grant SYSTEM access.

No production KMS activation, login cutover, credential mutation, PR merge or deployment is authorized by this implementation.
