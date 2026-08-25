# -*- coding: utf-8 -*-
"""Real-Mongo Vendor Registry certification; requires TEST_VENDOR_MONGO_URI and never targets Atlas."""

from __future__ import annotations

import copy
import os
import threading
import uuid

import pytest
from pymongo import MongoClient

from tools.eos.saas.billing import vendor_registry as registry_module
from tools.eos.saas.billing.vendor_registry import VendorAuditEventEvidenceConflictError, VendorAuditPendingError, VendorIdempotencyHorizonExceededError, VendorIdempotencyKeyReuseError, VendorMutationOutcome, VendorNotFoundError, VendorPersistedRecordInvalidError, VendorRegistry, VendorRevisionConflictError
from tools.eos.saas.domain.vendor import VendorIdentity


def _uri() -> str:
    uri = os.environ.get("TEST_VENDOR_MONGO_URI", "").strip()
    if not uri or "mongodb.net" in uri or "atlas" in uri.lower():
        raise RuntimeError("TEST_VENDOR_MONGO_URI must name an isolated local or CI MongoDB; Atlas is prohibited")
    return uri


@pytest.fixture(scope="module")
def mongo_collection():
    client = MongoClient(_uri(), serverSelectionTimeoutMS=5000, retryWrites=True)
    client.admin.command("ping")
    database = client[f"wilsy_vendor_registry_cert_{uuid.uuid4().hex}"]
    collection = database["vendors"]
    VendorRegistry.ensure_indexes(collection)
    yield collection
    client.drop_database(database.name)
    client.close()


def _vendor(tenant_id: str, vendor_id: str | None = None) -> VendorIdentity:
    return VendorIdentity(tenant_id=tenant_id, vendor_id=vendor_id or str(uuid.uuid4()), legal_name="Certification Vendor")


def test_real_mongo_cas_soak_and_tenant_isolation(mongo_collection):
    successes = conflicts = mismatches = 0
    for race in range(100):
        vendor = VendorRegistry.create(_vendor("tenant-a"), mongo_collection)
        barrier = threading.Barrier(2)
        outcomes = []

        def writer(name: str) -> None:
            barrier.wait()
            try:
                outcomes.append(("success", VendorRegistry.update("tenant-a", vendor.vendor_id, 1, {"trading_name": name}, mongo_collection)))
            except VendorRevisionConflictError:
                outcomes.append(("conflict", None))

        threads = [threading.Thread(target=writer, args=(f"writer-{race}-{index}",)) for index in range(2)]
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]
        successes += sum(kind == "success" for kind, _ in outcomes)
        conflicts += sum(kind == "conflict" for kind, _ in outcomes)
        final = VendorRegistry.get("tenant-a", vendor.vendor_id, mongo_collection)
        mismatches += int(final.revision != 2)
        with pytest.raises(VendorNotFoundError):
            VendorRegistry.get("tenant-b", vendor.vendor_id, mongo_collection)
        with pytest.raises(VendorNotFoundError):
            VendorRegistry.update("tenant-b", vendor.vendor_id, 1, {"trading_name": "forbidden"}, mongo_collection)
    assert successes == 100
    assert conflicts == 100
    assert mismatches == 0


def test_real_audit_pending_recovery_replay_and_hydration(mongo_collection, monkeypatch):
    original_audit = registry_module._audit_collection_or_none
    monkeypatch.setattr(registry_module, "_audit_collection_or_none", lambda _: None)
    vendor = _vendor("tenant-a")
    with pytest.raises(VendorAuditPendingError, match="VENDOR_COMMITTED_AUDIT_PENDING"):
        VendorRegistry.create(vendor, mongo_collection)
    persisted = mongo_collection.find_one({"tenant_id": "tenant-a", "vendor_id": vendor.vendor_id})
    assert persisted and persisted["audit_intent"]["status"] == "PENDING"
    monkeypatch.setattr(registry_module, "_audit_collection_or_none", original_audit)
    assert VendorRegistry.recover_pending_audits("tenant-a", collection=mongo_collection) >= 1
    persisted = mongo_collection.find_one({"tenant_id": "tenant-a", "vendor_id": vendor.vendor_id})
    event_key = persisted["audit_intent"]["event_key"]
    event = mongo_collection.database["billing_audit_events"].find_one({"event_key": event_key})
    assert persisted["audit_intent"]["status"] == "DELIVERED"
    assert event and event["revision"] == persisted["revision"] and event["proof_hash"] == persisted["proof_hash"]
    VendorRegistry._deliver_audit_intent("tenant-a", vendor.vendor_id, 1, mongo_collection)
    assert mongo_collection.database["billing_audit_events"].count_documents({"event_key": event_key}) == 1
    mongo_collection.insert_one({"tenant_id": "tenant-a", "vendor_id": "corrupt", "legal_name": None, "revision": 1, "metadata": {}, "created_at": persisted["created_at"], "updated_at": persisted["updated_at"], "proof_hash": "x"})
    with pytest.raises(VendorPersistedRecordInvalidError, match="VENDOR_PERSISTED_RECORD_INVALID"):
        VendorRegistry.get("tenant-a", "corrupt", mongo_collection)


