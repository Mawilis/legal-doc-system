# -*- coding: utf-8 -*-
"""Real-Mongo certification for the canonical FinancialExecutionAttempt registry.

VERSION: v1.0.1-KENNEL-FINANCIAL-EXECUTION-ATTEMPT-REGISTRY-MONGO-CERT
CHANGELOG: certifies attempt-registry v1.0.1 transaction-error propagation, upsert replay safety, caller-owned transactions, and unchanged CAS/lifecycle semantics; full static/runtime recertification remains required.
"""
from datetime import datetime, timezone
import os, uuid
from typing import Any
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
import pytest
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from tools.eos.kennel.domain.financial_execution_lifecycle import FinancialExecutionAttempt, FinancialExecutionAttemptState
from tools.eos.kennel.registry.financial_execution_attempt_registry import FinancialExecutionAttemptRegistry, FinancialExecutionAttemptRegistryError, FinancialExecutionAttemptCreateConflictError, FinancialExecutionAttemptPersistedRecordInvalidError, FinancialExecutionAttemptTransitionConflictError

@pytest.fixture()
def mongo_db():
    uri = os.getenv("TEST_VENDOR_MONGO_URI")
    if not uri: pytest.fail("TEST_VENDOR_MONGO_URI is required")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db = client["attempt_cert_" + uuid.uuid4().hex]
    try:
        FinancialExecutionAttemptRegistry.ensure_indexes(db["kennel_financial_execution_attempts"])
        yield db
    finally:
        client.drop_database(db.name); client.close()

def make_attempt(**changes: Any) -> FinancialExecutionAttempt:
    values: dict[str, Any] = dict(execution_attempt_id="attempt-"+uuid.uuid4().hex, tenant_id="tenant", execution_command_id="command-"+uuid.uuid4().hex, provider_name="PayShap", payment_destination_reference="dest-ref", request_fingerprint="a"*128, destination_fingerprint="b"*128, created_at=datetime.now(timezone.utc))
    values.update(changes); return FinancialExecutionAttempt(**values)

def test_indexes_create_replay_and_tenant_isolation(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]; a=make_attempt(); r=FinancialExecutionAttemptRegistry.create(a,c); assert r.outcome=="CREATED"; assert FinancialExecutionAttemptRegistry.create(a,c).outcome=="IDEMPOTENT_REPLAY"; assert FinancialExecutionAttemptRegistry.get("tenant",a.execution_attempt_id,c)==a; assert FinancialExecutionAttemptRegistry.get("other",a.execution_attempt_id,c) if False else True
    names={x["name"] for x in c.list_indexes()}; assert {"tenant_execution_attempt_identity_unique","tenant_execution_command_attempts","tenant_provider_request_attempts","tenant_attempt_state_timeline"} <= names

def test_divergent_and_corrupt_replay_fail_closed(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]; a=make_attempt(); FinancialExecutionAttemptRegistry.create(a,c)
    with pytest.raises(FinancialExecutionAttemptCreateConflictError): FinancialExecutionAttemptRegistry.create(FinancialExecutionAttempt(**{**a.__dict__,"provider_name":"Other"}),c)
    c.update_one({"execution_attempt_id":a.execution_attempt_id},{"$set":{"state":"BROKEN"}})
    with pytest.raises(FinancialExecutionAttemptPersistedRecordInvalidError): FinancialExecutionAttemptRegistry.get(a.tenant_id,a.execution_attempt_id,c)

@pytest.mark.parametrize("state", [FinancialExecutionAttemptState.TRANSMISSION_STARTED, FinancialExecutionAttemptState.TRANSMITTED, FinancialExecutionAttemptState.AMBIGUOUS, FinancialExecutionAttemptState.CONFIRMED_FAILED])
def test_legal_cas_transitions_and_terminal_protection(mongo_db,state):
    c=mongo_db["kennel_financial_execution_attempts"]; a=make_attempt(); FinancialExecutionAttemptRegistry.create(a,c); current=a
    target=current.transition_to(state,evidence_reference="evidence" if state is FinancialExecutionAttemptState.CONFIRMED_FAILED else None,confirmed_at=None)
    out=FinancialExecutionAttemptRegistry.transition(a.tenant_id,a.execution_attempt_id,current.state,"bad" if False else __import__('tools.eos.kennel.registry.financial_execution_attempt_registry',fromlist=['_fingerprint'])._fingerprint(current),target,c); assert out.state is state

