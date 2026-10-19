"""TITLE: WILSY OS P9 Immutable Practitioner Matter Access Evidence.
VERSION: v1.0.1-P9-R85R1-PRACTITIONER-MATTER-ACCESS-HYDRATION
AUTHORITY: Python EOS Legal Operations immutable policy evidence only.
EPITOME: Exact tenant/matter/practitioner ALLOW or DENY documentary
    evidence, UTC effective intervals, immutable revisions and SHA3-512.
ABSOLUTE CANONICAL PATH:
    tools/eos/legal_operations/domain/legal_practitioner_matter_access.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-10-19
CHANGELOG:
    2026-10-19 v1.0.1-P9-R85R1-PRACTITIONER-MATTER-ACCESS-HYDRATION
    Require persisted SHA3-512 integrity on hydration; never heal absence.
    2026-10-19 v1.0.1-P9-R85R1-PRACTITIONER-MATTER-ACCESS-HYDRATION
    Establish strict immutable evidence, deterministic integrity and
    fail-closed hydration against the frozen R83R1 RED certificate.
TENANT BOUNDARY: Exact non-pseudo tenant, matter and practitioner.
AUTHORITY BOUNDARY: ALLOW/DENY records are documentary policy facts,
    not proof of issuer authority or affirmative access. No professional
    qualification, confidentiality clearance, IAM, approval, transaction,
    persistence or reassignment execution authority is established.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha3_512
import json
import re
from typing import Final, Mapping, cast


VERSION: Final[str] = "v1.0.1-P9-R85R1-PRACTITIONER-MATTER-ACCESS-HYDRATION"
SCHEMA: Final[str] = "WILSY-LEGAL-PRACTITIONER-MATTER-ACCESS-EVIDENCE/V1"
_HEX: Final[re.Pattern[str]] = re.compile(r"[0-9a-f]{128}")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "root", "*"}
)


class LegalPractitionerMatterAccessError(ValueError):
    """Bounded validation error; no tenant or matter identifiers exposed."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalPractitionerMatterAccessDecision(StrEnum):
    """Documentary decision kind, not a runtime access authorization."""

    ALLOW = "ALLOW"
    DENY = "DENY"


def _fail(code: str) -> None:
    raise LegalPractitionerMatterAccessError(code)


