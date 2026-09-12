"""WILSY OS M12-P1 canonical billing-intelligence evidence engine.

TITLE: Canonical Billing Intelligence Evidence Engine
VERSION: v1.0.0-M12-P1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Derive deterministic, tenant-scoped billing evidence from immutable
         Python commercial objects without persistence or financial execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/billing_intelligence_engine.py
COLLABORATION / OWNERSHIP: Python EOS billing-intelligence derivation owner;
                            Node remains transport/projection and Kennel EOS
                            remains exclusive financial execution authority.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0-M12-P1 establishes immutable receivable/aging/dunning
           evidence, provenance binding, deterministic SHA3-512 fingerprints,
           strict tenant isolation, and fail-closed duplicate handling.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque tenant and source identities only; no
                             credentials, network, Mongo, KMS, or providers.
TENANT BOUNDARY: Every source object must belong to the explicit tenant_id.
AUTHORITY BOUNDARY: Pure commercial intelligence evidence only; no caller
                    supplied financial truth, authorization, or mutation.
FINANCIAL AUTHORITY BOUNDARY: No payment, execution, settlement, paid-state,
                              receivable closure, refund, or invoice mutation.
FAIL-CLOSED DECLARATION: Invalid identity, provenance, duplicate source,
                         mixed tenant, or unsupported input rejects.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from collections.abc import Sequence
from typing import Final

from tools.eos.saas.domain.commercial_receivable import (
    CommercialReceivable,
)
from tools.eos.saas.domain.commercial_receivable_aging import (
    AgingBucket,
    CommercialReceivableAging,
)
from tools.eos.saas.domain.commercial_receivable_dunning import (
    CommercialReceivableDunning,
    DunningStage,
)


VERSION: Final[str] = "v1.0.0-M12-P1"
EVIDENCE_CONTRACT: Final[str] = "WILSY-BILLING-INTELLIGENCE-EVIDENCE/V1"
UNSUPPORTED_INTELLIGENCE_OUTPUTS: Final[tuple[str, ...]] = (
    "arr",
    "arpu",
    "churn_rate",
    "growth_rate",
    "next_month_forecast",
    "next_quarter_forecast",
    "annual_projection",
    "credit_score",
    "anomaly_score",
)
_AGING_BUCKETS: Final[tuple[AgingBucket, ...]] = tuple(AgingBucket)
_DUNNING_STAGES: Final[tuple[DunningStage, ...]] = tuple(DunningStage)


class BillingIntelligenceError(ValueError):
    """Raised when canonical billing-intelligence evidence is invalid."""


def _tenant(value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise BillingIntelligenceError("M12P1_INVALID_TENANT")
    return value


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise BillingIntelligenceError("M12P1_INVALID_AS_OF")
    return value.astimezone(timezone.utc)


def _source_key(value: object) -> tuple[str, str]:
    if isinstance(value, CommercialReceivable):
        return ("commercial_receivable", f"{value.receivable_family.value}:{value.receivable_id}")
    if isinstance(value, CommercialReceivableAging):
        return ("commercial_receivable_aging", f"{value.receivable_family.value}:{value.receivable_id}")
    if isinstance(value, CommercialReceivableDunning):
        return ("commercial_receivable_dunning", f"{value.receivable_family}:{value.receivable_id}")
    raise BillingIntelligenceError("M12P1_UNSUPPORTED_SOURCE_TYPE")


def _source_provenance(value: object) -> tuple[str, str, str]:
    if isinstance(value, CommercialReceivable):
        return ("commercial_receivable", value.receivable_id, value.receivable_fingerprint)
    if isinstance(value, CommercialReceivableAging):
        return ("commercial_receivable_aging", value.receivable_id, value.aging_fingerprint)
    if isinstance(value, CommercialReceivableDunning):
        return ("commercial_receivable_dunning", value.receivable_id, value.dunning_fingerprint)
    raise BillingIntelligenceError("M12P1_UNSUPPORTED_SOURCE_TYPE")


def _validate_sources(
    tenant_id: str,
    values: Sequence[object],
) -> None:
    seen: set[tuple[str, str]] = set()
    for value in values:
        key = _source_key(value)
        if key in seen:
            raise BillingIntelligenceError("M12P1_DUPLICATE_SOURCE")
        seen.add(key)
        if getattr(value, "tenant_id", None) != tenant_id:
            raise BillingIntelligenceError("M12P1_MIXED_TENANT")


def _canonical_bytes(payload: dict[str, object]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


@dataclass(frozen=True, slots=True)
class BillingIntelligenceEvidence:
    """Immutable deterministic summary and source provenance for one tenant.

    This value is a projection of supplied canonical objects only. It owns no
    persistence and cannot assert execution, settlement, payment, paid state,
    or receivable closure. Its fingerprint excludes wall-clock generation time.
    """

    tenant_id: str
    evidence_contract: str
    as_of: datetime | None
    receivable_count: int
    receivable_outstanding_amount_minor: int
    aging_evidence_count: int
    aging_by_bucket: tuple[tuple[str, int], ...]
    dunning_evidence_count: int
    dunning_by_stage: tuple[tuple[str, int], ...]
    source_provenance: tuple[tuple[str, str, str], ...]
    unsupported_outputs: tuple[str, ...]
    evidence_fingerprint: str

    def __post_init__(self) -> None:
        _tenant(self.tenant_id)
        if self.evidence_contract != EVIDENCE_CONTRACT:
            raise BillingIntelligenceError("M12P1_EVIDENCE_CONTRACT_INVALID")
        _aware(self.as_of)
        if self.receivable_count < 0 or self.aging_evidence_count < 0 or self.dunning_evidence_count < 0:
            raise BillingIntelligenceError("M12P1_NEGATIVE_COUNT")
        if self.receivable_outstanding_amount_minor < 0:
            raise BillingIntelligenceError("M12P1_NEGATIVE_OUTSTANDING")
        if self.unsupported_outputs != UNSUPPORTED_INTELLIGENCE_OUTPUTS:
            raise BillingIntelligenceError("M12P1_UNSUPPORTED_OUTPUTS_MUTATED")
        if self.evidence_fingerprint != self.compute_fingerprint():
            raise BillingIntelligenceError("M12P1_FINGERPRINT_MISMATCH")

    def to_dict(self, *, include_fingerprint: bool = True) -> dict[str, object]:
        """Return the fixed canonical evidence representation."""
        payload: dict[str, object] = {
            "as_of": self.as_of.isoformat() if self.as_of is not None else None,
            "aging_by_bucket": [list(item) for item in self.aging_by_bucket],
            "aging_evidence_count": self.aging_evidence_count,
            "dunning_by_stage": [list(item) for item in self.dunning_by_stage],
            "dunning_evidence_count": self.dunning_evidence_count,
            "evidence_contract": self.evidence_contract,
            "receivable_count": self.receivable_count,
            "receivable_outstanding_amount_minor": self.receivable_outstanding_amount_minor,
            "source_provenance": [list(item) for item in self.source_provenance],
            "tenant_id": self.tenant_id,
            "unsupported_outputs": list(self.unsupported_outputs),
        }
        if include_fingerprint:
            payload["evidence_fingerprint"] = self.evidence_fingerprint
        return payload

    def compute_fingerprint(self) -> str:
        """Compute lowercase SHA3-512 over canonical evidence bytes."""
        return hashlib.sha3_512(_canonical_bytes(self.to_dict(include_fingerprint=False))).hexdigest()


def derive_billing_intelligence(
    *,
    tenant_id: str,
    receivables: Sequence[CommercialReceivable] = (),
    aging: Sequence[CommercialReceivableAging] = (),
    dunning: Sequence[CommercialReceivableDunning] = (),
    as_of: datetime | None = None,
) -> BillingIntelligenceEvidence:
    """Derive tenant-scoped receivable, aging, and dunning evidence.

    Inputs are already-certified immutable Python values. The caller supplies
    explicit tenant scope and optional canonical ``as_of`` semantics; no tenant
    or financial fact is inferred from transport, providers, or persistence.
    Duplicate identities, mixed tenants, and broken receivable→aging→dunning
    provenance fail closed before any result is constructed.
    """
    tenant = _tenant(tenant_id)
    normalized_as_of = _aware(as_of)
    _validate_sources(tenant, (*receivables, *aging, *dunning))

    receivable_by_identity: dict[tuple[str, str], CommercialReceivable] = {}
    for value in receivables:
        identity = (value.receivable_family.value, value.receivable_id)
        receivable_by_identity[identity] = value

    aging_by_identity: dict[tuple[str, str], CommercialReceivableAging] = {}
    for value in aging:
        identity = (value.receivable_family.value, value.receivable_id)
        source = receivable_by_identity.get(identity)
        if source is None or value.source_receivable_fingerprint != source.receivable_fingerprint:
            raise BillingIntelligenceError("M12P1_AGING_PROVENANCE_DRIFT")
        aging_by_identity[identity] = value

    for value in dunning:
        identity = (value.receivable_family, value.receivable_id)
        source = aging_by_identity.get(identity)
        if source is None or value.aging_fingerprint != source.aging_fingerprint:
            raise BillingIntelligenceError("M12P1_DUNNING_PROVENANCE_DRIFT")

    aging_counts = {bucket.value: 0 for bucket in _AGING_BUCKETS}
    for value in aging:
        aging_counts[value.bucket.value] += 1
    dunning_counts = {stage.value: 0 for stage in _DUNNING_STAGES}
    for value in dunning:
        dunning_counts[value.stage.value] += 1

    all_sources = tuple((*receivables, *aging, *dunning))
    provenance = tuple(sorted((_source_provenance(value) for value in all_sources)))
    aging_summary = tuple((bucket.value, aging_counts[bucket.value]) for bucket in _AGING_BUCKETS)
    dunning_summary = tuple((stage.value, dunning_counts[stage.value]) for stage in _DUNNING_STAGES)
    evidence_fields: dict[str, object] = {
        "as_of": normalized_as_of.isoformat() if normalized_as_of is not None else None,
        "aging_by_bucket": [list(item) for item in aging_summary],
        "aging_evidence_count": len(aging),
        "dunning_by_stage": [list(item) for item in dunning_summary],
        "dunning_evidence_count": len(dunning),
        "evidence_contract": EVIDENCE_CONTRACT,
        "receivable_count": len(receivables),
        "receivable_outstanding_amount_minor": sum(value.outstanding_amount_minor for value in receivables),
        "source_provenance": [list(item) for item in provenance],
        "tenant_id": tenant,
        "unsupported_outputs": list(UNSUPPORTED_INTELLIGENCE_OUTPUTS),
    }
    fingerprint = hashlib.sha3_512(_canonical_bytes(evidence_fields)).hexdigest()
    evidence = BillingIntelligenceEvidence(
        tenant_id=tenant,
        evidence_contract=EVIDENCE_CONTRACT,
        as_of=normalized_as_of,
        receivable_count=len(receivables),
        receivable_outstanding_amount_minor=sum(value.outstanding_amount_minor for value in receivables),
        aging_evidence_count=len(aging),
        aging_by_bucket=aging_summary,
        dunning_evidence_count=len(dunning),
        dunning_by_stage=dunning_summary,
        source_provenance=provenance,
        unsupported_outputs=UNSUPPORTED_INTELLIGENCE_OUTPUTS,
        evidence_fingerprint=fingerprint,
    )
    return evidence


__all__ = [
    "BillingIntelligenceError",
    "BillingIntelligenceEvidence",
    "EVIDENCE_CONTRACT",
    "UNSUPPORTED_INTELLIGENCE_OUTPUTS",
    "VERSION",
    "derive_billing_intelligence",
]


# ARTIFACT: billing_intelligence_engine.py
# VERSION: v1.0.0-M12-P1
# AUTHORITY BOUNDARY: Pure tenant-scoped commercial evidence derivation only.
# TENANT POSTURE: Explicit tenant required; mixed tenants fail closed.
# FAIL-CLOSED POSTURE: Invalid, duplicate, or drifted provenance rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
