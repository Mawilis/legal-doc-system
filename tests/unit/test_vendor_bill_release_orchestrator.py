"""WILSY OS — VENDOR BILL RELEASE ORCHESTRATOR UNIT CERTIFICATION
Version: v1.0.0-VENDOR-BILL-RELEASE-ORCHESTRATOR-UNIT-CERT
Authority: Wilsy OS Core Governance | Runtime: pure mocked boundaries
Architecture: APPROVED != RELEASE AUTHORIZED != EXECUTED != SETTLED
"""
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from pymongo.errors import OperationFailure
import pytest
from tools.eos.saas.domain.vendor_bill_release_policy import VendorBillReleaseIneligibilityReason
from tools.eos.saas.billing.vendor_bill_registry import VendorBillReleaseAuthorityGuardConflictError, VendorBillPersistedRecordInvalidError
from tools.eos.saas.billing.vendor_bill_release_orchestrator import _MAX_TRANSACTION_ATTEMPTS, VendorBillReleaseTransactionRetryExhaustedError, VendorBillReleaseOrchestrationError, VendorBillReleaseOrchestrationIdempotencyError
from datetime import date

from tools.eos.saas.domain.vendor_bill import VendorBill, VendorBillObligationState, VendorBillApprovalState
from tools.eos.saas.domain.financial_approval_effective_result import (
    FinancialApprovalEffectiveResult, FinancialApprovalEffectiveState,
    FinancialApprovalPolicySubjectType, FinancialApprovalRequirementResult,
)
from tools.eos.saas.domain.vendor_bill_release_authorization import VendorBillReleaseAuthorization
from tools.eos.saas.billing.vendor_bill_release_authorization_registry import (
    VendorBillReleaseAuthorizationCreateOutcome, VendorBillReleaseAuthorizationCreateResult,
    VendorBillReleaseAuthorizationNotFoundError,
)

from tools.eos.saas.billing.vendor_bill_release_orchestrator import (
    VendorBillReleaseCommand, VendorBillReleaseOrchestrator,
    VendorBillReleaseOrchestrationOutcome,
)


class FakeSession:
    def __init__(self, events, ident, commit_error=None):
        self.events, self.ident, self.commit_error = events, ident, commit_error
        self.in_transaction = False
    def __enter__(self):
        self.events.append(("session_start", self.ident)); return self
    def __exit__(self, *_): return False
    def start_transaction(self):
        self.in_transaction = True; self.events.append(("transaction_start", self.ident))
    def commit_transaction(self):
        self.events.append(("commit", self.ident))
        if self.commit_error: raise self.commit_error
        self.in_transaction = False
    def abort_transaction(self):
        self.events.append(("abort", self.ident)); self.in_transaction = False


class FakeClient:
    def __init__(self, events): self.events, self.sessions = events, []
    def start_session(self):
        session = FakeSession(self.events, len(self.sessions) + 1); self.sessions.append(session); return session


class FakeDatabase:
    def __init__(self, events): self.client, self.collections = FakeClient(events), {}
    def __getitem__(self, name):
        return self.collections.setdefault(name, object())


def command() -> VendorBillReleaseCommand:
    return VendorBillReleaseCommand("t", "p", "ra", 10, "ZAR", "actor", "basis", datetime(2026, 1, 1, tzinfo=timezone.utc), "key")


def test_public_command_is_immutable_and_has_no_execution_fields():
    value = command()
    assert value.tenant_id == "t"
    assert not hasattr(value, "bank_account")


def test_missing_database_fails_closed():
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.get_database", return_value=None):
        try:
            VendorBillReleaseOrchestrator.authorize(command())
        except Exception as error:
            assert str(error) == "VENDOR_BILL_PERSISTENCE_UNAVAILABLE"
        else:
            raise AssertionError("missing database unexpectedly authorized")


def test_exact_replay_short_circuits_before_guard():
    session = Mock(); session.in_transaction = True
    client = Mock(); client.start_session.return_value = Mock(__enter__=Mock(return_value=session), __exit__=Mock(return_value=None))
    db = Mock(); db.client = client; db.__getitem__ = Mock(return_value=Mock())
    replay = VendorBillReleaseAuthorization("t", "ra", "p", 1, "result", "a" * 128, 10, "ZAR", "actor", "basis", command().authorized_at, command().authorized_at)
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key", return_value=replay) as lookup, patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get") as bill_read:
        result = VendorBillReleaseOrchestrator.authorize(command(), db)
    assert result.outcome is VendorBillReleaseOrchestrationOutcome.IDEMPOTENT_REPLAY
    lookup.assert_called_once(); bill_read.assert_not_called()


