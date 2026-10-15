"""TITLE: WILSY OS System Permission Bootstrap Issuance Service.
VERSION: v1.0.0-P4-R4-D11-R5-BOOTSTRAP-ISSUANCE-SERVICE
AUTHORITY: Composition of current creator, signed creation trust and persistence.
EPITOME: Issues only closed bootstrap command-authority seed evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/system_permission_bootstrap_issuance_service.py
COLLABORATION: PrincipalAuthorityRepository, D11 verifier/domain/registry.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0 establishes caller-transaction-owned exact issuance/replay.
COMPLIANCE / SECURITY: POPIA 19; GDPR 32; SOC2 CC7.2; secret-free evidence.
AUTHORITY BOUNDARY: No normal permission assignment, activation, break glass or finance.
"""
from __future__ import annotations
from datetime import datetime
from typing import Any, Final
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityNotFoundError, PrincipalAuthorityRepository, PrincipalAuthorityRepositoryError
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.system_permission_bootstrap_authority import SystemPermissionBootstrapAuthority
from tools.eos.auth.system_permission_bootstrap_authority_registry import SystemPermissionBootstrapAuthorityRegistry
from tools.eos.auth.system_permission_bootstrap_creation_authorization import SystemPermissionBootstrapCreationAuthorization, VerifiedSystemPermissionBootstrapCreationAuthorization, verify_system_permission_bootstrap_creation_authorization
from tools.eos.auth.system_permission_bootstrap_creation_trust import SystemPermissionBootstrapCreationTrustRoot

VERSION: Final[str] = "v1.0.0-P4-R4-D11-R5-BOOTSTRAP-ISSUANCE-SERVICE"
class SystemPermissionBootstrapIssuanceError(RuntimeError):
    """Fail-closed issuance composition failure with stable code."""
    def __init__(self, code: str) -> None: super().__init__(code); self.code = code

class SystemPermissionBootstrapIssuanceService:
    """Compose existing sovereign authorities without owning transaction lifecycle."""
    def __init__(self, *, principal_collection: Any, bootstrap_registry: SystemPermissionBootstrapAuthorityRegistry, trust_root: SystemPermissionBootstrapCreationTrustRoot) -> None:
        if principal_collection is None or bootstrap_registry is None or not isinstance(trust_root, SystemPermissionBootstrapCreationTrustRoot): raise SystemPermissionBootstrapIssuanceError("ISSUANCE_DEPENDENCY_INVALID")
        self._principals = principal_collection; self._registry = bootstrap_registry; self._trust_root = trust_root
    def issue(self, authorization: SystemPermissionBootstrapCreationAuthorization, *, now: datetime, session: object) -> SystemPermissionBootstrapAuthority:
        """Issue or replay one exact bootstrap authority inside caller transaction."""
        if session is None or getattr(session, "in_transaction", False) is not True: raise SystemPermissionBootstrapIssuanceError("ACTIVE_TRANSACTION_REQUIRED")
        verified: VerifiedSystemPermissionBootstrapCreationAuthorization = verify_system_permission_bootstrap_creation_authorization(authorization, self._trust_root, now=now)
        envelope = verified.authorization
        try: principal = PrincipalAuthorityRepository.get(envelope.creator_principal_id, collection=self._principals, session=session)  # type: ignore[arg-type]
        except PrincipalAuthorityNotFoundError as error: raise SystemPermissionBootstrapIssuanceError("CREATOR_PRINCIPAL_NOT_FOUND") from error
        except PrincipalAuthorityRepositoryError as error: raise SystemPermissionBootstrapIssuanceError("CREATOR_PRINCIPAL_CURRENTNESS_UNAVAILABLE") from error
        if principal.principal_id != envelope.creator_principal_id or principal.status is not PrincipalStatus.ACTIVE: raise SystemPermissionBootstrapIssuanceError("CREATOR_PRINCIPAL_NOT_CURRENT")
        authority = SystemPermissionBootstrapAuthority.issue(bootstrap_id=envelope.bootstrap_id, actor_principal_id=envelope.target_principal_id, purpose=envelope.bootstrap_purpose, evidence_reference=envelope.evidence_reference, issued_at=envelope.issued_at)
        return self._registry.create_or_replay(authority, idempotency_key=envelope.idempotency_key, session=session)

__all__ = ["VERSION", "SystemPermissionBootstrapIssuanceError", "SystemPermissionBootstrapIssuanceService"]
# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: system_permission_bootstrap_issuance_service.py
# VERSION: v1.0.0-P4-R4-D11-R5-BOOTSTRAP-ISSUANCE-SERVICE
# TRANSACTION / SESSION OWNERSHIP: CALLER
# PERMISSION ASSIGNMENT / ACTIVATION / BREAK GLASS / FINANCE: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
