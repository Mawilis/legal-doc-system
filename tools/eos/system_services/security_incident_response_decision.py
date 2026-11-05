"""Independent, non-executing containment and recovery decision evidence.

This module records a separately governed decision. It is not an account,
credential, session, principal, permission, or notification authority. Approved
records must be handed to the existing canonical EOS service for execution.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import StrEnum
from typing import Final

VERSION: Final[str] = "v1.0.0-EOS-SECURITY-INCIDENT-RESPONSE-DECISION"
SCHEMA: Final[str] = "WILSY-EOS-SECURITY-INCIDENT-RESPONSE-DECISION/V1"
_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")


class SecurityIncidentResponseDecisionError(ValueError):
    """Reject malformed or non-independent response decisions."""


class SecurityIncidentResponseAction(StrEnum):
    PASSWORD_RESET = "PASSWORD_RESET"
    SYSTEM_PERMISSION_REVOCATION = "SYSTEM_PERMISSION_REVOCATION"


class SecurityIncidentResponseDecisionStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


def _identifier(name: str, value: object) -> str:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise SecurityIncidentResponseDecisionError(name + "_INVALID")
    return value


def _aware_utc(name: str, value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise SecurityIncidentResponseDecisionError(name + "_INVALID")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class SecurityIncidentResponseDecision:
    """Immutable request and independent decision for one exact incident target.

    Requester and decision-maker must be distinct. Revision 0 is pending;
    revision 1 is a terminal approve/reject decision. This record does not
    execute the approved action and contains no password, reset token, session
    token, recovery address, or notification payload.
    """

    decision_id: str
    incident_id: str
    tenant_id: str
    target_principal_id: str
    action: SecurityIncidentResponseAction
    requested_by_principal_id: str
    requested_at: datetime
    request_evidence_reference: str
    target_assignment_id: str | None = None
    target_permission_id: str | None = None
    status: SecurityIncidentResponseDecisionStatus = SecurityIncidentResponseDecisionStatus.PENDING
    revision: int = 0
    decided_by_principal_id: str | None = None
    decided_at: datetime | None = None
    decision_evidence_reference: str | None = None

    def __post_init__(self) -> None:
        for name in (
            "decision_id", "incident_id", "tenant_id", "target_principal_id",
            "requested_by_principal_id", "request_evidence_reference",
        ):
            object.__setattr__(self, name, _identifier(name.upper(), getattr(self, name)))
        object.__setattr__(self, "requested_at", _aware_utc("REQUESTED_AT", self.requested_at))
        if not isinstance(self.action, SecurityIncidentResponseAction):
            raise SecurityIncidentResponseDecisionError("ACTION_INVALID")
        if self.action is SecurityIncidentResponseAction.SYSTEM_PERMISSION_REVOCATION:
            object.__setattr__(
                self, "target_assignment_id",
                _identifier("TARGET_ASSIGNMENT_ID", self.target_assignment_id),
            )
            object.__setattr__(
                self, "target_permission_id",
                _identifier("TARGET_PERMISSION_ID", self.target_permission_id),
            )
        elif self.target_assignment_id is not None or self.target_permission_id is not None:
            raise SecurityIncidentResponseDecisionError("PERMISSION_REVOCATION_BINDING_FORBIDDEN")
        if not isinstance(self.status, SecurityIncidentResponseDecisionStatus):
            raise SecurityIncidentResponseDecisionError("STATUS_INVALID")
        if self.revision == 0 and self.status is SecurityIncidentResponseDecisionStatus.PENDING:
            if any(value is not None for value in (
                self.decided_by_principal_id, self.decided_at, self.decision_evidence_reference,
            )):
                raise SecurityIncidentResponseDecisionError("PENDING_DECISION_HAS_OUTCOME")
            return
        if self.revision != 1 or self.status is SecurityIncidentResponseDecisionStatus.PENDING:
            raise SecurityIncidentResponseDecisionError("DECISION_REVISION_INVALID")
        if self.decided_by_principal_id is None or self.decided_at is None or self.decision_evidence_reference is None:
            raise SecurityIncidentResponseDecisionError("DECISION_OUTCOME_REQUIRED")
        object.__setattr__(
            self, "decided_by_principal_id",
            _identifier("DECIDED_BY_PRINCIPAL_ID", self.decided_by_principal_id),
        )
        object.__setattr__(self, "decided_at", _aware_utc("DECIDED_AT", self.decided_at))
        object.__setattr__(
            self, "decision_evidence_reference",
            _identifier("DECISION_EVIDENCE_REFERENCE", self.decision_evidence_reference),
        )
        if self.decided_by_principal_id == self.requested_by_principal_id:
            raise SecurityIncidentResponseDecisionError("INDEPENDENT_DECISION_MAKER_REQUIRED")
        if self.decided_at < self.requested_at:
            raise SecurityIncidentResponseDecisionError("DECISION_PRECEDES_REQUEST")

    def decide(
        self,
        *,
        approved: bool,
        decided_by_principal_id: str,
        decided_at: datetime,
        decision_evidence_reference: str,
        expected_revision: int,
    ) -> "SecurityIncidentResponseDecision":
        """Return one independent terminal decision; never execute its action."""
        if expected_revision != self.revision or self.revision != 0:
            raise SecurityIncidentResponseDecisionError("DECISION_REVISION_CONFLICT")
        if not isinstance(approved, bool):
            raise SecurityIncidentResponseDecisionError("APPROVAL_VALUE_INVALID")
        return replace(
            self,
            status=(
                SecurityIncidentResponseDecisionStatus.APPROVED
                if approved else SecurityIncidentResponseDecisionStatus.REJECTED
            ),
            revision=1,
            decided_by_principal_id=decided_by_principal_id,
            decided_at=decided_at,
            decision_evidence_reference=decision_evidence_reference,
        )


__all__ = [
    "VERSION", "SCHEMA", "SecurityIncidentResponseDecisionError",
    "SecurityIncidentResponseAction", "SecurityIncidentResponseDecisionStatus",
    "SecurityIncidentResponseDecision",
]
