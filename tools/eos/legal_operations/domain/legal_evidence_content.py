"""WILSY OS immutable tenant legal-evidence content identity.

TITLE: Legal Evidence Content Domain
VERSION: v1.0.0-L10A1-LEGAL-EVIDENCE-CONTENT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Own exact tenant-, matter-, and process-document-bound content metadata
         and SHA3-512 byte identity for legal evidence without granting storage,
         lifecycle, Court filing, service, IAM, AI, billing, payment, execution,
         or settlement authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/domain/legal_evidence_content.py
COLLABORATION / OWNERSHIP: Legal Operations lifecycle owns CaseMatter,
                            ProcessDocument and custody truth. This pure domain
                            owns only immutable uploaded-content identity.
                            A later registry may persist exact bytes, and a later
                            authenticated HTTP seam may derive tenant/principal
                            authority before invoking this domain.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: 2026-09-29 v1.0.0-L10A1-LEGAL-EVIDENCE-CONTENT establishes
           tenant/matter/document-bound legal-evidence metadata, deterministic
           server-derived content references, bounded legal-document/image
           media admission, filename sanitization, SHA3-512 byte identity,
           provenance evidence, deterministic metadata integrity, and strict
           rehydration without creating downstream lifecycle authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Raw bytes are hashed but never retained by this pure
                             domain. Paths, URLs, credentials, scripts, HTML,
                             executable formats and macro-enabled Office media
                             are not admitted. Malware/content inspection
                             remains a separate later admission boundary.
TENANT BOUNDARY: Every artifact is bound to one explicit non-pseudo tenant,
                 case_matter_id and document_id. content_reference is derived
                 from those validated identities and exact byte fingerprint.
AUTHORITY BOUNDARY: Content identity only. Existence does not create or advance
                    CaseMatter, LegalInstruction, ProcessDocument, custody,
                    service, return, Court filing, Court Online, client
                    visibility, legal acceptance or AI authority.
FINANCIAL AUTHORITY BOUNDARY: No pricing, invoice, payment, execution or
                              settlement authority. Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Invalid tenant/matter/document identity, unsupported
                         media, unsafe filename, empty/oversize bytes, malformed
                         provenance, fingerprint mismatch, schema drift and
                         persisted metadata corruption reject.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
import unicodedata
from typing import Any, Final, cast


VERSION: Final[str] = "v1.0.0-L10A1-LEGAL-EVIDENCE-CONTENT"
SCHEMA: Final[str] = "WILSY-LEGAL-EVIDENCE-CONTENT/V1"

# WILSY internal ingestion safety ceiling. This is not a Court Online,
# judiciary, provider or external-system file-size claim.
MAX_CONTENT_BYTES: Final[int] = 25 * 1024 * 1024

SAFE_MEDIA_TYPES: Final[frozenset[str]] = frozenset(
    {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "image/jpeg",
        "image/png",
        "image/webp",
        "text/plain",
    }
)

_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "evidence_content_version",
    "tenant_id",
    "case_matter_id",
    "document_id",
    "content_reference",
    "media_type",
    "original_filename",
    "content_length",
    "content_fingerprint",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "registered_at",
    "fingerprint",
)
LEGAL_EVIDENCE_CONTENT_FIELDS: Final[tuple[str, ...]] = _FIELDS

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_FILENAME: Final[re.Pattern[str]] = re.compile(
    r"^[^\x00-\x1f\x7f/\\]{1,255}$"
)
_HEX_DIGITS: Final[frozenset[str]] = frozenset("0123456789abcdef")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalEvidenceContentError(ValueError):
    """Raised when immutable Legal evidence-content evidence is invalid."""


def _text(name: str, value: object, *, limit: int = 512) -> str:
    """Return exact bounded NFC text without control characters."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise LegalEvidenceContentError(f"L10A1_INVALID_{name.upper()}")
    normalized = unicodedata.normalize("NFC", value)
    if (
        not normalized
        or len(normalized) > limit
        or any(ord(character) < 32 for character in normalized)
    ):
        raise LegalEvidenceContentError(f"L10A1_INVALID_{name.upper()}")
    return normalized


