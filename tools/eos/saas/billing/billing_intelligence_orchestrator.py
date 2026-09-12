"""WILSY OS M12-P8 canonical billing-intelligence composition owner.

TITLE: Billing Intelligence Orchestrator
VERSION: v1.2.0-M12-P8
AUTHORITY: Wilsy OS Core Governance
EPITOME: Load canonical tenant evidence, invoke frozen P1 derivation, and
         persist/replay through the frozen P2 registry.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/billing_intelligence_orchestrator.py
COLLABORATION / OWNERSHIP: Python composition owner; P1 owns derivation, P2
                            owns durable evidence, and HTTP owns transport.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.2.0-M12-P8 accepts an explicit prior evidence identity and
           delegates exact growth derivation to the certified P7 owner.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Explicit tenant filters; no clients, providers,
                             secrets, KMS, or financial execution access.
TENANT BOUNDARY: Root/global tenant aliases are rejected; every source query
                 and persisted evidence record is tenant-scoped.
AUTHORITY BOUNDARY: Composition only; no new intelligence or financial truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution and
                               settlement truth.
TRANSACTION BOUNDARY: Caller supplies an optional session; this owner never
                      starts, commits, aborts, or ends a transaction.
FAIL-CLOSED DECLARATION: Missing/corrupt source evidence and persistence
                         conflicts reject rather than becoming empty success.
"""
from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any, Iterable

from tools.eos.saas.billing.billing_intelligence_engine import (
    BillingIntelligenceError,
    BillingIntelligenceEvidence,
    derive_billing_intelligence,
)
from tools.eos.saas.billing.billing_intelligence_registry import (
    BillingIntelligenceRegistry,
    BillingIntelligenceRegistryError,
    _canonical_identity,
)
from tools.eos.saas.billing.subscription_registry import (
    SubscriptionRegistry,
    SubscriptionRegistryError,
)
from tools.eos.saas.billing.recurring_revenue_policy import RecurringRevenuePolicyError
from tools.eos.saas.billing.recurring_revenue_growth_policy import (
    RecurringRevenueGrowthPolicyError,
    derive_recurring_revenue_growth,
)
from tools.eos.saas.billing.commercial_receivable_registry import (
    CommercialReceivableRegistry,
    CommercialReceivableRegistryError,
)
from tools.eos.saas.domain.commercial_receivable_aging import (
    AgingBucket,
    CommercialReceivableAging,
)
from tools.eos.saas.domain.commercial_receivable import ReceivableFamily
from tools.eos.saas.domain.commercial_receivable_dunning import (
    CommercialReceivableDunning,
    DunningStage,
)


_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_ROOT_TENANTS = frozenset({"MASTER", "GLOBAL_ROOT", "SOVEREIGN_ROOT"})
_AGING_FIELDS = frozenset(
    {
        "tenant_id",
        "receivable_family",
        "receivable_id",
        "source_invoice_id",
        "currency",
        "outstanding_amount_minor",
        "due_at",
        "as_of",
        "overdue_days",
        "bucket",
        "source_receivable_fingerprint",
        "aging_fingerprint",
    }
)
_DUNNING_FIELDS = frozenset(
    {
        "tenant_id",
        "receivable_family",
        "receivable_id",
        "aging_fingerprint",
        "outstanding_amount_minor",
        "stage",
        "effective_at",
        "dunning_fingerprint",
    }
)


class BillingIntelligenceOrchestratorError(RuntimeError):
    """Raised when canonical source composition cannot be proven."""


