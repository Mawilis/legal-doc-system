"""Host-backed certificate for the Legal Operations P2 evidence registry.

TITLE: Wilsy OS Legal Operations Lifecycle Registry Real-Mongo Certificate
VERSION: v1.2.1-L8-5-LEGAL-OPERATIONS-TENANT-ENTITY-ENUMERATION-RM-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify real replica-set durability, immutable snapshot progression,
         tenant/entity-class enumeration, indexed document-custody history,
         factory provenance, strict corruption rejection, tenant isolation, and
         caller-owned transaction semantics for the P2 registry.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_lifecycle_registry_real_mongo.py
COLLABORATION / OWNERSHIP: Host-backed P2 certificate only; P1 owns lifecycle,
                            service, return, and evidence semantics. The test
                            caller owns Mongo sessions and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: 2026-09-23 v1.2.1-L8-5-LEGAL-OPERATIONS-TENANT-ENTITY-ENUMERATION-RM-CERT
           adds explicit exact-LegalInstruction runtime certification and
           static tuple narrowing for real-Mongo enumeration assertions;
           production behavior and authority contracts remain unchanged.
           2026-09-23 v1.2.0-L8-5-LEGAL-OPERATIONS-TENANT-ENTITY-ENUMERATION-RM-CERT
           certifies P2 v1.3.0 exact tenant/entity-class enumeration against
           real Mongo, including deterministic output, foreign isolation,
           multiple immutable histories, and caller-session compatibility.
           2026-09-23 v1.1.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY-RM-CERT
           certifies the P2 v1.2.0 tenant/document custody-history index and
           strict real-Mongo query, binds the host certificate to the current
           production version, and treats unavailable/wrong replica runtime as
           certification failure rather than a skip.
           2026-09-13 v1.0.0-LEGAL-OPERATIONS-LIFECYCLE-REGISTRY-RM-CERT
           certifies durable P1 snapshots and factory-derived evidence against
           the wilsyVendorCertRS replica set with fail-closed corruption.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic tenants and identifiers;
                             no provider, secret, customer, or external call.
TENANT BOUNDARY: Every write and read is explicitly tenant-scoped; foreign
                 evidence is represented only as governed absence.
AUTHORITY BOUNDARY: P2 persistence and strict hydration certification only;
                    this certificate does not derive or fabricate lifecycle
                    state, service, return, billing, or authorization truth.
TRANSACTION BOUNDARY: The certificate starts, commits, and aborts sessions
                      solely as the caller; the registry owns no transaction.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; legal evidence never proves
                              payment, invoice, or settlement.
FAIL-CLOSED DECLARATION: Wrong runtime, persistence errors, corruption,
                         provenance divergence, and tenant violations reject.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import os
from typing import Any, Iterator, cast
import uuid

import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    DocumentCustodyEvent,
    DocumentCustodyEventType,
    LegalInstruction,
    LegalInstructionState,
    ReturnOfService,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
)
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
    LegalOperationsLifecycleRegistryError,
    VERSION as P2_VERSION,
)


VERSION = "v1.2.1-L8-5-LEGAL-OPERATIONS-TENANT-ENTITY-ENUMERATION-RM-CERT"
MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc)
TERMINAL_FINGERPRINT = "a" * 128


@pytest.fixture
def mongo_context() -> Iterator[tuple[Any, Any, Any]]:
    """Provide one isolated real replica-set database, or skip pre-yield only."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database = None
    try:
        hello = client.admin.command("hello")
    except PyMongoError as error:
        client.close()
        pytest.fail(
            f"P2_MONGO_RUNTIME_UNAVAILABLE:{type(error).__name__}:{error}"
        )
    if hello.get("setName") != EXPECTED_REPLICA_SET:
        client.close()
        pytest.fail(
            f"P2_MONGO_REPLICA_SET_MISMATCH:{hello.get('setName')!r}"
        )
    if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
        client.close()
        pytest.fail("P2_MONGO_WRITABLE_PRIMARY_UNAVAILABLE")
    database = client[f"legal_operations_p2_{uuid.uuid4().hex}"]
    collection = database.get_collection(
        COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    LegalOperationsLifecycleRegistry.ensure_indexes(collection)
    try:
        yield client, database, collection
    finally:
        try:
            if database is not None:
                client.drop_database(database.name)
        except PyMongoError:
            pass
        finally:
            client.close()


def _instruction(tenant_id: str, *, instruction_id: str = "instruction-1") -> LegalInstruction:
    """Build a deterministic initial P1 instruction snapshot."""
    return LegalInstruction(
        tenant_id=tenant_id,
        instruction_id=instruction_id,
        case_matter_id="matter-1",
        document_id="document-1",
        registered_at=NOW,
        evidence_reference="registration-evidence",
    )


def _terminal_attempt(
    tenant_id: str,
    *,
    attempt_id: str = "attempt-1",
    instruction_id: str = "instruction-1",
    document_id: str = "document-1",
) -> ServiceAttempt:
    """Build a complete P1 attempt chain with terminal source evidence."""
    allocated = ServiceAttempt(
        tenant_id=tenant_id,
        attempt_id=attempt_id,
        instruction_id=instruction_id,
        document_id=document_id,
        deputy_id="deputy-1",
        allocated_at=NOW,
        allocation_evidence_reference="allocation-evidence",
    )
    attempted = allocated.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference="attempt-evidence",
        occurred_at=NOW + timedelta(minutes=1),
    )
    return attempted.transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference="completion-evidence",
        evidence_fingerprint=TERMINAL_FINGERPRINT,
        occurred_at=NOW + timedelta(minutes=2),
    )


