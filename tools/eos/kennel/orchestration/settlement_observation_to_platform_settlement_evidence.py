"""WILSY OS — M11E2D5R2 durable settlement-observation bridge.
TITLE: Settlement Observation to Platform Settlement Evidence
VERSION: v1.0.0-M11E2D5R2
AUTHORITY: Kennel EOS / Wilsy OS Core Governance
EPITOME: Derives full settlement evidence only from durable correlated records.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/orchestration/settlement_observation_to_platform_settlement_evidence.py
COLLABORATION / OWNERSHIP: Kennel EOS settlement-evidence owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11E2D5R2 adds canonical observation provenance bridge.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: opaque references only.
TENANT BOUNDARY: all registry reads/writes are tenant-scoped.
AUTHORITY BOUNDARY: durable evidence derivation only.
FINANCIAL AUTHORITY BOUNDARY: no provider, paid, or receivable mutation.
TRANSACTION BOUNDARY: caller-owned session and transaction.
FAIL-CLOSED DECLARATION: mismatched, partial, corrupt, or non-executed inputs reject.
"""
from datetime import datetime
from typing import Optional, cast
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from ..registry.financial_settlement_observation_registry import FinancialSettlementObservationRegistry
from ..registry.financial_execution_registry import FinancialExecutionFactRegistry
from ..registry.platform_billing_financial_execution_truth_registry import PlatformBillingFinancialExecutionTruthRegistry
from ..registry.platform_billing_financial_settlement_evidence_registry import PlatformBillingFinancialSettlementEvidenceRegistry
from ..domain.financial_execution import FinancialExecutionStatus
from ..domain.financial_execution import FinancialExecutionTruth
from ..domain.platform_billing_financial_execution_truth import PlatformBillingFinancialExecutionTruth
from ..domain.platform_billing_financial_execution_truth import PlatformExecutionStatus
from ..domain.platform_billing_financial_settlement_evidence import PlatformBillingFinancialSettlementEvidence

class SettlementObservationBridgeError(RuntimeError):
    """Fail-closed settlement provenance error."""

def bridge_settlement_observation_to_platform_evidence(tenant_id: str, observation_id: str, platform_truth_id: str, *, observation_collection: Collection, generic_truth_collection: Collection, platform_truth_collection: Collection, evidence_collection: Collection, session: Optional[ClientSession] = None, created_at: datetime) -> PlatformBillingFinancialSettlementEvidence:
    """Hydrate durable observation/truth records and persist full evidence."""
    if session is None or not bool(getattr(session, 'in_transaction', False)):
        raise SettlementObservationBridgeError('M11E2D5R2_ACTIVE_SESSION_REQUIRED')
    observation = FinancialSettlementObservationRegistry.get(tenant_id, observation_id, observation_collection, session=session)
    generic = FinancialExecutionFactRegistry.get(tenant_id, observation.execution_truth_id, generic_truth_collection, session=session)
    platform = cast(PlatformBillingFinancialExecutionTruth, PlatformBillingFinancialExecutionTruthRegistry.get(tenant_id, platform_truth_id, platform_truth_collection, session=session))
    if generic.execution_status is not FinancialExecutionStatus.EXECUTED or platform.execution_status is not PlatformExecutionStatus.EXECUTED:
        raise SettlementObservationBridgeError('EXECUTED_TRUTH_REQUIRED')
    if platform.source_financial_execution_truth_id != generic.execution_fact_id or platform.source_financial_execution_truth_fingerprint != generic.fingerprint:
        raise SettlementObservationBridgeError('GENERIC_PLATFORM_PROVENANCE_MISMATCH')
    if (observation.tenant_id, observation.provider_name, observation.provider_execution_reference, observation.currency, observation.payment_destination_reference, observation.settled_amount_minor) != (generic.tenant_id, generic.provider, generic.provider_execution_reference, generic.currency, generic.payment_destination_reference, generic.executed_amount_minor):
        raise SettlementObservationBridgeError('SETTLEMENT_EXECUTION_MISMATCH')
    if observation.settled_amount_minor != platform.executed_amount_minor:
        raise SettlementObservationBridgeError('PARTIAL_SETTLEMENT_NOT_PLATFORM_FULL_EVIDENCE')
    value = PlatformBillingFinancialSettlementEvidence.from_execution_truth(platform, observation.settlement_reference, observation.provider_settlement_evidence_reference, observation.settled_at, created_at, source_financial_settlement_observation_id=observation.observation_id, source_financial_settlement_observation_fingerprint=observation.fingerprint)
    return PlatformBillingFinancialSettlementEvidenceRegistry.create(value, evidence_collection, session=session)

# ARTIFACT: settlement_observation_to_platform_settlement_evidence.py
# VERSION: v1.0.0-M11E2D5R2
# AUTHORITY BOUNDARY: durable settlement evidence only.
# TENANT POSTURE: tenant-scoped caller-session-bound.
# FAIL-CLOSED POSTURE: mismatches and partial settlement reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
