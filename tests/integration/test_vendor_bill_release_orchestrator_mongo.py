"""WILSY OS — VENDOR BILL RELEASE ORCHESTRATOR REAL-MONGO CERTIFICATION
Version: v1.0.0-VENDOR-BILL-RELEASE-ORCHESTRATOR-MONGO-CERT
Authority: Wilsy OS Core Governance
Architecture: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
Runtime: caller-owned Mongo transactions; Kennel EOS exclusively executes money.
"""
from datetime import datetime, timezone
from dataclasses import replace
import pytest
from unittest.mock import patch

from tools.eos.saas.billing.vendor_bill_release_orchestrator import (
    VendorBillReleaseCommand, VendorBillReleaseOrchestrator,
    VendorBillReleaseOrchestrationOutcome, VendorBillReleaseOrchestrationIdempotencyError,
)
from tools.eos.saas.billing.vendor_bill_release_authorization_registry import VendorBillReleaseAuthorizationRegistry
from pymongo import MongoClient
from tools.eos.saas.billing.vendor_bill_registry import VendorBillRegistry
from tools.eos.saas.domain.vendor_bill_release_policy import VendorBillReleasePolicyError
from tests.integration.test_financial_approval_aggregator_mongo import fixture as approval_fixture, add_evidence
from tools.eos.saas.billing.financial_approval_aggregator import FinancialApprovalAggregator
from tools.eos.saas.billing.financial_approval_effective_result_registry import FinancialApprovalEffectiveResultRegistry
from tools.eos.saas.billing.vendor_bill_registry import VendorBillApprovalProjectionConflictError


def _fixture(amount: int = 1000):
    uri = __import__("os").environ.get("TEST_VENDOR_MONGO_URI")
    if not uri:
        pytest.skip("TEST_VENDOR_MONGO_URI is not configured")
    probe = MongoClient(uri, serverSelectionTimeoutMS=2000)
    try:
        probe.admin.command("hello")
    except Exception as error:
        pytest.skip(f"MongoDB certification environment unavailable: {error}")
    finally:
        probe.close()
    client, db, _, decisions, authorizations, evaluation, opened = approval_fixture(1)
    db["vendor_bills"].update_one({"tenant_id": "t", "payable_id": "p"}, {"$set": {"gross_amount_minor": amount, "outstanding_amount_minor": amount}})
    add_evidence(decisions, authorizations, evaluation, opened, "A", "decision-a")
    result = FinancialApprovalAggregator(database=db).aggregate("t", "e", "orchestrator-result", datetime.now(timezone.utc), datetime.now(timezone.utc))
    results = db["financial_approval_effective_results"]
    FinancialApprovalEffectiveResultRegistry.create(result, "result-key", results)
    VendorBillRegistry.project_financial_approval_result("t", "p", result.result_id, opened.revision, 0, "projection-key", db["vendor_bills"])
    bill = VendorBillRegistry.get("t", "p", db["vendor_bills"])
    assert bill.approval_state.value == "APPROVED"
    return client, db, bill


def _command(bill, suffix="a", amount=100):
    return VendorBillReleaseCommand("t", "p", f"release-{suffix}", amount, "ZAR", "actor", "basis", datetime(2026, 1, 2, tzinfo=timezone.utc), f"key-{suffix}")


def test_vendor_bill_release_orchestrator_basic_atomic_authorization_real_mongo():
    client, db, bill = _fixture()
    try:
        result = VendorBillReleaseOrchestrator.authorize(_command(bill), db)
        assert result.outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED
        assert db["vendor_bill_release_authorizations"].count_documents({"tenant_id":"t","payable_id":"p"}) == 1
        assert VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor("t", "p", db["vendor_bill_release_authorizations"]) == 100
        assert VendorBillRegistry.get("t", "p", db["vendor_bills"]).release_authority_guard_revision == 1
    finally: client.drop_database(db.name); client.close()


def test_vendor_bill_release_orchestrator_exact_replay_real_mongo():
    client, db, bill = _fixture()
    try:
        command = _command(bill); first = VendorBillReleaseOrchestrator.authorize(command, db); second = VendorBillReleaseOrchestrator.authorize(command, db)
        assert first.outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED and second.outcome is VendorBillReleaseOrchestrationOutcome.IDEMPOTENT_REPLAY
        assert db["vendor_bill_release_authorizations"].count_documents({"tenant_id":"t","payable_id":"p"}) == 1
        assert VendorBillRegistry.get("t", "p", db["vendor_bills"]).release_authority_guard_revision == 1
    finally: client.drop_database(db.name); client.close()


@pytest.mark.parametrize("field,value", [("release_authorization_id","other"),("requested_amount_minor",101),("currency","USD"),("authorized_by_actor_id","other"),("authorization_basis_reference","other"),("authorized_at",datetime(2026,1,3,tzinfo=timezone.utc))])
def test_vendor_bill_release_orchestrator_divergent_same_key_fails_closed_real_mongo(field, value):
    client, db, bill = _fixture()
    try:
        command = _command(bill); VendorBillReleaseOrchestrator.authorize(command, db)
        with pytest.raises(VendorBillReleaseOrchestrationIdempotencyError, match="VENDOR_BILL_RELEASE_AUTHORIZATION_IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_COMMAND"):
            VendorBillReleaseOrchestrator.authorize(replace(command, **{field:value}), db)
        assert db["vendor_bill_release_authorizations"].count_documents({"tenant_id":"t","payable_id":"p"}) == 1
    finally: client.drop_database(db.name); client.close()


def test_vendor_bill_release_orchestrator_cumulative_partial_reservations_real_mongo():
    client, db, bill = _fixture()
    try:
        assert VendorBillReleaseOrchestrator.authorize(_command(bill,"a",400), db).outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED
        assert VendorBillReleaseOrchestrator.authorize(_command(bill,"b",350), db).outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED
        assert VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor("t","p",db["vendor_bill_release_authorizations"]) == 750
    finally: client.drop_database(db.name); client.close()


def test_vendor_bill_release_orchestrator_over_reservation_denied_real_mongo():
    client, db, bill = _fixture()
    try:
        VendorBillReleaseOrchestrator.authorize(_command(bill,"a",900), db)
        with pytest.raises(Exception, match="CUMULATIVE_AUTHORITY_EXCEEDED"):
            VendorBillReleaseOrchestrator.authorize(_command(bill,"b",200), db)
        assert db["vendor_bill_release_authorizations"].count_documents({"tenant_id":"t","payable_id":"p"}) == 1
        assert VendorBillRegistry.get("t","p",db["vendor_bills"]).release_authority_guard_revision == 1
    finally: client.drop_database(db.name); client.close()


def test_vendor_bill_release_orchestrator_transaction_abort_is_atomic_real_mongo():
    client, db, bill = _fixture()
    try:
        command = _command(bill)
        with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.create", side_effect=RuntimeError("injected abort")):
            with pytest.raises(RuntimeError, match="injected abort"):
                VendorBillReleaseOrchestrator.authorize(command, db, max_attempts=1)
        fresh = VendorBillRegistry.get("t","p",db["vendor_bills"])
        assert fresh.release_authority_guard_revision == 0
        assert db["vendor_bill_release_authorizations"].count_documents({"tenant_id":"t","payable_id":"p"}) == 0
    finally: client.drop_database(db.name); client.close()


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_vendor_bill_release_orchestrator_mongo.py
# VERSION: v1.0.0-VENDOR-BILL-RELEASE-ORCHESTRATOR-MONGO-CERT
# AUTHORITY: Wilsy OS Core Governance
# END OF WILSY OS SOVEREIGN ARTIFACT
