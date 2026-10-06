"""WILSY OS CRM Core entitlement domain.

TITLE: CRM Core Entitlement Domain
VERSION: v1.0.0-CRM-CORE-ENTITLEMENT
AUTHORITY: Wilsy OS Core Governance
EPITOME:
    Own immutable, tenant-scoped entitlement evidence for the exact
    ``crm.core`` feature, bound to already-derived canonical subscription
    commercial provenance.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/crm/domain/crm_core_entitlement.py
COLLABORATION / OWNERSHIP:
    Subscription/Plan domains remain sovereign commercial truth.
    This domain owns CRM Core entitlement evidence only.
    Tenant authorization and business roles remain separate conjuncts.
    Kennel EOS remains exclusive financial execution authority.
CERTIFICATION / UPDATE DATE:
    2026-10-06
CHANGELOG:
    v1.0.0 establishes strict immutable entitlement evidence, exact crm.core
    feature binding, revisioned lifecycle transitions, chronology validation,
    strict hydration, and deterministic SHA3-512 identity.
SECURITY / PRIVACY POSTURE:
    No credentials, secrets, payment execution, settlement, AI authority,
    quota authority, IAM assignment, or principal authentication.
TENANT BOUNDARY:
    Every entitlement is exact-tenant and global/root pseudo-tenants reject.
AUTHORITY BOUNDARY:
    Entitlement evidence only. Plan labels, tiers, browser flags, roles,
    permissions, quotas and subscription presence do not themselves grant
    executable CRM authority.
FINANCIAL AUTHORITY BOUNDARY:
    Kennel EOS exclusively owns financial execution and settlement.
FAIL-CLOSED DECLARATION:
    Unknown fields, malformed source provenance, lifecycle drift, stale
    revisions, illegal transitions, chronology violations and fingerprint
    drift reject.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import hmac
import json
import unicodedata
from typing import Any, Final, cast


CRM_CORE_ENTITLEMENT_VERSION: Final[str] = (
    "v1.0.0-CRM-CORE-ENTITLEMENT"
)
CRM_CORE_ENTITLEMENT_SCHEMA: Final[str] = (
    "WILSY-CRM-CORE-ENTITLEMENT/V1"
)
CRM_CORE_FEATURE_ID: Final[str] = "crm.core"

_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "entitlement_version",
    "lifecycle_revision",
    "tenant_id",
    "entitlement_id",
    "feature_id",
    "subscription_id",
    "plan_id",
    "plan_catalogue_version",
    "subscription_proof_hash",
    "lifecycle_state",
    "activated_at",
    "activation_evidence_reference",
    "activation_evidence_fingerprint",
    "suspended_at",
    "suspension_evidence_reference",
    "suspension_evidence_fingerprint",
    "revoked_at",
    "revocation_evidence_reference",
    "revocation_evidence_fingerprint",
    "fingerprint",
)

CRM_CORE_ENTITLEMENT_FIELDS: Final[tuple[str, ...]] = _FIELDS

_HEX_DIGITS: Final[frozenset[str]] = frozenset(
    "0123456789abcdef"
)
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "root",
        "*",
        "master",
        "global_root",
        "sovereign_root",
        "wilsy-sovereign-root",
    }
)


class CrmCoreEntitlementError(ValueError):
    """Raised when CRM Core entitlement evidence fails closed."""


class CrmCoreEntitlementState(str, Enum):
    """Closed CRM Core entitlement lifecycle."""

    PENDING_SOURCE = "PENDING_SOURCE"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"


def _exact_text(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise CrmCoreEntitlementError(
            f"CRM_CORE_ENTITLEMENT_{name.upper()}_INVALID"
        )

    normalized = unicodedata.normalize("NFC", value)

    if (
        not normalized
        or normalized != value
        or any(ord(char) < 32 for char in normalized)
    ):
        raise CrmCoreEntitlementError(
            f"CRM_CORE_ENTITLEMENT_{name.upper()}_INVALID"
        )

    return normalized


def _tenant(value: object) -> str:
    tenant = _exact_text("tenant_id", value)

    if tenant.lower() in _FORBIDDEN_TENANTS:
        raise CrmCoreEntitlementError(
            "CRM_CORE_ENTITLEMENT_TENANT_ID_INVALID"
        )

    return tenant


def _digest(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 128
        or not value
        or any(char not in _HEX_DIGITS for char in value)
    ):
        raise CrmCoreEntitlementError(
            f"CRM_CORE_ENTITLEMENT_{name.upper()}_INVALID"
        )

    return value


def _catalogue_version(value: object) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
    ):
        raise CrmCoreEntitlementError(
            "CRM_CORE_ENTITLEMENT_PLAN_CATALOGUE_VERSION_INVALID"
        )

    return value


def _revision(value: object) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
    ):
        raise CrmCoreEntitlementError(
            "CRM_CORE_ENTITLEMENT_LIFECYCLE_REVISION_INVALID"
        )

    return value


def _when(
    name: str,
    value: object,
) -> datetime | None:
    if value is None:
        return None

    candidate = value

    if isinstance(candidate, str):
        try:
            candidate = datetime.fromisoformat(
                candidate.replace("Z", "+00:00")
            )
        except ValueError as error:
            raise CrmCoreEntitlementError(
                f"CRM_CORE_ENTITLEMENT_{name.upper()}_INVALID"
            ) from error

    if (
        not isinstance(candidate, datetime)
        or candidate.tzinfo is None
        or candidate.utcoffset() is None
    ):
        raise CrmCoreEntitlementError(
            f"CRM_CORE_ENTITLEMENT_{name.upper()}_INVALID"
        )

    return candidate.astimezone(timezone.utc)


def _evidence_pair(
    reference_name: str,
    reference: object,
    fingerprint_name: str,
    fingerprint: object,
) -> tuple[str | None, str | None]:
    if reference is None and fingerprint is None:
        return None, None

    if reference is None or fingerprint is None:
        raise CrmCoreEntitlementError(
            "CRM_CORE_ENTITLEMENT_EVIDENCE_PAIR_INVALID"
        )

    return (
        _exact_text(reference_name, reference),
        _digest(fingerprint_name, fingerprint),
    )


def _json_value(value: object) -> object:
    if isinstance(value, datetime):
        return (
            value.astimezone(timezone.utc)
            .isoformat()
            .replace("+00:00", "Z")
        )

    if isinstance(value, Enum):
        return value.value

    return value


@dataclass(frozen=True, slots=True)
class CrmCoreEntitlement:
    """Immutable exact-tenant CRM Core entitlement evidence."""

    tenant_id: str
    entitlement_id: str
    feature_id: str
    subscription_id: str
    plan_id: str
    plan_catalogue_version: int
    subscription_proof_hash: str
    lifecycle_state: CrmCoreEntitlementState | str

    activated_at: datetime | None = None
    activation_evidence_reference: str | None = None
    activation_evidence_fingerprint: str | None = None

    suspended_at: datetime | None = None
    suspension_evidence_reference: str | None = None
    suspension_evidence_fingerprint: str | None = None

    revoked_at: datetime | None = None
    revocation_evidence_reference: str | None = None
    revocation_evidence_fingerprint: str | None = None

    schema: str = CRM_CORE_ENTITLEMENT_SCHEMA
    entitlement_version: str = CRM_CORE_ENTITLEMENT_VERSION
    lifecycle_revision: int = 0
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if (
            self.schema != CRM_CORE_ENTITLEMENT_SCHEMA
            or self.entitlement_version
            != CRM_CORE_ENTITLEMENT_VERSION
        ):
            raise CrmCoreEntitlementError(
                "CRM_CORE_ENTITLEMENT_IDENTITY_INVALID"
            )

        tenant = _tenant(self.tenant_id)
        entitlement_id = _exact_text(
            "entitlement_id",
            self.entitlement_id,
        )

        if self.feature_id != CRM_CORE_FEATURE_ID:
            raise CrmCoreEntitlementError(
                "CRM_CORE_ENTITLEMENT_FEATURE_ID_INVALID"
            )

        subscription_id = _exact_text(
            "subscription_id",
            self.subscription_id,
        )
        plan_id = _exact_text(
            "plan_id",
            self.plan_id,
        )
        catalogue_version = _catalogue_version(
            self.plan_catalogue_version
        )
        subscription_proof = _digest(
            "subscription_proof_hash",
            self.subscription_proof_hash,
        )
        revision = _revision(
            self.lifecycle_revision
        )

        try:
            state = CrmCoreEntitlementState(
                self.lifecycle_state
            )
        except (TypeError, ValueError) as error:
            raise CrmCoreEntitlementError(
                "CRM_CORE_ENTITLEMENT_STATE_INVALID"
            ) from error

        activated = _when(
            "activated_at",
            self.activated_at,
        )
        activation_ref, activation_fp = _evidence_pair(
            "activation_evidence_reference",
            self.activation_evidence_reference,
            "activation_evidence_fingerprint",
            self.activation_evidence_fingerprint,
        )

        suspended = _when(
            "suspended_at",
            self.suspended_at,
        )
        suspension_ref, suspension_fp = _evidence_pair(
            "suspension_evidence_reference",
            self.suspension_evidence_reference,
            "suspension_evidence_fingerprint",
            self.suspension_evidence_fingerprint,
        )

        revoked = _when(
            "revoked_at",
            self.revoked_at,
        )
        revocation_ref, revocation_fp = _evidence_pair(
            "revocation_evidence_reference",
            self.revocation_evidence_reference,
            "revocation_evidence_fingerprint",
            self.revocation_evidence_fingerprint,
        )

        activation_complete = (
            activated is not None
            and activation_ref is not None
            and activation_fp is not None
        )
        suspension_complete = (
            suspended is not None
            and suspension_ref is not None
            and suspension_fp is not None
        )
        revocation_complete = (
            revoked is not None
            and revocation_ref is not None
            and revocation_fp is not None
        )

        if state is CrmCoreEntitlementState.PENDING_SOURCE:
            if any(
                value is not None
                for value in (
                    activated,
                    activation_ref,
                    activation_fp,
                    suspended,
                    suspension_ref,
                    suspension_fp,
                    revoked,
                    revocation_ref,
                    revocation_fp,
                )
            ):
                raise CrmCoreEntitlementError(
                    "CRM_CORE_ENTITLEMENT_PENDING_SHAPE_INVALID"
                )

        elif state is CrmCoreEntitlementState.ACTIVE:
            if (
                not activation_complete
                or suspension_complete
                or revocation_complete
                or any(
                    value is not None
                    for value in (
                        suspended,
                        suspension_ref,
                        suspension_fp,
                        revoked,
                        revocation_ref,
                        revocation_fp,
                    )
                )
            ):
                raise CrmCoreEntitlementError(
                    "CRM_CORE_ENTITLEMENT_ACTIVE_SHAPE_INVALID"
                )

        elif state is CrmCoreEntitlementState.SUSPENDED:
            if (
                not activation_complete
                or not suspension_complete
                or any(
                    value is not None
                    for value in (
                        revoked,
                        revocation_ref,
                        revocation_fp,
                    )
                )
            ):
                raise CrmCoreEntitlementError(
                    "CRM_CORE_ENTITLEMENT_SUSPENDED_SHAPE_INVALID"
                )

        elif state is CrmCoreEntitlementState.REVOKED:
            if (
                not activation_complete
                or not revocation_complete
                or any(
                    value is not None
                    for value in (
                        suspended,
                        suspension_ref,
                        suspension_fp,
                    )
                )
            ):
                raise CrmCoreEntitlementError(
                    "CRM_CORE_ENTITLEMENT_REVOKED_SHAPE_INVALID"
                )

        if (
            activated is not None
            and suspended is not None
            and suspended < activated
        ):
            raise CrmCoreEntitlementError(
                "CRM_CORE_ENTITLEMENT_CHRONOLOGY_INVALID"
            )

        if (
            activated is not None
            and revoked is not None
            and revoked < activated
        ):
            raise CrmCoreEntitlementError(
                "CRM_CORE_ENTITLEMENT_CHRONOLOGY_INVALID"
            )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "entitlement_id",
            entitlement_id,
        )
        object.__setattr__(
            self,
            "feature_id",
            CRM_CORE_FEATURE_ID,
        )
        object.__setattr__(
            self,
            "subscription_id",
            subscription_id,
        )
        object.__setattr__(
            self,
            "plan_id",
            plan_id,
        )
        object.__setattr__(
            self,
            "plan_catalogue_version",
            catalogue_version,
        )
        object.__setattr__(
            self,
            "subscription_proof_hash",
            subscription_proof,
        )
        object.__setattr__(
            self,
            "lifecycle_state",
            state,
        )
        object.__setattr__(
            self,
            "lifecycle_revision",
            revision,
        )

        normalized = {
            "activated_at": activated,
            "activation_evidence_reference": activation_ref,
            "activation_evidence_fingerprint": activation_fp,
            "suspended_at": suspended,
            "suspension_evidence_reference": suspension_ref,
            "suspension_evidence_fingerprint": suspension_fp,
            "revoked_at": revoked,
            "revocation_evidence_reference": revocation_ref,
            "revocation_evidence_fingerprint": revocation_fp,
        }

        for field_name, value in normalized.items():
            object.__setattr__(
                self,
                field_name,
                value,
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
            stored = _digest(
                "fingerprint",
                self.fingerprint,
            )

            if not hmac.compare_digest(
                stored,
                digest,
            ):
                raise CrmCoreEntitlementError(
                    "CRM_CORE_ENTITLEMENT_FINGERPRINT_MISMATCH"
                )

        object.__setattr__(
            self,
            "fingerprint",
            digest,
        )

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact closed entitlement evidence document."""

        return {
            field: _json_value(
                getattr(self, field)
            )
            for field in _FIELDS
        }

    def transition(
        self,
        target_state: CrmCoreEntitlementState | str,
        *,
        expected_revision: int,
        evidence_reference: str,
        evidence_fingerprint: str,
        occurred_at: datetime,
    ) -> "CrmCoreEntitlement":
        """Return one legal revisioned lifecycle transition."""

        if (
            isinstance(expected_revision, bool)
            or not isinstance(expected_revision, int)
            or expected_revision != self.lifecycle_revision
        ):
            raise CrmCoreEntitlementError(
                "CRM_CORE_ENTITLEMENT_STALE_REVISION"
            )

        try:
            target = CrmCoreEntitlementState(
                target_state
            )
        except (TypeError, ValueError) as error:
            raise CrmCoreEntitlementError(
                "CRM_CORE_ENTITLEMENT_TRANSITION_INVALID"
            ) from error

        current = cast(
            CrmCoreEntitlementState,
            self.lifecycle_state,
        )

        legal: dict[
            CrmCoreEntitlementState,
            frozenset[CrmCoreEntitlementState],
        ] = {
            CrmCoreEntitlementState.PENDING_SOURCE: frozenset(
                {
                    CrmCoreEntitlementState.ACTIVE,
                }
            ),
            CrmCoreEntitlementState.ACTIVE: frozenset(
                {
                    CrmCoreEntitlementState.SUSPENDED,
                    CrmCoreEntitlementState.REVOKED,
                }
            ),
            CrmCoreEntitlementState.SUSPENDED: frozenset(),
            CrmCoreEntitlementState.REVOKED: frozenset(),
        }

        if target not in legal[current]:
            raise CrmCoreEntitlementError(
                "CRM_CORE_ENTITLEMENT_ILLEGAL_TRANSITION"
            )

        reference = _exact_text(
            "evidence_reference",
            evidence_reference,
        )
        evidence_digest = _digest(
            "evidence_fingerprint",
            evidence_fingerprint,
        )
        when = _when(
            "occurred_at",
            occurred_at,
        )

        if when is None:
            raise CrmCoreEntitlementError(
                "CRM_CORE_ENTITLEMENT_OCCURRED_AT_INVALID"
            )

        if (
            self.activated_at is not None
            and when < self.activated_at
        ):
            raise CrmCoreEntitlementError(
                "CRM_CORE_ENTITLEMENT_CHRONOLOGY_INVALID"
            )

        values: dict[str, object] = {
            field: getattr(self, field)
            for field in _FIELDS[:-1]
        }

        values.update(
            {
                "lifecycle_state": target,
                "lifecycle_revision": (
                    self.lifecycle_revision + 1
                ),
            }
        )

        if target is CrmCoreEntitlementState.ACTIVE:
            values.update(
                {
                    "activated_at": when,
                    "activation_evidence_reference": reference,
                    "activation_evidence_fingerprint": evidence_digest,
                }
            )

        elif target is CrmCoreEntitlementState.SUSPENDED:
            values.update(
                {
                    "suspended_at": when,
                    "suspension_evidence_reference": reference,
                    "suspension_evidence_fingerprint": evidence_digest,
                }
            )

        elif target is CrmCoreEntitlementState.REVOKED:
            values.update(
                {
                    "revoked_at": when,
                    "revocation_evidence_reference": reference,
                    "revocation_evidence_fingerprint": evidence_digest,
                }
            )

        return CrmCoreEntitlement(
            **cast(Any, values)
        )

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "CrmCoreEntitlement":
        """Hydrate exactly one strict durable entitlement document."""

        if (
            not isinstance(payload, Mapping)
            or set(payload) != set(_FIELDS)
        ):
            raise CrmCoreEntitlementError(
                "CRM_CORE_ENTITLEMENT_SCHEMA_INVALID"
            )

        values = dict(payload)
        stored = values.pop("fingerprint")

        item = cls(
            **cast(Any, values)
        )

        if (
            not isinstance(stored, str)
            or not hmac.compare_digest(
                stored,
                item.fingerprint,
            )
        ):
            raise CrmCoreEntitlementError(
                "CRM_CORE_ENTITLEMENT_FINGERPRINT_MISMATCH"
            )

        return item


__all__ = [
    "CRM_CORE_ENTITLEMENT_FIELDS",
    "CRM_CORE_ENTITLEMENT_SCHEMA",
    "CRM_CORE_ENTITLEMENT_VERSION",
    "CRM_CORE_FEATURE_ID",
    "CrmCoreEntitlement",
    "CrmCoreEntitlementError",
    "CrmCoreEntitlementState",
]

# ARTIFACT: crm_core_entitlement.py
# VERSION: v1.0.0-CRM-CORE-ENTITLEMENT
# AUTHORITY BOUNDARY: immutable exact-tenant crm.core entitlement evidence only
# COMMERCIAL POSTURE: subscription/plan/proof provenance is evidence, not execution
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