def _record(collection: Any, tenant_id: str, entity_type: str, identity: str) -> dict[str, Any]:
    """Read one raw durable record for controlled corruption restoration."""
    value = collection.find_one(
        {"tenant_id": tenant_id, "entity_type": entity_type, "entity_identity": identity}
    )
    assert value is not None
    return cast_record(value)


def cast_record(value: Any) -> dict[str, Any]:
    """Narrow a Mongo mapping for explicit test mutations."""
    assert isinstance(value, dict)
    return value


def _restore(collection: Any, original: dict[str, Any]) -> None:
    """Restore the pristine durable row after one corruption assertion."""
    assert "_id" in original
    collection.replace_one({"_id": original["_id"]}, deepcopy(original))


def test_real_indexes_and_immutable_snapshot_progression(mongo_context: Any) -> None:
    """Certify index uniqueness and two immutable snapshots for one entity."""
    _, _, collection = mongo_context
    LegalOperationsLifecycleRegistry.ensure_indexes(collection)
    indexes = {entry["name"]: entry for entry in collection.list_indexes()}
    history = indexes["legal_operations_tenant_entity_history"]
    custody = indexes["legal_operations_tenant_document_custody_history"]
    evidence = indexes["legal_operations_tenant_evidence_unique"]
    assert history["key"] == {"tenant_id": 1, "entity_type": 1, "entity_identity": 1}
    assert history.get("unique", False) is False
    assert custody["key"] == {
        "tenant_id": 1,
        "entity_type": 1,
        "p1_payload.document_id": 1,
    }
    assert custody.get("unique", False) is False
    assert evidence["key"] == {"tenant_id": 1, "evidence_identity": 1}
    assert evidence["unique"] is True

    tenant = f"tenant-{uuid.uuid4().hex}"
    initial = _instruction(tenant)
    accepted = initial.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="acceptance-evidence",
        occurred_at=NOW + timedelta(minutes=1),
    )
    LegalOperationsLifecycleRegistry.create(initial, collection)
    LegalOperationsLifecycleRegistry.create(accepted, collection)
    assert collection.count_documents({"tenant_id": tenant}) == 2
    assert initial.fingerprint != accepted.fingerprint
    initial_identity = _record(collection, tenant, "LegalInstruction", "instruction-1")["entity_identity"]
    rows = list(collection.find({"tenant_id": tenant, "entity_type": "LegalInstruction"}))
    assert len(rows) == 2
    identities = {row["evidence_identity"] for row in rows}
    assert len(identities) == 2
    for row in rows:
        hydrated = LegalOperationsLifecycleRegistry.get(tenant, row["evidence_identity"], collection)
        assert hydrated.to_dict() in (initial.to_dict(), accepted.to_dict())
    assert initial_identity == "instruction-1"


