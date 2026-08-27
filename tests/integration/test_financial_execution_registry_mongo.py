"""WILSY OS Kennel EOS real-Mongo registry certification.

VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TRUTH-REGISTRY-REAL-MONGO-CERT
TITLE: FinancialExecutionTruthRegistry real-Mongo certification
AUTHORITY: Wilsy OS Core Governance
ARCHITECTURE LOCK: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
FINANCIAL AUTHORITY: Kennel EOS exclusively owns execution truth.
SCOPE: persistence semantics only; provider execution and settlement excluded.
CHANGELOG: v1.0.0 establishes real replica-set persistence proofs against registry v1.0.4 caller-owned transaction replay correction.
DOMAIN CONTRACT VERSION: v1.0.1-KENNEL-FINANCIAL-EXECUTION-TRUTH-DOMAIN-PERSISTENCE-HYDRATION
DOMAIN CONTRACT COMMIT: 6783d523efea6c311453c794afca6b0520777c0a
DOMAIN SHA3-512: d268c94813636d65605079b6939d1dadb1cb34d2cce6ddf62c8ecd2f2582175de171dacca3698551768706ece096018df96dcc9f7684f850c9f9e156a393dc17
REGISTRY CONTRACT VERSION: v1.0.4-KENNEL-FINANCIAL-EXECUTION-TRUTH-REGISTRY-CALLER-TRANSACTION-REPLAY
REGISTRY CONTRACT COMMIT: a5cec760cdb03f7b3d88a3869f2cf7bf379c1d0d
REGISTRY GIT BLOB: 5ed7c3851e5f580311c4cf0e6981c2dca6edb9e3
REGISTRY SHA3-512: f20fc1d2c932a2663f6832d68db777efea864a68318f5fce263ae514705cd75e3a0d31a8c5ab92e7b218f01c270cc38709a78e9ee5de0e9d25d6b261a28dd994
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_financial_execution_registry_mongo.py
PRIMARY CONTRACT: immutable FinancialExecutionTruth persistence
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder); Codex (AI engineering)
CERTIFICATION DATE: 2026-08-27
COMPLIANCE: POPIA §19 | GDPR Art. 32 | SOC2 CC7.2
SECURITY / PRIVACY POSTURE: opaque references only; no credentials
TENANT BOUNDARY: all APIs require tenant scope
TRANSACTION BOUNDARY: caller owns session lifecycle
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS only
REAL-MONGO ENVIRONMENT CONTRACT: TEST_VENDOR_MONGO_URI; writable replica set required
"""
from __future__ import annotations
import hashlib
import json
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import pytest
from pymongo import ASCENDING, MongoClient
from pymongo.errors import DuplicateKeyError
from tools.eos.kennel.domain.financial_execution import FinancialExecutionStatus, FinancialExecutionTruth
from tools.eos.kennel.registry.financial_execution_registry import (
    COLLECTION, FinancialExecutionCreateConflictError, FinancialExecutionCreateOutcome,
    FinancialExecutionIdempotencyKeyReuseError, FinancialExecutionPersistedRecordInvalidError,
    FinancialExecutionRegistryError, FinancialExecutionTruthRegistry,
)

def make_execution_truth(**overrides: object) -> FinancialExecutionTruth:
    values: dict[str, object] = {"execution_truth_id":"execution-a","tenant_id":"tenant-a","payable_id":"payable-a","release_authorization_id":"release-a","provider":"PAYSHAP","provider_execution_reference":"provider-execution-a","execution_status":FinancialExecutionStatus.SUBMITTED,"executed_amount_minor":100,"currency":"ZAR","executed_at":datetime(2026,1,1,tzinfo=timezone.utc),"created_at":datetime(2026,1,2,tzinfo=timezone.utc),"payment_destination_reference":"destination-ref-a","provider_evidence_reference":"provider-evidence-a","execution_command_fingerprint":"a"*128,"execution_evidence_fingerprint":"b"*128}
    values.update(overrides)
    return FinancialExecutionTruth(**values)  # type: ignore[arg-type]

