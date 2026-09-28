"""WILSY OS subscription-derived Tenant Branding VAS eligibility evidence.

TITLE: Tenant Branding Commercial Eligibility Domain
VERSION: v1.0.1-D21C1-CANONICAL-SUBSCRIPTION-INTEGRITY
AUTHORITY: Wilsy OS Core Governance
EPITOME: Project one canonical SubscriptionEntity snapshot into deterministic
         ELIGIBLE or INELIGIBLE Branding VAS evidence for D21B2B. This domain
         never creates subscription, payment, profile, asset, IAM or browser
         authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/domain/tenant_branding_commercial_eligibility.py
COLLABORATION / OWNERSHIP: PlanRegistry owns plan catalogue truth;
                            SubscriptionRegistry owns tenant subscription
                            truth; D21C1 catalogue owns exact Branding VAS
                            identities; D21B2B owns entitlement lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-D21C1 binds tenant, subscription, plan, catalogue version,
           exact Branding VAS identity, D21B tier, canonical subscription
           proof, lifecycle status, evaluated_at and deterministic SHA3-512
           evidence. Only ACTIVE subscriptions are eligible; all other states
           fail closed without inventing financial failure.
           v1.0.1 repairs validation of registry-persisted proof provenance by
           replaying the latest canonical AuditEntry action and metadata before
           merkle verification; no authority boundary changes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No secrets or payment-provider fields are read;
                             only canonical subscription evidence is consumed.
TENANT BOUNDARY: The supplied tenant must exactly equal SubscriptionEntity.tenant_id.
AUTHORITY BOUNDARY: Eligibility projection only; no entitlement activation,
                    profile approval, asset selection, IAM or browser authority.
FINANCIAL AUTHORITY BOUNDARY: No price, charge, payment, execution or
                               settlement truth. Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Tenant mismatch, stale/unknown status, missing
                         provenance, conflicting identities and integrity drift
                         reject deterministically.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import hmac
import json
from typing import Any, Final

from tools.eos.saas.billing.tenant_branding_vas_catalogue import (
    CATALOGUE_FINGERPRINT,
    TenantBrandingVASCatalogueError,
    TenantBrandingVASCommercialProduct,
    resolve_branding_vas_identity,
)
from tools.eos.saas.domain.subscription import (
    SubscriptionEntity,
    SubscriptionStatus,
    verify_subscription_integrity,
)
from tools.eos.saas.billing.tenant_branding_vas_policy import TenantBrandingTier


VERSION: Final[str] = "v1.0.1-D21C1-CANONICAL-SUBSCRIPTION-INTEGRITY"
SCHEMA: Final[str] = "WILSY-TENANT-BRANDING-COMMERCIAL-ELIGIBILITY/V1"


class TenantBrandingCommercialEligibilityError(ValueError):
    """Raised when canonical subscription evidence cannot be projected safely."""


class TenantBrandingCommercialEligibilityState(str, Enum):
    """Closed eligibility result states."""

    ELIGIBLE = "ELIGIBLE"
    INELIGIBLE = "INELIGIBLE"


def _text(name: str, value: object) -> str:
    """Require one non-empty exact identity string."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantBrandingCommercialEligibilityError(
            f"D21C1_{name.upper()}_INVALID"
        )
    return value


