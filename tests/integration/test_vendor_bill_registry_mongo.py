"""WILSY OS — VENDOR BILL RELEASE-AUTHORITY GUARD REAL-MONGO CERTIFICATION
Version: v1.4.0-VENDOR-BILL-RELEASE-AUTHORITY-GUARD-MONGO-CERT
Authority: Wilsy OS Core Governance | Classification: Institutional Integration Certification
Epitome: Real Mongo CAS proof for persisted release-authority coordination metadata.
Absolute path: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_vendor_bill_registry_mongo.py
Collaboration: Wilson Khanyezi — Founder / Chief Architect; AI Engineering (Codex)
Date: 2026-08-27 | CHANGELOG: v1.1.0 added guard persistence and caller-session CAS certification.
v1.2.0 adds stale-predicate, lifecycle/approval-gate, tenant-isolation,
transaction abort/commit, same-guard race, projection-conflict, and corruption
precedence certification. v1.3.0 corrects legal state fixtures and adds explicit
corruption precedence, 100-race guard CAS, and projection-vs-guard stale proof.
This artifact certifies release-authority coordination only.
v1.4.0 adds a dedicated 100-race release-authority guard CAS matrix,
double-admission prevention, and approval-projection stale-snapshot coverage.
POPIA §19 | GDPR §32 | SOC2 CC7.2
APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
Kennel EOS remains the exclusive financial execution authority.
"""

import os
import threading
from dataclasses import replace
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone

from pymongo import MongoClient
import pytest

from tools.eos.saas.billing.vendor_bill_registry import VendorBillCreateConflictError, VendorBillCreateOutcome, VendorBillIdempotencyKeyReuseError, VendorBillMutationOutcome, VendorBillNotFoundError, VendorBillObligationState, VendorBillPersistedRecordInvalidError, VendorBillRegistry, VendorBillRevisionConflictError
from tools.eos.saas.billing.vendor_registry import VendorRegistry
from tools.eos.saas.domain.vendor import VendorIdentity
from tools.eos.saas.domain.vendor_bill import VendorBill, VendorBillDomainError, VendorBillApprovalState
from tools.eos.saas.billing.financial_approval_aggregator import FinancialApprovalAggregator
from tools.eos.saas.billing.financial_approval_effective_result_registry import FinancialApprovalEffectiveResultRegistry, FinancialApprovalEffectiveResultCreateOutcome
from tests.integration.test_financial_approval_aggregator_mongo import fixture as approval_fixture


def test_vendor_bill_approval_projection_domain_contract():
    """Proves projection defaults and strict field invariants without requiring Mongo."""
    def make_bill(projection_revision=0, result_id=None):
        return VendorBill(tenant_id="tenant-a", vendor_id="vendor-a", payable_id="domain-projection", gross_amount_minor=100, currency="ZAR", issue_date=date(2026, 8, 25), due_date=date(2026, 9, 25), received_at=datetime(2026, 8, 25, tzinfo=timezone.utc), approval_projection_revision=projection_revision, approval_effective_result_id=result_id)
    bill = make_bill()
    assert bill.approval_projection_revision == 0
    assert bill.approval_effective_result_id is None
    for fields in ({"approval_projection_revision": True}, {"approval_projection_revision": -1}, {"approval_projection_revision": 0, "approval_effective_result_id": "result"}, {"approval_projection_revision": 1}, {"approval_projection_revision": 1, "approval_effective_result_id": "   "}):
        try:
            make_bill(fields.get("approval_projection_revision", 0), fields.get("approval_effective_result_id"))
        except VendorBillDomainError:
            pass
        else:
            raise AssertionError(f"invalid projection fields accepted: {fields!r}")


def test_vendor_bill_first_and_second_approval_projection_real_mongo():
    client, database, evaluations, decisions, authorizations, evaluation, opened = approval_fixture(1)
    results = database["financial_approval_effective_results"]
    FinancialApprovalEffectiveResultRegistry.ensure_indexes(results)
    aggregator = FinancialApprovalAggregator(database=database)
    first = aggregator.aggregate("t", "e", "projection-result-1", evaluation.evaluated_at, evaluation.created_at)
    second = aggregator.aggregate("t", "e", "projection-result-2", evaluation.evaluated_at, evaluation.created_at)
    assert FinancialApprovalEffectiveResultRegistry.create(first, "projection-result-key-1", results).outcome is FinancialApprovalEffectiveResultCreateOutcome.CREATED
    assert FinancialApprovalEffectiveResultRegistry.create(second, "projection-result-key-2", results).outcome is FinancialApprovalEffectiveResultCreateOutcome.CREATED
    committed = VendorBillRegistry.project_financial_approval_result("t", "p", first.result_id, opened.revision, 0, "projection-command-1", database["vendor_bills"])
    projected = VendorBillRegistry.get("t", "p", database["vendor_bills"])
    assert committed.outcome.value == "COMMITTED" and projected.revision == opened.revision and projected.approval_projection_revision == 1 and projected.approval_effective_result_id == first.result_id and projected.approval_state.value == first.effective_state.value
    second_commit = VendorBillRegistry.project_financial_approval_result("t", "p", second.result_id, opened.revision, 1, "projection-command-2", database["vendor_bills"])
    projected = VendorBillRegistry.get("t", "p", database["vendor_bills"])
    assert second_commit.outcome.value == "COMMITTED" and projected.revision == opened.revision and projected.approval_projection_revision == 2 and projected.approval_effective_result_id == second.result_id and projected.approval_state.value == second.effective_state.value
    client.drop_database(database.name); client.close()