def test_real_tenant_entity_snapshot_enumeration_is_exact_and_deterministic(
    mongo_context: Any,
) -> None:
    """Certify tenant/entity enumeration across multiple immutable histories."""
    client, _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    foreign = f"tenant-{uuid.uuid4().hex}"

    first = _instruction(tenant, instruction_id="instruction-b")
    first_accepted = first.transition_to(
        LegalInstructionState.ACCEPTED,
        evidence_reference="accepted-b",
        occurred_at=NOW + timedelta(minutes=1),
    )
    second = LegalInstruction(
        tenant_id=tenant,
        instruction_id="instruction-a",
        case_matter_id="matter-2",
        document_id="document-2",
        registered_at=NOW,
        evidence_reference="registration-a",
    )
    foreign_value = LegalInstruction(
        tenant_id=foreign,
        instruction_id="instruction-a",
        case_matter_id="matter-foreign",
        document_id="document-foreign",
        registered_at=NOW,
        evidence_reference="registration-foreign",
    )
    for value in (first_accepted, foreign_value, second, first):
        LegalOperationsLifecycleRegistry.create(value, collection)

    with client.start_session() as session:
        session.start_transaction()
        snapshots = LegalOperationsLifecycleRegistry.get_tenant_entity_snapshots(
            tenant,
            "LegalInstruction",
            collection,
            session=session,
        )
        session.commit_transaction()

    assert all(type(value) is LegalInstruction for value in snapshots)
    instruction_snapshots = cast(tuple[LegalInstruction, ...], snapshots)
    assert len(snapshots) == 3
    assert [value.instruction_id for value in instruction_snapshots] == [
        "instruction-a",
        "instruction-b",
        "instruction-b",
    ]
    assert all(value.tenant_id == tenant for value in snapshots)
    assert LegalOperationsLifecycleRegistry.get_tenant_entity_snapshots(
        foreign,
        "LegalInstruction",
        collection,
    ) == (foreign_value,)
    assert LegalOperationsLifecycleRegistry.get_tenant_entity_snapshots(
        f"tenant-{uuid.uuid4().hex}",
        "LegalInstruction",
        collection,
    ) == ()
    assert P2_VERSION == (
        "v1.3.0-L8-5-LEGAL-OPERATIONS-TENANT-ENTITY-ENUMERATION"
    )


def test_real_document_custody_history_is_exact_tenant_document_scope(
    mongo_context: Any,
) -> None:
    """Certify indexed strict custody history without foreign/document leakage."""
    client, _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    foreign = f"tenant-{uuid.uuid4().hex}"
    first = DocumentCustodyEvent(
        tenant_id=tenant,
        custody_event_id="custody-1",
        document_id="document-1",
        event_type=DocumentCustodyEventType.REGISTERED,
        occurred_at=NOW,
        sequence_number=1,
        evidence_reference="registration",
    )
    second = DocumentCustodyEvent(
        tenant_id=tenant,
        custody_event_id="custody-2",
        document_id="document-1",
        event_type=DocumentCustodyEventType.RECEIVED_IN_OFFICE,
        occurred_at=NOW + timedelta(minutes=1),
        sequence_number=2,
        evidence_reference="receipt",
        to_holder_reference="office-1",
    )
    other = DocumentCustodyEvent(
        tenant_id=tenant,
        custody_event_id="custody-other",
        document_id="document-2",
        event_type=DocumentCustodyEventType.REGISTERED,
        occurred_at=NOW,
        sequence_number=1,
        evidence_reference="other-registration",
    )
    foreign_event = DocumentCustodyEvent(
        tenant_id=foreign,
        custody_event_id="custody-foreign",
        document_id="document-1",
        event_type=DocumentCustodyEventType.REGISTERED,
        occurred_at=NOW,
        sequence_number=1,
        evidence_reference="foreign-registration",
    )
    for value in (first, second, other, foreign_event):
        LegalOperationsLifecycleRegistry.create(value, collection)

    with client.start_session() as session:
        session.start_transaction()
        history = LegalOperationsLifecycleRegistry.get_document_custody_history(
            tenant,
            "document-1",
            collection,
            session=session,
        )
        session.commit_transaction()

    assert {value.fingerprint for value in history} == {
        first.fingerprint,
        second.fingerprint,
    }
    assert all(value.tenant_id == tenant for value in history)
    assert all(value.document_id == "document-1" for value in history)
    assert LegalOperationsLifecycleRegistry.get_document_custody_history(
        tenant,
        "missing-document",
        collection,
    ) == ()
    assert P2_VERSION == "v1.3.0-L8-5-LEGAL-OPERATIONS-TENANT-ENTITY-ENUMERATION"


