"""WILSY OS tenant Legal Evidence capacity-profile evidence resolver.

TITLE: Tenant Legal Evidence Capacity Profile Resolver
VERSION: v1.0.0-L10A2Q-P2-TENANT-LEGAL-EVIDENCE-CAPACITY-PROFILE
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Derive immutable tenant-scoped Legal Evidence capacity-profile evidence
         from canonical subscription truth, ACTIVE Legal Operations product
         entitlement evidence and the certified capacity-profile binding seam.

EPITOME:
    SUBSCRIPTION ACTIVE
    != LEGAL_OPERATIONS ENTITLEMENT ACTIVE
    != CAPACITY PROFILE BOUND
    != STORAGE ADMISSION
    != BILLING AUTHORITY
    != PAYMENT EXECUTION
    != SETTLEMENT

    All required authorities must independently agree before this artifact emits
    one deterministic tenant capacity-profile evidence value.

COLLABORATION / OWNERSHIP:
    SubscriptionRegistry owns canonical tenant subscription truth.
    PlanRegistry owns canonical plan catalogue truth projected into subscription.
    TenantProductEntitlement owns tenant/product lifecycle evidence.
    L10A2Q-P2 profile resolver owns explicit capacity-profile identity binding.
    This artifact owns only immutable composition evidence.

CERTIFICATION / UPDATE DATE: 2026-09-29

TENANT BOUNDARY:
    Requested tenant, SubscriptionEntity.tenant_id and
    TenantProductEntitlement.tenant_id must match exactly. Mismatch rejects.

AUTHORITY BOUNDARY:
    Read-only evidence projection only. No plan mutation, subscription mutation,
    entitlement activation, IAM, storage admission, quota reservation, billing,
    payment, settlement or financial execution authority.

FINANCIAL AUTHORITY BOUNDARY:
    Price, amount, currency, invoice, payment and settlement fields are not
    projected. Kennel EOS remains exclusive financial execution authority.

FAIL-CLOSED DECLARATION:
    Invalid type, tenant mismatch, subscription integrity failure, inactive
    subscription, absent catalogue provenance, wrong/inactive product
    entitlement, malformed evaluation time, or unresolved profile rejects.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
import json
from typing import Final

from tools.eos.saas.billing.legal_evidence_capacity_policy_contract import (
    LegalEvidenceCapacityProfile,
)
from tools.eos.saas.billing.legal_evidence_capacity_profile_resolver import (
    LegalEvidenceCapacityProfileResolverError,
    resolve_legal_evidence_capacity_profile_identity,
)
from tools.eos.saas.domain.subscription import (
    SubscriptionEntity,
    SubscriptionStatus,
    verify_subscription_integrity,
)
from tools.eos.saas.domain.tenant_product_entitlement import (
    TenantProductEntitlement,
    TenantProductEntitlementState,
)
from tools.eos.saas.entitlement.product_catalogue import (
    TenantProductId,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2Q-P2-TENANT-LEGAL-EVIDENCE-CAPACITY-PROFILE"
)
SCHEMA: Final[str] = (
    "WILSY-TENANT-LEGAL-EVIDENCE-CAPACITY-PROFILE-EVIDENCE/V1"
)


class LegalEvidenceCapacityTenantProfileError(ValueError):
    """Raised when tenant capacity-profile evidence cannot be derived safely."""


def _text(name: str, value: object) -> str:
    """Require one non-empty exact text value."""
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
    ):
        raise LegalEvidenceCapacityTenantProfileError(
            f"L10A2Q_P2_{name.upper()}_INVALID"
        )
    return value


def _evaluated_at(value: object) -> datetime:
    """Require one timezone-aware instant and normalize it to UTC."""
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceCapacityTenantProfileError(
            "L10A2Q_P2_EVALUATED_AT_INVALID"
        )
    return value.astimezone(timezone.utc)


def _json_value(value: object) -> object:
    """Project supported immutable evidence values into canonical JSON."""
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace(
            "+00:00",
            "Z",
        )
    if isinstance(value, (
        TenantProductId,
        LegalEvidenceCapacityProfile,
    )):
        return value.value
    return value


@dataclass(frozen=True, slots=True)
class LegalEvidenceCapacityTenantProfile:
    """Immutable tenant-scoped Legal Evidence capacity-profile evidence."""

    tenant_id: str
    subscription_id: str
    plan_id: str
    plan_catalogue_version: int
    subscription_proof_hash: str
    entitlement_id: str
    entitlement_revision: int
    entitlement_fingerprint: str
    product_id: TenantProductId
    profile: LegalEvidenceCapacityProfile
    evaluated_at: datetime
    schema: str = SCHEMA
    resolver_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact evidence shape and derive deterministic SHA3-512."""
        tenant_id = _text("tenant_id", self.tenant_id)
        subscription_id = _text(
            "subscription_id",
            self.subscription_id,
        )
        plan_id = _text("plan_id", self.plan_id)

        if (
            isinstance(self.plan_catalogue_version, bool)
            or not isinstance(self.plan_catalogue_version, int)
            or self.plan_catalogue_version < 1
        ):
            raise LegalEvidenceCapacityTenantProfileError(
                "L10A2Q_P2_PLAN_CATALOGUE_VERSION_INVALID"
            )

        subscription_proof_hash = _text(
            "subscription_proof_hash",
            self.subscription_proof_hash,
        )

        entitlement_id = _text(
            "entitlement_id",
            self.entitlement_id,
        )
        if (
            isinstance(self.entitlement_revision, bool)
            or not isinstance(self.entitlement_revision, int)
            or self.entitlement_revision < 1
        ):
            raise LegalEvidenceCapacityTenantProfileError(
                "L10A2Q_P2_ENTITLEMENT_REVISION_INVALID"
            )

        entitlement_fingerprint = _text(
            "entitlement_fingerprint",
            self.entitlement_fingerprint,
        )
        if len(entitlement_fingerprint) != 128:
            raise LegalEvidenceCapacityTenantProfileError(
                "L10A2Q_P2_ENTITLEMENT_FINGERPRINT_INVALID"
            )
        try:
            int(entitlement_fingerprint, 16)
        except ValueError as error:
            raise LegalEvidenceCapacityTenantProfileError(
                "L10A2Q_P2_ENTITLEMENT_FINGERPRINT_INVALID"
            ) from error

        try:
            product_id = TenantProductId(self.product_id)
        except (TypeError, ValueError) as error:
            raise LegalEvidenceCapacityTenantProfileError(
                "L10A2Q_P2_PRODUCT_ID_INVALID"
            ) from error

        if product_id is not TenantProductId.LEGAL_OPERATIONS:
            raise LegalEvidenceCapacityTenantProfileError(
                "L10A2Q_P2_LEGAL_PRODUCT_REQUIRED"
            )

        try:
            profile = LegalEvidenceCapacityProfile(self.profile)
        except (TypeError, ValueError) as error:
            raise LegalEvidenceCapacityTenantProfileError(
                "L10A2Q_P2_PROFILE_INVALID"
            ) from error

        evaluated_at = _evaluated_at(self.evaluated_at)

        if self.schema != SCHEMA or self.resolver_version != VERSION:
            raise LegalEvidenceCapacityTenantProfileError(
                "L10A2Q_P2_IDENTITY_INVALID"
            )

        object.__setattr__(self, "tenant_id", tenant_id)
        object.__setattr__(
            self,
            "subscription_id",
            subscription_id,
        )
        object.__setattr__(self, "plan_id", plan_id)
        object.__setattr__(
            self,
            "subscription_proof_hash",
            subscription_proof_hash,
        )
        object.__setattr__(
            self,
            "entitlement_id",
            entitlement_id,
        )
        object.__setattr__(
            self,
            "entitlement_fingerprint",
            entitlement_fingerprint,
        )
        object.__setattr__(self, "product_id", product_id)
        object.__setattr__(self, "profile", profile)
        object.__setattr__(self, "evaluated_at", evaluated_at)

        payload = self._payload()
        digest = hashlib.sha3_512(
            json.dumps(
                payload,
                ensure_ascii=False,
                allow_nan=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        ).hexdigest()

        if self.fingerprint and (
            not isinstance(self.fingerprint, str)
            or not hmac.compare_digest(
                self.fingerprint,
                digest,
            )
        ):
            raise LegalEvidenceCapacityTenantProfileError(
                "L10A2Q_P2_FINGERPRINT_MISMATCH"
            )

        object.__setattr__(self, "fingerprint", digest)

    def _payload(self) -> dict[str, object]:
        """Return exact semantic evidence excluding derived fingerprint."""
        return {
            "schema": self.schema,
            "resolver_version": self.resolver_version,
            "tenant_id": self.tenant_id,
            "subscription_id": self.subscription_id,
            "plan_id": self.plan_id,
            "plan_catalogue_version":
                self.plan_catalogue_version,
            "subscription_proof_hash":
                self.subscription_proof_hash,
            "entitlement_id": self.entitlement_id,
            "entitlement_revision":
                self.entitlement_revision,
            "entitlement_fingerprint":
                self.entitlement_fingerprint,
            "product_id": _json_value(self.product_id),
            "profile": _json_value(self.profile),
            "evaluated_at": _json_value(self.evaluated_at),
        }

    def to_dict(self) -> dict[str, object]:
        """Serialize exact deterministic tenant profile evidence."""
        payload = self._payload()
        payload["fingerprint"] = self.fingerprint
        return payload


def derive_legal_evidence_capacity_tenant_profile(
    *,
    tenant_id: str,
    subscription: SubscriptionEntity,
    entitlement: TenantProductEntitlement,
    evaluated_at: datetime,
) -> LegalEvidenceCapacityTenantProfile:
    """Compose tenant Legal Evidence capacity-profile evidence fail closed."""
    tenant = _text("tenant_id", tenant_id)

    if type(subscription) is not SubscriptionEntity:
        raise LegalEvidenceCapacityTenantProfileError(
            "L10A2Q_P2_SUBSCRIPTION_REQUIRED"
        )

    if subscription.tenant_id != tenant:
        raise LegalEvidenceCapacityTenantProfileError(
            "L10A2Q_P2_SUBSCRIPTION_TENANT_MISMATCH"
        )

    if not verify_subscription_integrity(subscription):
        raise LegalEvidenceCapacityTenantProfileError(
            "L10A2Q_P2_SUBSCRIPTION_INTEGRITY_INVALID"
        )

    try:
        status = SubscriptionStatus(subscription.status)
    except (TypeError, ValueError) as error:
        raise LegalEvidenceCapacityTenantProfileError(
            "L10A2Q_P2_SUBSCRIPTION_STATUS_INVALID"
        ) from error

    if status is not SubscriptionStatus.ACTIVE:
        raise LegalEvidenceCapacityTenantProfileError(
            "L10A2Q_P2_SUBSCRIPTION_ACTIVE_REQUIRED"
        )

    if subscription.plan_catalogue_version is None:
        raise LegalEvidenceCapacityTenantProfileError(
            "L10A2Q_P2_PLAN_CATALOGUE_VERSION_REQUIRED"
        )

    if type(entitlement) is not TenantProductEntitlement:
        raise LegalEvidenceCapacityTenantProfileError(
            "L10A2Q_P2_ENTITLEMENT_REQUIRED"
        )

    if entitlement.tenant_id != tenant:
        raise LegalEvidenceCapacityTenantProfileError(
            "L10A2Q_P2_ENTITLEMENT_TENANT_MISMATCH"
        )

    if entitlement.product_id is not TenantProductId.LEGAL_OPERATIONS:
        raise LegalEvidenceCapacityTenantProfileError(
            "L10A2Q_P2_LEGAL_PRODUCT_REQUIRED"
        )

    if (
        entitlement.lifecycle_state
        is not TenantProductEntitlementState.ACTIVE
    ):
        raise LegalEvidenceCapacityTenantProfileError(
            "L10A2Q_P2_LEGAL_ENTITLEMENT_ACTIVE_REQUIRED"
        )

    try:
        profile = resolve_legal_evidence_capacity_profile_identity(
            plan_tier=subscription.plan,
            plan_features=subscription.plan_features,
        )
    except LegalEvidenceCapacityProfileResolverError as error:
        code = (
            str(error)
            if str(error)
            else "L10A2Q_P2_PROFILE_INVALID"
        )
        raise LegalEvidenceCapacityTenantProfileError(
            code
        ) from error

    instant = _evaluated_at(evaluated_at)

    return LegalEvidenceCapacityTenantProfile(
        tenant_id=tenant,
        subscription_id=subscription.subscription_id,
        plan_id=subscription.plan_id,
        plan_catalogue_version=
            subscription.plan_catalogue_version,
        subscription_proof_hash=subscription.proof_hash,
        entitlement_id=entitlement.entitlement_id,
        entitlement_revision=
            entitlement.lifecycle_revision,
        entitlement_fingerprint=
            entitlement.fingerprint,
        product_id=TenantProductId.LEGAL_OPERATIONS,
        profile=profile,
        evaluated_at=instant,
    )


__all__ = [
    "LegalEvidenceCapacityTenantProfile",
    "LegalEvidenceCapacityTenantProfileError",
    "SCHEMA",
    "VERSION",
    "derive_legal_evidence_capacity_tenant_profile",
]


# ARTIFACT: legal_evidence_capacity_tenant_profile_resolver.py
# VERSION: v1.0.0-L10A2Q-P2-TENANT-LEGAL-EVIDENCE-CAPACITY-PROFILE
# AUTHORITY BOUNDARY: immutable composition evidence only; no admission authority
# TENANT POSTURE: exact requested/subscription/entitlement tenant agreement
# FAIL-CLOSED POSTURE: invalid, inactive, mismatched or unbound authority rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