def _tenant(value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise BillingIntelligenceOrchestratorError("M12P3_TENANT_REQUIRED")
    if value.upper() in _ROOT_TENANTS:
        raise BillingIntelligenceOrchestratorError("M12P3_GLOBAL_TENANT_FORBIDDEN")
    return value


def parse_as_of(value: object) -> datetime:
    """Parse one explicit aware UTC snapshot timestamp; naive time is invalid."""
    if not isinstance(value, str) or not value.strip():
        raise BillingIntelligenceOrchestratorError("M12P3_AS_OF_REQUIRED")
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as error:
        raise BillingIntelligenceOrchestratorError("M12P3_AS_OF_INVALID") from error
    if parsed.tzinfo is None:
        raise BillingIntelligenceOrchestratorError("M12P3_AS_OF_INVALID")
    return parsed.astimezone(timezone.utc)


def _documents(collection: Any, tenant_id: str, session: Any) -> Iterable[dict[str, Any]]:
    if collection is None or not hasattr(collection, "find"):
        raise BillingIntelligenceOrchestratorError("M12P3_SOURCE_COLLECTION_REQUIRED")
    query = {"tenant_id": tenant_id}
    try:
        cursor = collection.find(query, session=session)
    except TypeError:
        cursor = collection.find(query)
    for document in cursor:
        if not isinstance(document, dict):
            raise BillingIntelligenceOrchestratorError("M12P3_SOURCE_DOCUMENT_INVALID")
        yield document


def _hydrate_aging(document: dict[str, Any]) -> CommercialReceivableAging:
    payload = dict(document)
    payload.pop("_id", None)
    if set(payload) != _AGING_FIELDS:
        raise BillingIntelligenceOrchestratorError("M12P3_AGING_CORRUPT")
    try:
        value = CommercialReceivableAging(
            tenant_id=payload["tenant_id"],
            receivable_family=ReceivableFamily(payload["receivable_family"]),
            receivable_id=payload["receivable_id"],
            source_invoice_id=payload["source_invoice_id"],
            currency=payload["currency"],
            outstanding_amount_minor=payload["outstanding_amount_minor"],
            due_at=datetime.fromisoformat(payload["due_at"]),
            as_of=datetime.fromisoformat(payload["as_of"]),
            overdue_days=payload["overdue_days"],
            bucket=AgingBucket(payload["bucket"]),
            source_receivable_fingerprint=payload["source_receivable_fingerprint"],
        )
    except Exception as error:
        raise BillingIntelligenceOrchestratorError("M12P3_AGING_CORRUPT") from error
    if not isinstance(payload["aging_fingerprint"], str) or not _SHA3.fullmatch(payload["aging_fingerprint"]):
        raise BillingIntelligenceOrchestratorError("M12P3_AGING_CORRUPT")
    if payload["aging_fingerprint"] != value.aging_fingerprint:
        raise BillingIntelligenceOrchestratorError("M12P3_AGING_CORRUPT")
    return value


def _hydrate_dunning(document: dict[str, Any]) -> CommercialReceivableDunning:
    payload = dict(document)
    payload.pop("_id", None)
    if set(payload) != _DUNNING_FIELDS:
        raise BillingIntelligenceOrchestratorError("M12P3_DUNNING_CORRUPT")
    try:
        value = CommercialReceivableDunning(
            tenant_id=payload["tenant_id"],
            receivable_family=payload["receivable_family"],
            receivable_id=payload["receivable_id"],
            aging_fingerprint=payload["aging_fingerprint"],
            outstanding_amount_minor=payload["outstanding_amount_minor"],
            stage=DunningStage(payload["stage"]),
            effective_at=datetime.fromisoformat(payload["effective_at"]),
        )
    except Exception as error:
        raise BillingIntelligenceOrchestratorError("M12P3_DUNNING_CORRUPT") from error
    if not isinstance(payload["dunning_fingerprint"], str) or not _SHA3.fullmatch(payload["dunning_fingerprint"]):
        raise BillingIntelligenceOrchestratorError("M12P3_DUNNING_CORRUPT")
    if payload["dunning_fingerprint"] != value.dunning_fingerprint:
        raise BillingIntelligenceOrchestratorError("M12P3_DUNNING_CORRUPT")
    return value


class BillingIntelligenceOrchestrator:
    """Compose canonical source evidence, P1 derivation, and P2 persistence."""

    __slots__ = (
        "_receivable_collection",
        "_aging_collection",
        "_dunning_collection",
        "_evidence_collection",
        "_subscription_collection",
    )

    def __init__(
        self,
        *,
        receivable_collection: Any,
        aging_collection: Any,
        dunning_collection: Any,
        evidence_collection: Any,
        subscription_collection: Any = None,
    ) -> None:
        if any(
            value is None
            for value in (
                receivable_collection,
                aging_collection,
                dunning_collection,
                evidence_collection,
            )
        ):
            raise BillingIntelligenceOrchestratorError("M12P3_COLLECTIONS_REQUIRED")
        self._receivable_collection = receivable_collection
        self._aging_collection = aging_collection
        self._dunning_collection = dunning_collection
        self._evidence_collection = evidence_collection
        self._subscription_collection = subscription_collection

    def collect_and_persist(
        self,
        tenant_id: str,
        *,
        as_of: datetime,
        session: Any = None,
        prior_evidence_identity: str | None = None,
    ) -> BillingIntelligenceEvidence:
        """Load, optionally compare, and persist one tenant evidence snapshot.

        ``prior_evidence_identity`` is an explicit tenant-scoped P2 identity.
        It is never inferred, replaced by a latest lookup, or synthesized from
        current subscriptions. The caller still owns the transaction/session.
        """
        tenant = _tenant(tenant_id)
        if not isinstance(as_of, datetime) or as_of.tzinfo is None:
            raise BillingIntelligenceOrchestratorError("M12P3_AS_OF_INVALID")
        prior: BillingIntelligenceEvidence | None = None
        if prior_evidence_identity is not None:
            try:
                prior = BillingIntelligenceRegistry.get(
                    tenant,
                    prior_evidence_identity,
                    self._evidence_collection,
                    session=session,
                )
            except BillingIntelligenceRegistryError as error:
                raise BillingIntelligenceOrchestratorError(str(error)) from error
            if prior.recurring_revenue is None:
                raise BillingIntelligenceOrchestratorError("M12P8_PRIOR_RECURRING_REVENUE_REQUIRED")
            prior_recurring = prior.recurring_revenue
            if prior.as_of is None or prior.as_of >= as_of.astimezone(timezone.utc):
                raise BillingIntelligenceOrchestratorError("M12P8_PRIOR_AS_OF_ORDER_INVALID")
        else:
            prior_recurring = None
        try:
            receivables = tuple(
                CommercialReceivableRegistry._hydrate(document)
                for document in _documents(self._receivable_collection, tenant, session)
            )
        except CommercialReceivableRegistryError as error:
            raise BillingIntelligenceOrchestratorError("M12P3_RECEIVABLE_CORRUPT") from error
        aging = tuple(
            _hydrate_aging(document)
            for document in _documents(self._aging_collection, tenant, session)
        )
        dunning = tuple(
            _hydrate_dunning(document)
            for document in _documents(self._dunning_collection, tenant, session)
        )
        try:
            subscriptions = (
                SubscriptionRegistry.list_entities(
                    tenant,
                    collection=self._subscription_collection,
                    session=session,
                )
                if self._subscription_collection is not None
                else ()
            )
        except SubscriptionRegistryError as error:
            raise BillingIntelligenceOrchestratorError("M12P3_SUBSCRIPTION_CORRUPT") from error
        if not receivables and not aging and not dunning and not subscriptions:
            raise BillingIntelligenceOrchestratorError("M12P3_SOURCE_EVIDENCE_UNAVAILABLE")
        try:
            evidence = derive_billing_intelligence(
                tenant_id=tenant,
                receivables=receivables,
                aging=aging,
                dunning=dunning,
                subscriptions=subscriptions,
                as_of=as_of,
            )
            growth = None
            if prior is not None:
                if evidence.recurring_revenue is None:
                    raise BillingIntelligenceOrchestratorError("M12P8_CURRENT_RECURRING_REVENUE_REQUIRED")
                if prior_recurring is None:
                    raise BillingIntelligenceOrchestratorError("M12P8_PRIOR_RECURRING_REVENUE_REQUIRED")
                growth = derive_recurring_revenue_growth(
                    prior=prior_recurring,
                    current=evidence.recurring_revenue,
                )
                evidence = derive_billing_intelligence(
                    tenant_id=tenant,
                    receivables=receivables,
                    aging=aging,
                    dunning=dunning,
                    subscriptions=subscriptions,
                    as_of=as_of,
                    recurring_revenue_growth=growth,
                )
            return BillingIntelligenceRegistry.create(
                evidence,
                self._evidence_collection,
                session=session,
            )
        except RecurringRevenueGrowthPolicyError as error:
            raise BillingIntelligenceOrchestratorError(str(error)) from error
        except (BillingIntelligenceError, RecurringRevenuePolicyError) as error:
            raise BillingIntelligenceOrchestratorError("M12P3_SUBSCRIPTION_CORRUPT") from error
        except BillingIntelligenceRegistryError as error:
            raise BillingIntelligenceOrchestratorError(str(error)) from error

    @staticmethod
    def response_payload(value: BillingIntelligenceEvidence) -> dict[str, object]:
        """Expose only frozen P1/P2 evidence plus its exact durable identity."""
        payload = value.to_dict()
        payload["evidence_identity"] = _canonical_identity(value)
        return payload


__all__ = [
    "BillingIntelligenceOrchestrator",
    "BillingIntelligenceOrchestratorError",
    "parse_as_of",
]


# ARTIFACT: billing_intelligence_orchestrator.py
# VERSION: v1.2.0-M12-P8
# AUTHORITY BOUNDARY: Canonical composition only; P1/P2 remain sovereign owners.
# TENANT POSTURE: Explicit tenant-only source queries; global aliases rejected.
# FAIL-CLOSED POSTURE: Source corruption and persistence conflicts reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