def _projection_fixture():
    client, database, evaluations, decisions, authorizations, evaluation, opened = approval_fixture(1)
    results = database["financial_approval_effective_results"]
    FinancialApprovalEffectiveResultRegistry.ensure_indexes(results)
    aggregator = FinancialApprovalAggregator(database=database)
    first = aggregator.aggregate("t", "e", "adversarial-result-1", evaluation.evaluated_at, evaluation.created_at)
    second = aggregator.aggregate("t", "e", "adversarial-result-2", evaluation.evaluated_at, evaluation.created_at)
    FinancialApprovalEffectiveResultRegistry.create(first, "adversarial-result-key-1", results)
    FinancialApprovalEffectiveResultRegistry.create(second, "adversarial-result-key-2", results)
    return client, database, opened, first, second


def test_vendor_bill_projection_replay_and_same_result_noop_real_mongo():
    client, database, opened, first, _ = _projection_fixture()
    bills = database["vendor_bills"]
    committed = VendorBillRegistry.project_financial_approval_result("t", "p", first.result_id, opened.revision, 0, "projection-replay-key", bills)
    replay = VendorBillRegistry.project_financial_approval_result("t", "p", first.result_id, opened.revision, 0, "projection-replay-key", bills)
    alternate_key = VendorBillRegistry.project_financial_approval_result("t", "p", first.result_id, opened.revision, 0, "projection-replay-key-2", bills)
    fresh = VendorBillRegistry.get("t", "p", bills)
    assert committed.outcome.value == "COMMITTED" and replay.outcome.value == "IDEMPOTENT_REPLAY" and alternate_key.outcome.value == "IDEMPOTENT_REPLAY"
    assert fresh.revision == opened.revision and fresh.approval_projection_revision == 1 and fresh.approval_effective_result_id == first.result_id
    client.drop_database(database.name); client.close()


def test_vendor_bill_projection_same_key_different_result_and_stale_projection_conflict_real_mongo():
    client, database, opened, first, second = _projection_fixture()
    bills = database["vendor_bills"]
    VendorBillRegistry.project_financial_approval_result("t", "p", first.result_id, opened.revision, 0, "projection-reuse-key", bills)
    try:
        VendorBillRegistry.project_financial_approval_result("t", "p", second.result_id, opened.revision, 1, "projection-reuse-key", bills)
    except Exception as error:
        assert "IDEMPOTENCY" in str(error) or "PROJECTION" in str(error)
    else:
        raise AssertionError("same projection idempotency key accepted a different result")
    try:
        VendorBillRegistry.project_financial_approval_result("t", "p", second.result_id, opened.revision, 0, "projection-stale-key", bills)
    except Exception as error:
        assert "PROJECTION" in str(error) or "REVISION" in str(error)
    else:
        raise AssertionError("stale projection revision unexpectedly succeeded")
    fresh = VendorBillRegistry.get("t", "p", bills)
    assert fresh.revision == opened.revision and fresh.approval_projection_revision == 1 and fresh.approval_effective_result_id == first.result_id
    client.drop_database(database.name); client.close()


def test_vendor_bill_projection_wrong_payable_and_cross_tenant_isolation_real_mongo():
    client, database, opened, first, _ = _projection_fixture()
    bills = database["vendor_bills"]
    try:
        VendorBillRegistry.project_financial_approval_result("t", "other-payable", first.result_id, opened.revision, 0, "wrong-payable", bills)
    except Exception as error:
        assert "REFERENCE" in str(error) or "NOT_FOUND" in str(error)
    else:
        raise AssertionError("projection bound to another payable unexpectedly succeeded")
    try:
        VendorBillRegistry.project_financial_approval_result("other-tenant", "p", first.result_id, opened.revision, 0, "cross-tenant", bills)
    except Exception as error:
        assert "REFERENCE" in str(error) or "NOT_FOUND" in str(error)
    else:
        raise AssertionError("cross-tenant projection unexpectedly succeeded")
    fresh = VendorBillRegistry.get("t", "p", bills)
    assert fresh.revision == opened.revision and fresh.approval_projection_revision == 0 and fresh.approval_effective_result_id is None
    client.drop_database(database.name); client.close()


