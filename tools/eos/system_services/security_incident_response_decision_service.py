"""Permission-gated orchestration for independent incident response decisions."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Final

from .eos_authorizer import SystemServicesEosAuthorizer
from .security_incident_registry import SecurityIncidentNotFoundError, SecurityIncidentRegistry
from .security_incident_response_decision import (
    SecurityIncidentResponseDecision,
    SecurityIncidentResponseDecisionStatus,
)
from .security_incident_response_decision_registry import (
    SecurityIncidentResponseDecisionRegistry,
)

VERSION: Final[str] = "v1.0.0-EOS-INDEPENDENT-INCIDENT-RESPONSE-GOVERNANCE"


class SecurityIncidentResponseDecisionServiceError(RuntimeError):
    """Stable failure for permission-gated decision orchestration."""


class SecurityIncidentResponseDecisionService:
    """Require current SYSTEM workforce permissions for request and approval."""

    def __init__(
        self,
        *,
        decisions: SecurityIncidentResponseDecisionRegistry,
        incidents: SecurityIncidentRegistry,
        authorizer: SystemServicesEosAuthorizer,
    ) -> None:
        if type(decisions) is not SecurityIncidentResponseDecisionRegistry:
            raise SecurityIncidentResponseDecisionServiceError("RESPONSE_DECISION_REGISTRY_REQUIRED")
        if type(incidents) is not SecurityIncidentRegistry:
            raise SecurityIncidentResponseDecisionServiceError("SECURITY_INCIDENT_REGISTRY_REQUIRED")
        if type(authorizer) is not SystemServicesEosAuthorizer:
            raise SecurityIncidentResponseDecisionServiceError("CURRENT_PLATFORM_AUTHORIZER_REQUIRED")
        self._decisions = decisions
        self._incidents = incidents
        self._authorizer = authorizer

    def request(
        self,
        *,
        actor_principal_id: str,
        decision: SecurityIncidentResponseDecision,
        session: Any,
    ) -> SecurityIncidentResponseDecision:
        """Create one response proposal bound to the actual reporter and incident."""
        if (
            not isinstance(decision, SecurityIncidentResponseDecision)
            or decision.status is not SecurityIncidentResponseDecisionStatus.PENDING
            or decision.requested_by_principal_id != actor_principal_id
        ):
            raise SecurityIncidentResponseDecisionServiceError("RESPONSE_REQUEST_ACTOR_BINDING_INVALID")
        self._authorizer.require(
            principal_id=actor_principal_id,
            permission_id="system_services:incident:escalate",
            session=session,
        )
        try:
            incident = self._incidents.get_by_id(
                incident_id=decision.incident_id,
                session=session,
            )
        except SecurityIncidentNotFoundError as error:
            raise SecurityIncidentResponseDecisionServiceError("RESPONSE_INCIDENT_NOT_FOUND") from error
        if (
            incident.tenant_id != decision.tenant_id
            or incident.reporter_principal_id != decision.target_principal_id
        ):
            raise SecurityIncidentResponseDecisionServiceError("RESPONSE_TARGET_INCIDENT_BINDING_INVALID")
        return self._decisions.create(decision, session=session)

    def decide(
        self,
        decision_id: str,
        *,
        actor_principal_id: str,
        approved: bool,
        decided_at: datetime,
        decision_evidence_reference: str,
        expected_revision: int,
        session: Any,
    ) -> SecurityIncidentResponseDecision:
        """Record an independent approve/reject decision under its own IAM grant."""
        self._authorizer.require(
            principal_id=actor_principal_id,
            permission_id="system_services:incident:response:decide",
            session=session,
        )
        return self._decisions.decide(
            decision_id,
            approved=approved,
            decided_by_principal_id=actor_principal_id,
            decided_at=decided_at,
            decision_evidence_reference=decision_evidence_reference,
            expected_revision=expected_revision,
            session=session,
        )


__all__ = [
    "VERSION",
    "SecurityIncidentResponseDecisionServiceError",
    "SecurityIncidentResponseDecisionService",
]
