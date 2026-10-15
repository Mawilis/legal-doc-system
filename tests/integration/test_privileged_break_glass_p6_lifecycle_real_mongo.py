"""WILSY OS P7 to P6 terminal lifecycle real-Mongo certificate.

TITLE: Privileged Break-Glass P6 Lifecycle Certificate
VERSION: v1.0.0-P7-P6-BREAK-GLASS-TERMINAL-LIFECYCLE-REAL-MONGO
AUTHORITY: Wilsy OS Sovereign IAM
EPITOME: Prove lawful P7 issuance is exactly revocable through sealed P6 authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_privileged_break_glass_p6_lifecycle_real_mongo.py
COLLABORATION / OWNERSHIP: Composes certified D12, P2, P3, P4, P5-currentness and P6.
CERTIFICATION DATE: 2026-10-15
CHANGELOG: v1.0.0 establishes the complete emergency activation terminal lifecycle.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic references only; no credentials or emergency narrative.
TENANT BOUNDARY: Platform target forbids tenant material throughout the lifecycle.
AUTHORITY BOUNDARY: Executable certificate only; no HTTP, role, token, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively executes finance.
"""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from tools.eos.auth.current_system_permission_possession import CurrentSystemPermissionPossessionResolver
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.privileged_activation_revocation_command_evidence import PRIVILEGED_ACTIVATION_REVOKE_PERMISSION, PrivilegedActivationRevocationCommandEvidence
from tools.eos.auth.privileged_activation_revocation_command_evidence_registry import PrivilegedActivationRevocationCommandEvidenceRegistry
from tools.eos.auth.privileged_activation_revocation_command_service import PrivilegedActivationRevocationCommandService
from tools.eos.auth.privileged_break_glass_command_evidence_registry import PrivilegedBreakGlassCommandEvidenceRegistry
from tools.eos.auth.privileged_break_glass_service import PrivilegedBreakGlassService, PrivilegedBreakGlassServiceError
from tools.eos.auth.privileged_channel_currentness import FactorVerificationStatus, InteractiveFactorVerificationEvent
from tools.eos.auth.privileged_interactive_security_proof import PrivilegedInteractiveProofStatus, PrivilegedInteractiveSecurityProof
from tools.eos.auth.system_permission_assignment import SystemPermissionAssignment
from tools.eos.auth.privileged_eligibility import PrivilegedTargetClass, SOVEREIGN_ARCHITECT
from tests.integration.test_privileged_activation_issuance_service_real_mongo import ASSIGNMENT_COLLECTION, ELIGIBILITY_ID, NOW, PRINCIPAL, PROOF_TENANT, _seed, context as p4_context

APPROVER = "principal-p7-approver"
SUPERVISOR = "principal-p7-supervisor"
BREAK_GLASS = "privileged_activation:break_glass"


def _assignment(principal: str, permission: str, suffix: str) -> SystemPermissionAssignment:
    return SystemPermissionAssignment.assign(assignment_id="assignment-" + suffix, principal_id=principal, permission_id=permission, assigned_by_principal_id="p7-governance", assigned_at=NOW - timedelta(minutes=1), assignment_evidence_reference="evidence-" + suffix)


def _seed_p7(context: dict[str, Any]) -> tuple[SystemPermissionAssignment, SystemPermissionAssignment, SystemPermissionAssignment]:
    _seed(context)
    requester = _assignment(PRINCIPAL, BREAK_GLASS, "p7-requester")
    approver = _assignment(APPROVER, BREAK_GLASS, "p7-approver")
    supervisor = _assignment(SUPERVISOR, PRIVILEGED_ACTIVATION_REVOKE_PERMISSION, "p7-supervisor-revoke")
    with context["client"].start_session() as session:
        with session.start_transaction():
            for principal in (APPROVER, SUPERVISOR):
                PrincipalAuthorityRepository.create(PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 1), context["principals"], session=session)
            context["database"]["users"].insert_one({"user_id": APPROVER, "email": "p7-approver@example.com", "firstName": "P7", "lastName": "Approver", "role": "USER", "permissions": [], "tenantId": PROOF_TENANT, "passwordHash": "synthetic", "credential_revision": 9, "mfaRegistered": True, "hasSignedCovenant": True, "createdAt": NOW.replace(tzinfo=None), "updatedAt": NOW.replace(tzinfo=None)}, session=session)
            context["database"]["sessions"].insert_one({"tenant_id": PROOF_TENANT, "user_id": APPROVER, "session_reference": "session-p7-approver", "expires_at": NOW + timedelta(hours=1)}, session=session)
            context["factor_registry"].create_or_replay(InteractiveFactorVerificationEvent("factor-p7-approver", APPROVER, "session-p7-approver", 9, NOW, FactorVerificationStatus.VERIFIED), recorded_at=NOW, session=session)
            context["proof_registry"].create_or_replay(PrivilegedInteractiveSecurityProof("proof-p7-approver", APPROVER, "factor-p7-approver", NOW, 9, "session-p7-approver", PrivilegedInteractiveProofStatus.VERIFIED, "proof-ref-p7-approver"), status_changed_at=NOW, idempotency_key="proof-idem-p7-approver", session=session)
            for assignment in (requester, approver, supervisor):
                context["assignment_registry"].create_or_replay(assignment, idempotency_key="create-" + assignment.assignment_id, session=session)
    return requester, approver, supervisor