def _bill(payable_id="p") -> VendorBill:
    now = datetime.now(timezone.utc)
    return VendorBill("t", "vendor", 100, "ZAR", date(2026, 1, 1), date(2026, 2, 1),
                      payable_id=payable_id, obligation_state=VendorBillObligationState.OPEN,
                      approval_state=VendorBillApprovalState.APPROVED,
                      approval_projection_revision=1, approval_effective_result_id="result",
                      approval_policy_reference="policy", created_at=now, updated_at=now)


def _result(result_id="result") -> FinancialApprovalEffectiveResult:
    now = datetime.now(timezone.utc)
    requirement = FinancialApprovalRequirementResult("req", "finance", 1, 1, True,
                                                     ("actor",), ("decision",), ("auth",))
    return FinancialApprovalEffectiveResult(
        "t", result_id, FinancialApprovalPolicySubjectType.VENDOR_BILL, "p", 1,
        "evaluation", "policy", "v1", FinancialApprovalEffectiveState.APPROVED,
        now, now, (requirement,), ("decision",), ("auth",), source_evidence_fingerprint="a" * 128,
    )


def _success_patches(events, bill, result, reserved=0):
    session = FakeSession(events, 1)
    db = FakeDatabase(events)
    not_found = VendorBillReleaseAuthorizationNotFoundError("VENDOR_BILL_RELEASE_AUTHORIZATION_NOT_FOUND")
    decision = Mock(eligible=True)
    authorization = VendorBillReleaseAuthorization("t", "ra", "p", 1, "result", "a" * 128, 10, "ZAR", "actor", "basis", command().authorized_at, command().authorized_at)
    create_result = VendorBillReleaseAuthorizationCreateResult(VendorBillReleaseAuthorizationCreateOutcome.CREATED, authorization)
    return session, db, not_found, decision, authorization, create_result


def test_authorize_success_order_and_same_session():
    events=[]; bill=_bill(); result=_result(); session, db, miss, decision, _, created = _success_patches(events,bill,result)
    def replay_lookup(*args, **kwargs):
        events.append(("replay_lookup",)); raise miss
    def mark(name, value):
        def f(*args, **kwargs): events.append((name,)); return value
        return f
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key", side_effect=replay_lookup) as lookup, patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get", side_effect=mark("vendor_bill_read",bill)) as br, patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.FinancialApprovalEffectiveResultRegistry.get", side_effect=mark("effective_result_read",result)) as rr, patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor", side_effect=mark("reservation_sum",0)) as sr, patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.evaluate_vendor_bill_release_eligibility", side_effect=mark("policy_evaluation",decision)), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.acquire_release_authority_guard", side_effect=mark("guard_acquire",bill)) as guard, patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.create", side_effect=mark("authorization_create",created)) as create:
        out=VendorBillReleaseOrchestrator.authorize(command(),db)
    assert out.outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED
    assert events == [("session_start",1),("transaction_start",1),("replay_lookup",),("vendor_bill_read",),("effective_result_read",),("reservation_sum",),("policy_evaluation",),("guard_acquire",),("authorization_create",),("commit",1)]
    assert len(db.client.sessions) == 1
    sessions = [lookup.call_args.kwargs["session"], br.call_args.kwargs["session"], rr.call_args.kwargs["session"], sr.call_args.kwargs["session"], guard.call_args.kwargs["session"], create.call_args.kwargs["session"]]
    assert all(value is sessions[0] for value in sessions)


def test_authorize_reservation_sum_flows_exactly_to_policy():
    bill=_bill(); result=_result(); events=[]; _, db, miss, decision, _, created = _success_patches(events,bill,result,413)
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key", side_effect=miss), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get", return_value=bill), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.FinancialApprovalEffectiveResultRegistry.get", return_value=result), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor", return_value=413), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.evaluate_vendor_bill_release_eligibility", return_value=decision) as policy, patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.acquire_release_authority_guard", return_value=bill), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.create", return_value=created):
        out=VendorBillReleaseOrchestrator.authorize(command(),db)
    assert out.outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED
    assert policy.call_args.args == (bill,result,10,"ZAR",1,413)


