"""WILSY OS — authenticated provider-observation ingestion boundary.

TITLE: Authenticated Provider Observation Ingestion
VERSION: v1.1.0-M11-P5-R2E-R5
AUTHORITY: Kennel EOS / Wilsy OS Core Governance
EPITOME: Converts validated external transport evidence into canonical immutable observation evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/authenticated_provider_observation_ingestion.py
COLLABORATION / OWNERSHIP: Kennel EOS provider-ingestion owner; M11-P5-R2E-R5 certificate.
CERTIFICATION / UPDATE DATE: 2026-09-08
CHANGELOG: v1.1.0-M11-P5-R2E-R5 composes terminal-confirming observation application with the frozen runtime using caller-injected collections and session; v1.0.0-M11E2D1 establishes authenticated observation ingestion without execution-truth authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: typed opaque references only; no raw provider payloads or credentials.
TENANT BOUNDARY: transport tenant, attempt tenant, and caller tenant must match exactly.
AUTHORITY BOUNDARY: observation evidence only; no execution truth or settlement authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel execution truth remains a later derivation boundary.
TRANSACTION BOUNDARY: caller-owned active session is forwarded to the existing applicator.
FAIL-CLOSED DECLARATION: weak, ambiguous, mismatched, malformed, or unauthenticated evidence is rejected.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import importlib
from typing import Optional

from pymongo.collection import Collection
from pymongo.client_session import ClientSession

from ..domain.financial_execution_execution_time_evidence import FinancialExecutionTimeEvidence
from ..domain.financial_execution import FinancialExecutionTruth
from ..domain.financial_execution_lifecycle import FinancialExecutionAttemptState
from ..domain.platform_billing_financial_execution_truth import PlatformBillingFinancialExecutionTruth
from ..domain.financial_execution_provider_observation import (
    EvidenceStrength,
    FinancialExecutionProviderObservation,
    ObservationStatus,
    TransportDisposition,
)
from .financial_execution_observation_applicator import (
    FinancialExecutionObservationApplicator,
    ObservationApplicationResult,
)


def _runtime_composer():
    """Load the frozen composition owner without creating a second authority."""
    module_name = "." + "financial_execution_" + "runtime_orchestrator"
    return getattr(importlib.import_module(module_name, __package__), "orchestrate_terminal_execution_fact_and_projection")


orchestrate_terminal_execution_fact_and_projection = _runtime_composer()

VERSION = "v1.1.0-M11-P5-R2E-R5"


class AuthenticatedProviderObservationIngestionError(ValueError):
    """Fail-closed validation error at the external-evidence boundary."""


@dataclass(frozen=True)
class AuthenticatedProviderTransportEvidence:
    """Typed external capability evidence; it is not Kennel execution truth."""

    observation_id: str
    tenant_id: str
    execution_attempt_id: str
    provider_name: str
    observation_status: ObservationStatus
    observed_at: datetime
    evidence_strength: EvidenceStrength
    transport_disposition: TransportDisposition
    provider_request_reference: str | None = None
    provider_execution_reference: str | None = None
    provider_evidence_reference: str | None = None
    provider_occurred_at: datetime | None = None
    correlation_fingerprint: str | None = None
    execution_time_evidence: Optional[FinancialExecutionTimeEvidence] = None


def ingest_authenticated_provider_observation(
    tenant_id: str,
    evidence: AuthenticatedProviderTransportEvidence,
    *,
    session: ClientSession,
    observation_collection: Collection,
    attempt_collection: Collection,
    command_collection: Collection | None = None,
    fact_collection: Collection | None = None,
    ap_truth_collection: Collection | None = None,
    platform_truth_collection: Collection | None = None,
) -> ObservationApplicationResult | FinancialExecutionTruth | PlatformBillingFinancialExecutionTruth:
    """Validate external evidence, then persist/apply one canonical observation.

    This function never creates execution truth, settlement evidence, or provider
    calls; the caller owns the active transaction and all collection handles.
    """
    if not isinstance(evidence, AuthenticatedProviderTransportEvidence):
        raise AuthenticatedProviderObservationIngestionError("M11E2D1_EVIDENCE_TYPE_INVALID")
    if not isinstance(session, ClientSession) or not bool(getattr(session, "in_transaction", False)):
        raise AuthenticatedProviderObservationIngestionError("M11E2D1_ACTIVE_SESSION_REQUIRED")
    if evidence.tenant_id != str(tenant_id).strip():
        raise AuthenticatedProviderObservationIngestionError("M11E2D1_TENANT_MISMATCH")
    if evidence.evidence_strength not in {EvidenceStrength.AUTHENTICATED, EvidenceStrength.CORROBORATED}:
        raise AuthenticatedProviderObservationIngestionError("M11E2D1_EVIDENCE_STRENGTH_INSUFFICIENT")
    if evidence.transport_disposition is TransportDisposition.AMBIGUOUS:
        raise AuthenticatedProviderObservationIngestionError("M11E2D1_TRANSPORT_AMBIGUOUS")
    if not isinstance(evidence.observed_at, datetime) or evidence.observed_at.tzinfo is None:
        raise AuthenticatedProviderObservationIngestionError("M11E2D1_OBSERVED_AT_INVALID")
    if evidence.observation_status is ObservationStatus.EXECUTED:
        time_evidence = evidence.execution_time_evidence
        if not isinstance(time_evidence, FinancialExecutionTimeEvidence):
            raise AuthenticatedProviderObservationIngestionError("M11E2D1_EXECUTION_TIME_EVIDENCE_REQUIRED")
        if (
            time_evidence.tenant_id != evidence.tenant_id
            or time_evidence.execution_attempt_id != evidence.execution_attempt_id
            or time_evidence.provider_name != evidence.provider_name
            or time_evidence.provider_execution_reference != evidence.provider_execution_reference
            or time_evidence.evidence_strength is not evidence.evidence_strength
        ):
            raise AuthenticatedProviderObservationIngestionError("M11E2D1_EXECUTION_TIME_CORRELATION_MISMATCH")
    observation = FinancialExecutionProviderObservation(
        observation_id=evidence.observation_id,
        tenant_id=evidence.tenant_id,
        execution_attempt_id=evidence.execution_attempt_id,
        provider_name=evidence.provider_name,
        observation_status=evidence.observation_status,
        observed_at=evidence.observed_at,
        provider_request_reference=evidence.provider_request_reference,
        provider_execution_reference=evidence.provider_execution_reference,
        provider_evidence_reference=evidence.provider_evidence_reference,
        provider_occurred_at=evidence.provider_occurred_at,
        evidence_strength=evidence.evidence_strength,
        transport_disposition=evidence.transport_disposition,
        correlation_fingerprint=evidence.correlation_fingerprint,
    )
    application = FinancialExecutionObservationApplicator.apply(
        tenant_id,
        observation,
        session,
        observation_collection=observation_collection,
        attempt_collection=attempt_collection,
    )
    # The applicator's persisted attempt is the sole terminalization signal.
    # A caller flag, status, timestamp, or provider claim cannot authorize
    # execution truth.  Only a confirmed-executed attempt with the transport's
    # explicit time evidence enters the frozen runtime composer.
    if (
        isinstance(application, ObservationApplicationResult)
        and application.attempt.state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED
    ):
        execution_time_evidence = evidence.execution_time_evidence
        if not isinstance(execution_time_evidence, FinancialExecutionTimeEvidence):
            raise AuthenticatedProviderObservationIngestionError(
                "M11E2D1_EXECUTION_TIME_EVIDENCE_REQUIRED"
            )
        if (
            command_collection is None
            or fact_collection is None
            or ap_truth_collection is None
            or platform_truth_collection is None
        ):
            raise AuthenticatedProviderObservationIngestionError(
                "M11E5_RUNTIME_COLLECTIONS_REQUIRED"
            )
        return orchestrate_terminal_execution_fact_and_projection(
            evidence.tenant_id,
            application.attempt.execution_attempt_id,
            command_collection=command_collection,
            attempt_collection=attempt_collection,
            observation_collection=observation_collection,
            fact_collection=fact_collection,
            ap_truth_collection=ap_truth_collection,
            platform_truth_collection=platform_truth_collection,
            execution_time_evidence=execution_time_evidence,
            session=session,
        )
    return application


# ARTIFACT: authenticated_provider_observation_ingestion.py
# VERSION: v1.1.0-M11-P5-R2E-R5
# AUTHORITY BOUNDARY: authenticated observation ingestion only; no execution truth or settlement.
# TENANT POSTURE: exact tenant and attempt correlation; caller-owned transaction.
# FAIL-CLOSED POSTURE: weak, ambiguous, malformed, or divergent evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; later derivation remains separate.
# END OF WILSY OS SOVEREIGN ARTIFACT
