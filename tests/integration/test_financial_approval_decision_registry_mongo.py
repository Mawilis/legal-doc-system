import os
import threading
import uuid
from typing import Any
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timezone

from pymongo import MongoClient
from pymongo.read_concern import ReadConcern

from tools.eos.saas.billing.financial_approval_decision_registry import FinancialApprovalDecisionCreateConflictError, FinancialApprovalDecisionCreateOutcome, FinancialApprovalDecisionPersistedRecordInvalidError, FinancialApprovalDecisionRegistry, FinancialApprovalSubjectIneligibleError, FinancialApprovalSubjectRevisionConflictError
from tools.eos.saas.billing.vendor_bill_registry import VendorBillNotFoundError, VendorBillRegistry
from tools.eos.saas.billing.vendor_registry import VendorRegistry
from tools.eos.saas.domain.financial_approval_decision import FinancialApprovalDecision, FinancialApprovalDecisionType, FinancialApprovalSubjectType
from tools.eos.saas.domain.vendor import VendorIdentity
from tools.eos.saas.domain.vendor_bill import VendorBill, VendorBillObligationState


def _fixture():
    client = MongoClient(os.environ["TEST_VENDOR_MONGO_URI"], serverSelectionTimeoutMS=5000, retryWrites=True)
    assert client.admin.command("hello")["isWritablePrimary"]
    db = client[f"wilsy_financial_approval_cert_{uuid.uuid4().hex}"]
    vendors, bills, decisions = db["vendors"], db["vendor_bills"], db["financial_approval_decisions"]
    VendorRegistry.ensure_indexes(vendors); VendorBillRegistry.ensure_indexes(bills); FinancialApprovalDecisionRegistry.ensure_indexes(decisions)
    vendor = VendorRegistry.create(VendorIdentity(tenant_id="tenant-a", legal_name="Approval Certification Vendor"), vendors)

    def open_bill(payable_id="payable-1", tenant_id="tenant-a", state=VendorBillObligationState.DRAFT, transition=True):
        current = VendorBill(tenant_id=tenant_id, vendor_id=vendor.vendor_id, payable_id=payable_id, gross_amount_minor=10000, currency="ZAR", issue_date=date(2026, 8, 25), due_date=date(2026, 9, 25), received_at=datetime(2026, 8, 25, tzinfo=timezone.utc), obligation_state=state)
        VendorBillRegistry.create(current, bills)
        if not transition:
            return current
        return VendorBillRegistry.open_bill(tenant_id, payable_id, 1, f"open-{payable_id}", bills).vendor_bill

    def decision(decision_id="decision-1", payable_id="payable-1", revision=2, outcome=FinancialApprovalDecisionType.APPROVED):
        return FinancialApprovalDecision(tenant_id="tenant-a", decision_id=decision_id, subject_type=FinancialApprovalSubjectType.VENDOR_BILL, subject_id=payable_id, decision=outcome, actor_id="approver-1", actor_capacity="FINANCE_APPROVER", reason="Evidence reviewed", approval_policy_reference="AP-POLICY-1", subject_revision=revision, decided_at=datetime(2026, 8, 25, tzinfo=timezone.utc), created_at=datetime(2026, 8, 25, tzinfo=timezone.utc), evidence_references=("proof-1",))
    return client, db, bills, decisions, open_bill, decision