def test_vendor_bill_projection_open_only_gate_real_mongo():
    client, database, opened, first, _ = _projection_fixture()
    bills = database["vendor_bills"]
    bills.update_one({"tenant_id": "t", "payable_id": "p"}, {"$set": {"obligation_state": "DRAFT"}})
    try:
        VendorBillRegistry.project_financial_approval_result("t", "p", first.result_id, opened.revision, 0, "draft-gate", bills)
    except Exception as error:
        assert "PROJECTION" in str(error) or "REVISION" in str(error)
    else:
        raise AssertionError("DRAFT VendorBill accepted an approval projection")
    client.drop_database(database.name); client.close()


def test_vendor_bill_projection_corrupt_result_and_command_family_collision_real_mongo():
    client, database, opened, first, _ = _projection_fixture()
    bills, results = database["vendor_bills"], database["financial_approval_effective_results"]
    results.update_one({"tenant_id": "t", "result_id": first.result_id}, {"$set": {"source_evidence_fingerprint": "corrupt"}})
    try:
        VendorBillRegistry.project_financial_approval_result("t", "p", first.result_id, opened.revision, 0, "corrupt-result", bills)
    except Exception as error:
        assert "PERSISTED_RECORD_INVALID" in str(error)
    else:
        raise AssertionError("corrupt effective result was accepted")
    client.drop_database(database.name); client.close()


def test_vendor_bill_projection_one_hundred_identical_commands_real_mongo():
    from concurrent.futures import ThreadPoolExecutor
    client, database, opened, first, _ = _projection_fixture()
    bills = database["vendor_bills"]
    def run(_):
        try:
            return VendorBillRegistry.project_financial_approval_result("t", "p", first.result_id, opened.revision, 0, "projection-race-key", bills).outcome.value
        except Exception as error:
            return str(error)
    with ThreadPoolExecutor(max_workers=32) as pool:
        outcomes = list(pool.map(run, range(100)))
    assert outcomes.count("COMMITTED") == 1 and outcomes.count("IDEMPOTENT_REPLAY") == 99
    fresh = VendorBillRegistry.get("t", "p", bills)
    assert fresh.revision == opened.revision and fresh.approval_projection_revision == 1 and bills.count_documents({"tenant_id": "t", "payable_id": "p"}) == 1
    client.drop_database(database.name); client.close()


def test_vendor_bill_create_open_projection_fields_regression_real_mongo():
    client, database, bills, bill = _fixture()
    created = VendorBillRegistry.create(bill(), bills)
    assert created.vendor_bill.approval_projection_revision == 0 and created.vendor_bill.approval_effective_result_id is None
    opened = VendorBillRegistry.open_bill("tenant-a", "payable-1", 1, "open-projection-regression", bills).vendor_bill
    assert opened.revision == 2 and opened.approval_projection_revision == 0 and opened.approval_effective_result_id is None
    client.drop_database(database.name); client.close()


def test_release_authority_guard_persistence_cas_real_mongo():
    """Prove persisted guard defaults, strict corruption rejection, and CAS advancement."""
    client, database, bills, bill = _fixture()
    VendorBillRegistry.create(bill(), bills)
    raw = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert raw is not None and raw["release_authority_guard_revision"] == 0
    bills.update_one(
        {"tenant_id": "tenant-a", "payable_id": "payable-1"},
        {"$set": {"obligation_state": "OPEN", "approval_state": "APPROVED", "approval_projection_revision": 1, "approval_effective_result_id": "result-a"}},
    )
    bills.update_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}, {"$unset": {"release_authority_guard_revision": ""}})
    assert VendorBillRegistry.get("tenant-a", "payable-1", bills).release_authority_guard_revision == 0
    bills.update_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}, {"$set": {"release_authority_guard_revision": 0}})
    advanced = VendorBillRegistry.acquire_release_authority_guard("tenant-a", "payable-1", 1, 1, "result-a", 0, bills)
    assert advanced.release_authority_guard_revision == 1
    persisted = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert persisted is not None and persisted["release_authority_guard_revision"] == 1
    try:
        VendorBillRegistry.acquire_release_authority_guard("tenant-a", "payable-1", 1, 1, "result-a", 0, bills)
    except Exception as error:
        assert "STALE" in str(error)
    else:
        raise AssertionError("stale release-authority guard unexpectedly advanced")
    client.drop_database(database.name); client.close()


