"""WILSY OS immutable client acting-capacity evidence domain.

TITLE: WILSY OS Legal Client Acting Capacity
VERSION: v1.0.0-L9A4-P1A-CLIENT-ACTING-CAPACITY
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Bind one authenticated client principal to one exact tenant-scoped
         CaseMatter and one exact LegalMatterParty with a deliberately small
         capacity vocabulary, explicit source provenance, bounded validity and
         deterministic SHA3-512 integrity. This value is evidence of a bounded
         claimed capacity only; it is not a legal-sufficiency determination.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_acting_capacity.py
COLLABORATION / OWNERSHIP: P1 owns CaseMatter truth; L8-8A owns the exact
                            LegalMatterParty association; IAM owns principal
                            authentication, lifecycle, membership and role
                            authority; L9A4-P1A owns only this immutable
                            principal-to-party capacity evidence. A later
                            registry and orchestrator must independently prove
                            current authority and source-evidence sufficiency.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P1A-CLIENT-ACTING-CAPACITY establishes exact
           CaseMatter/LegalMatterParty correlation, bounded SELF/
           AUTHORIZED_AGENT/REPRESENTATIVE vocabulary, opaque principal and
           subject identity, aware-UTC validity chronology, distinct acting-
           capacity provenance, exact hydration and deterministic SHA3-512
           integrity. It creates no acceptance, engagement, representation,
           Court or financial authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque principal, party and subject references
                             plus lowercase SHA3-512 evidence fingerprints only;
                             no names, email, address, credentials, tokens,
                             legal narrative, identity numbers or raw PII.
TENANT BOUNDARY: Tenant, matter identity and matter fingerprint are derived
                 from one exact OPEN CaseMatter; party identity and subject
                 fields are derived from one exact matching LegalMatterParty.
AUTHORITY BOUNDARY: Immutable evidence that source E records principal P's
                    bounded capacity C to act for party X in matter M. It does
                    not authenticate P, grant IAM, prove membership or role,
                    establish visibility, acceptance, engagement, retainer,
                    mandate, law-firm representation, Court authority or legal
                    sufficiency.
FINANCIAL AUTHORITY BOUNDARY: No fee, billing, payment, execution or
                              settlement truth; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Pure immutable in-memory construction and deterministic
                      serialization only; no database, HTTP, IAM, transaction,
                      retry, notification or persistence behavior.
FAIL-CLOSED DECLARATION: Malformed identities, pseudo tenants, non-canonical
                         matter/party correlation, invalid capacity,
                         timezone-naive chronology, invalid intervals, schema
                         drift and fingerprint divergence reject without
                         coercion or authority expansion.
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

from tools.eos.legal_operations.domain.legal_matter_party import LegalMatterParty
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)


VERSION: Final[str] = "v1.0.0-L9A4-P1A-CLIENT-ACTING-CAPACITY"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-ACTING-CAPACITY/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_SUBJECT_REFERENCE: Final[re.Pattern[str]] = re.compile(
    r"^(crm|contact|organization|entity|client|subject):"
    r"[A-Za-z0-9][A-Za-z0-9._:-]{0,191}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalClientActingCapacityError(ValueError):
    """Stable, non-sensitive failure for acting-capacity value validation."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded validation code, never supplied authority data."""
        self.code = code
        super().__init__(code)


class LegalClientActingCapacityType(StrEnum):
    """Small descriptive capacity vocabulary without legal taxonomy claims."""

    SELF = "SELF"
    AUTHORIZED_AGENT = "AUTHORIZED_AGENT"
    REPRESENTATIVE = "REPRESENTATIVE"


