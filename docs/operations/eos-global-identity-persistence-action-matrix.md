# EOS Global Identity Persistence Action Matrix — Verified Repository Slice

**Revision inspected:** PR #342 branch `eos/tenant-discovery-iam-dashboard-roadmap`, commit immediately preceding this inventory update  
**Scope:** global-principal credential, membership-selection challenge, session/refresh, TOTP/MFA enrollment, and authentication rate-limit repositories  
**Status:** source-level operation inventory; not a complete API-wide or production-observed matrix

This slice resolves literal collection names and operations from the repository implementations. It does not identify the live production host or Atlas target. No production secrets, database data, Atlas users, roles, access lists, or deployments were accessed or changed.

## Literal collection/action matrix

| Literal collection | Source owner | Runtime operations observed | Startup index DDL observed |
|---|---|---|---|
| `principal_credentials` | `tools/eos/auth/principal_credential_repository.py` | `find` (bounded exact lookup by principal/email); `insert_one`; `update_one` (credential revision/state changes) | Unique `principal_id`; unique `normalized_email` |
| `eos_authentication_challenges` | `tools/eos/auth/membership_selection_challenge.py` | `insert_one`; `find_one` by challenge digest for membership-selection and MFA challenge context; atomic consume/update path | Unique `challenge_digest`; TTL `expires_at` |
| `global_principal_sessions` | `tools/eos/auth/global_principal_session_authority.py` | `insert_one`; `find_one` current session; `update_one` revoke | Unique `session_reference`; compound current lookup `principal_id, tenant_id, revoked_at` |
| `global_principal_refresh_tokens` | same | `insert_one`; `find_one` digest/session lookup; `update_many` revoke associated tokens; refresh rotation inserts replacement digest | Unique `token_digest`; TTL `expires_at` |
| `global_principal_mfa_factors` | `tools/eos/auth/global_principal_totp_verifier.py` and enrollment service | `find` by principal (bounded); `update_one` accepted TOTP step/replay protection; enrollment `update_one` factor state | Unique `principal_id` |
| `global_principal_mfa_enrollment_challenges` | `tools/eos/auth/global_principal_mfa_enrollment_service.py` | `delete_many` expired pending challenges for principal; `find_one`; `insert_one`; `update_one` attempt count; factor `update_one`; `delete_one` consumed challenge | Unique `principal_id`; unique `challenge_digest`; TTL `expires_at` |
| `principal_authentication_rate_limits` | `tools/eos/auth/principal_authentication_rate_limit.py` | `find_one` bucket; `update_one` bucket state/upsert (see implementation); `delete_one` expired/reset bucket | Unique compound `scope, subject_digest, bucket_start`; TTL `expires_at` |

### Important additional dependency

The MFA enrollment migration path reads the legacy factor collection using `legacy_factors.find({"user_id": principal_id})`. Its exact literal name and deployment injection path must be resolved from the legacy adapter and route composition before finalizing any role. Do not silently fold this dependency into `global_principal_mfa_factors`.

## Exact startup index specifications from inspected repositories

- `principal_credentials`: unique ascending `principal_id`; unique ascending `normalized_email`.
- `eos_authentication_challenges`: unique ascending `challenge_digest`; ascending `expires_at` with `expireAfterSeconds=0`.
- `global_principal_sessions`: unique ascending `session_reference`; non-unique compound ascending `principal_id, tenant_id, revoked_at`.
- `global_principal_refresh_tokens`: unique ascending `token_digest`; ascending `expires_at` with `expireAfterSeconds=0`.
- `global_principal_mfa_factors`: unique ascending `principal_id`.
- `global_principal_mfa_enrollment_challenges`: unique ascending `principal_id`; unique ascending `challenge_digest`; ascending `expires_at` with `expireAfterSeconds=0`.
- `principal_authentication_rate_limits`: unique compound ascending `scope, subject_digest, bucket_start`; ascending `expires_at` with `expireAfterSeconds=0`.

TTL indexes are server-managed expiry behavior, not application-issued delete privileges. The application still has explicit delete operations where code calls `delete_one` or `delete_many`; those must be separately considered.

## Permission design implications

1. The API runtime requires collection-scoped read/write privileges for the operations above. The final action vocabulary must be mapped to MongoDB/Atlas privilege actions only after all repositories and driver behavior are accounted for.
2. Index creation is not a normal request-path permission. Move these index definitions into a versioned, separately authenticated provisioning job and make that job idempotent and reviewable.
3. If provisioning remains in API startup, a role without index-management authority may fail readiness. Do not grant broad database-wide schema privileges as a shortcut.
4. Transactions/session use is part of the driver execution path. Validate the chosen role and topology against a replica-set test deployment, including transaction commits/aborts and duplicate-key paths.
5. The refresh/session collections have separate write patterns: refresh rotation creates a replacement token and revokes prior tokens; logout revokes a session and its refresh tokens. Do not overgrant delete when code uses revocation updates.
6. The legacy MFA migration read is a separate dependency and should be isolated to a migration identity or removed after the legacy cutover is independently certified.

## Next source-audit tranche

Continue the same method for:
- tenant membership, business capacity and role assignment repositories;
- System Services case registry and its event collection;
- authorization/revocation and privileged workload evidence registries;
- Legal Storefront public intent and rate-limit registries;
- practitioner/matter binding and conflict-disposition registries;
- AI orchestration, invocation, entitlement and usage-observation registries;
- every remaining mounted router's persistence dependencies;
- the separate Legal Evidence reconciliation audit client and its distinct secret/target.

For each collection, record literal name, read/write operations, transaction/session use, index definitions, optional feature gates, and owning runtime identity. Only after this complete matrix is checked against the deployed image should a custom Atlas role be designed.

## Decision

**NO-GO** for production custom-role creation, database-user replacement, credential rotation, or network-access changes. This verified slice is useful input, not the full runtime contract.
