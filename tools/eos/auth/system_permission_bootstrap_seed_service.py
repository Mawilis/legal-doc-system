"""TITLE: WILSY OS System Permission Bootstrap Seed Service.
VERSION: v1.0.0-D12-BOOTSTRAP-SEED-SERVICE
AUTHORITY: Purpose-matched bootstrap seeding of exact SYSTEM command permission.
EPITOME: Converts current bootstrap authority into one durable self-bound command assignment.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/system_permission_bootstrap_seed_service.py
COLLABORATION: Current bootstrap resolver, principal repository, D12 policy/evidence, assignment registry.
CERTIFICATION DATE: 2026-10-14
CHANGELOG: v1.0.0 establishes caller-transaction-owned assignment/revocation command self-seeding.
COMPLIANCE / SECURITY: Exact current principal and bootstrap bindings; no wildcard or arbitrary grant.
TENANT BOUNDARY: SYSTEM only; no tenant authority.
AUTHORITY BOUNDARY: Seeds only purpose-matched command authority to the bootstrap target itself.
FINANCIAL AUTHORITY BOUNDARY: None.
"""
from __future__ import annotations

from typing import Any, Final
from pymongo.client_session import ClientSession

from tools.eos.auth.current_system_permission_bootstrap_authority import CurrentSystemPermissionBootstrapAuthorityResolver
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError, PrincipalAuthorityRepository, PrincipalAuthorityRepositoryError
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.system_permission_assignment import SystemPermissionAssignment
from tools.eos.auth.system_permission_assignment_registry import SystemPermissionAssignmentRegistry
from tools.eos.auth.system_permission_command_evidence import SystemPermissionCommandEvidence, SystemPermissionCommandOperation
from tools.eos.auth.system_permission_command_policy import require_bootstrap_seed

VERSION: Final[str] = "v1.0.0-D12-BOOTSTRAP-SEED-SERVICE"


class SystemPermissionBootstrapSeedError(RuntimeError):
    """Stable fail-closed bootstrap seed composition failure."""
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class SystemPermissionBootstrapSeedService:
    """Persist one exact command assignment without owning session or transaction lifecycle."""
    def __init__(self, *, principal_collection: Any, bootstrap_resolver: CurrentSystemPermissionBootstrapAuthorityResolver, assignment_registry: SystemPermissionAssignmentRegistry) -> None:
        if principal_collection is None or type(bootstrap_resolver) is not CurrentSystemPermissionBootstrapAuthorityResolver or type(assignment_registry) is not SystemPermissionAssignmentRegistry:
            raise SystemPermissionBootstrapSeedError("BOOTSTRAP_SEED_DEPENDENCY_INVALID")
        self._principals = principal_collection
        self._bootstrap = bootstrap_resolver
        self._assignments = assignment_registry

    def seed(self, evidence: SystemPermissionCommandEvidence, *, session: ClientSession) -> SystemPermissionAssignment:
        """Seed purpose-matched command authority to the exact current bootstrap target."""
        if session is None or getattr(session, "in_transaction", False) is not True:
            raise SystemPermissionBootstrapSeedError("ACTIVE_TRANSACTION_REQUIRED")
        if not isinstance(evidence, SystemPermissionCommandEvidence) or evidence.operation is not SystemPermissionCommandOperation.BOOTSTRAP_SEED:
            raise SystemPermissionBootstrapSeedError("BOOTSTRAP_SEED_EVIDENCE_REQUIRED")
        if evidence.actor_principal_id != evidence.target_principal_id:
            raise SystemPermissionBootstrapSeedError("BOOTSTRAP_SELF_SEED_REQUIRED")
        require_bootstrap_seed(evidence.bootstrap_purpose, evidence.permission_id)  # type: ignore[arg-type]
        bootstrap = self._bootstrap.resolve(principal_id=evidence.actor_principal_id, purpose=evidence.bootstrap_purpose, session=session)  # type: ignore[arg-type]
        if bootstrap is None:
            raise SystemPermissionBootstrapSeedError("CURRENT_BOOTSTRAP_REQUIRED")
        if bootstrap.bootstrap_id != evidence.bootstrap_id or bootstrap.actor_principal_id != evidence.target_principal_id:
            raise SystemPermissionBootstrapSeedError("BOOTSTRAP_BINDING_INVALID")
        try:
            target = PrincipalAuthorityRepository.get(evidence.target_principal_id, collection=self._principals, session=session)
        except PrincipalAuthorityNotFoundError as error:
            raise SystemPermissionBootstrapSeedError("TARGET_PRINCIPAL_NOT_FOUND") from error
        except PrincipalAuthorityRepositoryError as error:
            raise SystemPermissionBootstrapSeedError("TARGET_CURRENTNESS_UNAVAILABLE") from error
        if target.principal_id != evidence.target_principal_id or target.status is not PrincipalStatus.ACTIVE:
            raise SystemPermissionBootstrapSeedError("TARGET_PRINCIPAL_NOT_CURRENT")
        assignment = SystemPermissionAssignment.assign(assignment_id=evidence.derived_assignment_id(), principal_id=evidence.target_principal_id, permission_id=evidence.permission_id, assigned_by_principal_id=evidence.actor_principal_id, assigned_at=evidence.occurred_at, assignment_evidence_reference=evidence.evidence_reference)
        return self._assignments.create_or_replay(assignment, idempotency_key=evidence.idempotency_key, session=session)


__all__ = ["VERSION", "SystemPermissionBootstrapSeedError", "SystemPermissionBootstrapSeedService"]
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: system_permission_bootstrap_seed_service.py
# VERSION: v1.0.0-D12-BOOTSTRAP-SEED-SERVICE
# AUTHORITY BOUNDARY: PURPOSE-MATCHED SELF-SEED ONLY
# TENANT POSTURE: SYSTEM ONLY
# FAIL-CLOSED POSTURE: CURRENT BOOTSTRAP + CURRENT TARGET + CALLER TRANSACTION
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