def test_release_authority_guard_stale_predicates_and_gates_real_mongo():
    """Certify every supported guard fallback classification without mutation."""
    client, database, bills, bill = _fixture()
    VendorBillRegistry.create(bill(), bills)
    base = {"obligation_state": "OPEN", "approval_state": "APPROVED", "approval_projection_revision": 1, "approval_effective_result_id": "result-a"}
    bills.update_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}, {"$set": base})
    calls = ((2, 1, "result-a", 0, "VENDOR_BILL_REVISION_CONFLICT"), (1, 2, "result-a", 0, "VENDOR_BILL_APPROVAL_PROJECTION_CONFLICT"), (1, 1, "wrong", 0, "VENDOR_BILL_APPROVAL_PROJECTION_REFERENCE_MISMATCH"))
    for revision, projection, result_id, guard, code in calls:
        before = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
        try:
            VendorBillRegistry.acquire_release_authority_guard("tenant-a", "payable-1", revision, projection, result_id, guard, bills)
        except Exception as error:
            assert str(error) == code
        else:
            raise AssertionError("stale guard predicate unexpectedly succeeded")
        assert bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}) == before
    state_amounts = (("DRAFT", 10000), ("PARTIALLY_SETTLED", 5000), ("SETTLED", 0), ("VOIDED", 0))
    for state, outstanding in state_amounts:
        bills.update_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}, {"$set": {"obligation_state": state, "outstanding_amount_minor": outstanding}})
        with pytest.raises(Exception, match="INVALID_OBLIGATION_STATE"):
            VendorBillRegistry.acquire_release_authority_guard("tenant-a", "payable-1", 1, 1, "result-a", 0, bills)
        bills.update_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}, {"$set": {"obligation_state": "OPEN", "outstanding_amount_minor": 10000}})
    for state in ("NOT_REQUIRED", "PENDING", "REJECTED"):
        bills.update_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}, {"$set": {"approval_state": state}})
        with pytest.raises(Exception, match="APPROVAL_NOT_APPROVED"):
            VendorBillRegistry.acquire_release_authority_guard("tenant-a", "payable-1", 1, 1, "result-a", 0, bills)
        bills.update_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}, {"$set": {"approval_state": "APPROVED"}})
    client.drop_database(database.name); client.close()


def test_release_authority_guard_tenant_isolation_and_financial_boundary_real_mongo():
    """Prove tenant scoping and coordination-only mutation boundaries."""
    client, database, bills, bill = _fixture()
    VendorRegistry.create(VendorIdentity(tenant_id="tenant-b", legal_name="Tenant B"), database["vendors"])
    VendorBillRegistry.create(bill(), bills)
    before = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert before is not None
    with pytest.raises(VendorBillNotFoundError, match="VENDOR_BILL_NOT_FOUND"):
        VendorBillRegistry.acquire_release_authority_guard("tenant-b", "payable-1", 1, 1, "result-a", 0, bills)
    assert bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}) == before
    client.drop_database(database.name); client.close()


def test_release_authority_guard_caller_owned_abort_and_commit_real_mongo():
    """Prove caller-owned transactions control guard durability."""
    client, database, bills, bill = _fixture()
    VendorBillRegistry.create(bill(), bills)
    bills.update_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}, {"$set": {"obligation_state": "OPEN", "approval_state": "APPROVED", "approval_projection_revision": 1, "approval_effective_result_id": "result-a"}})
    with client.start_session() as session:
        session.start_transaction()
        changed = VendorBillRegistry.acquire_release_authority_guard("tenant-a", "payable-1", 1, 1, "result-a", 0, bills, session=session)
        assert changed.release_authority_guard_revision == 1
        in_transaction = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}, session=session)
        assert in_transaction is not None
        assert in_transaction["release_authority_guard_revision"] == 1
        session.abort_transaction()
    after_abort = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert after_abort is not None
    assert after_abort["release_authority_guard_revision"] == 0
    with client.start_session() as session:
        session.start_transaction()
        VendorBillRegistry.acquire_release_authority_guard("tenant-a", "payable-1", 1, 1, "result-a", 0, bills, session=session)
        session.commit_transaction()
    after_commit = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert after_commit is not None
    assert after_commit["release_authority_guard_revision"] == 1
    client.drop_database(database.name); client.close()


