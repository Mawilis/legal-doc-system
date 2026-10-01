"""TITLE: WILSY OS Legal Evidence Tenant Authorization Binding Certificate.
VERSION: v1.0.0-L10A2R-C4D6D-A3-A1-LEGAL-EVIDENCE-IAM-BINDING-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS IAM certification only.
EPITOME: Certify that the pre-existing Partner-only Legal Evidence operation is
         bound exactly to its pre-existing canonical TENANT permission.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_evidence_tenant_authorization_binding.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-01.
CHANGELOG:
    2026-10-01 v1.0.0-L10A2R-C4D6D-A3-A1-LEGAL-EVIDENCE-IAM-BINDING-CERT
    establishes direct bounded certification of the exact operation/permission,
    Partner-only business eligibility and Partner-only authorization-role grant.
AUTHORITY BOUNDARY: IAM composition certificate only. It creates no Legal
                    Evidence disownership fact, orphan proof, retention
                    conclusion, legal-hold release, cleanup eligibility,
                    deletion authority or provider mutation authority.
TENANT POSTURE: Exact own-tenant permission/operation vocabulary only.
FAIL-CLOSED POSTURE: Crossed, malformed and unrelated bindings remain denied.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import tools.eos.auth.tenant_authorization as tenant_authorization
from tools.eos.auth.permission_namespace import (
    PermissionDisposition,
    permission_metadata,
)
from tools.eos.auth.roles import get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import (
    DENY,
    ELIGIBLE,
    OPERATIONS,
    TENANT_ROLES,
    permission_for_business_role_operation,
    tenant_role_operation_eligibility,
)


PERMISSION = "legal_operations:evidence:write"
OPERATION = "legal_evidence_write"


def test_exact_operation_permission_binding_is_present_once() -> None:
    """The generic IAM composer binds only the exact certified pair."""
    assert tenant_authorization._BINDINGS[OPERATION] == PERMISSION
    assert (
        sum(
            1
            for operation, permission
            in tenant_authorization._BINDINGS.items()
            if operation == OPERATION and permission == PERMISSION
        )
        == 1
    )


def test_permission_remains_canonical_tenant_nonfinancial_nonselfauthorizing() -> None:
    """Binding reuses the existing permission without broadening semantics."""
    metadata = permission_metadata(PERMISSION)

    assert metadata.disposition is PermissionDisposition.CANONICAL
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.system_assignment_required is False
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False


def test_business_operation_is_partner_only() -> None:
    """Business eligibility remains exactly tenant_legal_partner."""
    assert OPERATION in OPERATIONS
    assert permission_for_business_role_operation(OPERATION) == PERMISSION

    eligible = {
        role
        for role in TENANT_ROLES
        if tenant_role_operation_eligibility(role, OPERATION) == ELIGIBLE
    }

    assert eligible == {"tenant_legal_partner"}

    for role in TENANT_ROLES - {"tenant_legal_partner"}:
        assert tenant_role_operation_eligibility(role, OPERATION) == DENY


def test_authorization_role_grant_is_legal_partner_only() -> None:
    """Static role possession cannot widen beyond LEGAL_PARTNER."""
    assert get_roles_granting_permission(PERMISSION) == ("LEGAL_PARTNER",)


def test_crossed_and_malformed_operation_aliases_do_not_bind() -> None:
    """Nearby aliases cannot manufacture an IAM operation binding."""
    malformed = (
        "legal_evidence",
        "legal_evidence_read",
        "legal_evidence_write ",
        " legal_evidence_write",
        "LEGAL_EVIDENCE_WRITE",
        "legal_evidence_*",
    )

    for operation in malformed:
        assert tenant_authorization._BINDINGS.get(operation) != PERMISSION


def test_no_disownership_or_deletion_authority_is_added() -> None:
    """A3-A1 changes only IAM composition vocabulary."""
    source = __import__(
        "inspect"
    ).getsource(tenant_authorization)

    forbidden = (
        "orphan_proven",
        "provider_delete",
        "delete_authorization",
        "legal_hold_release",
        "retention_satisfied",
    )

    for symbol in forbidden:
        assert symbol not in source


# ARTIFACT: test_legal_evidence_tenant_authorization_binding.py
# VERSION: v1.0.0-L10A2R-C4D6D-A3-A1-LEGAL-EVIDENCE-IAM-BINDING-CERT
# AUTHORITY BOUNDARY: direct IAM binding verification only; no legal disposition authority
# TENANT POSTURE: exact own-tenant Partner-only conjunction
# FAIL-CLOSED POSTURE: unknown, crossed and malformed operation aliases remain non-authorizing
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
