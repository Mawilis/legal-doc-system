"""Host-backed certificate for Legal Operations acceptance and office receipt.

TITLE: WILSY OS Process Service Acceptance and Receipt Real-Mongo Certificate
VERSION: v1.0.0-L8-3-PROCESS-SERVICE-ACCEPTANCE-RECEIPT-RM-CERT
AUTHORITY: Host-backed certification of canonical L8-3 acceptance and office receipt.
EPITOME: Prove atomic LegalInstruction ACCEPTED, ProcessDocument RECEIVED,
         sequence-two RECEIVED_IN_OFFICE custody, canonical SheriffOffice
         binding, exact replay, later-progression replay, partial-state rejection,
         foreign-office absence, caller-session propagation, rollback, and
         non-financial durable evidence against the writable Wilsy Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_acceptance_receipt_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: L8-1 provides canonical directory prerequisites;
                            L8-2 provides canonical registered intake; L8-3 owns
                            acceptance plus physical office receipt; P1 owns
                            lifecycle/custody semantics; P2 owns immutable
                            persistence and custody-history hydration; L8-0 owns
                            current-history projection. This certificate caller
                            owns Mongo session/transaction lifecycle and cleanup.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-3-PROCESS-SERVICE-ACCEPTANCE-RECEIPT-RM-CERT
           establishes host-backed creation/replay, progressed-history replay,
           exact caller-session propagation, partial-state rejection,
           foreign-office non-disclosure, whole-transaction rollback, custody
           continuity, and non-financial durable evidence for L8-3.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and opaque legal
                             references only; no real customer, provider,
                             credential, secret, browser, payment, or external
                             service data is used.
TENANT BOUNDARY: Every directory, intake, history, custody, and write operation
                 is exact-tenant scoped. A SheriffOffice existing only under a
                 foreign tenant is indistinguishable from absence.
AUTHORITY BOUNDARY: Certificate only. ACCEPTED is not service; RECEIVED and
                    RECEIVED_IN_OFFICE are not deputy allocation, attempt,
                    service execution, return, invoice, payment, execution,
                    settlement, or accounting truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; persisted L8-3 evidence must carry
                              no financial-execution or settlement authority.
TRANSACTION BOUNDARY: The certificate explicitly owns every Mongo transaction.
                      L8-1/L8-2/L8-3/P2 receive the same caller session and must
                      never start, commit, abort, or retry it.
FAIL-CLOSED DECLARATION: Runtime unavailability, wrong replica set, missing
                         writable primary, session loss, partial acceptance/
                         receipt, foreign office scope, custody divergence,
                         rollback leakage, or financial-authority leakage fails.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
import sys
from typing import Any, Iterator
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.legal_operations.orchestration.process_service_acceptance_receipt_orchestrator as l8_3
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    DocumentCustodyEvent,
    DocumentCustodyEventType,
    LegalInstructionState,
    ProcessDocumentState,
)
from tools.eos.legal_operations.orchestration.process_service_acceptance_receipt_orchestrator import (
    VERSION as PRODUCTION_VERSION,
    ProcessServiceAcceptanceReceiptDisposition,
    ProcessServiceAcceptanceReceiptError,
    accept_instruction_and_receive_document,
)
from tools.eos.legal_operations.orchestration.process_service_directory_provisioning_orchestrator import (
    provision_district,
    provision_sheriff_office,
)
from tools.eos.legal_operations.orchestration.process_service_intake_registration_orchestrator import (
    register_process_service_intake,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-3-PROCESS-SERVICE-ACCEPTANCE-RECEIPT-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 23, 9, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable isolated database; host failure fails certification."""
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        retryWrites=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
        except PyMongoError as error:
            pytest.fail(
                f"L8_3_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_3_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_3_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_3_receipt_{uuid.uuid4().hex}"]
        lifecycle = database.get_collection(
            COLLECTION,
            write_concern=WriteConcern(w="majority", j=True),
            read_concern=ReadConcern("majority"),
        )
        LegalOperationsLifecycleRegistry.ensure_indexes(lifecycle)
        yield {
            "client": client,
            "database": database,
            "lifecycle": lifecycle,
        }
    finally:
        active_error = sys.exc_info()[0] is not None
        try:
            if database is not None:
                try:
                    client.drop_database(database.name)
                except PyMongoError:
                    if not active_error:
                        raise
        finally:
            client.close()


