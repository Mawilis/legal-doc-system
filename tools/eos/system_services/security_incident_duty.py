"""Explicit, fail-closed duty coverage and acknowledgement policy projection.

This module resolves only a supplied, approved roster snapshot. It does not
create assignments, notify responders, or imply a staffed rota when none exists.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum


class SecurityIncidentDutyError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class DutyRouteStatus(StrEnum):
    ROUTED = "ROUTED"
    OUT_OF_HOURS = "OUT_OF_HOURS"
    UNSTAFFED = "UNSTAFFED"


@dataclass(frozen=True, slots=True)
class SecurityIncidentDutyWindow:
    responder_principal_id: str
    starts_at: datetime
    ends_at: datetime

    def __post_init__(self) -> None:
        if (
            not isinstance(self.responder_principal_id, str)
            or not self.responder_principal_id
            or self.responder_principal_id != self.responder_principal_id.strip()
        ):
            raise SecurityIncidentDutyError("DUTY_RESPONDER_INVALID")
        for value in (self.starts_at, self.ends_at):
            if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
                raise SecurityIncidentDutyError("DUTY_WINDOW_TIMESTAMP_INVALID")
        if self.starts_at >= self.ends_at:
            raise SecurityIncidentDutyError("DUTY_WINDOW_RANGE_INVALID")


@dataclass(frozen=True, slots=True)
class SecurityIncidentDutyResolution:
    status: DutyRouteStatus
    responder_principal_id: str | None
    resolved_at: datetime
    acknowledgement_deadline_at: datetime
    next_coverage_at: datetime | None
    policy_id: str


@dataclass(frozen=True, slots=True)
class SecurityIncidentDutyPolicy:
    policy_id: str
    acknowledgement_minutes: int
    windows: tuple[SecurityIncidentDutyWindow, ...]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.policy_id, str)
            or not self.policy_id
            or self.policy_id != self.policy_id.strip()
        ):
            raise SecurityIncidentDutyError("DUTY_POLICY_ID_INVALID")
        if (
            isinstance(self.acknowledgement_minutes, bool)
            or not isinstance(self.acknowledgement_minutes, int)
            or not 1 <= self.acknowledgement_minutes <= 1440
        ):
            raise SecurityIncidentDutyError("DUTY_ACKNOWLEDGEMENT_SLA_INVALID")
        if not isinstance(self.windows, tuple) or any(
            not isinstance(window, SecurityIncidentDutyWindow) for window in self.windows
        ):
            raise SecurityIncidentDutyError("DUTY_WINDOWS_INVALID")

    def resolve(self, *, now: datetime) -> SecurityIncidentDutyResolution:
        """Resolve exactly one active responder or return an explicit uncovered state."""
        if not isinstance(now, datetime) or now.tzinfo is None or now.utcoffset() is None:
            raise SecurityIncidentDutyError("DUTY_RESOLUTION_TIME_INVALID")
        instant = now.astimezone(timezone.utc)
        active = [
            window for window in self.windows
            if window.starts_at.astimezone(timezone.utc) <= instant < window.ends_at.astimezone(timezone.utc)
        ]
        if len(active) > 1:
            raise SecurityIncidentDutyError("DUTY_ROSTER_OVERLAP_CONFLICT")
        next_coverage = min(
            (window.starts_at.astimezone(timezone.utc) for window in self.windows
             if window.starts_at.astimezone(timezone.utc) > instant),
            default=None,
        )
        deadline = instant + timedelta(minutes=self.acknowledgement_minutes)
        if len(active) == 1:
            status = DutyRouteStatus.ROUTED
            responder = active[0].responder_principal_id
        elif self.windows:
            status = DutyRouteStatus.OUT_OF_HOURS
            responder = None
        else:
            status = DutyRouteStatus.UNSTAFFED
            responder = None
        return SecurityIncidentDutyResolution(
            status=status, responder_principal_id=responder, resolved_at=instant,
            acknowledgement_deadline_at=deadline, next_coverage_at=next_coverage,
            policy_id=self.policy_id,
        )


__all__ = [
    "DutyRouteStatus", "SecurityIncidentDutyError",
    "SecurityIncidentDutyWindow", "SecurityIncidentDutyResolution",
    "SecurityIncidentDutyPolicy",
]
