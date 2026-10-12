"""WILSY OS Legal Operations courier observation ingestion orchestrator.

TITLE: Legal Operations Courier Observation Ingestion Orchestrator
VERSION: v1.0.0-L8-8C-COURIER-OBSERVATION-INGESTION
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Resolve current canonical CaseMatter and ProcessDocument evidence,
         correlate exact tenant/matter/document scope, normalize one already-
         authenticated external courier event through L8-8A, and persist/replay
         it through L8-8B inside one caller-owned transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_courier_observation_ingestion_orchestrator.py
COLLABORATION / OWNERSHIP: P1/P2 own canonical Legal lifecycle history. L8-0
                            owns deterministic current-snapshot selection.
                            L8-8A owns courier observation semantics/integrity.
                            L8-8B owns append-only durability/replay. This module
                            composes those authorities only.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8C-COURIER-OBSERVATION-INGESTION establishes
           exact current CaseMatter/ProcessDocument resolution, tenant/matter/
           document recorrelation, active caller-transaction enforcement,
           provider-neutral observation normalization, append-only replay and
           bounded fail-closed error translation without HTTP/IAM authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Accepts only opaque routing/provenance identifiers,
                             bounded provider status and SHA3-512 evidence.
                             No address, GPS, signature image, raw provider
                             payload, secret, credential, token, document bytes,
                             payment data or unrestricted narrative.
TENANT BOUNDARY: tenant_id/case_matter_id/document_id are caller routing
                 correlation inputs, never provider authority. Exact current P1
                 histories must resolve to the same tenant/matter/document
                 scope before any L8-8A observation can be constructed.
AUTHORITY BOUNDARY: Correlation, normalization and persistence only. Provider
                    DELIVERY_REPORTED remains external evidence and cannot
                    transition ProcessDocument/custody, certify service, create
                    ServiceExecution/ReturnOfService, send notification, file
                    with Court, issue invoice, execute payment or settle funds.
TRANSACTION BOUNDARY: Caller supplies and owns one already-active Mongo
                      transaction spanning canonical reads and observation
                      persistence. This module never starts, commits, aborts,
                      retries or reconciles a transaction.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial
                              execution authority; settlement remains separate.
FAIL-CLOSED DECLARATION: Missing transaction, absent/ambiguous/corrupt current
                         lifecycle evidence, scope divergence, invalid provider
                         evidence, replay conflict and persistence failure reject
                         without fallback, lifecycle inference or authority gain.
"""
from __future__ import annotations

import re
from typing import Any, Final, NoReturn

from tools.eos.legal_operations.domain.legal_courier_observation import (
    LegalCourierObservation,
    LegalCourierObservationError,
    LegalCourierObservationKind,
    create_legal_courier_observation,
)
from tools.eos.legal_operations.domain.legal_operations_current_projection import (
    LegalOperationsCurrentProjectionError,
    resolve_current_lifecycle_snapshot,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    ProcessDocument,
)
from tools.eos.legal_operations.registry.legal_courier_observation_registry import (
    LegalCourierObservationRegistry,
    LegalCourierObservationRegistryError,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
)


VERSION: Final[str] = "v1.0.0-L8-8C-COURIER-OBSERVATION-INGESTION"

_IDENTITY: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,159}$"
)
_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {"default", "global", "global_root", "root", "master", "*"}
)


