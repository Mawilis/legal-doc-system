"""Immutable lifecycle evidence for one matter acceptance instrument version.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument Lifecycle
VERSION: v1.0.0-L9A4-P2A-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Represent one immutable, tenant- and CaseMatter-scoped lifecycle
         fact for one exact client-review instrument version. The value keeps
         ACTIVE, SUPERSEDED, RETIRED and WITHDRAWN distinct and records the
         evidence needed for a later durable lifecycle registry. It does not
         infer current approval or presentation eligibility.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_acceptance_instrument_lifecycle.py
COLLABORATION / OWNERSHIP: L9A4-P1B owns immutable instrument identity and
                            content provenance; this P2A domain owns only
                            lifecycle fact shape and transition semantics. A
                            later registry owns chronology across facts. IAM,
                            visibility, acting capacity and approval remain
                            separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2A-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE establishes
           explicit ACTIVE baseline evidence, terminal SUPERSEDED/RETIRED/
           WITHDRAWN transitions, exact successor linkage, UTC chronology,
           strict hydration and deterministic SHA3-512 integrity. It creates
           no registry, approval, acceptance, engagement, Court or finance
           authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers, bounded evidence references
                             and lowercase SHA3-512 fingerprints only; no
                             client PII, credentials, tokens or narrative
                             withdrawal reasons are stored here.
TENANT BOUNDARY: Tenant, CaseMatter, instrument and version are explicit and
                 immutable. Successor identity must remain in the same exact
                 instrument chain; no cross-tenant or cross-matter inference
                 is possible in this value.
AUTHORITY BOUNDARY: Lifecycle evidence only. Existence of ACTIVE evidence
                    is not approval currentness, visibility, IAM permission,
                    acting capacity, presentation eligibility or acceptance.
                    Terminal evidence remains historical and cannot reactivate
                    a version.
FINANCIAL AUTHORITY BOUNDARY: No fee, billing, payment, execution or
                              settlement truth; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Pure immutable construction, serialization and
                      hydration only; no database, HTTP, registry, IAM,
                      transaction, retry, notification or browser behavior.
FAIL-CLOSED DECLARATION: Invalid identity, state, transition metadata,
                         chronology, provenance, schema or fingerprint raises
                         a bounded error without coercion or fallback.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast
import unicodedata


VERSION: Final[str] = "v1.0.0-L9A4-P2A-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "lifecycle_version",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "instrument_id",
    "version",
    "instrument_fingerprint",
    "status",
    "prior_status",
    "occurred_at",
    "lifecycle_evidence_reference",
    "lifecycle_evidence_fingerprint",
    "superseding_version_id",
    "superseding_instrument_fingerprint",
    "fingerprint",
)
LIFECYCLE_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterAcceptanceInstrumentLifecycleError(ValueError):
    """Stable, non-sensitive lifecycle validation failure."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code and never supplied lifecycle data."""
        self.code = code
        super().__init__(code)


