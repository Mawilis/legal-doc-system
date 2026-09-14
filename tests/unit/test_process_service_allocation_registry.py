"""Direct adversarial certificate for the Legal P4B allocation registry.

TITLE: Wilsy OS Process Service Allocation Registry Certificate
VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify immutable P4A allocation receipts, explicit current-pointer
         CAS, strict durable hydration, replay, tenant scope, and transaction
         ownership without a Mongo runtime.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_process_service_allocation_registry.py
COLLABORATION / OWNERSHIP: Direct P4B unit certificate; P1 remains lifecycle
                            authority, P2 remains evidence persistence,
                            P3 remains assignment authority, and a future P4A
                            caller owns allocation orchestration.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.0-PROCESS-SERVICE-ALLOCATION-REGISTRY-CERT
           certifies deterministic receipt/current schemas, replay, CAS,
           corruption rejection, and caller-owned transaction semantics.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Every fake query is tenant/document scoped; foreign records
                 are never treated as visible evidence.
AUTHORITY BOUNDARY: Persistence/currentness evidence only; this certificate
                    creates no allocation, custody, service, or transport
                    authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; no invoice, payment, or paid
                              state is represented here.
FAIL-CLOSED DECLARATION: Invalid values, schemas, digests, races, outages,
                         currentness, and transaction ownership fail closed.
"""
from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Any, Callable

import pytest
from pymongo.errors import AutoReconnect, DuplicateKeyError, OperationFailure

from tools.eos.legal_operations.registry import process_service_allocation_registry as registry


VERSION = "v1.0.0-PROCESS-SERVICE-ALLOCATION-REGISTRY-CERT"
BASE = datetime(2026, 9, 13, 9, 0, tzinfo=timezone.utc)
TENANT = "tenant-p4b-certificate"
OTHER_TENANT = "tenant-p4b-other"
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
HEX_D = "d" * 128
HEX_E = "e" * 128
HEX_F = "f" * 128
HEX_0 = "0" * 128


