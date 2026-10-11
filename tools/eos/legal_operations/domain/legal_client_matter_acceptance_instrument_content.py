"""WILSY OS immutable client matter acceptance-instrument content identity.

TITLE: Legal Client Matter Acceptance Instrument Content
VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-CONTENT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Bind exact review bytes to one tenant, OPEN CaseMatter, instrument and
         version through a deterministic opaque server-owned reference.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_client_matter_acceptance_instrument_content.py
COLLABORATION / OWNERSHIP: CaseMatter owns matter truth; the dedicated registry
                            owns bytes; the existing instrument owns reviewable
                            metadata; downstream approval and acceptance remain separate.
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0 establishes bounded text content, SHA3-512 byte
           identity, opaque deterministic references and strict hydration.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Raw scope identifiers are hashed before entering
                             the locator; raw bytes are excluded from metadata.
TENANT BOUNDARY: Exact non-pseudo tenant and CaseMatter scope is mandatory.
AUTHORITY BOUNDARY: Content identity only; no approval, acceptance, engagement,
                    representation, Court, AI or lifecycle authority.
TRANSACTION BOUNDARY: Pure construction and hydration; no persistence authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Invalid scope, media, size, digest, reference, schema
                         or persisted fingerprint rejects without coercion.
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


VERSION: Final[str] = "v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-CONTENT"
SCHEMA: Final[str] = "WILSY-LEGAL-CLIENT-MATTER-ACCEPTANCE-INSTRUMENT-CONTENT/V1"
MAX_CONTENT_BYTES: Final[int] = 2_000_000
SUPPORTED_MEDIA_TYPES: Final[frozenset[str]] = frozenset({"text/plain", "text/markdown"})
_IDENTITY: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$")
_HEX: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset({"default", "global", "global_root", "root", "master", "*"})
_FIELDS: Final[tuple[str, ...]] = (
    "schema", "content_version", "tenant_id", "case_matter_id", "instrument_id",
    "instrument_version", "content_reference", "content_fingerprint",
    "content_length", "media_type", "registered_at", "fingerprint",
)
CONTENT_FIELDS: Final[frozenset[str]] = frozenset(_FIELDS)


class LegalClientMatterAcceptanceInstrumentContentError(ValueError):
    """Stable validation failure for dedicated acceptance-instrument content."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise LegalClientMatterAcceptanceInstrumentContentError(code)


def _identity(name: str, value: object) -> str:
    if not isinstance(value, str) or value != value.strip() or _IDENTITY.fullmatch(value) is None:
        _fail(f"CLIENT_ACCEPTANCE_CONTENT_{name.upper()}_INVALID")
    return cast(str, value)


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        _fail("CLIENT_ACCEPTANCE_CONTENT_TENANT_REQUIRED")
    return tenant


def _timestamp(value: object) -> datetime:
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError:
            _fail("CLIENT_ACCEPTANCE_CONTENT_REGISTERED_AT_INVALID")
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        _fail("CLIENT_ACCEPTANCE_CONTENT_REGISTERED_AT_INVALID")
    return parsed.astimezone(timezone.utc)


def content_fingerprint(content: bytes) -> str:
    """Return SHA3-512 for non-empty bytes within the delivery-service ceiling."""
    if not isinstance(content, bytes):
        _fail("CLIENT_ACCEPTANCE_CONTENT_BYTES_REQUIRED")
    if not content or len(content) > MAX_CONTENT_BYTES:
        _fail("CLIENT_ACCEPTANCE_CONTENT_LENGTH_INVALID")
    return hashlib.sha3_512(content).hexdigest()


