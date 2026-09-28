"""WILSY OS tenant-branding entitlement currentness reconciliation.

TITLE: Tenant Branding Entitlement Reconciliation
VERSION: v1.0.0-D21C2-TENANT-BRANDING-ENTITLEMENT-RECONCILIATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Re-read canonical SubscriptionRegistry truth, derive the current
         D21C1 Branding VAS projection, and persist only a bounded D21B2
         commercial-loss transition under a caller-owned transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/tenant_branding_entitlement_reconciliation.py
COLLABORATION / OWNERSHIP: SubscriptionRegistry owns subscription truth;
                            D21C1 owns commercial eligibility; D21B2B owns
                            immutable entitlement persistence; the caller owns
                            Mongo transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-D21C2 freezes PAUSED/PAST_DUE as temporary suspension,
           CANCELLED/EXPIRED as terminal revocation, rejects trial and
           ambiguous commercial evidence, and records deterministic currentness
           evidence. Tier replacement terminates the old identity and requires
           a new entitlement lineage; no payment, profile, asset, IAM,
           browser, or Kennel authority is introduced.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Only canonical subscription proof and D21C1
                             evidence are consumed; payment secrets and
                             provider state are never read.
TENANT BOUNDARY: Subscription reads and entitlement persistence use the exact
                 admitted tenant and caller session.
AUTHORITY BOUNDARY: Currentness reconciliation only; caller cannot supply
                    status, tier, eligibility, target lifecycle, or policy.
FINANCIAL AUTHORITY BOUNDARY: No charge, release, execution, settlement or
                              payment-provider authority. Kennel EOS remains
                              exclusive.
TRANSACTION BOUNDARY: Requires an active caller-owned session and never starts,
                      commits, aborts, retries, or closes a transaction.
FAIL-CLOSED DECLARATION: Missing, corrupt, conflicting, stale, mismatched or
                          divergent evidence rejects without mutation.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
from typing import Any, Final

from tools.eos.saas.billing import tenant_branding_entitlement_registry
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistry
from tools.eos.saas.domain.subscription import SubscriptionEntity, SubscriptionStatus
from tools.eos.saas.domain.tenant_branding_commercial_eligibility import (
    TenantBrandingCommercialEligibility,
    TenantBrandingCommercialEligibilityError,
    TenantBrandingCommercialEligibilityState,
    derive_tenant_branding_commercial_eligibility,
)
from tools.eos.saas.domain.tenant_branding_entitlement import (
    TenantBrandingEntitlement,
    TenantBrandingEntitlementState,
)


VERSION: Final[str] = "v1.0.0-D21C2-TENANT-BRANDING-ENTITLEMENT-RECONCILIATION"


class TenantBrandingEntitlementReconciliationError(RuntimeError):
    """Raised when current commercial truth cannot be reconciled safely."""


class TenantBrandingEntitlementReconciliationOutcome(StrEnum):
    """Bounded read/transition outcomes; no outcome implies commercial approval."""

    CURRENT = "CURRENT"
    TRANSITIONED = "TRANSITIONED"
    IDEMPOTENT_REPLAY = "IDEMPOTENT_REPLAY"
    TERMINAL = "TERMINAL"


@dataclass(frozen=True, slots=True)
class TenantBrandingEntitlementReconciliationResult:
    """Deterministic result of one caller-owned currentness reconciliation."""

    outcome: TenantBrandingEntitlementReconciliationOutcome
    entitlement: TenantBrandingEntitlement
    eligibility: TenantBrandingCommercialEligibility
    target_state: TenantBrandingEntitlementState | None
    transition_evidence_fingerprint: str


def _active_transaction(session: Any) -> Any:
    """Require, but never acquire, the caller's active transaction."""
    if session is None:
        raise TenantBrandingEntitlementReconciliationError(
            "D21C2_ACTIVE_TRANSACTION_REQUIRED"
        )
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        raise TenantBrandingEntitlementReconciliationError(
            "D21C2_ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _text(name: str, value: object) -> str:
    """Require one explicit non-empty command coordinate."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise TenantBrandingEntitlementReconciliationError(
            f"D21C2_{name.upper()}_INVALID"
        )
    return value


def _when(name: str, value: object) -> datetime:
    """Require one timezone-aware lifecycle instant and normalize UTC."""
    parsed = value
    if isinstance(parsed, str):
        try:
            parsed = datetime.fromisoformat(parsed.replace("Z", "+00:00"))
        except ValueError as error:
            raise TenantBrandingEntitlementReconciliationError(
                f"D21C2_{name.upper()}_INVALID"
            ) from error
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        raise TenantBrandingEntitlementReconciliationError(
            f"D21C2_{name.upper()}_INVALID"
        )
    return parsed.astimezone(timezone.utc)


def _digest(payload: object) -> str:
    """Produce deterministic SHA3-512 transition evidence."""
    return hashlib.sha3_512(
        json.dumps(
            payload,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()


class TenantBrandingEntitlementReconciliationService:
    """Reconcile one D21B2 entitlement against fresh commercial truth.

    The service deliberately accepts no caller-supplied status, tier,
    eligibility or target state. It derives those values from a fresh
    SubscriptionRegistry snapshot and delegates all writes/CAS checks to the
    D21B2B registry under the caller-owned session.
    """

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
        """Bind injected read/write seams without opening clients or transactions."""
        if any(
            value is None
            for value in (
                subscription_collection,
                history_collection,
                current_collection,
                subscription_registry,
                entitlement_registry,
            )
        ):
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_PERSISTENCE_DEPENDENCY_REQUIRED"
            )
        self._subscription_registry = subscription_registry
        self._subscription_collection = subscription_collection
        self._entitlement_registry = entitlement_registry
        self._history_collection = history_collection
        self._current_collection = current_collection

    def reconcile(
        self,
        *,
        tenant_id: str,
        entitlement_id: str,
        evaluated_at: datetime,
        occurred_at: datetime,
        session: Any,
    ) -> TenantBrandingEntitlementReconciliationResult:
        """Derive currentness and persist at most one D21B2 terminal transition."""
        tx = _active_transaction(session)
        tenant = _text("tenant_id", tenant_id)
        identity = _text("entitlement_id", entitlement_id)
        evaluated = _when("evaluated_at", evaluated_at)
        occurred = _when("occurred_at", occurred_at)

        try:
            subscriptions = tuple(
                self._subscription_registry.list_entities(
                    tenant_id_header=tenant,
                    collection=self._subscription_collection,
                    session=tx,
                )
            )
        except Exception as error:
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_SUBSCRIPTION_READ_REJECTED"
            ) from error

        if any(type(item) is not SubscriptionEntity for item in subscriptions):
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_SUBSCRIPTION_SHAPE_INVALID"
            )
        try:
            projections = tuple(
                derive_tenant_branding_commercial_eligibility(
                    tenant_id=tenant,
                    subscription=item,
                    evaluated_at=evaluated,
                )
                for item in subscriptions
            )
        except TenantBrandingCommercialEligibilityError as error:
            raise TenantBrandingEntitlementReconciliationError(
                str(error)
            ) from error

        try:
            current = self._entitlement_registry.get_current(
                tenant,
                identity,
                self._history_collection,
                self._current_collection,
                session=tx,
            )
        except Exception as error:
            not_found = getattr(
                self._entitlement_registry,
                "TenantBrandingEntitlementRegistryNotFoundError",
                (),
            )
            if not_found and isinstance(error, not_found):
                raise TenantBrandingEntitlementReconciliationError(
                    "D21C2_ENTITLEMENT_NOT_FOUND"
                ) from error
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_ENTITLEMENT_READ_REJECTED"
            ) from error
        if type(current) is not TenantBrandingEntitlement:
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_ENTITLEMENT_SHAPE_INVALID"
            )
        if current.tenant_id != tenant:
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_TENANT_MISMATCH"
            )

        eligible = tuple(
            item
            for item in projections
            if item.state is TenantBrandingCommercialEligibilityState.ELIGIBLE
        )
        if len(eligible) > 1:
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_MULTIPLE_ELIGIBLE_BRANDING_SUBSCRIPTIONS"
            )

        matching = tuple(item for item in projections if item.branding_tier is not None)
        if len(matching) > 1:
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_AMBIGUOUS_BRANDING_SUBSCRIPTION"
            )
        if eligible and eligible[0].branding_tier is current.branding_tier:
            eligibility = eligible[0]
            evidence_source = (
                self._prior_active(current)
                if current.lifecycle_state
                in {TenantBrandingEntitlementState.SUSPENDED, TenantBrandingEntitlementState.REVOKED}
                else current
            )
            evidence = self._evidence(evidence_source, eligibility, evaluated)
            if current.lifecycle_state is TenantBrandingEntitlementState.ACTIVE:
                return TenantBrandingEntitlementReconciliationResult(
                    TenantBrandingEntitlementReconciliationOutcome.CURRENT,
                    current,
                    eligibility,
                    None,
                    evidence,
                )
            return self._terminal_replay_or_conflict(
                current, eligibility, None, evidence
            )

        if len(matching) != 1:
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_NO_EXACT_BRANDING_SUBSCRIPTION"
            )
        eligibility = matching[0]
        status = eligibility.subscription_status
        if status is SubscriptionStatus.TRIAL:
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_TRIAL_EXISTING_ACTIVE_FAIL_CLOSED"
            )
        if eligibility.branding_tier is not current.branding_tier:
            # A tier replacement always closes the old identity. A fresh
            # entitlement lineage must be composed for the new tier.
            target = TenantBrandingEntitlementState.REVOKED
        elif status in {SubscriptionStatus.PAUSED, SubscriptionStatus.PAST_DUE}:
            target = TenantBrandingEntitlementState.SUSPENDED
        elif status in {SubscriptionStatus.CANCELLED, SubscriptionStatus.EXPIRED}:
            target = TenantBrandingEntitlementState.REVOKED
        elif status is SubscriptionStatus.ACTIVE:
            target = TenantBrandingEntitlementState.REVOKED
        else:
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_COMMERCIAL_POSTURE_UNKNOWN"
            )

        evidence_source = (
            self._prior_active(current)
            if current.lifecycle_state
            in {TenantBrandingEntitlementState.SUSPENDED, TenantBrandingEntitlementState.REVOKED}
            else current
        )
        evidence = self._evidence(evidence_source, eligibility, evaluated)
        if current.lifecycle_state is not TenantBrandingEntitlementState.ACTIVE:
            return self._terminal_replay_or_conflict(
                current, eligibility, target, evidence
            )
        reference = (
            "subscription-branding-currentness:"
            f"{tenant}/{identity}/{current.lifecycle_revision}/{status.value}/{target.value}"
        )
        try:
            persisted = self._entitlement_registry.transition(
                tenant_id=tenant,
                entitlement_id=identity,
                target_state=target,
                expected_revision=current.lifecycle_revision,
                evidence_reference=reference,
                evidence_fingerprint=evidence,
                occurred_at=occurred,
                history_collection=self._history_collection,
                current_collection=self._current_collection,
                session=tx,
            )
        except Exception as error:
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_ENTITLEMENT_TRANSITION_REJECTED"
            ) from error
        result_entitlement = getattr(persisted, "entitlement", None)
        if type(result_entitlement) is not TenantBrandingEntitlement:
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_TRANSITION_RESULT_INVALID"
            )
        return TenantBrandingEntitlementReconciliationResult(
            TenantBrandingEntitlementReconciliationOutcome.TRANSITIONED,
            result_entitlement,
            eligibility,
            target,
            evidence,
        )

    @staticmethod
    def _evidence(
        entitlement: TenantBrandingEntitlement,
        eligibility: TenantBrandingCommercialEligibility,
        evaluated_at: datetime,
    ) -> str:
        """Bind current commercial truth and previous D21B2 revision exactly."""
        return _digest(
            {
                "tenant_id": entitlement.tenant_id,
                "entitlement_id": entitlement.entitlement_id,
                "entitlement_revision": entitlement.lifecycle_revision,
                "previous_entitlement_fingerprint": entitlement.fingerprint,
                "subscription_id": eligibility.subscription_id,
                "plan_id": eligibility.plan_id,
                "plan_catalogue_version": eligibility.plan_catalogue_version,
                "catalogue_fingerprint": eligibility.catalogue_fingerprint,
                "branding_vas_id": eligibility.branding_vas_id,
                "branding_tier": eligibility.branding_tier.value if eligibility.branding_tier else None,
                "subscription_status": eligibility.subscription_status.value,
                "evaluated_at": evaluated_at.isoformat().replace("+00:00", "Z"),
                "eligibility_fingerprint": eligibility.fingerprint,
            }
        )

    @staticmethod
    def _prior_active(entitlement: TenantBrandingEntitlement) -> TenantBrandingEntitlement:
        """Reconstruct the immutable ACTIVE predecessor for replay evidence."""
        if entitlement.lifecycle_revision < 1:
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_PRIOR_REVISION_INVALID"
            )
        return TenantBrandingEntitlement(
            tenant_id=entitlement.tenant_id,
            entitlement_id=entitlement.entitlement_id,
            branding_tier=entitlement.branding_tier,
            policy_fingerprint=entitlement.policy_fingerprint,
            lifecycle_state=TenantBrandingEntitlementState.ACTIVE,
            source_evidence_reference=entitlement.source_evidence_reference,
            source_evidence_fingerprint=entitlement.source_evidence_fingerprint,
            activated_at=entitlement.activated_at,
            activation_evidence_reference=entitlement.activation_evidence_reference,
            activation_evidence_fingerprint=entitlement.activation_evidence_fingerprint,
            lifecycle_revision=entitlement.lifecycle_revision - 1,
        )

    @staticmethod
    def _terminal_replay_or_conflict(
        current: TenantBrandingEntitlement,
        eligibility: TenantBrandingCommercialEligibility,
        target: TenantBrandingEntitlementState | None,
        evidence: str,
    ) -> TenantBrandingEntitlementReconciliationResult:
        """Recognize exact terminal replay; reject divergent stale evidence."""
        stored = (
            current.suspension_evidence_fingerprint
            if current.lifecycle_state is TenantBrandingEntitlementState.SUSPENDED
            else current.revocation_evidence_fingerprint
        )
        if stored == evidence:
            return TenantBrandingEntitlementReconciliationResult(
                TenantBrandingEntitlementReconciliationOutcome.IDEMPOTENT_REPLAY,
                current,
                eligibility,
                target,
                evidence,
            )
        if current.lifecycle_state in {
            TenantBrandingEntitlementState.SUSPENDED,
            TenantBrandingEntitlementState.REVOKED,
        }:
            raise TenantBrandingEntitlementReconciliationError(
                "D21C2_DIVERGENT_TERMINAL_REPLAY"
            )
        raise TenantBrandingEntitlementReconciliationError(
            "D21C2_TERMINAL_STATE_INVALID"
        )


__all__ = [
    "TenantBrandingEntitlementReconciliationError",
    "TenantBrandingEntitlementReconciliationOutcome",
    "TenantBrandingEntitlementReconciliationResult",
    "TenantBrandingEntitlementReconciliationService",
    "VERSION",
]

# ARTIFACT: tenant_branding_entitlement_reconciliation.py
# VERSION: v1.0.0-D21C2-TENANT-BRANDING-ENTITLEMENT-RECONCILIATION
# AUTHORITY BOUNDARY: derived currentness transition only; no profile, IAM or financial authority
# TENANT POSTURE: exact tenant and caller-owned session on every read/write
# FAIL-CLOSED POSTURE: ambiguity, corruption, stale state and divergent replay reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
