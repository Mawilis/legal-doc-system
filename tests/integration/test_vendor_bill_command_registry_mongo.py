import os
import uuid
from dataclasses import replace
from datetime import datetime, timezone
from pymongo import MongoClient
from tools.eos.saas.domain.vendor_bill_command import VendorBillCommand, VendorBillCommandType, VendorBillCommandOutcome, VendorBillCommandDomainError
from tools.eos.saas.billing.vendor_bill_command_registry import VendorBillCommandRegistry, VendorBillCommandCreateOutcome, VendorBillCommandIdempotencyReuseConflictError, VendorBillCommandSequenceConflictError

def _command(key="k", sequence=1, fingerprint="a"*128):
    return VendorBillCommand("tenant-a", "payable-a", key, sequence, VendorBillCommandType.OPEN_BILL, fingerprint, VendorBillCommandOutcome.COMMITTED, datetime(2026,1,1,tzinfo=timezone.utc), 1, 2, 0, 0)

def test_vendor_bill_command_domain_round_trip_and_invariants():
    command = _command()
    assert VendorBillCommand.from_persistence_dict(command.to_persistence_dict()) == command
    for invalid in (True, 0, -1):
        try: _command(sequence=invalid)
        except VendorBillCommandDomainError: pass
        else: raise AssertionError("invalid command sequence accepted")

def test_vendor_bill_command_projection_round_trip_and_strict_fields():
    command = VendorBillCommand("tenant-a", "payable-a", "projection-key", 2, VendorBillCommandType.PROJECT_FINANCIAL_APPROVAL_RESULT, "b"*128, VendorBillCommandOutcome.COMMITTED, datetime(2026,1,1,tzinfo=timezone.utc), 2, 2, 0, 1, "result-a")
    assert VendorBillCommand.from_persistence_dict(command.to_persistence_dict()) == command
    payload = command.to_persistence_dict()
    for field in ("tenant_id", "payable_id", "idempotency_key", "command_sequence", "command_type", "command_fingerprint", "committed_at", "obligation_revision_before", "approval_projection_revision_before", "effective_result_id"):
        missing = dict(payload); del missing[field]
        try: VendorBillCommand.from_persistence_dict(missing)
        except VendorBillCommandDomainError: pass
        else: raise AssertionError(f"missing field accepted: {field}")

def test_vendor_bill_command_registry_real_mongo():
    client = MongoClient(os.environ["TEST_VENDOR_MONGO_URI"], serverSelectionTimeoutMS=5000, retryWrites=True)
    assert client.admin.command("hello")["isWritablePrimary"]
    db = client[f"vendor_bill_commands_{uuid.uuid4().hex}"]; collection = db["vendor_bill_commands"]; VendorBillCommandRegistry.ensure_indexes(collection)
    command = _command(); created = VendorBillCommandRegistry.create_command(command, collection); replay = VendorBillCommandRegistry.create_command(command, collection)
    assert created.outcome is VendorBillCommandCreateOutcome.CREATED and replay.outcome is VendorBillCommandCreateOutcome.IDEMPOTENT_REPLAY and collection.count_documents({}) == 1
    try: VendorBillCommandRegistry.create_command(_command(fingerprint="b"*128), collection)
    except VendorBillCommandIdempotencyReuseConflictError: pass
    else: raise AssertionError("same key/different fingerprint accepted")
    client.drop_database(db.name); client.close()

