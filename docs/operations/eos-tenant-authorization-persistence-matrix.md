# EOS Tenant Membership and Authorization Persistence Matrix — Verified Source Slice

**Scope:** principal authority, tenant membership, tenant business-role capacity, and role assignment repositories  
**Repository:** `Mawilis/legal-doc-system`, PR #342 engineering branch  
**Status:** source-level repository inventory only; not proof of production route reachability or deployment usage

## Literal collections and observed operations

| Literal collection | Repository | Observed runtime operations | Index provisioning |
|---|---|---|---|
| `principal_authorities` | `tools/eos/auth/principal_authority_repository.py` | `insert_one`, `find_one`, `replace_one` with principal/revision match | Unique `principal_id` |
| `tenant_memberships` | `tools/eos/auth/tenant_membership_repository.py` | `insert_one`, `find_one`, bounded/sorted `find`, revision-guarded `replace_one` | Unique compound `principal_id, tenant_id` |
| `tenant_business_roles` | `tools/eos/auth/tenant_business_role_repository.py` | `find`, `find_one`, `insert_one`, revision-guarded `replace_one`; legacy single-role projection remains readable | Unique compound `principal_id, tenant_id` |
| `tenant_business_role_assignments` | same | `find`, `insert_one`, revision-guarded `replace_one` through multi-capacity authority path | Unique compound `principal_id, tenant_id, business_role` |
| `tenant_business_role_assignment_history` | same | append-only `insert_one` for assignment history/revision evidence | Unique compound `principal_id, tenant_id, business_role, revision` |
| `role_assignments` | `tools/eos/auth/role_assignment_repository.py` | `insert_one`, `find_one`, `find`, revision-guarded `replace_one` | Unique compound `principal_id, tenant_id, role_id` |

## Role and execution implications

- These collections represent distinct authority layers. Do not collapse principal identity, tenant membership, business capacity, and role assignment into one broad write permission.
- The repositories use revision-guarded replacement for updates. Preserve read/write permissions required for these operations; do not substitute broad deletes or unrestricted upserts.
- The business-role repository supports both a legacy single-role collection and multi-role/history collections. The multi-role/history index creation is a separate method that accepts a database and creates indexes on those two collections. The canonical API server bootstrap excerpt inspected earlier did not call that method directly; establish which provisioner/entrypoint invokes it before classifying it as API startup DDL.
- Transactions are caller-owned in these repositories. Validate session-bound insert/replace operations against the replica-set test environment.
- Provisioning indexes should be separated from request-serving runtime credentials. The API role should not receive index-management actions merely because repository classes expose `ensure_indexes`.

## Exact index keys

- `principal_authorities`: unique ascending `principal_id`.
- `tenant_memberships`: unique ascending `principal_id, tenant_id`.
- `tenant_business_roles`: unique ascending `principal_id, tenant_id`.
- `tenant_business_role_assignments`: unique ascending `principal_id, tenant_id, business_role`.
- `tenant_business_role_assignment_history`: unique ascending `principal_id, tenant_id, business_role, revision`.
- `role_assignments`: unique ascending `principal_id, tenant_id, role_id`.

## Remaining uncertainty

This is not a complete inventory of every authority/evidence collection consulted by authentication. In particular, trace the repository factories used by the live global login/membership selection routes and the API's authorization dependencies to prove which of these collections are read on every authenticated request. Also trace tenant membership and role provisioning entrypoints, background workers, migrations, and tests separately.

**Production decision remains NO-GO** for runtime user/role replacement, credential rotation, or network-access modification until the complete API + worker + audit + migration matrix and deployed host/secret/Atlas binding are proven.