def test_real_business_idempotency_replay_and_concurrent_duplicate(mongo_collection):
    vendor = VendorRegistry.create(_vendor("tenant-a"), mongo_collection)
    key = f"command-{uuid.uuid4().hex}"
    committed = VendorRegistry.update("tenant-a", vendor.vendor_id, 1, {"trading_name": "Replay Safe"}, mongo_collection, key)
    replay = VendorRegistry.update("tenant-a", vendor.vendor_id, 1, {"trading_name": "Replay Safe"}, mongo_collection, key)
    assert committed.revision == replay.revision == 2
    with pytest.raises(VendorIdempotencyKeyReuseError):
        VendorRegistry.update("tenant-a", vendor.vendor_id, 1, {"trading_name": "Different"}, mongo_collection, key)
    assert mongo_collection.database["billing_audit_events"].count_documents({"tenant_id": "tenant-a", "metadata.vendor_id": vendor.vendor_id}) == 2


def test_real_replay_horizon_fails_closed_after_receipt_eviction(mongo_collection):
    vendor = VendorRegistry.create(_vendor("tenant-horizon"), mongo_collection)
    first_key = f"command-{uuid.uuid4().hex}"
    for expected_revision in range(1, 22):
        key = first_key if expected_revision == 1 else f"command-{uuid.uuid4().hex}"
        VendorRegistry.update("tenant-horizon", vendor.vendor_id, expected_revision, {"trading_name": f"horizon-{expected_revision}"}, mongo_collection, key)
    document = mongo_collection.find_one({"tenant_id": "tenant-horizon", "vendor_id": vendor.vendor_id})
    assert document["replay_floor_revision"] == 2 and len(document["command_receipts"]) == 20
    with pytest.raises(VendorIdempotencyHorizonExceededError, match="IDEMPOTENCY_HORIZON_EXCEEDED"):
        VendorRegistry.update("tenant-horizon", vendor.vendor_id, 1, {"trading_name": "horizon-1"}, mongo_collection, first_key)
    assert VendorRegistry.get("tenant-horizon", vendor.vendor_id, mongo_collection).revision == 22


def test_real_concurrent_duplicate_command_soak(mongo_collection):
    races = successes = replays = conflicts = failures = 0
    for race in range(500):
        vendor = VendorRegistry.create(_vendor("tenant-duplicate"), mongo_collection)
        key = f"duplicate-{uuid.uuid4().hex}"
        barrier, outcomes = threading.Barrier(2), []
        def submit() -> None:
            try:
                barrier.wait()
                outcomes.append(VendorRegistry.update("tenant-duplicate", vendor.vendor_id, 1, {"trading_name": "same-command"}, mongo_collection, key))
            except Exception as error:
                outcomes.append(error)
        workers = [threading.Thread(target=submit) for _ in range(2)]
        [worker.start() for worker in workers]; [worker.join() for worker in workers]
        races += 1
        failures += sum(isinstance(value, Exception) for value in outcomes)
        successes += sum(not isinstance(value, Exception) and value.outcome is VendorMutationOutcome.COMMITTED_AUDITED for value in outcomes)
        replays += sum(not isinstance(value, Exception) and value.outcome is VendorMutationOutcome.IDEMPOTENT_REPLAY for value in outcomes)
        conflicts += sum(isinstance(value, VendorRevisionConflictError) for value in outcomes)
        assert VendorRegistry.get("tenant-duplicate", vendor.vendor_id, mongo_collection).revision == 2
        assert mongo_collection.database["billing_audit_events"].count_documents({"tenant_id": "tenant-duplicate", "metadata.vendor_id": vendor.vendor_id}) == 2
    assert races == 500 and successes == replays == 500 and conflicts == failures == 0


