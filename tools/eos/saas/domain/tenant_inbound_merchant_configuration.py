"""Wilsy OS tenant-owned inbound merchant configuration authority.

TITLE: Tenant Inbound Merchant Configuration
VERSION: v1.1.0-M11-R8-R3B-P8-P3D-P5-R8-P4-CREDENTIAL-METADATA-SOURCE-ROUTING
AUTHORITY: Wilsy OS Core Governance
EPITOME: Immutable tenant merchant configuration identity with explicit credential-metadata-source routing provenance.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/tenant_inbound_merchant_configuration.py
COLLABORATION / OWNERSHIP: SaaS domain owner; persistence and registered source resolution remain delegated to their paired registries.
CERTIFICATION / UPDATE DATE: 2026-09-11
CHANGELOG: v1.1.0-M11-R8-R3B-P8-P3D-P5-R8-P4-CREDENTIAL-METADATA-SOURCE-ROUTING adds explicit typed credential-metadata-source routing provenance to the immutable merchant configuration and its SHA3-512 identity; v1.0.0 established the closed PAYFAST configuration identity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only opaque identifiers, non-secret provider options, a stable secret locator, and explicit metadata-source routing provenance are accepted; raw credentials are rejected.
TENANT BOUNDARY: tenant_id is mandatory and participates in every identity and fingerprint.
AUTHORITY BOUNDARY: Configuration identity and routing provenance only; this value object does not resolve a source, retrieve credentials, authorize checkout, execute payment, infer settlement, or administer provider state.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement truth.
FAIL-CLOSED DECLARATION: Unknown providers, secret-shaped data, malformed versions, missing serialized routing fields, malformed routing keys, and digest drift reject; absent routing cannot authorize metadata-source lookup.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import re
from typing import Any, ClassVar, Mapping, TypeAlias, cast


VERSION = "v1.1.0-M11-R8-R3B-P8-P3D-P5-R8-P4-CREDENTIAL-METADATA-SOURCE-ROUTING"
_SHA3_512 = re.compile(r"^[0-9a-f]{128}$")
_VERSION = re.compile(r"^(?:0|[1-9][0-9]*)$")
_SECRET_KEY = re.compile(r"(?:secret|password|passphrase|token|credential|api[_-]?key|private[_-]?key)", re.IGNORECASE)
_OPTION_KEYS = frozenset({"mode", "merchant_name", "return_url", "cancel_url", "notify_url", "currency"})


class TenantInboundMerchantConfigurationError(ValueError):
    """Raised when immutable merchant configuration violates its closed schema."""


class InboundMerchantProviderId(str, Enum):
    """Closed V1 provider identity; capability integration is intentionally separate."""

    PAYFAST = "PAYFAST"


# Repository-facing alias retained so callers can use either explicit name.
TenantInboundMerchantProviderId: TypeAlias = InboundMerchantProviderId
InboundProviderId: TypeAlias = InboundMerchantProviderId


class _FrozenOptions(dict[str, str]):
    """Flat immutable mapping used for safe, deterministic non-secret options."""

    def _immutable(self, *args: object, **kwargs: object) -> None:
        raise TypeError("M11R8_CONFIGURATION_OPTIONS_IMMUTABLE")

    __setitem__ = _immutable  # type: ignore[assignment]
    __delitem__ = _immutable  # type: ignore[assignment]
    clear = _immutable  # type: ignore[assignment]
    pop = _immutable  # type: ignore[assignment]
    popitem = _immutable  # type: ignore[assignment]
    setdefault = _immutable  # type: ignore[assignment]
    update = _immutable  # type: ignore[assignment]


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantInboundMerchantConfigurationError(f"M11R8_INVALID_{name.upper()}")
    return value


def _version(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise TenantInboundMerchantConfigurationError("M11R8_INVALID_MERCHANT_CONFIGURATION_VERSION")
    return value


def _utc(value: object) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise TenantInboundMerchantConfigurationError("M11R8_INVALID_CREATED_AT")
    return value.astimezone(timezone.utc)


def _digest(value: object, field: str) -> str:
    if not isinstance(value, str) or _SHA3_512.fullmatch(value) is None:
        raise TenantInboundMerchantConfigurationError(f"M11R8_INVALID_{field.upper()}")
    return value


def _json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _options(value: object) -> _FrozenOptions:
    if not isinstance(value, Mapping) or set(value) - _OPTION_KEYS:
        raise TenantInboundMerchantConfigurationError("M11R8_UNKNOWN_PROVIDER_OPTION")
    result: dict[str, str] = {}
    for key, raw in value.items():
        if not isinstance(key, str) or _SECRET_KEY.search(key) or not isinstance(raw, str):
            raise TenantInboundMerchantConfigurationError("M11R8_RAW_SECRET_OR_INVALID_OPTION")
        result[_text("provider_option_key", key)] = _text("provider_option", raw)
    return _FrozenOptions(result)


@dataclass(frozen=True, slots=True)
class TenantInboundCredentialMetadataSourceRouting:
    """Exact registered metadata-source lookup key carried as routing provenance only."""

    source_identity: str
    source_contract_version: str

    _FIELDS: ClassVar[frozenset[str]] = frozenset({"source_identity", "source_contract_version"})

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_identity", _text("metadata_source_identity", self.source_identity))
        object.__setattr__(self, "source_contract_version", _text("metadata_source_contract_version", self.source_contract_version))

    def to_dict(self) -> dict[str, str]:
        return {"source_identity": self.source_identity, "source_contract_version": self.source_contract_version}

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "TenantInboundCredentialMetadataSourceRouting":
        if not isinstance(payload, dict) or set(payload) != cls._FIELDS:
            raise TenantInboundMerchantConfigurationError("M11R8_INVALID_CREDENTIAL_METADATA_SOURCE_ROUTING_SCHEMA")
        return cls(
            source_identity=cast(str, payload["source_identity"]),
            source_contract_version=cast(str, payload["source_contract_version"]),
        )


CredentialMetadataSourceRouting: TypeAlias = TenantInboundCredentialMetadataSourceRouting


def _routing(value: object) -> TenantInboundCredentialMetadataSourceRouting | None:
    if value is None:
        return None
    if not isinstance(value, TenantInboundCredentialMetadataSourceRouting):
        raise TenantInboundMerchantConfigurationError("M11R8_INVALID_CREDENTIAL_METADATA_SOURCE_ROUTING")
    return value


@dataclass(frozen=True, slots=True)
class TenantInboundMerchantConfiguration:
    """Immutable tenant/provider/account identity, excluding mutable lifecycle state."""

    merchant_configuration_id: str
    tenant_id: str
    provider_id: InboundMerchantProviderId
    merchant_account_id: str
    merchant_configuration_version: int
    non_secret_provider_options: Mapping[str, str]
    credential_secret_reference: str
    created_at: datetime
    credential_metadata_source_routing: TenantInboundCredentialMetadataSourceRouting | None = None

    _SEMANTIC_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {
            "merchant_configuration_id",
            "tenant_id",
            "provider_id",
            "merchant_account_id",
            "merchant_configuration_version",
            "non_secret_provider_options",
            "credential_secret_reference",
            "created_at",
            "credential_metadata_source_routing",
        }
    )

    def __post_init__(self) -> None:
        object.__setattr__(self, "merchant_configuration_id", _text("merchant_configuration_id", self.merchant_configuration_id))
        object.__setattr__(self, "tenant_id", _text("tenant_id", self.tenant_id))
        if not isinstance(self.provider_id, InboundMerchantProviderId):
            raise TenantInboundMerchantConfigurationError("M11R8_UNKNOWN_PROVIDER")
        object.__setattr__(self, "merchant_account_id", _text("merchant_account_id", self.merchant_account_id))
        object.__setattr__(self, "merchant_configuration_version", _version(self.merchant_configuration_version))
        object.__setattr__(self, "non_secret_provider_options", _options(self.non_secret_provider_options))
        reference = _text("credential_secret_reference", self.credential_secret_reference)
        object.__setattr__(self, "credential_secret_reference", reference)
        object.__setattr__(self, "created_at", _utc(self.created_at))
        object.__setattr__(self, "credential_metadata_source_routing", _routing(self.credential_metadata_source_routing))

    def _semantic_payload(self) -> dict[str, object]:
        """Return exactly the immutable fields covered by the configuration digest."""
        route = self.credential_metadata_source_routing
        return {
            "merchant_configuration_id": self.merchant_configuration_id,
            "tenant_id": self.tenant_id,
            "provider_id": self.provider_id.value,
            "merchant_account_id": self.merchant_account_id,
            "merchant_configuration_version": self.merchant_configuration_version,
            "non_secret_provider_options": dict(self.non_secret_provider_options),
            "credential_secret_reference": self.credential_secret_reference,
            "created_at": self.created_at.isoformat(),
            "credential_metadata_source_routing": None if route is None else route.to_dict(),
        }

    def compute_fingerprint(self) -> str:
        """Compute lowercase SHA3-512 over the canonical immutable payload."""
        return hashlib.sha3_512(_json_bytes(self._semantic_payload())).hexdigest()

    @property
    def merchant_configuration_fingerprint(self) -> str:
        """Expose the deterministic immutable configuration fingerprint."""
        return self.compute_fingerprint()

    @property
    def fingerprint(self) -> str:
        """Compatibility alias for the canonical configuration fingerprint."""
        return self.compute_fingerprint()

    def verify_fingerprint(self, fingerprint: str | None = None) -> bool:
        """Verify a supplied digest by recomputing canonical data, never by trusting it."""
        return self.compute_fingerprint() == _digest(
            self.compute_fingerprint() if fingerprint is None else fingerprint,
            "merchant_configuration_fingerprint",
        )

    def require_credential_metadata_source_routing(self) -> TenantInboundCredentialMetadataSourceRouting:
        """Return explicit routing provenance or fail closed without resolving a source."""
        route = self.credential_metadata_source_routing
        if route is None:
            raise TenantInboundMerchantConfigurationError("M11R8_CREDENTIAL_METADATA_SOURCE_ROUTING_REQUIRED")
        return route

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact strict immutable schema, including its derived digest."""
        payload = self._semantic_payload()
        payload["merchant_configuration_fingerprint"] = self.compute_fingerprint()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> TenantInboundMerchantConfiguration:
        """Hydrate strictly; reject unknown/missing fields and never backfill a digest."""
        expected = set(cls._SEMANTIC_FIELDS) | {"merchant_configuration_fingerprint"}
        if not isinstance(payload, dict) or set(payload) != expected:
            raise TenantInboundMerchantConfigurationError("M11R8_INVALID_CONFIGURATION_SCHEMA")
        data = cast(dict[str, Any], payload)
        try:
            provider = InboundMerchantProviderId(data["provider_id"])
            created = data["created_at"]
            if isinstance(created, str):
                created = datetime.fromisoformat(created)
            route_payload = data["credential_metadata_source_routing"]
            if route_payload is None:
                route = None
            elif isinstance(route_payload, dict):
                route = TenantInboundCredentialMetadataSourceRouting.from_dict(cast(dict[str, object], route_payload))
            else:
                raise TenantInboundMerchantConfigurationError("M11R8_INVALID_CREDENTIAL_METADATA_SOURCE_ROUTING")
            value = cls(
                merchant_configuration_id=data["merchant_configuration_id"],
                tenant_id=data["tenant_id"],
                provider_id=provider,
                merchant_account_id=data["merchant_account_id"],
                merchant_configuration_version=data["merchant_configuration_version"],
                non_secret_provider_options=data["non_secret_provider_options"],
                credential_secret_reference=data["credential_secret_reference"],
                created_at=created,
                credential_metadata_source_routing=route,
            )
            if value.compute_fingerprint() != _digest(data["merchant_configuration_fingerprint"], "merchant_configuration_fingerprint"):
                raise TenantInboundMerchantConfigurationError("M11R8_CONFIGURATION_FINGERPRINT_MISMATCH")
            return value
        except (KeyError, TypeError, ValueError) as error:
            if isinstance(error, TenantInboundMerchantConfigurationError):
                raise
            raise TenantInboundMerchantConfigurationError("M11R8_INVALID_CONFIGURATION") from error


# ARTIFACT: tenant_inbound_merchant_configuration.py
# VERSION: v1.1.0-M11-R8-R3B-P8-P3D-P5-R8-P4-CREDENTIAL-METADATA-SOURCE-ROUTING
# AUTHORITY BOUNDARY: immutable configuration identity and metadata-source routing provenance only; no source resolution, credential retrieval, policy, payment, or settlement authority.
# TENANT POSTURE: every configuration is explicitly tenant scoped.
# FAIL-CLOSED POSTURE: strict schema, routing, provider, secret-boundary, datetime, and fingerprint validation; no route inference or backfill.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