class LegalCourierObservationIngestionError(RuntimeError):
    """Stable fail-closed error for L8-8C courier observation composition."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _fail(code: str) -> NoReturn:
    raise LegalCourierObservationIngestionError(code)


def _identity(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY.fullmatch(value) is None
    ):
        _fail(f"L8_8C_{name.upper()}_INVALID")
    return value


def _tenant(value: object) -> str:
    tenant_id = _identity("tenant_id", value)
    if tenant_id.casefold() in _FORBIDDEN_TENANTS:
        _fail("L8_8C_TENANT_INVALID")
    return tenant_id


def _active_transaction(session: Any) -> Any:
    if session is None:
        _fail("L8_8C_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", False)
    if callable(marker):
        marker = marker()
    if marker is not True:
        _fail("L8_8C_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _current_matter(
    *,
    tenant_id: str,
    case_matter_id: str,
    lifecycle_collection: Any,
    session: Any,
) -> CaseMatter:
    try:
        history = LegalOperationsLifecycleRegistry.get_entity_history(
            tenant_id,
            "CaseMatter",
            case_matter_id,
            lifecycle_collection,
            session=session,
        )
        value = resolve_current_lifecycle_snapshot(
            history,
            expected_type=CaseMatter,
        )
    except (
        LegalOperationsLifecycleRegistryError,
        LegalOperationsCurrentProjectionError,
    ) as error:
        raise LegalCourierObservationIngestionError(
            "L8_8C_CASE_MATTER_UNAVAILABLE"
        ) from error
    if type(value) is not CaseMatter:
        _fail("L8_8C_CASE_MATTER_TYPE_INVALID")
    if (
        value.tenant_id != tenant_id
        or value.case_matter_id != case_matter_id
    ):
        _fail("L8_8C_CASE_MATTER_SCOPE_MISMATCH")
    return value


def _current_document(
    *,
    tenant_id: str,
    case_matter_id: str,
    document_id: str,
    lifecycle_collection: Any,
    session: Any,
) -> ProcessDocument:
    try:
        history = LegalOperationsLifecycleRegistry.get_entity_history(
            tenant_id,
            "ProcessDocument",
            document_id,
            lifecycle_collection,
            session=session,
        )
        value = resolve_current_lifecycle_snapshot(
            history,
            expected_type=ProcessDocument,
        )
    except (
        LegalOperationsLifecycleRegistryError,
        LegalOperationsCurrentProjectionError,
    ) as error:
        raise LegalCourierObservationIngestionError(
            "L8_8C_PROCESS_DOCUMENT_UNAVAILABLE"
        ) from error
    if type(value) is not ProcessDocument:
        _fail("L8_8C_PROCESS_DOCUMENT_TYPE_INVALID")
    if (
        value.tenant_id != tenant_id
        or value.case_matter_id != case_matter_id
        or value.document_id != document_id
    ):
        _fail("L8_8C_PROCESS_DOCUMENT_SCOPE_MISMATCH")
    return value


def ingest_legal_courier_observation(
    *,
    tenant_id: str,
    case_matter_id: str,
    document_id: str,
    observation_id: str,
    provider_key: str,
    tracking_reference: str,
    provider_event_reference: str,
    event_kind: LegalCourierObservationKind,
    provider_status: str,
    observed_at: Any,
    source_evidence_reference: str,
    source_evidence_fingerprint: str,
    lifecycle_collection: Any,
    courier_observation_collection: Any,
    session: Any,
) -> LegalCourierObservation:
    """Correlate and persist one authenticated external courier observation.

    The routing tenant/matter/document identifiers are not accepted as Legal
    truth by themselves. The function resolves current canonical CaseMatter and
    ProcessDocument histories in the caller transaction, requires exact scope
    agreement, then delegates immutable observation construction to L8-8A and
    durable append/replay to L8-8B.

    No lifecycle transition, provider call, HTTP authentication, IAM decision,
    notification delivery, service/outcome certification, return generation,
    Court filing, invoice, payment, execution or settlement occurs here.
    """
    tx = _active_transaction(session)
    tenant = _tenant(tenant_id)
    matter_id = _identity("case_matter_id", case_matter_id)
    doc_id = _identity("document_id", document_id)

    matter = _current_matter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        lifecycle_collection=lifecycle_collection,
        session=tx,
    )
    document = _current_document(
        tenant_id=tenant,
        case_matter_id=matter_id,
        document_id=doc_id,
        lifecycle_collection=lifecycle_collection,
        session=tx,
    )

    if (
        matter.tenant_id != document.tenant_id
        or matter.case_matter_id != document.case_matter_id
    ):
        _fail("L8_8C_CANONICAL_SCOPE_MISMATCH")

    try:
        observation = create_legal_courier_observation(
            case_matter=matter,
            process_document=document,
            observation_id=observation_id,
            provider_key=provider_key,
            tracking_reference=tracking_reference,
            provider_event_reference=provider_event_reference,
            event_kind=event_kind,
            provider_status=provider_status,
            observed_at=observed_at,
            source_evidence_reference=source_evidence_reference,
            source_evidence_fingerprint=source_evidence_fingerprint,
        )
    except LegalCourierObservationError as error:
        raise LegalCourierObservationIngestionError(
            "L8_8C_OBSERVATION_INVALID"
        ) from error

    try:
        return LegalCourierObservationRegistry(
            courier_observation_collection
        ).create_or_replay(
            observation,
            session=tx,
        )
    except LegalCourierObservationRegistryError as error:
        raise LegalCourierObservationIngestionError(
            "L8_8C_PERSISTENCE_FAILED"
        ) from error


__all__ = [
    "VERSION",
    "LegalCourierObservationIngestionError",
    "ingest_legal_courier_observation",
]


# ARTIFACT: legal_courier_observation_ingestion_orchestrator.py
# VERSION: v1.0.0-L8-8C-COURIER-OBSERVATION-INGESTION
# AUTHORITY BOUNDARY: current canonical scope correlation + L8-8A normalization + L8-8B persistence only
# TENANT POSTURE: routing scope must recorrect against exact current CaseMatter and ProcessDocument evidence
# TRANSACTION POSTURE: caller owns one active transaction spanning canonical reads and append-only observation persistence
# FAIL-CLOSED POSTURE: absent/ambiguous/corrupt current evidence, scope drift, invalid observation or persistence failure reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
