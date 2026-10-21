"""WILSY immutable ethical-wall restriction evidence.

VERSION: v1.0.1-P9-R105-P4G-P2R3
AUTHORITY: Restriction evidence only; no issuance, waiver, lift,
operational access, transport, reassignment or financial authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha3_512
from typing import Final, Mapping, cast
import json
import re

VERSION: Final[str] = "v1.0.1-P9-R105-P4G-P2R3"
SCHEMA: Final[str] = "WILSY-LEGAL-PRACTITIONER-ETHICAL-WALL-RESTRICTION/V1"
REASONS: Final[frozenset[str]] = frozenset({
    "CONFLICT_RESTRICTION",
    "CLIENT_CONFIDENTIALITY",
    "INFORMATION_BARRIER",
})
FIELDS: Final[frozenset[str]] = frozenset({
    "restriction_id", "tenant_id", "case_matter_id",
    "restricted_practitioner_principal_id",
    "source_evidence_fingerprint", "recorded_by_principal_id",
    "effective_from", "reason_code", "schema",
    "restriction_version", "fingerprint",
})

class LegalPractitionerEthicalWallRestrictionError(ValueError):
    """Stable, non-sensitive evidence validation failure."""

def _fail(code: str) -> None:
    raise LegalPractitionerEthicalWallRestrictionError(code)

def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or type(value) is not str:
        _fail("P9_WALL_" + name.upper() + "_INVALID")
    text = cast(str, value)
    if (
        not text or len(text) > 200 or text != text.strip()
        or any(ord(c) < 32 or ord(c) == 127 for c in text)
    ):
        _fail("P9_WALL_" + name.upper() + "_INVALID")
    return text

def _digest(value: object) -> str:
    if not isinstance(value, str) or type(value) is not str:
        _fail("P9_WALL_FINGERPRINT_INVALID")
    text = cast(str, value)
    if re.fullmatch("[0-9a-f]{128}", text) is None:
        _fail("P9_WALL_FINGERPRINT_INVALID")
    return text

def _instant(value: object) -> datetime:
    if not isinstance(value, datetime) or type(value) is not datetime:
        _fail("P9_WALL_TIME_INVALID")
    moment = cast(datetime, value)
    if moment.tzinfo is None or moment.utcoffset() is None:
        _fail("P9_WALL_TIME_INVALID")
    return moment.astimezone(timezone.utc)

@dataclass(frozen=True, slots=True)
class LegalPractitionerEthicalWallRestriction:
    restriction_id: str
    tenant_id: str
    case_matter_id: str
    restricted_practitioner_principal_id: str
    source_evidence_fingerprint: str
    recorded_by_principal_id: str
    effective_from: datetime
    reason_code: str
    schema: str = SCHEMA
    restriction_version: str = VERSION
    fingerprint: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        for name in (
            "restriction_id",
            "tenant_id",
            "case_matter_id",
            "restricted_practitioner_principal_id",
            "recorded_by_principal_id",
        ):
            object.__setattr__(
                self, name, _identity(name, getattr(self, name))
            )
        if type(self.reason_code) is not str or self.reason_code not in REASONS:
            _fail("P9_WALL_REASON_INVALID")
        object.__setattr__(
            self, "source_evidence_fingerprint",
            _digest(self.source_evidence_fingerprint),
        )
        object.__setattr__(
            self, "effective_from", _instant(self.effective_from)
        )
        if self.schema != SCHEMA or self.restriction_version != VERSION:
            _fail("P9_WALL_SCHEMA_VERSION_INVALID")
        material = json.dumps(
            self._material(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        computed = sha3_512(material).hexdigest()
        if self.fingerprint:
            if _digest(self.fingerprint) != computed:
                _fail("P9_WALL_INTEGRITY_INVALID")
        elif type(self.fingerprint) is not str:
            _fail("P9_WALL_FINGERPRINT_INVALID")
        object.__setattr__(self, "fingerprint", computed)

    def _material(self) -> dict[str, object]:
        return {
            "restriction_id": self.restriction_id,
            "tenant_id": self.tenant_id,
            "case_matter_id": self.case_matter_id,
            "restricted_practitioner_principal_id":
                self.restricted_practitioner_principal_id,
            "source_evidence_fingerprint": self.source_evidence_fingerprint,
            "recorded_by_principal_id": self.recorded_by_principal_id,
            "effective_from": self.effective_from.isoformat(),
            "reason_code": self.reason_code,
            "schema": self.schema,
            "restriction_version": self.restriction_version,
        }

    def to_dict(self) -> dict[str, object]:
        return {**self._material(), "fingerprint": self.fingerprint}

    @classmethod
    def from_dict(
        cls, payload: Mapping[str, object]
    ) -> LegalPractitionerEthicalWallRestriction:
        if not isinstance(payload, Mapping) or set(payload) != FIELDS:
            _fail("P9_WALL_PERSISTED_SHAPE_INVALID")

        raw_time = payload["effective_from"]
        if type(raw_time) is not str:
            _fail("P9_WALL_PERSISTED_TIME_INVALID")
        try:
            moment = datetime.fromisoformat(cast(str, raw_time))
        except ValueError as exc:
            raise LegalPractitionerEthicalWallRestrictionError(
                "P9_WALL_PERSISTED_TIME_INVALID"
            ) from exc

        value = cls(
            restriction_id=cast(str, payload["restriction_id"]),
            tenant_id=cast(str, payload["tenant_id"]),
            case_matter_id=cast(str, payload["case_matter_id"]),
            restricted_practitioner_principal_id=cast(
                str, payload["restricted_practitioner_principal_id"]
            ),
            source_evidence_fingerprint=cast(
                str, payload["source_evidence_fingerprint"]
            ),
            recorded_by_principal_id=cast(
                str, payload["recorded_by_principal_id"]
            ),
            effective_from=moment,
            reason_code=cast(str, payload["reason_code"]),
            schema=cast(str, payload["schema"]),
            restriction_version=cast(str, payload["restriction_version"]),
            fingerprint=cast(str, payload["fingerprint"]),
        )
        if value.to_dict() != dict(payload):
            _fail("P9_WALL_PERSISTED_NONCANONICAL")
        return value

# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.1-P9-R105-P4G-P2R3
# RESTRICTION FACT ONLY; NO CLEARANCE OR ACCESS GRANT
# END OF WILSY OS SOVEREIGN ARTIFACT