def _transaction(client: Any) -> Any:
    """Start one caller-owned snapshot/majority transaction."""
    session = client.start_session()
    session.start_transaction(
        read_concern=ReadConcern("snapshot"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    return session


def _tenant(prefix: str) -> str:
    """Return one valid UUID-isolated synthetic tenant identifier."""
    return f"{prefix}-{uuid.uuid4().hex}"


def _seed_prerequisites(
    *,
    tenant_id: str,
    lifecycle: Any,
    session: Any,
    suffix: str = "1",
) -> Any:
    """Create canonical L8-1 office and L8-2 registered intake prerequisites."""
    provision_district(
        tenant_id=tenant_id,
        district_id=f"district-{suffix}",
        name="Johannesburg Central",
        jurisdiction_code="ZA-GP-JHB",
        evidence_reference=f"district-source-{suffix}",
        lifecycle_collection=lifecycle,
        session=session,
    )
    provision_sheriff_office(
        tenant_id=tenant_id,
        sheriff_office_id=f"office-{suffix}",
        district_id=f"district-{suffix}",
        name="Sheriff Johannesburg Central",
        evidence_reference=f"office-source-{suffix}",
        lifecycle_collection=lifecycle,
        session=session,
    )
    return register_process_service_intake(
        tenant_id=tenant_id,
        case_matter_id=f"matter-{suffix}",
        matter_reference=f"CASE-2026-{suffix}",
        case_opened_at=BASE,
        matter_evidence_reference=f"matter-source-{suffix}",
        instruction_id=f"instruction-{suffix}",
        instruction_registered_at=BASE + timedelta(minutes=1),
        instruction_evidence_reference=f"instruction-source-{suffix}",
        document_id=f"document-{suffix}",
        document_type="summons",
        document_registered_at=BASE + timedelta(minutes=2),
        document_registration_evidence_reference=f"document-source-{suffix}",
        registration_custody_event_id=f"custody-registration-{suffix}",
        lifecycle_collection=lifecycle,
        session=session,
    )


def _accept_receive(
    *,
    tenant_id: str,
    lifecycle: Any,
    session: Any,
    suffix: str = "1",
) -> Any:
    """Invoke the exact canonical L8-3 acceptance/receipt command."""
    return accept_instruction_and_receive_document(
        tenant_id=tenant_id,
        instruction_id=f"instruction-{suffix}",
        document_id=f"document-{suffix}",
        sheriff_office_id=f"office-{suffix}",
        accepted_at=BASE + timedelta(minutes=10),
        acceptance_evidence_reference=f"instruction-accepted-{suffix}",
        received_at=BASE + timedelta(minutes=15),
        receipt_evidence_reference=f"office-receipt-{suffix}",
        receipt_custody_event_id=f"custody-received-{suffix}",
        lifecycle_collection=lifecycle,
        session=session,
    )


def _all_key_names(item: Any) -> set[str]:
    """Collect nested mapping keys for financial-boundary assertions."""
    if isinstance(item, dict):
        names = set(item)
        for child in item.values():
            names.update(_all_key_names(child))
        return names
    if isinstance(item, list):
        names: set[str] = set()
        for child in item:
            names.update(_all_key_names(child))
        return names
    return set()


def test_real_mongo_acceptance_receipt_commit_replay_and_session_propagation(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Certify canonical prerequisites, three-fact L8-3 commit, replay, and one session."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-3-lineage")

    seed = _transaction(client)
    try:
        _seed_prerequisites(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=seed,
        )
        seed.commit_transaction()
    finally:
        seed.end_session()

    observed: list[tuple[str, object]] = []
    original_entity_history = l8_3.LegalOperationsLifecycleRegistry.get_entity_history
    original_custody_history = (
        l8_3.LegalOperationsLifecycleRegistry.get_document_custody_history
    )
    original_create = l8_3.LegalOperationsLifecycleRegistry.create

    def observed_entity_history(
        tenant: str,
        entity_type: str,
        entity_identity: str,
        collection: Any,
        *,
        session: object = None,
    ) -> tuple[Any, ...]:
        observed.append(("entity_history", session))
        return original_entity_history(
            tenant,
            entity_type,
            entity_identity,
            collection,
            session=session,
        )

    def observed_custody_history(
        tenant: str,
        document_id: str,
        collection: Any,
        *,
        session: object = None,
    ) -> tuple[Any, ...]:
        observed.append(("custody_history", session))
        return original_custody_history(
            tenant,
            document_id,
            collection,
            session=session,
        )

    def observed_create(
        value: Any,
        collection: Any,
        *,
        session: object = None,
        **kwargs: Any,
    ) -> Any:
        observed.append(("create", session))
        return original_create(
            value,
            collection,
            session=session,
            **kwargs,
        )

    monkeypatch.setattr(
        l8_3.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        staticmethod(observed_entity_history),
    )
    monkeypatch.setattr(
        l8_3.LegalOperationsLifecycleRegistry,
        "get_document_custody_history",
        staticmethod(observed_custody_history),
    )
    monkeypatch.setattr(
        l8_3.LegalOperationsLifecycleRegistry,
        "create",
        staticmethod(observed_create),
    )

    session = _transaction(client)
    try:
        created = _accept_receive(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=session,
        )
        assert (
            created.disposition
            is ProcessServiceAcceptanceReceiptDisposition.CREATED
        )
        assert created.accepted_instruction.state is LegalInstructionState.ACCEPTED
        assert created.received_document.state is ProcessDocumentState.RECEIVED
        assert (
            created.receipt_custody_event.event_type
            is DocumentCustodyEventType.RECEIVED_IN_OFFICE
        )
        assert created.receipt_custody_event.to_holder_reference == "office-1"
        assert observed
        assert all(observed_session is session for _, observed_session in observed)
        session.commit_transaction()
    finally:
        session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == 9

    replay_session = _transaction(client)
    try:
        replayed = _accept_receive(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=replay_session,
        )
        assert (
            replayed.disposition
            is ProcessServiceAcceptanceReceiptDisposition.REPLAYED
        )
        replay_session.commit_transaction()
    finally:
        replay_session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == 9
    custody = LegalOperationsLifecycleRegistry.get_document_custody_history(
        tenant_id,
        "document-1",
        lifecycle,
    )
    assert len(custody) == 2
    assert {event.sequence_number for event in custody} == {1, 2}


def test_real_mongo_receipt_replays_after_later_valid_progression(
    mongo_context: dict[str, Any],
) -> None:
    """Certify later close/allocation evidence does not erase exact L8-3 replay."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-3-progressed")

    seed = _transaction(client)
    try:
        _seed_prerequisites(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=seed,
        )
        seed.commit_transaction()
    finally:
        seed.end_session()

    receipt_session = _transaction(client)
    try:
        created = _accept_receive(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=receipt_session,
        )
        receipt_session.commit_transaction()
    finally:
        receipt_session.end_session()

    progress = _transaction(client)
    try:
        closed_instruction = created.accepted_instruction.transition_to(
            LegalInstructionState.CLOSED,
            evidence_reference="instruction-close",
            occurred_at=BASE + timedelta(hours=1),
        )
        allocated_document = created.received_document.transition_to(
            ProcessDocumentState.ALLOCATED_TO_DEPUTY,
            evidence_reference="allocation-evidence",
            occurred_at=BASE + timedelta(minutes=30),
        )
        allocated_custody = DocumentCustodyEvent(
            tenant_id=tenant_id,
            custody_event_id="custody-allocated-1",
            document_id="document-1",
            event_type=DocumentCustodyEventType.ALLOCATED_TO_DEPUTY,
            occurred_at=BASE + timedelta(minutes=30),
            sequence_number=3,
            evidence_reference="allocation-evidence",
            from_holder_reference="office-1",
            to_holder_reference="deputy-1",
        )
        for value in (
            closed_instruction,
            allocated_document,
            allocated_custody,
        ):
            LegalOperationsLifecycleRegistry.create(
                value,
                lifecycle,
                session=progress,
            )
        progress.commit_transaction()
    finally:
        progress.end_session()

    rows_before = lifecycle.count_documents({"tenant_id": tenant_id})
    replay_session = _transaction(client)
    try:
        replayed = _accept_receive(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=replay_session,
        )
        assert (
            replayed.disposition
            is ProcessServiceAcceptanceReceiptDisposition.REPLAYED
        )
        assert replayed.accepted_instruction.state is LegalInstructionState.ACCEPTED
        assert replayed.received_document.state is ProcessDocumentState.RECEIVED
        assert len(replayed.receipt_custody_chain) == 2
        replay_session.commit_transaction()
    finally:
        replay_session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == rows_before


def test_real_mongo_partial_acceptance_receipt_rejects_without_healing(
    mongo_context: dict[str, Any],
) -> None:
    """Certify a preexisting exact ACCEPTED snapshot alone cannot be healed."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-3-partial")

    seed = _transaction(client)
    try:
        intake = _seed_prerequisites(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=seed,
        )
        accepted = intake.instruction.transition_to(
            LegalInstructionState.ACCEPTED,
            evidence_reference="instruction-accepted-1",
            occurred_at=BASE + timedelta(minutes=10),
        )
        LegalOperationsLifecycleRegistry.create(
            accepted,
            lifecycle,
            session=seed,
        )
        seed.commit_transaction()
    finally:
        seed.end_session()

    rows_before = lifecycle.count_documents({"tenant_id": tenant_id})
    session = _transaction(client)
    try:
        with pytest.raises(ProcessServiceAcceptanceReceiptError) as caught:
            _accept_receive(
                tenant_id=tenant_id,
                lifecycle=lifecycle,
                session=session,
            )
        assert caught.value.code == "L8_3_PARTIAL_ACCEPTANCE_RECEIPT"
        session.abort_transaction()
    finally:
        session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == rows_before


def test_real_mongo_foreign_office_is_absent_and_writes_nothing(
    mongo_context: dict[str, Any],
) -> None:
    """Certify a foreign-tenant office identity cannot become receipt authority."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-3-local")
    foreign_tenant = _tenant("tenant-l8-3-foreign")

    local = _transaction(client)
    try:
        register_process_service_intake(
            tenant_id=tenant_id,
            case_matter_id="matter-1",
            matter_reference="CASE-2026-1",
            case_opened_at=BASE,
            matter_evidence_reference="matter-source-1",
            instruction_id="instruction-1",
            instruction_registered_at=BASE + timedelta(minutes=1),
            instruction_evidence_reference="instruction-source-1",
            document_id="document-1",
            document_type="summons",
            document_registered_at=BASE + timedelta(minutes=2),
            document_registration_evidence_reference="document-source-1",
            registration_custody_event_id="custody-registration-1",
            lifecycle_collection=lifecycle,
            session=local,
        )
        local.commit_transaction()
    finally:
        local.end_session()

    foreign = _transaction(client)
    try:
        provision_district(
            tenant_id=foreign_tenant,
            district_id="district-1",
            name="Foreign District",
            jurisdiction_code="ZA-WC-CPT",
            evidence_reference="foreign-district",
            lifecycle_collection=lifecycle,
            session=foreign,
        )
        provision_sheriff_office(
            tenant_id=foreign_tenant,
            sheriff_office_id="office-1",
            district_id="district-1",
            name="Foreign Sheriff Office",
            evidence_reference="foreign-office",
            lifecycle_collection=lifecycle,
            session=foreign,
        )
        foreign.commit_transaction()
    finally:
        foreign.end_session()

    local_rows = lifecycle.count_documents({"tenant_id": tenant_id})
    session = _transaction(client)
    try:
        with pytest.raises(ProcessServiceAcceptanceReceiptError) as caught:
            _accept_receive(
                tenant_id=tenant_id,
                lifecycle=lifecycle,
                session=session,
            )
        assert caught.value.code == "L8_3_SHERIFFOFFICE_NOT_FOUND"
        session.abort_transaction()
    finally:
        session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == local_rows


def test_real_mongo_whole_acceptance_receipt_abort_leaves_only_prerequisites(
    mongo_context: dict[str, Any],
) -> None:
    """Certify caller abort rolls back all three L8-3 facts as one transaction."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-3-rollback")

    seed = _transaction(client)
    try:
        _seed_prerequisites(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=seed,
        )
        seed.commit_transaction()
    finally:
        seed.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == 6

    session = _transaction(client)
    try:
        result = _accept_receive(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=session,
        )
        assert (
            result.disposition
            is ProcessServiceAcceptanceReceiptDisposition.CREATED
        )
        assert lifecycle.count_documents(
            {"tenant_id": tenant_id},
            session=session,
        ) == 9
        session.abort_transaction()
    finally:
        session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == 6


