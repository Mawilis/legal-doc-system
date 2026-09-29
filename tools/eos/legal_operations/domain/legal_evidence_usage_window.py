"""WILSY OS immutable complete Legal Evidence usage-window evidence.

TITLE: Legal Evidence Usage Window
VERSION: v1.0.0-L10A2Q-P3C-A-LEGAL-EVIDENCE-USAGE-WINDOW
AUTHORITY: WILSY OS Core Governance
PURPOSE:
    Represent one immutable tenant/document usage snapshot proving the complete
    aggregate P3 usage facts required by P4 without granting remaining-capacity,
    reservation, admission or financial authority.

EPITOME:
    USAGE OBSERVATIONS DURABLE
    -> COMPLETE USAGE WINDOW EVIDENCE
    != REMAINING CAPACITY
    != CAPACITY RESERVED
    != STORAGE ADMISSION

METRIC SCOPE:
    tenant_storage_bytes_added is tenant-wide cumulative through as_of.
    monthly_ingress_bytes_added is tenant-wide for the UTC calendar month
    through as_of.
    document_versions_added is cumulative for exactly one document through as_of.

COMPLETENESS POSTURE:
    This value does not discover observations itself. A certified P3C-B registry
    retrieval seam must construct it from one complete caller-owned snapshot
    transaction. Legitimate emptiness is representable only when that retrieval
    seam proves completeness.

CERTIFICATION / UPDATE DATE: 2026-09-30

TENANT BOUNDARY:
    One exact tenant and one exact document identity bind every aggregate.

AUTHORITY BOUNDARY:
    Complete aggregated usage evidence only. No capacity derivation, quota
    mutation, reservation, admission, billing, payment, settlement, execution,
    retention or deletion authority.

FAIL-CLOSED DECLARATION:
    Malformed identity/time/counts/counters, invalid monthly boundaries, invalid
    source-observation-set fingerprint, schema drift or fingerprint drift reject.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
import re
from typing import Any, Final, cast


VERSION: Final[str] = (
    "v1.0.0-L10A2Q-P3C-A-LEGAL-EVIDENCE-USAGE-WINDOW"
)
SCHEMA: Final[str] = "WILSY-LEGAL-EVIDENCE-USAGE-WINDOW/V1"

_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id",
    "document_id",
    "as_of",
    "monthly_window_start",
    "monthly_window_end",
    "tenant_observation_count",
    "monthly_observation_count",
    "document_observation_count",
    "tenant_storage_bytes_added",
    "monthly_ingress_bytes_added",
    "document_versions_added",
    "source_observation_set_fingerprint",
    "schema",
    "window_version",
    "fingerprint",
)

_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,511}$"
)
_SHA3_RE: Final[re.Pattern[str]] = re.compile(r"^[0-9a-f]{128}$")

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "root",
        "*",
        "global_root",
    }
)


class LegalEvidenceUsageWindowError(ValueError):
    """Raised when complete Legal Evidence usage-window evidence is invalid."""


def _identity(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceUsageWindowError(
            f"L10A2Q_P3C_A_{name.upper()}_INVALID"
        )
    return value


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.lower() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceUsageWindowError(
            "L10A2Q_P3C_A_TENANT_REQUIRED"
        )
    return tenant


def _aware(
    name: str,
    value: object,
) -> datetime:
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(
                value.replace("Z", "+00:00")
            )
        except ValueError as error:
            raise LegalEvidenceUsageWindowError(
                f"L10A2Q_P3C_A_{name.upper()}_INVALID"
            ) from error

    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceUsageWindowError(
            f"L10A2Q_P3C_A_{name.upper()}_INVALID"
        )

    return value.astimezone(timezone.utc)


def _nonnegative(
    name: str,
    value: object,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
    ):
        raise LegalEvidenceUsageWindowError(
            f"L10A2Q_P3C_A_{name.upper()}_INVALID"
        )
    return value


def _source_fingerprint(value: object) -> str:
    if (
        not isinstance(value, str)
        or _SHA3_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceUsageWindowError(
            "L10A2Q_P3C_A_SOURCE_FINGERPRINT_INVALID"
        )
    return value


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return (
            value.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )
    return value


@dataclass(frozen=True, slots=True)
class LegalEvidenceUsageWindow:
    """Immutable complete aggregate usage evidence for one tenant/document."""

    tenant_id: str
    document_id: str

    as_of: datetime
    monthly_window_start: datetime
    monthly_window_end: datetime

    tenant_observation_count: int
    monthly_observation_count: int
    document_observation_count: int

    tenant_storage_bytes_added: int
    monthly_ingress_bytes_added: int
    document_versions_added: int

    source_observation_set_fingerprint: str

    schema: str = SCHEMA
    window_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        document = _identity(
            "document_id",
            self.document_id,
        )

        if (
            self.schema != SCHEMA
            or self.window_version != VERSION
        ):
            raise LegalEvidenceUsageWindowError(
                "L10A2Q_P3C_A_SCHEMA_INVALID"
            )

        as_of = _aware("as_of", self.as_of)
        month_start = _aware(
            "monthly_window_start",
            self.monthly_window_start,
        )
        month_end = _aware(
            "monthly_window_end",
            self.monthly_window_end,
        )

        expected_month_start = as_of.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        if (
            month_start != expected_month_start
            or month_end != as_of
            or month_start > month_end
        ):
            raise LegalEvidenceUsageWindowError(
                "L10A2Q_P3C_A_WINDOW_INVALID"
            )

        tenant_count = _nonnegative(
            "tenant_observation_count",
            self.tenant_observation_count,
        )
        monthly_count = _nonnegative(
            "monthly_observation_count",
            self.monthly_observation_count,
        )
        document_count = _nonnegative(
            "document_observation_count",
            self.document_observation_count,
        )

        if (
            monthly_count > tenant_count
            or document_count > tenant_count
        ):
            raise LegalEvidenceUsageWindowError(
                "L10A2Q_P3C_A_COUNT_INVALID"
            )

        tenant_storage = _nonnegative(
            "tenant_storage_bytes_added",
            self.tenant_storage_bytes_added,
        )
        monthly_ingress = _nonnegative(
            "monthly_ingress_bytes_added",
            self.monthly_ingress_bytes_added,
        )
        document_versions = _nonnegative(
            "document_versions_added",
            self.document_versions_added,
        )

        if (
            tenant_count == 0
            and (
                monthly_count != 0
                or document_count != 0
                or tenant_storage != 0
                or monthly_ingress != 0
                or document_versions != 0
            )
        ):
            raise LegalEvidenceUsageWindowError(
                "L10A2Q_P3C_A_COUNT_INVALID"
            )

        if (
            monthly_count == 0
            and monthly_ingress != 0
        ):
            raise LegalEvidenceUsageWindowError(
                "L10A2Q_P3C_A_COUNT_INVALID"
            )

        if (
            document_count == 0
            and document_versions != 0
        ):
            raise LegalEvidenceUsageWindowError(
                "L10A2Q_P3C_A_COUNT_INVALID"
            )

        source_fingerprint = _source_fingerprint(
            self.source_observation_set_fingerprint
        )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "document_id",
            document,
        )
        object.__setattr__(
            self,
            "as_of",
            as_of,
        )
        object.__setattr__(
            self,
            "monthly_window_start",
            month_start,
        )
        object.__setattr__(
            self,
            "monthly_window_end",
            month_end,
        )
        object.__setattr__(
            self,
            "tenant_observation_count",
            tenant_count,
        )
        object.__setattr__(
            self,
            "monthly_observation_count",
            monthly_count,
        )
        object.__setattr__(
            self,
            "document_observation_count",
            document_count,
        )
        object.__setattr__(
            self,
            "tenant_storage_bytes_added",
            tenant_storage,
        )
        object.__setattr__(
            self,
            "monthly_ingress_bytes_added",
            monthly_ingress,
        )
        object.__setattr__(
            self,
            "document_versions_added",
            document_versions,
        )
        object.__setattr__(
            self,
            "source_observation_set_fingerprint",
            source_fingerprint,
        )

        payload = {
            field: _json_value(
                getattr(self, field)
            )
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

        if self.fingerprint:
            if (
                not isinstance(self.fingerprint, str)
                or not hmac.compare_digest(
                    self.fingerprint,
                    digest,
                )
            ):
                raise LegalEvidenceUsageWindowError(
                    "L10A2Q_P3C_A_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize exact deterministic complete usage-window evidence."""
        return {
            field: _json_value(
                getattr(self, field)
            )
            for field in _FIELDS
        }

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "LegalEvidenceUsageWindow":
        """Strictly hydrate exact complete usage-window evidence."""
        if (
            not isinstance(payload, Mapping)
            or set(payload) != set(_FIELDS)
        ):
            raise LegalEvidenceUsageWindowError(
                "L10A2Q_P3C_A_SCHEMA_INVALID"
            )

        values = dict(payload)
        stored = values.pop("fingerprint")

        for field in (
            "as_of",
            "monthly_window_start",
            "monthly_window_end",
        ):
            value = values.get(field)
            if isinstance(value, str):
                values[field] = _aware(
                    field,
                    value,
                )

        item = cls(
            **cast(
                Any,
                values,
            )
        )

        if (
            not isinstance(stored, str)
            or not hmac.compare_digest(
                stored,
                item.fingerprint,
            )
        ):
            raise LegalEvidenceUsageWindowError(
                "L10A2Q_P3C_A_FINGERPRINT_MISMATCH"
            )

        return item


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalEvidenceUsageWindow",
    "LegalEvidenceUsageWindowError",
]


# ARTIFACT: legal_evidence_usage_window.py
# VERSION: v1.0.0-L10A2Q-P3C-A-LEGAL-EVIDENCE-USAGE-WINDOW
# AUTHORITY BOUNDARY: complete aggregated Legal Evidence usage only
# TENANT POSTURE: exact tenant/document binding
# CAPACITY POSTURE: no remaining-capacity, reservation or admission authority
# FAIL-CLOSED POSTURE: malformed/incomplete/fingerprint-drifted evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