def test_create_replay_conflict_get_and_list_real_mongo():
    client, db, _, decisions, open_bill, decision = _fixture(); open_bill()
    first = FinancialApprovalDecisionRegistry.create(decision(), "decision-key", decisions)
    replay = FinancialApprovalDecisionRegistry.create(decision(), "decision-key", decisions)
    assert first.outcome is FinancialApprovalDecisionCreateOutcome.CREATED
    assert replay.outcome is FinancialApprovalDecisionCreateOutcome.IDEMPOTENT_REPLAY
    assert decisions.count_documents({}) == 1
    try:
        FinancialApprovalDecisionRegistry.create(decision(outcome=FinancialApprovalDecisionType.REJECTED), "other-key", decisions)
    except FinancialApprovalDecisionCreateConflictError as error:
        assert str(error) == "FINANCIAL_APPROVAL_DECISION_CREATE_CONFLICT"
    else: raise AssertionError("different immutable command accepted")
    FinancialApprovalDecisionRegistry.create(decision("decision-2", outcome=FinancialApprovalDecisionType.REJECTED), "decision-key-2", decisions)
    listed = FinancialApprovalDecisionRegistry.list_for_subject("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 1, decisions)
    assert len(listed) == 1 and FinancialApprovalDecisionRegistry.get("tenant-a", "decision-1", decisions).decision is FinancialApprovalDecisionType.APPROVED
    client.drop_database(db.name); client.close()

def test_list_for_subject_shared_session_real_mongo():
    client, db, _, decisions, open_bill, decision = _fixture(); open_bill()
    FinancialApprovalDecisionRegistry.create(decision("decision-1"), "key-1", decisions)
    FinancialApprovalDecisionRegistry.create(decision("decision-2", outcome=FinancialApprovalDecisionType.REJECTED), "key-2", decisions)
    plain = FinancialApprovalDecisionRegistry.list_for_subject("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 10, decisions)
    assert [item.decision_id for item in plain] == ["decision-1", "decision-2"]
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"))
        listed = FinancialApprovalDecisionRegistry.list_for_subject("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 10, decisions, session=session)
        assert [item.decision_id for item in listed] == ["decision-1", "decision-2"]
        assert FinancialApprovalDecisionRegistry.list_for_subject("tenant-b", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 10, decisions, session=session) == []
        session.abort_transaction()
    decisions.update_one({"tenant_id": "tenant-a", "decision_id": "decision-1"}, {"$set": {"create_fingerprint": "invalid"}})
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"))
        try: FinancialApprovalDecisionRegistry.list_for_subject("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 10, decisions, session=session)
        except FinancialApprovalDecisionPersistedRecordInvalidError: pass
        else: raise AssertionError("corrupt decision accepted")
        session.abort_transaction()
    client.drop_database(db.name); client.close()

def test_bounded_keyset_pagination_real_mongo():
    client, db, _, decisions, open_bill, decision = _fixture(); open_bill()
    for index in range(23):
        FinancialApprovalDecisionRegistry.create(decision(f"page-{index:03d}"), f"page-key-{index}", decisions)
    cursor = None; seen = []; sizes = []
    while True:
        page = FinancialApprovalDecisionRegistry.list_for_subject_page("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 5, cursor, decisions)
        sizes.append(len(page.items)); seen.extend(item.decision_id for item in page.items)
        if page.next_cursor is None: break
        cursor = page.next_cursor
    assert sizes == [5, 5, 5, 5, 3] and len(seen) == len(set(seen)) == 23
    invalid_sizes: tuple[Any, ...] = (True, False, 0, -1, 251, "10", None)
    for bad in invalid_sizes:
        if bad is None: continue
        try: FinancialApprovalDecisionRegistry.list_for_subject_page("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", bad, None, decisions)
        except Exception: pass
        else: raise AssertionError("invalid page size accepted")
    client.drop_database(db.name); client.close()

def test_keyset_pagination_260_records_and_cursor_validation_real_mongo():
    client, db, _, decisions, open_bill, decision = _fixture(); open_bill()
    for index in range(260):
        FinancialApprovalDecisionRegistry.create(decision(f"bulk-{index:03d}"), f"bulk-key-{index}", decisions)
    cursor = None; seen = []; sizes = []
    while True:
        page = FinancialApprovalDecisionRegistry.list_for_subject_page("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 250, cursor, decisions)
        sizes.append(len(page.items)); seen.extend(item.decision_id for item in page.items)
        if page.next_cursor is None: break
        cursor = page.next_cursor
    assert sizes == [250, 10] and len(seen) == len(set(seen)) == 260
    for bad in ("", " ", "not-base64", "e30=", "eyJjcmVhdGVkX2F0IjoxfQ==", "eyJjcmVhdGVkX2F0IjoiMjAyNi0wMS0wMVQwMDowMDowMFoiLCJkZWNpc2lvbl9pZCI6MX0=", "A" * 513):
        try:
            FinancialApprovalDecisionRegistry.list_for_subject_page("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 5, bad, decisions)
        except Exception:
            pass
        else:
            raise AssertionError("invalid cursor accepted")
    client.drop_database(db.name); client.close()

def test_keyset_pagination_shared_snapshot_and_later_page_corruption_real_mongo():
    client, db, _, decisions, open_bill, decision = _fixture(); open_bill()
    for index in range(260): FinancialApprovalDecisionRegistry.create(decision(f"snap-{index:03d}"), f"snap-key-{index}", decisions)
    with client.start_session() as session:
        session.start_transaction(read_concern=ReadConcern("snapshot"))
        page = FinancialApprovalDecisionRegistry.list_for_subject_page("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 250, None, decisions, session=session)
        assert len(page.items) == 250 and page.next_cursor is not None
        outside = MongoClient(os.environ["TEST_VENDOR_MONGO_URI"]); ext = outside[db.name]["financial_approval_decisions"]
        extra = decision("snap-new"); FinancialApprovalDecisionRegistry.create(extra, "snap-new-key", ext); outside.close()
        page2 = FinancialApprovalDecisionRegistry.list_for_subject_page("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 250, page.next_cursor, decisions, session=session)
        assert len(page2.items) == 10 and "snap-new" not in {item.decision_id for item in page2.items}
        session.commit_transaction()
    fresh = FinancialApprovalDecisionRegistry.list_for_subject_page("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 250, None, decisions)
    fresh2 = FinancialApprovalDecisionRegistry.list_for_subject_page("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 250, fresh.next_cursor, decisions)
    assert "snap-new" in {item.decision_id for item in fresh.items + fresh2.items}
    decisions.update_one({"decision_id": "snap-255"}, {"$set": {"create_fingerprint": "invalid"}})
    first = FinancialApprovalDecisionRegistry.list_for_subject_page("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 250, None, decisions)
    assert len(first.items) == 250
    try: FinancialApprovalDecisionRegistry.list_for_subject_page("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 10, first.next_cursor, decisions)
    except FinancialApprovalDecisionPersistedRecordInvalidError: pass
    else: raise AssertionError("corrupt later-page decision was skipped")
    client.drop_database(db.name); client.close()


def test_subject_boundaries_and_cross_tenant_real_mongo():
    client, db, bills, decisions, open_bill, decision = _fixture(); open_bill()
    try: FinancialApprovalDecisionRegistry.create(decision(revision=1), "stale", decisions)
    except FinancialApprovalSubjectRevisionConflictError: pass
    else: raise AssertionError("stale subject revision accepted")
    try: FinancialApprovalDecisionRegistry.create(decision(payable_id="missing"), "missing", decisions)
    except VendorBillNotFoundError: pass
    else: raise AssertionError("missing subject accepted")
    try: FinancialApprovalDecisionRegistry.create(FinancialApprovalDecision(tenant_id="tenant-b", decision_id="cross", subject_type=FinancialApprovalSubjectType.VENDOR_BILL, subject_id="payable-1", decision=FinancialApprovalDecisionType.APPROVED, actor_id="a", actor_capacity="FINANCE_APPROVER", reason="r", approval_policy_reference="p", subject_revision=2), "cross", decisions)
    except VendorBillNotFoundError: pass
    else: raise AssertionError("cross-tenant subject accepted")
    FinancialApprovalDecisionRegistry.create(decision(), "valid", decisions)
    try: FinancialApprovalDecisionRegistry.get("tenant-b", "decision-1", decisions)
    except Exception as error: assert str(error) == "FINANCIAL_APPROVAL_DECISION_NOT_FOUND"
    else: raise AssertionError("cross-tenant decision disclosed")
    bills.update_one({"tenant_id": "tenant-a", "payable_id": "payable-1"}, {"$set": {"revision": "corrupt"}})
    try: FinancialApprovalDecisionRegistry.create(decision("malformed-subject"), "malformed", decisions)
    except VendorBillNotFoundError: raise AssertionError("malformed subject misclassified as missing")
    except Exception as error: assert str(error) == "VENDOR_BILL_PERSISTED_RECORD_INVALID"
    client.drop_database(db.name); client.close()


def test_ineligible_and_corrupt_decision_real_mongo():
    client, db, _, decisions, open_bill, decision = _fixture(); open_bill("draft", state=VendorBillObligationState.DRAFT, transition=False)
    try: FinancialApprovalDecisionRegistry.create(decision("draft-decision", "draft", 1), "draft", decisions)
    except FinancialApprovalSubjectIneligibleError as error: assert str(error) == "FINANCIAL_APPROVAL_SUBJECT_INELIGIBLE"
    else: raise AssertionError("DRAFT subject accepted")
    open_bill(); FinancialApprovalDecisionRegistry.create(decision(), "corrupt", decisions)
    decisions.update_one({"tenant_id": "tenant-a", "decision_id": "decision-1"}, {"$set": {"create_fingerprint": "invalid"}})
    for action in (lambda: FinancialApprovalDecisionRegistry.get("tenant-a", "decision-1", decisions), lambda: FinancialApprovalDecisionRegistry.list_for_subject("tenant-a", FinancialApprovalSubjectType.VENDOR_BILL, "payable-1", 10, decisions), lambda: FinancialApprovalDecisionRegistry.create(decision(), "corrupt", decisions)):
        try: action()
        except FinancialApprovalDecisionPersistedRecordInvalidError: pass
        else: raise AssertionError("corrupt decision accepted")
    client.drop_database(db.name); client.close()


def test_one_hundred_identical_and_different_command_contention_real_mongo():
    client, db, _, decisions, open_bill, decision = _fixture(); open_bill(); start = threading.Event()
    with ThreadPoolExecutor(max_workers=32) as pool:
        futures = [pool.submit(lambda: (start.wait(), FinancialApprovalDecisionRegistry.create(decision(), "same-key", decisions))[1]) for _ in range(100)]
        start.set(); results = [future.result() for future in futures]
    assert sum(result.outcome is FinancialApprovalDecisionCreateOutcome.CREATED for result in results) == 1
    assert sum(result.outcome is FinancialApprovalDecisionCreateOutcome.IDEMPOTENT_REPLAY for result in results) == 99
    assert decisions.count_documents({"decision_id": "decision-1"}) == 1
    client.drop_database(db.name); client.close()


def test_one_hundred_different_command_identity_races_real_mongo():
    client, db, _, decisions, open_bill, decision = _fixture(); winners = conflicts = 0
    for race in range(100):
        payable_id, decision_id = f"payable-race-{race}", f"decision-race-{race}"
        open_bill(payable_id); start, outcomes = threading.Barrier(2), []

        def create_candidate(outcome, key):
            try:
                start.wait()
                outcomes.append(FinancialApprovalDecisionRegistry.create(decision(decision_id, payable_id, 2, outcome), key, decisions))
            except Exception as error:
                outcomes.append(error)

        workers = [threading.Thread(target=create_candidate, args=(FinancialApprovalDecisionType.APPROVED, f"approved-{race}")), threading.Thread(target=create_candidate, args=(FinancialApprovalDecisionType.REJECTED, f"rejected-{race}"))]
        [worker.start() for worker in workers]; [worker.join() for worker in workers]
        winners += sum(isinstance(item, type(next(item for item in outcomes if not isinstance(item, Exception)))) for item in outcomes if not isinstance(item, Exception))
        conflicts += sum(isinstance(item, FinancialApprovalDecisionCreateConflictError) for item in outcomes)
        assert decisions.count_documents({"tenant_id": "tenant-a", "decision_id": decision_id}) == 1
    assert winners == conflicts == 100
    client.drop_database(db.name); client.close()
