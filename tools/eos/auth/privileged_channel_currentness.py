"""Pure privileged-channel currentness facts for P3-R3G."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum


VERSION = "v1.0.0-P3-R3G-S3-CHANNEL-CURRENTNESS"


class ChannelCurrentnessError(ValueError):
    """Fail-closed currentness input error."""


class FactorVerificationStatus(StrEnum):
    VERIFIED = "VERIFIED"
    REVOKED = "REVOKED"
    INVALIDATED = "INVALIDATED"


class WorkloadTrustStatus(StrEnum):
    CURRENT = "CURRENT"
    REVOKED = "REVOKED"
    INVALIDATED = "INVALIDATED"


def _text(name: str, value: object) -> str:
    if not isinstance(value, str):
        raise ChannelCurrentnessError(f"{name} is invalid")

    result = value.strip()

    if not result or len(result) > 1024:
        raise ChannelCurrentnessError(f"{name} is invalid")

    return result


def _revision(value: object) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
    ):
        raise ChannelCurrentnessError(
            "credential_revision is invalid"
        )

    return value


def _time(name: str, value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise ChannelCurrentnessError(f"{name} is invalid")

    return value.astimezone(timezone.utc)


@dataclass(frozen=True, slots=True)
class InteractiveFactorVerificationEvent:
    factor_verification_reference: str
    principal_id: str
    session_reference: str
    credential_revision: int
    authenticated_at: datetime
    status: FactorVerificationStatus

    def __post_init__(self) -> None:
        for name in (
            "factor_verification_reference",
            "principal_id",
            "session_reference",
        ):
            object.__setattr__(
                self,
                name,
                _text(name, getattr(self, name)),
            )

        object.__setattr__(
            self,
            "credential_revision",
            _revision(self.credential_revision),
        )

        object.__setattr__(
            self,
            "authenticated_at",
            _time("authenticated_at", self.authenticated_at),
        )

        if not isinstance(self.status, FactorVerificationStatus):
            raise ChannelCurrentnessError(
                "factor status is invalid"
            )


@dataclass(frozen=True, slots=True)
class InteractiveCurrentness:
    factor_verification_current: bool
    authentication_recency_current: bool


def derive_interactive_currentness(
    event: InteractiveFactorVerificationEvent,
    *,
    principal_id: str,
    session_reference: str,
    credential_revision: int,
    session_current: bool,
    evaluated_at: datetime,
    maximum_age_seconds: int,
) -> InteractiveCurrentness:
    if type(event) is not InteractiveFactorVerificationEvent:
        raise ChannelCurrentnessError("event is invalid")

    if (
        not isinstance(session_current, bool)
        or not isinstance(maximum_age_seconds, int)
        or isinstance(maximum_age_seconds, bool)
        or maximum_age_seconds <= 0
    ):
        raise ChannelCurrentnessError(
            "interactive policy input is invalid"
        )

    factor_current = (
        session_current
        and event.status is FactorVerificationStatus.VERIFIED
        and event.principal_id == _text("principal_id", principal_id)
        and event.session_reference
        == _text("session_reference", session_reference)
        and event.credential_revision
        == _revision(credential_revision)
    )

    now = _time("evaluated_at", evaluated_at)
    age = now - event.authenticated_at

    recent = (
        factor_current
        and age >= timedelta(0)
        and age <= timedelta(seconds=maximum_age_seconds)
    )

    return InteractiveCurrentness(
        factor_verification_current=factor_current,
        authentication_recency_current=recent,
    )


@dataclass(frozen=True, slots=True)
class WorkloadTrustFact:
    proof_reference: str
    principal_id: str
    credential_or_attestation_reference: str
    observed_at: datetime
    status: WorkloadTrustStatus

    def __post_init__(self) -> None:
        for name in (
            "proof_reference",
            "principal_id",
            "credential_or_attestation_reference",
        ):
            object.__setattr__(
                self,
                name,
                _text(name, getattr(self, name)),
            )

        object.__setattr__(
            self,
            "observed_at",
            _time("observed_at", self.observed_at),
        )

        if not isinstance(self.status, WorkloadTrustStatus):
            raise ChannelCurrentnessError(
                "workload trust status is invalid"
            )


def derive_workload_proof_currentness(
    fact: WorkloadTrustFact,
    *,
    principal_id: str,
    proof_reference: str,
    credential_or_attestation_reference: str,
) -> bool:
    if type(fact) is not WorkloadTrustFact:
        raise ChannelCurrentnessError(
            "workload fact is invalid"
        )

    return (
        fact.status is WorkloadTrustStatus.CURRENT
        and fact.principal_id == _text("principal_id", principal_id)
        and fact.proof_reference
        == _text("proof_reference", proof_reference)
        and fact.credential_or_attestation_reference
        == _text(
            "credential_or_attestation_reference",
            credential_or_attestation_reference,
        )
    )


__all__ = [
    "VERSION",
    "ChannelCurrentnessError",
    "FactorVerificationStatus",
    "WorkloadTrustStatus",
    "InteractiveFactorVerificationEvent",
    "InteractiveCurrentness",
    "WorkloadTrustFact",
    "derive_interactive_currentness",
    "derive_workload_proof_currentness",
]