def test_malformed_command_receipt_fails_closed(mongo_collection):
    vendor = VendorRegistry.create(_vendor("tenant-corrupt-receipt"), mongo_collection)
    mongo_collection.update_one({"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id}, {"$set": {"command_receipts": "corrupt"}})
    with pytest.raises(VendorPersistedRecordInvalidError, match="VENDOR_PERSISTED_RECORD_INVALID"):
        VendorRegistry.update(vendor.tenant_id, vendor.vendor_id, 1, {"trading_name": "must-not-mutate"}, mongo_collection, "corrupt-receipt-test")


def test_audit_outage_duplicate_command_recovers_once(mongo_collection, monkeypatch):
    vendor = VendorRegistry.create(_vendor("tenant-outage"), mongo_collection)
    original = registry_module._audit_collection_or_none
    monkeypatch.setattr(registry_module, "_audit_collection_or_none", lambda _: None)
    key, barrier, outcomes = f"outage-{uuid.uuid4().hex}", threading.Barrier(2), []
    def submit() -> None:
        barrier.wait(); outcomes.append(VendorRegistry.update("tenant-outage", vendor.vendor_id, 1, {"trading_name": "outage"}, mongo_collection, key))
    workers = [threading.Thread(target=submit) for _ in range(2)]
    [worker.start() for worker in workers]; [worker.join() for worker in workers]
    assert sorted(result.outcome for result in outcomes) == [VendorMutationOutcome.COMMITTED_AUDIT_PENDING, VendorMutationOutcome.IDEMPOTENT_REPLAY]
    doc = mongo_collection.find_one({"tenant_id": "tenant-outage", "vendor_id": vendor.vendor_id})
    assert doc["revision"] == 2 and doc["audit_intent"]["status"] == "PENDING"
    assert mongo_collection.database["billing_audit_events"].count_documents({"metadata.vendor_id": vendor.vendor_id}) == 1
    monkeypatch.setattr(registry_module, "_audit_collection_or_none", original)
    VendorRegistry.recover_pending_audits("tenant-outage", collection=mongo_collection)
    assert mongo_collection.database["billing_audit_events"].count_documents({"metadata.vendor_id": vendor.vendor_id}) == 2


def test_process_restart_replay_uses_persisted_receipt(mongo_collection):
    vendor = VendorRegistry.create(_vendor("tenant-restart"), mongo_collection)
    key = f"restart-{uuid.uuid4().hex}"
    committed = VendorRegistry.update("tenant-restart", vendor.vendor_id, 1, {"trading_name": "restart"}, mongo_collection, key)
    client = MongoClient(_uri(), serverSelectionTimeoutMS=5000, retryWrites=True)
    fresh_collection = client[mongo_collection.database.name]["vendors"]
    replay = VendorRegistry.update("tenant-restart", vendor.vendor_id, 1, {"trading_name": "restart"}, fresh_collection, key)
    assert committed.outcome is VendorMutationOutcome.COMMITTED_AUDITED
    assert replay.outcome is VendorMutationOutcome.IDEMPOTENT_REPLAY
    assert replay.committed_revision == 2 and replay.current_revision == 2
    assert fresh_collection.database["billing_audit_events"].count_documents({"metadata.vendor_id": vendor.vendor_id}) == 2
    client.close()


def test_process_restart_replay_horizon_uses_persisted_floor(mongo_collection):
    vendor = VendorRegistry.create(_vendor("tenant-restart-horizon"), mongo_collection)
    keys = []
    for revision in range(1, 22):
        key = f"restart-horizon-{uuid.uuid4().hex}"; keys.append(key)
        VendorRegistry.update(vendor.tenant_id, vendor.vendor_id, revision, {"trading_name": f"r{revision}"}, mongo_collection, key)
    before = mongo_collection.find_one({"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id})
    client = MongoClient(_uri(), serverSelectionTimeoutMS=5000, retryWrites=True)
    fresh = client[mongo_collection.database.name]["vendors"]
    retained = VendorRegistry.update(vendor.tenant_id, vendor.vendor_id, 2, {"trading_name": "r2"}, fresh, keys[1])
    with pytest.raises(VendorIdempotencyHorizonExceededError):
        VendorRegistry.update(vendor.tenant_id, vendor.vendor_id, 1, {"trading_name": "r1"}, fresh, keys[0])
    after = fresh.find_one({"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id})
    assert retained.outcome is VendorMutationOutcome.IDEMPOTENT_REPLAY
    assert before is not None and after is not None
    assert before["revision"] == after["revision"] and before["replay_floor_revision"] == after["replay_floor_revision"] == 2
    client.close()


def _pending_revision_intent(mongo_collection, monkeypatch, tenant_id: str):
    """Creates one real pending revision intent without mutating audit evidence outside the certification fixture."""
    vendor = VendorRegistry.create(_vendor(tenant_id), mongo_collection)
    original = registry_module._audit_collection_or_none
    monkeypatch.setattr(registry_module, "_audit_collection_or_none", lambda _: None)
    result = VendorRegistry.update(tenant_id, vendor.vendor_id, 1, {"trading_name": "pending-recovery"}, mongo_collection, f"pending-{uuid.uuid4().hex}")
    monkeypatch.setattr(registry_module, "_audit_collection_or_none", original)
    assert result.outcome is VendorMutationOutcome.COMMITTED_AUDIT_PENDING
    document = mongo_collection.find_one({"tenant_id": tenant_id, "vendor_id": vendor.vendor_id})
    assert document and document["audit_intent"]["status"] == "PENDING"
    return vendor, document["audit_intent"]


@pytest.mark.parametrize("mutation", [
    lambda event: event.update({"proof_hash": "0" * 128}),
    lambda event: event.update({"revision": 999}),
    lambda event: event.update({"tenant_id": "hostile-tenant"}),
    lambda event: event["metadata"].update({"vendor_id": "hostile-vendor"}),
    lambda event: event.update({"event_type": "HOSTILE_OPERATION"}),
    lambda event: event.update({"proof_hash": "f" * 128, "revision": 999, "event_type": "HOSTILE_OPERATION"}),
])
def test_recovery_rejects_hostile_existing_audit_evidence(mongo_collection, monkeypatch, mutation):
    vendor, intent = _pending_revision_intent(mongo_collection, monkeypatch, f"tenant-hostile-{uuid.uuid4().hex}")
    audit = mongo_collection.database["billing_audit_events"]
    hostile = copy.deepcopy(registry_module._audit_event_document(intent, vendor.tenant_id, vendor.vendor_id))
    mutation(hostile)
    audit.insert_one(hostile)
    before = mongo_collection.find_one({"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id})
    with pytest.raises(VendorAuditEventEvidenceConflictError, match="AUDIT_EVENT_EVIDENCE_CONFLICT"):
        VendorRegistry.recover_pending_audits(vendor.tenant_id, collection=mongo_collection)
    after = mongo_collection.find_one({"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id})
    persisted_hostile = audit.find_one({"event_key": intent["event_key"]})
    assert before and after and persisted_hostile
    assert after["revision"] == before["revision"]
    assert after["command_receipts"] == before["command_receipts"]
    assert after["audit_intent"]["status"] == "PENDING"
    assert audit.count_documents({"event_key": intent["event_key"]}) == 1
    assert persisted_hostile["proof_hash"] == hostile["proof_hash"]


@pytest.mark.parametrize("mutation", [
    lambda event: event.pop("proof_hash"),
    lambda event: event.update({"proof_hash": 7}),
    lambda event: event.pop("revision"),
    lambda event: event.update({"revision": True}),
    lambda event: event.update({"metadata": {}}),
])
def test_recovery_rejects_malformed_existing_audit_evidence(mongo_collection, monkeypatch, mutation):
    vendor, intent = _pending_revision_intent(mongo_collection, monkeypatch, f"tenant-malformed-{uuid.uuid4().hex}")
    audit = mongo_collection.database["billing_audit_events"]
    malformed = copy.deepcopy(registry_module._audit_event_document(intent, vendor.tenant_id, vendor.vendor_id))
    mutation(malformed)
    audit.insert_one(malformed)
    with pytest.raises(VendorAuditEventEvidenceConflictError, match="AUDIT_EVENT_EVIDENCE_CONFLICT"):
        VendorRegistry.recover_pending_audits(vendor.tenant_id, collection=mongo_collection)
    after = mongo_collection.find_one({"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id})
    assert after and after["audit_intent"]["status"] == "PENDING"
    assert audit.count_documents({"event_key": intent["event_key"]}) == 1


def test_recovery_marks_matching_preexisting_event_delivered(mongo_collection, monkeypatch):
    vendor, intent = _pending_revision_intent(mongo_collection, monkeypatch, f"tenant-crash-{uuid.uuid4().hex}")
    audit = mongo_collection.database["billing_audit_events"]
    audit.insert_one(registry_module._audit_event_document(intent, vendor.tenant_id, vendor.vendor_id))
    assert VendorRegistry.recover_pending_audits(vendor.tenant_id, collection=mongo_collection) == 1
    after = mongo_collection.find_one({"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id})
    assert after and after["audit_intent"]["status"] == "DELIVERED"
    assert audit.count_documents({"event_key": intent["event_key"]}) == 1


def test_two_workers_recover_one_pending_audit_event(mongo_collection, monkeypatch):
    vendor, intent = _pending_revision_intent(mongo_collection, monkeypatch, f"tenant-two-worker-{uuid.uuid4().hex}")
    barrier, outcomes = threading.Barrier(2), []
    database_name = mongo_collection.database.name

    def recover() -> None:
        client = MongoClient(_uri(), serverSelectionTimeoutMS=5000, retryWrites=True)
        try:
            barrier.wait()
            outcomes.append(VendorRegistry.recover_pending_audits(vendor.tenant_id, collection=client[database_name]["vendors"]))
        except Exception as error:
            outcomes.append(error)
        finally:
            client.close()

    workers = [threading.Thread(target=recover) for _ in range(2)]
    [worker.start() for worker in workers]; [worker.join() for worker in workers]
    after = mongo_collection.find_one({"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id})
    audit = mongo_collection.database["billing_audit_events"]
    assert all(not isinstance(outcome, Exception) for outcome in outcomes)
    assert after and after["audit_intent"]["status"] == "DELIVERED"
    assert audit.count_documents({"event_key": intent["event_key"]}) == 1


def test_two_workers_reject_one_hostile_pending_audit_event(mongo_collection, monkeypatch):
    vendor, intent = _pending_revision_intent(mongo_collection, monkeypatch, f"tenant-two-worker-hostile-{uuid.uuid4().hex}")
    audit = mongo_collection.database["billing_audit_events"]
    hostile = registry_module._audit_event_document(intent, vendor.tenant_id, vendor.vendor_id)
    hostile["proof_hash"] = "f" * 128
    audit.insert_one(hostile)
    barrier, outcomes = threading.Barrier(2), []
    database_name = mongo_collection.database.name

    def recover() -> None:
        client = MongoClient(_uri(), serverSelectionTimeoutMS=5000, retryWrites=True)
        try:
            barrier.wait()
            outcomes.append(VendorRegistry.recover_pending_audits(vendor.tenant_id, collection=client[database_name]["vendors"]))
        except Exception as error:
            outcomes.append(error)
        finally:
            client.close()

    workers = [threading.Thread(target=recover) for _ in range(2)]
    [worker.start() for worker in workers]; [worker.join() for worker in workers]
    after = mongo_collection.find_one({"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id})
    assert len(outcomes) == 2 and all(isinstance(outcome, VendorAuditEventEvidenceConflictError) for outcome in outcomes)
    assert after and after["audit_intent"]["status"] == "PENDING"
    assert audit.count_documents({"event_key": intent["event_key"]}) == 1


def _assert_all_vendor_surfaces_reject_corruption(mongo_collection, vendor, command_key: str) -> None:
    """Proves ordinary reads and an exact retained replay share the canonical persisted-document boundary."""
    with pytest.raises(VendorPersistedRecordInvalidError, match="VENDOR_PERSISTED_RECORD_INVALID"):
        VendorRegistry.get(vendor.tenant_id, vendor.vendor_id, mongo_collection)
    with pytest.raises(VendorPersistedRecordInvalidError, match="VENDOR_PERSISTED_RECORD_INVALID"):
        VendorRegistry.list(vendor.tenant_id, collection=mongo_collection)
    with pytest.raises(VendorPersistedRecordInvalidError, match="VENDOR_PERSISTED_RECORD_INVALID"):
        VendorRegistry.update(vendor.tenant_id, vendor.vendor_id, 1, {"trading_name": "canonical-boundary"}, mongo_collection, command_key)


def _receipt_bearing_vendor(mongo_collection, tenant_id: str):
    """Creates one production-path Vendor fixture with a valid receipt and replay floor for corruption injection."""
    vendor = VendorRegistry.create(_vendor(tenant_id), mongo_collection)
    command_key = f"canonical-boundary-{uuid.uuid4().hex}"
    VendorRegistry.update(vendor.tenant_id, vendor.vendor_id, 1, {"trading_name": "canonical-boundary"}, mongo_collection, command_key)
    return vendor, command_key


def test_canonical_hydration_rejects_bool_replay_floor_on_get_list_and_update(mongo_collection):
    vendor, command_key = _receipt_bearing_vendor(mongo_collection, f"tenant-floor-boundary-{uuid.uuid4().hex}")
    predicate = {"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id}
    mongo_collection.update_one(predicate, {"$set": {"replay_floor_revision": True}})
    before = mongo_collection.find_one(predicate)
    _assert_all_vendor_surfaces_reject_corruption(mongo_collection, vendor, command_key)
    after = mongo_collection.find_one(predicate)
    assert before == after


def test_explicit_null_replay_floor_fails_closed_before_all_replay_classification(mongo_collection):
    tenant_id, vendor = f"tenant-null-floor-{uuid.uuid4().hex}", _vendor(f"tenant-null-floor-{uuid.uuid4().hex}")
    vendor = VendorIdentity(tenant_id=tenant_id, vendor_id=vendor.vendor_id, legal_name=vendor.legal_name)
    VendorRegistry.create(vendor, mongo_collection)
    commands = []
    for expected_revision in range(1, 22):
        command_key, changes = f"null-floor-{uuid.uuid4().hex}", {"trading_name": f"null-floor-{expected_revision}"}
        VendorRegistry.update(tenant_id, vendor.vendor_id, expected_revision, changes, mongo_collection, command_key)
        commands.append((command_key, changes))
    predicate = {"tenant_id": tenant_id, "vendor_id": vendor.vendor_id}
    mongo_collection.update_one(predicate, {"$set": {"replay_floor_revision": None}})
    before = mongo_collection.find_one(predicate)
    with pytest.raises(VendorPersistedRecordInvalidError, match="VENDOR_PERSISTED_RECORD_INVALID"):
        VendorRegistry.get(tenant_id, vendor.vendor_id, mongo_collection)
    with pytest.raises(VendorPersistedRecordInvalidError, match="VENDOR_PERSISTED_RECORD_INVALID"):
        VendorRegistry.list(tenant_id, collection=mongo_collection)
    for expected_revision, command in ((2, commands[1]), (1, commands[0]), (22, (f"fresh-null-{uuid.uuid4().hex}", {"trading_name": "fresh-null"}))):
        with pytest.raises(VendorPersistedRecordInvalidError, match="VENDOR_PERSISTED_RECORD_INVALID"):
            VendorRegistry.update(tenant_id, vendor.vendor_id, expected_revision, command[1], mongo_collection, command[0])
    after = mongo_collection.find_one(predicate)
    assert before == after


@pytest.mark.parametrize("corrupt_receipts", [
    "corrupt",
    [{"idempotency_key": "malformed"}],
])
def test_canonical_hydration_rejects_malformed_receipts_on_get_list_and_update(mongo_collection, corrupt_receipts):
    vendor, command_key = _receipt_bearing_vendor(mongo_collection, f"tenant-receipt-boundary-{uuid.uuid4().hex}")
    predicate = {"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id}
    mongo_collection.update_one(predicate, {"$set": {"command_receipts": corrupt_receipts}})
    _assert_all_vendor_surfaces_reject_corruption(mongo_collection, vendor, command_key)


def test_canonical_hydration_rejects_relational_receipt_corruption_on_get_list_and_update(mongo_collection):
    vendor, command_key = _receipt_bearing_vendor(mongo_collection, f"tenant-relation-boundary-{uuid.uuid4().hex}")
    predicate = {"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id}
    mongo_collection.update_one(predicate, {"$set": {"command_receipts.0.committed_revision": 99}})
    _assert_all_vendor_surfaces_reject_corruption(mongo_collection, vendor, command_key)


def test_canonical_hydration_accepts_healthy_get_list_and_horizon(mongo_collection):
    tenant_id, vendor = f"tenant-healthy-boundary-{uuid.uuid4().hex}", _vendor(f"tenant-healthy-boundary-{uuid.uuid4().hex}")
    vendor = VendorIdentity(tenant_id=tenant_id, vendor_id=vendor.vendor_id, legal_name=vendor.legal_name)
    VendorRegistry.create(vendor, mongo_collection)
    for expected_revision in range(1, 22):
        VendorRegistry.update(tenant_id, vendor.vendor_id, expected_revision, {"trading_name": f"healthy-{expected_revision}"}, mongo_collection, f"healthy-boundary-{uuid.uuid4().hex}")
    assert VendorRegistry.get(tenant_id, vendor.vendor_id, mongo_collection).revision == 22
    listed = VendorRegistry.list(tenant_id, collection=mongo_collection)
    assert len(listed) == 1 and listed[0].vendor_id == vendor.vendor_id


def _horizon_vendor(mongo_collection, tenant_id: str):
    """Builds a production-path 21-command fixture with receipt limit 20, floor 2, and replay identities."""
    vendor = VendorRegistry.create(_vendor(tenant_id), mongo_collection)
    commands = []
    for expected_revision in range(1, 22):
        key, changes = f"horizon-matrix-{uuid.uuid4().hex}", {"trading_name": f"horizon-matrix-{expected_revision}"}
        VendorRegistry.update(tenant_id, vendor.vendor_id, expected_revision, changes, mongo_collection, key)
        commands.append((key, changes))
    document = mongo_collection.find_one({"tenant_id": tenant_id, "vendor_id": vendor.vendor_id})
    assert document and document["revision"] == 22 and len(document["command_receipts"]) == 20 and document["replay_floor_revision"] == 2
    return vendor, commands


def _assert_horizon_corruption_fails_all_surfaces(mongo_collection, vendor, commands) -> None:
    """Proves corrupt replay state fails before any read, retained replay, horizon decision, or fresh command can proceed."""
    predicate = {"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id}
    before = mongo_collection.find_one(predicate)
    with pytest.raises(VendorPersistedRecordInvalidError, match="VENDOR_PERSISTED_RECORD_INVALID"):
        VendorRegistry.get(vendor.tenant_id, vendor.vendor_id, mongo_collection)
    with pytest.raises(VendorPersistedRecordInvalidError, match="VENDOR_PERSISTED_RECORD_INVALID"):
        VendorRegistry.list(vendor.tenant_id, collection=mongo_collection)
    for expected_revision, command in ((2, commands[1]), (1, commands[0]), (22, (f"fresh-matrix-{uuid.uuid4().hex}", {"trading_name": "fresh-matrix"}))):
        with pytest.raises(VendorPersistedRecordInvalidError, match="VENDOR_PERSISTED_RECORD_INVALID"):
            VendorRegistry.update(vendor.tenant_id, vendor.vendor_id, expected_revision, command[1], mongo_collection, command[0])
    assert mongo_collection.find_one(predicate) == before


@pytest.mark.parametrize("corrupt_floor", [True, False, 1.5, "2", -1, {}, [], 0])
def test_replay_floor_scalar_matrix_fails_closed(mongo_collection, corrupt_floor):
    vendor, commands = _horizon_vendor(mongo_collection, f"tenant-floor-scalar-{uuid.uuid4().hex}")
    mongo_collection.update_one({"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id}, {"$set": {"replay_floor_revision": corrupt_floor}})
    _assert_horizon_corruption_fails_all_surfaces(mongo_collection, vendor, commands)


@pytest.mark.parametrize("corrupt_floor", [23, 22, 3, 1, 17])
def test_replay_floor_relational_matrix_fails_closed(mongo_collection, corrupt_floor):
    vendor, commands = _horizon_vendor(mongo_collection, f"tenant-floor-relation-{uuid.uuid4().hex}")
    mongo_collection.update_one({"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id}, {"$set": {"replay_floor_revision": corrupt_floor}})
    _assert_horizon_corruption_fails_all_surfaces(mongo_collection, vendor, commands)


@pytest.mark.parametrize("corruption", [
    {"command_receipts.19.expected_revision": 3},
    {"command_receipts.19.committed_revision": 99},
    {"command_receipts.18.expected_revision": 2},
])
def test_replay_floor_receipt_cross_integrity_fails_closed(mongo_collection, corruption):
    vendor, commands = _horizon_vendor(mongo_collection, f"tenant-floor-cross-{uuid.uuid4().hex}")
    mongo_collection.update_one({"tenant_id": vendor.tenant_id, "vendor_id": vendor.vendor_id}, {"$set": corruption})
    _assert_horizon_corruption_fails_all_surfaces(mongo_collection, vendor, commands)
