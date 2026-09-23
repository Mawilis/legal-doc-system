"""Host-backed certificate for canonical Legal Operations intake registration.

TITLE: WILSY OS Process Service Intake Registration Real-Mongo Certificate
VERSION: v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION-RM-CERT
AUTHORITY: Host-backed certification of canonical L8-2 initial intake registration.
EPITOME: Prove atomic CaseMatter -> LegalInstruction -> ProcessDocument ->
         REGISTERED custody creation, exact replay, progressed-history replay,
         partial-state rejection, immutable divergence rejection, tenant
         isolation, caller-session propagation, rollback, and non-financial
         durability against the writable Wilsy certification Mongo replica set.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_process_service_intake_registration_orchestrator_real_mongo.py
COLLABORATION / OWNERSHIP: L8-2 owns initial registration composition; P1 owns
                            lifecycle/custody semantics; P2 owns immutable
                            persistence/hydration; L8-0 owns deterministic
                            complete-history validation. This certificate caller
                            exclusively owns Mongo sessions, transactions,
                            commit, abort, and cleanup.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION-RM-CERT
           establishes host-backed four-fact commit/replay, later-history replay,
           same-session propagation, partial-state rejection, identity/history
           divergence rejection, tenant isolation, whole-transaction rollback,
           and non-financial durable evidence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and opaque legal
                             references only; no real customer, provider,
                             credential, secret, browser, payment, or external
                             service data is used.
TENANT BOUNDARY: Every exact-history lookup and write remains tenant-scoped.
                 Identical matter/instruction/document/custody identities may
                 exist independently across different tenants without fallback
                 or disclosure.
AUTHORITY BOUNDARY: Certificate only. REGISTERED instruction is not ACCEPTED;
                    REGISTERED document/custody is not RECEIVED; registration
                    creates no allocation, attempt, service, return, invoice,
                    IAM, payment, execution, settlement, or accounting truth.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; persisted intake rows must contain
                              no financial-execution or settlement authority.
TRANSACTION BOUNDARY: This certificate starts every transaction explicitly with
                      snapshot read concern and majority+journaled write concern.
                      L8-2/P2 must receive the same active caller session and
                      never start, commit, abort, or retry that transaction.
FAIL-CLOSED DECLARATION: Runtime unavailability, wrong replica set, missing
                         writable primary, session loss, partial registration,
                         divergent identity/history, cross-tenant contamination,
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

import tools.eos.legal_operations.orchestration.process_service_intake_registration_orchestrator as l8_2
from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    CaseMatter,
    CaseMatterState,
    LegalInstructionState,
    ProcessDocumentState,
)
from tools.eos.legal_operations.orchestration.process_service_intake_registration_orchestrator import (
    VERSION as PRODUCTION_VERSION,
    ProcessServiceIntakeRegistrationDisposition,
    ProcessServiceIntakeRegistrationError,
    register_process_service_intake,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
BASE = datetime(2026, 9, 23, 7, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[dict[str, Any]]:
    """Yield one verified writable isolated database and clean it after the test.

    L8-2B is explicitly host-backed evidence, so unavailable Mongo, the wrong
    replica set, or absence of a writable primary is a certificate failure
    rather than a skip.
    """
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
                f"L8_2_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
            )
        if hello.get("setName") != EXPECTED_REPLICA_SET:
            pytest.fail(
                f"L8_2_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
            )
        if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
            pytest.fail("L8_2_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")

        database = client[f"legal_ops_l8_2_intake_{uuid.uuid4().hex}"]
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
    """Return one valid isolated synthetic tenant identifier."""
    return f"{prefix}-{uuid.uuid4().hex}"


def _kwargs(
    tenant_id: str,
    *,
    suffix: str = "1",
) -> dict[str, object]:
    """Return one complete linked initial intake registration payload."""
    return {
        "tenant_id": tenant_id,
        "case_matter_id": f"matter-{suffix}",
        "matter_reference": f"CASE-2026-{suffix}",
        "case_opened_at": BASE,
        "matter_evidence_reference": f"matter-registration-{suffix}",
        "instruction_id": f"instruction-{suffix}",
        "instruction_registered_at": BASE + timedelta(minutes=1),
        "instruction_evidence_reference": f"instruction-registration-{suffix}",
        "document_id": f"document-{suffix}",
        "document_type": "summons",
        "document_registered_at": BASE + timedelta(minutes=2),
        "document_registration_evidence_reference": (
            f"document-registration-{suffix}"
        ),
        "registration_custody_event_id": f"custody-registration-{suffix}",
    }


def _register(
    *,
    tenant_id: str,
    lifecycle: Any,
    session: Any,
    suffix: str = "1",
) -> Any:
    """Call L8-2 with one deterministic synthetic intake."""
    values = _kwargs(tenant_id, suffix=suffix)
    return register_process_service_intake(
        tenant_id=str(values["tenant_id"]),
        case_matter_id=str(values["case_matter_id"]),
        matter_reference=str(values["matter_reference"]),
        case_opened_at=values["case_opened_at"],
        matter_evidence_reference=str(values["matter_evidence_reference"]),
        instruction_id=str(values["instruction_id"]),
        instruction_registered_at=values["instruction_registered_at"],
        instruction_evidence_reference=str(
            values["instruction_evidence_reference"]
        ),
        document_id=str(values["document_id"]),
        document_type=str(values["document_type"]),
        document_registered_at=values["document_registered_at"],
        document_registration_evidence_reference=str(
            values["document_registration_evidence_reference"]
        ),
        registration_custody_event_id=str(
            values["registration_custody_event_id"]
        ),
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


def test_real_mongo_complete_intake_commit_replay_and_session_propagation(
    mongo_context: dict[str, Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Certify four-fact commit, exact no-write replay, and one caller session."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-2-lineage")

    observed: list[tuple[str, object]] = []
    original_history = l8_2.LegalOperationsLifecycleRegistry.get_entity_history
    original_create = l8_2.LegalOperationsLifecycleRegistry.create

    def observed_history(
        tenant: str,
        entity_type: str,
        entity_identity: str,
        collection: Any,
        *,
        session: object = None,
    ) -> tuple[Any, ...]:
        observed.append(("history", session))
        return original_history(
            tenant,
            entity_type,
            entity_identity,
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
        l8_2.LegalOperationsLifecycleRegistry,
        "get_entity_history",
        staticmethod(observed_history),
    )
    monkeypatch.setattr(
        l8_2.LegalOperationsLifecycleRegistry,
        "create",
        staticmethod(observed_create),
    )

    session = _transaction(client)
    try:
        created = _register(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=session,
        )
        assert (
            created.disposition
            is ProcessServiceIntakeRegistrationDisposition.CREATED
        )
        assert observed
        assert all(observed_session is session for _, observed_session in observed)
        session.commit_transaction()
    finally:
        session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == 4
    assert {
        row["entity_type"]
        for row in lifecycle.find({"tenant_id": tenant_id})
    } == {
        "CaseMatter",
        "LegalInstruction",
        "ProcessDocument",
        "DocumentCustodyEvent",
    }

    replay_session = _transaction(client)
    try:
        replayed = _register(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=replay_session,
        )
        assert (
            replayed.disposition
            is ProcessServiceIntakeRegistrationDisposition.REPLAYED
        )
        replay_session.commit_transaction()
    finally:
        replay_session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == 4
    for entity_type, identity in (
        ("CaseMatter", "matter-1"),
        ("LegalInstruction", "instruction-1"),
        ("ProcessDocument", "document-1"),
        ("DocumentCustodyEvent", "custody-registration-1"),
    ):
        history = LegalOperationsLifecycleRegistry.get_entity_history(
            tenant_id,
            entity_type,
            identity,
            lifecycle,
        )
        assert len(history) == 1


def test_real_mongo_registration_replays_after_valid_progression(
    mongo_context: dict[str, Any],
) -> None:
    """Certify original registration remains replayable after later lifecycle facts."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-2-progressed")

    create_session = _transaction(client)
    try:
        created = _register(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=create_session,
        )
        create_session.commit_transaction()
    finally:
        create_session.end_session()

    progress_session = _transaction(client)
    try:
        closed_case = created.case_matter.transition_to(
            CaseMatterState.CLOSED,
            evidence_reference="matter-close",
            occurred_at=BASE + timedelta(hours=1),
        )
        accepted_instruction = created.instruction.transition_to(
            LegalInstructionState.ACCEPTED,
            evidence_reference="instruction-accept",
            occurred_at=BASE + timedelta(minutes=10),
        )
        received_document = created.document.transition_to(
            ProcessDocumentState.RECEIVED,
            evidence_reference="office-receipt",
            occurred_at=BASE + timedelta(minutes=15),
        )
        for value in (
            closed_case,
            accepted_instruction,
            received_document,
        ):
            LegalOperationsLifecycleRegistry.create(
                value,
                lifecycle,
                session=progress_session,
            )
        progress_session.commit_transaction()
    finally:
        progress_session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == 7

    replay_session = _transaction(client)
    try:
        replayed = _register(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=replay_session,
        )
        assert (
            replayed.disposition
            is ProcessServiceIntakeRegistrationDisposition.REPLAYED
        )
        assert replayed.case_matter.state is CaseMatterState.OPEN
        assert replayed.instruction.state is LegalInstructionState.REGISTERED
        assert replayed.document.state is ProcessDocumentState.REGISTERED
        replay_session.commit_transaction()
    finally:
        replay_session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == 7


