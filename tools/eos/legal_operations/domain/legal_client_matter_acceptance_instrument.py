"""WILSY OS immutable matter-specific client-review instrument domain.

TITLE: WILSY OS Legal Client Matter Acceptance Instrument
VERSION: v1.0.0-L9A4-P1B-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Describe one exact tenant- and CaseMatter-scoped, immutable,
         client-reviewable instrument version. This value identifies the
         material that a later acceptance context may present; it is not an
         acceptance, engagement, representation, Court or financial decision.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_acceptance_instrument.py
COLLABORATION / OWNERSHIP: P1 CaseMatter owns matter identity and lifecycle;
                            L9A4-P1A owns acting-capacity evidence separately;
                            this L9A4-P1B domain owns only immutable reviewable
                            instrument metadata and content provenance. A
                            future registry/orchestrator owns admission and
                            current-version selection; L9A owns acceptance.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P1B-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT establishes
           exact tenant/matter binding, neutral instrument identity and kind,
           bounded human review scope, immutable content and approval evidence,
           UTC chronology, optional supersession and deterministic SHA3-512
           integrity without creating acceptance or engagement authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Opaque identifiers, bounded NFC metadata and
                             lowercase SHA3-512 references only; no client
                             names, contacts, identity numbers or document
                             body is duplicated in this metadata domain.
TENANT BOUNDARY: Tenant and matter identity/fingerprint derive only from one
                 exact canonical CaseMatter; party/audience selection remains
                 outside this value and is resolved by a later context.
AUTHORITY BOUNDARY: Immutable client-reviewable source-material identity and
                    provenance only. It does not authenticate a person, grant
                    visibility, establish capacity, acceptance, engagement,
                    retainer, mandate, representation, Court or legal outcome.
FINANCIAL AUTHORITY BOUNDARY: No fee, billing, payment, execution or
                              settlement truth; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Pure immutable construction, deterministic serialization
                      and hydration only; no database, HTTP, IAM, registry,
                      transaction, retry, notification or client behavior.
FAIL-CLOSED DECLARATION: Malformed identity, controls, chronology, evidence,
                         schema, supersession or fingerprint drift rejects
                         without coercion or authority expansion.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Final, NoReturn, cast
import unicodedata

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
)


VERSION: Final[str] = "v1.0.0-L9A4-P1B-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT/V1"
_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "instrument_version",
    "tenant_id",
    "case_matter_id",
    "matter_fingerprint",
    "instrument_id",
    "version",
    "instrument_kind",
    "title",
    "review_scope",
    "content_reference",
    "content_fingerprint",
    "created_at",
    "effective_from",
    "approval_evidence_reference",
    "approval_evidence_fingerprint",
    "supersedes_version_id",
    "fingerprint",
)
INSTRUMENT_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterAcceptanceInstrumentError(ValueError):
    """Stable, non-sensitive failure for instrument validation."""

    def __init__(self, code: str) -> None:
        """Expose only a bounded code; never include supplied metadata."""
        self.code = code
        super().__init__(code)


def _fail(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one fail-closed error while retaining only an internal cause."""
    error = LegalClientMatterAcceptanceInstrumentError(code)
    if cause is None:
        raise error
    raise error from cause