def test_vendor_bill_command_registry_indexes_scopes_and_sequence_collision_real_mongo():
    client = MongoClient(os.environ["TEST_VENDOR_MONGO_URI"], serverSelectionTimeoutMS=5000, retryWrites=True); assert client.admin.command("hello")["isWritablePrimary"]
    db = client[f"vendor_bill_commands_scope_{uuid.uuid4().hex}"]; collection = db["vendor_bill_commands"]; VendorBillCommandRegistry.ensure_indexes(collection)
    indexes = list(collection.list_indexes()); by_name = {item["name"]: item for item in indexes}
    assert by_name["tenant_payable_command_idempotency_unique"]["unique"] is True and list(by_name["tenant_payable_command_idempotency_unique"]["key"].items()) == [("tenant_id", 1), ("payable_id", 1), ("idempotency_key", 1)]
    assert by_name["tenant_payable_command_sequence_unique"]["unique"] is True and list(by_name["tenant_payable_command_sequence_unique"]["key"].items()) == [("tenant_id", 1), ("payable_id", 1), ("command_sequence", 1)]
    first = _command(); VendorBillCommandRegistry.create_command(first, collection)
    assert VendorBillCommandRegistry.get_by_idempotency_key("tenant-a", "payable-a", "k", collection) == first
    assert VendorBillCommandRegistry.get_by_sequence("tenant-a", "payable-a", 1, collection) == first
    VendorBillCommandRegistry.create_command(_command(key="k", sequence=1, fingerprint="a"*128), collection)
    payable_b = replace(first, payable_id="payable-b")
    tenant_b = replace(first, tenant_id="tenant-b")
    VendorBillCommandRegistry.create_command(payable_b, collection); VendorBillCommandRegistry.create_command(tenant_b, collection)
    assert collection.count_documents({}) == 3
    client.drop_database(db.name); client.close()

def test_vendor_bill_command_sequence_collision_is_structured_real_mongo():
    client = MongoClient(os.environ["TEST_VENDOR_MONGO_URI"], serverSelectionTimeoutMS=5000, retryWrites=True); assert client.admin.command("hello")["isWritablePrimary"]
    db = client[f"vendor_bill_commands_sequence_{uuid.uuid4().hex}"]; collection = db["vendor_bill_commands"]; VendorBillCommandRegistry.ensure_indexes(collection)
    VendorBillCommandRegistry.create_command(_command(), collection)
    try: VendorBillCommandRegistry.create_command(_command(key="different-key"), collection)
    except VendorBillCommandSequenceConflictError: pass
    else: raise AssertionError("sequence collision was not classified")
    assert collection.count_documents({}) == 1
    client.drop_database(db.name); client.close()

def test_vendor_bill_command_same_key_different_command_family_conflict_real_mongo():
    client = MongoClient(os.environ["TEST_VENDOR_MONGO_URI"], serverSelectionTimeoutMS=5000, retryWrites=True); assert client.admin.command("hello")["isWritablePrimary"]
    db = client[f"vendor_bill_commands_family_{uuid.uuid4().hex}"]; collection = db["vendor_bill_commands"]; VendorBillCommandRegistry.ensure_indexes(collection)
    VendorBillCommandRegistry.create_command(_command(), collection)
    projection = VendorBillCommand("tenant-a", "payable-a", "k", 2, VendorBillCommandType.PROJECT_FINANCIAL_APPROVAL_RESULT, "c"*128, VendorBillCommandOutcome.COMMITTED, datetime(2026,1,1,tzinfo=timezone.utc), 1, 1, 0, 1, "result-a")
    try: VendorBillCommandRegistry.create_command(projection, collection)
    except VendorBillCommandIdempotencyReuseConflictError: pass
    else: raise AssertionError("cross-family idempotency key was classified as replay")
    assert collection.count_documents({}) == 1
    client.drop_database(db.name); client.close()

