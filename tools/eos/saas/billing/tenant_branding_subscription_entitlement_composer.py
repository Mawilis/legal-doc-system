"""WILSY OS subscription-to-D21B Branding VAS entitlement composer.

TITLE: Tenant Branding Subscription Entitlement Composer
VERSION: v1.0.0-D21C1-TENANT-BRANDING-SUBSCRIPTION-ENTITLEMENT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Read canonical tenant subscription snapshots, derive the D21C1
         commercial eligibility projection, and provision/activate one D21B2B
         entitlement under a caller-owned transaction. This module does not
         own subscription lifecycle, pricing, payment, settlement, profile,
         asset, IAM or browser authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_branding_subscription_entitlement_composer.py
COLLABORATION / OWNERSHIP: SubscriptionRegistry owns subscription truth;
                            D21C1 owns commercial identity/eligibility;
                            D21B2B owns entitlement persistence/lifecycle;
                            the caller owns Mongo session/transaction.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-D21C1 adds tenant-scoped subscription snapshot reading,
           deterministic source evidence, ambiguous-multiple fail-closed
           semantics, exact pending creation, ACTIVE transition and replay
           protection. No financial or browser authority is introduced.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No payment-provider fields, credentials or raw
                             asset bytes are read or persisted.
TENANT BOUNDARY: Tenant identity is explicit and forwarded to every
                 SubscriptionRegistry read and D21B2B operation.
AUTHORITY BOUNDARY: Commercial eligibility and D21B2B entitlement provisioning
                    only; no profile approval, asset selection, IAM or browser.
FINANCIAL AUTHORITY BOUNDARY: No charge, payment, execution or settlement
                               operation. Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: An active caller-owned session is mandatory; this module
                      never starts, commits, aborts, retries or closes it.
FAIL-CLOSED DECLARATION: Missing subscription, tenant mismatch, multiple
                         eligible Branding VAS subscriptions, divergent replay,
                         closed entitlement and persistence errors reject.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Final

from tools.eos.saas.billing import tenant_branding_entitlement_registry
from tools.eos.saas.billing.tenant_branding_entitlement_registry import (
    TenantBrandingEntitlementPersistenceOutcome,
    TenantBrandingEntitlementRegistryNotFoundError,
)
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.domain.subscription import SubscriptionEntity
from tools.eos.saas.domain.tenant_branding_commercial_eligibility import (
    TenantBrandingCommercialEligibility,
    TenantBrandingCommercialEligibilityError,
    TenantBrandingCommercialEligibilityState,
    derive_tenant_branding_commercial_eligibility,
)
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlement,
    TenantBrandingEntitlementState,
    create_tenant_branding_entitlement,
)


VERSION: Final[str] = "v1.0.0-D21C1-TENANT-BRANDING-SUBSCRIPTION-ENTITLEMENT"


class TenantBrandingSubscriptionEntitlementComposerError(RuntimeError):
    """Raised when commercial-to-D21B composition cannot remain deterministic."""


@dataclass(frozen=True, slots=True)
class TenantBrandingSubscriptionEntitlementComposition:
    """Eligibility plus optional durable D21B2B persistence outcomes."""

    eligibility: TenantBrandingCommercialEligibility
    entitlement: TenantBrandingEntitlement | None
    creation_outcome: Any | None
    activation_outcome: Any | None


def _active_transaction(session: Any) -> Any:
    """Require an active caller-owned transaction without taking ownership."""
    if session is None:
        raise TenantBrandingSubscriptionEntitlementComposerError(
            "D21C1_ACTIVE_TRANSACTION_REQUIRED"
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        raise TenantBrandingSubscriptionEntitlementComposerError(
            "D21C1_ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _text(name: str, value: object) -> str:
    """Require one explicit non-empty caller command identity."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantBrandingSubscriptionEntitlementComposerError(
            f"D21C1_{name.upper()}_INVALID"
        )
    return value


