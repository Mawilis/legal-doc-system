"""TITLE: WILSY OS Founder HR IAM Read-Only Preflight
VERSION: v1.0.0-FOUNDER-HR-READ-ONLY-PREFLIGHT
AUTHORITY: Read-only inspection of current durable tenant IAM evidence.
EPITOME: Compare Founder, Owner, membership and employer HR prerequisites
         without issuing business capacities, role assignments or permissions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/ops/founder_hr_iam_preflight.py
COLLABORATION / OWNERSHIP: WILSY EOS IAM operator preflight; canonical authority repositories remain source owners.
CERTIFICATION / UPDATE DATE: 2026-11-27
CHANGELOG: v1.0.0-FOUNDER-HR-READ-ONLY-PREFLIGHT adds safe, exact-tenant, source-only HR readiness classification.
COMPLIANCE: POPIA section 19; GDPR Article 32.
SECURITY POSTURE: Never render principal IDs, credentials or personnel records.
TENANT BOUNDARY: Canonical WILSY employer only; no fallback tenant aliases.
AUTHORITY BOUNDARY: Findings are prerequisites, NEVER an authorization decision.
FINANCIAL AUTHORITY: Kennel EOS exclusively.
"""
from __future__ import annotations

import argparse
import json
from typing import Any, Final, Mapping, Sequence

from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID

VERSION: Final[str] = "v1.0.0-FOUNDER-HR-READ-ONLY-PREFLIGHT"


def _bounded_find(database: Any, collection: str, criteria: Mapping[str, object],
                  projection: Mapping[str, int], limit: int = 40) -> list[dict[str, Any]]:
    """Read only a bounded identity-authority projection; never enumerate employees."""
    return list(database[collection].find(dict(criteria), dict(projection)).limit(limit))


def inspect_founder_hr_prerequisites(database: Any, tenant_id: str) -> dict[str, object]:
    """Inspect source facts, not login/MFA/session currentness or effective access.

    An HR role and business capacity are separately mandatory. Passing these
    checks is not proof that a command will be admitted by EOS.
    """
    if tenant_id != WILSY_COMPANY_TENANT_ID:
        raise ValueError("FOUNDER_HR_PREFLIGHT_TENANT_NOT_CANONICAL")

    founders = _bounded_find(
        database, "institutional_principal_designations",
        {"tenant_id": tenant_id, "designation": "Founder"},
        {"_id": 0, "principal_id": 1, "state": 1, "business_role": 1,
         "grants_permissions": 1}, limit=2,
    )
    if len(founders) != 1 or not isinstance(founders[0].get("principal_id"), str):
        return {
            "schema": "WILSY-FOUNDER-HR-IAM-PREFLIGHT/V1",
            "tenant": "CANONICAL_WILSY_EMPLOYER",
            "status": "FOUNDER_DESIGNATION_NOT_UNIQUELY_VERIFIED",
            "hr_access_verified": False,
            "database_mutated": False,
        }

    founder = founders[0]
    principal_id = founder["principal_id"]
    criteria = {"tenant_id": tenant_id, "principal_id": principal_id}
    memberships = _bounded_find(database, "tenant_memberships", criteria,
                                {"_id": 0, "status": 1}, limit=3)
    legacy = _bounded_find(database, "tenant_business_roles", criteria,
                           {"_id": 0, "status": 1, "business_role": 1})
    multi = _bounded_find(database, "tenant_business_role_assignments", criteria,
                          {"_id": 0, "status": 1, "business_role": 1})
    assignments = _bounded_find(database, "role_assignments", criteria,
                                {"_id": 0, "status": 1, "role_id": 1})
    capacities = {
        item.get("business_role")
        for item in [*legacy, *multi]
        if item.get("status") == "ACTIVE"
    }
    roles = {item.get("role_id") for item in assignments
             if item.get("status") == "ACTIVE"}
    founder_active = (founder.get("state") == "ACTIVE"
                      and founder.get("business_role") == "tenant_owner"
                      and founder.get("grants_permissions") is False)
    membership_active = len(memberships) == 1 and memberships[0].get("status") == "ACTIVE"
    manager_cap = "tenant_hr_manager" in capacities
    director_cap = "tenant_hr_director" in capacities
    manager_grant = "HR_MANAGER" in roles
    director_grant = "HR_DIRECTOR" in roles
    owner_active = "tenant_owner" in capacities

    return {
        "schema": "WILSY-FOUNDER-HR-IAM-PREFLIGHT/V1",
        "tenant": "CANONICAL_WILSY_EMPLOYER",
        "founder_designation_active": founder_active,
        "membership_active": membership_active,
        "tenant_owner_capacity_active": owner_active,
        "enterprise_admin_role_active": "ENTERPRISE_ADMIN" in roles,
        "hr_manager_capacity_active": manager_cap,
        "hr_manager_authorization_role_active": manager_grant,
        "hr_director_capacity_active": director_cap,
        "hr_director_authorization_role_active": director_grant,
        "employer_hr_read_prerequisites_present": (
            founder_active and membership_active and owner_active
            and ((manager_cap and manager_grant) or (director_cap and director_grant))
        ),
        "status": (
            "AUTHENTICATED_EOS_HTTP_VERIFICATION_REQUIRED"
            if founder_active and membership_active and owner_active
            and ((manager_cap and manager_grant) or (director_cap and director_grant))
            else "GOVERNED_HR_IAM_ISSUANCE_REQUIRED"
        ),
        "hr_access_verified": False,
        "database_mutated": False,
        "limitations": (
            "Does not inspect active MFA/session currentness or HR entitlements.",
            "Does not authorize any action or establish issuer, approver, or payroll authority.",
            "Source must match the MongoDB database used by the running Python EOS.",
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only canonical Founder HR IAM preflight")
    parser.add_argument("--tenant-id", required=True)
    args = parser.parse_args(argv)
    if args.tenant_id != WILSY_COMPANY_TENANT_ID:
        parser.error("Only the canonical Wilsy employer tenant may be inspected")
    from tools.eos.kernel import db as kernel_db
    connected, _ = kernel_db.connect_db()
    if not connected:
        print(json.dumps({"status": "IAM_SOURCE_UNAVAILABLE", "database_mutated": False}))
        return 2
    try:
        database = kernel_db.get_database()
        if database is None:
            raise RuntimeError("IAM_SOURCE_UNAVAILABLE")
        report = inspect_founder_hr_prerequisites(database, args.tenant_id)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report.get("employer_hr_read_prerequisites_present") is True else 3
    except Exception:
        print(json.dumps({"status": "IAM_SOURCE_UNAVAILABLE", "database_mutated": False}))
        return 2
    finally:
        kernel_db.disconnect_db()


if __name__ == "__main__":
    raise SystemExit(main())

# ARTIFACT: tools/eos/ops/founder_hr_iam_preflight.py
# VERSION: v1.0.0-FOUNDER-HR-READ-ONLY-PREFLIGHT
# AUTHORITY BOUNDARY: Read-only source evidence; no grants, admission, JWT or session issuance.
# TENANT POSTURE: Exact canonical Wilsy employer only.
# FAIL-CLOSED POSTURE: Uncertain authority remains unverifiable.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
