"""Wilsy OS immutable credential-metadata source registry.

TITLE: Tenant Inbound Provider Credential Metadata Source Registry
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3
AUTHORITY: Wilsy OS Core Governance
EPITOME: Deployment-owned provider-neutral source descriptors with exact
         contract-version lookup and deterministic SHA3-512 integrity.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_inbound_provider_credential_metadata_source_registry.py
COLLABORATION / OWNERSHIP: SaaS billing source-registry owner; merchant
                            configuration routing, authenticated adapters,
                            security evidence, and provider binding remain
                            separate owners.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3 establishes immutable deployment
           registration, exact two-field lookup, strict descriptor hydration,
           and canonical SHA3-512 entry evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Registry metadata contains no secrets, tokens,
                             provider connections, KMS access, or clients.
TENANT BOUNDARY: Source registration is platform-scoped and intentionally has
                 no tenant_id; tenant route authorization remains issuance-owned.
AUTHORITY BOUNDARY: Registration resolves an approved implementation contract;
                    it does not authorize tenant selection or runtime access.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Unknown fields, malformed identities, duplicate keys,
                          fingerprint drift, and unknown lookups reject.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import hmac
import json
import re
import unicodedata
from types import MappingProxyType
from typing import ClassVar, Iterable, Mapping, TypeAlias, cast


VERSION = "v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3"
CAMPAIGN_IDENTITY = "M11-R8-R3B-P8-P3D-P5-R8-P3"
ENTRY_FINGERPRINT_SCHEMA = (
    "WILSY-TENANT-INBOUND-PROVIDER-CREDENTIAL-METADATA-SOURCE-REGISTRY-ENTRY/V1"
)
ENTRY_FINGERPRINT_ALGORITHM = "SHA3-512"
ENTRY_FINGERPRINT_HEX_LENGTH = 128
CAPABILITY_CLASS_CREDENTIAL_METADATA = "credential_metadata"

_ENTRY_FIELDS = (
    "source_identity",
    "source_contract_version",
    "implementation_identity",
    "capability_class",
    "registration_provenance",
    "entry_fingerprint",
)
_SEMANTIC_FIELDS = _ENTRY_FIELDS[:-1]
_PROVENANCE_FIELDS = ("platform_registration_id", "deployment_certification_id")
ENTRY_FINGERPRINT_SEMANTIC_FIELDS = _SEMANTIC_FIELDS
ENTRY_FINGERPRINT_JSON_KEY_ORDER = (
    "schema",
    "source_identity",
    "source_contract_version",
    "implementation_identity",
    "capability_class",
    "registration_provenance",
)
REGISTRATION_PROVENANCE_JSON_KEY_ORDER = _PROVENANCE_FIELDS
ENTRY_FINGERPRINT_JSON_SEPARATORS = (",", ":")
ENTRY_FINGERPRINT_TEXT_ENCODING = "UTF-8"
ENTRY_FINGERPRINT_JSON_ALLOW_NAN_INFINITY = False
ENTRY_FINGERPRINT_JSON_TRAILING_NEWLINE = False
ENTRY_FINGERPRINT_JSON_TRAILING_WHITESPACE = False
_TOKEN = re.compile(r"^[^\s/\\]{1,128}$")
_IMPLEMENTATION_KEY = re.compile(r"^impl:[^\s/\\]{1,120}$")
_DIGEST = re.compile(r"^[0-9a-f]{128}$")


class TenantInboundCredentialMetadataSourceRegistryError(ValueError):
    """Base fail-closed source-registry error."""


class TenantInboundCredentialMetadataSourceDescriptorError(
    TenantInboundCredentialMetadataSourceRegistryError
):
    """A descriptor or provenance value violates the closed contract."""


class TenantInboundCredentialMetadataSourceFingerprintMismatchError(
    TenantInboundCredentialMetadataSourceDescriptorError
):
    """Persisted entry evidence differs from deterministic recomputation."""


class TenantInboundCredentialMetadataSourceUnknownError(
    TenantInboundCredentialMetadataSourceRegistryError
):
    """The requested source identity has no registered descriptor."""


class TenantInboundCredentialMetadataSourceContractVersionUnknownError(
    TenantInboundCredentialMetadataSourceRegistryError
):
    """The source exists, but the exact requested contract version is absent."""


class TenantInboundCredentialMetadataSourceDuplicateRegistrationError(
    TenantInboundCredentialMetadataSourceRegistryError
):
    """Two immutable descriptors attempted to claim one lookup key."""


# Concise aliases are additive and preserve one error authority.
DescriptorError = TenantInboundCredentialMetadataSourceDescriptorError
FingerprintMismatchError = TenantInboundCredentialMetadataSourceFingerprintMismatchError
UnknownSourceError = TenantInboundCredentialMetadataSourceUnknownError
UnknownContractVersionError = TenantInboundCredentialMetadataSourceContractVersionUnknownError
DuplicateRegistrationError = TenantInboundCredentialMetadataSourceDuplicateRegistrationError


def _normalise_token(name: str, value: object) -> str:
    """Return NFC-normalised, trimmed identity text or fail closed."""
    if not isinstance(value, str):
        raise TenantInboundCredentialMetadataSourceDescriptorError(
            f"M11P8P3_INVALID_{name.upper()}"
        )
    if value != value.strip():
        raise TenantInboundCredentialMetadataSourceDescriptorError(
            f"M11P8P3_INVALID_{name.upper()}"
        )
    normalised = unicodedata.normalize("NFC", value.strip())
    if (
        not normalised
        or _TOKEN.fullmatch(normalised) is None
        or not normalised[0].isalnum()
        or any(unicodedata.category(char).startswith("C") for char in normalised)
    ):
        raise TenantInboundCredentialMetadataSourceDescriptorError(
            f"M11P8P3_INVALID_{name.upper()}"
        )
    return normalised


def _implementation_identity(value: object) -> str:
    """Require an opaque implementation key, never a Python import path."""
    if not isinstance(value, str):
        raise TenantInboundCredentialMetadataSourceDescriptorError(
            "M11P8P3_INVALID_IMPLEMENTATION_IDENTITY"
        )
    if value != value.strip():
        raise TenantInboundCredentialMetadataSourceDescriptorError(
            "M11P8P3_INVALID_IMPLEMENTATION_IDENTITY"
        )
    normalised = unicodedata.normalize("NFC", value.strip())
    if (
        _IMPLEMENTATION_KEY.fullmatch(normalised) is None
        or any(unicodedata.category(char).startswith("C") for char in normalised)
    ):
        raise TenantInboundCredentialMetadataSourceDescriptorError(
            "M11P8P3_INVALID_IMPLEMENTATION_IDENTITY"
        )
    return normalised


@dataclass(frozen=True, slots=True)
class TenantInboundCredentialMetadataSourceRegistrationProvenance:
    """Immutable platform registration evidence, not tenant authorization."""

    platform_registration_id: str
    deployment_certification_id: str

    _FIELDS: ClassVar[tuple[str, str]] = _PROVENANCE_FIELDS

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "platform_registration_id",
            _normalise_token("platform_registration_id", self.platform_registration_id),
        )
        object.__setattr__(
            self,
            "deployment_certification_id",
            _normalise_token(
                "deployment_certification_id", self.deployment_certification_id
            ),
        )

    @classmethod
    def from_mapping(
        cls, value: Mapping[str, object]
    ) -> "TenantInboundCredentialMetadataSourceRegistrationProvenance":
        """Hydrate exactly the two provenance fields; reject unknown fields."""
        if not isinstance(value, Mapping) or tuple(value) != _PROVENANCE_FIELDS:
            raise TenantInboundCredentialMetadataSourceDescriptorError(
                "M11P8P3_INVALID_REGISTRATION_PROVENANCE"
            )
        return cls(
            platform_registration_id=cast(str, value["platform_registration_id"]),
            deployment_certification_id=cast(str, value["deployment_certification_id"]),
        )

    def to_dict(self) -> dict[str, str]:
        """Return the exact ordered provenance representation."""
        return {
            "platform_registration_id": self.platform_registration_id,
            "deployment_certification_id": self.deployment_certification_id,
        }


RegistrationProvenance: TypeAlias = (
    TenantInboundCredentialMetadataSourceRegistrationProvenance
    | Mapping[str, object]
)


def _provenance(value: RegistrationProvenance) -> TenantInboundCredentialMetadataSourceRegistrationProvenance:
    """Convert a provenance value to its immutable typed representation."""
    if isinstance(value, TenantInboundCredentialMetadataSourceRegistrationProvenance):
        return value
    if isinstance(value, Mapping):
        return TenantInboundCredentialMetadataSourceRegistrationProvenance.from_mapping(value)
    raise TenantInboundCredentialMetadataSourceDescriptorError(
        "M11P8P3_INVALID_REGISTRATION_PROVENANCE"
    )


def _canonical_payload(
    source_identity: str,
    source_contract_version: str,
    implementation_identity: str,
    capability_class: str,
    registration_provenance: TenantInboundCredentialMetadataSourceRegistrationProvenance,
) -> dict[str, object]:
    """Build the frozen outer and nested key order used for hashing."""
    return {
        "schema": ENTRY_FINGERPRINT_SCHEMA,
        "source_identity": source_identity,
        "source_contract_version": source_contract_version,
        "implementation_identity": implementation_identity,
        "capability_class": capability_class,
        "registration_provenance": registration_provenance.to_dict(),
    }


def canonical_entry_fingerprint_bytes(
    source_identity: str,
    source_contract_version: str,
    implementation_identity: str,
    capability_class: str,
    registration_provenance: RegistrationProvenance,
) -> bytes:
    """Return the exact UTF-8 bytes of one validated canonical descriptor payload."""
    source = _normalise_token("source_identity", source_identity)
    contract = _normalise_token("source_contract_version", source_contract_version)
    implementation = _implementation_identity(implementation_identity)
    if capability_class != CAPABILITY_CLASS_CREDENTIAL_METADATA:
        raise TenantInboundCredentialMetadataSourceDescriptorError(
            "M11P8P3_INVALID_CAPABILITY_CLASS"
        )
    provenance = _provenance(registration_provenance)
    payload = _canonical_payload(source, contract, implementation, capability_class, provenance)
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=False,
        allow_nan=False,
        separators=ENTRY_FINGERPRINT_JSON_SEPARATORS,
    ).encode("utf-8")


def compute_entry_fingerprint(
    source_identity: str,
    source_contract_version: str,
    implementation_identity: str,
    capability_class: str,
    registration_provenance: RegistrationProvenance,
) -> str:
    """Compute the deterministic lowercase SHA3-512 descriptor fingerprint."""
    return hashlib.sha3_512(
        canonical_entry_fingerprint_bytes(
            source_identity,
            source_contract_version,
            implementation_identity,
            capability_class,
            registration_provenance,
        )
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class TenantInboundCredentialMetadataSourceDescriptor:
    """Immutable platform-approved source descriptor resolved by exact key.

    ``entry_fingerprint`` is derived by the constructor.  Callers cannot
    provide a digest; persisted hydration uses :meth:`from_dict`, recomputes
    the digest, and rejects any mismatch.  No source client is instantiated.
    """

    source_identity: str
    source_contract_version: str
    implementation_identity: str
    capability_class: str
    registration_provenance: RegistrationProvenance
    entry_fingerprint: str | None = None

    _FIELDS: ClassVar[tuple[str, ...]] = _ENTRY_FIELDS

    def __post_init__(self) -> None:
        source = _normalise_token("source_identity", self.source_identity)
        contract = _normalise_token("source_contract_version", self.source_contract_version)
        implementation = _implementation_identity(self.implementation_identity)
        if self.capability_class != CAPABILITY_CLASS_CREDENTIAL_METADATA:
            raise TenantInboundCredentialMetadataSourceDescriptorError(
                "M11P8P3_INVALID_CAPABILITY_CLASS"
            )
        provenance = _provenance(self.registration_provenance)
        if self.entry_fingerprint is not None:
            raise TenantInboundCredentialMetadataSourceDescriptorError(
                "M11P8P3_CALLER_SUPPLIED_ENTRY_FINGERPRINT_FORBIDDEN"
            )
        object.__setattr__(self, "source_identity", source)
        object.__setattr__(self, "source_contract_version", contract)
        object.__setattr__(self, "implementation_identity", implementation)
        object.__setattr__(self, "registration_provenance", provenance)
        object.__setattr__(
            self,
            "entry_fingerprint",
            compute_entry_fingerprint(source, contract, implementation, self.capability_class, provenance),
        )

    @classmethod
    def create(
        cls,
        source_identity: str,
        source_contract_version: str,
        implementation_identity: str,
        capability_class: str,
        registration_provenance: RegistrationProvenance,
    ) -> "TenantInboundCredentialMetadataSourceDescriptor":
        """Construct a descriptor while keeping fingerprint derivation internal."""
        return cls(
            source_identity=source_identity,
            source_contract_version=source_contract_version,
            implementation_identity=implementation_identity,
            capability_class=capability_class,
            registration_provenance=registration_provenance,
        )

    @classmethod
    def from_dict(
        cls, payload: Mapping[str, object]
    ) -> "TenantInboundCredentialMetadataSourceDescriptor":
        """Strictly hydrate six fields and verify persisted fingerprint integrity."""
        if not isinstance(payload, Mapping) or tuple(payload) != _ENTRY_FIELDS:
            raise TenantInboundCredentialMetadataSourceDescriptorError(
                "M11P8P3_INVALID_DESCRIPTOR_SCHEMA"
            )
        descriptor = cls.create(
            source_identity=cast(str, payload["source_identity"]),
            source_contract_version=cast(str, payload["source_contract_version"]),
            implementation_identity=cast(str, payload["implementation_identity"]),
            capability_class=cast(str, payload["capability_class"]),
            registration_provenance=cast(RegistrationProvenance, payload["registration_provenance"]),
        )
        stored = payload["entry_fingerprint"]
        if not isinstance(stored, str) or _DIGEST.fullmatch(stored) is None:
            raise TenantInboundCredentialMetadataSourceFingerprintMismatchError(
                "M11P8P3_INVALID_ENTRY_FINGERPRINT"
            )
        assert descriptor.entry_fingerprint is not None
        if not hmac.compare_digest(stored, descriptor.entry_fingerprint):
            raise TenantInboundCredentialMetadataSourceFingerprintMismatchError(
                "M11P8P3_ENTRY_FINGERPRINT_MISMATCH"
            )
        return descriptor

    def canonical_payload(self) -> dict[str, object]:
        """Return a fresh canonical payload without the derived digest."""
        return _canonical_payload(
            self.source_identity,
            self.source_contract_version,
            self.implementation_identity,
            self.capability_class,
            _provenance(self.registration_provenance),
        )

    def canonical_bytes(self) -> bytes:
        """Return canonical bytes used for this descriptor's fingerprint."""
        return canonical_entry_fingerprint_bytes(
            self.source_identity,
            self.source_contract_version,
            self.implementation_identity,
            self.capability_class,
            self.registration_provenance,
        )

    def verify_fingerprint(self) -> bool:
        """Verify the derived digest against a fresh deterministic computation."""
        assert self.entry_fingerprint is not None
        return hmac.compare_digest(
            self.entry_fingerprint,
            compute_entry_fingerprint(
                self.source_identity,
                self.source_contract_version,
                self.implementation_identity,
                self.capability_class,
                self.registration_provenance,
            ),
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact six-field descriptor contract."""
        assert self.entry_fingerprint is not None
        return {
            "source_identity": self.source_identity,
            "source_contract_version": self.source_contract_version,
            "implementation_identity": self.implementation_identity,
            "capability_class": self.capability_class,
            "registration_provenance": _provenance(self.registration_provenance).to_dict(),
            "entry_fingerprint": self.entry_fingerprint,
        }


class TenantInboundCredentialMetadataSourceRegistry:
    """Deployment-owned immutable descriptor map with exact two-field lookup.

    Construction is the deployment boundary.  There are deliberately no
    runtime register/unregister/replace methods.  Registry lookup returns
    metadata only and never opens a network, Mongo, KMS, provider, or client.
    """

    __slots__ = ("_entries",)

    def __init__(
        self, descriptors: Iterable[TenantInboundCredentialMetadataSourceDescriptor]
    ) -> None:
        entries: dict[tuple[str, str], TenantInboundCredentialMetadataSourceDescriptor] = {}
        for descriptor in descriptors:
            if not isinstance(descriptor, TenantInboundCredentialMetadataSourceDescriptor):
                raise TenantInboundCredentialMetadataSourceRegistryError(
                    "M11P8P3_DESCRIPTOR_REQUIRED"
                )
            if not descriptor.verify_fingerprint():
                raise TenantInboundCredentialMetadataSourceFingerprintMismatchError(
                    "M11P8P3_ENTRY_FINGERPRINT_MISMATCH"
                )
            key = (descriptor.source_identity, descriptor.source_contract_version)
            if key in entries:
                raise TenantInboundCredentialMetadataSourceDuplicateRegistrationError(
                    "M11P8P3_DUPLICATE_REGISTRATION_KEY"
                )
            entries[key] = descriptor
        object.__setattr__(self, "_entries", MappingProxyType(entries))

    def __setattr__(self, name: str, value: object) -> None:
        """Prevent mutation after deployment construction."""
        raise AttributeError("M11P8P3_REGISTRY_IMMUTABLE")

    @classmethod
    def from_descriptors(
        cls, descriptors: Iterable[TenantInboundCredentialMetadataSourceDescriptor]
    ) -> "TenantInboundCredentialMetadataSourceRegistry":
        """Build one deployment-owned immutable registry snapshot."""
        return cls(tuple(descriptors))

    def resolve(
        self, source_identity: str, source_contract_version: str
    ) -> TenantInboundCredentialMetadataSourceDescriptor:
        """Resolve exactly one descriptor; unknown identity/version fail closed."""
        source = _normalise_token("source_identity", source_identity)
        contract = _normalise_token("source_contract_version", source_contract_version)
        descriptor = self._entries.get((source, contract))
        if descriptor is not None:
            return descriptor
        if any(key[0] == source for key in self._entries):
            raise TenantInboundCredentialMetadataSourceContractVersionUnknownError(
                "M11P8P3_UNKNOWN_SOURCE_CONTRACT_VERSION"
            )
        raise TenantInboundCredentialMetadataSourceUnknownError(
            "M11P8P3_UNKNOWN_SOURCE_IDENTITY"
        )

    lookup = resolve

    def descriptors(self) -> tuple[TenantInboundCredentialMetadataSourceDescriptor, ...]:
        """Return an immutable deterministic descriptor snapshot."""
        return tuple(self._entries[key] for key in sorted(self._entries))

    def __len__(self) -> int:
        """Return the number of registered immutable descriptors."""
        return len(self._entries)


DEFAULT_SOURCE_REGISTRY = TenantInboundCredentialMetadataSourceRegistry.from_descriptors(())


__all__ = [
    "CAMPAIGN_IDENTITY",
    "CAPABILITY_CLASS_CREDENTIAL_METADATA",
    "DEFAULT_SOURCE_REGISTRY",
    "ENTRY_FINGERPRINT_ALGORITHM",
    "ENTRY_FINGERPRINT_HEX_LENGTH",
    "ENTRY_FINGERPRINT_JSON_ALLOW_NAN_INFINITY",
    "ENTRY_FINGERPRINT_JSON_KEY_ORDER",
    "ENTRY_FINGERPRINT_JSON_SEPARATORS",
    "ENTRY_FINGERPRINT_JSON_TRAILING_NEWLINE",
    "ENTRY_FINGERPRINT_JSON_TRAILING_WHITESPACE",
    "ENTRY_FINGERPRINT_SCHEMA",
    "ENTRY_FINGERPRINT_SEMANTIC_FIELDS",
    "ENTRY_FINGERPRINT_TEXT_ENCODING",
    "REGISTRATION_PROVENANCE_JSON_KEY_ORDER",
    "RegistrationProvenance",
    "TenantInboundCredentialMetadataSourceDescriptor",
    "TenantInboundCredentialMetadataSourceDuplicateRegistrationError",
    "TenantInboundCredentialMetadataSourceFingerprintMismatchError",
    "TenantInboundCredentialMetadataSourceRegistrationProvenance",
    "TenantInboundCredentialMetadataSourceRegistry",
    "TenantInboundCredentialMetadataSourceRegistryError",
    "TenantInboundCredentialMetadataSourceUnknownError",
    "TenantInboundCredentialMetadataSourceContractVersionUnknownError",
    "canonical_entry_fingerprint_bytes",
    "compute_entry_fingerprint",
]


# ARTIFACT: tenant_inbound_provider_credential_metadata_source_registry.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3
# AUTHORITY BOUNDARY: immutable platform source registration and exact resolution only
# TENANT POSTURE: no tenant identity in platform registry; tenant authorization remains issuance-owned
# FAIL-CLOSED POSTURE: unknown, ambiguous, mutable, or fingerprint-divergent descriptors reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
