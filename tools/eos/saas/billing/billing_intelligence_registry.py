"""WILSY OS M12-P6 durable billing-intelligence evidence registry.

TITLE: Durable Billing Intelligence Evidence Registry
VERSION: v1.1.0-M12-P6
AUTHORITY: Wilsy OS Core Governance
EPITOME: Persist and strictly hydrate immutable M12-P1 intelligence evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/billing_intelligence_registry.py
COLLABORATION / OWNERSHIP: Python EOS persistence owner for M12-P1 evidence;
                            the P1 engine owns derivation and callers own
                            sessions and transaction lifecycle.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.1.0-M12-P6 extends the strict durable schema with certified P5
           recurring-revenue evidence and rejects records from the prior
           schema rather than interpreting missing values as zero.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Stores opaque tenant/source evidence only; no
                             credentials, network, KMS, or provider access.
TENANT BOUNDARY: Every lookup and durable identity is explicitly tenant-scoped.
AUTHORITY BOUNDARY: Persistence and hydration only; P1 owns intelligence
                    derivation and no caller may replace canonical evidence.
FINANCIAL AUTHORITY BOUNDARY: No invoice mutation, payment, execution,
                              settlement, paid-state, closure, or refund.
TRANSACTION BOUNDARY: Caller owns ClientSession and transaction lifecycle.
FAIL-CLOSED DECLARATION: Corruption, divergence, unknown version, duplicate,
                         and cross-tenant access reject deterministically.
"""
from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
import hashlib
import json
import re
from typing import Any, Final

from pymongo.errors import DuplicateKeyError

from tools.eos.saas.billing.billing_intelligence_engine import (
    EVIDENCE_CONTRACT,
    BillingIntelligenceEvidence,
)
from tools.eos.saas.billing.recurring_revenue_policy import (
    EVIDENCE_CONTRACT as RECURRING_REVENUE_CONTRACT,
    RecurringRevenueEvidence,
    RecurringRevenueSource,
)


VERSION: Final[str] = "v1.1.0-M12-P6"
COLLECTION: Final[str] = "billing_intelligence_evidence"
_SHA3 = re.compile(r"^[0-9a-f]{128}$")
_RECORD_FIELDS = frozenset(
    {
        "tenant_id",
        "evidence_contract",
        "evidence_identity",
        "as_of",
        "receivable_count",
        "receivable_outstanding_amount_minor",
        "aging_evidence_count",
        "aging_by_bucket",
        "dunning_evidence_count",
        "dunning_by_stage",
        "source_provenance",
        "unsupported_outputs",
        "recurring_revenue",
        "evidence_fingerprint",
    }
)


class BillingIntelligenceRegistryError(RuntimeError):
    """Raised when durable billing-intelligence evidence is invalid or conflicts."""


