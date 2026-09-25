"""WILSY OS canonical immutable tenant branding asset evidence.

TITLE: Tenant Branding Asset Domain
VERSION: v1.0.0-D21B5A-TENANT-BRANDING-ASSET
AUTHORITY: Wilsy OS Core Governance
EPITOME: Own immutable tenant-scoped branding asset metadata and exact SHA3-512
         content identity without granting storage, profile-selection, browser,
         IAM or financial authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/tenant_branding_asset.py
COLLABORATION / OWNERSHIP: D21B3 owns approved profile references/fingerprints;
                            this domain defines the canonical asset evidence that
                            may satisfy such a reference. A separate registry owns
                            durable bytes. Runtime branding must still revalidate
                            D21B2B entitlement and D21B4B current profile.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-D21B5A-TENANT-BRANDING-ASSET establishes immutable LOGO/FAVICON
           evidence, exact tenant-bound asset references, bounded safe image
           media types, content length limits, SHA3-512 byte identity, source
           evidence and deterministic metadata integrity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Domain stores no raw bytes, URL, filesystem path,
                             cloud key, credentials, HTML, CSS or executable
                             content. SVG is deliberately excluded.
TENANT BOUNDARY: asset_reference must begin with the exact tenant-bound
                 "asset:<tenant_id>:" namespace; pseudo-tenants reject.
AUTHORITY BOUNDARY: Immutable branding-asset evidence only. Existence does not
                    approve a D21B3 profile, select current branding, grant
                    browser presentation or resolve any public URL.
FINANCIAL AUTHORITY BOUNDARY: No commercial, payment, execution or settlement
                               authority. Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Unsupported kind/media, unsafe reference, empty/oversize
                         content, fingerprint mismatch, schema drift and metadata
                         corruption reject.
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
import unicodedata
from typing import Any, Final, cast


VERSION: Final[str] = "v1.0.0-D21B5A-TENANT-BRANDING-ASSET"
SCHEMA: Final[str] = "WILSY-TENANT-BRANDING-ASSET/V1"
MAX_ASSET_BYTES: Final[int] = 2 * 1024 * 1024
SAFE_MEDIA_TYPES: Final[frozenset[str]] = frozenset(
    {
        "image/png",
        "image/jpeg",
        "image/webp",
        "image/x-icon",
        "image/vnd.microsoft.icon",
    }
)
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "asset_version",
    "tenant_id",
    "asset_reference",
    "asset_kind",
    "media_type",
    "content_length",
    "content_fingerprint",
    "source_evidence_reference",
    "source_evidence_fingerprint",
    "registered_at",
    "fingerprint",
)
ASSET_FIELDS: Final[tuple[str, ...]] = _FIELDS
_ASSET_REFERENCE: Final[re.Pattern[str]] = re.compile(
    r"^asset:[A-Za-z0-9][A-Za-z0-9._:-]{0,199}$"
)
_HEX_DIGITS: Final[frozenset[str]] = frozenset("0123456789abcdef")
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class TenantBrandingAssetError(ValueError):
    """Raised when tenant branding asset evidence violates the contract."""


class TenantBrandingAssetKind(StrEnum):
    """Closed tenant-branding asset purposes."""

    LOGO = "LOGO"
    FAVICON = "FAVICON"


def _text(name: str, value: object, *, limit: int = 512) -> str:
    """Return one exact bounded NFC text value."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantBrandingAssetError(f"D21B5A_INVALID_{name.upper()}")
    normalized = unicodedata.normalize("NFC", value)
    if (
        not normalized
        or len(normalized) > limit
        or any(ord(character) < 32 for character in normalized)
    ):
        raise TenantBrandingAssetError(f"D21B5A_INVALID_{name.upper()}")
    return normalized


def _fingerprint(name: str, value: object) -> str:
    """Require one canonical lowercase SHA3-512 fingerprint."""
    if (
        not isinstance(value, str)
        or len(value) != 128
        or any(character not in _HEX_DIGITS for character in value)
    ):
        raise TenantBrandingAssetError(f"D21B5A_INVALID_{name.upper()}")
    return value