def test_real_mongo_partial_registration_and_divergent_identity_fail_closed(
    mongo_context: dict[str, Any],
) -> None:
    """Certify partial or same-identity/different-registration state is never healed."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    partial_tenant = _tenant("tenant-l8-2-partial")

    seed_session = _transaction(client)
    try:
        partial_case = CaseMatter(
            tenant_id=partial_tenant,
            case_matter_id="matter-1",
            matter_reference="CASE-2026-1",
            opened_at=BASE,
            evidence_reference="matter-registration-1",
        )
        LegalOperationsLifecycleRegistry.create(
            partial_case,
            lifecycle,
            session=seed_session,
        )
        seed_session.commit_transaction()
    finally:
        seed_session.end_session()

    partial_session = _transaction(client)
    try:
        with pytest.raises(ProcessServiceIntakeRegistrationError) as caught:
            _register(
                tenant_id=partial_tenant,
                lifecycle=lifecycle,
                session=partial_session,
            )
        assert caught.value.code == "L8_2_PARTIAL_REGISTRATION"
        partial_session.abort_transaction()
    finally:
        partial_session.end_session()

    assert lifecycle.count_documents({"tenant_id": partial_tenant}) == 1

    divergent_tenant = _tenant("tenant-l8-2-identity")
    divergent_seed = _transaction(client)
    try:
        divergent_case = CaseMatter(
            tenant_id=divergent_tenant,
            case_matter_id="matter-1",
            matter_reference="DIFFERENT-CASE",
            opened_at=BASE,
            evidence_reference="different-registration",
        )
        LegalOperationsLifecycleRegistry.create(
            divergent_case,
            lifecycle,
            session=divergent_seed,
        )
        divergent_seed.commit_transaction()
    finally:
        divergent_seed.end_session()

    divergent_session = _transaction(client)
    try:
        with pytest.raises(ProcessServiceIntakeRegistrationError) as caught:
            _register(
                tenant_id=divergent_tenant,
                lifecycle=lifecycle,
                session=divergent_session,
            )
        assert caught.value.code == "L8_2_REGISTRATION_IDENTITY_DIVERGENCE"
        divergent_session.abort_transaction()
    finally:
        divergent_session.end_session()

    assert lifecycle.count_documents({"tenant_id": divergent_tenant}) == 1


def test_real_mongo_preexisting_divergent_history_rejects(
    mongo_context: dict[str, Any],
) -> None:
    """Certify forked/static-divergent history is never selected or healed."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-2-history")

    first = CaseMatter(
        tenant_id,
        "matter-1",
        "CASE-2026-1",
        BASE,
        "matter-registration-1",
    )
    second = CaseMatter(
        tenant_id,
        "matter-1",
        "DIFFERENT-CASE",
        BASE,
        "different-registration",
    )

    seed_session = _transaction(client)
    try:
        LegalOperationsLifecycleRegistry.create(
            first,
            lifecycle,
            session=seed_session,
        )
        LegalOperationsLifecycleRegistry.create(
            second,
            lifecycle,
            session=seed_session,
        )
        seed_session.commit_transaction()
    finally:
        seed_session.end_session()

    assert lifecycle.count_documents(
        {
            "tenant_id": tenant_id,
            "entity_type": "CaseMatter",
            "entity_identity": "matter-1",
        }
    ) == 2

    provision_session = _transaction(client)
    try:
        with pytest.raises(ProcessServiceIntakeRegistrationError) as caught:
            _register(
                tenant_id=tenant_id,
                lifecycle=lifecycle,
                session=provision_session,
            )
        assert caught.value.code == "L8_2_REGISTRATION_HISTORY_DIVERGENT"
        provision_session.abort_transaction()
    finally:
        provision_session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == 2