class LegalClientMatterAcceptanceInstrumentLifecycleStatus(StrEnum):
    """Explicit lifecycle vocabulary for one immutable instrument version."""

    ACTIVE = "ACTIVE"
    SUPERSEDED = "SUPERSEDED"
    RETIRED = "RETIRED"
    WITHDRAWN = "WITHDRAWN"


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one bounded error while retaining only an internal cause."""
    error = LegalClientMatterAcceptanceInstrumentLifecycleError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Require one bounded opaque identity without trimming or coercion."""
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"L9A4_P2A_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require an explicit non-global tenant identity."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9A4_P2A_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require lowercase SHA3-512 hexadecimal evidence."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9A4_P2A_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    """Require bounded NFC evidence reference without exposing narrative data."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(
            ord(character) < 32
            or 0x7F <= ord(character) <= 0x9F
            or 0xD800 <= ord(character) <= 0xDFFF
            for character in value
        )
    ):
        _fail(f"L9A4_P2A_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if normalized != value or not normalized:
        _fail(f"L9A4_P2A_{name.upper()}_INVALID")
    return normalized


def _timestamp(name: str, value: object) -> datetime:
    """Require aware chronology and normalize it to UTC with microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9A4_P2A_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L9A4_P2A_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Convert immutable lifecycle values to deterministic JSON-safe values."""
    if isinstance(value, datetime):
        return (
            value.astimezone(timezone.utc)
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z")
        )
    if isinstance(value, StrEnum):
        return value.value
    return value


def _sha3(payload: Mapping[str, object]) -> str:
    """Return the canonical SHA3-512 digest of semantic lifecycle payload."""
    encoded = json.dumps(
        {key: _json_value(value) for key, value in payload.items()},
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha3_512(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class LegalClientMatterAcceptanceInstrumentLifecycle:
    """One immutable lifecycle fact for one exact instrument version.

    ``ACTIVE`` is an explicit baseline event; instrument persistence alone does
    not imply eligibility. Terminal states require ``prior_status=ACTIVE`` and
    cannot be reactivated in this version. The future registry owns ordering
    across multiple facts and caller-owned persistence; this value performs no
    database or authority lookup.
    """

    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    instrument_id: str
    version: str
    instrument_fingerprint: str
    status: LegalClientMatterAcceptanceInstrumentLifecycleStatus
    prior_status: LegalClientMatterAcceptanceInstrumentLifecycleStatus | None
    occurred_at: datetime
    lifecycle_evidence_reference: str
    lifecycle_evidence_fingerprint: str
    superseding_version_id: str | None = None
    superseding_instrument_fingerprint: str | None = None
    schema: str = SCHEMA
    lifecycle_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact scope, transition metadata and deterministic integrity."""
        tenant = _tenant(self.tenant_id)
        matter = _identity("case_matter_id", self.case_matter_id)
        matter_fingerprint = _fingerprint("matter_fingerprint", self.matter_fingerprint)
        instrument = _identity("instrument_id", self.instrument_id)
        version = _identity("version", self.version)
        instrument_fingerprint = _fingerprint(
            "instrument_fingerprint", self.instrument_fingerprint
        )
        evidence_reference = _reference(
            "lifecycle_evidence_reference", self.lifecycle_evidence_reference
        )
        evidence_fingerprint = _fingerprint(
            "lifecycle_evidence_fingerprint", self.lifecycle_evidence_fingerprint
        )
        occurred_at = _timestamp("occurred_at", self.occurred_at)
        if self.schema != SCHEMA or self.lifecycle_version != VERSION:
            _fail("L9A4_P2A_IDENTITY_INVALID")
        if not isinstance(self.status, LegalClientMatterAcceptanceInstrumentLifecycleStatus):
            _fail("L9A4_P2A_STATUS_INVALID")
        if self.prior_status is not None and not isinstance(
            self.prior_status, LegalClientMatterAcceptanceInstrumentLifecycleStatus
        ):
            _fail("L9A4_P2A_PRIOR_STATUS_INVALID")

        successor = self.superseding_version_id
        successor_fingerprint = self.superseding_instrument_fingerprint
        if self.status is LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE:
            if self.prior_status is not None:
                _fail("L9A4_P2A_ACTIVE_PRIOR_STATUS_FORBIDDEN")
            if successor is not None or successor_fingerprint is not None:
                _fail("L9A4_P2A_ACTIVE_SUCCESSOR_FORBIDDEN")
        elif self.prior_status is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE:
            _fail("L9A4_P2A_TERMINAL_PRIOR_STATUS_REQUIRED")

        if self.status is LegalClientMatterAcceptanceInstrumentLifecycleStatus.SUPERSEDED:
            if successor is None or successor_fingerprint is None:
                _fail("L9A4_P2A_SUPERSESSION_SUCCESSOR_REQUIRED")
            successor = _identity("superseding_version_id", successor)
            successor_fingerprint = _fingerprint(
                "superseding_instrument_fingerprint", successor_fingerprint
            )
            expected_prefix = f"{instrument}:"
            if not successor.startswith(expected_prefix):
                _fail("L9A4_P2A_CROSS_INSTRUMENT_SUCCESSOR")
            if successor == f"{instrument}:{version}":
                _fail("L9A4_P2A_SELF_SUPERSESSION")
        elif successor is not None or successor_fingerprint is not None:
            _fail("L9A4_P2A_NON_SUPERSEDED_SUCCESSOR_FORBIDDEN")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "case_matter_id", matter)
        object.__setattr__(self, "matter_fingerprint", matter_fingerprint)
        object.__setattr__(self, "instrument_id", instrument)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "instrument_fingerprint", instrument_fingerprint)
        object.__setattr__(self, "occurred_at", occurred_at)
        object.__setattr__(self, "lifecycle_evidence_reference", evidence_reference)
        object.__setattr__(self, "lifecycle_evidence_fingerprint", evidence_fingerprint)
        object.__setattr__(self, "superseding_version_id", successor)
        object.__setattr__(self, "superseding_instrument_fingerprint", successor_fingerprint)

        payload = {
            field: _json_value(getattr(self, field)) for field in _FIELDS[:-1]
        }
        digest = _sha3(payload)
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9A4_P2A_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def version_id(self) -> str:
        """Return the exact instrument/version identity used for succession."""
        return f"{self.instrument_id}:{self.version}"

    @property
    def is_terminal(self) -> bool:
        """Return whether this immutable fact records a terminal lifecycle state."""
        return self.status is not LegalClientMatterAcceptanceInstrumentLifecycleStatus.ACTIVE

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact lifecycle schema with its derived fingerprint."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalClientMatterAcceptanceInstrumentLifecycle":
        """Hydrate only exact fields and verify the supplied fingerprint."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9A4_P2A_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        try:
            if isinstance(values.get("status"), str):
                values["status"] = LegalClientMatterAcceptanceInstrumentLifecycleStatus(
                    values["status"]
                )
            if isinstance(values.get("prior_status"), str):
                values["prior_status"] = LegalClientMatterAcceptanceInstrumentLifecycleStatus(
                    values["prior_status"]
                )
        except ValueError as error:
            _fail("L9A4_P2A_STATUS_INVALID", error)
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, result.fingerprint):
            _fail("L9A4_P2A_FINGERPRINT_MISMATCH")
        return result


def record_legal_client_matter_acceptance_instrument_lifecycle(
    *,
    tenant_id: str,
    case_matter_id: str,
    matter_fingerprint: str,
    instrument_id: str,
    version: str,
    instrument_fingerprint: str,
    status: LegalClientMatterAcceptanceInstrumentLifecycleStatus,
    occurred_at: datetime,
    lifecycle_evidence_reference: str,
    lifecycle_evidence_fingerprint: str,
    prior_status: LegalClientMatterAcceptanceInstrumentLifecycleStatus | None = None,
    superseding_version_id: str | None = None,
    superseding_instrument_fingerprint: str | None = None,
) -> LegalClientMatterAcceptanceInstrumentLifecycle:
    """Construct one explicit immutable lifecycle fact without persistence.

    Callers must supply canonical instrument identity and evidence already
    obtained from their governing authorities. This function does not infer
    approval, visibility, capacity, acceptance, engagement or finance state.
    """
    return LegalClientMatterAcceptanceInstrumentLifecycle(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        matter_fingerprint=matter_fingerprint,
        instrument_id=instrument_id,
        version=version,
        instrument_fingerprint=instrument_fingerprint,
        status=status,
        prior_status=prior_status,
        occurred_at=occurred_at,
        lifecycle_evidence_reference=lifecycle_evidence_reference,
        lifecycle_evidence_fingerprint=lifecycle_evidence_fingerprint,
        superseding_version_id=superseding_version_id,
        superseding_instrument_fingerprint=superseding_instrument_fingerprint,
    )


__all__ = [
    "LIFECYCLE_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterAcceptanceInstrumentLifecycle",
    "LegalClientMatterAcceptanceInstrumentLifecycleError",
    "LegalClientMatterAcceptanceInstrumentLifecycleStatus",
    "record_legal_client_matter_acceptance_instrument_lifecycle",
]


# ARTIFACT: legal_client_matter_acceptance_instrument_lifecycle.py
# VERSION: v1.0.0-L9A4-P2A-MATTER-ACCEPTANCE-INSTRUMENT-LIFECYCLE
# AUTHORITY BOUNDARY: immutable lifecycle evidence for one exact instrument version only
# TENANT POSTURE: explicit tenant/matter/instrument/version binding; no cross-scope inference
# FAIL-CLOSED POSTURE: illegal transitions, malformed evidence, naive chronology and fingerprint drift reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
