"""WILSY OS — VENDOR BILL RELEASE ORCHESTRATOR REAL-MONGO CERTIFICATION
Version: v1.1.2-VENDOR-BILL-RELEASE-ORCHESTRATOR-EXACT-CONCURRENT-CONVERGENCE-MONGO-CERT
Authority: Wilsy OS Core Governance
Architecture: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
Runtime: caller-owned Mongo transactions; Kennel EOS exclusively executes money.
"""
from datetime import datetime, timezone, date
from typing import Any
from dataclasses import replace
import pytest
import os, uuid
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pymongo import MongoClient
from tools.eos.saas.domain.vendor import VendorIdentity
from tools.eos.saas.domain.financial_approval_policy_evaluation import FinancialApprovalRequirement, FinancialApprovalPolicyEvaluation, FinancialApprovalPolicySubjectType, FinancialApprovalRejectionRule
from tools.eos.saas.domain.financial_approval_decision import FinancialApprovalDecision, FinancialApprovalDecisionType, FinancialApprovalSubjectType
from tools.eos.saas.domain.financial_approval_actor_authorization import FinancialApprovalActorAuthorization
from tools.eos.saas.billing.vendor_registry import VendorRegistry
from tools.eos.saas.billing.financial_approval_policy_evaluation_registry import FinancialApprovalPolicyEvaluationRegistry, _compute_vendor_bill_policy_snapshot_fingerprint
from tools.eos.saas.billing.financial_approval_decision_registry import FinancialApprovalDecisionRegistry
from tools.eos.saas.billing.financial_approval_actor_authorization_registry import FinancialApprovalActorAuthorizationRegistry
from tools.eos.saas.domain.financial_approval_effective_result import FinancialApprovalEffectiveState
from tools.eos.saas.domain.vendor_bill import VendorBill, VendorBillObligationState, VendorBillApprovalState
from unittest.mock import patch

from tools.eos.saas.billing.vendor_bill_release_orchestrator import (
    VendorBillReleaseCommand, VendorBillReleaseOrchestrator,
    VendorBillReleaseOrchestrationOutcome, VendorBillReleaseOrchestrationIdempotencyError,
    VendorBillReleaseOrchestrationError,
)
from tools.eos.saas.billing.vendor_bill_release_authorization_registry import VendorBillReleaseAuthorizationRegistry, VendorBillReleaseAuthorizationNotFoundError
from pymongo import MongoClient
from tools.eos.saas.billing.vendor_bill_registry import VendorBillRegistry
from tools.eos.saas.domain.vendor_bill_release_policy import VendorBillReleasePolicyError
from tools.eos.saas.billing.financial_approval_aggregator import FinancialApprovalAggregator
from tools.eos.saas.billing.financial_approval_effective_result_registry import FinancialApprovalEffectiveResultRegistry
from tools.eos.saas.billing.vendor_bill_registry import VendorBillApprovalProjectionConflictError


def _command(bill, suffix="a", amount=100):
    return VendorBillReleaseCommand(bill.tenant_id, bill.payable_id, f"release-{suffix}", amount, "ZAR", "actor", "basis", datetime(2026, 1, 2, tzinfo=timezone.utc), f"key-{suffix}")


def test_vendor_bill_release_orchestrator_basic_atomic_authorization_real_mongo():
    client, db, bill = _fixture()
    try:
        result = VendorBillReleaseOrchestrator.authorize(_command(bill), db)
        assert result.outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED
        assert db["vendor_bill_release_authorizations"].count_documents({"tenant_id":bill.tenant_id,"payable_id":bill.payable_id}) == 1
        assert VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor(bill.tenant_id, bill.payable_id, db["vendor_bill_release_authorizations"]) == 100
        assert VendorBillRegistry.get(bill.tenant_id, bill.payable_id, db["vendor_bills"]).release_authority_guard_revision == 1
    finally: client.drop_database(db.name); client.close()


def test_vendor_bill_release_orchestrator_exact_replay_real_mongo():
    client, db, bill = _fixture()
    try:
        command = _command(bill); first = VendorBillReleaseOrchestrator.authorize(command, db); second = VendorBillReleaseOrchestrator.authorize(command, db)
        assert first.outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED and second.outcome is VendorBillReleaseOrchestrationOutcome.IDEMPOTENT_REPLAY
        assert db["vendor_bill_release_authorizations"].count_documents({"tenant_id":bill.tenant_id,"payable_id":bill.payable_id}) == 1
        assert VendorBillRegistry.get(bill.tenant_id, bill.payable_id, db["vendor_bills"]).release_authority_guard_revision == 1
    finally: client.drop_database(db.name); client.close()


