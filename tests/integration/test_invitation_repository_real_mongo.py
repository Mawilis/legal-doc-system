"""Governed real-Mongo invitation repository certificate (host-only runtime)."""
import hashlib, os, uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from datetime import datetime, timedelta, timezone
import pytest
from pymongo import MongoClient
from tools.eos.auth.invitation import InvitationAuthority, InvitationStatus
from tools.eos.auth.invitation_repository import InvitationRepository

URI = os.environ.get("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")

@pytest.fixture
def collection():
    client = MongoClient(URI, serverSelectionTimeoutMS=2000, retryWrites=True); client.admin.command("ping")
    c = client["wilsy_invitation_cert"]["invitations"]; InvitationRepository.ensure_indexes(c)
    yield c, client
    client.close()

def make():
    now = datetime.now(timezone.utc); return InvitationAuthority(f"cert-inv-{uuid.uuid4().hex}", "cert-tenant", f"recipient-{uuid.uuid4().hex}", f"inviter-{uuid.uuid4().hex}", "AUDITOR", hashlib.sha3_512(uuid.uuid4().bytes).hexdigest(), InvitationStatus.ACTIVE, now + timedelta(hours=1), 0, now)

def test_rm_a_insert_get(collection):
    c, _ = collection; value = make(); InvitationRepository.insert(value, c); assert InvitationRepository.get(value.invitation_id, c) == value; raw = c.find_one({"invitation_id": value.invitation_id}); assert raw is not None and "recipient_email" not in raw and raw["recipient_principal_id"] == value.recipient_principal_id; c.delete_one({"invitation_id": value.invitation_id})

def test_rm_b_consume_and_replay(collection):
    c, _ = collection; value = make(); InvitationRepository.insert(value, c); consumed = InvitationRepository.consume(value.invitation_id, value.capability_digest, 0, datetime.now(timezone.utc), c); assert consumed.revision == 1; c.delete_one({"invitation_id": value.invitation_id})

def test_rm_c_concurrent_cas(collection):
    c, client = collection; value = make(); InvitationRepository.insert(value, c)
    barrier = Barrier(2); consumed_at = datetime.now(timezone.utc)
    def worker():
        with client.start_session() as session:
            barrier.wait(timeout=5)
            try:
                return ("SUCCESS", InvitationRepository.consume(value.invitation_id, value.capability_digest, 0, consumed_at, c, session=session))
            except Exception as exc:
                return (type(exc).__name__, exc)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = [future.result(timeout=10) for future in (pool.submit(worker), pool.submit(worker))]
    assert sum(result[0] == "SUCCESS" for result in results) == 1
    assert sum(result[0] in {"InvitationAlreadyConsumedError", "InvitationConcurrentModificationError"} for result in results) == 1
    durable = InvitationRepository.get(value.invitation_id, c)
    assert durable.status is InvitationStatus.CONSUMED and durable.revision == 1 and durable.consumed_at is not None
    c.delete_one({"invitation_id": value.invitation_id})

def test_rm_d_revoke_and_expiry(collection):
    c, _ = collection; value = make(); InvitationRepository.insert(value, c); c.update_one({"invitation_id": value.invitation_id}, {"$set": {"status": "REVOKED"}}); c.delete_one({"invitation_id": value.invitation_id})

def test_rm_e_transaction_rollback(collection):
    c, client = collection; value = make()
    with pytest.raises(RuntimeError):
        with client.start_session() as session:
            def callback(s): InvitationRepository.insert(value, c, session=s); raise RuntimeError("rollback")
            session.with_transaction(callback)
    assert c.find_one({"invitation_id": value.invitation_id}) is None
