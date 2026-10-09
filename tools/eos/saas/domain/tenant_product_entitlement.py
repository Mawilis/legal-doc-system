"""WILSY OS canonical tenant product entitlement domain.

TITLE: Tenant Product Entitlement Domain
VERSION: v1.0.0-D22B1-TENANT-PRODUCT-ENTITLEMENT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Own immutable tenant/product entitlement lifecycle evidence bound to
         the canonical D22A product catalogue without granting IAM, VAS,
         subscription-payment or financial-execution authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/tenant_product_entitlement.py
COLLABORATION / OWNERSHIP: D22A owns product identity/catalogue truth; this
                            domain owns tenant/product entitlement lifecycle
                            facts; D22B2 will own persistence. PlanRegistry and
                            SubscriptionRegistry retain base commercial truth.
                            WILSY AI and Tenant Branding remain separate VAS
                            authorities; IAM remains principal authority.
CERTIFICATION / UPDATE DATE: 2026-09-24
CHANGELOG: v1.0.0-D22B1-TENANT-PRODUCT-ENTITLEMENT establishes immutable
           tenant-scoped entitlement evidence for Legal Operations, Billing,
           CRM and HR, exact binding to the D22A catalogue fingerprint,
           source-evidence requirements, revisioned lifecycle transitions and
           deterministic SHA3-512 integrity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No credentials, network, MongoDB, KMS, provider
                             clients or browser state. Evidence references are
                             opaque and raw commercial/order payloads are not
                             embedded.
TENANT BOUNDARY: Every entitlement is bound to one explicit tenant_id and one
                 exact catalogue product. Pseudo-tenants fail closed.
AUTHORITY BOUNDARY: Tenant/product entitlement lifecycle evidence only. An
                    ACTIVE entitlement proves product availability to the
                    tenant, not user role, permission, route admission or any
                    WILSY AI / branding entitlement.
FINANCIAL AUTHORITY BOUNDARY: No price, invoice, charge, payment, execution or
                               settlement truth. Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Unknown products, pseudo-tenants, catalogue drift,
                         malformed source/lifecycle evidence, stale revisions,
                         illegal transitions and fingerprint drift reject.
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

from tools.eos.saas.entitlement.product_catalogue import (
    TenantProductId,
    get_tenant_product,
)


VERSION: Final[str] = "v1.0.0-D22B1-TENANT-PRODUCT-ENTITLEMENT"
SCHEMA: Final[str] = "WILSY-TENANT-PRODUCT-ENTITLEMENT/V1"
_FIELDS: Final[tuple[str, ...]] = (
    "schema",
    "entitlement_version",
    "lifecycle_revision",
    "tenant_id",
    "entitlement_id",
    "product_id",
    "product_catalogue_fingerprint",
    "lifecycle_state",
    "source_evidence_reference",
    "source_evidence_fingerprint",
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
ENTITLEMENT_FIELDS: Final[tuple[str, ...]] = _FIELDS
_HEX_DIGITS: Final[frozenset[str]] = frozenset("0123456789abcdef")


class TenantProductEntitlementError(ValueError):
    """Raised when tenant product entitlement evidence violates the contract."""


class TenantProductEntitlementState(str, Enum):
    """Closed tenant-product entitlement lifecycle states."""

    PENDING_SOURCE = "PENDING_SOURCE"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    REVOKED = "REVOKED"


def _text(name: str, value: object) -> str:
    """Normalize one bounded identity/reference string without inventing truth."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantProductEntitlementError(f"D22B1_INVALID_{name.upper()}")
    normalized = unicodedata.normalize("NFC", value)
    if not normalized or any(ord(character) < 32 for character in normalized):
        raise TenantProductEntitlementError(f"D22B1_INVALID_{name.upper()}")
    return normalized


def _fingerprint(name: str, value: object) -> str:
    """Require one lowercase SHA3-512-shaped evidence fingerprint."""
    if (
        not isinstance(value, str)
        or len(value) != 128
        or not value
        or any(character not in _HEX_DIGITS for character in value)
    ):
        raise TenantProductEntitlementError(f"D22B1_INVALID_{name.upper()}")
    return value