@pytest.mark.parametrize("field,value", [("release_authorization_id","other"),("requested_amount_minor",101),("currency","USD"),("authorized_by_actor_id","other"),("authorization_basis_reference","other"),("authorized_at",datetime(2026,1,3,tzinfo=timezone.utc))])
def test_vendor_bill_release_orchestrator_divergent_same_key_fails_closed_real_mongo(field, value):
    client, db, bill = _fixture()
    try:
        command = _command(bill); VendorBillReleaseOrchestrator.authorize(command, db)
        with pytest.raises(VendorBillReleaseOrchestrationIdempotencyError, match="VENDOR_BILL_RELEASE_AUTHORIZATION_IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_COMMAND"):
            VendorBillReleaseOrchestrator.authorize(replace(command, **{field:value}), db)
        assert db["vendor_bill_release_authorizations"].count_documents({"tenant_id":bill.tenant_id,"payable_id":bill.payable_id}) == 1
    finally: client.drop_database(db.name); client.close()


def test_vendor_bill_release_orchestrator_cumulative_partial_reservations_real_mongo():
    client, db, bill = _fixture()
    try:
        assert VendorBillReleaseOrchestrator.authorize(_command(bill,"a",400), db).outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED
        assert VendorBillReleaseOrchestrator.authorize(_command(bill,"b",350), db).outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED
        assert VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor(bill.tenant_id,bill.payable_id,db["vendor_bill_release_authorizations"]) == 750
    finally: client.drop_database(db.name); client.close()


def test_vendor_bill_release_orchestrator_over_reservation_denied_real_mongo():
    client, db, bill = _fixture()
    try:
        VendorBillReleaseOrchestrator.authorize(_command(bill,"a",900), db)
        with pytest.raises(Exception, match="CUMULATIVE_AUTHORITY_EXCEEDED"):
            VendorBillReleaseOrchestrator.authorize(_command(bill,"b",200), db)
        assert db["vendor_bill_release_authorizations"].count_documents({"tenant_id":bill.tenant_id,"payable_id":bill.payable_id}) == 1
        assert VendorBillRegistry.get(bill.tenant_id,bill.payable_id,db["vendor_bills"]).release_authority_guard_revision == 1
    finally: client.drop_database(db.name); client.close()


def test_vendor_bill_release_orchestrator_transaction_abort_is_atomic_real_mongo():
    client, db, bill = _fixture()
    try:
        command = _command(bill)
        with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.create", side_effect=RuntimeError("injected abort")):
            with pytest.raises(RuntimeError, match="injected abort"):
                VendorBillReleaseOrchestrator.authorize(command, db, max_attempts=1)
        fresh = VendorBillRegistry.get(bill.tenant_id,bill.payable_id,db["vendor_bills"])
        assert fresh.release_authority_guard_revision == 0
        assert db["vendor_bill_release_authorizations"].count_documents({"tenant_id":bill.tenant_id,"payable_id":bill.payable_id}) == 0
    finally: client.drop_database(db.name); client.close()


@dataclass(frozen=True)
class _CanonicalSpike:
    client: Any
    database: Any
    tenant_id: str
    payable_id: str
    bill: VendorBill
    effective_result: Any