def _identity(name: str, value: object) -> str:
    """Require one bounded opaque identifier without trimming or coercion."""
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"L9A4_P1B_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    """Require explicit tenant scope and reject pseudo/global tenants."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("L9A4_P1B_TENANT_REQUIRED")
    return tenant


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512 hexadecimal evidence fingerprint."""
    if not isinstance(value, str) or _HEX.fullmatch(value) is None:
        _fail(f"L9A4_P1B_{name.upper()}_INVALID")
    return value


def _text(name: str, value: object, *, limit: int) -> str:
    """Require bounded NFC text with no control or surrogate code points."""
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L9A4_P1B_{name.upper()}_INVALID")
    normalized = unicodedata.normalize("NFC", value)
    if (
        not normalized
        or len(normalized) > limit
        or any(
            ord(character) < 32
            or 0x7F <= ord(character) <= 0x9F
            or 0xD800 <= ord(character) <= 0xDFFF
            for character in normalized
        )
    ):
        _fail(f"L9A4_P1B_{name.upper()}_INVALID")
    return normalized


def _reference(name: str, value: object, *, limit: int = 512) -> str:
    """Require bounded immutable-content/provenance reference text."""
    return _text(name, value, limit=limit)


def _timestamp(name: str, value: object) -> datetime:
    """Require aware chronology and normalize it to UTC with microseconds."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            _fail(f"L9A4_P1B_{name.upper()}_INVALID", error)
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        _fail(f"L9A4_P1B_{name.upper()}_INVALID")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Convert immutable values to deterministic JSON-safe values."""
    if isinstance(value, datetime):
        return (
            value.astimezone(timezone.utc)
            .isoformat(timespec="microseconds")
            .replace("+00:00", "Z")
        )
    return value


@dataclass(frozen=True, slots=True)
class LegalClientMatterAcceptanceInstrument:
    """Immutable, matter-scoped material a client may later review.

    The instrument deliberately binds only one exact CaseMatter, not a party
    or audience. A common instrument version may be reviewed by several
    client-side parties; a future acceptance context must independently bind
    its actor, party, visibility and acting-capacity evidence. This object has
    no persistence or transaction authority and cannot record acceptance.
    """

    tenant_id: str
    case_matter_id: str
    matter_fingerprint: str
    instrument_id: str
    version: str
    instrument_kind: str
    title: str
    review_scope: str
    content_reference: str
    content_fingerprint: str
    created_at: datetime
    effective_from: datetime
    approval_evidence_reference: str
    approval_evidence_fingerprint: str
    supersedes_version_id: str | None = None
    schema: str = SCHEMA
    instrument_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate all fields and establish deterministic semantic integrity."""
        tenant = _tenant(self.tenant_id)
        matter_id = _identity("case_matter_id", self.case_matter_id)
        matter_fingerprint = _fingerprint("matter_fingerprint", self.matter_fingerprint)
        instrument_id = _identity("instrument_id", self.instrument_id)
        version = _identity("version", self.version)
        kind = _identity("instrument_kind", self.instrument_kind)
        title = _text("title", self.title, limit=200)
        review_scope = _text("review_scope", self.review_scope, limit=1000)
        content_reference = _reference("content_reference", self.content_reference)
        content_fingerprint = _fingerprint("content_fingerprint", self.content_fingerprint)
        created_at = _timestamp("created_at", self.created_at)
        effective_from = _timestamp("effective_from", self.effective_from)
        approval_reference = _reference(
            "approval_evidence_reference", self.approval_evidence_reference
        )
        approval_fingerprint = _fingerprint(
            "approval_evidence_fingerprint", self.approval_evidence_fingerprint
        )
        supersedes = self.supersedes_version_id
        if supersedes is not None:
            supersedes = _identity("supersedes_version_id", supersedes)
            if supersedes == f"{instrument_id}:{version}":
                _fail("L9A4_P1B_SELF_SUPERSESSION")
        if self.schema != SCHEMA or self.instrument_version != VERSION:
            _fail("L9A4_P1B_IDENTITY_INVALID")

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "case_matter_id", matter_id)
        object.__setattr__(self, "matter_fingerprint", matter_fingerprint)
        object.__setattr__(self, "instrument_id", instrument_id)
        object.__setattr__(self, "version", version)
        object.__setattr__(self, "instrument_kind", kind)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "review_scope", review_scope)
        object.__setattr__(self, "content_reference", content_reference)
        object.__setattr__(self, "content_fingerprint", content_fingerprint)
        object.__setattr__(self, "created_at", created_at)
        object.__setattr__(self, "effective_from", effective_from)
        object.__setattr__(self, "approval_evidence_reference", approval_reference)
        object.__setattr__(self, "approval_evidence_fingerprint", approval_fingerprint)
        object.__setattr__(self, "supersedes_version_id", supersedes)

        payload = {
            field: _json_value(getattr(self, field)) for field in _FIELDS[:-1]
        }
        digest = hashlib.sha3_512(
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=False,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()
        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(self.fingerprint, digest)
        ):
            _fail("L9A4_P1B_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    @property
    def version_id(self) -> str:
        """Return the immutable instrument/version identity used by supersession."""
        return f"{self.instrument_id}:{self.version}"

    def to_dict(self) -> dict[str, object]:
        """Serialize exact immutable metadata without raw document content."""
        return {field: _json_value(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalClientMatterAcceptanceInstrument":
        """Hydrate only the exact schema and verify deterministic integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("L9A4_P1B_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        result = cls(**cast(Any, values))
        if (
            not isinstance(stored, str)
            or not hmac.compare_digest(stored, result.fingerprint)
        ):
            _fail("L9A4_P1B_FINGERPRINT_MISMATCH")
        return result


def record_legal_client_matter_acceptance_instrument(
    *,
    case_matter: CaseMatter,
    instrument_id: str,
    version: str,
    instrument_kind: str,
    title: str,
    review_scope: str,
    content_reference: str,
    content_fingerprint: str,
    created_at: datetime,
    effective_from: datetime,
    approval_evidence_reference: str,
    approval_evidence_fingerprint: str,
    supersedes_version_id: str | None = None,
) -> LegalClientMatterAcceptanceInstrument:
    """Create one instrument from one exact OPEN canonical CaseMatter.

    Tenant, matter identity and matter fingerprint are derived from the
    supplied CaseMatter. Approval evidence is referenced but not verified or
    created here. The caller must later prove current approval, visibility,
    acting capacity and acceptance authority before any persistence or client
    presentation. No party, engagement or financial fact is inferred.
    """
    if type(case_matter) is not CaseMatter:
        _fail("L9A4_P1B_CASE_MATTER_REQUIRED")
    if case_matter.state is not CaseMatterState.OPEN:
        _fail("L9A4_P1B_OPEN_CASE_MATTER_REQUIRED")
    return LegalClientMatterAcceptanceInstrument(
        tenant_id=case_matter.tenant_id,
        case_matter_id=case_matter.case_matter_id,
        matter_fingerprint=case_matter.fingerprint,
        instrument_id=instrument_id,
        version=version,
        instrument_kind=instrument_kind,
        title=title,
        review_scope=review_scope,
        content_reference=content_reference,
        content_fingerprint=content_fingerprint,
        created_at=created_at,
        effective_from=effective_from,
        approval_evidence_reference=approval_evidence_reference,
        approval_evidence_fingerprint=approval_evidence_fingerprint,
        supersedes_version_id=supersedes_version_id,
    )


__all__ = [
    "INSTRUMENT_FIELDS",
    "SCHEMA",
    "VERSION",
    "LegalClientMatterAcceptanceInstrument",
    "LegalClientMatterAcceptanceInstrumentError",
    "record_legal_client_matter_acceptance_instrument",
]


# ARTIFACT: legal_client_matter_acceptance_instrument.py
# VERSION: v1.0.0-L9A4-P1B-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT
# AUTHORITY BOUNDARY: immutable matter-scoped client-reviewable source metadata only
# TENANT POSTURE: tenant/matter bind to exact OPEN CaseMatter; party is deferred
# FAIL-CLOSED POSTURE: malformed, unapproved-reference, naive, drifted or self-superseding values reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