def test_real_mongo_whole_intake_transaction_abort_leaves_no_rows(
    mongo_context: dict[str, Any],
) -> None:
    """Certify caller abort rolls back all four initial registration facts."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-2-rollback")

    session = _transaction(client)
    try:
        result = _register(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=session,
        )
        assert (
            result.disposition
            is ProcessServiceIntakeRegistrationDisposition.CREATED
        )
        assert lifecycle.count_documents(
            {"tenant_id": tenant_id},
            session=session,
        ) == 4
        session.abort_transaction()
    finally:
        session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_id}) == 0


def test_real_mongo_identical_intake_ids_are_isolated_by_tenant(
    mongo_context: dict[str, Any],
) -> None:
    """Certify equal local identities can coexist independently across tenants."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_a = _tenant("tenant-l8-2-a")
    tenant_b = _tenant("tenant-l8-2-b")

    for tenant_id in (tenant_a, tenant_b):
        session = _transaction(client)
        try:
            result = _register(
                tenant_id=tenant_id,
                lifecycle=lifecycle,
                session=session,
            )
            assert (
                result.disposition
                is ProcessServiceIntakeRegistrationDisposition.CREATED
            )
            session.commit_transaction()
        finally:
            session.end_session()

    assert lifecycle.count_documents({"tenant_id": tenant_a}) == 4
    assert lifecycle.count_documents({"tenant_id": tenant_b}) == 4
    assert lifecycle.count_documents(
        {
            "entity_type": "LegalInstruction",
            "entity_identity": "instruction-1",
        }
    ) == 2