def _fixture(amount: int = 1000):
    uri = os.environ.get("TEST_VENDOR_MONGO_URI")
    if not uri:
        pytest.skip("TEST_VENDOR_MONGO_URI is not configured")
    client = MongoClient(uri, serverSelectionTimeoutMS=3000)
    try:
        try:
            hello = client.admin.command("hello")
        except Exception as error:
            client.close()
            pytest.skip("MONGO_CERTIFICATION_ENDPOINT_UNAVAILABLE:" + type(error).__name__)
        if hello.get("setName") != "wilsyVendorCertRS" or hello.get("isWritablePrimary") is not True:
            pytest.skip(f"MONGO_CERTIFICATION_TOPOLOGY_INVALID:setName={hello.get('setName')!r}:isWritablePrimary={hello.get('isWritablePrimary')!r}")
        ns = uuid.uuid4().hex
        tenant, payable, vendor_id, policy_ref = f"tenant-{ns}", f"payable-{ns}", f"vendor-{ns}", f"policy-{ns}"
        db = client[f"vendor_bill_release_canonical_{ns}"]; vendors, bills, policies, decisions, auths, results = [db[n] for n in ("vendors","vendor_bills","financial_approval_policy_evaluations","financial_approval_decisions","financial_approval_actor_authorizations","financial_approval_effective_results")]
        VendorRegistry.ensure_indexes(vendors); VendorBillRegistry.ensure_indexes(bills); FinancialApprovalPolicyEvaluationRegistry.ensure_indexes(policies); FinancialApprovalDecisionRegistry.ensure_indexes(decisions); FinancialApprovalActorAuthorizationRegistry.ensure_indexes(auths); FinancialApprovalEffectiveResultRegistry.ensure_indexes(results)
        VendorRegistry.create(VendorIdentity(tenant_id=tenant, legal_name="V", vendor_id=vendor_id), vendors)
        bill = VendorBill(tenant_id=tenant, vendor_id=vendor_id, payable_id=payable, gross_amount_minor=amount, currency="ZAR", issue_date=date(2026,1,1), due_date=date(2026,2,1), received_at=datetime(2026,1,1,tzinfo=timezone.utc), approval_policy_reference=policy_ref)
        VendorBillRegistry.create(bill, bills); opened = VendorBillRegistry.open_bill(tenant, payable, 1, f"open-{ns}", bills).vendor_bill
        req = FinancialApprovalRequirement(f"requirement-{ns}", "CFO", 1); evaluation = FinancialApprovalPolicyEvaluation(tenant_id=tenant, evaluation_id=f"evaluation-{ns}", subject_type=FinancialApprovalPolicySubjectType.VENDOR_BILL, subject_id=payable, subject_revision=2, approval_policy_reference=policy_ref, approval_policy_version="1", approval_required=True, approval_requirements=(req,), rejection_rule=FinancialApprovalRejectionRule.ANY_VALID_REJECTION_BLOCKS, rejections_required=None, subject_snapshot_fingerprint=_compute_vendor_bill_policy_snapshot_fingerprint(opened), evaluator_reference="r", evaluated_at=datetime(2026,1,1,tzinfo=timezone.utc), created_at=datetime(2026,1,1,tzinfo=timezone.utc)); FinancialApprovalPolicyEvaluationRegistry.create(evaluation, f"evaluation-key-{ns}", policies)
        decision = FinancialApprovalDecision(tenant_id=tenant, decision_id=f"decision-{ns}", subject_type=FinancialApprovalSubjectType.VENDOR_BILL, subject_id=payable, decision=FinancialApprovalDecisionType.APPROVED, actor_id=f"actor-{ns}", actor_capacity="CFO", reason="r", approval_policy_reference=policy_ref, approval_policy_version="1", subject_revision=2, decided_at=datetime(2026,1,1,tzinfo=timezone.utc), created_at=datetime(2026,1,1,tzinfo=timezone.utc)); FinancialApprovalDecisionRegistry.create(decision, f"decision-key-{ns}", decisions)
        authorization = FinancialApprovalActorAuthorization(tenant_id=tenant, authorization_id=f"actor-auth-{ns}", subject_type=FinancialApprovalPolicySubjectType.VENDOR_BILL, subject_id=payable, subject_revision=2, evaluation_id=evaluation.evaluation_id, approval_policy_reference=policy_ref, approval_policy_version="1", requirement_id=req.requirement_id, actor_id=f"actor-{ns}", actor_capacity="CFO", authorization_source_reference="s", authorization_basis_reference="b", authorized_at=datetime(2026,1,1,tzinfo=timezone.utc), authorization_evidence_fingerprint="a"*128, created_at=datetime(2026,1,1,tzinfo=timezone.utc)); FinancialApprovalActorAuthorizationRegistry.create(authorization, f"auth-key-{ns}", auths)
        effective = FinancialApprovalAggregator(database=db).aggregate(tenant, evaluation.evaluation_id, f"effective-{ns}", datetime(2026,1,2,tzinfo=timezone.utc), datetime(2026,1,2,tzinfo=timezone.utc)); assert effective.effective_state is FinancialApprovalEffectiveState.APPROVED; FinancialApprovalEffectiveResultRegistry.create(effective, f"effective-key-{ns}", results); VendorBillRegistry.project_financial_approval_result(tenant, payable, effective.result_id, 2, 0, f"projection-{ns}", bills); projected = VendorBillRegistry.get(tenant, payable, bills); return client, db, projected
    except Exception:
        client.close(); raise


