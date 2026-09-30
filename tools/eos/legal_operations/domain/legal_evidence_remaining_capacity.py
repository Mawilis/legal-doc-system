"""WILSY OS immutable Legal Evidence remaining-capacity evidence.

TITLE: Legal Evidence Remaining Capacity
VERSION: v1.0.0-L10A2Q-P4-LEGAL-EVIDENCE-REMAINING-CAPACITY
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Derive one immutable tenant/document remaining-capacity projection from
    exact P2 tenant-capacity-profile evidence, the exact canonical P1 capacity
    policy for that profile, and one complete P3C usage window evaluated at the
    same explicit instant.

EPITOME:
    P2 TENANT CAPACITY PROFILE
    + P1 CANONICAL CAPACITY POLICY
    + P3C COMPLETE USAGE WINDOW
    -> P4 REMAINING CAPACITY
    != CAPACITY RESERVED
    != STORAGE ADMITTED
    != IAM AUTHORIZED
    != BILLING / PAYMENT / SETTLEMENT

TIME BINDING:
    tenant_profile.evaluated_at MUST equal usage_window.as_of. P4 does not
    combine commercial-authority evidence and usage evidence from different
    evaluation instants.

ACCOUNTING:
    remaining_storage_bytes =
        max(0, tenant_storage_limit_bytes - tenant_storage_consumed_bytes)

    remaining_ingress_bytes =
        max(0, monthly_ingress_limit_bytes - monthly_ingress_consumed_bytes)

    remaining_document_versions =
        max(0, max_document_versions - document_versions_consumed)

    Exhaustion is true when observed consumption is greater than or equal to
    the corresponding limit.

AUTHORITY BOUNDARY:
    Pure immutable remaining-capacity evidence only. This artifact does not
    reserve capacity, admit storage, authorize a principal, mutate entitlement,
    select a provider, price usage, bill, execute payment, or settle funds.

CERTIFICATION / UPDATE DATE: 2026-09-30
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

from tools.eos.legal_operations.domain.legal_evidence_usage_window import (
    LegalEvidenceUsageWindow,
)
from tools.eos.saas.billing.legal_evidence_capacity_policy_contract import (
    LegalEvidenceCapacityPolicy,
)
from tools.eos.saas.billing.legal_evidence_capacity_tenant_profile_resolver import (
    LegalEvidenceCapacityTenantProfile,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2Q-P4-LEGAL-EVIDENCE-REMAINING-CAPACITY"
)
SCHEMA: Final[str] = "WILSY-LEGAL-EVIDENCE-REMAINING-CAPACITY/V1"

_FIELDS: Final[tuple[str, ...]] = (
    "tenant_id",
    "document_id",
    "evaluated_at",
    "tenant_profile_fingerprint",
    "capacity_policy_fingerprint",
    "usage_window_fingerprint",
    "tenant_storage_limit_bytes",
    "tenant_storage_consumed_bytes",
    "remaining_storage_bytes",
    "storage_exhausted",
    "monthly_ingress_limit_bytes",
    "monthly_ingress_consumed_bytes",
    "remaining_ingress_bytes",
    "ingress_exhausted",
    "max_document_versions",
    "document_versions_consumed",
    "remaining_document_versions",
    "versions_exhausted",
    "schema",
    "capacity_version",
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


class LegalEvidenceRemainingCapacityError(ValueError):
    """Raised when Legal Evidence remaining-capacity evidence is invalid."""


def _identity(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceRemainingCapacityError(
            f"L10A2Q_P4_{name.upper()}_INVALID"
        )
    return value


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.lower() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceRemainingCapacityError(
            "L10A2Q_P4_TENANT_REQUIRED"
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
            raise LegalEvidenceRemainingCapacityError(
                f"L10A2Q_P4_{name.upper()}_INVALID"
            ) from error

    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceRemainingCapacityError(
            f"L10A2Q_P4_{name.upper()}_INVALID"
        )

    return value.astimezone(timezone.utc)


def _sha3(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or _SHA3_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceRemainingCapacityError(
            f"L10A2Q_P4_{name.upper()}_INVALID"
        )
    return value


def _nonnegative(
    name: str,
    value: object,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
    ):
        raise LegalEvidenceRemainingCapacityError(
            f"L10A2Q_P4_{name.upper()}_INVALID"
        )
    return value


def _boolean(
    name: str,
    value: object,
) -> bool:
    if not isinstance(value, bool):
        raise LegalEvidenceRemainingCapacityError(
            f"L10A2Q_P4_{name.upper()}_INVALID"
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
class LegalEvidenceRemainingCapacity:
    """Immutable P4 remaining-capacity evidence for one tenant/document."""

    tenant_id: str
    document_id: str
    evaluated_at: datetime

    tenant_profile_fingerprint: str
    capacity_policy_fingerprint: str
    usage_window_fingerprint: str

    tenant_storage_limit_bytes: int
    tenant_storage_consumed_bytes: int
    remaining_storage_bytes: int
    storage_exhausted: bool

    monthly_ingress_limit_bytes: int
    monthly_ingress_consumed_bytes: int
    remaining_ingress_bytes: int
    ingress_exhausted: bool

    max_document_versions: int
    document_versions_consumed: int
    remaining_document_versions: int
    versions_exhausted: bool

    schema: str = SCHEMA
    capacity_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact derived-state invariants and bind SHA3-512 evidence."""
        tenant = _tenant(self.tenant_id)
        document = _identity(
            "document_id",
            self.document_id,
        )
        evaluated_at = _aware(
            "evaluated_at",
            self.evaluated_at,
        )

        if (
            self.schema != SCHEMA
            or self.capacity_version != VERSION
        ):
            raise LegalEvidenceRemainingCapacityError(
                "L10A2Q_P4_SCHEMA_INVALID"
            )

        tenant_profile_fingerprint = _sha3(
            "tenant_profile_fingerprint",
            self.tenant_profile_fingerprint,
        )
        capacity_policy_fingerprint = _sha3(
            "capacity_policy_fingerprint",
            self.capacity_policy_fingerprint,
        )
        usage_window_fingerprint = _sha3(
            "usage_window_fingerprint",
            self.usage_window_fingerprint,
        )

        storage_limit = _nonnegative(
            "tenant_storage_limit_bytes",
            self.tenant_storage_limit_bytes,
        )
        storage_consumed = _nonnegative(
            "tenant_storage_consumed_bytes",
            self.tenant_storage_consumed_bytes,
        )
        storage_remaining = _nonnegative(
            "remaining_storage_bytes",
            self.remaining_storage_bytes,
        )
        storage_exhausted = _boolean(
            "storage_exhausted",
            self.storage_exhausted,
        )

        ingress_limit = _nonnegative(
            "monthly_ingress_limit_bytes",
            self.monthly_ingress_limit_bytes,
        )
        ingress_consumed = _nonnegative(
            "monthly_ingress_consumed_bytes",
            self.monthly_ingress_consumed_bytes,
        )
        ingress_remaining = _nonnegative(
            "remaining_ingress_bytes",
            self.remaining_ingress_bytes,
        )
        ingress_exhausted = _boolean(
            "ingress_exhausted",
            self.ingress_exhausted,
        )

        versions_limit = _nonnegative(
            "max_document_versions",
            self.max_document_versions,
        )
        versions_consumed = _nonnegative(
            "document_versions_consumed",
            self.document_versions_consumed,
        )
        versions_remaining = _nonnegative(
            "remaining_document_versions",
            self.remaining_document_versions,
        )
        versions_exhausted = _boolean(
            "versions_exhausted",
            self.versions_exhausted,
        )

        expected_storage_remaining = max(
            0,
            storage_limit - storage_consumed,
        )
        expected_ingress_remaining = max(
            0,
            ingress_limit - ingress_consumed,
        )
        expected_versions_remaining = max(
            0,
            versions_limit - versions_consumed,
        )

        expected_storage_exhausted = (
            storage_consumed >= storage_limit
        )
        expected_ingress_exhausted = (
            ingress_consumed >= ingress_limit
        )
        expected_versions_exhausted = (
            versions_consumed >= versions_limit
        )

        if (
            storage_remaining != expected_storage_remaining
            or storage_exhausted != expected_storage_exhausted
        ):
            raise LegalEvidenceRemainingCapacityError(
                "L10A2Q_P4_STORAGE_DERIVATION_INVALID"
            )

        if (
            ingress_remaining != expected_ingress_remaining
            or ingress_exhausted != expected_ingress_exhausted
        ):
            raise LegalEvidenceRemainingCapacityError(
                "L10A2Q_P4_INGRESS_DERIVATION_INVALID"
            )

        if (
            versions_remaining != expected_versions_remaining
            or versions_exhausted != expected_versions_exhausted
        ):
            raise LegalEvidenceRemainingCapacityError(
                "L10A2Q_P4_VERSIONS_DERIVATION_INVALID"
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
            "evaluated_at",
            evaluated_at,
        )
        object.__setattr__(
            self,
            "tenant_profile_fingerprint",
            tenant_profile_fingerprint,
        )
        object.__setattr__(
            self,
            "capacity_policy_fingerprint",
            capacity_policy_fingerprint,
        )
        object.__setattr__(
            self,
            "usage_window_fingerprint",
            usage_window_fingerprint,
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
                raise LegalEvidenceRemainingCapacityError(
                    "L10A2Q_P4_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize exact deterministic P4 remaining-capacity evidence."""
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
    ) -> "LegalEvidenceRemainingCapacity":
        """Strictly hydrate exact remaining-capacity evidence."""
        if (
            not isinstance(payload, Mapping)
            or set(payload) != set(_FIELDS)
        ):
            raise LegalEvidenceRemainingCapacityError(
                "L10A2Q_P4_SCHEMA_INVALID"
            )

        values = dict(payload)
        stored = values.pop("fingerprint")

        evaluated_at = values.get("evaluated_at")
        if isinstance(evaluated_at, str):
            values["evaluated_at"] = _aware(
                "evaluated_at",
                evaluated_at,
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
            raise LegalEvidenceRemainingCapacityError(
                "L10A2Q_P4_FINGERPRINT_MISMATCH"
            )

        return item


def derive_legal_evidence_remaining_capacity(
    *,
    tenant_profile: LegalEvidenceCapacityTenantProfile,
    policy: LegalEvidenceCapacityPolicy,
    usage_window: LegalEvidenceUsageWindow,
) -> LegalEvidenceRemainingCapacity:
    """Derive immutable P4 evidence from exact P1/P2/P3C authority inputs."""
    if type(tenant_profile) is not LegalEvidenceCapacityTenantProfile:
        raise LegalEvidenceRemainingCapacityError(
            "L10A2Q_P4_TENANT_PROFILE_REQUIRED"
        )

    if type(policy) is not LegalEvidenceCapacityPolicy:
        raise LegalEvidenceRemainingCapacityError(
            "L10A2Q_P4_POLICY_REQUIRED"
        )

    if type(usage_window) is not LegalEvidenceUsageWindow:
        raise LegalEvidenceRemainingCapacityError(
            "L10A2Q_P4_USAGE_WINDOW_REQUIRED"
        )

    if tenant_profile.tenant_id != usage_window.tenant_id:
        raise LegalEvidenceRemainingCapacityError(
            "L10A2Q_P4_TENANT_MISMATCH"
        )

    if tenant_profile.profile != policy.profile:
        raise LegalEvidenceRemainingCapacityError(
            "L10A2Q_P4_POLICY_PROFILE_MISMATCH"
        )

    profile_at = tenant_profile.evaluated_at.astimezone(
        timezone.utc
    )
    usage_at = usage_window.as_of.astimezone(
        timezone.utc
    )

    if profile_at != usage_at:
        raise LegalEvidenceRemainingCapacityError(
            "L10A2Q_P4_EVALUATION_TIME_MISMATCH"
        )

    storage_limit = policy.tenant_storage_limit_bytes
    storage_consumed = usage_window.tenant_storage_bytes_added

    ingress_limit = policy.monthly_ingress_limit_bytes
    ingress_consumed = usage_window.monthly_ingress_bytes_added

    versions_limit = policy.max_document_versions
    versions_consumed = usage_window.document_versions_added

    return LegalEvidenceRemainingCapacity(
        tenant_id=tenant_profile.tenant_id,
        document_id=usage_window.document_id,
        evaluated_at=profile_at,
        tenant_profile_fingerprint=tenant_profile.fingerprint,
        capacity_policy_fingerprint=policy.fingerprint,
        usage_window_fingerprint=usage_window.fingerprint,
        tenant_storage_limit_bytes=storage_limit,
        tenant_storage_consumed_bytes=storage_consumed,
        remaining_storage_bytes=max(
            0,
            storage_limit - storage_consumed,
        ),
        storage_exhausted=(
            storage_consumed >= storage_limit
        ),
        monthly_ingress_limit_bytes=ingress_limit,
        monthly_ingress_consumed_bytes=ingress_consumed,
        remaining_ingress_bytes=max(
            0,
            ingress_limit - ingress_consumed,
        ),
        ingress_exhausted=(
            ingress_consumed >= ingress_limit
        ),
        max_document_versions=versions_limit,
        document_versions_consumed=versions_consumed,
        remaining_document_versions=max(
            0,
            versions_limit - versions_consumed,
        ),
        versions_exhausted=(
            versions_consumed >= versions_limit
        ),
    )


__all__ = [
    "SCHEMA",
    "VERSION",
    "LegalEvidenceRemainingCapacity",
    "LegalEvidenceRemainingCapacityError",
    "derive_legal_evidence_remaining_capacity",
]


# ARTIFACT: legal_evidence_remaining_capacity.py
# VERSION: v1.0.0-L10A2Q-P4-LEGAL-EVIDENCE-REMAINING-CAPACITY
# AUTHORITY BOUNDARY: immutable remaining-capacity evidence only
# TENANT POSTURE: exact P2/P3C tenant binding
# TIME POSTURE: P2 evaluated_at equals P3C as_of
# RESERVATION POSTURE: no reservation, concurrency or admission authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