def _require_tenant(value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise BillingIntelligenceRegistryError("M12P2_INVALID_TENANT")
    return value


def _canonical_identity(value: BillingIntelligenceEvidence) -> str:
    payload = {
        "as_of": value.as_of.isoformat() if value.as_of is not None else None,
        "evidence_contract": value.evidence_contract,
        "tenant_id": value.tenant_id,
    }
    return hashlib.sha3_512(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    ).hexdigest()


def _validate_provenance(value: object) -> tuple[tuple[str, str, str], ...]:
    if not isinstance(value, list):
        raise BillingIntelligenceRegistryError("M12P2_PROVENANCE_INVALID")
    result: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()
    for item in value:
        if not isinstance(item, list) or len(item) != 3 or not all(isinstance(part, str) for part in item):
            raise BillingIntelligenceRegistryError("M12P2_PROVENANCE_INVALID")
        source_type, source_id, fingerprint = item
        key = (source_type, source_id)
        if key in seen or not source_type or not source_id or not _SHA3.fullmatch(fingerprint):
            raise BillingIntelligenceRegistryError("M12P2_PROVENANCE_INVALID")
        seen.add(key)
        result.append((source_type, source_id, fingerprint))
    return tuple(result)


def _validate_pairs(value: object, allowed: set[str], code: str) -> tuple[tuple[str, int], ...]:
    if not isinstance(value, list):
        raise BillingIntelligenceRegistryError(code)
    result: list[tuple[str, int]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, list) or len(item) != 2:
            raise BillingIntelligenceRegistryError(code)
        name, count = item
        if not isinstance(name, str) or name not in allowed or name in seen or isinstance(count, bool) or not isinstance(count, int) or count < 0:
            raise BillingIntelligenceRegistryError(code)
        seen.add(name)
        result.append((name, count))
    if seen != allowed:
        raise BillingIntelligenceRegistryError(code)
    return tuple(result)


def _hydrate_recurring(value: object, tenant: str, as_of: datetime | None) -> RecurringRevenueEvidence | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise BillingIntelligenceRegistryError("M12P2_RECURRING_REVENUE_INVALID")
    expected = {
        "evidence_contract", "tenant_id", "as_of", "currency",
        "qualifying_subscription_count", "mrr_minor", "arr_minor", "sources", "fingerprint",
    }
    if set(value) != expected:
        raise BillingIntelligenceRegistryError("M12P2_RECURRING_REVENUE_SCHEMA_INVALID")
    raw_as_of = value["as_of"]
    if not isinstance(raw_as_of, str):
        raise BillingIntelligenceRegistryError("M12P2_RECURRING_REVENUE_INVALID")
    try:
        recurring_as_of = datetime.fromisoformat(raw_as_of)
        sources_raw = value["sources"]
        if not isinstance(sources_raw, list):
            raise ValueError("sources")
        sources = tuple(
            RecurringRevenueSource(
                subscription_id=item["subscription_id"],
                subscription_fingerprint=item["subscription_fingerprint"],
                plan_id=item["plan_id"],
                plan_catalogue_version=item["plan_catalogue_version"],
                amount_minor=item["amount_minor"],
                billing_frequency=item["billing_frequency"],
            )
            for item in sources_raw
            if isinstance(item, dict) and set(item) == {
                "subscription_id", "subscription_fingerprint", "plan_id",
                "plan_catalogue_version", "amount_minor", "billing_frequency",
            }
        )
        if len(sources) != len(sources_raw):
            raise ValueError("source schema")
        result = RecurringRevenueEvidence(
            tenant_id=value["tenant_id"],
            as_of=recurring_as_of,
            currency=value["currency"],
            qualifying_subscription_count=value["qualifying_subscription_count"],
            mrr_minor=value["mrr_minor"],
            arr_minor=value["arr_minor"],
            sources=sources,
            evidence_contract=value["evidence_contract"],
            fingerprint=value["fingerprint"],
        )
    except Exception as error:
        raise BillingIntelligenceRegistryError("M12P2_RECURRING_REVENUE_INVALID") from error
    if result.evidence_contract != RECURRING_REVENUE_CONTRACT or result.tenant_id != tenant:
        raise BillingIntelligenceRegistryError("M12P2_RECURRING_REVENUE_INVALID")
    if as_of is None or result.as_of != as_of.astimezone(result.as_of.tzinfo):
        raise BillingIntelligenceRegistryError("M12P2_RECURRING_REVENUE_AS_OF_INVALID")
    return result


def _hydrate(document: Mapping[str, Any]) -> BillingIntelligenceEvidence:
    payload = dict(document)
    payload.pop("_id", None)
    if set(payload) != _RECORD_FIELDS:
        raise BillingIntelligenceRegistryError("M12P2_RECORD_SCHEMA_INVALID")
    tenant = _require_tenant(payload["tenant_id"])
    if payload["evidence_contract"] != EVIDENCE_CONTRACT:
        raise BillingIntelligenceRegistryError("M12P2_EVIDENCE_VERSION_UNSUPPORTED")
    if not isinstance(payload["evidence_identity"], str) or not _SHA3.fullmatch(payload["evidence_identity"]):
        raise BillingIntelligenceRegistryError("M12P2_IDENTITY_INVALID")
    raw_as_of = payload["as_of"]
    if raw_as_of is not None and not isinstance(raw_as_of, str):
        raise BillingIntelligenceRegistryError("M12P2_AS_OF_INVALID")
    try:
        as_of = datetime.fromisoformat(raw_as_of) if raw_as_of is not None else None
    except ValueError as error:
        raise BillingIntelligenceRegistryError("M12P2_AS_OF_INVALID") from error
    if as_of is not None and as_of.tzinfo is None:
        raise BillingIntelligenceRegistryError("M12P2_AS_OF_INVALID")
    counts = ("receivable_count", "aging_evidence_count", "dunning_evidence_count")
    for name in counts:
        if isinstance(payload[name], bool) or not isinstance(payload[name], int) or payload[name] < 0:
            raise BillingIntelligenceRegistryError("M12P2_DERIVED_VALUE_INVALID")
    amount = payload["receivable_outstanding_amount_minor"]
    if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
        raise BillingIntelligenceRegistryError("M12P2_DERIVED_VALUE_INVALID")
    aging = _validate_pairs(payload["aging_by_bucket"], {"CURRENT", "1_30", "31_60", "61_90", "90_PLUS"}, "M12P2_AGING_INVALID")
    dunning = _validate_pairs(payload["dunning_by_stage"], {"NONE", "ELIGIBLE", "REMINDER", "ESCALATED"}, "M12P2_DUNNING_INVALID")
    provenance = _validate_provenance(payload["source_provenance"])
    unsupported = payload["unsupported_outputs"]
    if not isinstance(unsupported, list) or not all(isinstance(item, str) for item in unsupported):
        raise BillingIntelligenceRegistryError("M12P2_UNSUPPORTED_OUTPUTS_INVALID")
    fingerprint = payload["evidence_fingerprint"]
    if not isinstance(fingerprint, str) or not _SHA3.fullmatch(fingerprint):
        raise BillingIntelligenceRegistryError("M12P2_FINGERPRINT_INVALID")
    recurring = _hydrate_recurring(payload["recurring_revenue"], tenant, as_of)
    if as_of is not None and recurring is None:
        raise BillingIntelligenceRegistryError("M12P2_RECURRING_REVENUE_REQUIRED")
    try:
        value = BillingIntelligenceEvidence(
            tenant_id=tenant,
            evidence_contract=payload["evidence_contract"],
            as_of=as_of,
            receivable_count=payload["receivable_count"],
            receivable_outstanding_amount_minor=amount,
            aging_evidence_count=payload["aging_evidence_count"],
            aging_by_bucket=aging,
            dunning_evidence_count=payload["dunning_evidence_count"],
            dunning_by_stage=dunning,
            source_provenance=provenance,
            unsupported_outputs=tuple(unsupported),
            recurring_revenue=recurring,
            evidence_fingerprint=fingerprint,
        )
    except Exception as error:
        raise BillingIntelligenceRegistryError("M12P2_FINGERPRINT_CORRUPT") from error
    if payload["evidence_identity"] != _canonical_identity(value):
        raise BillingIntelligenceRegistryError("M12P2_IDENTITY_MISMATCH")
    return value


class BillingIntelligenceRegistry:
    """Persist and hydrate immutable M12-P1 evidence using caller resources."""

    @staticmethod
    def ensure_indexes(collection: Any) -> None:
        """Create only tenant-scoped immutable identity indexes."""
        collection.create_index(
            [("tenant_id", 1), ("evidence_identity", 1)],
            unique=True,
            name="tenant_billing_intelligence_identity_unique",
        )
        collection.create_index(
            [("tenant_id", 1), ("evidence_fingerprint", 1)],
            unique=True,
            name="tenant_billing_intelligence_fingerprint_unique",
        )

    @staticmethod
    def create(value: BillingIntelligenceEvidence, collection: Any, *, session: Any = None) -> BillingIntelligenceEvidence:
        """Persist evidence or return exact replay; never owns a transaction."""
        if not isinstance(value, BillingIntelligenceEvidence):
            raise BillingIntelligenceRegistryError("M12P2_EVIDENCE_REQUIRED")
        document = value.to_dict()
        document["evidence_identity"] = _canonical_identity(value)
        query = {"tenant_id": value.tenant_id, "evidence_identity": document["evidence_identity"]}
        existing = collection.find_one(query, session=session)
        if existing is not None:
            current = _hydrate(existing)
            if current.to_dict() == value.to_dict():
                return current
            raise BillingIntelligenceRegistryError("M12P2_REPLAY_CONFLICT")
        try:
            collection.insert_one(document, session=session)
        except DuplicateKeyError as error:
            if session is not None and getattr(session, "in_transaction", False):
                raise BillingIntelligenceRegistryError("M12P2_RETRY_TRANSACTION_REQUIRED") from error
            current = collection.find_one(query, session=session)
            if current is not None and _hydrate(current).to_dict() == value.to_dict():
                return _hydrate(current)
            raise BillingIntelligenceRegistryError("M12P2_REPLAY_CONFLICT") from error
        return _hydrate(collection.find_one(query, session=session) or document)

    @staticmethod
    def get(tenant_id: str, evidence_identity: str, collection: Any, *, session: Any = None) -> BillingIntelligenceEvidence:
        """Read one exact tenant-scoped evidence record and strictly hydrate it."""
        tenant = _require_tenant(tenant_id)
        if not isinstance(evidence_identity, str) or not _SHA3.fullmatch(evidence_identity):
            raise BillingIntelligenceRegistryError("M12P2_IDENTITY_INVALID")
        document = collection.find_one(
            {"tenant_id": tenant, "evidence_identity": evidence_identity}, session=session
        )
        if document is None:
            raise BillingIntelligenceRegistryError("M12P2_EVIDENCE_NOT_FOUND")
        value = _hydrate(document)
        if value.tenant_id != tenant:
            raise BillingIntelligenceRegistryError("M12P2_TENANT_MISMATCH")
        return value


__all__ = [
    "BillingIntelligenceRegistry",
    "BillingIntelligenceRegistryError",
    "COLLECTION",
    "VERSION",
]


# ARTIFACT: billing_intelligence_registry.py
# VERSION: v1.1.0-M12-P6
# AUTHORITY BOUNDARY: Persistence and strict hydration only.
# TENANT POSTURE: Every identity and lookup includes tenant_id.
# FAIL-CLOSED POSTURE: Corruption and replay divergence reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