def _identity(name: str, value: object) -> str:
    """Require one bounded opaque repository identity."""
    identity = _text(name, value, limit=160)
    if _IDENTITY.fullmatch(identity) is None:
        raise LegalEvidenceContentError(f"L10A1_INVALID_{name.upper()}")
    return identity


def _tenant(value: object) -> str:
    """Require one explicit non-pseudo tenant identity."""
    tenant_id = _identity("tenant_id", value)
    if tenant_id.casefold() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceContentError("L10A1_TENANT_REQUIRED")
    return tenant_id


def _fingerprint(name: str, value: object) -> str:
    """Require canonical lowercase SHA3-512 hexadecimal evidence."""
    if (
        not isinstance(value, str)
        or len(value) != 128
        or any(character not in _HEX_DIGITS for character in value)
    ):
        raise LegalEvidenceContentError(f"L10A1_INVALID_{name.upper()}")
    return value


def _when(name: str, value: object) -> datetime:
    """Normalize one timezone-aware timestamp to UTC."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            raise LegalEvidenceContentError(
                f"L10A1_INVALID_{name.upper()}"
            ) from error
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise LegalEvidenceContentError(f"L10A1_INVALID_{name.upper()}")
    return parsed.astimezone(timezone.utc)


def _filename(value: object) -> str:
    """Require one basename-only display filename with no path semantics."""
    name = _text("original_filename", value, limit=255)
    if (
        _FILENAME.fullmatch(name) is None
        or name in {".", ".."}
        or name.startswith(".")
    ):
        raise LegalEvidenceContentError("L10A1_INVALID_ORIGINAL_FILENAME")
    return name


def _json_value(value: object) -> object:
    """Project exact domain values into deterministic JSON-compatible form."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return value


def content_fingerprint(content: bytes) -> str:
    """Return SHA3-512 identity for non-empty bounded Legal evidence bytes."""
    if not isinstance(content, bytes):
        raise LegalEvidenceContentError("L10A1_CONTENT_BYTES_REQUIRED")
    if not content or len(content) > MAX_CONTENT_BYTES:
        raise LegalEvidenceContentError("L10A1_CONTENT_LENGTH_INVALID")
    return hashlib.sha3_512(content).hexdigest()


def _content_reference(
    *,
    tenant_id: str,
    case_matter_id: str,
    document_id: str,
    digest: str,
) -> str:
    """Derive one deterministic server-owned Legal evidence content reference."""
    return (
        f"legal-evidence:{tenant_id}:{case_matter_id}:"
        f"{document_id}:{digest[:32]}"
    )