_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "capacity_version",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "capacity_id",
    "principal_id",
    "party_id",
    "subject_reference",
    "subject_identity_fingerprint",
    "capacity_type",
    "effective_from",
    "effective_until",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "fingerprint",
)
ACTING_CAPACITY_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one stable failure while retaining an internal technical cause."""
    error = LegalClientActingCapacityError(code)
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
        _fail(f"L9A4_P1A_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require one explicit tenant and reject pseudo/global scope."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9A4_P1A_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal evidence fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9A4_P1A_{name.upper()}_INVALID")
    return value


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    """Require bounded single-line NFC evidence/reference text."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(ord(character) < 32 for character in value)
    ):
        _fail(f"L9A4_P1A_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or len(normalized) > limit:
        _fail(f"L9A4_P1A_{name.upper()}_INVALID")
    return normalized


def _subject_reference(value: object) -> str:
    """Require the opaque subject-reference vocabulary used by matter parties."""
    reference = _reference("subject_reference", value, limit=224)
    if _SUBJECT_REFERENCE.fullmatch(reference) is None:
        _fail("L9A4_P1A_SUBJECT_REFERENCE_INVALID")
    return reference


def _timestamp(name: str, value: object) -> datetime:
    """Require aware chronology and normalize it to UTC with microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9A4_P1A_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L9A4_P1A_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Convert immutable values to deterministic JSON-safe values."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
            "+00:00", "Z"
        )
    if isinstance(value, StrEnum):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class LegalClientActingCapacity:
    """Immutable principal-to-party capacity evidence for one exact matter.

    Direct construction validates documentary fields and deterministic
    integrity. :func:`record_legal_client_acting_capacity` is the authoritative
    factory: it derives tenant, matter, party and subject identity from exact
    canonical ``CaseMatter`` and ``LegalMatterParty`` values. Neither path
    authenticates the principal or grants any runtime permission; a later
    orchestrator owns those checks and any caller-owned transaction.
    """

    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    capacity_id: str
    principal_id: str
    party_id: str
    subject_reference: str
    subject_identity_fingerprint: str
    capacity_type: LegalClientActingCapacityType | str
    effective_from: datetime
    effective_until: datetime | None
    source_evidence_reference: str
    source_evidence_fingerprint: str
    schema: str = SCHEMA
    capacity_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate every semantic field and compute/verify integrity."""
        tenant = _tenant(self.tenant_id)
        matter_id = _identity("case_matter_id", self.case_matter_id)
        matter_fingerprint = _fingerprint("matter_fingerprint", self.matter_fingerprint)
        capacity_id = _identity("capacity_id", self.capacity_id)
        principal = _identity("principal_id", self.principal_id)
        party_id = _identity("party_id", self.party_id)
        subject = _subject_reference(self.subject_reference)
        subject_fingerprint = _fingerprint(
            "subject_identity_fingerprint", self.subject_identity_fingerprint
        )
        try:
            capacity_type = LegalClientActingCapacityType(self.capacity_type)
        except (TypeError, ValueError) as error:
            _fail("L9A4_P1A_CAPACITY_TYPE_INVALID", error)
        effective_from = _timestamp("effective_from", self.effective_from)
        effective_until = (
            None
            if self.effective_until is None
            else _timestamp("effective_until", self.effective_until)
        )
        if effective_until is not None and effective_until <= effective_from:
            _fail("L9A4_P1A_VALIDITY_INTERVAL_INVALID")
        source_reference = _reference(
            "source_evidence_reference", self.source_evidence_reference
        )
        source_fingerprint = _fingerprint(
            "source_evidence_fingerprint", self.source_evidence_fingerprint
        )
        if self.schema != SCHEMA or self.capacity_version != VERSION:
            _fail("L9A4_P1A_IDENTITY_INVALID")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "case_matter_id", matter_id)
        object.__setattr__(self, "matter_fingerprint", matter_fingerprint)
        object.__setattr__(self, "capacity_id", capacity_id)
        object.__setattr__(self, "principal_id", principal)
        object.__setattr__(self, "party_id", party_id)
        object.__setattr__(self, "subject_reference", subject)
        object.__setattr__(self, "subject_identity_fingerprint", subject_fingerprint)
        object.__setattr__(self, "capacity_type", capacity_type)
        object.__setattr__(self, "effective_from", effective_from)
        object.__setattr__(self, "effective_until", effective_until)
        object.__setattr__(self, "source_evidence_reference", source_reference)
        object.__setattr__(self, "source_evidence_fingerprint", source_fingerprint)

        payload = {
            field: _json_value(getattr(self, field)) for field in _FIELDS[:-1]
        }
        digest = hashlib.sha3_512(
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9A4_P1A_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize the complete immutable evidence snapshot without PII."""
        return {
            field: _json_value(getattr(self, field)) for field in _FIELDS
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalClientActingCapacity":
        """Hydrate only the exact schema and verify its deterministic fingerprint."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9A4_P1A_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(
            stored, result.fingerprint
        ):
            _fail("L9A4_P1A_FINGERPRINT_MISMATCH")
        return result


def record_legal_client_acting_capacity(
    *,
    case_matter: CaseMatter,
    party: LegalMatterParty,
    capacity_id: str,
    principal_id: str,
    capacity_type: LegalClientActingCapacityType | str,
    effective_from: datetime,
    effective_until: datetime | None = None,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
) -> LegalClientActingCapacity:
    """Record capacity from exact canonical matter and party evidence.

    The factory requires an OPEN ``CaseMatter`` and an exact
    ``LegalMatterParty`` whose tenant, matter identifier, matter fingerprint,
    party identifier, subject reference and subject fingerprint all match the
    supplied matter. It never derives a party from visibility, a role, a name,
    email, username or browser claim. It also does not prove authentication,
    membership, LEGAL_CLIENT permission, legal sufficiency or source authority;
    those are mandatory later-orchestrator responsibilities.
    """
    if type(case_matter) is not CaseMatter:
        _fail("L9A4_P1A_CASE_MATTER_REQUIRED")
    if type(party) is not LegalMatterParty:
        _fail("L9A4_P1A_LEGAL_MATTER_PARTY_REQUIRED")
    try:
        case_matter.__post_init__()
        party.__post_init__()
    except Exception as error:
        _fail("L9A4_P1A_CANONICAL_EVIDENCE_INVALID", error)
    if case_matter.state is not CaseMatterState.OPEN:
        _fail("L9A4_P1A_OPEN_CASE_MATTER_REQUIRED")
    if (
        party.tenant_id != case_matter.tenant_id
        or party.case_matter_id != case_matter.case_matter_id
        or party.matter_fingerprint != case_matter.fingerprint
    ):
        _fail("L9A4_P1A_PARTY_MATTER_MISMATCH")
    return LegalClientActingCapacity(
        tenant_id=case_matter.tenant_id,
        case_matter_id=case_matter.case_matter_id,
        matter_fingerprint=case_matter.fingerprint,
        capacity_id=capacity_id,
        principal_id=principal_id,
        party_id=party.party_id,
        subject_reference=party.subject_reference,
        subject_identity_fingerprint=party.subject_identity_fingerprint,
        capacity_type=capacity_type,
        effective_from=effective_from,
        effective_until=effective_until,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
    )


__all__ = [
    "ACTING_CAPACITY_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientActingCapacity",
    "LegalClientActingCapacityError",
    "LegalClientActingCapacityType",
    "record_legal_client_acting_capacity",
]


# ARTIFACT: legal_client_acting_capacity.py
# VERSION: v1.0.0-L9A4-P1A-CLIENT-ACTING-CAPACITY
# AUTHORITY BOUNDARY: immutable bounded principal-to-party capacity evidence only
# TENANT POSTURE: tenant/matter/party derive from exact OPEN CaseMatter and party
# FAIL-CLOSED POSTURE: malformed, mismatched, naive, drifted, or tampered evidence rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