def derive_content_reference(*, tenant_id: str, case_matter_id: str, instrument_id: str, instrument_version: str, digest: str) -> str:
    """Derive an opaque locator binding scope, version and exact byte digest."""
    tenant = _tenant(tenant_id)
    matter = _identity("case_matter_id", case_matter_id)
    instrument = _identity("instrument_id", instrument_id)
    version = _identity("instrument_version", instrument_version)
    if not isinstance(digest, str) or _HEX.fullmatch(digest) is None:
        _fail("CLIENT_ACCEPTANCE_CONTENT_FINGERPRINT_INVALID")
    scope = hashlib.sha3_512(
        json.dumps([tenant, matter, instrument, version], ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return f"legal-client-acceptance-instrument:{scope}:{digest[:32]}"


@dataclass(frozen=True, slots=True)
class LegalClientMatterAcceptanceInstrumentContent:
    """Immutable metadata for exact dedicated acceptance-instrument bytes."""

    tenant_id: str
    case_matter_id: str
    instrument_id: str
    instrument_version: str
    content_reference: str
    content_fingerprint: str
    content_length: int
    media_type: str
    registered_at: datetime
    schema: str = SCHEMA
    content_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        matter = _identity("case_matter_id", self.case_matter_id)
        instrument = _identity("instrument_id", self.instrument_id)
        version = _identity("instrument_version", self.instrument_version)
        if not isinstance(self.content_fingerprint, str) or _HEX.fullmatch(self.content_fingerprint) is None:
            _fail("CLIENT_ACCEPTANCE_CONTENT_FINGERPRINT_INVALID")
        if isinstance(self.content_length, bool) or not isinstance(self.content_length, int) or not 1 <= self.content_length <= MAX_CONTENT_BYTES:
            _fail("CLIENT_ACCEPTANCE_CONTENT_LENGTH_INVALID")
        if not isinstance(self.media_type, str) or self.media_type != self.media_type.strip() or self.media_type.lower() not in SUPPORTED_MEDIA_TYPES:
            _fail("CLIENT_ACCEPTANCE_CONTENT_MEDIA_TYPE_UNSUPPORTED")
        registered = _timestamp(self.registered_at)
        expected = derive_content_reference(tenant_id=tenant, case_matter_id=matter, instrument_id=instrument, instrument_version=version, digest=self.content_fingerprint)
        if self.content_reference != expected:
            _fail("CLIENT_ACCEPTANCE_CONTENT_REFERENCE_INVALID")
        if self.schema != SCHEMA or self.content_version != VERSION:
            _fail("CLIENT_ACCEPTANCE_CONTENT_IDENTITY_INVALID")
        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "case_matter_id", matter)
        object.__setattr__(self, "instrument_id", instrument)
        object.__setattr__(self, "instrument_version", version)
        object.__setattr__(self, "media_type", self.media_type.lower())
        object.__setattr__(self, "registered_at", registered)
        payload = {field: self._json(getattr(self, field)) for field in _FIELDS[:-1]}
        fingerprint = hashlib.sha3_512(json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=False, separators=(",", ":")).encode("utf-8")).hexdigest()
        if self.fingerprint and (not isinstance(self.fingerprint, str) or not hmac.compare_digest(self.fingerprint, fingerprint)):
            _fail("CLIENT_ACCEPTANCE_CONTENT_METADATA_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", fingerprint)

    @staticmethod
    def _json(value: object) -> object:
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z") if isinstance(value, datetime) else value

    def to_dict(self) -> dict[str, object]:
        """Serialize exact immutable metadata without exposing raw bytes."""
        return {field: self._json(getattr(self, field)) for field in _FIELDS}

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "LegalClientMatterAcceptanceInstrumentContent":
        """Strictly hydrate persisted metadata and verify its fingerprint."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            _fail("CLIENT_ACCEPTANCE_CONTENT_SCHEMA_INVALID")
        values = dict(payload)
        stored = values.pop("fingerprint")
        value = cls(**cast(Any, values))
        if not isinstance(stored, str) or not hmac.compare_digest(stored, value.fingerprint):
            _fail("CLIENT_ACCEPTANCE_CONTENT_METADATA_FINGERPRINT_MISMATCH")
        return value


def register_legal_client_matter_acceptance_instrument_content(*, tenant_id: str, case_matter_id: str, instrument_id: str, instrument_version: str, content: bytes, media_type: str, registered_at: datetime) -> LegalClientMatterAcceptanceInstrumentContent:
    """Construct server-owned metadata from exact bounded raw bytes."""
    digest = content_fingerprint(content)
    return LegalClientMatterAcceptanceInstrumentContent(
        tenant_id=tenant_id, case_matter_id=case_matter_id, instrument_id=instrument_id,
        instrument_version=instrument_version,
        content_reference=derive_content_reference(tenant_id=tenant_id, case_matter_id=case_matter_id, instrument_id=instrument_id, instrument_version=instrument_version, digest=digest),
        content_fingerprint=digest, content_length=len(content), media_type=media_type,
        registered_at=registered_at,
    )


__all__ = ["CONTENT_FIELDS", "MAX_CONTENT_BYTES", "SCHEMA", "SUPPORTED_MEDIA_TYPES", "VERSION", "LegalClientMatterAcceptanceInstrumentContent", "LegalClientMatterAcceptanceInstrumentContentError", "content_fingerprint", "derive_content_reference", "register_legal_client_matter_acceptance_instrument_content"]

# ARTIFACT: legal_client_matter_acceptance_instrument_content.py
# VERSION: v1.0.0-CLIENT-ACCEPTANCE-INSTRUMENT-CONTENT
# AUTHORITY BOUNDARY: dedicated immutable acceptance-instrument content identity only
# TENANT POSTURE: opaque reference binds exact tenant/matter/instrument/version
# FAIL-CLOSED POSTURE: malformed, oversized, unsupported, forged or corrupt values reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