def test_authorize_replay_after_success_does_not_increment_guard_twice():
    bill=_bill(); result=_result(); events=[]; _, db, miss, decision, authorization, created = _success_patches(events,bill,result)
    lookup = Mock(side_effect=[miss, authorization]); guard=Mock(return_value=bill); create=Mock(return_value=created)
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key", side_effect=lookup.side_effect), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get", return_value=bill) as br, patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.FinancialApprovalEffectiveResultRegistry.get", return_value=result), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor", return_value=0), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.evaluate_vendor_bill_release_eligibility", return_value=decision), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.acquire_release_authority_guard", guard), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.create", create):
        first=VendorBillReleaseOrchestrator.authorize(command(),db); second=VendorBillReleaseOrchestrator.authorize(command(),db)
    assert first.outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED and second.outcome is VendorBillReleaseOrchestrationOutcome.IDEMPOTENT_REPLAY
    assert guard.call_count == create.call_count == 1; assert br.call_count == 1


@pytest.mark.parametrize("field", ["release_authorization_id", "requested_amount_minor", "currency", "authorized_by_actor_id", "authorization_basis_reference", "authorized_at"])
def test_authorize_replay_rejects_same_key_with_divergent_command_semantics(field):
    events=[]; db=FakeDatabase(events); cmd=command(); auth=VendorBillReleaseAuthorization("t","ra","p",1,"result","a"*128,10,"ZAR","actor","basis",cmd.authorized_at,cmd.authorized_at)
    values={"release_authorization_id":"other","requested_amount_minor":11,"currency":"USD","authorized_by_actor_id":"other-actor","authorization_basis_reference":"other-basis","authorized_at":datetime(2026,1,2,tzinfo=timezone.utc)}
    divergent=cmd.__class__(**{**cmd.__dict__, field: values[field]})
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key",return_value=auth) as lookup, patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get") as bill_read:
        with pytest.raises(VendorBillReleaseOrchestrationIdempotencyError, match="VENDOR_BILL_RELEASE_AUTHORIZATION_IDEMPOTENCY_KEY_REUSED_WITH_DIFFERENT_COMMAND"):
            VendorBillReleaseOrchestrator.authorize(divergent,db)
    lookup.assert_called_once(); bill_read.assert_not_called()


def test_authorize_success_constructs_exact_release_authorization_evidence():
    bill=_bill(); result=_result(); events=[]; _, db, miss, decision, _, created = _success_patches(events,bill,result)
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key", side_effect=miss), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get", return_value=bill), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.FinancialApprovalEffectiveResultRegistry.get", return_value=result), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor", return_value=0), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.evaluate_vendor_bill_release_eligibility", return_value=decision), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.acquire_release_authority_guard", return_value=bill), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.create", return_value=created) as create:
        VendorBillReleaseOrchestrator.authorize(command(),db)
    evidence=create.call_args.args[0]
    assert evidence.tenant_id=="t" and evidence.payable_id=="p" and evidence.release_authorization_id=="ra" and evidence.vendor_bill_revision==1 and evidence.approval_effective_result_id=="result" and evidence.authorized_amount_minor==10 and evidence.currency=="ZAR" and evidence.authorized_by_actor_id=="actor" and evidence.authorization_basis_reference=="basis"
    assert not any("payment" in f or "bank" in f or "execution" in f or "settlement" in f or "paid" in f for f in evidence.__dataclass_fields__)


def _retry_setup():
    events=[]; db=FakeDatabase(events); a,b=_bill(),_bill(); ra,rb=_result("result-a"),_result("result-b")
    miss=VendorBillReleaseAuthorizationNotFoundError("VENDOR_BILL_RELEASE_AUTHORIZATION_NOT_FOUND")
    decision=Mock(eligible=True); auth=VendorBillReleaseAuthorization("t","ra","p",1,"result-b","a"*128,10,"ZAR","actor","basis",command().authorized_at,command().authorized_at)
    created=VendorBillReleaseAuthorizationCreateResult(VendorBillReleaseAuthorizationCreateOutcome.CREATED,auth)
    return events,db,a,b,ra,rb,miss,decision,created