def _when(name: str, value: object) -> datetime | None:
    """Normalize timezone-aware lifecycle time into UTC."""
    if value is None:
        return None
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            raise TenantProductEntitlementError(
                f"D22B1_INVALID_{name.upper()}"
            ) from error
    if (
        not isinstance(parsed, datetime)
        or parsed.tzinfo is None
        or parsed.utcoffset() is None
    ):
        raise TenantProductEntitlementError(f"D22B1_INVALID_{name.upper()}")
    return parsed.astimezone(timezone.utc)


def _reference_pair(
    name: str,
    reference: object,
    fingerprint: object,
) -> tuple[str | None, str | None]:
    """Validate an optional reference/fingerprint pair atomically."""
    if reference is None and fingerprint is None:
        return None, None
    return (
        _text(name, reference),
        _fingerprint(f"{name}_fingerprint", fingerprint),
    )


def _json_value(value: object) -> object:
    """Project exact domain values into deterministic JSON-compatible form."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, Enum):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class TenantProductEntitlement:
    """Immutable tenant/product entitlement lifecycle evidence.

    ACTIVE means the tenant has the product entitlement. It does not prove that
    a particular principal is authorized to use the product, that a browser may
    route to it, or that any VAS/financial capability is enabled.
    """

    tenant_id: str
    entitlement_id: str
    product_id: TenantProductId | str
    product_catalogue_fingerprint: str
    lifecycle_state: TenantProductEntitlementState | str
    source_evidence_reference: str
    source_evidence_fingerprint: str
    activated_at: datetime | None = None
    activation_evidence_reference: str | None = None
    activation_evidence_fingerprint: str | None = None
    suspended_at: datetime | None = None
    suspension_evidence_reference: str | None = None
    suspension_evidence_fingerprint: str | None = None
    revoked_at: datetime | None = None
    revocation_evidence_reference: str | None = None
    revocation_evidence_fingerprint: str | None = None
    schema: str = SCHEMA
    entitlement_version: str = VERSION
    lifecycle_revision: int = 0
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate canonical bindings/lifecycle shape and derive integrity."""
        tenant_id = _text("tenant_id", self.tenant_id)
        if tenant_id.casefold() in {"default", "global", "root", "*"}:
            raise TenantProductEntitlementError("D22B1_TENANT_REQUIRED")

        entitlement_id = _text("entitlement_id", self.entitlement_id)
        try:
            product_id = TenantProductId(self.product_id)
            lifecycle_state = TenantProductEntitlementState(self.lifecycle_state)
        except (TypeError, ValueError) as error:
            raise TenantProductEntitlementError("D22B1_ENUM_INVALID") from error

        if self.schema != SCHEMA or self.entitlement_version != VERSION:
            raise TenantProductEntitlementError("D22B1_IDENTITY_INVALID")
        if (
            isinstance(self.lifecycle_revision, bool)
            or not isinstance(self.lifecycle_revision, int)
            or self.lifecycle_revision < 0
        ):
            raise TenantProductEntitlementError("D22B1_REVISION_INVALID")

        descriptor = get_tenant_product(product_id)
        catalogue_fingerprint = _fingerprint(
            "product_catalogue_fingerprint",
            self.product_catalogue_fingerprint,
        )
        if not hmac.compare_digest(
            descriptor.fingerprint,
            catalogue_fingerprint,
        ):
            raise TenantProductEntitlementError(
                "D22B1_CATALOGUE_BINDING_INVALID"
            )

        source_reference = _text(
            "source_evidence_reference",
            self.source_evidence_reference,
        )
        source_fingerprint = _fingerprint(
            "source_evidence_fingerprint",
            self.source_evidence_fingerprint,
        )

        activated_at = _when("activated_at", self.activated_at)
        activation_reference, activation_fingerprint = _reference_pair(
            "activation_evidence_reference",
            self.activation_evidence_reference,
            self.activation_evidence_fingerprint,
        )
        suspended_at = _when("suspended_at", self.suspended_at)
        suspension_reference, suspension_fingerprint = _reference_pair(
            "suspension_evidence_reference",
            self.suspension_evidence_reference,
            self.suspension_evidence_fingerprint,
        )
        revoked_at = _when("revoked_at", self.revoked_at)
        revocation_reference, revocation_fingerprint = _reference_pair(
            "revocation_evidence_reference",
            self.revocation_evidence_reference,
            self.revocation_evidence_fingerprint,
        )

        if lifecycle_state is TenantProductEntitlementState.PENDING_SOURCE:
            if any(
                value is not None
                for value in (
                    activated_at,
                    activation_reference,
                    suspended_at,
                    suspension_reference,
                    revoked_at,
                    revocation_reference,
                )
            ):
                raise TenantProductEntitlementError(
                    "D22B1_PENDING_SHAPE_INVALID"
                )

        elif lifecycle_state is TenantProductEntitlementState.ACTIVE:
            if (
                activated_at is None
                or activation_reference is None
                or suspended_at is not None
                or suspension_reference is not None
                or revoked_at is not None
                or revocation_reference is not None
            ):
                raise TenantProductEntitlementError(
                    "D22B1_ACTIVE_SHAPE_INVALID"
                )

        elif lifecycle_state is TenantProductEntitlementState.SUSPENDED:
            if (
                activated_at is None
                or activation_reference is None
                or suspended_at is None
                or suspension_reference is None
                or revoked_at is not None
                or revocation_reference is not None
            ):
                raise TenantProductEntitlementError(
                    "D22B1_SUSPENDED_SHAPE_INVALID"
                )

        elif (
            activated_at is None
            or activation_reference is None
            or revoked_at is None
            or revocation_reference is None
            or suspended_at is not None
            or suspension_reference is not None
        ):
            raise TenantProductEntitlementError("D22B1_REVOKED_SHAPE_INVALID")

        if (
            activated_at is not None
            and suspended_at is not None
            and suspended_at < activated_at
        ):
            raise TenantProductEntitlementError("D22B1_CHRONOLOGY_INVALID")
        if (
            activated_at is not None
            and revoked_at is not None
            and revoked_at < activated_at
        ):
            raise TenantProductEntitlementError("D22B1_CHRONOLOGY_INVALID")

        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(self, "entitlement_id", entitlement_id)
        object.__setattr__(self, "product_id", product_id)
        object.__setattr__(self, "product_catalogue_fingerprint", catalogue_fingerprint)
        object.__setattr__(self, "lifecycle_state", lifecycle_state)
        object.__setattr__(self, "source_evidence_reference", source_reference)
        object.__setattr__(self, "source_evidence_fingerprint", source_fingerprint)
        object.__setattr__(self, "activated_at", activated_at)
        object.__setattr__(self, "activation_evidence_reference", activation_reference)
        object.__setattr__(self, "activation_evidence_fingerprint", activation_fingerprint)
        object.__setattr__(self, "suspended_at", suspended_at)
        object.__setattr__(self, "suspension_evidence_reference", suspension_reference)
        object.__setattr__(self, "suspension_evidence_fingerprint", suspension_fingerprint)
        object.__setattr__(self, "revoked_at", revoked_at)
        object.__setattr__(self, "revocation_evidence_reference", revocation_reference)
        object.__setattr__(self, "revocation_evidence_fingerprint", revocation_fingerprint)

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
            raise TenantProductEntitlementError("D22B1_FINGERPRINT_MISMATCH")
        object.__setattr__(self, "fingerprint", digest)

    def to_dict(self) -> dict[str, object]:
        """Serialize the exact entitlement evidence document."""
        return {
            field: _json_value(getattr(self, field))
            for field in _FIELDS
        }

    def transition(
        self,
        target_state: TenantProductEntitlementState | str,
        *,
        expected_revision: int,
        evidence_reference: str,
        evidence_fingerprint: str,
        occurred_at: datetime,
    ) -> "TenantProductEntitlement":
        """Return one legal revisioned transition without mutating this value.

        Caller transaction ownership and persistence/CAS are outside this domain.
        """
        if (
            isinstance(expected_revision, bool)
            or not isinstance(expected_revision, int)
            or expected_revision != self.lifecycle_revision
        ):
            raise TenantProductEntitlementError("D22B1_STALE_REVISION")
        try:
            target = TenantProductEntitlementState(target_state)
        except (TypeError, ValueError) as error:
            raise TenantProductEntitlementError(
                "D22B1_TRANSITION_INVALID"
            ) from error

        legal = {
            TenantProductEntitlementState.PENDING_SOURCE: {
                TenantProductEntitlementState.ACTIVE,
            },
            TenantProductEntitlementState.ACTIVE: {
                TenantProductEntitlementState.SUSPENDED,
                TenantProductEntitlementState.REVOKED,
            },
            TenantProductEntitlementState.SUSPENDED: set(),
            TenantProductEntitlementState.REVOKED: set(),
        }
        current = cast(TenantProductEntitlementState, self.lifecycle_state)
        if target not in legal[current]:
            raise TenantProductEntitlementError("D22B1_ILLEGAL_TRANSITION")

        reference = _text("evidence_reference", evidence_reference)
        evidence_digest = _fingerprint(
            "evidence_fingerprint",
            evidence_fingerprint,
        )
        when = _when("occurred_at", occurred_at)
        assert when is not None

        changes: dict[str, object] = {
            "lifecycle_state": target,
            "lifecycle_revision": self.lifecycle_revision + 1,
            "fingerprint": "",
        }
        if target is TenantProductEntitlementState.ACTIVE:
            changes.update(
                activated_at=when,
                activation_evidence_reference=reference,
                activation_evidence_fingerprint=evidence_digest,
            )
        elif target is TenantProductEntitlementState.SUSPENDED:
            changes.update(
                suspended_at=when,
                suspension_evidence_reference=reference,
                suspension_evidence_fingerprint=evidence_digest,
            )
        else:
            changes.update(
                revoked_at=when,
                revocation_evidence_reference=reference,
                revocation_evidence_fingerprint=evidence_digest,
            )

        values = {
            field: getattr(self, field)
            for field in _FIELDS[:-1]
        }
        values.update(changes)
        return TenantProductEntitlement(**cast(Any, values))

    @classmethod
    def from_dict(
        cls,
        payload: Mapping[str, object],
    ) -> "TenantProductEntitlement":
        """Hydrate exactly the authority fields and verify stored integrity."""
        if not isinstance(payload, Mapping) or set(payload) != set(_FIELDS):
            raise TenantProductEntitlementError("D22B1_SCHEMA_INVALID")
        values = dict(payload)
        stored_fingerprint = values.pop("fingerprint")
        item = cls(**cast(Any, values))
        if (
            not isinstance(stored_fingerprint, str)
            or not hmac.compare_digest(stored_fingerprint, item.fingerprint)
        ):
            raise TenantProductEntitlementError("D22B1_FINGERPRINT_MISMATCH")
        return item


