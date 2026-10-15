"""TITLE: WILSY OS System Permission Revocation Command Service.
VERSION: v1.0.0-D12-REVOCATION-COMMAND-SERVICE
AUTHORITY: Ongoing bounded SYSTEM permission revocation command composition.
EPITOME: Requires current revoke-command possession and terminally revokes only privileged_activation:issue.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/system_permission_revocation_command_service.py
COLLABORATION: Current possession resolver, principal repository, D12 policy/evidence, assignment registry.
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.0.0 establishes non-recursive caller-transaction-owned revocation.
COMPLIANCE / SECURITY: Current actor and target; exact assignment lineage and replay.
TENANT BOUNDARY: SYSTEM only.
AUTHORITY BOUNDARY: Cannot revoke command permissions or arbitrary permissions.
FINANCIAL AUTHORITY BOUNDARY: None.
"""
from __future__ import annotations

from typing import Any, Final
from pymongo.client_session import ClientSession
from tools.eos.auth.current_system_permission_possession import CurrentSystemPermissionPossessionResolver
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError, PrincipalAuthorityRepository, PrincipalAuthorityRepositoryError
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.system_permission_assignment import SystemPermissionAssignment, SystemPermissionAssignmentStatus
from tools.eos.auth.system_permission_assignment_registry import SystemPermissionAssignmentRegistry
from tools.eos.auth.system_permission_command_evidence import SystemPermissionCommandEvidence, SystemPermissionCommandOperation
from tools.eos.auth.system_permission_command_policy import REVOKE_COMMAND_PERMISSION, require_ongoing_revocation

VERSION: Final[str] = "v1.0.0-D12-REVOCATION-COMMAND-SERVICE"


class SystemPermissionRevocationCommandError(RuntimeError):
    """Stable fail-closed revocation command composition failure."""
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class SystemPermissionRevocationCommandService:
    """Persist terminal revocation evidence without owning transaction lifecycle."""
    def __init__(self, *, principal_collection: Any, possession_resolver: CurrentSystemPermissionPossessionResolver, assignment_registry: SystemPermissionAssignmentRegistry) -> None:
        if principal_collection is None or type(possession_resolver) is not CurrentSystemPermissionPossessionResolver or type(assignment_registry) is not SystemPermissionAssignmentRegistry:
            raise SystemPermissionRevocationCommandError("REVOCATION_COMMAND_DEPENDENCY_INVALID")
        self._principals = principal_collection
        self._possession = possession_resolver
        self._assignments = assignment_registry

    def revoke(self, evidence: SystemPermissionCommandEvidence, *, session: ClientSession) -> SystemPermissionAssignment:
        """Revoke the sole ongoing revocable permission inside the caller transaction."""
        if session is None or getattr(session, "in_transaction", False) is not True:
            raise SystemPermissionRevocationCommandError("ACTIVE_TRANSACTION_REQUIRED")
        if not isinstance(evidence, SystemPermissionCommandEvidence) or evidence.operation is not SystemPermissionCommandOperation.REVOKE:
            raise SystemPermissionRevocationCommandError("REVOCATION_COMMAND_EVIDENCE_REQUIRED")
        require_ongoing_revocation(evidence.permission_id)
        if self._possession.resolve(principal_id=evidence.actor_principal_id, permission_id=REVOKE_COMMAND_PERMISSION, session=session) is None:
            raise SystemPermissionRevocationCommandError("CURRENT_REVOCATION_COMMAND_AUTHORITY_REQUIRED")
        try:
            target = PrincipalAuthorityRepository.get(evidence.target_principal_id, collection=self._principals, session=session)
        except PrincipalAuthorityNotFoundError as error:
            raise SystemPermissionRevocationCommandError("TARGET_PRINCIPAL_NOT_FOUND") from error
        except PrincipalAuthorityRepositoryError as error:
            raise SystemPermissionRevocationCommandError("TARGET_CURRENTNESS_UNAVAILABLE") from error
        if target.principal_id != evidence.target_principal_id or target.status is not PrincipalStatus.ACTIVE:
            raise SystemPermissionRevocationCommandError("TARGET_PRINCIPAL_NOT_CURRENT")
        history = self._assignments.get_history(evidence.assignment_id, session=session)  # type: ignore[arg-type]
        if not history:
            raise SystemPermissionRevocationCommandError("TARGET_ASSIGNMENT_NOT_FOUND")
        original = history[0]
        if original.principal_id != evidence.target_principal_id or original.permission_id != evidence.permission_id:
            raise SystemPermissionRevocationCommandError("TARGET_ASSIGNMENT_BINDING_INVALID")
        revoked = original.revoke(revoked_by_principal_id=evidence.actor_principal_id, revoked_at=evidence.occurred_at, revocation_evidence_reference=evidence.evidence_reference)
        if len(history) > 1 and history[-1].status is not SystemPermissionAssignmentStatus.REVOKED:
            raise SystemPermissionRevocationCommandError("TARGET_ASSIGNMENT_STATE_INVALID")
        return self._assignments.revoke_or_replay(revoked, revocation_idempotency_key=evidence.idempotency_key, session=session)


__all__ = ["VERSION", "SystemPermissionRevocationCommandError", "SystemPermissionRevocationCommandService"]
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: system_permission_revocation_command_service.py
# VERSION: v1.0.0-D12-REVOCATION-COMMAND-SERVICE
# AUTHORITY BOUNDARY: PRIVILEGED ACTIVATION ISSUE REVOCATION ONLY
# TENANT POSTURE: SYSTEM ONLY
# FAIL-CLOSED POSTURE: CURRENT ACTOR COMMAND + CURRENT TARGET + EXACT LINEAGE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
