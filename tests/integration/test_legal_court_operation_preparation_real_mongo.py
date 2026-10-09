"""Real-Mongo certificate for the immutable Court operation preparation registry.

TITLE: WILSY OS Legal Court Operation Preparation Real-Mongo Certificate
VERSION: v1.0.0-L9C12-P1R-COURT-OPERATION-PREPARATION-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify the published P1 preparation domain and registry against a
         writable sanctioned replica set using one UUID-isolated disposable
         database.  The certificate proves persistence, replay, rollback,
         strict hydration, tenant/lineage isolation and append-only posture;
         it never asserts a judicial or external Court result.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_court_operation_preparation_real_mongo.py
COLLABORATION / OWNERSHIP: P1 domain owns immutable preparation truth; P1
                            registry owns only caller-transaction persistence
                            and reads; this file owns disposable runtime
                            evidence. Court ingress and external evidence are
                            later authorities.
CERTIFICATION / UPDATE DATE: 2026-09-28
CHANGELOG: v1.0.0-L9C12-P1R certifies sanctioned topology, physical replay
           and history indexes, transaction ownership, durable commit,
           rollback, BSON normalization, collision rejection, strict
           corruption handling and tenant/lineage isolation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque references and SHA3-512
                             fingerprints only; no credentials or PII.
TENANT BOUNDARY: Every registry lookup and history read is explicitly scoped.
AUTHORITY BOUNDARY: Internal Court filing preparation only; no filing,
                    acceptance, issuance, service, hearing, order, admission,
                    attorney-of-record, IAM or financial authority.
TRANSACTION BOUNDARY: This certificate owns sessions and commit/abort; the
                      registry must never start, commit, abort or retry one.
FAIL-CLOSED DECLARATION: Topology, index drift, corruption, collision,
                         rollback or isolation failures fail certification.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from dataclasses import fields
import inspect
import os
from pathlib import Path
from typing import Any, Iterator, cast
import uuid

import pytest
from pymongo import MongoClient, version as pymongo_version
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_court_operation_preparation import (
    LegalCourtOperationPreparation,
    LegalCourtOperationPreparationState,
    LegalCourtOperationType,
)
from tools.eos.legal_operations.registry.legal_court_operation_preparation_registry import (
    COLLECTION,
    FINGERPRINT_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    MATTER_OPERATION_HISTORY_INDEX_NAME,
    MATTER_REPRESENTATION_HISTORY_INDEX_NAME,
    OPERATION_PREPARATION_ID_INDEX_NAME,
    TARGET_COURT_HISTORY_INDEX_NAME,
    LegalCourtOperationPreparationRegistryConflictError,
    LegalCourtOperationPreparationRegistryNotFoundError,
    LegalCourtOperationPreparationRegistryPersistedRecordInvalidError,
    LegalCourtOperationPreparationRegistryTransactionRequiredError,
    ensure_indexes,
    get_court_operation_preparation,
    get_court_operation_preparation_by_fingerprint,
    get_court_operation_preparation_by_idempotency_key,
    list_court_operation_preparations_for_matter,
    persist_court_operation_preparation,
)
import tools.eos.legal_operations.registry.legal_court_operation_preparation_registry as preparation_registry


MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
EXPECTED_MONGO_VERSION = "7.0.37"
BASE = datetime(2026, 9, 28, 12, 0, 0, 123456, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128


class MongoContext:
    """Handles for one UUID-isolated disposable P1R database."""

    def __init__(self, client: MongoClient[Any], database: Any, collection: Any) -> None:
        self.client = client
        self.database = database
        self.collection = collection


@pytest.fixture()
def mongo_context() -> Iterator[MongoContext]:
    """Yield a writable sanctioned database and drop only that database."""
    client: MongoClient[Any] = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=3000,
        connectTimeoutMS=3000,
        retryWrites=True,
        tz_aware=True,
    )
    database: Any = None
    try:
        try:
            hello = client.admin.command("hello")
            server_version = client.server_info().get("version")
        except PyMongoError as error:
            pytest.skip(f"real Mongo unavailable for operator runtime: {type(error).__name__}")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary", hello.get("ismaster")) is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        assert server_version == EXPECTED_MONGO_VERSION
        database_name = f"wilsy_l9c12_p1r_{uuid.uuid4().hex}"
        assert len(database_name) <= 63
        assert database_name != "wilsy"
        database = client[database_name]
        collection = database.get_collection(COLLECTION)
        ensure_indexes(collection)
        yield MongoContext(client, database, collection)
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def preparation(**overrides: object) -> LegalCourtOperationPreparation:
    """Construct valid production P1 truth through the canonical constructor."""
    values: dict[str, object] = {
        "tenant_id": "tenant-p1r-court",
        "case_matter_id": "matter-p1r-court",
        "matter_fingerprint": HEX_A,
        "final_representation_id": "final-representation:p1r-court",
        "final_representation_fingerprint": HEX_B,
        "operation_type": LegalCourtOperationType.COURT_FILING_PREPARATION,
        "target_court_reference": "court:opaque-p1r",
        "target_jurisdiction_reference": "jurisdiction:opaque-gp",
        "document_evidence_lineage": ("document:evidence-2", "document:evidence-1"),
        "requested_scope_capabilities": ("COURT_FILING_PREPARATION",),
        "preparation_state": LegalCourtOperationPreparationState.PREPARATION_REQUIRED,
        "source_evidence_reference": "evidence:preparation-p1r",
        "source_evidence_fingerprint": HEX_C,
        "provenance_reference": "provenance:p1r-court",
        "prepared_at": BASE,
        "occurred_at": BASE + timedelta(minutes=1),
        "idempotency_key": "idempotency:p1r-court",
    }
    values.update(overrides)
    return LegalCourtOperationPreparation(**cast(Any, values))


def commit_value(context: MongoContext, value: LegalCourtOperationPreparation) -> LegalCourtOperationPreparation:
    """Persist one value in a transaction owned by this certificate."""
    with context.client.start_session() as session:
        with session.start_transaction():
            result = persist_court_operation_preparation(value, context.collection, session=session)
    return result


def read_by_id(context: MongoContext, value: LegalCourtOperationPreparation) -> LegalCourtOperationPreparation:
    """Hydrate one committed value through a fresh caller-owned session."""
    with context.client.start_session() as session:
        with session.start_transaction():
            return get_court_operation_preparation(value.tenant_id, value.operation_preparation_id, context.collection, session=session)


def test_topology_indexes_and_transaction_boundaries(mongo_context: MongoContext) -> None:
    context = mongo_context
    hello = context.client.admin.command("hello")
    assert hello["setName"] == EXPECTED_REPLICA_SET
    assert hello.get("isWritablePrimary") is True
    assert hello.get("logicalSessionTimeoutMinutes") is not None
    assert pymongo_version
    indexes = {item["name"]: item for item in context.collection.list_indexes()}
    expected = {
        OPERATION_PREPARATION_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        MATTER_OPERATION_HISTORY_INDEX_NAME,
        MATTER_REPRESENTATION_HISTORY_INDEX_NAME,
        TARGET_COURT_HISTORY_INDEX_NAME,
    }
    assert expected.issubset(indexes)
    assert all("expireAfterSeconds" not in item for item in indexes.values())
    assert indexes[OPERATION_PREPARATION_ID_INDEX_NAME]["unique"] is True
    assert indexes[FINGERPRINT_INDEX_NAME]["unique"] is True
    assert indexes[IDEMPOTENCY_INDEX_NAME]["unique"] is True
    assert list(indexes[OPERATION_PREPARATION_ID_INDEX_NAME]["key"].items()) == [("tenant_id", 1), ("operation_preparation_id", 1)]
    assert list(indexes[FINGERPRINT_INDEX_NAME]["key"].items()) == [("tenant_id", 1), ("fingerprint", 1)]
    assert list(indexes[IDEMPOTENCY_INDEX_NAME]["key"].items()) == [("tenant_id", 1), ("idempotency_key", 1)]
    assert list(indexes[MATTER_OPERATION_HISTORY_INDEX_NAME]["key"].items()) == [("tenant_id", 1), ("case_matter_id", 1), ("operation_type", 1), ("occurred_at", 1)]
    assert list(indexes[MATTER_REPRESENTATION_HISTORY_INDEX_NAME]["key"].items()) == [("tenant_id", 1), ("case_matter_id", 1), ("final_representation_id", 1), ("occurred_at", 1)]
    assert list(indexes[TARGET_COURT_HISTORY_INDEX_NAME]["key"].items()) == [("tenant_id", 1), ("target_court_reference", 1), ("occurred_at", 1)]
    value = preparation()
    with pytest.raises(LegalCourtOperationPreparationRegistryTransactionRequiredError):
        persist_court_operation_preparation(value, context.collection, session=None)
    with context.client.start_session() as session:
        with pytest.raises(LegalCourtOperationPreparationRegistryTransactionRequiredError):
            persist_court_operation_preparation(value, context.collection, session=session)
        with session.start_transaction():
            assert persist_court_operation_preparation(value, context.collection, session=session) == value
            assert context.collection.count_documents({}, session=session) == 1


def test_commit_durability_and_all_exact_read_apis(mongo_context: MongoContext) -> None:
    context = mongo_context
    value = preparation()
    assert commit_value(context, value) == value
    assert read_by_id(context, value) == value
    with context.client.start_session() as session:
        with session.start_transaction():
            assert get_court_operation_preparation_by_fingerprint(value.tenant_id, value.fingerprint, context.collection, session=session) == value
            assert get_court_operation_preparation_by_idempotency_key(value.tenant_id, value.idempotency_key, context.collection, session=session) == value
    assert context.collection.count_documents({}) == 1


def test_abort_rolls_back_and_registry_owns_no_transaction_lifecycle(mongo_context: MongoContext) -> None:
    context = mongo_context
    value = preparation()
    with context.client.start_session() as session:
        with session.start_transaction():
            persist_court_operation_preparation(value, context.collection, session=session)
            session.abort_transaction()
    with context.client.start_session() as session:
        with session.start_transaction():
            assert context.collection.count_documents({}, session=session) == 0
    source = Path("tools/eos/legal_operations/registry/legal_court_operation_preparation_registry.py").read_text()
    assert "start_transaction" not in source and "commit_transaction" not in source and "abort_transaction" not in source


def test_exact_replay_is_one_append_only_row(mongo_context: MongoContext) -> None:
    context = mongo_context
    value = preparation()
    assert commit_value(context, value) == value
    assert commit_value(context, value) == value
    assert context.collection.count_documents({}) == 1
    source = Path("tools/eos/legal_operations/registry/legal_court_operation_preparation_registry.py").read_text()
    assert "update_one" not in source and "replace_one" not in source and "delete_one" not in source


@pytest.mark.parametrize("identity", ["operation_preparation_id", "fingerprint", "idempotency_key"])
def test_divergent_identity_collisions_fail_closed(mongo_context: MongoContext, identity: str) -> None:
    context = mongo_context
    first = preparation()
    commit_value(context, first)
    second = preparation(
        target_court_reference="court:divergent",
        idempotency_key="idempotency:divergent",
        source_evidence_reference="evidence:divergent",
    )
    object.__setattr__(second, identity, getattr(first, identity))
    with pytest.raises(LegalCourtOperationPreparationRegistryConflictError):
        commit_value(context, second)
    assert context.collection.count_documents({}) == 1


@pytest.mark.parametrize("duplicate_field", ["operation_preparation_id", "fingerprint", "idempotency_key"])
def test_database_unique_indexes_enforce_each_replay_identity(mongo_context: MongoContext, duplicate_field: str) -> None:
    context = mongo_context
    value = preparation()
    commit_value(context, value)
    raw = value.to_dict()
    raw["operation_preparation_id"] = value.operation_preparation_id if duplicate_field == "operation_preparation_id" else "court-operation-preparation:raw-unique"
    raw["fingerprint"] = value.fingerprint if duplicate_field == "fingerprint" else HEX_D
    raw["idempotency_key"] = value.idempotency_key if duplicate_field == "idempotency_key" else "idempotency:raw-unique"
    with pytest.raises(DuplicateKeyError):
        with context.client.start_session() as session:
            with session.start_transaction():
                context.collection.insert_one(raw, session=session)
    assert context.collection.count_documents({}) == 1


@pytest.mark.parametrize("state", list(LegalCourtOperationPreparationState))
def test_all_six_internal_states_round_trip_without_judicial_claims(mongo_context: MongoContext, state: LegalCourtOperationPreparationState) -> None:
    context = mongo_context
    value = preparation(
        preparation_state=state,
        idempotency_key=f"idempotency:state:{state.value.lower()}",
        source_evidence_reference=f"evidence:state:{state.value.lower()}",
    )
    assert commit_value(context, value) == value
    payload = read_by_id(context, value).to_dict()
    assert payload["preparation_state"] == state
    assert payload["operation_type"] == LegalCourtOperationType.COURT_FILING_PREPARATION
    assert not {"filed_at", "accepted_at", "issued_at", "served_at", "hearing_result", "judicial_order", "attorney_of_record", "professional_admission", "court_online_credentials"} & set(payload)


def test_bson_lineage_normalization_and_strict_hydration(mongo_context: MongoContext) -> None:
    context = mongo_context
    value = preparation()
    commit_value(context, value)
    row = context.collection.find_one({"operation_preparation_id": value.operation_preparation_id})
    assert isinstance(row["document_evidence_lineage"], list)
    assert isinstance(row["requested_scope_capabilities"], list)
    assert read_by_id(context, value) == value
    context.collection.update_one({}, {"$set": {"document_evidence_lineage": "malformed"}})
    with context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError):
                get_court_operation_preparation(value.tenant_id, value.operation_preparation_id, context.collection, session=session)
    context.collection.update_one({}, {"$set": {"document_evidence_lineage": list(value.document_evidence_lineage), "fingerprint": "0" * 128}})
    with context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError):
                get_court_operation_preparation(value.tenant_id, value.operation_preparation_id, context.collection, session=session)


def test_missing_required_field_and_corrupt_identity_are_rejected_then_restored(mongo_context: MongoContext) -> None:
    context = mongo_context
    value = preparation()
    commit_value(context, value)
    context.collection.update_one({}, {"$unset": {"source_evidence_reference": ""}})
    with context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError):
                get_court_operation_preparation(value.tenant_id, value.operation_preparation_id, context.collection, session=session)
    context.collection.update_one({}, {"$set": {"source_evidence_reference": value.source_evidence_reference}})
    context.collection.update_one({}, {"$set": {"operation_preparation_id": "malformed"}})
    with context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError):
                get_court_operation_preparation(value.tenant_id, "malformed", context.collection, session=session)
    context.collection.update_one({}, {"$set": {"operation_preparation_id": value.operation_preparation_id}})
    assert read_by_id(context, value) == value


def test_history_is_tenant_matter_and_representation_isolated_and_ordered(mongo_context: MongoContext) -> None:
    context = mongo_context
    first = preparation(prepared_at=BASE + timedelta(minutes=2), occurred_at=BASE + timedelta(minutes=3), idempotency_key="idempotency:history:first", source_evidence_reference="evidence:history:first")
    second = preparation(prepared_at=BASE, occurred_at=BASE + timedelta(minutes=1), idempotency_key="idempotency:history:second", source_evidence_reference="evidence:history:second", target_court_reference="court:opaque-second")
    tenant_b = preparation(tenant_id="tenant-p1r-other", idempotency_key="idempotency:history:tenant-b", source_evidence_reference="evidence:history:tenant-b")
    other_matter = preparation(case_matter_id="matter-p1r-other", idempotency_key="idempotency:history:matter-b", source_evidence_reference="evidence:history:matter-b")
    for value in (first, tenant_b, other_matter, second):
        commit_value(context, value)
    with context.client.start_session() as session:
        with session.start_transaction():
            assert list_court_operation_preparations_for_matter(first.tenant_id, first.case_matter_id, operation_type=LegalCourtOperationType.COURT_FILING_PREPARATION, preparation_collection=context.collection, session=session) == (second, first)
            assert list_court_operation_preparations_for_matter("tenant-p1r-other", first.case_matter_id, operation_type=LegalCourtOperationType.COURT_FILING_PREPARATION, preparation_collection=context.collection, session=session) == (tenant_b,)
            assert list_court_operation_preparations_for_matter(first.tenant_id, "matter-p1r-other", operation_type=LegalCourtOperationType.COURT_FILING_PREPARATION, preparation_collection=context.collection, session=session) == (other_matter,)
            with pytest.raises(LegalCourtOperationPreparationRegistryNotFoundError):
                get_court_operation_preparation("tenant-p1r-other", first.operation_preparation_id, context.collection, session=session)
    assert context.collection.count_documents({}) == 4


def test_history_limit_and_scope_are_fail_closed(mongo_context: MongoContext) -> None:
    context = mongo_context
    first = preparation()
    second = preparation(idempotency_key="idempotency:history:limit", source_evidence_reference="evidence:history:limit", prepared_at=BASE + timedelta(minutes=2), occurred_at=BASE + timedelta(minutes=3))
    commit_value(context, first)
    commit_value(context, second)
    with context.client.start_session() as session:
        with session.start_transaction():
            with pytest.raises(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError):
                list_court_operation_preparations_for_matter(first.tenant_id, first.case_matter_id, operation_type=LegalCourtOperationType.COURT_FILING_PREPARATION, preparation_collection=context.collection, session=session, limit=1)


def test_preparation_only_scope_and_external_authority_boundaries_are_not_writable(mongo_context: MongoContext) -> None:
    context = mongo_context
    value = preparation()
    assert value.requested_scope_capabilities == ("COURT_FILING_PREPARATION",)
    assert value.operation_type is LegalCourtOperationType.COURT_FILING_PREPARATION
    assert context.database.list_collection_names() == [COLLECTION]
    domain_fields = {item.name for item in fields(LegalCourtOperationPreparation)}
    forbidden_fields = {
        "court_online_credentials", "username", "password", "token", "session_secret",
        "filed_at", "accepted_at", "issued_at", "served_at", "heard_at", "granted_at",
        "filing_success", "external_submission_id", "attorney_of_record", "professional_admission",
        "judicial_order", "payment", "payment_execution", "settlement", "settlement_execution",
        "iam_assignment", "iam_mutation", "p24_mutation", "p25_mutation",
    }
    assert domain_fields.isdisjoint(forbidden_fields)
    assert domain_fields == {
        "schema", "preparation_version", "operation_preparation_id", "tenant_id", "case_matter_id",
        "matter_fingerprint", "final_representation_id", "final_representation_fingerprint",
        "operation_type", "target_court_reference", "target_jurisdiction_reference",
        "document_evidence_lineage", "requested_scope_capabilities", "preparation_state",
        "source_evidence_reference", "source_evidence_fingerprint", "provenance_reference",
        "prepared_at", "occurred_at", "idempotency_key", "fingerprint",
    }
    registry_public_api = {name for name in dir(preparation_registry.LegalCourtOperationPreparationRegistry) if not name.startswith("_")}
    assert registry_public_api == {
        "ensure_indexes", "persist_court_operation_preparation", "get_court_operation_preparation",
        "get_court_operation_preparation_by_fingerprint", "get_court_operation_preparation_by_idempotency_key",
        "list_court_operation_preparations_for_matter",
    }
    assert all("session" in inspect.signature(getattr(preparation_registry, name)).parameters for name in (
        "persist_court_operation_preparation", "get_court_operation_preparation",
        "get_court_operation_preparation_by_fingerprint", "get_court_operation_preparation_by_idempotency_key",
        "list_court_operation_preparations_for_matter",
    ))
    assert preparation_registry.COLLECTION == "legal_court_operation_preparations"
    assert set(context.database.list_collection_names()) == {preparation_registry.COLLECTION}
    assert context.collection.count_documents({}) == 0


# ARTIFACT: test_legal_court_operation_preparation_real_mongo.py
# VERSION: v1.0.0-L9C12-P1R-COURT-OPERATION-PREPARATION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable real-Mongo preparation certificate only
# FAIL-CLOSED POSTURE: no canonical database, external Court authority or downstream writes
# END OF WILSY OS SOVEREIGN ARTIFACT