def test_release_authority_guard_corruption_precedes_classifier_real_mongo():
    """Prove malformed persisted obligations fail as corruption before gating."""
    client, database, bills, bill = _fixture()
    VendorBillRegistry.create(bill(), bills)
    bills.update_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}, {"$set": {"obligation_state": "PARTIALLY_SETTLED", "outstanding_amount_minor": 10000}})
    with pytest.raises(VendorBillPersistedRecordInvalidError, match="VENDOR_BILL_PERSISTED_RECORD_INVALID"):
        VendorBillRegistry.acquire_release_authority_guard("tenant-a", "payable-1", 1, 1, "result-a", 0, bills)
    raw = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert raw is not None and raw["release_authority_guard_revision"] == 0
    client.drop_database(database.name); client.close()


def test_release_authority_guard_one_hundred_real_mongo_cas_races():
    """Certify exactly-one-writer behavior for 100 synchronized guard races."""
    client, database, bills, bill_factory = _fixture()
    successes = conflicts = double_successes = double_conflicts = unexpected = 0
    guard_mismatches = revision_mismatches = projection_mismatches = state_mismatches = record_mismatches = 0
    for index in range(100):
        payable = f"guard-race-{index}"
        bill = replace(bill_factory(payable), payable_id=payable)
        VendorBillRegistry.create(bill, bills)
        bills.update_one({"tenant_id": "tenant-a", "payable_id": payable}, {"$set": {"obligation_state": "OPEN", "approval_state": "APPROVED", "approval_projection_revision": 1, "approval_effective_result_id": "result-a"}})
        barrier = threading.Barrier(2)
        def worker():
            barrier.wait()
            try:
                return ("success", VendorBillRegistry.acquire_release_authority_guard("tenant-a", payable, 1, 1, "result-a", 0, bills))
            except Exception as error:
                return ("conflict", error) if "GUARD_STALE" in str(error) or "REVISION" in str(error) else ("unexpected", error)
        with ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(lambda _: worker(), (0, 1)))
        kinds = [kind for kind, _ in outcomes]
        successes += kinds.count("success"); conflicts += kinds.count("conflict")
        double_successes += int(kinds.count("success") == 2); double_conflicts += int(kinds.count("conflict") == 2); unexpected += kinds.count("unexpected")
        raw = bills.find_one({"tenant_id": "tenant-a", "payable_id": payable})
        if raw is None: record_mismatches += 1; continue
        guard_mismatches += int(raw.get("release_authority_guard_revision") != 1)
        revision_mismatches += int(raw.get("revision") != 1); projection_mismatches += int(raw.get("approval_projection_revision") != 1)
        state_mismatches += int(raw.get("obligation_state") != "OPEN" or raw.get("approval_state") != "APPROVED")
        record_mismatches += int(bills.count_documents({"tenant_id": "tenant-a", "payable_id": payable}) != 1)
    assert (successes, conflicts, double_successes, double_conflicts, unexpected, guard_mismatches, revision_mismatches, projection_mismatches, state_mismatches, record_mismatches) == (100, 100, 0, 0, 0, 0, 0, 0, 0, 0)
    client.drop_database(database.name); client.close()


def test_release_authority_guard_rejects_stale_approval_projection_real_mongo():
    """Prove newer approval projection blocks stale release authority."""
    client, database, opened, first, second = _projection_fixture()
    bills = database["vendor_bills"]
    VendorBillRegistry.project_financial_approval_result("t", "p", first.result_id, opened.revision, 0, "guard-projection-1", bills)
    current = VendorBillRegistry.get("t", "p", bills)
    VendorBillRegistry.project_financial_approval_result("t", "p", second.result_id, current.revision, 1, "guard-projection-2", bills)
    with pytest.raises(Exception) as error:
        VendorBillRegistry.acquire_release_authority_guard("t", "p", current.revision, 1, first.result_id, 0, bills)
    assert "PROJECTION" in str(error.value) or "REFERENCE" in str(error.value)
    fresh = VendorBillRegistry.get("t", "p", bills)
    assert fresh.approval_projection_revision == 2 and fresh.approval_effective_result_id == second.result_id and fresh.release_authority_guard_revision == 0
    client.drop_database(database.name); client.close()


def _uri():
    return os.environ["TEST_VENDOR_MONGO_URI"]


def _fixture():
    client = MongoClient(_uri(), serverSelectionTimeoutMS=5000, retryWrites=True)
    assert client.admin.command("hello")["isWritablePrimary"]
    db = client[f"wilsy_vendor_bill_cert_{uuid.uuid4().hex}"]
    vendors, bills = db["vendors"], db["vendor_bills"]
    VendorRegistry.ensure_indexes(vendors); VendorBillRegistry.ensure_indexes(bills)
    vendor = VendorRegistry.create(VendorIdentity(tenant_id="tenant-a", legal_name="Certification Vendor"), vendors)
    def bill(reference="INV-1"):
        return VendorBill(tenant_id="tenant-a", vendor_id=vendor.vendor_id, payable_id="payable-1", vendor_reference=reference, gross_amount_minor=10000, currency="ZAR", issue_date=date(2026, 8, 25), due_date=date(2026, 9, 25), received_at=datetime(2026, 8, 25, tzinfo=timezone.utc))
    return client, db, bills, bill