@pytest.fixture
def mongo_db():
    uri = os.environ.get("TEST_VENDOR_MONGO_URI")
    assert uri, "TEST_VENDOR_MONGO_URI is required"
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    hello = client.admin.command("hello")
    assert hello.get("isWritablePrimary") is True
    assert hello.get("setName") == "wilsyVendorCertRS"
    name = f"kennel_execution_registry_cert_{uuid.uuid4().hex}"
    db = client[name]
    try:
        yield client, db
    finally:
        client.drop_database(name)
        client.close()

def test_six_indexes_and_exact_replay(mongo_db):
    _, db = mongo_db; c = db[COLLECTION]; FinancialExecutionTruthRegistry.ensure_indexes(c)
    indexes = {i["name"]: i for i in c.list_indexes()}
    expected = {"tenant_execution_truth_identity_unique":[("tenant_id",1),("execution_truth_id",1)],"tenant_payable_execution_create_idempotency_unique":[("tenant_id",1),("payable_id",1),("create_idempotency_key",1)],"tenant_provider_execution_timeline":[("tenant_id",1),("provider",1),("provider_execution_reference",1),("executed_at",1),("execution_truth_id",1)],"tenant_release_authorization_execution_timeline":[("tenant_id",1),("release_authorization_id",1),("executed_at",1),("execution_truth_id",1)],"tenant_payable_execution_timeline":[("tenant_id",1),("payable_id",1),("executed_at",1),("execution_truth_id",1)],"tenant_execution_status_timeline":[("tenant_id",1),("execution_status",1),("executed_at",1),("execution_truth_id",1)]}
    for name, keys in expected.items(): assert list(indexes[name]["key"].items()) == keys
    assert indexes["tenant_execution_truth_identity_unique"].get("unique") is True and indexes["tenant_payable_execution_create_idempotency_unique"].get("unique") is True
    assert indexes["tenant_provider_execution_timeline"].get("unique") is not True
    truth = make_execution_truth(); first = FinancialExecutionTruthRegistry.create(truth,"key-a",c); replay = FinancialExecutionTruthRegistry.create(truth,"key-a",c)
    assert first.outcome is FinancialExecutionCreateOutcome.CREATED and replay.outcome is FinancialExecutionCreateOutcome.IDEMPOTENT_REPLAY and replay.execution_truth == truth
    assert c.count_documents({"tenant_id":"tenant-a","payable_id":"payable-a"}) == 1
    payload = {"execution_truth":truth.evidence_payload(),"create_idempotency_key":"key-a"}; digest = hashlib.sha3_512(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest(); row = c.find_one({"execution_truth_id":"execution-a"}); assert row and row["create_idempotency_key"] == "key-a" and row["create_fingerprint"] == digest and len(row["create_fingerprint"]) == 128 and all(ch in "0123456789abcdef" for ch in row["create_fingerprint"])

def test_timelines_isolation_and_collection_boundary(mongo_db):
    _, db = mongo_db; c = db[COLLECTION]; FinancialExecutionTruthRegistry.ensure_indexes(c)
    for i, status in enumerate(FinancialExecutionStatus):
        if status is FinancialExecutionStatus.FAILED: continue
        FinancialExecutionTruthRegistry.create(make_execution_truth(execution_truth_id=f"e-{i}",execution_status=status,executed_at=datetime(2026,1,i+1,tzinfo=timezone.utc),created_at=datetime(2026,1,i+2,tzinfo=timezone.utc)),f"k-{i}",c)
    provider_rows = FinancialExecutionTruthRegistry.list_for_provider_execution("tenant-a","PAYSHAP","provider-execution-a",collection=c)
    assert [x.execution_truth_id for x in provider_rows] == ["e-0","e-1","e-2"]
    assert {x.execution_status for x in provider_rows} == {FinancialExecutionStatus.SUBMITTED, FinancialExecutionStatus.ACCEPTED, FinancialExecutionStatus.EXECUTED}
    assert len(FinancialExecutionTruthRegistry.list_for_payable("tenant-a","payable-a",collection=c)) == 3
    assert len(FinancialExecutionTruthRegistry.list_for_release_authorization("tenant-a","release-a",collection=c)) == 3
    assert not {"payments","vendor_bills","settlements"}.intersection(db.list_collection_names())

def test_conflicts_corruption_and_transaction_lifecycle(mongo_db):
    client, db = mongo_db; c = db[COLLECTION]; FinancialExecutionTruthRegistry.ensure_indexes(c); truth = make_execution_truth(); FinancialExecutionTruthRegistry.create(truth,"key-a",c)
    with pytest.raises(FinancialExecutionIdempotencyKeyReuseError): FinancialExecutionTruthRegistry.create(make_execution_truth(executed_amount_minor=101),"key-a",c)
    assert c.count_documents({}) == 1
    with pytest.raises(FinancialExecutionCreateConflictError): FinancialExecutionTruthRegistry.create(make_execution_truth(payable_id="other"),"key-b",c)
    c.update_one({"execution_truth_id":"execution-a"},{"$set":{"currency":"zar"}})
    with pytest.raises(FinancialExecutionPersistedRecordInvalidError): FinancialExecutionTruthRegistry.create(truth,"key-a",c)
    c.delete_many({}); s=client.start_session(); s.start_transaction(); FinancialExecutionTruthRegistry.create(truth,"key-a",c,session=s); assert FinancialExecutionTruthRegistry.get("tenant-a","execution-a",c,session=s)==truth; s.abort_transaction(); s.end_session(); assert c.count_documents({})==0

def test_bounded_reads_and_session_commit(mongo_db):
    client, db = mongo_db; c = db[COLLECTION]; FinancialExecutionTruthRegistry.ensure_indexes(c); truth = make_execution_truth(); s=client.start_session(); s.start_transaction(); FinancialExecutionTruthRegistry.create(truth,"key-a",c,session=s); s.commit_transaction(); s.end_session(); assert FinancialExecutionTruthRegistry.get_by_idempotency_key("tenant-a","payable-a","key-a",c)==truth
    assert len(FinancialExecutionTruthRegistry.list_for_payable("tenant-a","payable-a",1,c)) == 1
    assert len(FinancialExecutionTruthRegistry.list_for_payable("tenant-a","payable-a",250,c)) == 1
    for limit in (0,-1,251,True,"10",None):
        with pytest.raises(FinancialExecutionRegistryError): FinancialExecutionTruthRegistry.list_for_payable("tenant-a","payable-a",limit,c)  # type: ignore[arg-type]

def test_scope_validation_and_metadata_corruption(mongo_db):
    _, db = mongo_db; c = db[COLLECTION]; FinancialExecutionTruthRegistry.ensure_indexes(c); truth = make_execution_truth(); FinancialExecutionTruthRegistry.create(truth, "key-a", c)
    assert FinancialExecutionTruthRegistry.get("tenant-a", "execution-a", c) == truth
    assert FinancialExecutionTruthRegistry.get("tenant-b", "execution-a", c) is None
    assert FinancialExecutionTruthRegistry.get_by_idempotency_key("tenant-a", "payable-a", "key-a", c) == truth
    assert FinancialExecutionTruthRegistry.get_by_idempotency_key("tenant-b", "payable-a", "key-a", c) is None
    assert FinancialExecutionTruthRegistry.get_by_idempotency_key("tenant-a", "other", "key-a", c) is None
    scoped = [
        (make_execution_truth(payable_id="payable-b", execution_truth_id="execution-b"), "tenant-a", "payable-b"),
        (make_execution_truth(tenant_id="tenant-b", execution_truth_id="execution-c"), "tenant-b", "payable-a"),
    ]
    for item, tenant, payable in scoped:
        assert FinancialExecutionTruthRegistry.create(item, "key-a", c).outcome is FinancialExecutionCreateOutcome.CREATED
        assert FinancialExecutionTruthRegistry.get_by_idempotency_key(tenant, payable, "key-a", c) == item
    for call in (lambda: FinancialExecutionTruthRegistry.get(" ", "execution-a", c), lambda: FinancialExecutionTruthRegistry.get("tenant-a", " ", c), lambda: FinancialExecutionTruthRegistry.get_by_idempotency_key(" ", "payable-a", "key-a", c), lambda: FinancialExecutionTruthRegistry.get_by_idempotency_key("tenant-a", " ", "key-a", c), lambda: FinancialExecutionTruthRegistry.get_by_idempotency_key("tenant-a", "payable-a", " ", c), lambda: FinancialExecutionTruthRegistry.list_for_provider_execution(" ", "PAYSHAP", "x", collection=c), lambda: FinancialExecutionTruthRegistry.list_for_payable("tenant-a", " ", collection=c), lambda: FinancialExecutionTruthRegistry.list_for_release_authorization("tenant-a", " ", collection=c)):
        with pytest.raises(FinancialExecutionRegistryError): call()
    for update in ({"create_fingerprint":"bad"},{"create_fingerprint":None},{"create_idempotency_key":" key-a "}):
        c.update_one({"execution_truth_id":"execution-a"},{"$set":update});
        with pytest.raises(FinancialExecutionPersistedRecordInvalidError): FinancialExecutionTruthRegistry.create(truth, "key-a", c)
        c.update_one({"execution_truth_id":"execution-a"},{"$set":{"create_fingerprint":"0"*128,"create_idempotency_key":"key-a"}})

def test_cross_session_uncommitted_and_timeline_reads(mongo_db):
    client, db = mongo_db; c = db[COLLECTION]; FinancialExecutionTruthRegistry.ensure_indexes(c); truth = make_execution_truth()
    session = client.start_session(); session.start_transaction(); FinancialExecutionTruthRegistry.create(truth, "key-a", c, session=session)
    assert FinancialExecutionTruthRegistry.get_by_idempotency_key("tenant-a", "payable-a", "key-a", c, session=session) == truth
    assert FinancialExecutionTruthRegistry.list_for_provider_execution("tenant-a", "PAYSHAP", "provider-execution-a", collection=c, session=session)[0] == truth
    other = MongoClient(os.environ["TEST_VENDOR_MONGO_URI"], serverSelectionTimeoutMS=5000); assert other[db.name][COLLECTION].count_documents({}) == 0
    session.abort_transaction(); session.end_session(); other.close(); assert c.count_documents({}) == 0

def test_distinct_provider_reference_records(mongo_db):
    _, db = mongo_db; c = db[COLLECTION]; FinancialExecutionTruthRegistry.ensure_indexes(c)
    for i in range(3): FinancialExecutionTruthRegistry.create(make_execution_truth(execution_truth_id=f"p-{i}", payable_id=f"pay-{i}", execution_evidence_fingerprint=f"{i+1:x}"*128), f"key-{i}", c)
    records = FinancialExecutionTruthRegistry.list_for_provider_execution("tenant-a", "PAYSHAP", "provider-execution-a", collection=c)
    assert len(records) == 3 and len({r.execution_truth_id for r in records}) == 3
    assert all(r.execution_status in tuple(FinancialExecutionStatus) for r in records)

def test_caller_owned_abort_commit_and_replay(mongo_db):
    client, db = mongo_db
    c = db[COLLECTION]
    FinancialExecutionTruthRegistry.ensure_indexes(c)
    truth = make_execution_truth()
    session = client.start_session()
    session.start_transaction()
    first = FinancialExecutionTruthRegistry.create(truth, "key-a", c, session=session)
    second = FinancialExecutionTruthRegistry.create(truth, "key-a", c, session=session)
    assert first.outcome is FinancialExecutionCreateOutcome.CREATED
    assert second.outcome is FinancialExecutionCreateOutcome.IDEMPOTENT_REPLAY
    assert FinancialExecutionTruthRegistry.get("tenant-a", "execution-a", c, session=session) == truth
    assert FinancialExecutionTruthRegistry.get_by_idempotency_key("tenant-a", "payable-a", "key-a", c, session=session) == truth
    assert FinancialExecutionTruthRegistry.list_for_payable("tenant-a", "payable-a", collection=c, session=session) == (truth,)
    assert c.count_documents({"execution_truth_id":"execution-a"}, session=session) == 1
    session.abort_transaction()
    session.end_session()
    assert c.count_documents({}) == 0
    session = client.start_session()
    session.start_transaction()
    FinancialExecutionTruthRegistry.create(truth, "key-a", c, session=session)
    session.commit_transaction()
    session.end_session()
    assert FinancialExecutionTruthRegistry.get("tenant-a", "execution-a", c) == truth
    assert FinancialExecutionTruthRegistry.get_by_idempotency_key("tenant-a", "payable-a", "key-a", c) == truth
    assert FinancialExecutionTruthRegistry.list_for_payable("tenant-a", "payable-a", collection=c) == (truth,)

def test_complete_round_trip_security_and_collection_boundary(mongo_db):
    _, db = mongo_db
    c = db[COLLECTION]
    FinancialExecutionTruthRegistry.ensure_indexes(c)
    truth = make_execution_truth()
    FinancialExecutionTruthRegistry.create(truth, "key-a", c)
    values = (
        FinancialExecutionTruthRegistry.get("tenant-a", "execution-a", c),
        FinancialExecutionTruthRegistry.get_by_idempotency_key("tenant-a", "payable-a", "key-a", c),
    )
    collections = (
        FinancialExecutionTruthRegistry.list_for_provider_execution("tenant-a", "PAYSHAP", "provider-execution-a", collection=c),
        FinancialExecutionTruthRegistry.list_for_payable("tenant-a", "payable-a", collection=c),
        FinancialExecutionTruthRegistry.list_for_release_authorization("tenant-a", "release-a", collection=c),
    )
    assert all(isinstance(value, FinancialExecutionTruth) for value in values)
    assert all(isinstance(item, FinancialExecutionTruth) for group in collections for item in group)
    assert all(value and value.payment_destination_reference == "destination-ref-a" for value in values)
    assert all(item.payment_destination_reference == "destination-ref-a" for group in collections for item in group)
    row = c.find_one({"execution_truth_id":"execution-a"})
    assert row is not None
    forbidden = {"paid","paid_at","settled","settled_at","settlement_id","settlement_status","amount_paid","outstanding_balance","bank_account","bank_account_number","account_number","card_number","card_pan","cvv","provider_token","access_token","refresh_token","credentials"}
    assert not forbidden.intersection(row)
    assert COLLECTION in db.list_collection_names()
    assert not {"payments","vendor_bills","invoices","settlement","settlements","settlement_allocations"}.intersection(db.list_collection_names())

def test_metadata_corruption_precedes_identity_conflict(mongo_db):
    _, db = mongo_db
    c = db[COLLECTION]
    FinancialExecutionTruthRegistry.ensure_indexes(c)
    cases = ({"create_fingerprint": "bad"}, {"create_fingerprint": None})
    for update in cases:
        truth = make_execution_truth(execution_truth_id=f"h-{len(cases)}")
        FinancialExecutionTruthRegistry.create(truth, "key-a", c)
        if update["create_fingerprint"] is None:
            c.update_one({"execution_truth_id": truth.execution_truth_id}, {"$unset": {"create_fingerprint": ""}})
        else:
            c.update_one({"execution_truth_id": truth.execution_truth_id}, {"$set": update})
        row = c.find_one({"execution_truth_id": truth.execution_truth_id})
        assert row is not None
        if update["create_fingerprint"] is None:
            assert "create_fingerprint" not in row
        else:
            assert row["create_fingerprint"] == "bad"
        with pytest.raises(FinancialExecutionPersistedRecordInvalidError):
            FinancialExecutionTruthRegistry.create(truth, "key-a", c)
        c.delete_many({})
    truth = make_execution_truth()
    FinancialExecutionTruthRegistry.create(truth, "key-a", c)
    c.update_one({"execution_truth_id": truth.execution_truth_id}, {"$set": {"create_idempotency_key": " key-a "}})
    incoming = make_execution_truth(payable_id="payable-b", executed_amount_minor=101)
    with pytest.raises(FinancialExecutionPersistedRecordInvalidError):
        FinancialExecutionTruthRegistry.create(incoming, "key-b", c)

def test_provider_payable_and_release_isolation(mongo_db):
    _, db = mongo_db
    c = db[COLLECTION]
    FinancialExecutionTruthRegistry.ensure_indexes(c)
    records = []
    for tenant, release, payable, prefix in (("tenant-a", "release-a", "payable-a", "a"), ("tenant-a", "release-b", "payable-b", "b"), ("tenant-b", "release-a", "payable-a", "t")):
        for i in range(3 if prefix == "a" else 1):
            truth = make_execution_truth(tenant_id=tenant, release_authorization_id=release, payable_id=payable, execution_truth_id=f"{prefix}-{i}", provider_execution_reference="provider-shared", provider_evidence_reference=f"{prefix}-evidence-{i}", execution_evidence_fingerprint=f"{i + 1:x}" * 128, executed_at=datetime(2026, 3, i + 1, tzinfo=timezone.utc), created_at=datetime(2026, 3, i + 2, tzinfo=timezone.utc))
            FinancialExecutionTruthRegistry.create(truth, f"{prefix}-key-{i}", c)
            records.append(truth)
    provider_a = FinancialExecutionTruthRegistry.list_for_provider_execution("tenant-a", "PAYSHAP", "provider-shared", collection=c)
    provider_b = FinancialExecutionTruthRegistry.list_for_provider_execution("tenant-b", "PAYSHAP", "provider-shared", collection=c)
    assert all(item.tenant_id == "tenant-a" for item in provider_a)
    assert all(item.tenant_id == "tenant-b" for item in provider_b)
    assert [item.execution_truth_id for item in FinancialExecutionTruthRegistry.list_for_payable("tenant-a", "payable-a", collection=c)] == ["a-0", "a-1", "a-2"]
    assert [item.execution_truth_id for item in FinancialExecutionTruthRegistry.list_for_release_authorization("tenant-a", "release-a", collection=c)] == ["a-0", "a-1", "a-2"]

def test_corruption_precedes_divergent_reuse_and_identity_conflict(mongo_db):
    _, db = mongo_db
    c = db[COLLECTION]
    FinancialExecutionTruthRegistry.ensure_indexes(c)
    truth_g = make_execution_truth(tenant_id="tenant-g", payable_id="payable-g", execution_truth_id="execution-g")
    FinancialExecutionTruthRegistry.create(truth_g, "key-g", c)
    c.update_one({"execution_truth_id":"execution-g"}, {"$set":{"currency":"zar"}})
    divergent = make_execution_truth(tenant_id="tenant-g", payable_id="payable-g", execution_truth_id="execution-g-new", executed_amount_minor=101)
    with pytest.raises(FinancialExecutionPersistedRecordInvalidError) as reuse_error:
        FinancialExecutionTruthRegistry.create(divergent, "key-g", c)
    assert not isinstance(reuse_error.value, FinancialExecutionIdempotencyKeyReuseError)
    c.delete_many({})
    truth_i = make_execution_truth(tenant_id="tenant-i", payable_id="payable-i-a", execution_truth_id="execution-i")
    FinancialExecutionTruthRegistry.create(truth_i, "key-i-a", c)
    c.update_one({"execution_truth_id":"execution-i"}, {"$set":{"currency":"zar"}})
    incoming = make_execution_truth(tenant_id="tenant-i", payable_id="payable-i-b", execution_truth_id="execution-i", executed_amount_minor=102)
    with pytest.raises(FinancialExecutionPersistedRecordInvalidError) as identity_error:
        FinancialExecutionTruthRegistry.create(incoming, "key-i-b", c)
    assert not isinstance(identity_error.value, FinancialExecutionCreateConflictError)

def test_blank_identifier_matrix_explicit(mongo_db):
    _, db = mongo_db
    c = db[COLLECTION]
    calls = (
        ("get tenant", lambda: FinancialExecutionTruthRegistry.get("", "execution-a", c)),
        ("get execution", lambda: FinancialExecutionTruthRegistry.get("tenant-a", "", c)),
        ("idempotency tenant", lambda: FinancialExecutionTruthRegistry.get_by_idempotency_key("", "payable-a", "key-a", c)),
        ("idempotency payable", lambda: FinancialExecutionTruthRegistry.get_by_idempotency_key("tenant-a", "", "key-a", c)),
        ("idempotency key", lambda: FinancialExecutionTruthRegistry.get_by_idempotency_key("tenant-a", "payable-a", "", c)),
        ("provider tenant", lambda: FinancialExecutionTruthRegistry.list_for_provider_execution("", "PAYSHAP", "provider-a", collection=c)),
        ("provider name", lambda: FinancialExecutionTruthRegistry.list_for_provider_execution("tenant-a", "", "provider-a", collection=c)),
        ("provider reference", lambda: FinancialExecutionTruthRegistry.list_for_provider_execution("tenant-a", "PAYSHAP", "", collection=c)),
        ("payable tenant", lambda: FinancialExecutionTruthRegistry.list_for_payable("", "payable-a", collection=c)),
        ("payable id", lambda: FinancialExecutionTruthRegistry.list_for_payable("tenant-a", "", collection=c)),
        ("release tenant", lambda: FinancialExecutionTruthRegistry.list_for_release_authorization("", "release-a", collection=c)),
        ("release id", lambda: FinancialExecutionTruthRegistry.list_for_release_authorization("tenant-a", "", collection=c)),
    )
    for name, call in calls:
        with pytest.raises(FinancialExecutionRegistryError, match="invalid"):
            call()

def test_concurrent_exact_create_converges(mongo_db):
    _, db = mongo_db
    c = db[COLLECTION]
    FinancialExecutionTruthRegistry.ensure_indexes(c)
    truth = make_execution_truth()
    def invoke():
        return FinancialExecutionTruthRegistry.create(truth, "key-a", c).outcome
    def invoke_categorized():
        try:
            return ("created", invoke())
        except DuplicateKeyError:
            return ("duplicate", None)
        except Exception as error:
            return ("unexpected", error)
    with ThreadPoolExecutor(max_workers=20) as executor:
        outcomes = list(executor.map(lambda _: invoke_categorized(), range(100)))
    values = [value for category, value in outcomes if category == "created"]
    assert values.count(FinancialExecutionCreateOutcome.CREATED) == 1
    assert values.count(FinancialExecutionCreateOutcome.IDEMPOTENT_REPLAY) == 99
    assert sum(category == "duplicate" for category, _ in outcomes) == 0
    assert sum(category == "unexpected" for category, _ in outcomes) == 0
    assert len(outcomes) == 100
    assert c.count_documents({}) == 1

def test_concurrent_provider_reference_is_non_unique(mongo_db):
    _, db = mongo_db
    c = db[COLLECTION]
    FinancialExecutionTruthRegistry.ensure_indexes(c)
    truths = [make_execution_truth(execution_truth_id=f"concurrent-{i}", payable_id=f"payable-{i}", provider_evidence_reference=f"evidence-{i}", execution_evidence_fingerprint=f"{i + 1:x}" * 128, executed_at=datetime(2026, 2, i + 1, tzinfo=timezone.utc), created_at=datetime(2026, 2, i + 2, tzinfo=timezone.utc)) for i in range(8)]
    def create(item):
        return FinancialExecutionTruthRegistry.create(item, f"key-{item.execution_truth_id}", c).outcome
    def categorized(item):
        try:
            return ("created", create(item))
        except DuplicateKeyError:
            return ("duplicate", None)
        except Exception as error:
            return ("unexpected", error)
    with ThreadPoolExecutor(max_workers=8) as executor:
        outcomes = list(executor.map(categorized, truths))
    assert sum(category == "duplicate" for category, _ in outcomes) == 0
    assert sum(category == "unexpected" for category, _ in outcomes) == 0
    outcomes = [value for _, value in outcomes]
    assert outcomes == [FinancialExecutionCreateOutcome.CREATED] * 8
    rows = FinancialExecutionTruthRegistry.list_for_provider_execution("tenant-a", "PAYSHAP", "provider-execution-a", collection=c)
    assert [row.execution_truth_id for row in rows] == [f"concurrent-{i}" for i in range(8)]
    assert c.count_documents({}) == 8

# ARTIFACT: test_financial_execution_registry_mongo.py
# VERSION: v1.0.0-KENNEL-FINANCIAL-EXECUTION-TRUTH-REGISTRY-REAL-MONGO-CERT
# STATUS: REAL-MONGO PERSISTENCE CERTIFICATION
# PRODUCTION CONTRACT VERSION: v1.0.4-KENNEL-FINANCIAL-EXECUTION-TRUTH-REGISTRY-CALLER-TRANSACTION-REPLAY
# PRODUCTION CONTRACT COMMIT: a5cec760cdb03f7b3d88a3869f2cf7bf379c1d0d
# DOMAIN CONTRACT VERSION: v1.0.1-KENNEL-FINANCIAL-EXECUTION-TRUTH-DOMAIN-PERSISTENCE-HYDRATION
# DOMAIN CONTRACT COMMIT: 6783d523efea6c311453c794afca6b0520777c0a
# ARCHITECTURE LOCK: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
# TENANT POSTURE: tenant-scoped immutable evidence
# TRANSACTION POSTURE: caller-owned sessions
# FINANCIAL AUTHORITY: Kennel EOS exclusively owns execution truth
# SCOPE LIMITATION: persistence only; provider execution and settlement excluded
# END OF WILSY OS SOVEREIGN ARTIFACT