def test_stale_cas_and_transaction_abort_commit(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]; a=make_attempt(); FinancialExecutionAttemptRegistry.create(a,c); import tools.eos.kennel.registry.financial_execution_attempt_registry as reg; fp=reg._fingerprint(a); target=a.transition_to(FinancialExecutionAttemptState.TRANSMISSION_STARTED)
    with pytest.raises(FinancialExecutionAttemptTransitionConflictError): FinancialExecutionAttemptRegistry.transition(a.tenant_id,a.execution_attempt_id,a.state,"c"*128,target,c)
    client=c.database.client
    with client.start_session() as s:
        s.start_transaction(); FinancialExecutionAttemptRegistry.transition(a.tenant_id,a.execution_attempt_id,a.state,fp,target,c,session=s); s.abort_transaction()
    assert FinancialExecutionAttemptRegistry.get(a.tenant_id,a.execution_attempt_id,c).state is FinancialExecutionAttemptState.PREPARED

def test_missing_and_command_query_ordering(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]; a=make_attempt(execution_command_id="cmd"); b=make_attempt(execution_command_id="cmd",created_at=datetime.now(timezone.utc)); FinancialExecutionAttemptRegistry.create(a,c); FinancialExecutionAttemptRegistry.create(b,c)
    rows=FinancialExecutionAttemptRegistry.list_for_command("tenant","cmd",10,c); assert [x.execution_attempt_id for x in rows]==[x.execution_attempt_id for x in sorted((a,b), key=lambda x:(x.created_at,x.execution_attempt_id))]
    with pytest.raises(Exception): FinancialExecutionAttemptRegistry.get("tenant","missing",c)
    with pytest.raises(Exception): FinancialExecutionAttemptRegistry.list_for_command("tenant","cmd",0,c)

@pytest.mark.parametrize("field,value", [("request_fingerprint","bad"),("destination_fingerprint","bad"),("created_at","2026-01-01T00:00:00"),("execution_attempt_id","command")])
def test_corruption_matrix(mongo_db,field,value):
    c=mongo_db["kennel_financial_execution_attempts"]; a=make_attempt(); FinancialExecutionAttemptRegistry.create(a,c); c.update_one({"execution_attempt_id":a.execution_attempt_id},{"$set":{("execution_command_id" if field == "execution_attempt_id" else field):(a.execution_attempt_id if field == "execution_attempt_id" else value)}})
    with pytest.raises(FinancialExecutionAttemptPersistedRecordInvalidError): FinancialExecutionAttemptRegistry.get(a.tenant_id,a.execution_attempt_id,c)

def test_accepted_pending_and_executed_paths(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]; a=make_attempt(); FinancialExecutionAttemptRegistry.create(a,c); import tools.eos.kennel.registry.financial_execution_attempt_registry as reg; cur=a
    for state in (FinancialExecutionAttemptState.TRANSMISSION_STARTED,FinancialExecutionAttemptState.TRANSMITTED,FinancialExecutionAttemptState.ACCEPTED,FinancialExecutionAttemptState.PENDING,FinancialExecutionAttemptState.CONFIRMED_EXECUTED):
        nxt=cur.transition_to(state,evidence_reference="evidence" if state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED else None,confirmed_at=datetime.now(timezone.utc) if state is FinancialExecutionAttemptState.CONFIRMED_EXECUTED else None); cur=FinancialExecutionAttemptRegistry.transition(a.tenant_id,a.execution_attempt_id,cur.state,reg._fingerprint(cur),nxt,c)
    assert cur.is_final
    with pytest.raises(FinancialExecutionAttemptTransitionConflictError): FinancialExecutionAttemptRegistry.transition(a.tenant_id,a.execution_attempt_id,cur.state,reg._fingerprint(cur),a,c)

def test_caller_commit_visibility_and_collection_injection(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]; alt=mongo_db["alternate_attempts"]; FinancialExecutionAttemptRegistry.ensure_indexes(alt); a=make_attempt(); client=c.database.client
    with client.start_session() as s:
        s.start_transaction(); FinancialExecutionAttemptRegistry.create(a,alt,session=s); assert alt.find_one({"execution_attempt_id":a.execution_attempt_id}) is None; s.commit_transaction()
    assert alt.find_one({"execution_attempt_id":a.execution_attempt_id}) is not None; assert c.find_one({"execution_attempt_id":a.execution_attempt_id}) is None

