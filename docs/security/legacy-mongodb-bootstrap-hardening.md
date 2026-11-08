# WILSY EOS — Legacy MongoDB Bootstrap Retirement

**Version:** v1.0.0  
**Status:** Development remediation; no production database was accessed or modified  
**Scope:** Four legacy shell scripts that bypass canonical IAM or grant application identities administrative database authority.

## Security findings

The reviewed repository revision contained four unsafe bootstrap scripts:

| Script | Unsafe behavior identified |
|---|---|
| `server/fix_tenant_auth.sh` | Embedded service-account credential and self-grant of tenant database access |
| `server/inject_master_user.sh` | Embedded service-account credential and direct upsert of an active privileged identity, bypassing canonical principal, membership, capacity and MFA |
| `server/elevate_wilsy_app.sh` | Grants `userAdmin` to the application service identity |
| `server/force_fix_wilsy.sh` | Unauthenticated MongoDB role injection and broad application database grants |

The credential value is deliberately not reproduced. A tracked credential must be treated as exposed even if its current validity is unknown. Removing it from the latest file contents does not erase it from Git history.

## Code remediation

Each of the four scripts has been replaced with an inert, fail-closed retirement stub. The stubs:
- contain no credential or database command;
- cannot grant MongoDB roles or mutate user records;
- emit a clear disabled status and exit non-zero;
- direct operators to externally authenticated, governed provisioning or break-glass workflows.

A parameterized unit test executes each script and verifies that it fails closed without invoking MongoDB or performing identity/role mutation.

## Required operational response

Code retirement does not rotate a database credential or prove that an already-running MongoDB user has lost its roles. Before any production trust activation:

1. Identify every environment where the exposed credential may have been configured.
2. Rotate/revoke it through an authenticated database administrator identity; do not use the retired scripts.
3. Inspect MongoDB authentication and role-change audit logs for use of the credential and for privileged identity injection.
4. Remove excess roles from the application identity; it must not hold `userAdmin`, `dbAdmin`, or role-management privileges.
5. Provision separate least-privilege application and audit-writer identities. The application identity must not update/delete audit events, audit heads or denial evidence.
6. Verify the effective roles from each deployed runtime identity and test denied write/delete operations against audit collections.

No database credentials were available to this code change, and no live database role or credential was modified. Operational rotation and log review remain required.

## Certification boundary

This is a development-only repository change. It does not authorize production activation, merge of PR #393, institutional trust anchors, or use of real DHA/CIPC material.