def _when(value: object) -> datetime:
    """Require one explicit timezone-aware evaluation instant and normalize UTC."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            raise TenantBrandingCommercialEligibilityError(
                "D21C1_EVALUATED_AT_INVALID"
            ) from error
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TenantBrandingCommercialEligibilityError(
            "D21C1_EVALUATED_AT_INVALID"
        )
    return parsed.astimezone(timezone.utc)


def _canonical_status(value: object) -> SubscriptionStatus:
    """Require a known canonical SubscriptionStatus."""
    try:
        return SubscriptionStatus(value)
    except (TypeError, ValueError) as error:
        raise TenantBrandingCommercialEligibilityError(
            "D21C1_SUBSCRIPTION_STATUS_INVALID"
        ) from error


def _digest(payload: object) -> str:
    """Hash deterministic JSON eligibility evidence."""
    return hashlib.sha3_512(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class TenantBrandingCommercialEligibility:
    """Immutable subscription-derived D21B eligibility evidence."""

    tenant_id: str
    subscription_id: str
    plan_id: str
    plan_catalogue_version: int | None
    branding_vas_id: str | None
    branding_tier: TenantBrandingTier | None
    subscription_status: SubscriptionStatus
    subscription_proof_hash: str
    evaluated_at: datetime
    state: TenantBrandingCommercialEligibilityState
    catalogue_fingerprint: str = CATALOGUE_FINGERPRINT
    schema: str = SCHEMA
    eligibility_version: str = VERSION
    fingerprint: str = ""

    def __post_init__(self) -> None:
        """Validate exact field shape and derive the integrity fingerprint."""
        tenant = _text("tenant_id", self.tenant_id)
        subscription = _text("subscription_id", self.subscription_id)
        plan = _text("plan_id", self.plan_id)
        if tenant.casefold() in {"default", "global", "root", "*"}:
            raise TenantBrandingCommercialEligibilityError("D21C1_TENANT_REQUIRED")
        if self.plan_catalogue_version is not None and (
            isinstance(self.plan_catalogue_version, bool)
            or not isinstance(self.plan_catalogue_version, int)
            or self.plan_catalogue_version < 1
        ):
            raise TenantBrandingCommercialEligibilityError(
                "D21C1_PLAN_CATALOGUE_VERSION_INVALID"
            )
        if self.branding_vas_id is None:
            if self.branding_tier is not None:
                raise TenantBrandingCommercialEligibilityError(
                    "D21C1_BRANDING_IDENTITY_TIER_MISMATCH"
                )
        else:
            try:
                product = resolve_branding_vas_identity((self.branding_vas_id,))
            except TenantBrandingVASCatalogueError as error:
                raise TenantBrandingCommercialEligibilityError(
                    "D21C1_BRANDING_IDENTITY_INVALID"
                ) from error
            if product is None or product.branding_tier is not self.branding_tier:
                raise TenantBrandingCommercialEligibilityError(
                    "D21C1_BRANDING_IDENTITY_TIER_MISMATCH"
                )
        if not isinstance(self.subscription_status, SubscriptionStatus):
            raise TenantBrandingCommercialEligibilityError(
                "D21C1_SUBSCRIPTION_STATUS_INVALID"
            )
        proof = _text("subscription_proof_hash", self.subscription_proof_hash)
        evaluated = _when(self.evaluated_at)
        if self.schema != SCHEMA or self.eligibility_version != VERSION:
            raise TenantBrandingCommercialEligibilityError(
                "D21C1_IDENTITY_INVALID"
            )
        if not hmac.compare_digest(self.catalogue_fingerprint, CATALOGUE_FINGERPRINT):
            raise TenantBrandingCommercialEligibilityError(
                "D21C1_CATALOGUE_FINGERPRINT_INVALID"
            )
        if not isinstance(self.state, TenantBrandingCommercialEligibilityState):
            raise TenantBrandingCommercialEligibilityError("D21C1_STATE_INVALID")
        if self.state is TenantBrandingCommercialEligibilityState.ELIGIBLE and (
            self.branding_vas_id is None
            or self.branding_tier is None
            or self.subscription_status is not SubscriptionStatus.ACTIVE
            or self.plan_catalogue_version is None
        ):
            raise TenantBrandingCommercialEligibilityError(
                "D21C1_ELIGIBLE_SHAPE_INVALID"
            )
        payload = self._payload(
            tenant,
            subscription,
            plan,
            proof,
            evaluated,
        )
        digest = _digest(payload)
        if self.fingerprint and not hmac.compare_digest(self.fingerprint, digest):
            raise TenantBrandingCommercialEligibilityError(
                "D21C1_FINGERPRINT_MISMATCH"
            )
        object.__setattr__(self, "tenant_id", tenant)
        object.__setattr__(self, "subscription_id", subscription)
        object.__setattr__(self, "plan_id", plan)
        object.__setattr__(self, "subscription_proof_hash", proof)
        object.__setattr__(self, "evaluated_at", evaluated)
        object.__setattr__(self, "fingerprint", digest)

    def _payload(
        self,
        tenant: str | None = None,
        subscription: str | None = None,
        plan: str | None = None,
        proof: str | None = None,
        evaluated: datetime | None = None,
    ) -> dict[str, object]:
        """Return exact semantic evidence excluding the derived fingerprint."""
        instant = evaluated or self.evaluated_at
        return {
            "schema": self.schema,
            "eligibility_version": self.eligibility_version,
            "tenant_id": tenant or self.tenant_id,
            "subscription_id": subscription or self.subscription_id,
            "plan_id": plan or self.plan_id,
            "plan_catalogue_version": self.plan_catalogue_version,
            "branding_vas_id": self.branding_vas_id,
            "branding_tier": self.branding_tier.value if self.branding_tier else None,
            "subscription_status": self.subscription_status.value,
            "subscription_proof_hash": proof or self.subscription_proof_hash,
            "evaluated_at": instant.isoformat().replace("+00:00", "Z"),
            "state": self.state.value,
            "catalogue_fingerprint": self.catalogue_fingerprint,
        }

    def to_dict(self) -> dict[str, object]:
        """Serialize exact deterministic eligibility evidence."""
        payload = self._payload()
        payload["fingerprint"] = self.fingerprint
        return payload


def derive_tenant_branding_commercial_eligibility(
    *,
    tenant_id: str,
    subscription: SubscriptionEntity,
    evaluated_at: datetime,
) -> TenantBrandingCommercialEligibility:
    """Derive eligibility from canonical SubscriptionEntity truth only."""
    if type(subscription) is not SubscriptionEntity:
        raise TenantBrandingCommercialEligibilityError(
            "D21C1_SUBSCRIPTION_REQUIRED"
        )
    tenant = _text("tenant_id", tenant_id)
    if subscription.tenant_id != tenant:
        raise TenantBrandingCommercialEligibilityError("D21C1_TENANT_MISMATCH")
    if not verify_subscription_integrity(subscription):
        raise TenantBrandingCommercialEligibilityError(
            "D21C1_SUBSCRIPTION_INTEGRITY_INVALID"
        )
    status = _canonical_status(subscription.status)
    try:
        product: TenantBrandingVASCommercialProduct | None = resolve_branding_vas_identity(
            subscription.plan_features
        )
    except TenantBrandingVASCatalogueError as error:
        raise TenantBrandingCommercialEligibilityError(
            error.args[0] if error.args else "D21C1_BRANDING_IDENTITY_INVALID"
        ) from error
    eligible = (
        product is not None
        and status is SubscriptionStatus.ACTIVE
        and subscription.plan_catalogue_version is not None
    )
    return TenantBrandingCommercialEligibility(
        tenant_id=tenant,
        subscription_id=subscription.subscription_id,
        plan_id=subscription.plan_id,
        plan_catalogue_version=subscription.plan_catalogue_version,
        branding_vas_id=product.commercial_id if product else None,
        branding_tier=product.branding_tier if product else None,
        subscription_status=status,
        subscription_proof_hash=subscription.proof_hash,
        evaluated_at=evaluated_at,
        state=(
            TenantBrandingCommercialEligibilityState.ELIGIBLE
            if eligible
            else TenantBrandingCommercialEligibilityState.INELIGIBLE
        ),
    )


__all__ = [
    "SCHEMA",
    "TenantBrandingCommercialEligibility",
    "TenantBrandingCommercialEligibilityError",
    "TenantBrandingCommercialEligibilityState",
    "VERSION",
    "derive_tenant_branding_commercial_eligibility",
]

# ARTIFACT: tenant_branding_commercial_eligibility.py
# VERSION: v1.0.1-D21C1-CANONICAL-SUBSCRIPTION-INTEGRITY
# AUTHORITY BOUNDARY: subscription-derived eligibility evidence only; no D21B activation/profile/browser authority
# TENANT POSTURE: exact tenant/subscription binding; mismatch rejects
# FAIL-CLOSED POSTURE: unknown state, identity, provenance or fingerprint drift rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