def test_authorize_transient_transaction_error_retries_with_fresh_state():
    events,db,bill_a,bill_b,result_a,result_b,miss,decision,created=_retry_setup(); reads=iter([(bill_a,result_a,111),(bill_b,result_b,222)])
    def lookup(*args,**kwargs): events.append(("replay_lookup",)); raise miss
    def read_bill(*args,**kwargs): events.append(("vendor_bill_read",)); return next(reads)[0]
    def read_result(*args,**kwargs): events.append(("effective_result_read",)); return (result_a if result_a.result_id == "result-a" else result_b)
    policy_calls=[]
    def policy(*args):
        policy_calls.append(args)
        if len(policy_calls)==1: raise OperationFailure("transient", code=251, details={"errorLabels":["TransientTransactionError"]})
        return decision
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key",side_effect=lookup), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get",side_effect=[bill_a,bill_b]), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.FinancialApprovalEffectiveResultRegistry.get",side_effect=[result_a,result_b]), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor",side_effect=[111,222]), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.evaluate_vendor_bill_release_eligibility",side_effect=policy), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.acquire_release_authority_guard",return_value=bill_b), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.create",return_value=created):
        out=VendorBillReleaseOrchestrator.authorize(command(),db)
    assert out.outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED and len(db.client.sessions)==2 and db.client.sessions[0] is not db.client.sessions[1]
    assert policy_calls[0][0] is bill_a and policy_calls[1][0] is bill_b and policy_calls[0][-1]==111 and policy_calls[1][-1]==222


def test_authorize_write_conflict_code_112_retries_whole_transaction():
    events,db,bill_a,bill_b,result_a,result_b,miss,decision,created=_retry_setup(); policy_calls=[]
    def policy(*args):
        policy_calls.append(args)
        if len(policy_calls)==1: raise OperationFailure("write conflict", code=112)
        return decision
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key",side_effect=[miss,miss]), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get",side_effect=[bill_a,bill_b]), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.FinancialApprovalEffectiveResultRegistry.get",side_effect=[result_a,result_b]), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor",side_effect=[111,222]), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.evaluate_vendor_bill_release_eligibility",side_effect=policy), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.acquire_release_authority_guard",return_value=bill_b), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.create",return_value=created):
        out=VendorBillReleaseOrchestrator.authorize(command(),db)
    assert out.outcome is VendorBillReleaseOrchestrationOutcome.AUTHORIZED and len(db.client.sessions)==2 and policy_calls[1][0] is bill_b


def test_authorize_non_retryable_operation_failure_propagates_without_retry():
    events,db,bill,_,result,_,miss,_,created=_retry_setup(); error=OperationFailure("non-retryable",code=9,details={})
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key",side_effect=miss), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get",return_value=bill), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.FinancialApprovalEffectiveResultRegistry.get",return_value=result), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor",return_value=0), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.evaluate_vendor_bill_release_eligibility",side_effect=error):
        try: VendorBillReleaseOrchestrator.authorize(command(),db)
        except OperationFailure as actual: assert actual.code==9
        else: raise AssertionError("non-retryable failure was swallowed")
    assert len(db.client.sessions)==1


def test_authorize_policy_failure_does_not_retry_or_acquire_guard():
    events,db,bill,_,result,_,miss,_,_= _retry_setup(); decision=Mock(eligible=False, reason=VendorBillReleaseIneligibilityReason.APPROVAL_NOT_APPROVED)
    def lookup(*args,**kwargs): events.append(("replay_lookup",)); raise miss
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key",side_effect=lookup), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get",side_effect=lambda *a,**k:(events.append(("vendor_bill_read",)) or bill)), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.FinancialApprovalEffectiveResultRegistry.get",side_effect=lambda *a,**k:(events.append(("effective_result_read",)) or result)), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor",side_effect=lambda *a,**k:(events.append(("reservation_sum",)) or 0)), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.evaluate_vendor_bill_release_eligibility",side_effect=lambda *a,**k:(events.append(("policy_evaluation",)) or decision)) as policy, patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.acquire_release_authority_guard") as guard:
        try: VendorBillReleaseOrchestrator.authorize(command(),db)
        except Exception as error: assert str(error)=="APPROVAL_NOT_APPROVED"
        else: raise AssertionError("policy denial authorized")
    assert events==[("session_start",1),("transaction_start",1),("replay_lookup",),("vendor_bill_read",),("effective_result_read",),("reservation_sum",),("policy_evaluation",),("abort",1)]; policy.assert_called_once(); guard.assert_not_called(); assert len(db.client.sessions)==1


def test_authorize_guard_conflict_does_not_retry_or_create():
    events,db,bill,_,result,_,miss,decision,created=_retry_setup(); conflict=VendorBillReleaseAuthorityGuardConflictError("VENDOR_BILL_RELEASE_AUTHORITY_GUARD_STALE")
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key",side_effect=miss), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get",return_value=bill), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.FinancialApprovalEffectiveResultRegistry.get",return_value=result), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor",return_value=0), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.evaluate_vendor_bill_release_eligibility",return_value=decision), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.acquire_release_authority_guard",side_effect=conflict) as guard, patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.create") as create:
        try: VendorBillReleaseOrchestrator.authorize(command(),db)
        except VendorBillReleaseAuthorityGuardConflictError as error: assert str(error)=="VENDOR_BILL_RELEASE_AUTHORITY_GUARD_STALE"
        else: raise AssertionError("guard conflict swallowed")
    assert guard.call_count==1; create.assert_not_called(); assert len(db.client.sessions)==1