def test_vendor_bill_release_orchestrator_remaining_capacity_race_real_mongo():
    client, db, bill = _fixture()
    try:
        auths = db["vendor_bill_release_authorizations"]
        seed = VendorBillReleaseOrchestrator.authorize(_command(bill, "seed", 600), db)
        assert seed.outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED
        assert VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor(bill.tenant_id, bill.payable_id, auths) == 600
        barrier = threading.Barrier(2, timeout=30)
        observed = []
        real_sum_authorized_amount_minor = VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor
        local = threading.local()

        def synchronized_sum(*args, **kwargs):
            amount = real_sum_authorized_amount_minor(*args, **kwargs)
            if not getattr(local, "is_competing_worker", False) or getattr(local, "first_sum_seen", False):
                return amount
            local.first_sum_seen = True
            observed.append(amount)
            barrier.wait(timeout=30)
            return amount

        def invoke(command):
            local.is_competing_worker = True
            with patch.object(VendorBillReleaseAuthorizationRegistry, "sum_authorized_amount_minor", synchronized_sum):
                try:
                    return ("AUTHORIZED", VendorBillReleaseOrchestrator.authorize(command, db))
                except VendorBillReleaseOrchestrationError as error:
                    assert str(error) == "CUMULATIVE_AUTHORITY_EXCEEDED"
                    return ("DENIED", error)
                finally:
                    local.is_competing_worker = False

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(invoke, _command(bill, "a", 300)), executor.submit(invoke, _command(bill, "b", 300))]
            outcomes = [future.result(timeout=30) for future in futures]
        assert len(observed) == 2
        assert sorted(observed) == [600, 600]
        assert [kind for kind, _ in outcomes].count("AUTHORIZED") == 1
        assert [kind for kind, _ in outcomes].count("DENIED") == 1
        assert auths.count_documents({"tenant_id": bill.tenant_id, "payable_id": bill.payable_id}) == 2
        assert real_sum_authorized_amount_minor(bill.tenant_id, bill.payable_id, auths) == 900
        assert VendorBillRegistry.get(bill.tenant_id, bill.payable_id, db["vendor_bills"]).release_authority_guard_revision == 2
    finally:
        client.drop_database(db.name); client.close()


def test_vendor_bill_release_orchestrator_exact_command_concurrent_convergence_real_mongo():
    client, db, bill = _fixture()
    try:
        command = _command(bill, "convergent", 100)
        barrier = threading.Barrier(20, timeout=30)
        states = []
        local = threading.local()
        real_lookup = VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key

        def synchronized_lookup(*args, **kwargs):
            try:
                value = real_lookup(*args, **kwargs)
                state = ("FOUND", value)
            except VendorBillReleaseAuthorizationNotFoundError as error:
                state = ("NOT_FOUND", error)
            if not getattr(local, "waited", False):
                local.waited = True
                states.append(state[0])
                barrier.wait(timeout=30)
            if state[0] == "FOUND":
                return state[1]
            raise state[1]

        def invoke():
            with patch.object(VendorBillReleaseAuthorizationRegistry, "get_by_idempotency_key", synchronized_lookup):
                return VendorBillReleaseOrchestrator.authorize(command, db).outcome

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(invoke) for _ in range(20)]
            outcomes = [future.result(timeout=30) for future in futures]
        assert len(states) == 20
        assert states == ["NOT_FOUND"] * 20
        assert all(outcome in (VendorBillReleaseOrchestrationOutcome.AUTHORIZED, VendorBillReleaseOrchestrationOutcome.IDEMPOTENT_REPLAY) for outcome in outcomes)
        assert VendorBillReleaseOrchestrationOutcome.AUTHORIZED in outcomes
        auths = db["vendor_bill_release_authorizations"]
        durable = real_lookup(bill.tenant_id, bill.payable_id, command.idempotency_key, auths)
        assert durable.tenant_id == command.tenant_id
        assert durable.payable_id == command.payable_id
        assert durable.release_authorization_id == command.release_authorization_id
        assert durable.authorized_amount_minor == 100
        assert durable.currency == command.currency
        assert auths.count_documents({"tenant_id": bill.tenant_id, "payable_id": bill.payable_id, "create_idempotency_key": command.idempotency_key}) == 1
        assert auths.count_documents({"tenant_id": bill.tenant_id, "release_authorization_id": command.release_authorization_id}) == 1
        assert VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor(bill.tenant_id, bill.payable_id, auths) == 100
        assert VendorBillRegistry.get(bill.tenant_id, bill.payable_id, db["vendor_bills"]).release_authority_guard_revision == 1
    finally:
        client.drop_database(db.name); client.close()


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_vendor_bill_release_orchestrator_mongo.py
# VERSION: v1.1.2-VENDOR-BILL-RELEASE-ORCHESTRATOR-EXACT-CONCURRENT-CONVERGENCE-MONGO-CERT
# AUTHORITY: Wilsy OS Core Governance
# END OF WILSY OS SOVEREIGN ARTIFACT
