"""WILSY OS tenant inbound provider credential-material metadata value.

TITLE: Tenant Inbound Provider Credential Material Metadata
VERSION: v1.1.0-M11-R8-R3B-P8-P3D-P5-R4D
AUTHORITY: Wilsy OS Core Governance
EPITOME: Provider-neutral immutable structural metadata for one claimed
         credential-material generation; it is not a durable security fact.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/tenant_inbound_provider_credential_material_metadata.py
COLLABORATION / OWNERSHIP: SaaS credential-material metadata domain owner;
                            authenticated adapters, registry, security evidence,
                            and issuance remain separate future owners.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.1.0-M11-R8-R3B-P8-P3D-P5-R4D reclassifies observed_at as
           descriptive observation metadata and excludes it from generation
           identity and the V1 SHA3-512 fingerprint payload.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque references and version metadata only; no
                             raw/decrypted secret, secret hash, KMS, provider,
                             network, or database access.
TENANT BOUNDARY: tenant_id and the complete configuration identity are required
                 structural correlation fields.
AUTHORITY BOUNDARY: Value validation and integrity only; construction does not
                    authenticate a source, establish durability, currentness,
                    eligibility, binding, checkout, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement truth.
FAIL-CLOSED DECLARATION: Blank identities, malformed versions, non-UTC time,
                          schema drift, and fingerprint mismatch reject.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
from typing import Any, ClassVar, Mapping, cast


VERSION = "v1.1.0-M11-R8-R3B-P8-P3D-P5-R4D"
CAMPAIGN_IDENTITY = "M11-R8-R3B-P8-P3D-P5-R4D"
METADATA_FINGERPRINT_VERSION = "v1"
METADATA_FINGERPRINT_SCHEMA = (
    "WILSY-TENANT-INBOUND-PROVIDER-CREDENTIAL-MATERIAL-METADATA/V1"
)
HASH_ALGORITHM = "SHA3-512"
MAX_CREDENTIAL_VERSION_LENGTH = 128
_SHA3_512 = re.compile(r"^[0-9a-f]{128}$")


class TenantInboundProviderCredentialMaterialMetadataError(ValueError):
    """Raised when one metadata value or observation violates its shape."""


def _text(name: str, value: object, *, maximum: int | None = None) -> str:
    """Require an opaque non-blank string without changing identity data."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantInboundProviderCredentialMaterialMetadataError(
            f"M11P5R2_INVALID_{name.upper()}"
        )
    if maximum is not None and len(value) > maximum:
        raise TenantInboundProviderCredentialMaterialMetadataError(
            f"M11P5R2_INVALID_{name.upper()}"
        )
    return value


def _credential_version(value: object) -> str:
    """Validate an opaque credential-material generation token."""
    return _text(
        "credential_version",
        value,
        maximum=MAX_CREDENTIAL_VERSION_LENGTH,
    )


def _configuration_version(value: object) -> int:
    """Require a positive, non-boolean merchant-configuration version."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise TenantInboundProviderCredentialMaterialMetadataError(
            "M11P5R2_INVALID_MERCHANT_CONFIGURATION_VERSION"
        )
    return value


def _fingerprint(name: str, value: object) -> str:
    """Require a lowercase canonical SHA3-512 hexadecimal digest."""
    if not isinstance(value, str) or _SHA3_512.fullmatch(value) is None:
        raise TenantInboundProviderCredentialMaterialMetadataError(
            f"M11P5R2_INVALID_{name.upper()}"
        )
    return value


def _observed_at(value: object) -> datetime:
    """Require an aware UTC observation timestamp; non-UTC offsets reject."""
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise TenantInboundProviderCredentialMaterialMetadataError(
            "M11P5R2_INVALID_OBSERVED_AT"
        )
    if value.utcoffset() != timedelta(0):
        raise TenantInboundProviderCredentialMaterialMetadataError(
            "M11P5R2_NON_UTC_OBSERVED_AT"
        )
    return value.astimezone(timezone.utc)


def _json_bytes(value: Mapping[str, object]) -> bytes:
    """Serialize authority-bearing values deterministically."""
    return json.dumps(
        dict(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


@dataclass(frozen=True, slots=True)
class TenantInboundProviderCredentialMaterialObservation:
    """Immutable runtime observation supplied by a future metadata adapter.

    This six-field value validates provenance shape only.  Adapter
    authentication, canonical merchant-configuration correlation, and durable
    authority remain outside the value object.
    """

    credential_reference: str
    credential_version: str
    metadata_source_identity: str
    metadata_source_version: str
    version_provenance_reference: str
    observed_at: datetime

    _FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "credential_reference",
            "credential_version",
            "metadata_source_identity",
            "metadata_source_version",
            "version_provenance_reference",
            "observed_at",
        }
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "credential_reference", _text("credential_reference", self.credential_reference))
        object.__setattr__(self, "credential_version", _credential_version(self.credential_version))
        object.__setattr__(self, "metadata_source_identity", _text("metadata_source_identity", self.metadata_source_identity))
        object.__setattr__(self, "metadata_source_version", _text("metadata_source_version", self.metadata_source_version))
        object.__setattr__(self, "version_provenance_reference", _text("version_provenance_reference", self.version_provenance_reference))
        object.__setattr__(self, "observed_at", _observed_at(self.observed_at))

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact six-field observation shape."""
        return {
            "credential_reference": self.credential_reference,
            "credential_version": self.credential_version,
            "metadata_source_identity": self.metadata_source_identity,
            "metadata_source_version": self.metadata_source_version,
            "version_provenance_reference": self.version_provenance_reference,
            "observed_at": self.observed_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "TenantInboundProviderCredentialMaterialObservation":
        """Hydrate strictly from the six-field runtime observation shape."""
        if not isinstance(payload, Mapping) or set(payload) != cls._FIELDS:
            raise TenantInboundProviderCredentialMaterialMetadataError(
                "M11P5R2_INVALID_OBSERVATION_SCHEMA"
            )
        observed = payload["observed_at"]
        if isinstance(observed, str):
            try:
                observed = datetime.fromisoformat(observed)
            except ValueError as error:
                raise TenantInboundProviderCredentialMaterialMetadataError(
                    "M11P5R2_INVALID_OBSERVED_AT"
                ) from error
        try:
            return cls(
                credential_reference=cast(str, payload["credential_reference"]),
                credential_version=cast(str, payload["credential_version"]),
                metadata_source_identity=cast(str, payload["metadata_source_identity"]),
                metadata_source_version=cast(str, payload["metadata_source_version"]),
                version_provenance_reference=cast(str, payload["version_provenance_reference"]),
                observed_at=cast(datetime, observed),
            )
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, TenantInboundProviderCredentialMaterialMetadataError):
                raise
            raise TenantInboundProviderCredentialMaterialMetadataError(
                "M11P5R2_INVALID_OBSERVATION"
            ) from error


