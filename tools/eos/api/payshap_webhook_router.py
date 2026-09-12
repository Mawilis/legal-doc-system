"""WILSY OS authenticated PayShap host-runtime ingress.

TITLE: PayShap Authenticated Host-Runtime Webhook Router
VERSION: v1.1.0-M11-HOST-PAYSHAP-ROUTER-RECONCILIATION
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Composes authenticated PayShap evidence into canonical Kennel execution observation without inventing execution or settlement truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/payshap_webhook_router.py
COLLABORATION / OWNERSHIP: Kennel EOS provider-ingress / Python API composition owner.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.1.0 delegates authenticated EXECUTED evidence to the canonical reconciliation owner with the caller transaction and existing runtime collections; v1.0.0 established fail-closed PayShap command-to-attempt correlation and canonical authenticated observation composition.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: HMAC-authenticated opaque evidence only; secrets are resolved at execution time and never persisted here.
TENANT BOUNDARY: Signed provider tenant, durable command lineage, and durable attempt tenant must agree exactly.
AUTHORITY BOUNDARY: HTTP composition only; provider evidence is submitted to existing Kennel authorities.
FINANCIAL AUTHORITY BOUNDARY: Provider EXECUTED is evidence requiring reconciliation; EXECUTION != SETTLEMENT.
TRANSACTION BOUNDARY: One caller-owned Mongo transaction encloses provider evidence, canonical observation, reconciliation CAS, and runtime projection.
FAIL-CLOSED DECLARATION: Missing runtime, authentication failure, absent/ambiguous attempt correlation, and canonical-ingestion failures reject.
"""

from __future__ import annotations

from dataclasses import dataclass
import logging
import os
from typing import Any, Mapping

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pymongo.client_session import ClientSession

from tools.eos.kennel.domain.financial_execution_execution_time_evidence import (
    ExecutionTimeAuthorityKind,
    FinancialExecutionTimeEvidence,
)
from tools.eos.kennel.domain.financial_execution_provider_observation import (
    EvidenceStrength,
    ObservationStatus,
    TransportDisposition,
)
from tools.eos.kennel.evidence.payshap_evidence_store import (
    PayShapEvidenceRegistry,
    PayShapEvidenceReplayConflictError,
)
from tools.eos.kennel.evidence.payshap_webhook_ingestion import (
    PayShapWebhookError,
    ingest_webhook,
)
from tools.eos.kennel.orchestration.authenticated_provider_observation_ingestion import (
    AuthenticatedProviderTransportEvidence,
    ingest_authenticated_provider_observation,
)
from tools.eos.kennel.orchestration.financial_execution_reconciliation import (
    FinancialExecutionReconciliationError,
    reconcile_and_finalize_execution,
)
from tools.eos.kennel.providers.payshap_contract import PayShapStatus
from tools.eos.kennel.registry.financial_execution_attempt_registry import (
    FinancialExecutionAttemptRegistry,
)
from tools.eos.kennel.registry.financial_execution_command_registry import (
    COLLECTION as _COMMANDS,
)
from tools.eos.kennel.registry.financial_execution_registry import (
    COLLECTION as _AP_TRUTH,
    FACT_COLLECTION as _FACTS,
)

VERSION = "v1.1.0-M11-HOST-PAYSHAP-ROUTER-RECONCILIATION"
ROUTE_PATH = "/providers/payshap/webhook"
_SIGNATURE_HEADER = "X-PayShap-Signature"
_ATTEMPTS = "kennel_financial_execution_attempts"
_OBSERVATIONS = "kennel_financial_execution_provider_observations"
_PAYSHAP_EVIDENCE = "kennel_payshap_provider_evidence"
_PLATFORM_TRUTH = "kennel_platform_billing_financial_execution_truth"

logger = logging.getLogger(__name__)
router = APIRouter(tags=["PayShap Provider Evidence"])


class PayShapWebhookHostError(RuntimeError):
    """Fail-closed host composition or durable-correlation failure."""


@dataclass(frozen=True, slots=True)
class PayShapWebhookRuntime:
    """Live database handles only; no authority or credentials."""

    client: Any
    database: Any


@dataclass(frozen=True, slots=True)
class PayShapWebhookHostResult:
    """Bounded response; never an execution or settlement receipt."""

    provider_event_id: str
    provider_status: str
    replay: bool
    reconciliation_required: bool


