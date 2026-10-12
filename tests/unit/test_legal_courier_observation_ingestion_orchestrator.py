"""Direct adversarial certificate for Legal courier observation ingestion.

TITLE: Legal Operations Courier Observation Ingestion Direct Certificate
VERSION: v1.0.0-L8-8C-COURIER-OBSERVATION-INGESTION-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify exact current CaseMatter/ProcessDocument correlation, active
         caller-transaction enforcement, L8-8A normalization, L8-8B replay,
         provider-evidence rejection and downstream non-authority boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_courier_observation_ingestion_orchestrator.py
COLLABORATION / OWNERSHIP: Certificate only. P1/P2 own lifecycle evidence,
                            L8-0 current projection, L8-8A observation semantics,
                            L8-8B durability, and L8-8C composition.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8C-COURIER-OBSERVATION-INGESTION-CERT
           establishes direct happy-path/replay, transaction, current-history,
           tenant/matter/document correlation, invalid-provider-evidence and
           static downstream-authority firewall coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and SHA3-512 only.
TENANT BOUNDARY: Routing scope must recorrect against canonical P1 evidence.
AUTHORITY BOUNDARY: Correlation/normalization/persistence certificate only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing transaction, absent/current-history failure,
                         scope drift and malformed provider evidence reject.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import inspect
from typing import Any

import pytest

import tools.eos.legal_operations.orchestration.legal_courier_observation_ingestion_orchestrator as ingestion
from tools.eos.legal_operations.domain.legal_courier_observation import (
    LegalCourierObservationKind,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    ProcessDocument,
)
from tools.eos.legal_operations.orchestration.legal_courier_observation_ingestion_orchestrator import (
    LegalCourierObservationIngestionError,
    ingest_legal_courier_observation,
)


BASE = datetime(2026, 10, 12, 5, 0, tzinfo=timezone.utc)
FP = "a" * 128


class Session:
    in_transaction = True


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, object] | None:
        del session
        return next(
            (
                row
                for row in self.rows
                if all(row.get(key) == value for key, value in query.items())
            ),
            None,
        )

    def insert_one(
        self,
        row: dict[str, object],
        *,
        session: object = None,
    ) -> None:
        del session
        self.rows.append(dict(row))


def matter(
    *,
    tenant_id: str = "tenant-a",
    case_matter_id: str = "matter-1",
) -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant_id,
        case_matter_id=case_matter_id,
        matter_reference="MAT-001",
        opened_at=BASE,
        evidence_reference="matter-registration-1",
    )


def document(
    *,
    tenant_id: str = "tenant-a",
    case_matter_id: str = "matter-1",
    document_id: str = "document-1",
) -> ProcessDocument:
    return ProcessDocument(
        tenant_id=tenant_id,
        document_id=document_id,
        case_matter_id=case_matter_id,
        document_type="SUMMONS",
        registered_at=BASE + timedelta(minutes=1),
        registration_evidence_reference="document-registration-1",
    )


def install_histories(
    monkeypatch: pytest.MonkeyPatch,
    *,
    matter_value: CaseMatter | None = None,
    document_value: ProcessDocument | None = None,
) -> None:
    current_matter = matter_value or matter()
    current_document = document_value or document()

    def get_entity_history(
        tenant_id: str,
        entity_type: str,
        entity_identity: str,
        collection: object,
        *,
        session: object = None,
    ) -> tuple[CaseMatter | ProcessDocument, ...]:
        del collection, session
        if tenant_id != "tenant-a":
            return ()
        if entity_type == "CaseMatter" and entity_identity == "matter-1":
            return (current_matter,)
        if entity_type == "ProcessDocument" and entity_identity == "document-1":
            return (current_document,)
        return ()

    monkeypatch.setattr(
        ingestion.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        staticmethod(get_entity_history),
    )


def kwargs(
    *,
    collection: Collection,
    session: object,
) -> dict[str, object]:
    return {
        "tenant_id": "tenant-a",
        "case_matter_id": "matter-1",
        "document_id": "document-1",
        "observation_id": "obs-1",
        "provider_key": "provider-alpha",
        "tracking_reference": "tracking-123",
        "provider_event_reference": "provider-event-1",
        "event_kind": LegalCourierObservationKind.IN_TRANSIT,
        "provider_status": "IN_TRANSIT",
        "observed_at": BASE + timedelta(minutes=2),
        "source_evidence_reference": "provider-webhook-1",
        "source_evidence_fingerprint": FP,
        "lifecycle_collection": object(),
        "courier_observation_collection": collection,
        "session": session,
    }


def test_ingests_exact_current_scope_and_replays(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_histories(monkeypatch)
    collection = Collection()
    session = Session()

    first = ingest_legal_courier_observation(
        **kwargs(collection=collection, session=session)  # type: ignore[arg-type]
    )
    replay = ingest_legal_courier_observation(
        **kwargs(collection=collection, session=session)  # type: ignore[arg-type]
    )

    assert first == replay
    assert first.tenant_id == "tenant-a"
    assert first.case_matter_id == "matter-1"
    assert first.document_id == "document-1"
    assert first.matter_fingerprint == matter().fingerprint
    assert first.document_fingerprint == document().fingerprint
    assert len(collection.rows) == 1


def test_requires_active_transaction_before_reads(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def forbidden(*args: object, **kwargs: object) -> tuple[object, ...]:
        nonlocal called
        del args, kwargs
        called = True
        return ()

    monkeypatch.setattr(
        ingestion.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        staticmethod(forbidden),
    )

    with pytest.raises(
        LegalCourierObservationIngestionError,
        match="L8_8C_ACTIVE_TRANSACTION_REQUIRED",
    ):
        ingest_legal_courier_observation(
            **kwargs(collection=Collection(), session=None)  # type: ignore[arg-type]
        )

    assert called is False


def test_missing_current_matter_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def empty_history(
        tenant_id: str,
        entity_type: str,
        entity_identity: str,
        collection: object,
        *,
        session: object = None,
    ) -> tuple[object, ...]:
        del tenant_id, entity_type, entity_identity, collection, session
        return ()

    monkeypatch.setattr(
        ingestion.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        staticmethod(empty_history),
    )

    with pytest.raises(
        LegalCourierObservationIngestionError,
        match="L8_8C_CASE_MATTER_UNAVAILABLE",
    ):
        ingest_legal_courier_observation(
            **kwargs(collection=Collection(), session=Session())  # type: ignore[arg-type]
        )


def test_document_scope_drift_rejects_before_persistence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_histories(
        monkeypatch,
        document_value=document(case_matter_id="matter-other"),
    )
    collection = Collection()

    with pytest.raises(
        LegalCourierObservationIngestionError,
        match="L8_8C_PROCESS_DOCUMENT_SCOPE_MISMATCH",
    ):
        ingest_legal_courier_observation(
            **kwargs(collection=collection, session=Session())  # type: ignore[arg-type]
        )

    assert collection.rows == []


def test_tenant_scope_drift_rejects_before_persistence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_histories(
        monkeypatch,
        document_value=document(tenant_id="tenant-b"),
    )
    collection = Collection()

    with pytest.raises(
        LegalCourierObservationIngestionError,
        match="L8_8C_PROCESS_DOCUMENT_SCOPE_MISMATCH",
    ):
        ingest_legal_courier_observation(
            **kwargs(collection=collection, session=Session())  # type: ignore[arg-type]
        )

    assert collection.rows == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("provider_key", " provider-alpha"),
        ("tracking_reference", ""),
        ("provider_event_reference", "event\nnewline"),
        ("provider_status", ""),
        ("source_evidence_fingerprint", "not-a-sha3"),
    ],
)
def test_invalid_provider_evidence_rejects(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
    value: object,
) -> None:
    install_histories(monkeypatch)
    collection = Collection()
    values = kwargs(collection=collection, session=Session())
    values[field] = value

    with pytest.raises(
        LegalCourierObservationIngestionError,
        match="L8_8C_OBSERVATION_INVALID",
    ):
        ingest_legal_courier_observation(
            **values  # type: ignore[arg-type]
        )

    assert collection.rows == []


def test_delivery_reported_remains_external_observation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    install_histories(monkeypatch)
    collection = Collection()
    values = kwargs(collection=collection, session=Session())
    values["event_kind"] = LegalCourierObservationKind.DELIVERY_REPORTED
    values["provider_status"] = "DELIVERED"

    result = ingest_legal_courier_observation(
        **values  # type: ignore[arg-type]
    )

    assert result.event_kind is LegalCourierObservationKind.DELIVERY_REPORTED
    assert result.provider_status == "DELIVERED"
    assert len(collection.rows) == 1


def test_source_contains_no_provider_or_downstream_execution_authority() -> None:
    source = inspect.getsource(ingestion)

    forbidden = (
        "requests.",
        "httpx.",
        "aiohttp.",
        ".transition_to(",
        "ServiceExecution.from_attempt(",
        "ReturnOfService.from_service_execution(",
        "notification_send",
        "court_file",
        "invoice_issue",
        "payment_execute",
        "settlement_execute",
        "start_transaction(",
        "commit_transaction(",
        "abort_transaction(",
    )
    for token in forbidden:
        assert token not in source

    assert "DELIVERY_REPORTED remains external evidence" in source
    assert "Kennel EOS" in source


# ARTIFACT: test_legal_courier_observation_ingestion_orchestrator.py
# VERSION: v1.0.0-L8-8C-COURIER-OBSERVATION-INGESTION-CERT
# AUTHORITY BOUNDARY: composition certificate only; no HTTP/IAM/provider/lifecycle/financial authority
# TENANT POSTURE: routing scope must recorrect against exact current canonical matter/document evidence
# TRANSACTION POSTURE: active caller transaction required before canonical reads or persistence
# FAIL-CLOSED POSTURE: current-history, scope, provider-evidence and persistence failures reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