@dataclass(frozen=True, slots=True)
class TenantInboundProviderCredentialMaterialMetadata:
    """Immutable structural metadata for one claimed credential generation.

    The constructor validates values and derives integrity, but it never
    authenticates an external source, queries canonical configuration, opens a
    database, contacts a provider, accesses KMS, or creates durable authority.
    """

    tenant_id: str
    provider_id: str
    merchant_configuration_id: str
    merchant_configuration_version: int
    merchant_configuration_fingerprint: str
    credential_reference: str
    credential_version: str
    observed_at: datetime
    metadata_source_identity: str
    metadata_source_version: str
    version_provenance_reference: str
    metadata_fingerprint_version: str = METADATA_FINGERPRINT_VERSION
    metadata_fingerprint: str | None = None

    _FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "tenant_id",
            "provider_id",
            "merchant_configuration_id",
            "merchant_configuration_version",
            "merchant_configuration_fingerprint",
            "credential_reference",
            "credential_version",
            "observed_at",
            "metadata_source_identity",
            "metadata_source_version",
            "version_provenance_reference",
            "metadata_fingerprint_version",
            "metadata_fingerprint",
        }
    )
    _GENERATION_SEMANTIC_FIELDS: ClassVar[tuple[str, ...]] = (
        "tenant_id",
        "provider_id",
        "merchant_configuration_id",
        "merchant_configuration_version",
        "merchant_configuration_fingerprint",
        "credential_reference",
        "credential_version",
        "metadata_source_identity",
        "metadata_source_version",
        "version_provenance_reference",
        "metadata_fingerprint_version",
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "tenant_id", _text("tenant_id", self.tenant_id))
        object.__setattr__(self, "provider_id", _text("provider_id", self.provider_id))
        object.__setattr__(self, "merchant_configuration_id", _text("merchant_configuration_id", self.merchant_configuration_id))
        object.__setattr__(self, "merchant_configuration_version", _configuration_version(self.merchant_configuration_version))
        object.__setattr__(self, "merchant_configuration_fingerprint", _fingerprint("merchant_configuration_fingerprint", self.merchant_configuration_fingerprint))
        object.__setattr__(self, "credential_reference", _text("credential_reference", self.credential_reference))
        object.__setattr__(self, "credential_version", _credential_version(self.credential_version))
        object.__setattr__(self, "observed_at", _observed_at(self.observed_at))
        object.__setattr__(self, "metadata_source_identity", _text("metadata_source_identity", self.metadata_source_identity))
        object.__setattr__(self, "metadata_source_version", _text("metadata_source_version", self.metadata_source_version))
        object.__setattr__(self, "version_provenance_reference", _text("version_provenance_reference", self.version_provenance_reference))
        if self.metadata_fingerprint_version != METADATA_FINGERPRINT_VERSION:
            raise TenantInboundProviderCredentialMaterialMetadataError(
                "M11P5R2_INVALID_METADATA_FINGERPRINT_VERSION"
            )
        expected = self.compute_fingerprint()
        if self.metadata_fingerprint is not None:
            supplied = _fingerprint("metadata_fingerprint", self.metadata_fingerprint)
            if supplied != expected:
                raise TenantInboundProviderCredentialMaterialMetadataError(
                    "M11P5R2_METADATA_FINGERPRINT_MISMATCH"
                )
        object.__setattr__(self, "metadata_fingerprint", expected)

    def generation_identity(self) -> tuple[object, ...]:
        """Return canonical generation identity, excluding observation time."""
        return tuple(getattr(self, name) for name in self._GENERATION_SEMANTIC_FIELDS)

    def same_generation(self, other: object) -> bool:
        """Compare generation identity without treating re-observation as replay."""
        return (
            isinstance(other, TenantInboundProviderCredentialMaterialMetadata)
            and self.generation_identity() == other.generation_identity()
        )

    def _semantic_payload(self) -> dict[str, object]:
        """Return generation fields for the V1 integrity fingerprint.

        ``observed_at`` remains part of the structural value and persisted
        document, but is descriptive observation metadata rather than
        generation identity or generation-integrity input.
        """
        return {
            name: getattr(self, name) for name in self._GENERATION_SEMANTIC_FIELDS
        }

    def compute_fingerprint(self) -> str:
        """Compute deterministic lowercase SHA3-512 value integrity."""
        return hashlib.sha3_512(_json_bytes(self._semantic_payload())).hexdigest()

    @property
    def fingerprint(self) -> str:
        """Return the canonical metadata fingerprint."""
        assert self.metadata_fingerprint is not None
        return self.metadata_fingerprint

    def verify_fingerprint(self, fingerprint: str | None = None) -> bool:
        """Validate an optional supplied digest against recomputed metadata."""
        supplied = self.fingerprint if fingerprint is None else _fingerprint("metadata_fingerprint", fingerprint)
        return supplied == self.compute_fingerprint()

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact thirteen-field metadata schema."""
        payload = {
            "tenant_id": self.tenant_id,
            "provider_id": self.provider_id,
            "merchant_configuration_id": self.merchant_configuration_id,
            "merchant_configuration_version": self.merchant_configuration_version,
            "merchant_configuration_fingerprint": self.merchant_configuration_fingerprint,
            "credential_reference": self.credential_reference,
            "credential_version": self.credential_version,
            "observed_at": self.observed_at.isoformat(),
            "metadata_source_identity": self.metadata_source_identity,
            "metadata_source_version": self.metadata_source_version,
            "version_provenance_reference": self.version_provenance_reference,
            "metadata_fingerprint_version": self.metadata_fingerprint_version,
        }
        payload["metadata_fingerprint"] = self.fingerprint
        return payload

    to_persisted = to_dict

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> "TenantInboundProviderCredentialMaterialMetadata":
        """Hydrate strictly, rejecting unknown fields and digest drift."""
        expected_fields = set(cls._FIELDS)
        if not isinstance(payload, Mapping) or set(payload) != expected_fields:
            raise TenantInboundProviderCredentialMaterialMetadataError(
                "M11P5R2_INVALID_METADATA_SCHEMA"
            )
        observed = payload["observed_at"]
        if isinstance(observed, str):
            try:
                observed = datetime.fromisoformat(observed)
            except ValueError as error:
                raise TenantInboundProviderCredentialMaterialMetadataError(
                    "M11P5R2_INVALID_OBSERVED_AT"
                ) from error
        try:
            return cls(
                tenant_id=cast(str, payload["tenant_id"]),
                provider_id=cast(str, payload["provider_id"]),
                merchant_configuration_id=cast(str, payload["merchant_configuration_id"]),
                merchant_configuration_version=cast(int, payload["merchant_configuration_version"]),
                merchant_configuration_fingerprint=cast(str, payload["merchant_configuration_fingerprint"]),
                credential_reference=cast(str, payload["credential_reference"]),
                credential_version=cast(str, payload["credential_version"]),
                observed_at=cast(datetime, observed),
                metadata_source_identity=cast(str, payload["metadata_source_identity"]),
                metadata_source_version=cast(str, payload["metadata_source_version"]),
                version_provenance_reference=cast(str, payload["version_provenance_reference"]),
                metadata_fingerprint_version=cast(str, payload["metadata_fingerprint_version"]),
                metadata_fingerprint=cast(str, payload["metadata_fingerprint"]),
            )
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, TenantInboundProviderCredentialMaterialMetadataError):
                raise
            raise TenantInboundProviderCredentialMaterialMetadataError(
                "M11P5R2_INVALID_METADATA"
            ) from error


__all__ = [
    "CAMPAIGN_IDENTITY",
    "HASH_ALGORITHM",
    "MAX_CREDENTIAL_VERSION_LENGTH",
    "METADATA_FINGERPRINT_SCHEMA",
    "METADATA_FINGERPRINT_VERSION",
    "TenantInboundProviderCredentialMaterialMetadata",
    "TenantInboundProviderCredentialMaterialMetadataError",
    "TenantInboundProviderCredentialMaterialObservation",
    "VERSION",
]


# ARTIFACT: tenant_inbound_provider_credential_material_metadata.py
# VERSION: v1.1.0-M11-R8-R3B-P8-P3D-P5-R4D
# AUTHORITY BOUNDARY: immutable structural metadata and value integrity only.
# TENANT POSTURE: tenant and complete merchant-configuration correlation fields are required.
# FAIL-CLOSED POSTURE: malformed values, schema drift, and fingerprint mismatch reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