class TenantBrandingSubscriptionEntitlementComposer:
    """Compose subscription-derived eligibility into one D21B2B entitlement."""

    __slots__ = (
        "_subscription_registry",
        "_subscription_collection",
        "_entitlement_registry",
        "_history_collection",
        "_current_collection",
    )

    def __init__(
        self,
        *,
        subscription_collection: Any,
        history_collection: Any,
        current_collection: Any,
        subscription_registry: Any = SubscriptionRegistry,
        entitlement_registry: Any = tenant_branding_entitlement_registry,
    ) -> None:
        """Bind caller-injected persistence dependencies without opening clients."""
        if (
            subscription_collection is None
            or history_collection is None
            or current_collection is None
            or subscription_registry is None
            or entitlement_registry is None
        ):
            raise TenantBrandingSubscriptionEntitlementComposerError(
                "D21C1_PERSISTENCE_DEPENDENCY_REQUIRED"
            )
        self._subscription_registry = subscription_registry
        self._subscription_collection = subscription_collection
        self._entitlement_registry = entitlement_registry
        self._history_collection = history_collection
        self._current_collection = current_collection

    def compose(
        self,
        *,
        tenant_id: str,
        subscription_id: str,
        entitlement_id: str,
        evaluated_at: datetime,
        occurred_at: datetime,
        idempotency_key: str,
        session: Any,
    ) -> TenantBrandingSubscriptionEntitlementComposition:
        """Derive and persist one exact current commercial Branding VAS result.

        ``idempotency_key`` is validated as command evidence but is not allowed
        to override canonical subscription fields. D21B2B replay identity and
        lifecycle revision remain authoritative.
        """
        tx = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)
        subscription_identity = _text("subscription_id", subscription_id)
        entitlement_identity = _text("entitlement_id", entitlement_id)
        _text("idempotency_key", idempotency_key)

        try:
            subscriptions = tuple(
                self._subscription_registry.list_entities(
                    tenant_id_header=tenant,
                    collection=self._subscription_collection,
                    session=tx,
                )
            )
        except Exception as error:
            raise TenantBrandingSubscriptionEntitlementComposerError(
                "D21C1_SUBSCRIPTION_READ_REJECTED"
            ) from error

        exact = tuple(
            item
            for item in subscriptions
            if type(item) is SubscriptionEntity
            and item.subscription_id == subscription_identity
        )
        if len(exact) != 1:
            raise TenantBrandingSubscriptionEntitlementComposerError(
                "D21C1_SUBSCRIPTION_NOT_FOUND"
            )

        try:
            projections = tuple(
                derive_tenant_branding_commercial_eligibility(
                    tenant_id=tenant,
                    subscription=item,
                    evaluated_at=evaluated_at,
                )
                for item in subscriptions
            )
        except TenantBrandingCommercialEligibilityError as error:
            raise TenantBrandingSubscriptionEntitlementComposerError(
                str(error)
            ) from error

        eligible = tuple(
            item
            for item in projections
            if item.state is TenantBrandingCommercialEligibilityState.ELIGIBLE
        )
        if len(eligible) > 1:
            raise TenantBrandingSubscriptionEntitlementComposerError(
                "D21C1_MULTIPLE_ELIGIBLE_BRANDING_SUBSCRIPTIONS"
            )
        eligibility = next(
            item
            for item in projections
            if item.subscription_id == subscription_identity
        )
        if eligibility.state is TenantBrandingCommercialEligibilityState.INELIGIBLE:
            return TenantBrandingSubscriptionEntitlementComposition(
                eligibility=eligibility,
                entitlement=None,
                creation_outcome=None,
                activation_outcome=None,
            )

        assert eligibility.branding_tier is not None
        source_reference = (
            "subscription-branding-eligibility:"
            f"{eligibility.tenant_id}/{eligibility.subscription_id}/"
            f"{eligibility.plan_id}/{eligibility.plan_catalogue_version}/"
            f"{eligibility.branding_vas_id}"
        )
        source_fingerprint = eligibility.fingerprint
        try:
            current = self._entitlement_registry.get_current(
                tenant,
                entitlement_identity,
                self._history_collection,
                self._current_collection,
                session=tx,
            )
        except TenantBrandingEntitlementRegistryNotFoundError:
            current = None
        except Exception as error:
            raise TenantBrandingSubscriptionEntitlementComposerError(
                "D21C1_ENTITLEMENT_READ_REJECTED"
            ) from error

        if current is not None:
            if (
                current.branding_tier is not eligibility.branding_tier
                or current.source_evidence_reference != source_reference
                or current.source_evidence_fingerprint != source_fingerprint
            ):
                raise TenantBrandingSubscriptionEntitlementComposerError(
                    "D21C1_DIVERGENT_ENTITLEMENT_REPLAY"
                )
            if current.lifecycle_state is TenantBrandingEntitlementState.ACTIVE:
                return TenantBrandingSubscriptionEntitlementComposition(
                    eligibility=eligibility,
                    entitlement=current,
                    creation_outcome=None,
                    activation_outcome=TenantBrandingEntitlementPersistenceOutcome.IDEMPOTENT_REPLAY,
                )
            if current.lifecycle_state is not TenantBrandingEntitlementState.PENDING_SOURCE:
                raise TenantBrandingSubscriptionEntitlementComposerError(
                    "D21C1_ENTITLEMENT_CLOSED"
                )

        pending = create_tenant_branding_entitlement(
            tenant_id=tenant,
            entitlement_id=entitlement_identity,
            branding_tier=eligibility.branding_tier,
            source_evidence_reference=source_reference,
            source_evidence_fingerprint=source_fingerprint,
        )
        try:
            created = self._entitlement_registry.create_or_replay(
                pending,
                self._history_collection,
                self._current_collection,
                session=tx,
            )
            activated = self._entitlement_registry.transition(
                tenant_id=tenant,
                entitlement_id=entitlement_identity,
                target_state=TenantBrandingEntitlementState.ACTIVE,
                expected_revision=created.entitlement.lifecycle_revision,
                evidence_reference=(
                    f"{source_reference}:active:{eligibility.fingerprint}"
                ),
                evidence_fingerprint=eligibility.fingerprint,
                occurred_at=occurred_at,
                history_collection=self._history_collection,
                current_collection=self._current_collection,
                session=tx,
            )
        except Exception as error:
            raise TenantBrandingSubscriptionEntitlementComposerError(
                "D21C1_ENTITLEMENT_PERSISTENCE_REJECTED"
            ) from error
        return TenantBrandingSubscriptionEntitlementComposition(
            eligibility=eligibility,
            entitlement=activated.entitlement,
            creation_outcome=created.outcome,
            activation_outcome=activated.outcome,
        )


__all__ = [
    "VERSION",
    "TenantBrandingSubscriptionEntitlementComposer",
    "TenantBrandingSubscriptionEntitlementComposerError",
    "TenantBrandingSubscriptionEntitlementComposition",
]

# ARTIFACT: tenant_branding_subscription_entitlement_composer.py
# VERSION: v1.0.0-D21C1-TENANT-BRANDING-SUBSCRIPTION-ENTITLEMENT
# AUTHORITY BOUNDARY: subscription-derived D21B2B entitlement composition only
# TENANT POSTURE: exact tenant scope forwarded through every read/write
# FAIL-CLOSED POSTURE: ambiguous subscriptions, divergent replay and closed lifecycle reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