def test_real_p7_activation_is_p6_revocable_terminal_and_nonresurrectable(p4_context: dict[str, Any]) -> None:
    context = p4_context
    _, _, supervisor = _seed_p7(context)
    evidence_registry = PrivilegedBreakGlassCommandEvidenceRegistry(context["database"]["privileged_break_glass_command_evidence"])
    evidence_registry.ensure_indexes()
    possession = CurrentSystemPermissionPossessionResolver(principal_collection=context["principals"], assignment_registry=context["assignment_registry"])
    assurance = getattr(context["issuance_service"], "_interactive_assurance_service")
    service = PrivilegedBreakGlassService(possession_resolver=possession, eligibility_resolver=getattr(context["issuance_service"], "_eligibility_resolver"), interactive_assurance_service=assurance, activation_registry=context["activation_registry"], evidence_registry=evidence_registry, clock=lambda: NOW, assurance_attempt_id_factory=iter(("p7-requester-1", "p7-approver-1", "p7-requester-2", "p7-approver-2")).__next__)
    with context["client"].start_session() as session:
        with session.start_transaction():
            issued = service.issue_interactive(requester_principal_id=PRINCIPAL, approver_principal_id=APPROVER, tenant_id=None, requester_proof_tenant_id=PROOF_TENANT, requester_proof_reference="WILSYPROOFREF-p4-c5", approver_proof_tenant_id=PROOF_TENANT, approver_proof_reference="proof-ref-p7-approver", eligibility_evidence_id=ELIGIBILITY_ID, reason_reference="incident-p7-opaque", effective_until=NOW + timedelta(minutes=10), idempotency_key="p7-lifecycle", session=session)
    assert issued.activation.is_current(at=NOW, tenant_id=None, principal_id=PRINCIPAL, privileged_role_id=SOVEREIGN_ARCHITECT, target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT)

    revocation_registry = PrivilegedActivationRevocationCommandEvidenceRegistry(context["database"]["privileged_activation_revocation_command_evidence"])
    revocation_registry.ensure_indexes()
    revocation_service = PrivilegedActivationRevocationCommandService(possession_resolver=possession, activation_registry=context["activation_registry"], evidence_registry=revocation_registry)
    command = PrivilegedActivationRevocationCommandEvidence.compose(actor_principal_id=SUPERVISOR, actor_permission_id=PRIVILEGED_ACTIVATION_REVOKE_PERMISSION, actor_permission_assignment_id=supervisor.assignment_id, actor_permission_assignment_revision=supervisor.revision, actor_permission_assignment_fingerprint=supervisor.assignment_fingerprint, target_activation_id=issued.activation.activation_id, target_principal_id=PRINCIPAL, target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT.value, target_tenant_id=None, revocation_reason_reference="incident-p7-contained", authorized_at=NOW + timedelta(minutes=1), idempotency_key="p7-lifecycle-revoke")
    with context["client"].start_session() as session:
        with session.start_transaction():
            revoked = revocation_service.revoke(command, session=session)
    assert revoked.activation.status.value == "REVOKED"
    assert context["activation_registry"].resolve_current(tenant_id=None, principal_id=PRINCIPAL, privileged_role_id=SOVEREIGN_ARCHITECT, target_class=PrivilegedTargetClass.PLATFORM_SYSTEM_ROOT, at=NOW + timedelta(minutes=1)) is None
    with context["client"].start_session() as session:
        with session.start_transaction():
            try:
                service.issue_interactive(requester_principal_id=PRINCIPAL, approver_principal_id=APPROVER, tenant_id=None, requester_proof_tenant_id=PROOF_TENANT, requester_proof_reference="WILSYPROOFREF-p4-c5", approver_proof_tenant_id=PROOF_TENANT, approver_proof_reference="proof-ref-p7-approver", eligibility_evidence_id=ELIGIBILITY_ID, reason_reference="incident-p7-opaque", effective_until=NOW + timedelta(minutes=10), idempotency_key="p7-lifecycle", session=session)
            except PrivilegedBreakGlassServiceError as error:
                assert str(error) == "TERMINAL_ACTIVATION_REPLAY_FORBIDDEN"
            else:
                raise AssertionError("terminal activation replay unexpectedly succeeded")
    assert context["database"]["privileged_break_glass_command_evidence"].count_documents({}) == 1
    assert not ({"payments", "refunds", "settlements"} & set(context["database"].list_collection_names()))

# ARTIFACT: test_privileged_break_glass_p6_lifecycle_real_mongo.py
# VERSION: v1.0.0-P7-P6-BREAK-GLASS-TERMINAL-LIFECYCLE-REAL-MONGO
# AUTHORITY BOUNDARY: executable P7 issuance to P6 terminal revocation proof only
# TENANT POSTURE: platform target carries no tenant material
# FAIL-CLOSED POSTURE: revoked activation is noncurrent and cannot be replay-resurrected
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
