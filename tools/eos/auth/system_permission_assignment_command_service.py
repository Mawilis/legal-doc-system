"""TITLE: WILSY OS System Permission Assignment Command Service.
VERSION: v1.1.0-L10A2R-C4D7-RECONCILIATION-READ-DELEGATION
AUTHORITY: Ongoing bounded SYSTEM permission assignment command composition.
EPITOME: Requires current write-command possession and delegates only exact source-policy allowlisted non-command SYSTEM permissions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/system_permission_assignment_command_service.py
COLLABORATION: Current possession resolver, principal repository, D12 policy/evidence, assignment registry.
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.1.0-L10A2R-C4D7-RECONCILIATION-READ-DELEGATION documents the source policy's exact allowlist extension for
    legal_operations:evidence_provider_reconciliation:read. Command permissions
    remain non-delegable; the service still creates no authority outside policy.
COMPLIANCE / SECURITY: Current actor and target; exact policy; immutable evidence.
TENANT BOUNDARY: SYSTEM only.
AUTHORITY BOUNDARY: Cannot assign command permissions or arbitrary permissions.
FINANCIAL AUTHORITY BOUNDARY: None.
"""
from __future__ import annotations

from typing import Any, Final
from pymongo.client_session import ClientSession
from tools.eos.auth.current_system_permission_possession import CurrentSystemPermissionPossessionResolver
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError, PrincipalAuthorityRepository, PrincipalAuthorityRepositoryError
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.system_permission_assignment import SystemPermissionAssignment
from tools.eos.auth.system_permission_assignment_registry import SystemPermissionAssignmentRegistry
from tools.eos.auth.system_permission_command_evidence import SystemPermissionCommandEvidence, SystemPermissionCommandOperation
from tools.eos.auth.system_permission_command_policy import ASSIGN_COMMAND_PERMISSION, require_ongoing_assignment

VERSION: Final[str] = "v1.1.0-L10A2R-C4D7-RECONCILIATION-READ-DELEGATION"


class SystemPermissionAssignmentCommandError(RuntimeError):
    """Stable fail-closed assignment command composition failure."""
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class SystemPermissionAssignmentCommandService:
    """Create bounded assignment evidence without transaction lifecycle ownership."""
    def __init__(self, *, principal_collection: Any, possession_resolver: CurrentSystemPermissionPossessionResolver, assignment_registry: SystemPermissionAssignmentRegistry) -> None:
        if principal_collection is None or type(possession_resolver) is not CurrentSystemPermissionPossessionResolver or type(assignment_registry) is not SystemPermissionAssignmentRegistry:
            raise SystemPermissionAssignmentCommandError("ASSIGNMENT_COMMAND_DEPENDENCY_INVALID")
        self._principals = principal_collection
        self._possession = possession_resolver
        self._assignments = assignment_registry

    def assign(self, evidence: SystemPermissionCommandEvidence, *, session: ClientSession) -> SystemPermissionAssignment:
        """Assign one source-policy allowlisted permission inside the caller transaction."""
        if session is None or getattr(session, "in_transaction", False) is not True:
            raise SystemPermissionAssignmentCommandError("ACTIVE_TRANSACTION_REQUIRED")
        if not isinstance(evidence, SystemPermissionCommandEvidence) or evidence.operation is not SystemPermissionCommandOperation.ASSIGN:
            raise SystemPermissionAssignmentCommandError("ASSIGNMENT_COMMAND_EVIDENCE_REQUIRED")
        require_ongoing_assignment(evidence.permission_id)
        if self._possession.resolve(principal_id=evidence.actor_principal_id, permission_id=ASSIGN_COMMAND_PERMISSION, session=session) is None:
            raise SystemPermissionAssignmentCommandError("CURRENT_ASSIGNMENT_COMMAND_AUTHORITY_REQUIRED")
        try:
            target = PrincipalAuthorityRepository.get(evidence.target_principal_id, collection=self._principals, session=session)
        except PrincipalAuthorityNotFoundError as error:
            raise SystemPermissionAssignmentCommandError("TARGET_PRINCIPAL_NOT_FOUND") from error
        except PrincipalAuthorityRepositoryError as error:
            raise SystemPermissionAssignmentCommandError("TARGET_CURRENTNESS_UNAVAILABLE") from error
        if target.principal_id != evidence.target_principal_id or target.status is not PrincipalStatus.ACTIVE:
            raise SystemPermissionAssignmentCommandError("TARGET_PRINCIPAL_NOT_CURRENT")
        assignment = SystemPermissionAssignment.assign(assignment_id=evidence.derived_assignment_id(), principal_id=evidence.target_principal_id, permission_id=evidence.permission_id, assigned_by_principal_id=evidence.actor_principal_id, assigned_at=evidence.occurred_at, assignment_evidence_reference=evidence.evidence_reference)
        return self._assignments.create_or_replay(assignment, idempotency_key=evidence.idempotency_key, session=session)


__all__ = ["VERSION", "SystemPermissionAssignmentCommandError", "SystemPermissionAssignmentCommandService"]
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: system_permission_assignment_command_service.py
# VERSION: v1.1.0-L10A2R-C4D7-RECONCILIATION-READ-DELEGATION
# AUTHORITY BOUNDARY: PRIVILEGED ACTIVATION ISSUE ASSIGNMENT ONLY
# TENANT POSTURE: SYSTEM ONLY
# FAIL-CLOSED POSTURE: CURRENT ACTOR COMMAND + CURRENT TARGET + CLOSED POLICY
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