def test_real_exact_replay_has_one_durable_row(mongo_context: Any) -> None:
    """Certify byte-identical replay without overwrite or a second row."""
    _, _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    value = _instruction(tenant)
    first = LegalOperationsLifecycleRegistry.create(value, collection)
    before = _record(collection, tenant, "LegalInstruction", "instruction-1")
    second = LegalOperationsLifecycleRegistry.create(value, collection)
    after = _record(collection, tenant, "LegalInstruction", "instruction-1")
    assert first == second == value
    assert collection.count_documents({"tenant_id": tenant}) == 1
    assert {key: before[key] for key in before if key != "_id"} == {
        key: after[key] for key in after if key != "_id"
    }


def test_real_factory_provenance_service_and_return(mongo_context: Any) -> None:
    """Certify ServiceExecution and ReturnOfService source envelopes exactly."""
    _, _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    attempt = _terminal_attempt(tenant)
    execution_at = NOW + timedelta(minutes=3)
    execution = ServiceExecution.from_attempt(
        attempt=attempt,
        service_execution_id="execution-1",
        executed_at=execution_at,
    )
    LegalOperationsLifecycleRegistry.create(attempt, collection)
    LegalOperationsLifecycleRegistry.create(execution, collection, source_attempt=attempt)
    execution_row = _record(collection, tenant, "ServiceExecution", "execution-1")
    assert execution_row["source_payload"]["attempt"] == attempt.to_dict()
    hydrated_execution = LegalOperationsLifecycleRegistry.get(
        tenant, execution_row["evidence_identity"], collection
    )
    assert hydrated_execution == execution

    returned = ReturnOfService.from_service_execution(
        instruction_id="instruction-1",
        service_execution=execution,
        return_id="return-1",
        generated_at=execution_at + timedelta(minutes=1),
    )
    LegalOperationsLifecycleRegistry.create(
        returned,
        collection,
        source_attempt=attempt,
        source_execution=execution,
    )
    return_row = _record(collection, tenant, "ReturnOfService", "return-1")
    source_execution_payload = return_row["source_payload"]["service_execution"]
    assert source_execution_payload["executed_at"] == execution_at.isoformat()
    assert datetime.fromisoformat(source_execution_payload["executed_at"]) > attempt.transition_history[-1].occurred_at
    hydrated_return = LegalOperationsLifecycleRegistry.get(
        tenant, return_row["evidence_identity"], collection
    )
    assert hydrated_return == returned