def _runtime() -> PayShapWebhookRuntime:
    """Resolve already-owned Kennel persistence only when a request executes."""
    from tools.eos.kernel.db import get_client, get_database

    client = get_client()
    database = get_database()
    if client is None or database is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PAYSHAP_RUNTIME_UNAVAILABLE",
        )
    return PayShapWebhookRuntime(client=client, database=database)


def _webhook_secret() -> str:
    """Resolve the webhook secret at execution time without persisting it."""
    secret = os.getenv("WILSY_PAYSHAP_WEBHOOK_SECRET", "")
    if not secret.strip():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PAYSHAP_WEBHOOK_SECRET_UNAVAILABLE",
        )
    return secret


def _observation_status(value: PayShapStatus) -> ObservationStatus:
    """Map provider vocabulary into evidence vocabulary, never settlement."""
    try:
        return ObservationStatus(value.value)
    except ValueError:
        return ObservationStatus.UNKNOWN


def _resolve_attempt(
    tenant_id: str,
    execution_command_id: str,
    *,
    attempt_collection: Any,
    session: ClientSession,
) -> Any:
    """Resolve exactly one durable PayShap attempt for one tenant command."""
    attempts = FinancialExecutionAttemptRegistry.list_for_command(
        tenant_id,
        execution_command_id,
        limit=250,
        collection=attempt_collection,
        session=session,
    )
    matches = tuple(
        attempt
        for attempt in attempts
        if attempt.provider_name.strip().upper() == "PAYSHAP"
    )
    if len(matches) != 1:
        raise PayShapWebhookHostError(
            "PAYSHAP_WEBHOOK_ATTEMPT_CORRELATION_NOT_UNIQUE"
        )
    return matches[0]


def compose_authenticated_payshap_webhook(
    payload: Mapping[str, Any],
    signature: str,
    secret: str,
    *,
    database: Any,
    session: ClientSession,
) -> PayShapWebhookHostResult:
    """Persist authenticated evidence and apply one canonical observation.

    A provider EXECUTED status remains evidence until the canonical
    reconciliation owner accepts it. This router never performs the lifecycle
    transition itself and never invokes settlement authority.
    """
    webhook = ingest_webhook(
        payload,
        signature,
        secret,
        database[_PAYSHAP_EVIDENCE],
        session=session,
    )
    stored = PayShapEvidenceRegistry.get(
        webhook.tenant_id,
        webhook.provider_event_id,
        database[_PAYSHAP_EVIDENCE],
        session=session,
    )
    attempt = _resolve_attempt(
        webhook.tenant_id,
        webhook.execution_command_id,
        attempt_collection=database[_ATTEMPTS],
        session=session,
    )
    if attempt.tenant_id != webhook.tenant_id:
        raise PayShapWebhookHostError(
            "PAYSHAP_WEBHOOK_ATTEMPT_TENANT_MISMATCH"
        )

    observed_status = _observation_status(webhook.provider_status)
    time_evidence = None
    if observed_status is ObservationStatus.EXECUTED:
        if (
            webhook.provider_execution_reference is None
            or webhook.provider_timestamp is None
        ):
            raise PayShapWebhookHostError(
                "PAYSHAP_WEBHOOK_EXECUTION_EVIDENCE_INCOMPLETE"
            )
        time_evidence = FinancialExecutionTimeEvidence(
            tenant_id=webhook.tenant_id,
            execution_attempt_id=attempt.execution_attempt_id,
            provider_name=attempt.provider_name,
            provider_execution_reference=webhook.provider_execution_reference,
            evidence_reference=webhook.evidence_reference,
            executed_at=webhook.provider_timestamp,
            authority_kind=ExecutionTimeAuthorityKind.PROVIDER_EXECUTION_CONFIRMATION,
            evidence_strength=EvidenceStrength.AUTHENTICATED,
        )

    evidence = AuthenticatedProviderTransportEvidence(
        observation_id=f"payshap-observation-{webhook.provider_event_id}",
        tenant_id=webhook.tenant_id,
        execution_attempt_id=attempt.execution_attempt_id,
        provider_name=attempt.provider_name,
        observation_status=observed_status,
        observed_at=webhook.observed_at,
        evidence_strength=EvidenceStrength.AUTHENTICATED,
        transport_disposition=TransportDisposition.RESPONSE_RECEIVED,
        provider_request_reference=webhook.provider_reference,
        provider_execution_reference=webhook.provider_execution_reference,
        provider_evidence_reference=webhook.evidence_reference,
        provider_occurred_at=webhook.provider_timestamp,
        correlation_fingerprint=stored.payload_fingerprint,
        execution_time_evidence=time_evidence,
    )
    application = ingest_authenticated_provider_observation(
        webhook.tenant_id,
        evidence,
        session=session,
        observation_collection=database[_OBSERVATIONS],
        attempt_collection=database[_ATTEMPTS],
        command_collection=database[_COMMANDS],
        fact_collection=database[_FACTS],
        ap_truth_collection=database[_AP_TRUTH],
        platform_truth_collection=database[_PLATFORM_TRUTH],
    )
    if observed_status is ObservationStatus.EXECUTED:
        if not isinstance(time_evidence, FinancialExecutionTimeEvidence):
            raise PayShapWebhookHostError(
                "PAYSHAP_WEBHOOK_EXECUTION_TIME_EVIDENCE_REQUIRED"
            )
        reconcile_and_finalize_execution(
            webhook.tenant_id,
            attempt.execution_attempt_id,
            command_collection=database[_COMMANDS],
            attempt_collection=database[_ATTEMPTS],
            observation_collection=database[_OBSERVATIONS],
            fact_collection=database[_FACTS],
            ap_truth_collection=database[_AP_TRUTH],
            platform_truth_collection=database[_PLATFORM_TRUTH],
            execution_time_evidence=time_evidence,
            session=session,
        )
        reconcile = False
    else:
        decision = getattr(application, "decision", None)
        reconcile = bool(getattr(decision, "reconciliation_required", False))
    return PayShapWebhookHostResult(
        provider_event_id=webhook.provider_event_id,
        provider_status=webhook.provider_status.value,
        replay=webhook.is_replay,
        reconciliation_required=reconcile,
    )


