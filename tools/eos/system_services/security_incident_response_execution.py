"""Narrow adapters from approved decisions to canonical EOS security services.

No password, recovery capability, session, or permission mutation is implemented
here. Every execution delegates to the existing canonical service.
"""

from __future__ import annotations

from typing import Any, Final, Iterable

from tools.eos.auth.system_permission_command_evidence import (
    SystemPermissionCommandEvidence,
    SystemPermissionCommandOperation,
)
from tools.eos.auth.system_permission_revocation_command_service import (
    SystemPermissionRevocationCommandService,
)
from tools.eos.system_services.eos_authorizer import SystemServicesEosAuthorizer
from tools.eos.saas.auth.password_reset_service import (
    PasswordResetResult,
    PasswordResetService,
)

from .security_incident_response_decision import (
    SecurityIncidentResponseAction,
    SecurityIncidentResponseDecision,
    SecurityIncidentResponseDecisionStatus,
)

VERSION: Final[str] = "v1.0.0-EOS-INCIDENT-RESPONSE-CANONICAL-EXECUTION"


class SecurityIncidentResponseExecutionError(RuntimeError):
    """Reject unapproved, mismatched, or non-canonical execution requests."""


class SecurityIncidentResponseCanonicalExecutor:
    """Delegate approved decisions to the canonical password and permission services."""

    def __init__(
        self,
        *,
        password_reset_service: PasswordResetService,
        permission_revocation_service: SystemPermissionRevocationCommandService,
        system_services_authorizer: SystemServicesEosAuthorizer,
    ) -> None:
        if type(password_reset_service) is not PasswordResetService:
            raise SecurityIncidentResponseExecutionError("CANONICAL_PASSWORD_RESET_SERVICE_REQUIRED")
        if type(permission_revocation_service) is not SystemPermissionRevocationCommandService:
            raise SecurityIncidentResponseExecutionError("CANONICAL_PERMISSION_REVOCATION_SERVICE_REQUIRED")
        if type(system_services_authorizer) is not SystemServicesEosAuthorizer:
            raise SecurityIncidentResponseExecutionError("CURRENT_PLATFORM_WORKFORCE_AUTHORIZER_REQUIRED")
        self._password_reset = password_reset_service
        self._permission_revocation = permission_revocation_service
        self._authorizer = system_services_authorizer

    @staticmethod
    def _require_approved(
        decision: SecurityIncidentResponseDecision,
        action: SecurityIncidentResponseAction,
    ) -> None:
        if not isinstance(decision, SecurityIncidentResponseDecision):
            raise SecurityIncidentResponseExecutionError("RESPONSE_DECISION_REQUIRED")
        if decision.status is not SecurityIncidentResponseDecisionStatus.APPROVED:
            raise SecurityIncidentResponseExecutionError("APPROVED_RESPONSE_DECISION_REQUIRED")
        if decision.action is not action or decision.decided_at is None:
            raise SecurityIncidentResponseExecutionError("RESPONSE_DECISION_ACTION_MISMATCH")

    def execute_password_reset(
        self,
        decision: SecurityIncidentResponseDecision,
        *,
        recovery_token: str,
        new_password: str,
        context_terms: Iterable[str] | None = None,
    ) -> PasswordResetResult:
        """Delegate only to canonical R10 password reset with its durable capability.

        Approval does not mint or replace the single-use recovery capability;
        PasswordResetService remains the sole credential/session mutation owner.
        Secret values are passed transiently and are not retained on this adapter.
        """
        self._require_approved(decision, SecurityIncidentResponseAction.PASSWORD_RESET)
        return self._password_reset.reset_password(
            tenant_id=decision.tenant_id,
            recovery_token=recovery_token,
            new_password=new_password,
            context_terms=context_terms,
        )

    def execute_system_permission_revocation(
        self,
        decision: SecurityIncidentResponseDecision,
        *,
        evidence: SystemPermissionCommandEvidence,
        session: Any,
    ) -> Any:
        """Delegate exact approved assignment lineage to canonical D12 revocation."""
        self._require_approved(
            decision,
            SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION,
        )
        decided_at = decision.decided_at
        if decided_at is None:
            raise SecurityIncidentResponseExecutionError("APPROVED_RESPONSE_DECISION_REQUIRED")
        if (
            decision.target_assignment_id is None
            or decision.target_permission_id is None
            or not isinstance(evidence, SystemPermissionCommandEvidence)
            or evidence.operation is not SystemPermissionCommandOperation.REVOKE
            or evidence.target_principal_id != decision.target_principal_id
            or evidence.actor_principal_id in {
                decision.requested_by_principal_id,
                decision.decided_by_principal_id,
                decision.target_principal_id,
            }
            or evidence.assignment_id != decision.target_assignment_id
            or evidence.permission_id != decision.target_permission_id
            or evidence.evidence_reference != (
                "security-incident-response-decision:" + decision.decision_id
            )
            or evidence.occurred_at < decided_at
        ):
            raise SecurityIncidentResponseExecutionError(
                "CANONICAL_REVOCATION_EVIDENCE_BINDING_INVALID"
            )
        self._authorizer.require(
            principal_id=evidence.actor_principal_id,
            permission_id="system_services:incident:response:execute",
            session=session,
        )
        return self._permission_revocation.revoke(evidence, session=session)


__all__ = [
    "VERSION",
    "SecurityIncidentResponseExecutionError",
    "SecurityIncidentResponseCanonicalExecutor",
]