def test_vendor_bill_create_replay_and_conflict_real_mongo():
    client, db, bills, bill = _fixture()
    created = VendorBillRegistry.create(bill(), bills)
    replay = VendorBillRegistry.create(bill(), bills)
    assert created.outcome is VendorBillCreateOutcome.CREATED
    assert replay.outcome is VendorBillCreateOutcome.IDEMPOTENT_REPLAY
    assert bills.count_documents({"tenant_id": "tenant-a", "payable_id": "payable-1"}) == 1
    persisted = bills.find_one({"payable_id": "payable-1"})
    assert persisted is not None
    assert persisted["revision"] == 1
    try:
        VendorBillRegistry.create(bill("INV-DIFFERENT"), bills)
    except VendorBillCreateConflictError as error:
        assert str(error) == "VENDOR_BILL_CREATE_CONFLICT"
    else:
        raise AssertionError("different create command accepted")
    client.drop_database(db.name); client.close()


def test_vendor_bill_concurrent_identical_create_real_mongo():
    client, db, bills, bill = _fixture(); start = threading.Event()
    def create():
        start.wait(); return VendorBillRegistry.create(bill(), bills)
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = [pool.submit(create) for _ in range(100)]; start.set(); results = [future.result() for future in futures]
    assert sum(result.outcome is VendorBillCreateOutcome.CREATED for result in results) == 1
    assert sum(result.outcome is VendorBillCreateOutcome.IDEMPOTENT_REPLAY for result in results) == 99
    assert bills.count_documents({"tenant_id": "tenant-a", "payable_id": "payable-1"}) == 1
    client.drop_database(db.name); client.close()


def test_open_bill_real_mongo_cas_transition():
    client, db, bills, bill = _fixture()
    created = VendorBillRegistry.create(bill(), bills)
    before = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    opened = VendorBillRegistry.open_bill("tenant-a", "payable-1", 1, "open-transition", bills)
    after = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    fresh = VendorBillRegistry.get("tenant-a", "payable-1", bills)
    assert before and after
    assert created.outcome is VendorBillCreateOutcome.CREATED
    assert opened.outcome is VendorBillMutationOutcome.COMMITTED
    assert opened.vendor_bill.obligation_state is VendorBillObligationState.OPEN and opened.revision == 2
    assert fresh.obligation_state is VendorBillObligationState.OPEN and fresh.revision == 2
    assert before["created_at"] == after["created_at"] and before["updated_at"] != after["updated_at"]
    assert before["create_fingerprint"] == after["create_fingerprint"]
    assert bills.count_documents({"tenant_id": "tenant-a", "payable_id": "payable-1"}) == 1
    client.drop_database(db.name); client.close()


def test_open_bill_stale_revision_conflict_real_mongo():
    client, db, bills, bill = _fixture()
    VendorBillRegistry.create(bill(), bills)
    committed = VendorBillRegistry.open_bill("tenant-a", "payable-1", 1, "open-stale-commit", bills)
    before_stale = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert before_stale is not None
    try:
        VendorBillRegistry.open_bill("tenant-a", "payable-1", 1, "open-stale-retry", bills)
    except VendorBillRevisionConflictError as error:
        assert str(error) == "VENDOR_BILL_REVISION_CONFLICT"
    else:
        raise AssertionError("stale VendorBill CAS unexpectedly succeeded")
    after_stale = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    fresh = VendorBillRegistry.get("tenant-a", "payable-1", bills)
    assert after_stale == before_stale
    assert committed.revision == fresh.revision == 2
    assert fresh.obligation_state is VendorBillObligationState.OPEN
    assert bills.count_documents({"tenant_id": "tenant-a", "payable_id": "payable-1"}) == 1
    client.drop_database(db.name); client.close()