def test_real_mongo_l8_3_rows_have_no_allocation_service_or_financial_authority(
    mongo_context: dict[str, Any],
) -> None:
    """Certify successful receipt persists only bounded L8-3 lifecycle evidence."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-3-boundary")

    seed = _transaction(client)
    try:
        _seed_prerequisites(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=seed,
        )
        seed.commit_transaction()
    finally:
        seed.end_session()

    session = _transaction(client)
    try:
        result = _accept_receive(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=session,
        )
        assert result.accepted_instruction.state is LegalInstructionState.ACCEPTED
        assert result.received_document.state is ProcessDocumentState.RECEIVED
        session.commit_transaction()
    finally:
        session.end_session()

    rows = list(lifecycle.find({"tenant_id": tenant_id}))
    assert len(rows) == 9
    serialized = str(rows)
    for forbidden_state in (
        "ALLOCATED_TO_DEPUTY",
        "ServiceAttempt",
        "ServiceExecution",
        "ReturnOfService",
    ):
        assert forbidden_state not in serialized

    forbidden_keys = {
        "payment",
        "settlement",
        "paid_state",
        "refund",
        "invoice",
        "billing_execution",
        "bank_execution",
        "provider_execution",
    }
    for row in rows:
        assert forbidden_keys.isdisjoint(_all_key_names(deepcopy(row)))

    assert (
        PRODUCTION_VERSION
        == "v1.1.1-L8-3-PROCESS-SERVICE-ACCEPTANCE-RECEIPT"
    )
    assert VERSION == "v1.0.0-L8-3-PROCESS-SERVICE-ACCEPTANCE-RECEIPT-RM-CERT"


# ARTIFACT: test_process_service_acceptance_receipt_orchestrator_real_mongo.py
# VERSION: v1.0.0-L8-3-PROCESS-SERVICE-ACCEPTANCE-RECEIPT-RM-CERT
# AUTHORITY BOUNDARY: host-backed L8-3 acceptance/office-receipt certificate only
# TENANT POSTURE: UUID-isolated exact tenant scope with foreign-office absence
# FAIL-CLOSED POSTURE: runtime/session/partial/scope/custody/rollback leakage fails
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
