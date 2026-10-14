"""WILSY OS platform privileged-eligibility prerequisite authority.

TITLE: Platform Privileged Eligibility Prerequisite
VERSION: v1.0.0-P2-R3-PLATFORM-PREREQUISITE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable revision evidence for the exact platform prerequisite leg of
         SOVEREIGN_ARCHITECT P2 eligibility.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/platform_privileged_eligibility_prerequisite.py
COLLABORATION / OWNERSHIP: Core Governance designates records; IAM evaluates them.
CERTIFICATION / UPDATE DATE: 2026-10-14
CHANGELOG: v1.0.0 establishes exact identity, lifecycle, effective window,
           provenance, and SHA3-512 lineage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque principal and evidence identifiers only.
TENANT BOUNDARY: PLATFORM_SYSTEM scope only; tenant delegation is forbidden.
AUTHORITY BOUNDARY: Satisfies one P2 prerequisite leg only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import json
import re
from typing import Final, Mapping

VERSION: Final[str] = "v1.0.0-P2-R3-PLATFORM-PREREQUISITE"
SCHEMA: Final[str] = "WILSY-PLATFORM-PRIVILEGED-ELIGIBILITY-PREREQUISITE/V1"
SCOPE: Final[str] = "PLATFORM_SYSTEM"
PRIVILEGE_CLASS: Final[str] = "SOVEREIGN_ARCHITECT"
SOURCE_AUTHORITY: Final[str] = "WILSY_OS_CORE_GOVERNANCE"
_HEX = re.compile(r"^[0-9a-f]{128}$")


class PlatformPrivilegedEligibilityPrerequisiteError(ValueError):
    """Reject malformed or authority-expanding prerequisite material."""


class PlatformPrerequisiteStatus(StrEnum):
    """Closed lifecycle vocabulary; terminal states cannot resurrect."""

    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"
    REVOKED = "REVOKED"


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip() or "*" in value:
        raise PlatformPrivilegedEligibilityPrerequisiteError(field + "_INVALID")
    return value


def _time(value: object, field: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise PlatformPrivilegedEligibilityPrerequisiteError(field + "_INVALID")
    return value.astimezone(timezone.utc)


def _fingerprint(payload: Mapping[str, object]) -> str:
    return sha3_512(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class PlatformPrivilegedEligibilityPrerequisite:
    """One immutable Core-Governance designation revision.

    It grants no permission, activation, tenant, break-glass, or financial
    authority and owns no persistence or transaction lifecycle.
    """

    platform_prerequisite_id: str
    revision: int
    principal_id: str
    privilege_class: str
    scope: str
    status: PlatformPrerequisiteStatus
    effective_from: datetime
    effective_until: datetime | None
    source_authority: str
    source_evidence_reference: str
    prerequisite_fingerprint: str

    def __post_init__(self) -> None:
        _text(self.platform_prerequisite_id, "PLATFORM_PREREQUISITE_ID")
        _text(self.principal_id, "PRINCIPAL_ID")
        _text(self.source_evidence_reference, "SOURCE_EVIDENCE_REFERENCE")
        if self.privilege_class != PRIVILEGE_CLASS or self.scope != SCOPE:
            raise PlatformPrivilegedEligibilityPrerequisiteError("PREREQUISITE_SCOPE_INVALID")
        if self.source_authority != SOURCE_AUTHORITY:
            raise PlatformPrivilegedEligibilityPrerequisiteError("SOURCE_AUTHORITY_INVALID")
        if isinstance(self.revision, bool) or not isinstance(self.revision, int) or self.revision < 1:
            raise PlatformPrivilegedEligibilityPrerequisiteError("REVISION_INVALID")
        if not isinstance(self.status, PlatformPrerequisiteStatus):
            raise PlatformPrivilegedEligibilityPrerequisiteError("STATUS_INVALID")
        start = _time(self.effective_from, "EFFECTIVE_FROM")
        end = None if self.effective_until is None else _time(self.effective_until, "EFFECTIVE_UNTIL")
        if end is not None and start >= end:
            raise PlatformPrivilegedEligibilityPrerequisiteError("EFFECTIVE_WINDOW_INVALID")
        object.__setattr__(self, "effective_from", start)
        object.__setattr__(self, "effective_until", end)
        if _HEX.fullmatch(self.prerequisite_fingerprint) is None or self.prerequisite_fingerprint != _fingerprint(self._payload()):
            raise PlatformPrivilegedEligibilityPrerequisiteError("PREREQUISITE_FINGERPRINT_INVALID")

    def _payload(self) -> dict[str, object]:
        return {
            "schema": SCHEMA, "version": VERSION,
            "platform_prerequisite_id": self.platform_prerequisite_id,
            "revision": self.revision, "principal_id": self.principal_id,
            "privilege_class": self.privilege_class, "scope": self.scope,
            "status": self.status.value, "effective_from": self.effective_from.isoformat(),
            "effective_until": None if self.effective_until is None else self.effective_until.isoformat(),
            "source_authority": self.source_authority,
            "source_evidence_reference": self.source_evidence_reference,
        }

    @classmethod
    def designate(cls, *, platform_prerequisite_id: object, principal_id: object,
                  effective_from: object, source_evidence_reference: object,
                  effective_until: object = None) -> "PlatformPrivilegedEligibilityPrerequisite":
        """Create revision one from explicit Core-Governance ceremony data."""
        prerequisite_id = _text(platform_prerequisite_id, "PLATFORM_PREREQUISITE_ID")
        principal = _text(principal_id, "PRINCIPAL_ID")
        evidence = _text(source_evidence_reference, "SOURCE_EVIDENCE_REFERENCE")
        start = _time(effective_from, "EFFECTIVE_FROM")
        end = None if effective_until is None else _time(effective_until, "EFFECTIVE_UNTIL")
        provisional = cls.__new__(cls)
        values = (prerequisite_id, 1, principal, PRIVILEGE_CLASS, SCOPE, PlatformPrerequisiteStatus.ACTIVE, start, end, SOURCE_AUTHORITY, evidence)
        payload = {"schema": SCHEMA, "version": VERSION, "platform_prerequisite_id": prerequisite_id, "revision": 1, "principal_id": principal, "privilege_class": PRIVILEGE_CLASS, "scope": SCOPE, "status": "ACTIVE", "effective_from": start.isoformat(), "effective_until": None if end is None else end.isoformat(), "source_authority": SOURCE_AUTHORITY, "source_evidence_reference": evidence}
        return cls(*values, _fingerprint(payload))

    def transition(self, *, status: PlatformPrerequisiteStatus, effective_from: object,
                   source_evidence_reference: object) -> "PlatformPrivilegedEligibilityPrerequisite":
        """Create one terminal successor; resurrection and in-place mutation are impossible."""
        if self.status is not PlatformPrerequisiteStatus.ACTIVE or status not in {PlatformPrerequisiteStatus.RETIRED, PlatformPrerequisiteStatus.REVOKED}:
            raise PlatformPrivilegedEligibilityPrerequisiteError("LIFECYCLE_TRANSITION_INVALID")
        at = _time(effective_from, "EFFECTIVE_FROM")
        if at < self.effective_from or (self.effective_until is not None and at > self.effective_until):
            raise PlatformPrivilegedEligibilityPrerequisiteError("LIFECYCLE_TRANSITION_TIME_INVALID")
        evidence = _text(source_evidence_reference, "SOURCE_EVIDENCE_REFERENCE")
        revision = self.revision + 1
        payload = {"schema": SCHEMA, "version": VERSION, "platform_prerequisite_id": self.platform_prerequisite_id, "revision": revision, "principal_id": self.principal_id, "privilege_class": PRIVILEGE_CLASS, "scope": SCOPE, "status": status.value, "effective_from": at.isoformat(), "effective_until": None, "source_authority": SOURCE_AUTHORITY, "source_evidence_reference": evidence}
        return type(self)(self.platform_prerequisite_id, revision, self.principal_id, PRIVILEGE_CLASS, SCOPE, status, at, None, SOURCE_AUTHORITY, evidence, _fingerprint(payload))

    def is_current_at(self, at: object) -> bool:
        """Evaluate ACTIVE half-open window currentness without reading a clock."""
        moment = _time(at, "EVALUATED_AT")
        return self.status is PlatformPrerequisiteStatus.ACTIVE and self.effective_from <= moment and (self.effective_until is None or moment < self.effective_until)

    def to_persisted(self) -> dict[str, object]:
        """Serialize the exact fingerprinted revision."""
        return {**self._payload(), "prerequisite_fingerprint": self.prerequisite_fingerprint}

    @classmethod
    def from_persisted(cls, row: object) -> "PlatformPrivilegedEligibilityPrerequisite":
        """Strictly hydrate one persisted revision and reject corruption."""
        expected = {"schema", "version", "platform_prerequisite_id", "revision", "principal_id", "privilege_class", "scope", "status", "effective_from", "effective_until", "source_authority", "source_evidence_reference", "prerequisite_fingerprint"}
        if not isinstance(row, Mapping) or set(row) != expected or row.get("schema") != SCHEMA or row.get("version") != VERSION:
            raise PlatformPrivilegedEligibilityPrerequisiteError("PERSISTED_SHAPE_INVALID")
        try:
            start = datetime.fromisoformat(row["effective_from"]) if isinstance(row["effective_from"], str) else row["effective_from"]
            raw_end = row["effective_until"]
            end = datetime.fromisoformat(raw_end) if isinstance(raw_end, str) else raw_end
            return cls(row["platform_prerequisite_id"], row["revision"], row["principal_id"], row["privilege_class"], row["scope"], PlatformPrerequisiteStatus(row["status"]), start, end, row["source_authority"], row["source_evidence_reference"], row["prerequisite_fingerprint"])
        except (KeyError, TypeError, ValueError) as error:
            raise PlatformPrivilegedEligibilityPrerequisiteError("PERSISTED_RECORD_INVALID") from error


__all__ = ["PRIVILEGE_CLASS", "SCHEMA", "SCOPE", "SOURCE_AUTHORITY", "VERSION", "PlatformPrerequisiteStatus", "PlatformPrivilegedEligibilityPrerequisite", "PlatformPrivilegedEligibilityPrerequisiteError"]

# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: platform_privileged_eligibility_prerequisite.py
# VERSION: v1.0.0-P2-R3-PLATFORM-PREREQUISITE
# AUTHORITY BOUNDARY: exact Core-Governance P2 prerequisite leg only
# TENANT POSTURE: PLATFORM_SYSTEM only; no tenant delegation
# FAIL-CLOSED POSTURE: malformed scope, lineage, lifecycle, and fingerprints reject
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
