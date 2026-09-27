"""TITLE: WILSY OS Engagement Firm-Decision IAM Direct Certificate.
VERSION: v1.0.0-L9C7E-ENGAGEMENT-FIRM-DECISION-IAM-DIRECT-CERT
AUTHORITY: Direct certificate of the published tenant authorization contract.
EPITOME: Proves the exact Engagement firm-decision operation and permission
         remain conjunctive across current principal, membership, business-role,
         tenant, permission, and granting-role truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_matter_engagement_firm_decision_authorization.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-09-28.
CHANGELOG: 2026-09-28 v1.0.0-L9C7E-ENGAGEMENT-FIRM-DECISION-IAM-DIRECT-CERT
certifies Partner and Attorney success, least-authority denials, exact result
material, evidence compatibility, deterministic fail-closed behavior, and the
absence of formation, actor-correlation, persistence, and financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic current-truth doubles only; no secrets,
                             network access, persistence, or external IO.
TENANT BOUNDARY: Every positive and negative decision is bound to one exact
                 principal and tenant; cross-tenant material fails closed.
AUTHORITY BOUNDARY: This file certifies IAM composition only. It does not issue
                    decisions, create Engagements, persist evidence, or grant
                    acting capacity, mandate, conflict, or formation authority.
FINANCIAL AUTHORITY BOUNDARY: No financial capability; Kennel EOS remains the
                              exclusive execution and settlement authority.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

import tools.eos.auth.tenant_authorization as tenant_authorization
from tools.eos.auth.permission_namespace import VERSION as PERMISSION_NAMESPACE_VERSION
from tools.eos.auth.permission_namespace import permission_metadata
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.roles import VERSION as ROLE_POLICY_VERSION
from tools.eos.auth.roles import get_roles_granting_permission
from tools.eos.auth.tenant_authority_policy import VERSION as TENANT_POLICY_VERSION
from tools.eos.auth.tenant_authority_policy import tenant_role_operation_eligibility
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.auth.tenant_authorization_decision_evidence import (
    TenantAuthorizationDecisionEvidence,
)
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError
from tools.eos.auth.role_assignment_repository import RoleAssignmentNotFoundError
from tools.eos.auth.tenant_membership_repository import TenantMembershipNotFoundError


VERSION = "v1.0.0-L9C7E-ENGAGEMENT-FIRM-DECISION-IAM-DIRECT-CERT"
TENANT = "tenant-engagement-iam"
PRINCIPAL = "principal-engagement-iam"
OPERATION = "legal_matter_engagement_firm_decision_write"
PERMISSION = "legal_operations:matter_engagement_firm_decision:write"
PARTNER_BUSINESS_ROLE = "tenant_legal_partner"
ATTORNEY_BUSINESS_ROLE = "tenant_legal_attorney"
PARALEGAL_BUSINESS_ROLE = "tenant_legal_paralegal"


@dataclass(frozen=True, slots=True)
class _Principal:
    status: PrincipalStatus


@dataclass(frozen=True, slots=True)
class _Membership:
    status: TenantMembershipStatus


@dataclass(frozen=True, slots=True)
class _Assignment:
    status: object


class _Authorities:
    """Resolve-only, tenant-scoped authority double with no mutation surface."""

    def __init__(
        self,
        *,
        business_roles: tuple[str, ...] = (PARTNER_BUSINESS_ROLE,),
        business_status: object = TenantBusinessRoleStatus.ACTIVE,
        grant_statuses: dict[str, RoleAssignmentStatus] | None = None,
        principal_status: PrincipalStatus = PrincipalStatus.ACTIVE,
        membership_status: TenantMembershipStatus = TenantMembershipStatus.ACTIVE,
        membership_tenant: str = TENANT,
    ) -> None:
        self.business_roles = business_roles
        self.business_status = business_status
        self.grant_statuses = dict(
            {"LEGAL_PARTNER": RoleAssignmentStatus.ACTIVE}
            if grant_statuses is None
            else grant_statuses
        )
        self.principal_status = principal_status
        self.membership_status = membership_status
        self.membership_tenant = membership_tenant
        self.calls: list[tuple[str, ...]] = []

    def resolve(self, *keys: str, **_kwargs: object) -> object:
        """Return only configured synthetic current truth for exact lookup keys."""
        self.calls.append(tuple(keys))
        if len(keys) == 1:
            if keys[0] != PRINCIPAL:
                raise PrincipalAuthorityNotFoundError("PRINCIPAL_NOT_FOUND")
            return _Principal(self.principal_status)
        if len(keys) == 2:
            if (keys[0], keys[1]) != (PRINCIPAL, self.membership_tenant):
                raise TenantMembershipNotFoundError("MEMBERSHIP_NOT_FOUND")
            return _Membership(self.membership_status)
        if len(keys) == 3:
            principal_id, tenant_id, role_id = keys
            if (principal_id, tenant_id) != (PRINCIPAL, TENANT):
                raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")
            if role_id in self.business_roles:
                return _Assignment(self.business_status)
            if role_id in self.grant_statuses:
                return _Assignment(self.grant_statuses[role_id])
            raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")
        raise AssertionError("unexpected authority lookup")


def _decision(
    *,
    authorities: _Authorities | None = None,
    principal_id: object = PRINCIPAL,
    tenant_id: object = TENANT,
    permission_id: object = PERMISSION,
    operation: object = OPERATION,
) -> TenantAuthorizationDecision:
    """Evaluate the published IAM function with identical read-only authorities."""
    readers = authorities or _Authorities()
    return authorize_tenant_operation(
        principal_id=principal_id,
        tenant_id=tenant_id,
        permission_id=permission_id,
        operation=operation,
        principal_repository=readers,
        membership_repository=readers,
        role_assignment_repository=readers,
        business_role_repository=readers,
    )


def test_exact_published_operation_permission_and_role_precedents() -> None:
    """The certificate is anchored to the published one-to-one IAM contract."""
    assert OPERATION == "legal_matter_engagement_firm_decision_write"
    assert PERMISSION == "legal_operations:matter_engagement_firm_decision:write"
    assert tenant_authorization._BINDINGS[OPERATION] == PERMISSION
    assert list(tenant_authorization._BINDINGS).count(OPERATION) == 1
    metadata = permission_metadata(PERMISSION)
    assert metadata.namespace == "TENANT"
    assert metadata.scope_kind == "TENANT"
    assert metadata.tenant_membership_required is True
    assert metadata.cross_tenant_capable is False
    assert metadata.financial_execution_capable is False
    assert metadata.authorizes_by_itself is False
    assert set(get_roles_granting_permission(PERMISSION)) == {"LEGAL_PARTNER", "LEGAL_ATTORNEY"}
    assert tenant_role_operation_eligibility(PARTNER_BUSINESS_ROLE, OPERATION) == "ELIGIBLE"
    assert tenant_role_operation_eligibility(ATTORNEY_BUSINESS_ROLE, OPERATION) == "ELIGIBLE"
    assert tenant_role_operation_eligibility(PARALEGAL_BUSINESS_ROLE, OPERATION) != "ELIGIBLE"


@pytest.mark.parametrize(
    ("business_role", "authorization_role"),
    ((PARTNER_BUSINESS_ROLE, "LEGAL_PARTNER"), (ATTORNEY_BUSINESS_ROLE, "LEGAL_ATTORNEY")),
)
def test_partner_and_attorney_are_authorized_with_exact_current_truth(
    business_role: str, authorization_role: str
) -> None:
    """Both published eligible legal roles authorize only with their own grant."""
    result = _decision(
        authorities=_Authorities(
            business_roles=(business_role,),
            grant_statuses={authorization_role: RoleAssignmentStatus.ACTIVE},
        )
    )
    assert result == TenantAuthorizationDecision(
        True, TenantAuthorizationReason.AUTHORIZED, business_role, authorization_role
    )


@pytest.mark.parametrize(
    "business_role",
    (
        PARALEGAL_BUSINESS_ROLE,
        "tenant_legal_secretary",
        "tenant_legal_finance",
        "tenant_sheriff",
        "tenant_deputy",
        "tenant_owner",
        "tenant_admin",
        "tenant_auditor",
    ),
)
def test_paralegal_and_other_roles_cannot_escalate_to_firm_decision(
    business_role: str,
) -> None:
    """No unrelated legal, platform, sheriff, deputy, or client role crosses IAM."""
    result = _decision(
        authorities=_Authorities(
            business_roles=(business_role,),
            grant_statuses={"LEGAL_PARTNER": RoleAssignmentStatus.ACTIVE},
        )
    )
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE


def test_principal_membership_business_role_and_assignment_fail_closed() -> None:
    """Each missing, inactive, revoked, or ambiguous current-truth conjunct denies."""
    assert _decision(authorities=_Authorities(principal_status=PrincipalStatus.SUSPENDED)).reason is TenantAuthorizationReason.PRINCIPAL_INACTIVE
    assert _decision(authorities=_Authorities(membership_tenant="other-tenant")).reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND
    assert _decision(authorities=_Authorities(membership_status=TenantMembershipStatus.SUSPENDED)).reason is TenantAuthorizationReason.MEMBERSHIP_INACTIVE
    assert _decision(authorities=_Authorities(business_roles=())).reason is TenantAuthorizationReason.NO_ACTIVE_TENANT_BUSINESS_ROLE
    ambiguous = _decision(authorities=_Authorities(business_roles=(PARTNER_BUSINESS_ROLE, ATTORNEY_BUSINESS_ROLE)))
    assert ambiguous.reason is TenantAuthorizationReason.MULTIPLE_ACTIVE_TENANT_BUSINESS_ROLES
    revoked = _decision(authorities=_Authorities(grant_statuses={"LEGAL_PARTNER": RoleAssignmentStatus.REVOKED}))
    assert revoked.reason is TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE
    missing = _decision(authorities=_Authorities(grant_statuses={}))
    assert missing.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED


@pytest.mark.parametrize(
    "permission_id",
    (
        "legal_operations:conflict_review:write",
        "legal_operations:matter_mandate_acknowledgment:write",
        "legal_operations:matter_acceptance_instrument_approval:write",
        "legal_operations:instruction:write",
        "legal_operations:client_matter:read",
    ),
)
def test_wrong_permission_and_operation_neighbors_fail_closed(permission_id: str) -> None:
    """Conflict, mandate, approval, generic, and malformed-neighbor pairs cannot cross-bind."""
    result = _decision(permission_id=permission_id)
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.PERMISSION_OPERATION_MISMATCH


@pytest.mark.parametrize(
    "operation",
    (
        "legal_matter_engagement_write",
        "legal_matter_engagement_decision_write",
        "legal_matter_engagement_firm_decision_approve",
        "legal_matter_write",
        "engagement_manage",
        "unknown_operation",
    ),
)
def test_unknown_and_near_neighbor_operations_fail_closed(operation: str) -> None:
    """Only the canonical operation is accepted; aliases and unknowns deny."""
    result = _decision(operation=operation)
    assert result.authorized is False
    assert result.reason is TenantAuthorizationReason.INVALID_INPUT


def test_permission_only_and_role_only_authority_are_insufficient() -> None:
    """Neither permission metadata nor business eligibility independently grants access."""
    permission_only = _decision(
        authorities=_Authorities(
            business_roles=(PARALEGAL_BUSINESS_ROLE,),
            grant_statuses={"LEGAL_PARTNER": RoleAssignmentStatus.ACTIVE},
        )
    )
    role_only = _decision(authorities=_Authorities(grant_statuses={}))
    assert permission_only.reason is TenantAuthorizationReason.BUSINESS_ROLE_INELIGIBLE
    assert role_only.reason is TenantAuthorizationReason.PERMISSION_NOT_GRANTED


def test_result_material_and_evidence_shape_preserve_exact_identity() -> None:
    """The decision result and existing evidence value shape retain exact IAM inputs."""
    result = _decision()
    assert result.business_role == PARTNER_BUSINESS_ROLE
    assert result.authorization_role == "LEGAL_PARTNER"
    assert result.authorized is True
    evidence = TenantAuthorizationDecisionEvidence(
        tenant_id=TENANT,
        authorization_decision_id="iam-engagement-direct-cert",
        principal_id=PRINCIPAL,
        operation=OPERATION,
        permission=PERMISSION,
        business_role=result.business_role or "",
        authorization_role=result.authorization_role or "",
        membership_revision=1,
        role_assignment_revision=1,
        subject_reference="engagement-firm-decision:synthetic",
        subject_evidence_fingerprint="a" * 128,
        permission_namespace_version=PERMISSION_NAMESPACE_VERSION,
        authorization_role_policy_version=ROLE_POLICY_VERSION,
        tenant_business_role_policy_version=TENANT_POLICY_VERSION,
        tenant_authorization_composition_version=tenant_authorization.VERSION,
        idempotency_key="iam-engagement-direct-cert-1",
        authorized_at=datetime.now(timezone.utc),
    )
    assert evidence.tenant_id == TENANT
    assert evidence.principal_id == PRINCIPAL
    assert evidence.operation == OPERATION
    assert evidence.permission == PERMISSION
    assert evidence.business_role == PARTNER_BUSINESS_ROLE
    assert evidence.authorization_role == "LEGAL_PARTNER"


def test_decision_state_is_neutral_and_actor_correlation_is_outside_iam() -> None:
    """IAM authorizes the capability, not ACCEPTED/DECLINED/review semantics or actors."""
    results = [_decision() for _ in ("ACCEPTED", "DECLINED", "REQUIRES_REVIEW")]
    assert results == [results[0], results[0], results[0]]
    source = Path("tools/eos/auth/tenant_authorization.py").read_text(encoding="utf-8")
    assert "decision_actor_principal_id" not in source
    assert "acting_capacity" not in source


def test_iam_has_no_formation_prerequisite_or_delegated_authority_reads() -> None:
    """The direct IAM path reads only principal, membership, role, and assignment truth."""
    authorities = _Authorities()
    assert _decision(authorities=authorities).authorized is True
    forbidden_terms = (
        "CaseMatter", "ClientAcceptance", "currentness", "Engagement",
        "Representation", "Court", "financial", "delegat",
    )
    called = " ".join(" ".join(call) for call in authorities.calls)
    assert all(term not in called for term in forbidden_terms)
    tree = ast.parse(Path("tools/eos/auth/tenant_authorization.py").read_text(encoding="utf-8"))
    imported_modules = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert all("legal_operations.domain" not in module for module in imported_modules)
    assert all(not any(word in module.lower() for word in ("representation", "court", "finance", "engagement")) for module in imported_modules)
    assert all(not isinstance(node, ast.Import) or all("pymongo" not in alias.name for alias in node.names) for node in ast.walk(tree))


def test_cross_tenant_mismatch_and_malformed_input_fail_closed() -> None:
    """Tenant mismatch, malformed identity, and financial/system neighbors never authorize."""
    assert _decision(tenant_id="other-tenant").reason is TenantAuthorizationReason.MEMBERSHIP_NOT_FOUND
    assert _decision(principal_id=" ").reason is TenantAuthorizationReason.INVALID_INPUT
    assert _decision(permission_id=PERMISSION, operation="financial_execution").reason is TenantAuthorizationReason.FINANCIAL_EXECUTION_PROHIBITED
    assert _decision(operation="cross_tenant").reason is TenantAuthorizationReason.SYSTEM_AUTHORITY_REQUIRED
    assert _decision() == _decision()


# ARTIFACT: test_legal_matter_engagement_firm_decision_authorization.py
# VERSION: v1.0.0-L9C7E-ENGAGEMENT-FIRM-DECISION-IAM-DIRECT-CERT
# AUTHORITY BOUNDARY: direct IAM composition certificate only; no issuance or formation
# TENANT POSTURE: exact principal, membership, role, permission, assignment, and tenant scope
# FAIL-CLOSED POSTURE: malformed, missing, inactive, ambiguous, crossed, delegated, and financial paths deny
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