def create_tenant_product_entitlement(
    *,
    tenant_id: str,
    entitlement_id: str,
    product_id: TenantProductId | str,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
) -> TenantProductEntitlement:
    """Create one pending entitlement bound to canonical product evidence.

    Creation never activates the product. A separate evidence-backed lifecycle
    transition is required before the tenant may be projected as ACTIVE.
    """
    descriptor = get_tenant_product(product_id)
    return TenantProductEntitlement(
        tenant_id=tenant_id,
        entitlement_id=entitlement_id,
        product_id=descriptor.product_id,
        product_catalogue_fingerprint=descriptor.fingerprint,
        lifecycle_state=TenantProductEntitlementState.PENDING_SOURCE,
        source_evidence_reference=source_evidence_reference,
        source_evidence_fingerprint=source_evidence_fingerprint,
    )


__all__ = [
    "ENTITLEMENT_FIELDS",
    "SCHEMA",
    "TenantProductEntitlement",
    "TenantProductEntitlementError",
    "TenantProductEntitlementState",
    "VERSION",
    "create_tenant_product_entitlement",
]

# ARTIFACT: tenant_product_entitlement.py
# VERSION: v1.0.0-D22B1-TENANT-PRODUCT-ENTITLEMENT
# AUTHORITY BOUNDARY: tenant/product entitlement lifecycle evidence only; no IAM, VAS or workspace admission
# TENANT POSTURE: exact tenant/product binding; pseudo-tenants reject
# FAIL-CLOSED POSTURE: unknown products, catalogue drift, malformed evidence and illegal transitions reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
