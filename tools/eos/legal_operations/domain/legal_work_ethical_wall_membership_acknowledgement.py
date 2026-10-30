"""G78 immutable ethical-wall membership and acknowledgement evidence.

Evidence is revisioned, tenant/matter/principal/policy scoped and non-authorizing.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import json
import re
from typing import Final, Iterable

VERSION: Final[str] = "v1.0.0-G78-WALL-MEMBERSHIP-ACKNOWLEDGEMENT"
SCHEMA: Final[str] = "WILSY-LEGAL-ETHICAL-WALL-MEMBERSHIP-ACK/V1"
_ID: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,199}\\Z")
_HEX: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{128}\\Z")


class WallEvidenceError(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class MembershipState(StrEnum):
    INCLUDED = "INCLUDED"
    RESTRICTED = "RESTRICTED"
    REVOKED = "REVOKED"


class AcknowledgementState(StrEnum):
    ACKNOWLEDGED = "ACKNOWLEDGED"
    REVOKED = "REVOKED"


class WallEvidenceCurrentness(StrEnum):
    MEMBERSHIP_MISSING = "MEMBERSHIP_MISSING"
    MEMBERSHIP_RESTRICTED = "MEMBERSHIP_RESTRICTED"
    MEMBERSHIP_REVOKED = "MEMBERSHIP_REVOKED"
    MEMBERSHIP_EXPIRED = "MEMBERSHIP_EXPIRED"
    MEMBERSHIP_POLICY_MISMATCH = "MEMBERSHIP_POLICY_MISMATCH"
    ACKNOWLEDGEMENT_MISSING = "ACKNOWLEDGEMENT_MISSING"
    ACKNOWLEDGEMENT_REVOKED = "ACKNOWLEDGEMENT_REVOKED"
    ACKNOWLEDGEMENT_EXPIRED = "ACKNOWLEDGEMENT_EXPIRED"
    ACKNOWLEDGEMENT_POLICY_MISMATCH = "ACKNOWLEDGEMENT_POLICY_MISMATCH"
    ACKNOWLEDGEMENT_MEMBERSHIP_MISMATCH = "ACKNOWLEDGEMENT_MEMBERSHIP_MISMATCH"
    EVIDENCE_CORRUPT = "EVIDENCE_CORRUPT"
    RECORDED_COMPLETE_UNVERIFIED = "RECORDED_COMPLETE_UNVERIFIED"


def _id(name: str, value: object) -> str:
    if type(value) is not str or _ID.fullmatch(value) is None:
        raise WallEvidenceError(name.upper() + "_INVALID")
    if value.casefold() in {"default", "global", "root", "*"}:
        raise WallEvidenceError(name.upper() + "_INVALID")
    return value


def _fp(name: str, value: object) -> str:
    if type(value) is not str or _HEX.fullmatch(value) is None:
        raise WallEvidenceError(name.upper() + "_INVALID")
    return value


def _time(name: str, value: object) -> datetime:
    if type(value) is not datetime or value.tzinfo is None or value.utcoffset() is None:
        raise WallEvidenceError(name.upper() + "_INVALID")
    result = value.astimezone(timezone.utc)
    if result.microsecond or result != value:
        raise WallEvidenceError(name.upper() + "_NONCANONICAL")
    return result


def _material(value: object) -> dict[str, object]:
    return {
        name: (getattr(value, name).value if isinstance(getattr(value, name), StrEnum)
               else getattr(value, name).isoformat() if isinstance(getattr(value, name), datetime)
               else getattr(value, name))
        for name in value.__dataclass_fields__ if name != "fingerprint"
    }


@dataclass(frozen=True, slots=True)
class WallMembershipEvidence:
    membership_id: str
    revision: int
    predecessor_fingerprint: str | None
    tenant_id: str
    case_matter_id: str
    policy_id: str
    policy_fingerprint: str
    practitioner_principal_id: str
    state: MembershipState | str
    effective_at: datetime
    expires_at: datetime
    issuer_principal_id: str
    issuer_authorization_reference: str
    issuer_authorization_fingerprint: str
    evidence_reference: str
    evidence_fingerprint: str
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.version != VERSION:
            raise WallEvidenceError("MEMBERSHIP_IDENTITY_INVALID")
        for name in ("membership_id", "tenant_id", "case_matter_id", "policy_id",
                     "practitioner_principal_id", "issuer_principal_id",
                     "issuer_authorization_reference", "evidence_reference"):
            object.__setattr__(self, name, _id(name, getattr(self, name)))
        if type(self.revision) is not int or self.revision < 1:
            raise WallEvidenceError("MEMBERSHIP_REVISION_INVALID")
        predecessor = self.predecessor_fingerprint
        if self.revision == 1:
            if predecessor is not None:
                raise WallEvidenceError("MEMBERSHIP_ROOT_PREDECESSOR_INVALID")
        else:
            predecessor = _fp("membership_predecessor_fingerprint", predecessor)
        object.__setattr__(self, "predecessor_fingerprint", predecessor)
        for name in ("policy_fingerprint", "issuer_authorization_fingerprint", "evidence_fingerprint"):
            object.__setattr__(self, name, _fp(name, getattr(self, name)))
        try:
            state = MembershipState(self.state)
        except (TypeError, ValueError) as error:
            raise WallEvidenceError("MEMBERSHIP_STATE_INVALID") from error
        object.__setattr__(self, "state", state)
        start, end = _time("membership_effective_at", self.effective_at), _time("membership_expires_at", self.expires_at)
        if end <= start:
            raise WallEvidenceError("MEMBERSHIP_WINDOW_INVALID")
        object.__setattr__(self, "effective_at", start)
        object.__setattr__(self, "expires_at", end)
        raw = json.dumps(_material(self), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        object.__setattr__(self, "fingerprint", sha3_512(raw).hexdigest())

    @property
    def permits_operational_access(self) -> bool:
        return False


@dataclass(frozen=True, slots=True)
class WallAcknowledgementEvidence:
    acknowledgement_id: str
    revision: int
    predecessor_fingerprint: str | None
    tenant_id: str
    case_matter_id: str
    policy_id: str
    policy_fingerprint: str
    practitioner_principal_id: str
    membership_fingerprint: str
    state: AcknowledgementState | str
    acknowledged_by_principal_id: str
    independently_verified_by_principal_id: str
    verification_authorization_reference: str
    verification_authorization_fingerprint: str
    acknowledged_at: datetime
    expires_at: datetime
    evidence_reference: str
    evidence_fingerprint: str
    schema: str = SCHEMA
    version: str = VERSION
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        if self.schema != SCHEMA or self.version != VERSION:
            raise WallEvidenceError("ACKNOWLEDGEMENT_IDENTITY_INVALID")
        for name in ("acknowledgement_id", "tenant_id", "case_matter_id", "policy_id",
                     "practitioner_principal_id", "acknowledged_by_principal_id",
                     "independently_verified_by_principal_id",
                     "verification_authorization_reference", "evidence_reference"):
            object.__setattr__(self, name, _id(name, getattr(self, name)))
        if self.acknowledged_by_principal_id != self.practitioner_principal_id:
            raise WallEvidenceError("ACKNOWLEDGEMENT_ACTOR_MISMATCH")
        if self.independently_verified_by_principal_id in {
            self.practitioner_principal_id, self.acknowledged_by_principal_id
        }:
            raise WallEvidenceError("ACKNOWLEDGEMENT_INDEPENDENCE_INVALID")
        if type(self.revision) is not int or self.revision < 1:
            raise WallEvidenceError("ACKNOWLEDGEMENT_REVISION_INVALID")
        predecessor = self.predecessor_fingerprint
        if self.revision == 1:
            if predecessor is not None:
                raise WallEvidenceError("ACKNOWLEDGEMENT_ROOT_PREDECESSOR_INVALID")
        else:
            predecessor = _fp("acknowledgement_predecessor_fingerprint", predecessor)
        object.__setattr__(self, "predecessor_fingerprint", predecessor)
        for name in ("policy_fingerprint", "membership_fingerprint",
                     "verification_authorization_fingerprint", "evidence_fingerprint"):
            object.__setattr__(self, name, _fp(name, getattr(self, name)))
        try:
            state = AcknowledgementState(self.state)
        except (TypeError, ValueError) as error:
            raise WallEvidenceError("ACKNOWLEDGEMENT_STATE_INVALID") from error
        object.__setattr__(self, "state", state)
        start, end = _time("acknowledged_at", self.acknowledged_at), _time("acknowledgement_expires_at", self.expires_at)
        if end <= start:
            raise WallEvidenceError("ACKNOWLEDGEMENT_WINDOW_INVALID")
        object.__setattr__(self, "acknowledged_at", start)
        object.__setattr__(self, "expires_at", end)
        raw = json.dumps(_material(self), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
        object.__setattr__(self, "fingerprint", sha3_512(raw).hexdigest())

    @property
    def permits_operational_access(self) -> bool:
        return False


@dataclass(frozen=True, slots=True)
class WallMembershipAcknowledgementProjection:
    state: WallEvidenceCurrentness
    membership_fingerprint: str | None = None
    acknowledgement_fingerprint: str | None = None

    @property
    def permits_operational_access(self) -> bool:
        return False


def _linear(history: Iterable[object], expected_type: type, *, tenant: str,
            matter: str, policy: str, principal: str, at: datetime) -> tuple[object, ...]:
    values = tuple(history)
    if not values:
        return ()
    if any(type(item) is not expected_type or replace(item).fingerprint != item.fingerprint
           for item in values):
        raise WallEvidenceError("EVIDENCE_CORRUPT")
    values = tuple(sorted(values, key=lambda item: item.revision))
    if len(values) > 128 or [item.revision for item in values] != list(range(1, len(values) + 1)):
        raise WallEvidenceError("EVIDENCE_CORRUPT")
    first = values[0]
    identity_fields = ("tenant_id", "case_matter_id", "policy_id", "practitioner_principal_id")
    if any(getattr(first, name) != value for name, value in zip(identity_fields, (tenant, matter, policy, principal))):
        raise WallEvidenceError("EVIDENCE_CORRUPT")
    for previous, current in zip(values, values[1:]):
        if current.predecessor_fingerprint != previous.fingerprint or current.effective_at <= previous.effective_at if hasattr(current, "effective_at") else current.predecessor_fingerprint != previous.fingerprint or current.acknowledged_at <= previous.acknowledged_at:
            raise WallEvidenceError("EVIDENCE_CORRUPT")
    effective = tuple(item for item in values if (item.effective_at if hasattr(item, "effective_at") else item.acknowledged_at) <= at)
    return effective


def project_wall_membership_and_acknowledgement(
    *, tenant_id: str, case_matter_id: str, policy_id: str,
    practitioner_principal_id: str, policy_fingerprint: str,
    evaluation_time: datetime, memberships: Iterable[WallMembershipEvidence],
    acknowledgements: Iterable[WallAcknowledgementEvidence],
) -> WallMembershipAcknowledgementProjection:
    try:
        tenant, matter, policy, principal = (
            _id("tenant_id", tenant_id), _id("case_matter_id", case_matter_id),
            _id("policy_id", policy_id), _id("practitioner_principal_id", practitioner_principal_id),
        )
        at = _time("evaluation_time", evaluation_time)
        policy_fp = _fp("policy_fingerprint", policy_fingerprint)
        member_history = _linear(memberships, WallMembershipEvidence, tenant=tenant,
                                 matter=matter, policy=policy, principal=principal, at=at)
        if not member_history:
            return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.MEMBERSHIP_MISSING)
        member = member_history[-1]
        if member.policy_fingerprint != policy_fp:
            return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.MEMBERSHIP_POLICY_MISMATCH, member.fingerprint)
        if member.state is MembershipState.RESTRICTED:
            return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.MEMBERSHIP_RESTRICTED, member.fingerprint)
        if member.state is MembershipState.REVOKED:
            return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.MEMBERSHIP_REVOKED, member.fingerprint)
        if at >= member.expires_at:
            return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.MEMBERSHIP_EXPIRED, member.fingerprint)
        if member.state is not MembershipState.INCLUDED:
            return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.MEMBERSHIP_MISSING, member.fingerprint)
        ack_history = _linear(acknowledgements, WallAcknowledgementEvidence, tenant=tenant,
                              matter=matter, policy=policy, principal=principal, at=at)
        if not ack_history:
            return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.ACKNOWLEDGEMENT_MISSING, member.fingerprint)
        ack = ack_history[-1]
        if ack.policy_fingerprint != policy_fp:
            return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.ACKNOWLEDGEMENT_POLICY_MISMATCH, member.fingerprint, ack.fingerprint)
        if ack.membership_fingerprint != member.fingerprint:
            return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.ACKNOWLEDGEMENT_MEMBERSHIP_MISMATCH, member.fingerprint, ack.fingerprint)
        if ack.state is AcknowledgementState.REVOKED:
            return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.ACKNOWLEDGEMENT_REVOKED, member.fingerprint, ack.fingerprint)
        if at >= ack.expires_at:
            return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.ACKNOWLEDGEMENT_EXPIRED, member.fingerprint, ack.fingerprint)
        return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.RECORDED_COMPLETE_UNVERIFIED, member.fingerprint, ack.fingerprint)
    except WallEvidenceError:
        return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.EVIDENCE_CORRUPT)
    except Exception:
        return WallMembershipAcknowledgementProjection(WallEvidenceCurrentness.EVIDENCE_CORRUPT)


__all__ = [
    "VERSION", "SCHEMA", "WallEvidenceError", "MembershipState",
    "AcknowledgementState", "WallEvidenceCurrentness", "WallMembershipEvidence",
    "WallAcknowledgementEvidence", "WallMembershipAcknowledgementProjection",
    "project_wall_membership_and_acknowledgement",
]