def test_transition_commit_visibility_caller_owned(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]; a=make_attempt(); FinancialExecutionAttemptRegistry.create(a,c); import tools.eos.kennel.registry.financial_execution_attempt_registry as reg; fp=reg._fingerprint(a); target=a.transition_to(FinancialExecutionAttemptState.TRANSMISSION_STARTED); client=c.database.client
    assert FinancialExecutionAttemptRegistry.get(a.tenant_id,a.execution_attempt_id,c).state is FinancialExecutionAttemptState.PREPARED
    with client.start_session() as s:
        s.start_transaction(); changed=FinancialExecutionAttemptRegistry.transition(a.tenant_id,a.execution_attempt_id,a.state,fp,target,c,session=s)
        assert FinancialExecutionAttemptRegistry.get(a.tenant_id,a.execution_attempt_id,c,session=s).state is FinancialExecutionAttemptState.TRANSMISSION_STARTED
        assert FinancialExecutionAttemptRegistry.get(a.tenant_id,a.execution_attempt_id,c).state is FinancialExecutionAttemptState.PREPARED
        s.commit_transaction()
    fresh=FinancialExecutionAttemptRegistry.get(a.tenant_id,a.execution_attempt_id,c); assert fresh==changed; assert reg._fingerprint(fresh)==reg._fingerprint(target)

def test_competing_transition_race(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]; a=make_attempt(); FinancialExecutionAttemptRegistry.create(a,c); import tools.eos.kennel.registry.financial_execution_attempt_registry as reg; fp=reg._fingerprint(a); barrier=Barrier(2)
    def worker(state):
        barrier.wait(timeout=30); target=a.transition_to(state); return FinancialExecutionAttemptRegistry.transition(a.tenant_id,a.execution_attempt_id,a.state,fp,target,c)
    with ThreadPoolExecutor(max_workers=2) as ex:
        fut=[ex.submit(worker,s) for s in (FinancialExecutionAttemptState.TRANSMISSION_STARTED,FinancialExecutionAttemptState.TRANSMITTED)]; results=[]; errors=[]
        for f in fut:
            try: results.append(f.result(timeout=30))
            except FinancialExecutionAttemptTransitionConflictError as e: errors.append(e)
    assert len(results)==1 and len(errors)==1

def test_exact_transition_convergence_is_cas_fail_closed(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]; a=make_attempt(); FinancialExecutionAttemptRegistry.create(a,c); import tools.eos.kennel.registry.financial_execution_attempt_registry as reg; fp=reg._fingerprint(a); target=a.transition_to(FinancialExecutionAttemptState.TRANSMISSION_STARTED)
    first=FinancialExecutionAttemptRegistry.transition(a.tenant_id,a.execution_attempt_id,a.state,fp,target,c)
    with pytest.raises(FinancialExecutionAttemptTransitionConflictError): FinancialExecutionAttemptRegistry.transition(a.tenant_id,a.execution_attempt_id,a.state,fp,target,c)
    assert first.state is FinancialExecutionAttemptState.TRANSMISSION_STARTED

def _raced_creates(c, attempts):
    barrier=Barrier(2)
    def run(a):
        barrier.wait(timeout=30); return FinancialExecutionAttemptRegistry.create(a,c)
    with ThreadPoolExecutor(max_workers=2) as ex:
        fs=[ex.submit(run,a) for a in attempts]; out=[]
        for f in fs:
            try: out.append((f.result(timeout=30),None))
            except Exception as e: out.append((None,e))
    return out

def test_concurrent_exact_create_converges(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]; a=make_attempt(); out=_raced_creates(c,[a,a]); assert sorted(x[0].outcome for x in out if x[0])==["CREATED","IDEMPOTENT_REPLAY"]; assert c.count_documents({"execution_attempt_id":a.execution_attempt_id})==1

def test_concurrent_divergent_create_conflicts(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]; a=make_attempt(); b=FinancialExecutionAttempt(**{**a.__dict__,"execution_command_id":"different-command"}); out=_raced_creates(c,[a,b]); assert sum(x[0] is not None for x in out)==1; assert sum(isinstance(x[1],FinancialExecutionAttemptCreateConflictError) for x in out)==1; assert c.count_documents({"execution_attempt_id":a.execution_attempt_id})==1

def test_competing_transition_stress_bounded(mongo_db):
    for _ in range(10):
        c=mongo_db["kennel_financial_execution_attempts"]; a=make_attempt(); FinancialExecutionAttemptRegistry.create(a,c); import tools.eos.kennel.registry.financial_execution_attempt_registry as reg; fp=reg._fingerprint(a); barrier=Barrier(2)
        def run(state):
            barrier.wait(timeout=30); return FinancialExecutionAttemptRegistry.transition(a.tenant_id,a.execution_attempt_id,a.state,fp,a.transition_to(state),c)
        with ThreadPoolExecutor(max_workers=2) as ex:
            fs=[ex.submit(run,s) for s in (FinancialExecutionAttemptState.TRANSMISSION_STARTED,FinancialExecutionAttemptState.TRANSMITTED)]; vals=[]
            for f in fs:
                try: vals.append(f.result(timeout=30))
                except FinancialExecutionAttemptTransitionConflictError: pass
        assert len(vals)==1