def test_vendor_bill_command_corruption_precedes_replay_and_sequence_lookup_real_mongo():
    client = MongoClient(os.environ["TEST_VENDOR_MONGO_URI"], serverSelectionTimeoutMS=5000, retryWrites=True); assert client.admin.command("hello")["isWritablePrimary"]
    db = client[f"vendor_bill_commands_corrupt_{uuid.uuid4().hex}"]; collection = db["vendor_bill_commands"]; VendorBillCommandRegistry.ensure_indexes(collection); command = _command(); VendorBillCommandRegistry.create_command(command, collection)
    collection.update_one({"tenant_id": "tenant-a", "payable_id": "payable-a", "idempotency_key": "k"}, {"$set": {"command_sequence": True}})
    for action in (lambda: VendorBillCommandRegistry.create_command(command, collection), lambda: VendorBillCommandRegistry.get_by_sequence("tenant-a", "payable-a", 1, collection)):
        try: action()
        except Exception as error: assert "PERSISTED_RECORD_INVALID" in str(error)
        else: raise AssertionError("corrupt command was accepted")
    client.drop_database(db.name); client.close()

def test_vendor_bill_command_corruption_precedes_idempotency_conflict_real_mongo():
    client = MongoClient(os.environ["TEST_VENDOR_MONGO_URI"], serverSelectionTimeoutMS=5000, retryWrites=True); assert client.admin.command("hello")["isWritablePrimary"]
    db = client[f"vendor_bill_commands_corrupt_conflict_{uuid.uuid4().hex}"]; collection = db["vendor_bill_commands"]; VendorBillCommandRegistry.ensure_indexes(collection); command = _command(); VendorBillCommandRegistry.create_command(command, collection)
    collection.update_one({"tenant_id": "tenant-a", "payable_id": "payable-a", "idempotency_key": "k"}, {"$set": {"command_fingerprint": "bad"}})
    try: VendorBillCommandRegistry.create_command(_command(fingerprint="b"*128), collection)
    except Exception as error: assert "PERSISTED_RECORD_INVALID" in str(error)
    else: raise AssertionError("corrupt record was classified as idempotency conflict")
    client.drop_database(db.name); client.close()

def test_vendor_bill_command_identical_create_concurrency_real_mongo():
    from concurrent.futures import ThreadPoolExecutor
    client = MongoClient(os.environ["TEST_VENDOR_MONGO_URI"], serverSelectionTimeoutMS=5000, retryWrites=True); assert client.admin.command("hello")["isWritablePrimary"]
    db = client[f"vendor_bill_commands_race_{uuid.uuid4().hex}"]; collection = db["vendor_bill_commands"]; VendorBillCommandRegistry.ensure_indexes(collection); command = _command()
    def create(_):
        try: return VendorBillCommandRegistry.create_command(command, collection).outcome
        except Exception as error: return error
    with ThreadPoolExecutor(max_workers=32) as pool: outcomes = list(pool.map(create, range(100)))
    assert outcomes.count(VendorBillCommandCreateOutcome.CREATED) == 1 and outcomes.count(VendorBillCommandCreateOutcome.IDEMPOTENT_REPLAY) == 99 and collection.count_documents({}) == 1
    client.drop_database(db.name); client.close()

def test_vendor_bill_command_caller_transaction_abort_and_commit_real_mongo():
    client = MongoClient(os.environ["TEST_VENDOR_MONGO_URI"], serverSelectionTimeoutMS=5000, retryWrites=True); assert client.admin.command("hello")["isWritablePrimary"]
    db = client[f"vendor_bill_commands_tx_{uuid.uuid4().hex}"]; collection = db["vendor_bill_commands"]; VendorBillCommandRegistry.ensure_indexes(collection)
    with client.start_session() as session:
        session.start_transaction(); VendorBillCommandRegistry.create_command(_command(key="abort-key"), collection, session=session); session.abort_transaction()
    assert collection.count_documents({"idempotency_key": "abort-key"}) == 0
    with client.start_session() as session:
        session.start_transaction(); command = _command(key="commit-key"); VendorBillCommandRegistry.create_command(command, collection, session=session); session.commit_transaction()
    assert VendorBillCommandRegistry.get_by_idempotency_key("tenant-a", "payable-a", "commit-key", collection) == command
    assert VendorBillCommandRegistry.get_by_sequence("tenant-a", "payable-a", 1, collection) == command
    client.drop_database(db.name); client.close()
