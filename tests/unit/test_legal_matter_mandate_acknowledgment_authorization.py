"""TITLE: WILSY OS Firm Mandate Acknowledgment IAM Certificate.
VERSION: v1.0.0-L9B10-P5-MANDATE-ACKNOWLEDGMENT-IAM-CERT
AUTHORITY: Direct certificate of one bounded Legal Operations IAM primitive.
EPITOME: Proves exact operation/permission composition and the existing
         principal, membership, business-role, assignment, tenant and
         fail-closed boundaries without issuing an acknowledgment.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_matter_mandate_acknowledgment_authorization.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-09-27.
CHANGELOG: v1.0.0-L9B10-P5-MANDATE-ACKNOWLEDGMENT-IAM-CERT certifies one
           dedicated own-tenant, non-financial operation and permission for
           all three acknowledgment decisions. It does not issue, persist or
           currentness-evaluate acknowledgments.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic authority doubles only; no secrets,
                             persistence, transport or external IO.
TENANT BOUNDARY: Exact principal, active membership, business role and role
                 assignment are required for the selected tenant.
AUTHORITY BOUNDARY: IAM permission and operation composition only; grant,
                    matter, mandate, engagement and evidence issuance remain
                    separate authorities.
FINANCIAL AUTHORITY BOUNDARY: No financial capability; Kennel EOS remains
                              exclusive for execution and settlement.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.roles import ROLE_PERMISSIONS_MAP, get_roles_granting_permission
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceRegistry,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
from tools.eos.auth.tenant_authority_policy import (
    ELIGIBLE,
    tenant_role_operation_eligibility,
)


TENANT = "tenant-mandate"
PRINCIPAL = "principal-mandate"
OPERATION = "legal_matter_mandate_acknowledgment_write"
PERMISSION = "legal_operations:matter_mandate_acknowledgment:write"
DECISIONS = ("ACKNOWLEDGED", "DECLINED", "REQUIRES_REVIEW")


@dataclass(frozen=True)
class _Principal:
    status: PrincipalStatus


@dataclass(frozen=True)
class _Membership:
    status: TenantMembershipStatus
    revision: int = 3


@dataclass(frozen=True)
class _Assignment:
    role_id: str
    status: RoleAssignmentStatus
    revision: int = 4


class _Reader:
    """Read-only synthetic current-truth authority double."""

    def __init__(
        self,
        *,
        principal: _Principal | None = None,
        membership: _Membership | None = None,
        business_role: str | None = "tenant_legal_partner",
        authorization_role: str | None = "LEGAL_PARTNER",
        authorization_status: RoleAssignmentStatus = RoleAssignmentStatus.ACTIVE,
        membership_tenant: str = TENANT,
        assignment_tenant: str = TENANT,
    ) -> None:
        self.principal = principal or _Principal(PrincipalStatus.ACTIVE)
        self.membership = membership or _Membership(TenantMembershipStatus.ACTIVE)
        self.business_role = business_role
        self.authorization_role = authorization_role
        self.authorization_status = authorization_status
        self.membership_tenant = membership_tenant
        self.assignment_tenant = assignment_tenant
        self.calls: list[tuple[str, ...]] = []

    def resolve(self, *keys: str, **_kwargs: object) -> object:
        self.calls.append(tuple(keys))
        if len(keys) == 1:
            if keys[0] != PRINCIPAL:
                raise PrincipalAuthorityNotFoundError("PRINCIPAL_NOT_FOUND")
            return self.principal
        if len(keys) == 2:
            if (keys[0], keys[1]) != (PRINCIPAL, self.membership_tenant):
                raise TenantMembershipNotFoundError("MEMBERSHIP_NOT_FOUND")
            return self.membership
        if len(keys) == 3:
            principal_id, tenant_id, role_id = keys
            if (principal_id, tenant_id) != (PRINCIPAL, self.assignment_tenant):
                raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")
            if role_id == self.business_role:
                return _Assignment(role_id, RoleAssignmentStatus.ACTIVE)
            if role_id == self.authorization_role:
                return _Assignment(role_id, self.authorization_status)
            raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")
        raise AssertionError("unexpected authority lookup")


def _decision(
    *,
    reader: _Reader | None = None,
    permission: object = PERMISSION,
    operation: object = OPERATION,
    tenant: object = TENANT,
):
    authorities = reader or _Reader()
    return authorize_tenant_operation(
        principal_id=PRINCIPAL,
        tenant_id=tenant,
        permission_id=permission,
        operation=operation,
        principal_repository=authorities,
        membership_repository=authorities,
        business_role_repository=authorities,
        role_assignment_repository=authorities,
    )


def test_operation_permission_and_metadata_are_exact() -> None:
    metadata = permission_metadata(PERMISSION)
    assert OPERATION in __import__(
        "tools.eos.auth.tenant_authority_policy",
        fromlist=["OPERATIONS"],
    ).OPERATIONS
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False
    assert get_roles_granting_permission(PERMISSION) == (
        "LEGAL_ATTORNEY",
        "LEGAL_PARTNER",
    )


@pytest.mark.parametrize("decision", DECISIONS)
def test_all_acknowledgment_decisions_share_one_iam_pair(decision: str) -> None:
    assert decision in DECISIONS
    assert OPERATION == "legal_matter_mandate_acknowledgment_write"
    assert PERMISSION == "legal_operations:matter_mandate_acknowledgment:write"
    assert _decision().authorized is True


@pytest.mark.parametrize(
    ("business_role", "authorization_role"),
    [("tenant_legal_partner", "LEGAL_PARTNER"), ("tenant_legal_attorney", "LEGAL_ATTORNEY")],
)
def test_partner_and_attorney_require_full_conjunction(
    business_role: str,
    authorization_role: str,
) -> None:
    result = _decision(
        reader=_Reader(
            business_role=business_role,
            authorization_role=authorization_role,
        )
    )
    assert result.authorized is True
    assert result.business_role == business_role
    assert result.authorization_role == authorization_role


def test_paralegal_is_not_eligible_even_with_partner_assignment() -> None:
    result = _decision(
        reader=_Reader(
            business_role="tenant_legal_paralegal",
            authorization_role="LEGAL_PARTNER",
        )
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE


def test_role_alone_and_permission_without_eligible_role_fail_closed() -> None:
    role_only = _decision(reader=_Reader(authorization_role=None))
    assert role_only.authorized is False
    assert role_only.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED

    permission_only = _decision(
        reader=_Reader(
            business_role="tenant_legal_paralegal",
            authorization_role="LEGAL_PARTNER",
        )
    )
    assert permission_only.authorized is False
    assert permission_only.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE


def test_unrelated_permission_and_aliases_cannot_cross_bind() -> None:
    result = _decision(permission="legal_operations:conflict_review:write")
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH
    assert _decision(permission="legal_operations:matter_mandate_acknowledgment:*").authorized is False
    assert _decision(operation="legal_matter_mandate_acknowledgment").authorized is False


@pytest.mark.parametrize(
    "status", [PrincipalStatus.SUSPENDED, PrincipalStatus.REVOKED]
)
def test_non_active_principals_are_rejected(status: PrincipalStatus) -> None:
    result = _decision(reader=_Reader(principal=_Principal(status)))
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.PRINCIPAL_INACTIVE


def test_missing_inactive_and_wrong_tenant_membership_are_rejected() -> None:
    inactive = _decision(
        reader=_Reader(
            membership=_Membership(TenantMembershipStatus.SUSPENDED),
        )
    )
    assert inactive.reason is TenantAuthorizationReason.MEMBERSHIP_INACTIVE

    wrong_tenant_reader = _Reader()
    wrong_tenant = _decision(reader=wrong_tenant_reader, tenant="tenant-other")
    assert wrong_tenant.authorized is False
    assert wrong_tenant.reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND
    assert wrong_tenant_reader.calls == [(PRINCIPAL,), (PRINCIPAL, "tenant-other")]


def test_inactive_and_wrong_tenant_assignments_are_rejected() -> None:
    inactive = _decision(
        reader=_Reader(authorization_status=RoleAssignmentStatus.REVOKED)
    )
    assert inactive.authorized is False
    assert inactive.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE

    wrong_tenant_reader = _Reader(assignment_tenant="tenant-other")
    wrong_tenant = _decision(reader=wrong_tenant_reader)
    assert wrong_tenant.authorized is False
    assert wrong_tenant.reason is TenantAuthorizationReason.NO_ACTIVE_TENANT_BUSINESS_ROLE


def test_policy_eligibility_is_non_authorizing_and_paralegal_is_denied() -> None:
    assert tenant_role_operation_eligibility(
        "tenant_legal_partner", OPERATION
    ) == ELIGIBLE
    assert tenant_role_operation_eligibility(
        "tenant_legal_attorney", OPERATION
    ) == ELIGIBLE
    assert tenant_role_operation_eligibility(
        "tenant_legal_paralegal", OPERATION
    ) != ELIGIBLE


class _Session:
    in_transaction = True


class _EvidenceCollection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def find_one(self, _query: object, **_kwargs: object) -> None:
        return None

    def insert_one(self, document: dict[str, object], **_kwargs: object) -> None:
        self.rows.append(document)


def test_authorization_evidence_records_exact_pair_and_identity() -> None:
    authorities = _Reader()
    collection = _EvidenceCollection()
    registry = TenantAuthorizationDecisionEvidenceRegistry(
        cast(Any, collection),
        principal_repository=authorities,
        membership_repository=authorities,
        role_assignment_repository=authorities,
        business_role_repository=authorities,
    )
    evidence = registry.issue(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        operation=OPERATION,
        permission=PERMISSION,
        subject_reference="mandate-grant:synthetic",
        subject_evidence_fingerprint="a" * 128,
        idempotency_key="iam-test-1",
        session=cast(Any, _Session()),
    )
    assert evidence.operation == OPERATION
    assert evidence.permission == PERMISSION
    assert evidence.tenant_id == TENANT
    assert evidence.principal_id == PRINCIPAL
    assert collection.rows[0]["operation"] == OPERATION
    assert collection.rows[0]["permission"] == PERMISSION


def test_iam_surfaces_have_no_subject_issuance_or_transport_dependencies() -> None:
    for relative in (
        "tools/eos/auth/permission_namespace.py",
        "tools/eos/auth/roles.py",
        "tools/eos/auth/tenant_authority_policy.py",
        "tools/eos/auth/tenant_authorization.py",
    ):
        tree = ast.parse(Path(relative).read_text(encoding="utf-8"))
        imported = {
            node.module
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        }
        assert not any(
            module.startswith("tools.eos.legal_operations") for module in imported
        )
        assert not {"requests", "httpx", "pymongo"} & imported


def test_no_legal_role_receives_financial_or_wildcard_authority() -> None:
    for grants in ROLE_PERMISSIONS_MAP.values():
        assert "financial_execution" not in grants
        assert not any("*" in grant for grant in grants)


# ARTIFACT: test_legal_matter_mandate_acknowledgment_authorization.py
# VERSION: v1.0.0-L9B10-P5-MANDATE-ACKNOWLEDGMENT-IAM-CERT
# AUTHORITY BOUNDARY: direct IAM primitive certificate only; no subject issuance.
# TENANT POSTURE: exact active principal/membership/business-role/assignment.
# FAIL-CLOSED POSTURE: malformed, inactive, crossed, unrelated and incomplete
# requests deny without grant, mandate, engagement or transport side effects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