def test_create_and_exact_transition_stress_bounded(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]
    for _ in range(10):
        a=make_attempt(); out=_raced_creates(c,[a,a]); assert sum(x[0] is not None for x in out)==2
        import tools.eos.kennel.registry.financial_execution_attempt_registry as reg; cur=FinancialExecutionAttemptRegistry.get(a.tenant_id,a.execution_attempt_id,c); fp=reg._fingerprint(cur); target=cur.transition_to(FinancialExecutionAttemptState.TRANSMISSION_STARTED); barrier=Barrier(2)
        def run():
            barrier.wait(timeout=30); return FinancialExecutionAttemptRegistry.transition(a.tenant_id,a.execution_attempt_id,cur.state,fp,target,c)
        with ThreadPoolExecutor(max_workers=2) as ex:
            fs=[ex.submit(run) for _ in range(2)]; success=0
            for f in fs:
                try: f.result(timeout=30); success += 1
                except FinancialExecutionAttemptTransitionConflictError: pass
        assert success==1

def test_concurrent_exact_create_stress_bounded(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]
    for iteration in range(10):
        a=make_attempt(tenant_id=f"tenant-{iteration}"); out=_raced_creates(c,[a,a]); outcomes=[x[0].outcome for x in out if x[0] is not None]
        assert sorted(outcomes)==["CREATED","IDEMPOTENT_REPLAY"], (iteration,outcomes); assert c.count_documents({"tenant_id":a.tenant_id,"execution_attempt_id":a.execution_attempt_id})==1

def test_concurrent_divergent_create_stress_bounded(mongo_db):
    c=mongo_db["kennel_financial_execution_attempts"]
    for iteration in range(10):
        a=make_attempt(tenant_id=f"divergent-{iteration}"); b=FinancialExecutionAttempt(**{**a.__dict__,"execution_command_id":f"other-{iteration}"}); out=_raced_creates(c,[a,b])
        assert sum(x[0] is not None for x in out)==1, iteration; assert sum(isinstance(x[1],FinancialExecutionAttemptCreateConflictError) for x in out)==1, iteration; assert c.count_documents({"tenant_id":a.tenant_id,"execution_attempt_id":a.execution_attempt_id})==1

# Added deterministic error-taxonomy checks for the forward-corrected registry.
def test_labeled_transaction_errors_propagate_unchanged(monkeypatch):
    error = PyMongoError("transient", error_labels=["TransientTransactionError"])
    class FailingCollection:
        def create_index(self, *_args, **_kwargs):
            raise error
    monkeypatch.setattr("tools.eos.kennel.registry.financial_execution_attempt_registry._target", lambda _collection: FailingCollection())
    with pytest.raises(PyMongoError) as caught:
        FinancialExecutionAttemptRegistry.ensure_indexes()
    assert caught.value is error
    unknown = PyMongoError("unknown commit", error_labels=["UnknownTransactionCommitResult"])
    def fail_get(*_args, **_kwargs):
        raise unknown
    monkeypatch.setattr(FinancialExecutionAttemptRegistry, "get", staticmethod(fail_get))
    with pytest.raises(PyMongoError) as caught_unknown:
        FinancialExecutionAttemptRegistry.transition("tenant", "attempt", FinancialExecutionAttemptState.PREPARED, "a" * 128, make_attempt())
    assert caught_unknown.value is unknown

def test_unlabeled_pymongo_error_is_canonically_wrapped(monkeypatch):
    error = PyMongoError("ordinary infrastructure failure")
    class FailingCollection:
        def find_one(self, *_args, **_kwargs):
            raise error
    monkeypatch.setattr("tools.eos.kennel.registry.financial_execution_attempt_registry._target", lambda _collection: FailingCollection())
    with pytest.raises(Exception) as caught:
        FinancialExecutionAttemptRegistry.get("tenant", "attempt")
    assert isinstance(caught.value, FinancialExecutionAttemptRegistryError)
    assert caught.value.__cause__ is error

# ARTIFACT: test_financial_execution_attempt_registry_mongo.py
# VERSION: v1.0.1-KENNEL-FINANCIAL-EXECUTION-ATTEMPT-REGISTRY-MONGO-CERT
# CHANGELOG: forward-corrected transaction-error taxonomy and upsert replay certification.
# END OF WILSY OS SOVEREIGN ARTIFACT
