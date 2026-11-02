"""Sheriff appointment evidence IAM certificate.

TITLE: WILSY OS Sheriff Appointment Evidence IAM Certificate
VERSION: v1.0.0-L8-SHERIFF-APPOINTMENT-EVIDENCE-IAM-CERT
AUTHORITY: Static permission possession and tenant business-role eligibility only.
EPITOME: Prove only ENTERPRISE_ADMIN plus tenant_admin can admit the Sheriff appointment evidence command.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sheriff_office_appointment_authority_iam.py
"""

from __future__ import annotations

from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.roles import (
    get_permissions_for_roles,
    get_roles_granting_permission,
)
from tools.eos.auth.tenant_authority_policy import (
    DENY,
    ELIGIBLE,
    permission_for_business_role_operation,
    tenant_role_operation_eligibility,
)

PERMISSION = "legal_operations:sheriff_appointment:write"
OPERATION = "legal_sheriff_appointment_write"


def test_permission_is_canonical_and_tenant_scoped() -> None:
    assert permission_metadata(PERMISSION) is not None
    assert permission_for_business_role_operation(OPERATION) == PERMISSION


def test_only_enterprise_admin_has_static_permission_possession() -> None:
    assert get_roles_granting_permission(PERMISSION) == ("ENTERPRISE_ADMIN",)
    assert PERMISSION in get_permissions_for_roles(["ENTERPRISE_ADMIN"])
    for role in (
        "SHERIFF",
        "DEPUTY",
        "LEGAL_PARTNER",
        "LEGAL_ATTORNEY",
        "AUDITOR",
        "SERVICE_WORKER",
    ):
        assert PERMISSION not in get_permissions_for_roles([role])


def test_only_tenant_admin_is_business_eligible_for_appointment_verification() -> None:
    assert tenant_role_operation_eligibility("tenant_admin", OPERATION) == ELIGIBLE
    for business_role in (
        "tenant_owner",
        "tenant_manager",
        "tenant_auditor",
        "tenant_sheriff",
        "tenant_deputy",
        "tenant_legal_partner",
        "tenant_legal_attorney",
        "tenant_legal_client",
    ):
        assert tenant_role_operation_eligibility(business_role, OPERATION) == DENY


# ARTIFACT: test_sheriff_office_appointment_authority_iam.py
# VERSION: v1.0.0-L8-SHERIFF-APPOINTMENT-EVIDENCE-IAM-CERT
# AUTHORITY BOUNDARY: static permission grant and business eligibility only; current possession remains runtime authority
# TENANT POSTURE: exact own-tenant admin admission; no Sheriff/Deputy self-approval
# FAIL-CLOSED POSTURE: every non-admin business role and non-enterprise authorization role denies
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