def _identity(name: str, value: object, limit: int = 200) -> str:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(char) < 33 or ord(char) == 127 for char in value)
    ):
        _fail("P9_R84_" + name.upper() + "_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value, 160)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("P9_R84_TENANT_ID_INVALID")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    if type(value) is not str or _HEX.fullmatch(value) is None:
        _fail("P9_R84_" + name.upper() + "_INVALID")
    return cast(str, value)


def _timestamp(name: str, value: object) -> datetime:
    if (
        type(value) is not datetime
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _fail("P9_R84_" + name.upper() + "_INVALID")
    return cast(datetime, value).astimezone(timezone.utc)


def _optional_timestamp(name: str, value: object) -> datetime | None:
    return None if value is None else _timestamp(name, value)


def _parse_time(name: str, value: object) -> datetime:
    if type(value) is not str:
        _fail("P9_R84_" + name.upper() + "_INVALID")
    try:
        parsed = datetime.fromisoformat(cast(str, value))
    except ValueError:
        _fail("P9_R84_" + name.upper() + "_INVALID")
        raise AssertionError("unreachable")
    return _timestamp(name, parsed)


_FIELDS: Final[frozenset[str]] = frozenset({
    "access_evidence_id",
    "tenant_id",
    "case_matter_id",
    "practitioner_principal_id",
    "revision",
    "decision",
    "effective_from",
    "effective_until",
    "issued_by_principal_id",
    "source_evidence_fingerprint",
    "supersedes_fingerprint",
    "schema",
    "evidence_version",
    "fingerprint",
})


@dataclass(frozen=True, slots=True, kw_only=True)
class LegalPractitionerMatterAccessEvidence:
    """Immutable policy evidence; does not establish valid issuance."""

    access_evidence_id: str
    tenant_id: str
    case_matter_id: str
    practitioner_principal_id: str
    revision: int
    decision: LegalPractitionerMatterAccessDecision
    effective_from: datetime
    effective_until: datetime | None
    issued_by_principal_id: str
    source_evidence_fingerprint: str
    supersedes_fingerprint: str | None
    schema: str = SCHEMA
    evidence_version: str = VERSION
    fingerprint: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        normalized = {
            "access_evidence_id": _identity(
                "access_evidence_id", self.access_evidence_id
            ),
            "tenant_id": _tenant(self.tenant_id),
            "case_matter_id": _identity(
                "case_matter_id", self.case_matter_id
            ),
            "practitioner_principal_id": _identity(
                "practitioner_principal_id",
                self.practitioner_principal_id,
            ),
            "issued_by_principal_id": _identity(
                "issued_by_principal_id", self.issued_by_principal_id
            ),
            "source_evidence_fingerprint": _fingerprint(
                "source_evidence_fingerprint",
                self.source_evidence_fingerprint,
            ),
            "effective_from": _timestamp(
                "effective_from", self.effective_from
            ),
            "effective_until": _optional_timestamp(
                "effective_until", self.effective_until
            ),
        }

        if type(self.revision) is not int or self.revision < 1:
            _fail("P9_R84_REVISION_INVALID")

        if type(self.decision) is not LegalPractitionerMatterAccessDecision:
            _fail("P9_R84_DECISION_INVALID")

        if self.schema != SCHEMA or self.evidence_version != VERSION:
            _fail("P9_R84_SCHEMA_VERSION_INVALID")

        predecessor = (
            None
            if self.supersedes_fingerprint is None
            else _fingerprint(
                "supersedes_fingerprint",
                self.supersedes_fingerprint,
            )
        )

        if self.revision == 1 and predecessor is not None:
            _fail("P9_R84_FIRST_REVISION_PREDECESSOR_FORBIDDEN")

        if self.revision > 1 and predecessor is None:
            _fail("P9_R84_LATER_REVISION_PREDECESSOR_REQUIRED")

        until = normalized["effective_until"]
        start = normalized["effective_from"]

        if until is not None and until <= start:
            _fail("P9_R84_EFFECTIVE_INTERVAL_INVALID")

        for name, value in normalized.items():
            object.__setattr__(self, name, value)

        payload = self._material()
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        computed = sha3_512(encoded).hexdigest()

        if self.fingerprint:
            if _fingerprint("fingerprint", self.fingerprint) != computed:
                _fail("P9_R84_FINGERPRINT_MISMATCH")
        elif type(self.fingerprint) is not str:
            _fail("P9_R84_FINGERPRINT_INVALID")

        object.__setattr__(self, "fingerprint", computed)

    def _material(self) -> dict[str, object]:
        return {
            "access_evidence_id": self.access_evidence_id,
            "tenant_id": self.tenant_id,
            "case_matter_id": self.case_matter_id,
            "practitioner_principal_id": self.practitioner_principal_id,
            "revision": self.revision,
            "decision": self.decision.value,
            "effective_from": self.effective_from.isoformat(),
            "effective_until": (
                None
                if self.effective_until is None
                else self.effective_until.isoformat()
            ),
            "issued_by_principal_id": self.issued_by_principal_id,
            "source_evidence_fingerprint": self.source_evidence_fingerprint,
            "supersedes_fingerprint": self.supersedes_fingerprint,
            "schema": self.schema,
            "evidence_version": self.evidence_version,
        }

    def to_dict(self) -> dict[str, object]:
        """Return exact integrity-protected documentary evidence."""
        return {**self._material(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> LegalPractitionerMatterAccessEvidence:
        """Strict hydration with no unknown, absent or forged fields."""
        if not isinstance(payload, Mapping):
            _fail("P9_R84_PERSISTED_SHAPE_INVALID")

        if set(payload) != _FIELDS:
            _fail("P9_R84_PERSISTED_SHAPE_INVALID")

        try:
            decision = LegalPractitionerMatterAccessDecision(
                payload["decision"]
            )
        except (ValueError, TypeError):
            _fail("P9_R84_DECISION_INVALID")
            raise AssertionError("unreachable")

        # Persisted evidence cannot bootstrap or repair its own integrity.
        _fingerprint("fingerprint", payload["fingerprint"])

        raw_until = payload["effective_until"]

        return cls(
            access_evidence_id=cast(str, payload["access_evidence_id"]),
            tenant_id=cast(str, payload["tenant_id"]),
            case_matter_id=cast(str, payload["case_matter_id"]),
            practitioner_principal_id=cast(
                str, payload["practitioner_principal_id"]
            ),
            revision=cast(int, payload["revision"]),
            decision=decision,
            effective_from=_parse_time(
                "effective_from", payload["effective_from"]
            ),
            effective_until=(
                None if raw_until is None
                else _parse_time("effective_until", raw_until)
            ),
            issued_by_principal_id=cast(
                str, payload["issued_by_principal_id"]
            ),
            source_evidence_fingerprint=cast(
                str, payload["source_evidence_fingerprint"]
            ),
            supersedes_fingerprint=cast(
                str | None, payload["supersedes_fingerprint"]
            ),
            schema=cast(str, payload["schema"]),
            evidence_version=cast(str, payload["evidence_version"]),
            fingerprint=cast(str, payload["fingerprint"]),
        )


__all__ = [
    "VERSION",
    "SCHEMA",
    "LegalPractitionerMatterAccessError",
    "LegalPractitionerMatterAccessDecision",
    "LegalPractitionerMatterAccessEvidence",
]


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: legal_practitioner_matter_access.py
# VERSION: v1.0.1-P9-R85R1-PRACTITIONER-MATTER-ACCESS-HYDRATION
# AUTHORITY BOUNDARY: immutable documentary policy evidence only
# AFFIRMATIVE MATTER ACCESS / ISSUANCE AUTHORITY: NOT GRANTED
# ETHICAL WALL / PROFESSIONAL STATUS / APPROVAL: NOT GRANTED
# REASSIGNMENT EXECUTION / PERSISTENCE: NONE
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
