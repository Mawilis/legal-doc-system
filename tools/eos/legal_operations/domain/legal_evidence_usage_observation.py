"""WILSY OS immutable Legal Evidence usage-observation domain contract.

TITLE: Legal Evidence Usage Observation
VERSION: v1.0.0-L10A2Q-P3A-LEGAL-EVIDENCE-USAGE-OBSERVATION
AUTHORITY: WILSY OS Core Governance
PURPOSE:
    Derive one immutable source-evidenced Legal Evidence consumption fact from
    one already-canonical LegalEvidenceContent value.

EPITOME:
    PROVIDER OBJECT COMPLETE
    != LEGAL EVIDENCE COMMITTED
    != USAGE OBSERVED
    != REMAINING CAPACITY
    != CAPACITY RESERVED
    != STORAGE ADMISSION

COLLABORATION / OWNERSHIP:
    L10A1 LegalEvidenceContent owns canonical Legal Evidence content identity,
    exact committed content length, tenant/matter/document coordinates and
    canonical content evidence fingerprint.
    L10A2Q-P3 owns immutable usage observation only.
    L10A2Q-P4 owns remaining-capacity derivation.
    L10A2Q-P5 owns reservation, expiry, concurrency and reconciliation.

CERTIFICATION / UPDATE DATE: 2026-09-30

TENANT BOUNDARY:
    Tenant, matter, document and content coordinates are copied only from one
    canonical LegalEvidenceContent value. No caller-selected tenant override
    exists. Pseudo/global tenant identities reject during hydration.

AUTHORITY BOUNDARY:
    Observed consumption only. This artifact grants no entitlement, quota,
    remaining-capacity, reservation, admission, billing, payment, settlement,
    execution, deletion, retention or legal-hold authority.

FINANCIAL AUTHORITY BOUNDARY:
    No price, amount, currency, invoice, payment or settlement fields exist.
    Kennel EOS remains exclusive financial execution authority.

FAIL-CLOSED DECLARATION:
    Invalid content type, malformed identity, invalid dimensions/time, schema
    drift, persisted shape drift or fingerprint divergence reject.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Final, Mapping, cast

from tools.eos.legal_operations.domain.legal_evidence_content import (
    LegalEvidenceContent,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2Q-P3A-LEGAL-EVIDENCE-USAGE-OBSERVATION"
)
SCHEMA: Final[str] = (
    "WILSY-LEGAL-EVIDENCE-USAGE-OBSERVATION/V1"
)

_HEX: Final[frozenset[str]] = frozenset("0123456789abcdef")
_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,511}$"
)
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "root",
        "*",
        "global_root",
    }
)

_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id",
    "usage_observation_id",
    "case_matter_id",
    "document_id",
    "content_reference",
    "content_fingerprint",
    "content_evidence_fingerprint",
    "storage_bytes_added",
    "monthly_ingress_bytes",
    "document_versions_added",
    "occurred_at",
    "schema",
    "observation_version",
    "fingerprint",
)


class LegalEvidenceUsageObservationError(ValueError):
    """Raised when Legal Evidence usage evidence violates the closed contract."""


def _identity(name: str, value: object) -> str:
    """Require one bounded opaque identity."""
    if (
        not isinstance(value, str)
        or value != value.strip()
        or not value
        or not _IDENTITY_RE.fullmatch(value)
    ):
        raise LegalEvidenceUsageObservationError(
            f"L10A2Q_P3A_{name.upper()}_INVALID"
        )
    return value


def _tenant(value: object) -> str:
    """Require one non-pseudo tenant identity."""
    tenant = _identity("tenant_id", value)
    if tenant.casefold() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceUsageObservationError(
            "L10A2Q_P3A_TENANT_REQUIRED"
        )
    return tenant


def _sha3(name: str, value: object) -> str:
    """Require canonical lowercase SHA3-512 hexadecimal evidence."""
    if (
        not isinstance(value, str)
        or len(value) != 128
        or set(value) > _HEX
    ):
        raise LegalEvidenceUsageObservationError(
            f"L10A2Q_P3A_{name.upper()}_INVALID"
        )
    return value


def _positive_int(name: str, value: object) -> int:
    """Require one positive integer without bool coercion."""
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        raise LegalEvidenceUsageObservationError(
            f"L10A2Q_P3A_{name.upper()}_INVALID"
        )
    return value


def _when(value: object) -> datetime:
    """Require one timezone-aware instant normalized to UTC."""
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceUsageObservationError(
            "L10A2Q_P3A_OCCURRED_AT_INVALID"
        )
    return value.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Serialize deterministic domain primitives."""
    if isinstance(value, datetime):
        return (
            value.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )
    return value