class _Cursor:
    """Minimal deterministic Mongo-like cursor with bounded ``limit``."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self._rows = rows

    def limit(self, amount: int) -> "_Cursor":
        return _Cursor(self._rows[:amount])

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self._rows)


class _WriteResult:
    def __init__(self, matched_count: int) -> None:
        self.matched_count = matched_count


class _Session:
    """Caller-owned transaction marker that explodes on lifecycle takeover."""

    def __init__(self, state: bool | Callable[[], bool] = True) -> None:
        self.in_transaction = state

    def start_transaction(self) -> None:
        raise AssertionError("P4B must not start transactions")

    def commit_transaction(self) -> None:
        raise AssertionError("P4B must not commit transactions")

    def abort_transaction(self) -> None:
        raise AssertionError("P4B must not abort transactions")


class _FakeCollection:
    """Small equality-query fake preserving session and write semantics."""

    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self.rows = [dict(row) for row in (rows or [])]
        self.indexes: list[dict[str, Any]] = []
        self.find_calls: list[tuple[dict[str, Any], object]] = []
        self.insert_calls: list[tuple[dict[str, Any], object]] = []
        self.update_calls: list[tuple[dict[str, Any], dict[str, Any], object]] = []
        self.find_error: Exception | None = None
        self.insert_error: Exception | None = None
        self.update_error: Exception | None = None
        self.force_duplicate_insert = False
        self.force_update_miss = False

    @staticmethod
    def _matches(row: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def create_index(self, keys: list[tuple[str, int]], *, unique: bool, name: str) -> str:
        self.indexes.append({"key": keys, "unique": unique, "name": name})
        return name

    def find(self, query: dict[str, Any], *, session: object) -> _Cursor:
        self.find_calls.append((dict(query), session))
        if self.find_error is not None:
            raise self.find_error
        return _Cursor([dict(row) for row in self.rows if self._matches(row, query)])

    def insert_one(self, row: dict[str, Any], *, session: object) -> object:
        self.insert_calls.append((dict(row), session))
        if self.insert_error is not None:
            raise self.insert_error
        if self.force_duplicate_insert:
            raise DuplicateKeyError("duplicate race")
        self.rows.append(dict(row))
        return object()

    def update_one(self, query: dict[str, Any], update: dict[str, Any], *, session: object) -> _WriteResult:
        self.update_calls.append((dict(query), dict(update), session))
        if self.update_error is not None:
            raise self.update_error
        if self.force_update_miss:
            return _WriteResult(0)
        for index, row in enumerate(self.rows):
            if self._matches(row, query):
                replacement = dict(row)
                replacement.update(dict(update.get("$set", {})))
                self.rows[index] = replacement
                return _WriteResult(1)
        return _WriteResult(0)


def _receipt(**changes: Any) -> registry.ProcessServiceAllocationReceipt:
    """Build one valid immutable receipt with deterministic evidence."""
    values: dict[str, Any] = {
        "tenant_id": TENANT,
        "allocation_command_id": "allocation-command-1",
        "idempotency_key": "idempotency-1",
        "instruction_id": "instruction-1",
        "case_matter_id": "matter-1",
        "document_id": "document-1",
        "district_id": "district-1",
        "sheriff_office_id": "office-1",
        "deputy_id": "deputy-1",
        "assignment_decision_id": "assignment-1",
        "assignment_decision_fingerprint": HEX_A,
        "source_instruction_fingerprint": HEX_B,
        "source_document_fingerprint": HEX_C,
        "source_district_fingerprint": HEX_D,
        "source_sheriff_office_fingerprint": HEX_E,
        "source_deputy_fingerprint": HEX_F,
        "prior_custody_chain_fingerprint": HEX_0,
        "prior_custody_head_event_id": "custody-head-1",
        "prior_custody_head_fingerprint": HEX_A,
        "prior_custody_head_sequence_number": 7,
        "from_holder_reference": "office-holder-1",
        "to_holder_reference": "deputy-holder-1",
        "allocation_custody_event_id": "custody-allocation-1",
        "allocation_evidence_reference": "allocation-evidence-1",
        "allocated_at": BASE + timedelta(minutes=5),
        "allocated_document_fingerprint": HEX_B,
        "allocation_custody_event_fingerprint": HEX_C,
        "result_custody_chain_fingerprint": HEX_D,
    }
    values.update(changes)
    return registry.ProcessServiceAllocationReceipt(**values)


def _prior(receipt: registry.ProcessServiceAllocationReceipt) -> registry.ProcessServiceAllocationCurrent:
    return registry.ProcessServiceAllocationCurrent(
        tenant_id=receipt.tenant_id,
        document_id=receipt.document_id,
        process_document_fingerprint=receipt.source_document_fingerprint,
        custody_chain_fingerprint=receipt.prior_custody_chain_fingerprint,
        custody_head_event_id=receipt.prior_custody_head_event_id,
        custody_head_fingerprint=receipt.prior_custody_head_fingerprint,
        custody_head_sequence_number=receipt.prior_custody_head_sequence_number,
        current_holder_reference=receipt.from_holder_reference,
        authority_evidence_reference="migration-head-1",
        authority_evidence_fingerprint=HEX_E,
    )


def _record(receipt: registry.ProcessServiceAllocationReceipt) -> dict[str, Any]:
    return dict(registry._record_for(receipt))  # type: ignore[attr-defined]


def _next(receipt: registry.ProcessServiceAllocationReceipt) -> registry.ProcessServiceAllocationCurrent:
    return registry.ProcessServiceAllocationCurrent(
        tenant_id=receipt.tenant_id,
        document_id=receipt.document_id,
        process_document_fingerprint=receipt.allocated_document_fingerprint,
        custody_chain_fingerprint=receipt.result_custody_chain_fingerprint,
        custody_head_event_id=receipt.allocation_custody_event_id,
        custody_head_fingerprint=receipt.allocation_custody_event_fingerprint,
        custody_head_sequence_number=receipt.prior_custody_head_sequence_number + 1,
        current_holder_reference=receipt.to_holder_reference,
        authority_evidence_reference=receipt.allocation_command_id,
        authority_evidence_fingerprint=receipt.fingerprint,
    )


def _persist(
    receipt: registry.ProcessServiceAllocationReceipt,
    prior: registry.ProcessServiceAllocationCurrent,
    receipts: _FakeCollection,
    current: _FakeCollection,
    session: object | None = None,
) -> registry.ProcessServiceAllocationPersistenceResult:
    return registry.persist_receipt_and_advance_current(
        receipt, prior, receipts, current, session=session or _Session()
    )


def test_receipt_crypto_contract_and_result_separation() -> None:
    receipt = _receipt()
    assert registry.VERSION == "v1.0.0-PROCESS-SERVICE-ALLOCATION-REGISTRY"
    assert receipt.to_dict()["schema"] == registry.RECEIPT_SCHEMA
    assert receipt.to_dict()["version"] == registry.VERSION
    assert receipt.to_dict()["entity_type"] == "ProcessServiceAllocationReceipt"
    for value in (receipt.command_fingerprint, receipt.fingerprint, receipt.evidence_identity):
        assert isinstance(value, str) and len(value) == 128 and value == value.lower()
        int(value, 16)
    changed_command = replace(receipt, to_holder_reference="deputy-holder-2")
    changed_result = replace(receipt, result_custody_chain_fingerprint=HEX_E)
    assert changed_command.command_fingerprint != receipt.command_fingerprint
    assert changed_result.command_fingerprint == receipt.command_fingerprint
    assert changed_result.fingerprint != receipt.fingerprint
    assert "command_fingerprint" in receipt.to_dict()
    assert "fingerprint" in receipt.to_dict()
    canonical_payload = receipt.to_dict()
    canonical_payload.pop("fingerprint")
    canonical = json.dumps(canonical_payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":"))
    assert hashlib.sha3_512(canonical.encode()).hexdigest() == receipt.fingerprint


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("allocated_at", BASE.replace(tzinfo=None)),
        ("allocated_at", BASE.replace(tzinfo=timezone(timedelta(hours=2)))),
        ("assignment_decision_fingerprint", "x" * 128),
        ("assignment_decision_fingerprint", "A" * 128),
        ("assignment_decision_fingerprint", "short"),
        ("tenant_id", "global"),
        ("allocation_command_id", "bad/id"),
        ("prior_custody_head_sequence_number", 0),
        ("prior_custody_head_sequence_number", -1),
        ("prior_custody_head_sequence_number", True),
        ("from_holder_reference", None),
        ("from_holder_reference", " "),
        ("to_holder_reference", ""),
    ),
)
def test_receipt_input_validation_fails_closed(field: str, value: Any) -> None:
    with pytest.raises(registry.ProcessServiceAllocationRegistryInputError):
        _receipt(**{field: value})


def test_caller_cannot_assert_receipt_or_command_fingerprints() -> None:
    with pytest.raises(TypeError):
        registry.ProcessServiceAllocationReceipt(**_receipt().to_dict())  # type: ignore[reportArgumentType]


def test_current_pointer_contract() -> None:
    pointer = _prior(_receipt())
    payload = pointer.to_dict()
    assert payload["schema"] == registry.CURRENT_SCHEMA
    assert payload["version"] == registry.VERSION
    assert payload["entity_type"] == "ProcessServiceAllocationCurrent"
    with pytest.raises(registry.ProcessServiceAllocationRegistryInputError):
        replace(pointer, custody_head_sequence_number=0)
    with pytest.raises(registry.ProcessServiceAllocationRegistryInputError):
        replace(pointer, authority_evidence_reference="")


def test_indexes_are_exactly_four_unique_primitives() -> None:
    receipts = _FakeCollection()
    current = _FakeCollection()
    registry.ensure_indexes(receipts, current)
    assert len(receipts.indexes) == 3
    assert len(current.indexes) == 1
    assert all(item["unique"] for item in receipts.indexes + current.indexes)
    assert [item["key"] for item in receipts.indexes] == [
        [("tenant_id", 1), ("allocation_command_id", 1)],
        [("tenant_id", 1), ("document_id", 1), ("idempotency_key", 1)],
        [("tenant_id", 1), ("allocation_custody_event_id", 1)],
    ]
    assert current.indexes[0]["key"] == [("tenant_id", 1), ("document_id", 1)]


@pytest.mark.parametrize("session", (None, _Session(False), _Session(lambda: False)))
def test_all_runtime_operations_require_active_transaction(session: object | None) -> None:
    with pytest.raises(registry.ProcessServiceAllocationRegistryTransactionRequiredError):
        registry.get_current(TENANT, "document-1", _FakeCollection(), session=session)


@pytest.mark.parametrize("session", (_Session(True), _Session(lambda: True)))
def test_active_transaction_markers_and_session_forwarding(session: _Session) -> None:
    receipt = _receipt()
    receipts = _FakeCollection()
    current = _FakeCollection([_prior(receipt).to_dict()])
    result = _persist(receipt, _prior(receipt), receipts, current, session)
    assert result.outcome is registry.ProcessServiceAllocationPersistenceOutcome.CREATED
    assert all(call[1] is session for call in receipts.find_calls)
    assert all(call[1] is session for call in current.find_calls)
    assert receipts.insert_calls[0][1] is session
    assert current.update_calls[0][2] is session


def test_get_current_hydrates_missing_duplicate_and_corrupt_as_persisted_errors() -> None:
    receipt = _receipt()
    pointer = _prior(receipt)
    with pytest.raises(registry.ProcessServiceAllocationRegistryCurrentPointerMissingError):
        registry.get_current(TENANT, receipt.document_id, _FakeCollection(), session=_Session())
    duplicate = _FakeCollection([pointer.to_dict(), pointer.to_dict()])
    with pytest.raises(registry.ProcessServiceAllocationRegistryMultipleCurrentPointerError):
        registry.get_current(TENANT, receipt.document_id, duplicate, session=_Session())
    corrupt = pointer.to_dict()
    corrupt["custody_head_sequence_number"] = 0
    with pytest.raises(registry.ProcessServiceAllocationRegistryPersistedRecordInvalidError):
        registry.get_current(TENANT, receipt.document_id, _FakeCollection([corrupt]), session=_Session())
    missing = pointer.to_dict()
    del missing["authority_evidence_fingerprint"]
    with pytest.raises(registry.ProcessServiceAllocationRegistryPersistedRecordInvalidError):
        registry.get_current(TENANT, receipt.document_id, _FakeCollection([missing]), session=_Session())


def test_receipt_lookup_replay_schema_and_hydration_corruption() -> None:
    receipt = _receipt()
    valid = _FakeCollection([_record(receipt)])
    assert registry.get_receipt_by_idempotency_key(TENANT, receipt.document_id, receipt.idempotency_key, valid, session=_Session()) == receipt
    assert registry.get_receipt_by_idempotency_key(OTHER_TENANT, receipt.document_id, receipt.idempotency_key, valid, session=_Session()) is None
    duplicate = _FakeCollection([_record(receipt), _record(receipt)])
    with pytest.raises(registry.ProcessServiceAllocationRegistryPersistedRecordInvalidError):
        registry.get_receipt_by_idempotency_key(TENANT, receipt.document_id, receipt.idempotency_key, duplicate, session=_Session())
    for mutate in (
        lambda row: row.pop("receipt_fingerprint"),
        lambda row: row.__setitem__("command_fingerprint", HEX_F),
        lambda row: row.__setitem__("evidence_identity", HEX_F),
        lambda row: row["receipt_payload"].__setitem__("to_holder_reference", ""),
        lambda row: row.__setitem__("unexpected", True),
    ):
        corrupt = _record(receipt)
        mutate(corrupt)
        with pytest.raises(registry.ProcessServiceAllocationRegistryPersistedRecordInvalidError):
            registry.get_receipt_by_idempotency_key(TENANT, receipt.document_id, receipt.idempotency_key, _FakeCollection([corrupt]), session=_Session())


def test_created_happy_path_derives_and_cas_advances_current() -> None:
    receipt = _receipt()
    prior = _prior(receipt)
    receipts = _FakeCollection()
    current = _FakeCollection([prior.to_dict()])
    result = _persist(receipt, prior, receipts, current)
    assert result.outcome is registry.ProcessServiceAllocationPersistenceOutcome.CREATED
    assert result.receipt == receipt
    assert result.current == _next(receipt)
    assert len(receipts.insert_calls) == 1
    assert len(current.update_calls) == 1
    query, update, _ = current.update_calls[0]
    assert query == prior.to_dict()
    assert update == {"$set": _next(receipt).to_dict()}
    inserted = receipts.insert_calls[0][0]
    assert inserted["command_fingerprint"] == receipt.command_fingerprint
    assert inserted["receipt_fingerprint"] == receipt.fingerprint
    assert inserted["evidence_identity"] == receipt.evidence_identity
    assert result.current.custody_head_sequence_number == prior.custody_head_sequence_number + 1


def test_exact_replay_is_first_and_performs_no_writes() -> None:
    receipt = _receipt()
    prior = _prior(receipt)
    receipts = _FakeCollection([_record(receipt)])
    current = _FakeCollection([_next(receipt).to_dict()])
    result = _persist(receipt, prior, receipts, current)
    assert result.outcome is registry.ProcessServiceAllocationPersistenceOutcome.IDEMPOTENT_REPLAY
    assert result.receipt == receipt
    assert result.current == _next(receipt)
    assert receipts.insert_calls == []
    assert current.update_calls == []


def test_divergent_idempotency_and_replay_pointer_correlation_fail_closed() -> None:
    receipt = _receipt()
    prior = _prior(receipt)
    divergent = replace(receipt, to_holder_reference="different-holder")
    with pytest.raises(registry.ProcessServiceAllocationRegistryIdempotencyConflictError):
        _persist(divergent, prior, _FakeCollection([_record(receipt)]), _FakeCollection([_next(receipt).to_dict()]))
    broken_current = replace(_next(receipt), current_holder_reference="wrong-holder")
    with pytest.raises(registry.ProcessServiceAllocationRegistryReceiptPointerCorrelationError):
        _persist(receipt, prior, _FakeCollection([_record(receipt)]), _FakeCollection([broken_current.to_dict()]))


def test_command_identity_conflict_hydrates_existing_row_without_writes() -> None:
    receipt = _receipt()
    prior = _prior(receipt)
    existing = replace(receipt, idempotency_key="other-key")
    receipts = _FakeCollection([_record(existing)])
    current = _FakeCollection([prior.to_dict()])
    with pytest.raises(registry.ProcessServiceAllocationRegistryAllocationCommandConflictError):
        _persist(receipt, prior, receipts, current)
    assert receipts.insert_calls == []
    assert current.update_calls == []


def test_custody_event_identity_conflict_is_dedicated() -> None:
    receipt = _receipt()
    prior = _prior(receipt)
    existing = replace(receipt, allocation_command_id="other-command", idempotency_key="other-key")
    receipts = _FakeCollection([_record(existing)])
    current = _FakeCollection([prior.to_dict()])
    with pytest.raises(registry.ProcessServiceAllocationRegistryCustodyEventConflictError) as raised:
        _persist(receipt, prior, receipts, current)
    assert str(raised.value) == "P4_ALLOCATION_CUSTODY_EVENT_IDENTITY_CONFLICT"
    assert receipts.insert_calls == []
    assert current.update_calls == []


def test_insert_duplicate_key_is_whole_transaction_retry() -> None:
    receipt = _receipt()
    prior = _prior(receipt)
    receipts = _FakeCollection()
    receipts.force_duplicate_insert = True
    with pytest.raises(registry.ProcessServiceAllocationRegistryRetryRequiredError):
        _persist(receipt, prior, receipts, _FakeCollection([prior.to_dict()]))


def test_update_duplicate_key_and_cas_miss_are_retry_required() -> None:
    receipt = _receipt()
    prior = _prior(receipt)
    current = _FakeCollection([prior.to_dict()])
    current.update_error = DuplicateKeyError("pointer race")
    with pytest.raises(registry.ProcessServiceAllocationRegistryRetryRequiredError):
        _persist(receipt, prior, _FakeCollection(), current)
    current = _FakeCollection([prior.to_dict()])
    current.force_update_miss = True
    with pytest.raises(registry.ProcessServiceAllocationRegistryRetryRequiredError):
        _persist(receipt, prior, _FakeCollection(), current)


@pytest.mark.parametrize("field", (
    "process_document_fingerprint", "custody_chain_fingerprint", "custody_head_event_id",
    "custody_head_fingerprint", "custody_head_sequence_number", "current_holder_reference",
))
def test_prior_current_and_receipt_correlation_reject_before_writes(field: str) -> None:
    receipt = _receipt()
    prior = _prior(receipt)
    changed = replace(
        prior,
        **{
            field: (
                prior.custody_head_sequence_number + 1
                if field == "custody_head_sequence_number"
                else HEX_F
                if "fingerprint" in field
                else "different"
            )
        },
    )
    receipts = _FakeCollection()
    current = _FakeCollection([changed.to_dict()])
    with pytest.raises(registry.ProcessServiceAllocationRegistryCurrentPointerConflictError):
        _persist(receipt, prior, receipts, current)
    assert receipts.insert_calls == []


@pytest.mark.parametrize("field", (
    "source_document_fingerprint", "prior_custody_chain_fingerprint", "prior_custody_head_event_id",
    "prior_custody_head_fingerprint", "prior_custody_head_sequence_number", "from_holder_reference",
))
def test_receipt_prior_correlation_rejects_before_writes(field: str) -> None:
    receipt = _receipt()
    prior = _prior(receipt)
    changed = replace(
        receipt,
        **{
            field: (
                receipt.prior_custody_head_sequence_number + 1
                if field == "prior_custody_head_sequence_number"
                else HEX_F
                if "fingerprint" in field
                else "different"
            )
        },
    )
    receipts = _FakeCollection()
    with pytest.raises(registry.ProcessServiceAllocationRegistryReceiptPointerCorrelationError):
        _persist(changed, prior, receipts, _FakeCollection([prior.to_dict()]))
    assert receipts.insert_calls == []


def test_missing_current_pointer_never_bootstraps() -> None:
    receipt = _receipt()
    receipts = _FakeCollection()
    with pytest.raises(registry.ProcessServiceAllocationRegistryCurrentPointerMissingError):
        _persist(receipt, _prior(receipt), receipts, _FakeCollection())
    assert receipts.insert_calls == []


@pytest.mark.parametrize("operation", ("get", "lookup", "create"))
def test_persistence_failures_are_governed(operation: str) -> None:
    receipt = _receipt()
    if operation == "get":
        collection = _FakeCollection()
        collection.find_error = AutoReconnect("read unavailable")
        with pytest.raises(registry.ProcessServiceAllocationRegistryPersistenceUnavailableError):
            registry.get_current(TENANT, receipt.document_id, collection, session=_Session())
    elif operation == "lookup":
        collection = _FakeCollection()
        collection.find_error = OperationFailure("read unavailable")
        with pytest.raises(registry.ProcessServiceAllocationRegistryPersistenceUnavailableError):
            registry.get_receipt_by_idempotency_key(TENANT, receipt.document_id, receipt.idempotency_key, collection, session=_Session())
    else:
        receipts = _FakeCollection()
        receipts.insert_error = AutoReconnect("write unavailable")
        with pytest.raises(registry.ProcessServiceAllocationRegistryPersistenceUnavailableError):
            _persist(receipt, _prior(receipt), receipts, _FakeCollection([_prior(receipt).to_dict()]))


def test_public_api_is_minimal_and_transaction_free() -> None:
    forbidden = {
        "TransactionRequiredError", "PersistedRecordInvalidError", "IdempotencyConflictError",
        "CurrentPointerConflictError", "RetryRequiredError", "bootstrap", "seed", "get_latest",
        "history", "allocate", "create_service_attempt", "execute", "settle",
    }
    assert forbidden.isdisjoint(set(registry.__all__))
    assert not any(hasattr(registry.ProcessServiceAllocationRegistry, name) for name in forbidden)
    assert "ProcessServiceAllocationRegistryCustodyEventConflictError" in registry.__all__
    source = registry.ProcessServiceAllocationRegistry
    assert not any(name in dir(source) for name in ("start_transaction", "commit_transaction", "abort_transaction"))


def test_result_and_receipt_are_immutable_and_financially_neutral() -> None:
    receipt = _receipt()
    result = _persist(receipt, _prior(receipt), _FakeCollection(), _FakeCollection([_prior(receipt).to_dict()]))
    with pytest.raises(FrozenInstanceError):
        result.receipt.tenant_id = OTHER_TENANT  # type: ignore[misc]
    forbidden_fields = {"invoice", "payment", "settlement", "paid_state", "billing_execution", "service_execution"}
    serialized = json.dumps(result.to_dict()).lower()
    assert forbidden_fields.isdisjoint(serialized)


# ARTIFACT: test_process_service_allocation_registry.py
# VERSION: v1.0.0-PROCESS-SERVICE-ALLOCATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct P4B persistence/currentness certificate only.
# TENANT POSTURE: explicit tenant/document scoping; no foreign disclosure.
# FAIL-CLOSED POSTURE: malformed evidence, replay divergence, races, and outages reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns execution and settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