@dataclass(frozen=True, slots=True)
class LegalEvidenceContent:
    """Immutable metadata binding one process document to exact evidence bytes."""

    tenant_id: str
    case_matter_id: str
    document_id: str
    content_reference: str
    media_type: str
    original_filename: str
    content_length: int
    content_fingerprint: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    registered_at: datetime
    schema: str = SCHEMA
    evidence_content_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate identity, provenance and deterministic metadata integrity."""
        tenant_id = _tenant(self.tenant_id)
        case_matter_id = _identity("case_matter_id", self.case_matter_id)
        document_id = _identity("document_id", self.document_id)

        media_type = _text("media_type", self.media_type, limit=128).lower()
        if media_type not in SAFE_MEDIA_TYPES:
            raise LegalEvidenceContentError("L10A1_MEDIA_TYPE_UNSUPPORTED")

        original_filename = _filename(self.original_filename)

        if (
            isinstance(self.content_length, bool)
            or not isinstance(self.content_length, int)
            or self.content_length < 1
            or self.content_length > MAX_CONTENT_BYTES
        ):
            raise LegalEvidenceContentError("L10A1_CONTENT_LENGTH_INVALID")

        content_digest = _fingerprint(
            "content_fingerprint",
            self.content_fingerprint,
        )

        expected_reference = _content_reference(
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            document_id=document_id,
            digest=content_digest,
        )
        if self.content_reference != expected_reference:
            raise LegalEvidenceContentError(
                "L10A1_CONTENT_REFERENCE_INVALID"
            )

        source_reference = _text(
            "source_evidence_reference",
            self.source_evidence_reference,
        )
        source_fingerprint = _fingerprint(
            "source_evidence_fingerprint",
            self.source_evidence_fingerprint,
        )
        registered_at = _when("registered_at", self.registered_at)

        if (
            self.schema != SCHEMA
            or self.evidence_content_version != VERSION
        ):
            raise LegalEvidenceContentError("L10A1_IDENTITY_INVALID")

        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "case_matter_id", case_matter_id)
        object.__setattr__(self, "document_id", document_id)
        object.__setattr__(self, "media_type", media_type)
        object.__setattr__(self, "original_filename", original_filename)
        object.__setattr__(
            self,
            "content_fingerprint",
            content_digest,
        )
        object.__setattr__(
            self,
            "source_evidence_reference",
            source_reference,
        )
        object.__setattr__(
            self,
            "source_evidence_fingerprint",
            source_fingerprint,
        )
        object.__setattr__(self, "registered_at", registered_at)

        payload = {
            field: _json_value(getattr(self, field))
            for field in _FIELDS[:-1]
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
            raise LegalEvidenceContentError(
                "L10A1_FINGERPRINT_MISMATCH"
            )

        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize immutable metadata only; raw content is never exposed."""
        return {
            field: _json_value(getattr(self, field))
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalEvidenceContent":
        """Hydrate exact stored metadata and reject schema/integrity drift."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise LegalEvidenceContentError("L10A1_SCHEMA_INVALID")

        values = dict(payload)
        stored_fingerprint = values.pop("fingerprint")
        item = cls(**cast(Any, values))

        if (
            not isinstance(stored_fingerprint, str)
            or not hmac.compare_digest(
                stored_fingerprint,
                item.fingerprint,
            )
        ):
            raise LegalEvidenceContentError(
                "L10A1_FINGERPRINT_MISMATCH"
            )

        return item


def register_legal_evidence_content(
    *,
    tenant_id: str,
    case_matter_id: str,
    document_id: str,
    media_type: str,
    original_filename: str,
    content: bytes,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    registered_at: datetime,
) -> LegalEvidenceContent:
    """Create immutable metadata bound to exact supplied Legal evidence bytes.

    This pure domain hashes but never stores the raw bytes. It also creates no
    ProcessDocument, custody, Court filing, service, AI, billing or financial
    truth. Later bounded layers must separately prove those authorities.
    """
    canonical_tenant = _tenant(tenant_id)
    canonical_matter = _identity("case_matter_id", case_matter_id)
    canonical_document = _identity("document_id", document_id)
    digest = content_fingerprint(content)

    return LegalEvidenceContent(
        tenant_id=canonical_tenant,
        case_matter_id=canonical_matter,
        document_id=canonical_document,
        content_reference=_content_reference(
            tenant_id=canonical_tenant,
            case_matter_id=canonical_matter,
            document_id=canonical_document,
            digest=digest,
        ),
        media_type=media_type,
        original_filename=original_filename,
        content_length=len(content),
        content_fingerprint=digest,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
        registered_at=registered_at,
    )


__all__ = [
    "LEGAL_EVIDENCE_CONTENT_FIELDS",
    "MAX_CONTENT_BYTES",
    "SAFE_MEDIA_TYPES",
    "SCHEMA",
    "LegalEvidenceContent",
    "LegalEvidenceContentError",
    "VERSION",
    "content_fingerprint",
    "register_legal_evidence_content",
]

# ARTIFACT: legal_evidence_content.py
# VERSION: v1.0.0-L10A1-LEGAL-EVIDENCE-CONTENT
# AUTHORITY BOUNDARY: immutable tenant/matter/document evidence-content identity only; no storage, lifecycle, Court, IAM, AI or financial authority
# TENANT POSTURE: exact tenant/matter/document binding with deterministic server-owned content references
# FAIL-CLOSED POSTURE: unsafe media/name, invalid identities, empty/oversize bytes, provenance, schema or fingerprint corruption reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