def test_real_tenant_isolation_and_corruption_rejection(mongo_context: Any) -> None:
    """Certify foreign absence and representative strict durable corruption gates."""
    _, _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    foreign = f"tenant-{uuid.uuid4().hex}"
    value = _instruction(tenant)
    LegalOperationsLifecycleRegistry.create(value, collection)
    original = _record(collection, tenant, "LegalInstruction", "instruction-1")
    identity = original["evidence_identity"]
    assert LegalOperationsLifecycleRegistry.get(tenant, identity, collection) == value
    with pytest.raises(LegalOperationsLifecycleRegistryError, match="M2_EVIDENCE_NOT_FOUND"):
        LegalOperationsLifecycleRegistry.get(foreign, identity, collection)

    mutations = (
        ("p1_fingerprint", "b" * 128, "M2_P1_FINGERPRINT_MISMATCH"),
        ("evidence_identity", "c" * 128, "M2_EVIDENCE_IDENTITY_MISMATCH"),
        ("p1_version", "unsupported", "M2_P1_VERSION_UNSUPPORTED"),
        ("p1_schema", "unsupported", "M2_P1_VERSION_UNSUPPORTED"),
    )
    for field, replacement, code in mutations:
        changed = deepcopy(original)
        changed[field] = replacement
        if field in {"p1_version", "p1_schema"}:
            changed["p1_payload"][field.removeprefix("p1_")] = replacement
        _restore(collection, changed)
        lookup = replacement if field == "evidence_identity" else identity
        with pytest.raises(LegalOperationsLifecycleRegistryError, match=code):
            LegalOperationsLifecycleRegistry.get(tenant, lookup, collection)
        _restore(collection, original)

    attempt = _terminal_attempt(tenant, attempt_id="attempt-corrupt")
    execution = ServiceExecution.from_attempt(
        attempt=attempt,
        service_execution_id="execution-corrupt",
        executed_at=NOW + timedelta(minutes=3),
    )
    returned = ReturnOfService.from_service_execution(
        instruction_id="instruction-1",
        service_execution=execution,
        return_id="return-corrupt",
        generated_at=NOW + timedelta(minutes=4),
    )
    LegalOperationsLifecycleRegistry.create(attempt, collection)
    LegalOperationsLifecycleRegistry.create(execution, collection, source_attempt=attempt)
    LegalOperationsLifecycleRegistry.create(
        returned, collection, source_attempt=attempt, source_execution=execution
    )
    execution_row = _record(collection, tenant, "ServiceExecution", "execution-corrupt")
    changed_execution = deepcopy(execution_row)
    changed_execution["source_fingerprint"] = "d" * 128
    _restore(collection, changed_execution)
    with pytest.raises(LegalOperationsLifecycleRegistryError, match="M2_EVIDENCE_IDENTITY_MISMATCH"):
        LegalOperationsLifecycleRegistry.get(tenant, execution_row["evidence_identity"], collection)
    _restore(collection, execution_row)

    return_row = _record(collection, tenant, "ReturnOfService", "return-corrupt")
    changed_return = deepcopy(return_row)
    changed_return["source_payload"]["service_execution"]["executed_at"] = attempt.transition_history[-1].occurred_at.isoformat()
    _restore(collection, changed_return)
    with pytest.raises(LegalOperationsLifecycleRegistryError, match="M2_FACTORY_SOURCE_INVALID"):
        LegalOperationsLifecycleRegistry.get(tenant, return_row["evidence_identity"], collection)
    _restore(collection, return_row)


def test_real_caller_owned_transaction_abort_and_commit(mongo_context: Any) -> None:
    """Certify registry participation without transaction ownership."""
    client, _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    value = _instruction(tenant)
    with client.start_session() as session:
        session.start_transaction()
        LegalOperationsLifecycleRegistry.create(value, collection, session=session)
        assert collection.count_documents({"tenant_id": tenant}, session=session) == 1
        session.abort_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 0

    with client.start_session() as session:
        session.start_transaction()
        LegalOperationsLifecycleRegistry.create(value, collection, session=session)
        session.commit_transaction()
    assert collection.count_documents({"tenant_id": tenant}) == 1


def test_real_persisted_records_have_no_financial_authority_fields(mongo_context: Any) -> None:
    """Certify legal evidence does not become payment or settlement authority."""
    _, _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    value = _instruction(tenant)
    LegalOperationsLifecycleRegistry.create(value, collection)
    document = _record(collection, tenant, "LegalInstruction", "instruction-1")

    forbidden = {"payment", "settlement", "paid_state", "refund", "invoice", "billing_execution"}

    def key_names(item: Any) -> set[str]:
        if isinstance(item, dict):
            names = set(item)
            for child in item.values():
                names.update(key_names(child))
            return names
        if isinstance(item, list):
            names: set[str] = set()
            for child in item:
                names.update(key_names(child))
            return names
        return set()

    assert forbidden.isdisjoint(key_names(document))


# ARTIFACT: test_legal_operations_lifecycle_registry_real_mongo.py
# VERSION: v1.2.1-L8-5-LEGAL-OPERATIONS-TENANT-ENTITY-ENUMERATION-RM-CERT
# AUTHORITY BOUNDARY: host-backed P2 persistence, tenant-entity enumeration, and strict hydration certificate only.
# TENANT POSTURE: UUID-isolated explicit tenant scope; foreign records disclose nothing.
# FAIL-CLOSED POSTURE: unavailable/wrong host runtime and corrupt durable evidence fail certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT