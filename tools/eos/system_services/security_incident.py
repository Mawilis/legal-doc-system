"""Immutable, sanitized tenant account-security incident intake evidence.

The domain records only structured observations. It deliberately accepts no
free-form narrative, credential material, recovery proof, token, or device secret.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Final

VERSION: Final[str] = "v1.0.0-EOS-SECURITY-INCIDENT-INTAKE"
SCHEMA: Final[str] = "WILSY-EOS-SECURITY-INCIDENT/V1"
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")


class SecurityIncidentCategory(StrEnum):
    UNRECOGNIZED_SIGN_IN = "UNRECOGNIZED_SIGN_IN"
    MFA_PROMPT_NOT_INITIATED = "MFA_PROMPT_NOT_INITIATED"
    UNREQUESTED_RECOVERY_CHANGE = "UNREQUESTED_RECOVERY_CHANGE"
    UNKNOWN_SESSION_OR_DEVICE = "UNKNOWN_SESSION_OR_DEVICE"
    SUSPECTED_ACCOUNT_COMPROMISE = "SUSPECTED_ACCOUNT_COMPROMISE"


class SecurityIncidentError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


@dataclass(frozen=True, slots=True)
class SecurityIncident:
    incident_id: str
    tenant_id: str
    reporter_principal_id: str
    idempotency_fingerprint: str
    category: SecurityIncidentCategory
    observed_at: datetime
    received_at: datetime
    revision: int = 0
    status: str = "RECEIVED"

    def __post_init__(self) -> None:
        for name, value in (
            ("incident_id", self.incident_id),
            ("tenant_id", self.tenant_id),
            ("reporter_principal_id", self.reporter_principal_id),
            ("idempotency_fingerprint", self.idempotency_fingerprint),
        ):
            if not isinstance(value, str) or not _ID.fullmatch(value):
                raise SecurityIncidentError("SECURITY_INCIDENT_IDENTIFIER_INVALID")
        if not isinstance(self.category, SecurityIncidentCategory):
            raise SecurityIncidentError("SECURITY_INCIDENT_CATEGORY_INVALID")
        for value in (self.observed_at, self.received_at):
            if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
                raise SecurityIncidentError("SECURITY_INCIDENT_TIMESTAMP_INVALID")
        if self.observed_at > self.received_at:
            raise SecurityIncidentError("SECURITY_INCIDENT_OBSERVED_AFTER_RECEIPT")
        if self.revision != 0 or self.status != "RECEIVED":
            raise SecurityIncidentError("SECURITY_INCIDENT_INITIAL_STATE_INVALID")


@dataclass(frozen=True, slots=True)
class SecurityIncidentEvent:
    event_id: str
    incident_id: str
    tenant_id: str
    actor_principal_id: str
    event_type: str
    occurred_at: datetime
    fingerprint: str

    def __post_init__(self) -> None:
        for value in (
            self.event_id, self.incident_id, self.tenant_id,
            self.actor_principal_id, self.event_type, self.fingerprint,
        ):
            if not isinstance(value, str) or not _ID.fullmatch(value):
                raise SecurityIncidentError("SECURITY_INCIDENT_EVENT_INVALID")
        if not isinstance(self.occurred_at, datetime) or self.occurred_at.tzinfo is None:
            raise SecurityIncidentError("SECURITY_INCIDENT_EVENT_TIMESTAMP_INVALID")


__all__ = [
    "VERSION", "SCHEMA", "SecurityIncidentCategory", "SecurityIncidentError",
    "SecurityIncident", "SecurityIncidentEvent",
]