def _observation_identity(content: LegalEvidenceContent) -> str:
    """Derive one deterministic identity from canonical content evidence."""
    raw = json.dumps(
        {
            "tenant_id": content.tenant_id,
            "case_matter_id": content.case_matter_id,
            "document_id": content.document_id,
            "content_reference": content.content_reference,
            "content_evidence_fingerprint": content.fingerprint,
        },
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    digest = hashlib.sha3_512(raw).hexdigest()

    return f"legal-evidence-usage:{digest[:48]}"


@dataclass(frozen=True, slots=True)
class LegalEvidenceUsageObservation:
    """Immutable observation of one canonical Legal Evidence content commit."""

    tenant_id: str
    usage_observation_id: str
    case_matter_id: str
    document_id: str
    content_reference: str
    content_fingerprint: str
    content_evidence_fingerprint: str
    storage_bytes_added: int
    monthly_ingress_bytes: int
    document_versions_added: int
    occurred_at: datetime
    schema: str = SCHEMA
    observation_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate and seal one immutable usage observation."""
        tenant = _tenant(self.tenant_id)
        usage_id = _identity(
            "usage_observation_id",
            self.usage_observation_id,
        )
        matter = _identity("case_matter_id", self.case_matter_id)
        document = _identity("document_id", self.document_id)
        content_reference = _identity(
            "content_reference",
            self.content_reference,
        )
        content_fingerprint = _sha3(
            "content_fingerprint",
            self.content_fingerprint,
        )
        content_evidence_fingerprint = _sha3(
            "content_evidence_fingerprint",
            self.content_evidence_fingerprint,
        )
        storage_bytes = _positive_int(
            "storage_bytes_added",
            self.storage_bytes_added,
        )
        ingress_bytes = _positive_int(
            "monthly_ingress_bytes",
            self.monthly_ingress_bytes,
        )
        versions = _positive_int(
            "document_versions_added",
            self.document_versions_added,
        )
        occurred_at = _when(self.occurred_at)

        if (
            self.schema != SCHEMA
            or self.observation_version != VERSION
        ):
            raise LegalEvidenceUsageObservationError(
                "L10A2Q_P3A_IDENTITY_INVALID"
            )

        if versions != 1:
            raise LegalEvidenceUsageObservationError(
                "L10A2Q_P3A_DOCUMENT_VERSIONS_INVALID"
            )

        if storage_bytes != ingress_bytes:
            raise LegalEvidenceUsageObservationError(
                "L10A2Q_P3A_USAGE_DIMENSIONS_DIVERGENT"
            )

        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "usage_observation_id", usage_id)
        object.__setattr__(self, "case_matter_id", matter)
        object.__setattr__(self, "document_id", document)
        object.__setattr__(
            self,
            "content_reference",
            content_reference,
        )
        object.__setattr__(
            self,
            "content_fingerprint",
            content_fingerprint,
        )
        object.__setattr__(
            self,
            "content_evidence_fingerprint",
            content_evidence_fingerprint,
        )
        object.__setattr__(
            self,
            "storage_bytes_added",
            storage_bytes,
        )
        object.__setattr__(
            self,
            "monthly_ingress_bytes",
            ingress_bytes,
        )
        object.__setattr__(
            self,
            "document_versions_added",
            versions,
        )
        object.__setattr__(self, "occurred_at", occurred_at)

        payload = {
            key: _json_value(getattr(self, key))
            for key in _FIELDS[:-1]
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

        if self.fingerprint:
            supplied = _sha3("fingerprint", self.fingerprint)
            if not hmac.compare_digest(supplied, digest):
                raise LegalEvidenceUsageObservationError(
                    "L10A2Q_P3A_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize all and only authority-bearing observation fields."""
        return {
            key: _json_value(getattr(self, key))
            for key in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalEvidenceUsageObservation":
        """Strictly hydrate persisted observation evidence."""
        if (
            not isinstance(payload, Mapping)
            or set(payload) != set(_FIELDS)
        ):
            raise LegalEvidenceUsageObservationError(
                "L10A2Q_P3A_SCHEMA_INVALID"
            )

        values = dict(payload)
        stored_fingerprint = values.pop("fingerprint")

        occurred_at = values.get("occurred_at")
        if isinstance(occurred_at, str):
            try:
                values["occurred_at"] = datetime.fromisoformat(
                    occurred_at.replace("Z", "+00:00")
                )
            except ValueError as error:
                raise LegalEvidenceUsageObservationError(
                    "L10A2Q_P3A_OCCURRED_AT_INVALID"
                ) from error

        observation = cls(
            **cast(Any, values),
            fingerprint=cast(Any, stored_fingerprint),
        )

        return observation


def observe_legal_evidence_usage(
    *,
    content: LegalEvidenceContent,
) -> LegalEvidenceUsageObservation:
    """Derive one usage fact from one exact canonical content value."""
    if type(content) is not LegalEvidenceContent:
        raise LegalEvidenceUsageObservationError(
            "L10A2Q_P3A_CONTENT_REQUIRED"
        )

    return LegalEvidenceUsageObservation(
        tenant_id=content.tenant_id,
        usage_observation_id=_observation_identity(content),
        case_matter_id=content.case_matter_id,
        document_id=content.document_id,
        content_reference=content.content_reference,
        content_fingerprint=content.content_fingerprint,
        content_evidence_fingerprint=content.fingerprint,
        storage_bytes_added=content.content_length,
        monthly_ingress_bytes=content.content_length,
        document_versions_added=1,
        occurred_at=content.registered_at,
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalEvidenceUsageObservation",
    "LegalEvidenceUsageObservationError",
    "observe_legal_evidence_usage",
]


# ARTIFACT: legal_evidence_usage_observation.py
# VERSION: v1.0.0-L10A2Q-P3A-LEGAL-EVIDENCE-USAGE-OBSERVATION
# AUTHORITY BOUNDARY: immutable observed Legal Evidence consumption only
# TENANT POSTURE: coordinates derive only from canonical LegalEvidenceContent
# FAIL-CLOSED POSTURE: malformed/corrupt/noncanonical usage evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