def test_real_mongo_intake_rows_have_no_downstream_or_financial_authority(
    mongo_context: dict[str, Any],
) -> None:
    """Certify durable registration evidence does not imply later lifecycle truth."""
    client = mongo_context["client"]
    lifecycle = mongo_context["lifecycle"]
    tenant_id = _tenant("tenant-l8-2-financial")

    session = _transaction(client)
    try:
        result = _register(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            session=session,
        )
        assert result.instruction.state is LegalInstructionState.REGISTERED
        assert result.document.state is ProcessDocumentState.REGISTERED
        session.commit_transaction()
    finally:
        session.end_session()

    documents = list(lifecycle.find({"tenant_id": tenant_id}))
    assert len(documents) == 4
    forbidden = {
        "payment",
        "settlement",
        "paid_state",
        "refund",
        "invoice",
        "billing_execution",
        "bank_execution",
        "provider_execution",
    }
    for document in documents:
        assert forbidden.isdisjoint(_all_key_names(deepcopy(document)))

    assert PRODUCTION_VERSION == "v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION"
    assert VERSION == "v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION-RM-CERT"


# ARTIFACT: test_process_service_intake_registration_orchestrator_real_mongo.py
# VERSION: v1.0.0-L8-2-PROCESS-SERVICE-INTAKE-REGISTRATION-RM-CERT
# AUTHORITY BOUNDARY: host-backed L8-2 initial intake registration certificate only
# TENANT POSTURE: UUID-isolated exact tenant scope with equal-id isolation
# FAIL-CLOSED POSTURE: runtime/session/partial/divergence/rollback leakage fails
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