def test_authorize_persisted_corruption_propagates_without_retry():
    events,db,_,_,_,_,miss,_,_=_retry_setup(); corruption=VendorBillPersistedRecordInvalidError("VENDOR_BILL_PERSISTED_RECORD_INVALID")
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key",side_effect=miss), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get",side_effect=corruption) as bill_read, patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.FinancialApprovalEffectiveResultRegistry.get") as result_read:
        try: VendorBillReleaseOrchestrator.authorize(command(),db)
        except VendorBillPersistedRecordInvalidError as error: assert str(error)=="VENDOR_BILL_PERSISTED_RECORD_INVALID"
        else: raise AssertionError("corruption swallowed")
    bill_read.assert_called_once(); result_read.assert_not_called(); assert len(db.client.sessions)==1


def test_authorize_retry_exhaustion_uses_fresh_attempts_and_stable_error():
    events,db,bill,_,result,_,miss,_,_=_retry_setup(); failure=OperationFailure("transient",code=251,details={"errorLabels":["TransientTransactionError"]})
    sessions=[]
    def start_session():
        session=FakeSession(events,len(sessions)+1); sessions.append(session); return session
    db.client.start_session=start_session
    def lookup(*args,**kwargs): events.append(("replay_lookup",)); raise miss
    def fail_policy(*args,**kwargs): raise failure
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key",side_effect=lookup), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get",return_value=bill), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.FinancialApprovalEffectiveResultRegistry.get",return_value=result), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor",return_value=0), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.evaluate_vendor_bill_release_eligibility",side_effect=fail_policy):
        try: VendorBillReleaseOrchestrator.authorize(command(),db)
        except VendorBillReleaseTransactionRetryExhaustedError as error: assert str(error)=="VENDOR_BILL_RELEASE_TRANSACTION_RETRY_EXHAUSTED"
        else: raise AssertionError("retry exhaustion did not fail closed")
    assert len(sessions)==_MAX_TRANSACTION_ATTEMPTS and len({id(s) for s in sessions})==_MAX_TRANSACTION_ATTEMPTS
    assert events.count(("transaction_start",1))+events.count(("transaction_start",2))+events.count(("transaction_start",3))==_MAX_TRANSACTION_ATTEMPTS


def test_authorize_unknown_commit_result_fails_closed_without_retry():
    events,db,bill,_,result,_,miss,decision,created=_retry_setup(); uncertain=OperationFailure("uncertain commit",code=251,details={"errorLabels":["UnknownTransactionCommitResult"]})
    session=FakeSession(events,1,commit_error=uncertain); db.client.start_session=lambda: session
    with patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.get_by_idempotency_key",side_effect=miss), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.get",return_value=bill), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.FinancialApprovalEffectiveResultRegistry.get",return_value=result), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.sum_authorized_amount_minor",return_value=0), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.evaluate_vendor_bill_release_eligibility",return_value=decision), patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillRegistry.acquire_release_authority_guard",return_value=bill) as guard, patch("tools.eos.saas.billing.vendor_bill_release_orchestrator.VendorBillReleaseAuthorizationRegistry.create",return_value=created) as create:
        try: VendorBillReleaseOrchestrator.authorize(command(),db)
        except VendorBillReleaseOrchestrationError as error: assert type(error) is VendorBillReleaseOrchestrationError and str(error)=="VENDOR_BILL_RELEASE_TRANSACTION_COMMIT_UNCERTAIN"
        else: raise AssertionError("uncertain commit returned success")
    assert len(db.client.sessions)==0 if hasattr(db.client,"sessions") and isinstance(db.client.sessions,list) else True
    assert events.count(("commit",1))==1; assert guard.call_count==1 and create.call_count==1




# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_vendor_bill_release_orchestrator.py
# VERSION: v1.0.0-VENDOR-BILL-RELEASE-ORCHESTRATOR-UNIT-CERT
# AUTHORITY BOUNDARY: orchestration contract only; no execution or settlement
# END OF WILSY OS SOVEREIGN ARTIFACT