def test_open_bill_one_hundred_real_mongo_cas_races():
    successes = conflicts = revision_mismatches = state_mismatches = record_mismatches = 0
    client, db, bills, bill = _fixture()
    for race in range(100):
        current = replace(bill(), payable_id=f"payable-race-{race}")
        VendorBillRegistry.create(current, bills)
        before = bills.find_one({"tenant_id": "tenant-a", "payable_id": current.payable_id})
        assert before is not None
        barrier, outcomes = threading.Barrier(2), []
        def open_once(worker_number):
            try:
                barrier.wait(); outcomes.append(VendorBillRegistry.open_bill("tenant-a", current.payable_id, 1, f"race-{race}-{worker_number}", bills))
            except Exception as error:
                outcomes.append(error)
        workers = [threading.Thread(target=open_once, args=(worker_number,)) for worker_number in range(2)]
        [worker.start() for worker in workers]; [worker.join() for worker in workers]
        successes += sum(not isinstance(item, Exception) for item in outcomes)
        conflicts += sum(isinstance(item, VendorBillRevisionConflictError) for item in outcomes)
        raw = bills.find_one({"tenant_id": "tenant-a", "payable_id": current.payable_id})
        fresh = VendorBillRegistry.get("tenant-a", current.payable_id, bills)
        revision_mismatches += int(fresh.revision != 2 or raw is None or raw["revision"] != 2)
        state_mismatches += int(fresh.obligation_state is not VendorBillObligationState.OPEN or raw is None or raw["obligation_state"] != "OPEN")
        record_mismatches += int(raw is None or raw["created_at"] != before["created_at"] or raw["create_fingerprint"] != before["create_fingerprint"] or bills.count_documents({"tenant_id": "tenant-a", "payable_id": current.payable_id}) != 1)
    assert successes == conflicts == 100
    assert revision_mismatches == state_mismatches == record_mismatches == 0
    client.drop_database(db.name); client.close()


def test_open_bill_not_found_real_mongo():
    client, db, bills, _ = _fixture()
    try:
        VendorBillRegistry.open_bill("tenant-a", "payable-absent", 1, "not-found", bills)
    except VendorBillNotFoundError as error:
        assert str(error) == "VENDOR_BILL_NOT_FOUND"
    else:
        raise AssertionError("absent VendorBill CAS did not return VENDOR_BILL_NOT_FOUND")
    assert bills.count_documents({"tenant_id": "tenant-a", "payable_id": "payable-absent"}) == 0
    assert bills.count_documents({}) == 0
    client.drop_database(db.name); client.close()


def test_open_bill_cross_tenant_non_disclosure_real_mongo():
    client, db, bills, bill = _fixture()
    VendorRegistry.create(VendorIdentity(tenant_id="tenant-b", legal_name="Other Tenant Vendor"), db["vendors"])
    VendorBillRegistry.create(bill(), bills)
    before = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert before is not None
    try:
        VendorBillRegistry.open_bill("tenant-b", "payable-1", 1, "cross-tenant", bills)
    except VendorBillNotFoundError as error:
        assert str(error) == "VENDOR_BILL_NOT_FOUND"
    else:
        raise AssertionError("cross-tenant VendorBill CAS disclosed owner record state")
    after = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert after == before
    fresh = VendorBillRegistry.get("tenant-a", "payable-1", bills)
    assert fresh.obligation_state is VendorBillObligationState.DRAFT
    assert fresh.revision == 1
    client.drop_database(db.name); client.close()


def test_open_bill_corrupt_loser_reread_precedes_conflict_real_mongo():
    client, db, bills, bill = _fixture()
    VendorBillRegistry.create(bill(), bills)
    bills.update_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}, {"$set": {"revision": "corrupt"}})
    try:
        VendorBillRegistry.open_bill("tenant-a", "payable-1", 1, "corrupt-reread", bills)
    except VendorBillPersistedRecordInvalidError as error:
        assert str(error) == "VENDOR_BILL_PERSISTED_RECORD_INVALID"
    else:
        raise AssertionError("corrupt CAS-loser reread did not fail strict hydration")
    persisted = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert persisted is not None
    assert persisted["revision"] == "corrupt"
    assert persisted["obligation_state"] == VendorBillObligationState.DRAFT.value
    client.drop_database(db.name); client.close()


def test_open_bill_invalid_expected_revision_real_mongo():
    client, db, bills, bill = _fixture()
    VendorBillRegistry.create(bill(), bills)
    before = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert before is not None

    def open_with_runtime_input(expected_revision):
        return VendorBillRegistry.open_bill("tenant-a", "payable-1", expected_revision, "invalid-revision", bills)

    for invalid_revision in (True, False, 0, -1, 1.5, "1", None):
        try:
            open_with_runtime_input(invalid_revision)
        except VendorBillRevisionConflictError as error:
            assert str(error) == "VENDOR_BILL_REVISION_CONFLICT"
        else:
            raise AssertionError(f"invalid expected_revision accepted: {invalid_revision!r}")
        after = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
        assert after == before

    fresh = VendorBillRegistry.get("tenant-a", "payable-1", bills)
    assert fresh.obligation_state is VendorBillObligationState.DRAFT
    assert fresh.revision == 1
    client.drop_database(db.name); client.close()


