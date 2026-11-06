"""Narrow adapters from approved decisions to canonical EOS security services.

No password, recovery capability, session, or permission mutation is implemented
here. Every execution delegates to the existing canonical service.
"""

from __future__ import annotations

from typing import Any, Callable, Final, Iterable

from tools.eos.auth.system_permission_command_evidence import (
    SystemPermissionCommandEvidence,
    SystemPermissionCommandOperation,
)
from tools.eos.auth.system_permission_revocation_command_service import (
    SystemPermissionRevocationCommandService,
)
from tools.eos.system_services.eos_authorizer import SystemServicesEosAuthorizer
from tools.eos.saas.auth.password_reset_service import (
    PasswordResetExecutionEvidenceError,
    PasswordResetExecutionGuardError,
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

    @staticmethod
    def _validate_independent_executor(
        decision: SecurityIncidentResponseDecision,
        *,
        actor_principal_id: str,
    ) -> None:
        if (
            not isinstance(actor_principal_id, str)
            or not actor_principal_id
            or actor_principal_id != actor_principal_id.strip()
            or actor_principal_id in {
                decision.requested_by_principal_id,
                decision.decided_by_principal_id,
                decision.target_principal_id,
            }
        ):
            raise SecurityIncidentResponseExecutionError(
                "INDEPENDENT_RESPONSE_EXECUTOR_REQUIRED"
            )

    def _require_independent_executor(
        self,
        decision: SecurityIncidentResponseDecision,
        *,
        actor_principal_id: str,
        session: Any,
    ) -> None:
        self._validate_independent_executor(
            decision,
            actor_principal_id=actor_principal_id,
        )
        self._authorizer.require(
            principal_id=actor_principal_id,
            permission_id="system_services:incident:response:execute",
            session=session,
        )

    def authorize_execution(
        self,
        decision: SecurityIncidentResponseDecision,
        *,
        actor_principal_id: str,
        session: Any,
    ) -> None:
        """Authorize before receipt lookup so replay cannot bypass actor checks."""
        self._require_approved(
            decision,
            SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION,
        )
        self._require_independent_executor(
            decision,
            actor_principal_id=actor_principal_id,
            session=session,
        )

    def authorize_password_reset_replay(
        self,
        decision: SecurityIncidentResponseDecision,
        *,
        actor_principal_id: str,
        session: Any,
    ) -> None:
        """Re-prove independent execution authority before a reset receipt replay lookup."""
        self._require_approved(
            decision,
            SecurityIncidentResponseAction.PASSWORD_RESET,
        )
        self._require_independent_executor(
            decision,
            actor_principal_id=actor_principal_id,
            session=session,
        )

    def execute_password_reset(
        self,
        decision: SecurityIncidentResponseDecision,
        *,
        actor_principal_id: str,
        recovery_token: str,
        new_password: str,
        transaction_completion: Callable[[Any, str, str, int], None],
        context_terms: Iterable[str] | None = None,
    ) -> PasswordResetResult:
        """Delegate only to canonical R10 password reset with its durable capability.

        Approval does not mint or replace the single-use recovery capability;
        PasswordResetService remains the sole credential/session mutation owner.
        The current SYSTEM execute grant is re-proven inside R10's own Mongo
        transaction after the durable capability is re-read. No HTTP route is
        exposed until an execution receipt can be committed idempotently with
        the canonical reset transaction; this adapter does not claim cross-
        transaction atomicity with the decision projection.
        Secret values are passed transiently and are not retained on this adapter.
        """
        self._require_approved(decision, SecurityIncidentResponseAction.PASSWORD_RESET)
        if not callable(transaction_completion):
            raise SecurityIncidentResponseExecutionError(
                "PASSWORD_RESET_EXECUTION_RECEIPT_CALLBACK_REQUIRED"
            )
        self._validate_independent_executor(
            decision,
            actor_principal_id=actor_principal_id,
        )

        def authorize_inside_canonical_reset_transaction(session: Any, capability: Any) -> None:
            if (
                capability.tenant_id != decision.tenant_id
                or capability.principal_id != decision.target_principal_id
            ):
                raise SecurityIncidentResponseExecutionError(
                    "PASSWORD_RESET_TARGET_BINDING_INVALID"
                )
            self._require_independent_executor(
                decision,
                actor_principal_id=actor_principal_id,
                session=session,
            )

        def persist_execution_receipt(
            session: Any,
            tenant_id: str,
            principal_id: str,
            credential_revision: int,
        ) -> None:
            if (
                tenant_id != decision.tenant_id
                or principal_id != decision.target_principal_id
                or not isinstance(credential_revision, int)
                or isinstance(credential_revision, bool)
                or credential_revision < 1
            ):
                raise SecurityIncidentResponseExecutionError(
                    "PASSWORD_RESET_EXECUTION_RECEIPT_BINDING_INVALID"
                )
            transaction_completion(
                session,
                tenant_id,
                principal_id,
                credential_revision,
            )

        try:
            return self._password_reset.reset_password(
                tenant_id=decision.tenant_id,
                recovery_token=recovery_token,
                new_password=new_password,
                context_terms=context_terms,
                transaction_guard=authorize_inside_canonical_reset_transaction,
                transaction_completion=persist_execution_receipt,
            )
        except PasswordResetExecutionGuardError as error:
            if error.__cause__ is not None:
                raise error.__cause__
            raise SecurityIncidentResponseExecutionError(
                "PASSWORD_RESET_EXECUTION_AUTHORIZATION_FAILED"
            ) from error
        except PasswordResetExecutionEvidenceError as error:
            if error.__cause__ is not None:
                raise error.__cause__
            raise SecurityIncidentResponseExecutionError(
                "PASSWORD_RESET_EXECUTION_EVIDENCE_FAILED"
            ) from error

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
        self._require_independent_executor(
            decision,
            actor_principal_id=evidence.actor_principal_id,
            session=session,
        )
        return self._permission_revocation.revoke(evidence, session=session)


__all__ = [
    "VERSION",
    "SecurityIncidentResponseExecutionError",
    "SecurityIncidentResponseCanonicalExecutor",
]
