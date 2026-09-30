"""WILSY OS provider-neutral Legal Evidence cleanup discovery contract.

TITLE: Legal Evidence Provider Cleanup Discovery Port
VERSION: v1.0.0-L10A2R-C4D1-PROVIDER-CLEANUP-DISCOVERY-PORT
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Define the provider-neutral evidence contract required to discover
    incomplete provider write sessions and completed provider object versions
    under exact tenant scope before any orphan classification or cleanup action.

EPITOME:
    EXACT TENANT DISCOVERY SCOPE
    -> PROVIDER DISCOVERY OBSERVATIONS
    -> IMMUTABLE EVIDENCE

    DISCOVERED SESSION
    != ABORT AUTHORIZED

    DISCOVERED OBJECT
    != ORPHAN PROVEN
    != DELETE AUTHORIZED

    PROVIDER OBSERVATION
    != CANONICAL LEGAL EVIDENCE TRUTH

TENANT:
    Discovery is explicitly tenant-scoped. The tenant scope carries a sealed
    SHA3-512 fingerprint that later provider adapters may use to derive or
    validate opaque provider prefixes without exposing raw business identity.

AUTHORITY BOUNDARY:
    Discovery evidence only. No provider mutation, abort execution, deletion,
    retention/legal-hold decision, availability, IAM, billing, payment or
    settlement authority.

FAIL CLOSED:
    Pseudo/global tenant identities, malformed SHA3-512 values, malformed
    provider/session/object references, invalid timestamps, non-positive object
    lengths and temporal inversions reject.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Final, Protocol, runtime_checkable


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D1-PROVIDER-CLEANUP-DISCOVERY-PORT"
)

_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,511}$"
)

_SHA3_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "global_root",
        "root",
        "master",
        "*",
    }
)


class LegalEvidenceProviderCleanupDiscoveryError(
    ValueError
):
    """Stable fail-closed provider cleanup discovery contract error."""


def _text(
    name: str,
    value: object,
    *,
    limit: int = 2048,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
        or len(value) > limit
        or any(
            ord(character) < 32
            for character in value
        )
    ):
        raise LegalEvidenceProviderCleanupDiscoveryError(
            f"L10A2R_C4D1_{name.upper()}_INVALID"
        )

    return value


def _identity(
    name: str,
    value: object,
) -> str:
    text = _text(
        name,
        value,
        limit=512,
    )

    if _IDENTITY_RE.fullmatch(
        text
    ) is None:
        raise LegalEvidenceProviderCleanupDiscoveryError(
            f"L10A2R_C4D1_{name.upper()}_INVALID"
        )

    return text


def _tenant(
    value: object,
) -> str:
    tenant = _identity(
        "tenant_id",
        value,
    )

    if tenant.casefold() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceProviderCleanupDiscoveryError(
            "L10A2R_C4D1_TENANT_REQUIRED"
        )

    return tenant


def _sha3(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or _SHA3_RE.fullmatch(
            value
        ) is None
    ):
        raise LegalEvidenceProviderCleanupDiscoveryError(
            f"L10A2R_C4D1_{name.upper()}_INVALID"
        )

    return value


def _utc(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceProviderCleanupDiscoveryError(
            f"L10A2R_C4D1_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidenceProviderDiscoveryScope:
    """Immutable exact tenant scope for provider discovery."""

    tenant_id: str
    tenant_scope_fingerprint: str

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "tenant_id",
            _tenant(
                self.tenant_id
            ),
        )

        object.__setattr__(
            self,
            "tenant_scope_fingerprint",
            _sha3(
                "tenant_scope_fingerprint",
                self.tenant_scope_fingerprint,
            ),
        )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidenceIncompleteWriteSessionObservation:
    """Immutable observation of one incomplete provider write session."""

    tenant_id: str
    provider_name: str
    storage_reference: str
    write_session_reference: str
    initiated_at: datetime
    observed_at: datetime

    def __post_init__(
        self,
    ) -> None:
        tenant = _tenant(
            self.tenant_id
        )
        provider = _identity(
            "provider_name",
            self.provider_name,
        )
        storage = _text(
            "storage_reference",
            self.storage_reference,
        )
        session = _text(
            "write_session_reference",
            self.write_session_reference,
        )
        initiated = _utc(
            "initiated_at",
            self.initiated_at,
        )
        observed = _utc(
            "observed_at",
            self.observed_at,
        )

        if observed < initiated:
            raise LegalEvidenceProviderCleanupDiscoveryError(
                "L10A2R_C4D1_SESSION_OBSERVATION_TIME_INVALID"
            )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "provider_name",
            provider,
        )
        object.__setattr__(
            self,
            "storage_reference",
            storage,
        )
        object.__setattr__(
            self,
            "write_session_reference",
            session,
        )
        object.__setattr__(
            self,
            "initiated_at",
            initiated,
        )
        object.__setattr__(
            self,
            "observed_at",
            observed,
        )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidenceCompletedObjectObservation:
    """Immutable observation of one completed provider object version."""

    tenant_id: str
    provider_name: str
    storage_reference: str
    object_version_reference: str
    provider_integrity_reference: str
    content_length: int
    last_modified_at: datetime
    observed_at: datetime

    def __post_init__(
        self,
    ) -> None:
        tenant = _tenant(
            self.tenant_id
        )
        provider = _identity(
            "provider_name",
            self.provider_name,
        )
        storage = _text(
            "storage_reference",
            self.storage_reference,
        )
        version = _text(
            "object_version_reference",
            self.object_version_reference,
        )
        integrity = _text(
            "provider_integrity_reference",
            self.provider_integrity_reference,
        )

        if (
            isinstance(
                self.content_length,
                bool,
            )
            or not isinstance(
                self.content_length,
                int,
            )
            or self.content_length <= 0
        ):
            raise LegalEvidenceProviderCleanupDiscoveryError(
                "L10A2R_C4D1_CONTENT_LENGTH_INVALID"
            )

        modified = _utc(
            "last_modified_at",
            self.last_modified_at,
        )
        observed = _utc(
            "observed_at",
            self.observed_at,
        )

        if observed < modified:
            raise LegalEvidenceProviderCleanupDiscoveryError(
                "L10A2R_C4D1_OBJECT_OBSERVATION_TIME_INVALID"
            )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "provider_name",
            provider,
        )
        object.__setattr__(
            self,
            "storage_reference",
            storage,
        )
        object.__setattr__(
            self,
            "object_version_reference",
            version,
        )
        object.__setattr__(
            self,
            "provider_integrity_reference",
            integrity,
        )
        object.__setattr__(
            self,
            "last_modified_at",
            modified,
        )
        object.__setattr__(
            self,
            "observed_at",
            observed,
        )


@runtime_checkable
class LegalEvidenceProviderCleanupDiscoveryPort(
    Protocol
):
    """Provider-neutral discovery-only cleanup evidence seam."""

    def list_incomplete_write_sessions(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
    ) -> tuple[
        LegalEvidenceIncompleteWriteSessionObservation,
        ...,
    ]:
        """Return immutable incomplete-session observations for exact scope."""
        ...

    def list_completed_object_versions(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
    ) -> tuple[
        LegalEvidenceCompletedObjectObservation,
        ...,
    ]:
        """Return immutable completed-object observations for exact scope."""
        ...


__all__ = [
    "VERSION",
    "LegalEvidenceCompletedObjectObservation",
    "LegalEvidenceIncompleteWriteSessionObservation",
    "LegalEvidenceProviderCleanupDiscoveryError",
    "LegalEvidenceProviderCleanupDiscoveryPort",
    "LegalEvidenceProviderDiscoveryScope",
]


# ARTIFACT: legal_evidence_provider_cleanup_discovery_port.py
# VERSION: v1.0.0-L10A2R-C4D1-PROVIDER-CLEANUP-DISCOVERY-PORT
# AUTHORITY BOUNDARY: provider cleanup discovery evidence only
# TENANT POSTURE: exact tenant-scoped discovery
# SESSION POSTURE: discovered session is not abort authorization
# OBJECT POSTURE: discovered object is not orphan proof
# DELETION POSTURE: no deletion authority
# RETENTION POSTURE: no retention/legal-hold authority
# AVAILABILITY POSTURE: no availability authority
# PROVIDER MUTATION POSTURE: protocol exposes observation only
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
