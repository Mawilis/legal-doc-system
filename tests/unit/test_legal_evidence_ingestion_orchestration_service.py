"""Direct certificate for C4D5D8 ingestion orchestration.

TITLE: Legal Evidence Ingestion Orchestration Direct Certificate
VERSION: v1.0.2-L10A2R-C4D5D8-INGESTION-ORCHESTRATION-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
PURPOSE:
    Certify prepare -> fresh durable verification -> provider begin ordering
    without transaction ownership, false distributed transactions or later
    legal/provider authority.
CERTIFICATION / UPDATE DATE: 2026-10-01
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import inspect
from typing import Any
from unittest.mock import patch

import pytest

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
)
from tools.eos.legal_operations.domain.legal_evidence_ingestion_admission import (
    LegalEvidenceIngestionAdmission,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ProcessDocument,
)
from tools.eos.legal_operations.registry.legal_evidence_binary_write_intent_registry import (
    LegalEvidenceBinaryWriteIntentRecord,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryWriteSession,
)
from tools.eos.legal_operations.service.legal_evidence_ingestion_orchestration_service import (
    LegalEvidenceDurableIngestionVerification,
    LegalEvidenceIngestionOrchestrationError,
    LegalEvidenceIngestionOrchestrationService,
    LegalEvidenceIngestionTransactionRequiredError,
)


AT = datetime(
    2026,
    10,
    1,
    20,
    0,
    tzinfo=timezone.utc,
)

SHA_A = "a" * 128


class _FixedUUID:
    hex = "0123456789abcdef0123456789abcdef"


class _Tx:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


def _admission() -> LegalEvidenceIngestionAdmission:
    document = ProcessDocument(
        tenant_id="tenant-c4d5d8",
        document_id="document-c4d5d8",
        case_matter_id="matter-c4d5d8",
        document_type="court-filing",
        registered_at=AT,
        registration_evidence_reference=(
            "evidence:process:c4d5d8"
        ),
    )

    with patch(
        "tools.eos.legal_operations.domain."
        "legal_evidence_ingestion_admission.uuid4",
        return_value=_FixedUUID(),
    ):
        return LegalEvidenceIngestionAdmission.issue(
            process_document=document,
            media_type="Application/PDF",
            original_filename="founding-affidavit.pdf",
            declared_content_length=4096,
            admitted_at=AT,
        )


class _Capacity:
    def __init__(
        self,
    ) -> None:
        self.calls: list[
            tuple[Any, Any, Any]
        ] = []

    def reserve(
        self,
        *,
        command: Any,
        tenant_profile: Any,
        session: Any,
    ) -> LegalEvidenceCapacityReservation:
        self.calls.append(
            (
                command,
                tenant_profile,
                session,
            )
        )

        return LegalEvidenceCapacityReservation(
            tenant_id=command.tenant_id,
            document_id=command.document_id,
            reservation_id=command.reservation_id,
            ingestion_intent_id=(
                command.ingestion_intent_id
            ),
            remaining_capacity_fingerprint=SHA_A,
            reserved_storage_bytes=(
                command.reserved_storage_bytes
            ),
            reserved_ingress_bytes=(
                command.reserved_ingress_bytes
            ),
            reserved_document_versions=(
                command.reserved_document_versions
            ),
            reserved_at=command.reserved_at,
            expires_at=command.expires_at,
        )


class _Registry:
    def __init__(
        self,
    ) -> None:
        self.created: list[
            tuple[Any, datetime, Any]
        ] = []
        self.reads: list[
            tuple[str, str, Any]
        ] = []
        self.record: (
            LegalEvidenceBinaryWriteIntentRecord
            | None
        ) = None

    def create_or_replay(
        self,
        intent: Any,
        *,
        registered_at: datetime,
        session: Any,
    ) -> LegalEvidenceBinaryWriteIntentRecord:
        self.created.append(
            (
                intent,
                registered_at,
                session,
            )
        )

        self.record = (
            LegalEvidenceBinaryWriteIntentRecord(
                intent=intent,
                registered_at=registered_at,
            )
        )

        return self.record

    def get_by_ingestion_reference(
        self,
        *,
        tenant_id: str,
        ingestion_reference: str,
        session: Any,
    ) -> LegalEvidenceBinaryWriteIntentRecord:
        self.reads.append(
            (
                tenant_id,
                ingestion_reference,
                session,
            )
        )

        if self.record is None:
            raise AssertionError(
                "record not prepared"
            )

        return self.record


class _Storage:
    def __init__(
        self,
    ) -> None:
        self.intents: list[Any] = []

    def begin(
        self,
        intent: Any,
    ) -> LegalEvidenceBinaryWriteSession:
        self.intents.append(
            intent
        )

        return LegalEvidenceBinaryWriteSession(
            provider_name="test-provider",
            write_session_reference=(
                "provider-session-c4d5d8"
            ),
            storage_reference=(
                "storage-c4d5d8"
            ),
            write_intent_fingerprint=(
                intent.fingerprint
            ),
        )


def _service() -> tuple[
    LegalEvidenceIngestionOrchestrationService,
    _Capacity,
    _Registry,
    _Storage,
]:
    capacity = _Capacity()
    registry = _Registry()
    storage = _Storage()

    service = (
        LegalEvidenceIngestionOrchestrationService(
            capacity_service=capacity,  # type: ignore[arg-type]
            write_intent_registry=registry,
            storage=storage,  # type: ignore[arg-type]
        )
    )

    return (
        service,
        capacity,
        registry,
        storage,
    )


def _prepare() -> tuple[
    LegalEvidenceIngestionOrchestrationService,
    _Capacity,
    _Registry,
    _Storage,
    Any,
]:
    (
        service,
        capacity,
        registry,
        storage,
    ) = _service()

    tx = _Tx()

    prepared = service.prepare(
        admission=_admission(),
        reservation_id="reservation-c4d5d8",
        idempotency_key="idempotency-c4d5d8",
        tenant_profile=object(),  # type: ignore[arg-type]
        reserved_at=AT,
        expires_at=AT + timedelta(minutes=15),
        session=tx,
    )

    return (
        service,
        capacity,
        registry,
        storage,
        prepared,
    )


def test_prepare_derives_all_ingestion_coordinates_from_admission() -> None:
    (
        _,
        capacity,
        registry,
        storage,
        prepared,
    ) = _prepare()

    admission = prepared.admission
    command = capacity.calls[0][0]

    assert (
        command.ingestion_intent_id
        == admission.ingestion_reference
    )
    assert command.tenant_id == admission.tenant_id
    assert command.document_id == admission.document_id
    assert (
        command.reserved_storage_bytes
        == admission.declared_content_length
    )
    assert (
        command.reserved_ingress_bytes
        == admission.declared_content_length
    )
    assert command.reserved_document_versions == 1

    intent = registry.created[0][0]

    assert intent.tenant_id == admission.tenant_id
    assert (
        intent.case_matter_id
        == admission.case_matter_id
    )
    assert intent.document_id == admission.document_id
    assert (
        intent.ingestion_reference
        == admission.ingestion_reference
    )
    assert intent.media_type == admission.media_type
    assert (
        intent.original_filename
        == admission.original_filename
    )
    assert (
        intent.admitted_max_content_length
        == admission.declared_content_length
    )

    assert storage.intents == []


def test_prepare_uses_same_caller_transaction_for_capacity_and_c4d5c() -> None:
    (
        _,
        capacity,
        registry,
        _,
        _,
    ) = _prepare()

    assert len(capacity.calls) == 1
    assert len(registry.created) == 1
    assert (
        capacity.calls[0][2]
        is registry.created[0][2]
    )


@pytest.mark.parametrize(
    "session",
    [
        None,
        _Tx(False),
    ],
)
def test_prepare_requires_active_caller_transaction(
    session: object,
) -> None:
    service, _, _, _ = _service()

    with pytest.raises(
        LegalEvidenceIngestionTransactionRequiredError,
        match="L10A2R_C4D5D8_TRANSACTION_REQUIRED",
    ):
        service.prepare(
            admission=_admission(),
            reservation_id="reservation-c4d5d8",
            idempotency_key="idempotency-c4d5d8",
            tenant_profile=object(),  # type: ignore[arg-type]
            reserved_at=AT,
            expires_at=AT + timedelta(minutes=15),
            session=session,
        )


def test_prepare_signature_has_no_caller_ingestion_identity() -> None:
    parameters = inspect.signature(
        LegalEvidenceIngestionOrchestrationService.prepare
    ).parameters

    assert "ingestion_intent_id" not in parameters
    assert "ingestion_reference" not in parameters


def test_verify_durable_requires_fresh_active_transaction() -> None:
    (
        service,
        _,
        _,
        _,
        prepared,
    ) = _prepare()

    with pytest.raises(
        LegalEvidenceIngestionTransactionRequiredError,
        match="L10A2R_C4D5D8_TRANSACTION_REQUIRED",
    ):
        service.verify_durable(
            prepared=prepared,
            session=_Tx(False),
        )


def test_verify_durable_rereads_exact_c4d5c_record() -> None:
    (
        service,
        _,
        registry,
        storage,
        prepared,
    ) = _prepare()

    fresh = _Tx()

    verified = service.verify_durable(
        prepared=prepared,
        session=fresh,
    )

    assert registry.reads == [
        (
            prepared.admission.tenant_id,
            prepared.admission.ingestion_reference,
            fresh,
        )
    ]

    assert (
        verified.write_intent_record
        == prepared.write_intent_record
    )
    assert (
        verified.admission_fingerprint
        == prepared.admission.fingerprint
    )
    assert (
        verified.reservation_fingerprint
        == prepared.reservation.fingerprint
    )

    assert storage.intents == []


def test_verify_durable_rejects_divergent_record() -> None:
    (
        service,
        _,
        registry,
        _,
        prepared,
    ) = _prepare()

    other_intent = type(
        prepared.write_intent_record.intent
    )(
        tenant_id=prepared.admission.tenant_id,
        case_matter_id=prepared.admission.case_matter_id,
        document_id=prepared.admission.document_id,
        ingestion_reference=(
            prepared.admission.ingestion_reference
        ),
        media_type=prepared.admission.media_type,
        original_filename="different.pdf",
        admitted_max_content_length=(
            prepared.admission.declared_content_length
        ),
    )

    registry.record = LegalEvidenceBinaryWriteIntentRecord(
        intent=other_intent,
        registered_at=AT,
    )

    with pytest.raises(
        LegalEvidenceIngestionOrchestrationError,
        match="L10A2R_C4D5D8_DURABLE_RECORD_MISMATCH",
    ):
        service.verify_durable(
            prepared=prepared,
            session=_Tx(),
        )


def test_durable_verification_public_construction_is_forbidden() -> None:
    with pytest.raises(
        LegalEvidenceIngestionOrchestrationError,
        match=(
            "L10A2R_C4D5D8_"
            "DURABLE_VERIFICATION_FACTORY_REQUIRED"
        ),
    ):
        LegalEvidenceDurableIngestionVerification(
            admission_fingerprint=SHA_A,
            reservation_fingerprint=SHA_A,
            write_intent_record=object(),
        )


def test_begin_provider_rejects_verification_from_another_service() -> None:
    (
        issuing_service,
        _,
        _,
        _,
        prepared,
    ) = _prepare()

    verified = issuing_service.verify_durable(
        prepared=prepared,
        session=_Tx(),
    )

    (
        other_service,
        _,
        _,
        other_storage,
    ) = _service()

    with pytest.raises(
        LegalEvidenceIngestionOrchestrationError,
        match="L10A2R_C4D5D8_DURABLE_VERIFICATION_REQUIRED",
    ):
        other_service.begin_provider(
            verified=verified,
        )

    assert other_storage.intents == []


def test_begin_provider_accepts_no_mongo_session_parameter() -> None:
    parameters = inspect.signature(
        LegalEvidenceIngestionOrchestrationService.begin_provider
    ).parameters

    assert "session" not in parameters


def test_begin_provider_only_after_durable_verification() -> None:
    (
        service,
        _,
        _,
        storage,
        prepared,
    ) = _prepare()

    verified = service.verify_durable(
        prepared=prepared,
        session=_Tx(),
    )

    result = service.begin_provider(
        verified=verified,
    )

    assert len(storage.intents) == 1
    assert (
        storage.intents[0]
        == verified.write_intent_record.intent
    )
    assert (
        result.write_intent_fingerprint
        == verified.write_intent_record.intent.fingerprint
    )


def test_begin_provider_rejects_unverified_input() -> None:
    service, _, _, _ = _service()

    with pytest.raises(
        LegalEvidenceIngestionOrchestrationError,
        match="L10A2R_C4D5D8_DURABLE_VERIFICATION_REQUIRED",
    ):
        service.begin_provider(
            verified=object(),  # type: ignore[arg-type]
        )


def test_provider_failure_does_not_trigger_mongo_mutation() -> None:
    (
        _,
        capacity,
        registry,
        _,
        prepared,
    ) = _prepare()

    class _FailingStorage:
        def begin(
            self,
            intent: Any,
        ) -> LegalEvidenceBinaryWriteSession:
            raise RuntimeError(
                "provider unavailable"
            )

    failing = (
        LegalEvidenceIngestionOrchestrationService(
            capacity_service=capacity,  # type: ignore[arg-type]
            write_intent_registry=registry,
            storage=_FailingStorage(),  # type: ignore[arg-type]
        )
    )

    # Durable verification must be issued by the exact service instance that
    # will later invoke the provider. verify_durable() performs only the fresh
    # caller-owned C4D5C read and does not call provider I/O.
    verified = failing.verify_durable(
        prepared=prepared,
        session=_Tx(),
    )

    created_before = list(
        registry.created
    )
    reads_before = list(
        registry.reads
    )
    capacity_before = list(
        capacity.calls
    )

    with pytest.raises(
        RuntimeError,
        match="provider unavailable",
    ):
        failing.begin_provider(
            verified=verified,
        )

    assert registry.created == created_before
    assert registry.reads == reads_before
    assert capacity.calls == capacity_before


def test_durable_verification_contains_no_later_authority() -> None:
    (
        service,
        _,
        _,
        _,
        prepared,
    ) = _prepare()

    verified = service.verify_durable(
        prepared=prepared,
        session=_Tx(),
    )

    forbidden = {
        "content_reference",
        "content_fingerprint",
        "object_version_reference",
        "provider_integrity_reference",
        "orphan_proven",
        "abort_authorized",
        "deletion_authorized",
        "provider_delete_authorized",
        "retention_authorized",
        "legal_hold_released",
    }

    assert all(
        not hasattr(
            verified,
            field,
        )
        for field in forbidden
    )


# ARTIFACT: test_legal_evidence_ingestion_orchestration_service.py
# VERSION: v1.0.2-L10A2R-C4D5D8-INGESTION-ORCHESTRATION-CERT
# AUTHORITY BOUNDARY: direct three-phase ingestion orchestration certification only
# TENANT POSTURE: admission/reservation/write-intent/provider scope remains exact
# TRANSACTION POSTURE: prepare/read require caller transaction; provider begin accepts none
# PROVIDER POSTURE: provider begin follows fresh durable C4D5C verification only
# ORPHAN POSTURE: no orphan proof
# ABORT POSTURE: no abort authority
# DELETION POSTURE: no deletion authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