def _when(name: str, value: object) -> datetime:
    """Normalize one timezone-aware timestamp into UTC."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            raise TenantBrandingAssetError(
                f"D21B5A_INVALID_{name.upper()}"
            ) from error
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise TenantBrandingAssetError(f"D21B5A_INVALID_{name.upper()}")
    return parsed.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Project exact domain values into deterministic JSON-compatible form."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, StrEnum):
        return value.value
    return value


def content_fingerprint(content: bytes) -> str:
    """Return SHA3-512 identity for non-empty bounded immutable asset bytes."""
    if not isinstance(content, bytes):
        raise TenantBrandingAssetError("D21B5A_CONTENT_BYTES_REQUIRED")
    if not content or len(content) > MAX_ASSET_BYTES:
        raise TenantBrandingAssetError("D21B5A_CONTENT_LENGTH_INVALID")
    return hashlib.sha3_512(content).hexdigest()


@dataclass(frozen=True, slots=True)
class TenantBrandingAsset:
    """Immutable tenant branding asset metadata bound to exact byte identity."""

    tenant_id: str
    asset_reference: str
    asset_kind: TenantBrandingAssetKind | str
    media_type: str
    content_length: int
    content_fingerprint: str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    registered_at: datetime
    schema: str = SCHEMA
    asset_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact tenant/reference/media/content evidence and integrity."""
        tenant_id = _text("tenant_id", self.tenant_id, limit=160)
        if tenant_id.casefold() in _FORBIDDEN_TENANTS:
            raise TenantBrandingAssetError("D21B5A_TENANT_REQUIRED")
        asset_reference = _text(
            "asset_reference",
            self.asset_reference,
            limit=256,
        )
        if (
            _ASSET_REFERENCE.fullmatch(asset_reference) is None
            or not asset_reference.startswith(f"asset:{tenant_id}:")
        ):
            raise TenantBrandingAssetError("D21B5A_ASSET_REFERENCE_INVALID")
        try:
            asset_kind = TenantBrandingAssetKind(self.asset_kind)
        except (TypeError, ValueError) as error:
            raise TenantBrandingAssetError(
                "D21B5A_ASSET_KIND_INVALID"
            ) from error
        media_type = _text("media_type", self.media_type, limit=64).lower()
        if media_type not in SAFE_MEDIA_TYPES:
            raise TenantBrandingAssetError("D21B5A_MEDIA_TYPE_UNSUPPORTED")
        if (
            isinstance(self.content_length, bool)
            or not isinstance(self.content_length, int)
            or self.content_length < 1
            or self.content_length > MAX_ASSET_BYTES
        ):
            raise TenantBrandingAssetError("D21B5A_CONTENT_LENGTH_INVALID")
        content_digest = _fingerprint(
            "content_fingerprint",
            self.content_fingerprint,
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
        if self.schema != SCHEMA or self.asset_version != VERSION:
            raise TenantBrandingAssetError("D21B5A_IDENTITY_INVALID")

        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "asset_reference", asset_reference)
        object.__setattr__(self, "asset_kind", asset_kind)
        object.__setattr__(self, "media_type", media_type)
        object.__setattr__(self, "content_fingerprint", content_digest)
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
            raise TenantBrandingAssetError("D21B5A_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize exact immutable metadata; raw content is never included."""
        return {
            field: _json_value(getattr(self, field))
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "TenantBrandingAsset":
        """Hydrate only the exact schema and verify stored metadata integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise TenantBrandingAssetError("D21B5A_SCHEMA_INVALID")
        values = dict(payload)
        stored_fingerprint = values.pop("fingerprint")
        item = cls(**cast(Any, values))
        if (
            not isinstance(stored_fingerprint, str)
            or not hmac.compare_digest(stored_fingerprint, item.fingerprint)
        ):
            raise TenantBrandingAssetError("D21B5A_FINGERPRINT_MISMATCH")
        return item


def register_tenant_branding_asset(
    *,
    tenant_id: str,
    asset_reference: str,
    asset_kind: TenantBrandingAssetKind | str,
    media_type: str,
    content: bytes,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    registered_at: datetime,
) -> TenantBrandingAsset:
    """Create immutable metadata bound to exact supplied content bytes.

    The bytes are hashed but not retained by this pure domain. A later registry
    must persist and re-verify the exact bytes before any runtime resolution.
    """
    digest = content_fingerprint(content)
    return TenantBrandingAsset(
        tenant_id=tenant_id,
        asset_reference=asset_reference,
        asset_kind=asset_kind,
        media_type=media_type,
        content_length=len(content),
        content_fingerprint=digest,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
        registered_at=registered_at,
    )


__all__ = [
    "ASSET_FIELDS",
    "MAX_ASSET_BYTES",
    "SAFE_MEDIA_TYPES",
    "SCHEMA",
    "TenantBrandingAsset",
    "TenantBrandingAssetError",
    "TenantBrandingAssetKind",
    "VERSION",
    "content_fingerprint",
    "register_tenant_branding_asset",
]

# ARTIFACT: tenant_branding_asset.py
# VERSION: v1.0.0-D21B5A-TENANT-BRANDING-ASSET
# AUTHORITY BOUNDARY: immutable tenant branding asset metadata/content identity only; no storage, profile, browser, IAM or financial authority
# TENANT POSTURE: asset references are exact-tenant namespaced and pseudo-tenants reject
# FAIL-CLOSED POSTURE: unsafe media/reference, empty/oversize content, fingerprint/schema corruption reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