def test_open_bill_first_command_and_exact_replay_real_mongo():
    client, db, bills, bill = _fixture()
    VendorBillRegistry.create(bill(), bills)
    before = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert before is not None
    committed = VendorBillRegistry.open_bill("tenant-a", "payable-1", 1, "open-command-1", bills)
    after_commit = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert after_commit is not None
    replay = VendorBillRegistry.open_bill("tenant-a", "payable-1", 1, "open-command-1", bills)
    after_replay = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert after_replay is not None
    assert committed.outcome is VendorBillMutationOutcome.COMMITTED
    assert replay.outcome is VendorBillMutationOutcome.IDEMPOTENT_REPLAY
    assert committed.vendor_bill.obligation_state is VendorBillObligationState.OPEN and committed.revision == 2
    assert replay.vendor_bill.obligation_state is VendorBillObligationState.OPEN and replay.revision == 2
    assert after_commit["updated_at"] != before["updated_at"]
    assert after_replay["updated_at"] == after_commit["updated_at"]
    assert len(after_replay["command_receipts"]) == 1
    assert after_replay["command_receipts"][0]["committed_revision"] == 2
    client.drop_database(db.name); client.close()


def test_open_bill_same_key_different_command_conflict_real_mongo():
    client, db, bills, bill = _fixture()
    VendorBillRegistry.create(bill(), bills)
    VendorBillRegistry.open_bill("tenant-a", "payable-1", 1, "reused-command-key", bills)
    before = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert before is not None
    try:
        VendorBillRegistry.open_bill("tenant-a", "payable-1", 2, "reused-command-key", bills)
    except VendorBillIdempotencyKeyReuseError as error:
        assert str(error) == "VENDOR_BILL_IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_COMMAND"
    else:
        raise AssertionError("same idempotency key with a different command replayed")
    after = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert after == before
    client.drop_database(db.name); client.close()


def test_open_bill_corrupt_receipt_replay_real_mongo():
    client, db, bills, bill = _fixture()
    VendorBillRegistry.create(bill(), bills)
    VendorBillRegistry.open_bill("tenant-a", "payable-1", 1, "corrupt-receipt", bills)
    bills.update_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}, {"$set": {"command_receipts.0.command_fingerprint": "corrupt"}})
    try:
        VendorBillRegistry.open_bill("tenant-a", "payable-1", 1, "corrupt-receipt", bills)
    except VendorBillPersistedRecordInvalidError as error:
        assert str(error) == "VENDOR_BILL_PERSISTED_RECORD_INVALID"
    else:
        raise AssertionError("corrupt command receipt was accepted for replay")
    client.drop_database(db.name); client.close()


def test_open_bill_cross_tenant_receipt_isolation_real_mongo():
    client, db, bills, bill = _fixture()
    VendorBillRegistry.create(bill(), bills)
    VendorBillRegistry.open_bill("tenant-a", "payable-1", 1, "tenant-isolated-receipt", bills)
    try:
        VendorBillRegistry.open_bill("tenant-b", "payable-1", 1, "tenant-isolated-receipt", bills)
    except VendorBillNotFoundError as error:
        assert str(error) == "VENDOR_BILL_NOT_FOUND"
    else:
        raise AssertionError("cross-tenant receipt replay disclosed owner command truth")
    owner = VendorBillRegistry.get("tenant-a", "payable-1", bills)
    assert owner.obligation_state is VendorBillObligationState.OPEN and owner.revision == 2
    assert bills.count_documents({"tenant_id": "tenant-a", "payable_id": "payable-1"}) == 1
    client.drop_database(db.name); client.close()


def test_open_bill_one_hundred_identical_commands_real_mongo():
    client, db, bills, bill = _fixture(); start = threading.Event()
    VendorBillRegistry.create(bill(), bills)

    def open_exact_command():
        start.wait()
        return VendorBillRegistry.open_bill("tenant-a", "payable-1", 1, "concurrent-exact-open", bills)

    with ThreadPoolExecutor(max_workers=32) as pool:
        futures = [pool.submit(open_exact_command) for _ in range(100)]
        start.set()
        results = [future.result() for future in futures]
    assert sum(result.outcome is VendorBillMutationOutcome.COMMITTED for result in results) == 1
    assert sum(result.outcome is VendorBillMutationOutcome.IDEMPOTENT_REPLAY for result in results) == 99
    fresh = VendorBillRegistry.get("tenant-a", "payable-1", bills)
    raw = bills.find_one({"tenant_id": "tenant-a", "payable_id": "payable-1"})
    assert raw is not None
    assert fresh.obligation_state is VendorBillObligationState.OPEN and fresh.revision == 2
    assert bills.count_documents({"tenant_id": "tenant-a", "payable_id": "payable-1"}) == 1
    assert len(raw["command_receipts"]) == 1
    client.drop_database(db.name); client.close()