@router.post(ROUTE_PATH)
async def receive_payshap_webhook(
    request: Request,
    runtime: PayShapWebhookRuntime = Depends(_runtime),
    secret: str = Depends(_webhook_secret),
) -> dict[str, object]:
    """Authenticate and atomically submit one PayShap provider observation."""
    signature = request.headers.get(_SIGNATURE_HEADER, "")
    try:
        payload = await request.json()
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PAYSHAP_WEBHOOK_PAYLOAD_INVALID",
        ) from error
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PAYSHAP_WEBHOOK_PAYLOAD_INVALID",
        )
    try:
        with runtime.client.start_session() as session:
            with session.start_transaction():
                result = compose_authenticated_payshap_webhook(
                    payload,
                    signature,
                    secret,
                    database=runtime.database,
                    session=session,
                )
    except PayShapWebhookError as error:
        code = str(error)
        http_status = (
            status.HTTP_401_UNAUTHORIZED
            if code == "PAYSHAP_WEBHOOK_AUTHENTICATION_FAILED"
            else status.HTTP_422_UNPROCESSABLE_ENTITY
        )
        raise HTTPException(status_code=http_status, detail=code) from error
    except PayShapEvidenceReplayConflictError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="PAYSHAP_WEBHOOK_REPLAY_CONFLICT",
        ) from error
    except PayShapWebhookHostError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error
    except FinancialExecutionReconciliationError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error.code,
        ) from error
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("PayShap webhook canonical ingestion failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="PAYSHAP_WEBHOOK_INGESTION_UNAVAILABLE",
        ) from error

    return {
        "accepted": True,
        "provider_event_id": result.provider_event_id,
        "provider_status": result.provider_status,
        "replay": result.replay,
        "reconciliation_required": result.reconciliation_required,
    }


__all__ = [
    "PayShapWebhookHostError",
    "PayShapWebhookHostResult",
    "PayShapWebhookRuntime",
    "ROUTE_PATH",
    "compose_authenticated_payshap_webhook",
    "receive_payshap_webhook",
    "router",
]

# ARTIFACT: payshap_webhook_router.py
# VERSION: v1.1.0-M11-HOST-PAYSHAP-ROUTER-RECONCILIATION
# AUTHORITY BOUNDARY: HTTP composition of authenticated provider evidence only.
# TENANT POSTURE: Signed tenant plus durable command/attempt lineage fail closed.
# FAIL-CLOSED POSTURE: Missing, ambiguous, malformed, or divergent correlation rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; provider EXECUTED requires reconciliation; EXECUTION != SETTLEMENT.
# END OF WILSY OS SOVEREIGN ARTIFACT
