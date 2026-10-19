"""Transactional partner-controlled practitioner matter binding provisioning.

Relationship evidence only. No content admission, ethical-wall clearance,
waiver, or independent transaction authority.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final, NoReturn

from tools.eos.auth.tenant_authorization import (
    authorize_tenant_operation, TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.role_assignment import RoleAssignmentStatus
from tools.eos.auth.tenant_business_role_authority import (
    BusinessRoleResolution, resolve_current_tenant_business_role,
)
from tools.eos.legal_operations.domain.legal_practitioner_matter_access import (
    LegalPractitionerMatterAccessEvidence,
)
from tools.eos.legal_operations.domain.legal_practitioner_matter_binding import (
    LegalPractitionerMatterBinding, PractitionerMatterBindingStatus,
)
from tools.eos.legal_operations.registry.legal_practitioner_matter_access_registry import get_by_id
from tools.eos.legal_operations.registry.legal_practitioner_matter_access_history_reader import (
    read_practitioner_matter_access_history,
)
from tools.eos.legal_operations.domain.legal_practitioner_matter_access_currentness import (
    LegalPractitionerMatterAccessCurrentnessState,
    project_legal_practitioner_matter_access_currentness,
)
from tools.eos.legal_operations.registry.legal_practitioner_matter_binding_registry import (
    append_binding, read_binding_history,
)
from tools.eos.legal_operations.service.legal_practitioner_matter_access_conflict_provenance import (
    verify_current_conflict_provenance,
)
from tools.eos.legal_operations.orchestration.legal_client_matter_visibility_orchestrator import (
    _case_matter,
)

PERMISSION: Final[str] = "legal_operations:practitioner_matter_binding:provision"
OPERATION: Final[str] = "legal_practitioner_matter_binding_provision"
PRACTITIONER_ROLES: Final[tuple[tuple[str,str],...]] = (
    ("tenant_legal_partner","LEGAL_PARTNER"),
    ("tenant_legal_attorney","LEGAL_ATTORNEY"),
    ("tenant_legal_paralegal","LEGAL_PARALEGAL"),
)

class PractitionerBindingProvisioningDenied(ValueError):
    pass

def _deny(code: str, cause: Exception | None = None) -> NoReturn:
    if cause is not None:
        raise PractitionerBindingProvisioningDenied(code) from cause
    raise PractitionerBindingProvisioningDenied(code)

def _valid_id(value: object) -> bool:
    return (type(value) is str and bool(value)
            and value == value.strip()
            and all(ord(c) >= 32 for c in value))

def _valid_time(value: object) -> bool:
    return (isinstance(value, datetime)
            and value.tzinfo is not None
            and value.utcoffset() is not None)

def _tx(session: Any) -> None:
    if session is None or getattr(session,"in_transaction",False) is not True:
        _deny("P9_PROVISION_TRANSACTION_REQUIRED")

def _partner(actor: str, tenant: str, repos: tuple[Any,Any,Any,Any],
             session: Any) -> None:
    principals,memberships,business,roles=repos
    try:
        decision=authorize_tenant_operation(
            principal_id=actor, tenant_id=tenant,
            permission_id=PERMISSION,operation=OPERATION,
            principal_repository=principals,
            membership_repository=memberships,
            business_role_repository=business,
            role_assignment_repository=roles,session=session,
        )
    except Exception as exc:
        _deny("P9_PROVISION_ACTOR_IAM_UNAVAILABLE",exc)
    if not (
        type(decision) is TenantAuthorizationDecision
        and decision.authorized is True
        and decision.reason is TenantAuthorizationReason.AUTHORIZED
        and decision.business_role=="tenant_legal_partner"
        and decision.authorization_role=="LEGAL_PARTNER"
    ):
        _deny("P9_PROVISION_PARTNER_DENIED")

def _practitioner(target: str,tenant: str,repos: tuple[Any,Any,Any,Any],
                  session: Any) -> None:
    principals,memberships,business,roles=repos
    try:
        principal=principals.resolve(target,session=session)
        if getattr(principal,"status",None) is not PrincipalStatus.ACTIVE:
            _deny("P9_PROVISION_TARGET_INACTIVE")
        membership=memberships.resolve(target,tenant,session=session)
        if getattr(membership,"status",None) is not TenantMembershipStatus.ACTIVE:
            _deny("P9_PROVISION_TARGET_MEMBERSHIP_INACTIVE")
    except PractitionerBindingProvisioningDenied:
        raise
    except Exception as exc:
        _deny("P9_PROVISION_TARGET_IAM_UNAVAILABLE",exc)

    try:
        result=resolve_current_tenant_business_role(
            principal_id=target,tenant_id=tenant,
            repository=business,session=session,
        )
    except Exception as exc:
        _deny("P9_PROVISION_TARGET_ROLE_UNAVAILABLE",exc)
    if result.resolution is not BusinessRoleResolution.RESOLVED:
        _deny("P9_PROVISION_TARGET_ROLE_AMBIGUOUS_OR_DENIED")
    if result.role is None:
        _deny("P9_PROVISION_TARGET_ROLE_INELIGIBLE")
    role_map: dict[str, str] = dict(PRACTITIONER_ROLES)
    authorized_role=role_map.get(result.role)
    if authorized_role is None:
        _deny("P9_PROVISION_TARGET_ROLE_INELIGIBLE")
    try:
        assignment=roles.resolve(target,tenant,authorized_role,session=session)
    except Exception as exc:
        _deny("P9_PROVISION_TARGET_PERMISSION_UNAVAILABLE",exc)
    if getattr(assignment,"status",None) is not RoleAssignmentStatus.ACTIVE:
        _deny("P9_PROVISION_TARGET_PERMISSION_DENIED")

def grant_binding(
    *, authenticated_principal_id: str,tenant_id: str,case_matter_id: str,
    practitioner_principal_id: str,binding_id: str,access_evidence_id: str,
    expected_access_evidence_fingerprint: str,granted_at: datetime,
    client_party_id: str,subject_identity_fingerprint: str,
    principal_repository: Any,membership_repository: Any,
    business_role_repository: Any,role_assignment_repository: Any,
    lifecycle_collection: Any,access_evidence_collection: Any,
    disposition_collection: Any,binding_collection: Any,session: Any,
) -> LegalPractitionerMatterBinding:
    if not all(_valid_id(x) for x in (
        authenticated_principal_id,tenant_id,case_matter_id,
        practitioner_principal_id,binding_id,access_evidence_id,
        expected_access_evidence_fingerprint,client_party_id,
        subject_identity_fingerprint,
    )) or not _valid_time(granted_at):
        _deny("P9_PROVISION_GRANT_INPUT_INVALID")
    _tx(session)
    repos=(principal_repository,membership_repository,
           business_role_repository,role_assignment_repository)
    _partner(authenticated_principal_id,tenant_id,repos,session)
    _practitioner(practitioner_principal_id,tenant_id,repos,session)
    try:
        matter=_case_matter(
            tenant_id=tenant_id,case_matter_id=case_matter_id,
            lifecycle_collection=lifecycle_collection,session=session,
        )
    except Exception as exc:
        _deny("P9_PROVISION_MATTER_UNAVAILABLE",exc)
    if (matter.tenant_id!=tenant_id
        or matter.case_matter_id!=case_matter_id):
        _deny("P9_PROVISION_MATTER_SCOPE_MISMATCH")
    try:
        evidence=get_by_id(
            tenant_id=tenant_id,access_evidence_id=access_evidence_id,
            collection=access_evidence_collection,session=session,
        )
    except Exception as exc:
        _deny("P9_PROVISION_EVIDENCE_UNAVAILABLE",exc)
    if type(evidence) is not LegalPractitionerMatterAccessEvidence:
        _deny("P9_PROVISION_EVIDENCE_MISSING")
    try:
        canonical=LegalPractitionerMatterAccessEvidence.from_dict(
            evidence.to_dict()
        )
    except Exception as exc:
        _deny("P9_PROVISION_EVIDENCE_CORRUPT",exc)
    if not (
        canonical==evidence
        and evidence.fingerprint==expected_access_evidence_fingerprint
        and evidence.tenant_id==tenant_id
        and evidence.case_matter_id==case_matter_id
        and evidence.practitioner_principal_id==practitioner_principal_id
        and evidence.access_evidence_id==access_evidence_id
        and evidence.revision==1
        and evidence.supersedes_fingerprint is None
        and evidence.decision.name=="ALLOW"
        and evidence.effective_from<=granted_at
        and (evidence.effective_until is None
             or granted_at<evidence.effective_until)
    ):
        _deny("P9_PROVISION_EVIDENCE_SCOPE_OR_TIME_DENIED")

    try:
        history=read_practitioner_matter_access_history(
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            practitioner_principal_id=practitioner_principal_id,
            collection=access_evidence_collection,
            session=session,
        )
        finding=project_legal_practitioner_matter_access_currentness(
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            practitioner_principal_id=practitioner_principal_id,
            evaluation_time=granted_at,
            evidence=history,
        )
    except Exception as exc:
        _deny("P9_PROVISION_POLICY_HISTORY_UNAVAILABLE",exc)

    if (
        finding.state is not
            LegalPractitionerMatterAccessCurrentnessState.ALLOW_UNVERIFIED
        or finding.decisive_fingerprints != (evidence.fingerprint,)
        or evidence.fingerprint not in finding.evidence_fingerprints
    ):
        _deny("P9_PROVISION_POLICY_NOT_DECISIVE_CURRENT_ALLOW")

    try:
        verify_current_conflict_provenance(
            evidence=evidence,matter_fingerprint=matter.fingerprint,
            client_party_id=client_party_id,
            subject_identity_fingerprint=subject_identity_fingerprint,
            evaluation_time=granted_at,
            disposition_collection=disposition_collection,session=session,
        )
    except Exception as exc:
        _deny("P9_PROVISION_CONFLICT_PROVENANCE_DENIED",exc)
    try:
        binding=LegalPractitionerMatterBinding.grant(
            binding_id=binding_id,case_matter=matter,
            practitioner_principal_id=practitioner_principal_id,
            granted_by_principal_id=authenticated_principal_id,
            granted_at=granted_at,evidence_reference=access_evidence_id,
        )
        return append_binding(
            binding=binding,collection=binding_collection,session=session
        )
    except Exception as exc:
        _deny("P9_PROVISION_GRANT_WRITE_DENIED",exc)

def revoke_binding(
    *,authenticated_principal_id: str,tenant_id: str,binding_id: str,
    evidence_reference: str,revoked_at: datetime,
    principal_repository: Any,membership_repository: Any,
    business_role_repository: Any,role_assignment_repository: Any,
    binding_collection: Any,session: Any,
) -> LegalPractitionerMatterBinding:
    if not all(_valid_id(x) for x in (
        authenticated_principal_id,tenant_id,binding_id,evidence_reference,
    )) or not _valid_time(revoked_at):
        _deny("P9_PROVISION_REVOKE_INPUT_INVALID")
    _tx(session)
    repos=(principal_repository,membership_repository,
           business_role_repository,role_assignment_repository)
    _partner(authenticated_principal_id,tenant_id,repos,session)
    try:
        history=read_binding_history(
            tenant_id=tenant_id,binding_id=binding_id,
            collection=binding_collection,session=session,
        )
    except Exception as exc:
        _deny("P9_PROVISION_HISTORY_UNAVAILABLE",exc)
    if len(history)!=1:
        _deny("P9_PROVISION_BINDING_NOT_CURRENT")
    current=history[0]
    if (type(current) is not LegalPractitionerMatterBinding
        or current.tenant_id!=tenant_id
        or current.binding_id!=binding_id
        or current.status is not PractitionerMatterBindingStatus.ACTIVE):
        _deny("P9_PROVISION_BINDING_CORRUPT")
    try:
        revoked=current.revoke(
            revoked_by_principal_id=authenticated_principal_id,
            revoked_at=revoked_at,evidence_reference=evidence_reference,
        )
        return append_binding(
            binding=revoked,collection=binding_collection,session=session,
        )
    except Exception as exc:
        _deny("P9_PROVISION_REVOKE_WRITE_DENIED",exc)

__all__=[
    "PERMISSION","OPERATION","PractitionerBindingProvisioningDenied",
    "grant_binding","revoke_binding",
]
# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P6-R7B-P4-R4-R2C
# END OF WILSY OS SOVEREIGN ARTIFACT
