"""WILSY OS — Legal Evidence provider coverage enumeration contract.

TITLE: Legal Evidence Provider Coverage Enumeration Contract
VERSION: v1.0.0-L10A2R-C4D6B-PROVIDER-COVERAGE-ENUMERATION
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
PURPOSE:
    Define a provider-neutral, non-authorizing page contract for later exhaustive
    Legal Evidence provider enumeration without changing the certified C4D2
    cleanup-discovery observation seam.

EPITOME:
    One page binds exact tenant/provider scope, one enumeration kind, one
    observation time, the exact observations returned for that page and an
    opaque provider continuation reference. A page is evidence of a page only.
    Neither absence nor presence of a continuation reference proves complete
    provider coverage.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_provider_coverage_enumeration_port.py

COLLABORATION / OWNERSHIP:
    C4D1/C4D2 own provider observations. C4D6B introduces only a sibling
    pagination-capable enumeration contract. Later gates own provider-specific
    pagination, trusted complete-coverage issuance, persistence, orphan proof,
    retention/hold composition and deletion authorization/execution.

CERTIFICATION / UPDATE DATE: 2026-10-01

CHANGELOG:
    v1.0.0-L10A2R-C4D6B establishes immutable deterministic page evidence and a
    sibling provider-neutral enumeration protocol without changing C4D2.

AUTHORITY BOUNDARY:
    Enumeration-page evidence only. This module does not assert exhaustive
    provider coverage, canonical ownership, disownership, orphan status,
    retention satisfaction, legal-hold release, abort authority or deletion
    authority. It performs no provider or database I/O.

TENANT BOUNDARY:
    Every page binds one exact tenant scope fingerprint and all observations must
    correlate to that tenant and provider.

FAIL-CLOSED POSTURE:
    Invalid type, tenant/provider mismatch, observation-time mismatch,
    enumeration-kind mismatch, malformed continuation, version drift or
    fingerprint mismatch rejects.

FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains exclusive financial execution authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import hmac
import json
import re
from typing import Final, Protocol, TypeAlias, runtime_checkable

from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceIncompleteWriteSessionObservation,
    LegalEvidenceProviderDiscoveryScope,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D6B-PROVIDER-COVERAGE-ENUMERATION"
)

_SCHEMA: Final[str] = (
    "WILSY-LEGAL-EVIDENCE-PROVIDER-COVERAGE-ENUMERATION-PAGE/V1"
)

_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,511}$"
)

_SHA3_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)


class LegalEvidenceProviderCoverageEnumerationError(ValueError):
    """Reject malformed or authority-expanding C4D6B enumeration evidence."""


class LegalEvidenceProviderEnumerationKind(StrEnum):
    """Provider collection being enumerated by one C4D6B page."""

    INCOMPLETE_WRITE_SESSIONS = "INCOMPLETE_WRITE_SESSIONS"
    COMPLETED_OBJECT_VERSIONS = "COMPLETED_OBJECT_VERSIONS"


LegalEvidenceProviderEnumerationObservation: TypeAlias = (
    LegalEvidenceIncompleteWriteSessionObservation
    | LegalEvidenceCompletedObjectObservation
)


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise LegalEvidenceProviderCoverageEnumerationError(
            f"L10A2R_C4D6B_{name.upper()}_INVALID"
        )
    return value


def _identity(
    name: str,
    value: object,
) -> str:
    text = _text(name, value)
    if _IDENTITY_RE.fullmatch(text) is None:
        raise LegalEvidenceProviderCoverageEnumerationError(
            f"L10A2R_C4D6B_{name.upper()}_INVALID"
        )
    return text


def _sha3(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or _SHA3_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceProviderCoverageEnumerationError(
            f"L10A2R_C4D6B_{name.upper()}_INVALID"
        )
    return value


def _utc(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceProviderCoverageEnumerationError(
            f"L10A2R_C4D6B_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


def _observation_payload(
    value: LegalEvidenceProviderEnumerationObservation,
) -> dict[str, object]:
    if type(value) is LegalEvidenceIncompleteWriteSessionObservation:
        return {
            "kind": "INCOMPLETE_WRITE_SESSION",
            "tenant_id": value.tenant_id,
            "provider_name": value.provider_name,
            "storage_reference": value.storage_reference,
            "write_session_reference": value.write_session_reference,
            "initiated_at": value.initiated_at.isoformat(),
            "observed_at": value.observed_at.isoformat(),
        }

    if type(value) is LegalEvidenceCompletedObjectObservation:
        return {
            "kind": "COMPLETED_OBJECT_VERSION",
            "tenant_id": value.tenant_id,
            "provider_name": value.provider_name,
            "storage_reference": value.storage_reference,
            "object_version_reference":
                value.object_version_reference,
            "provider_integrity_reference":
                value.provider_integrity_reference,
            "content_length": value.content_length,
            "last_modified_at":
                value.last_modified_at.isoformat(),
            "observed_at":
                value.observed_at.isoformat(),
            "write_intent_metadata_state":
                value.write_intent_metadata_state.value,
            "write_intent_fingerprint":
                value.write_intent_fingerprint,
        }

    raise LegalEvidenceProviderCoverageEnumerationError(
        "L10A2R_C4D6B_OBSERVATION_TYPE_INVALID"
    )


def _page_fingerprint(
    *,
    tenant_id: str,
    tenant_scope_fingerprint: str,
    provider_name: str,
    enumeration_kind: LegalEvidenceProviderEnumerationKind,
    observed_at: datetime,
    observations: tuple[
        LegalEvidenceProviderEnumerationObservation,
        ...,
    ],
    next_page_reference: str | None,
) -> str:
    payload = {
        "schema": _SCHEMA,
        "version": VERSION,
        "tenant_id": tenant_id,
        "tenant_scope_fingerprint": tenant_scope_fingerprint,
        "provider_name": provider_name,
        "enumeration_kind": enumeration_kind.value,
        "observed_at": observed_at.isoformat(),
        "observations": [
            _observation_payload(value)
            for value in observations
        ],
        "next_page_reference": next_page_reference,
    }

    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode(
        "utf-8"
    )

    return hashlib.sha3_512(
        encoded
    ).hexdigest()


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidenceProviderEnumerationPage:
    """Immutable non-authorizing evidence for exactly one provider page."""

    tenant_id: str
    tenant_scope_fingerprint: str
    provider_name: str
    enumeration_kind: LegalEvidenceProviderEnumerationKind
    observed_at: datetime
    observations: tuple[
        LegalEvidenceProviderEnumerationObservation,
        ...,
    ]
    next_page_reference: str | None = None
    enumeration_page_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(
        self,
    ) -> None:
        tenant = _identity(
            "tenant_id",
            self.tenant_id,
        )
        scope_fingerprint = _sha3(
            "tenant_scope_fingerprint",
            self.tenant_scope_fingerprint,
        )
        provider = _identity(
            "provider_name",
            self.provider_name,
        )

        if (
            type(self.enumeration_kind)
            is not LegalEvidenceProviderEnumerationKind
        ):
            raise LegalEvidenceProviderCoverageEnumerationError(
                "L10A2R_C4D6B_ENUMERATION_KIND_INVALID"
            )

        observed = _utc(
            "observed_at",
            self.observed_at,
        )

        if not isinstance(
            self.observations,
            tuple,
        ):
            raise LegalEvidenceProviderCoverageEnumerationError(
                "L10A2R_C4D6B_OBSERVATIONS_INVALID"
            )

        expected_type = (
            LegalEvidenceIncompleteWriteSessionObservation
            if self.enumeration_kind
            is LegalEvidenceProviderEnumerationKind
            .INCOMPLETE_WRITE_SESSIONS
            else LegalEvidenceCompletedObjectObservation
        )

        for value in self.observations:
            if type(value) is not expected_type:
                raise LegalEvidenceProviderCoverageEnumerationError(
                    "L10A2R_C4D6B_OBSERVATION_KIND_MISMATCH"
                )

            if (
                value.tenant_id != tenant
                or value.provider_name != provider
                or value.observed_at != observed
            ):
                raise LegalEvidenceProviderCoverageEnumerationError(
                    "L10A2R_C4D6B_OBSERVATION_SCOPE_MISMATCH"
                )

        continuation = self.next_page_reference

        if continuation is not None:
            continuation = _text(
                "next_page_reference",
                continuation,
            )

        if self.enumeration_page_version != VERSION:
            raise LegalEvidenceProviderCoverageEnumerationError(
                "L10A2R_C4D6B_VERSION_INVALID"
            )

        digest = _page_fingerprint(
            tenant_id=tenant,
            tenant_scope_fingerprint=scope_fingerprint,
            provider_name=provider,
            enumeration_kind=self.enumeration_kind,
            observed_at=observed,
            observations=self.observations,
            next_page_reference=continuation,
        )

        if self.fingerprint:
            if (
                not isinstance(
                    self.fingerprint,
                    str,
                )
                or not hmac.compare_digest(
                    self.fingerprint,
                    digest,
                )
            ):
                raise LegalEvidenceProviderCoverageEnumerationError(
                    "L10A2R_C4D6B_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "tenant_scope_fingerprint",
            scope_fingerprint,
        )
        object.__setattr__(
            self,
            "provider_name",
            provider,
        )
        object.__setattr__(
            self,
            "observed_at",
            observed,
        )
        object.__setattr__(
            self,
            "next_page_reference",
            continuation,
        )
        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )


@runtime_checkable
class LegalEvidenceProviderCoverageEnumerationPort(
    Protocol
):
    """Sibling provider seam for page-wise enumeration; never coverage proof."""

    def list_incomplete_write_session_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        """Return one non-authorizing incomplete-session page."""
        ...

    def list_completed_object_version_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: datetime,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        """Return one non-authorizing completed-object-version page."""
        ...


__all__ = [
    "VERSION",
    "LegalEvidenceProviderCoverageEnumerationError",
    "LegalEvidenceProviderCoverageEnumerationPort",
    "LegalEvidenceProviderEnumerationKind",
    "LegalEvidenceProviderEnumerationObservation",
    "LegalEvidenceProviderEnumerationPage",
]


# ARTIFACT: legal_evidence_provider_coverage_enumeration_port.py
# VERSION: v1.0.0-L10A2R-C4D6B-PROVIDER-COVERAGE-ENUMERATION
# AUTHORITY BOUNDARY: non-authorizing provider enumeration page evidence only
# COVERAGE POSTURE: page evidence is not exhaustive-coverage attestation
# TENANT POSTURE: exact tenant-scope fingerprint and provider correlation
# CONTINUATION POSTURE: opaque next-page reference is evidence only, not authority
# ORPHAN POSTURE: no orphan proof or disownership inference
# RETENTION / HOLD POSTURE: no retention or legal-hold authority
# DELETION POSTURE: no abort, delete authorization or provider deletion authority
# PROVIDER MUTATION POSTURE: protocol performs no provider operation by itself
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
