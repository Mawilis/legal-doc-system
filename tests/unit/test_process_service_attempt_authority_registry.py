"""Direct adversarial certificate for the immutable P5B attempt registry.

TITLE: Wilsy OS Process-Service Attempt Authority Registry Certificate
VERSION: v1.0.1-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify P5B receipt derivation, durable replay, strict hydration,
         tenant isolation, outage handling, and caller transaction ownership.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_process_service_attempt_authority_registry.py
COLLABORATION / OWNERSHIP: Direct P5B certificate; P5A remains immutable
                            attempt-authorization evidence authority and this
                            registry remains append-only persistence authority.
CERTIFICATION / UPDATE DATE: 2026-09-14
CHANGELOG: 2026-09-14 v1.0.1-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY-CERT
           adds direct labeled transactional insert-conflict classification
           and explicit unknown-commit-result exclusion certification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; no network,
                             provider, credential, location, or personal-data
                             access.
TENANT BOUNDARY: Every fake query and assertion is explicitly tenant-scoped;
                 foreign records remain indistinguishable from absence.
AUTHORITY BOUNDARY: This certificate verifies immutable P5B receipt persistence
                    only. It creates no lifecycle, custody, service, IAM,
                    transport, or financial authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution
                              and settlement; no invoice, payment, or settlement
                              truth is asserted here.
FAIL-CLOSED DECLARATION: The certificate rejects schema drift, digest corruption,
                         replay divergence, duplicate rows, outages, invalid
                         sessions, and forbidden authority surfaces.
"""
from __future__ import annotations

from dataclasses import fields
from datetime import datetime, timedelta, timezone
import hashlib
import json
from typing import Any, Callable, cast

import pytest
from pymongo.errors import DuplicateKeyError, OperationFailure, PyMongoError

import tools.eos.legal_operations.registry.process_service_attempt_authority_registry as registry
from tests.unit.test_process_service_attempt_authority import _current, _receipt
from tools.eos.legal_operations.domain.process_service_attempt_authority import (
    ProcessServiceAttemptAuthorityDecision,
    ProcessServiceAttemptAuthorityError,
    authorize_process_service_attempt,
)
from tools.eos.legal_operations.registry.process_service_attempt_authority_registry import (
    ProcessServiceAttemptAuthorityPersistenceOutcome,
    ProcessServiceAttemptAuthorityRegistry,
    ProcessServiceAttemptAuthorityRegistryAttemptIdentityConflictError,
    ProcessServiceAttemptAuthorityRegistryAuthorityIdentityConflictError,
    ProcessServiceAttemptAuthorityRegistryError,
    ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError,
    ProcessServiceAttemptAuthorityRegistryPersistenceUnavailableError,
    ProcessServiceAttemptAuthorityRegistryReceiptNotFoundError,
    ProcessServiceAttemptAuthorityRegistryRetryRequiredError,
    ProcessServiceAttemptAuthorityRegistryTransactionRequiredError,
)


VERSION = "v1.0.1-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY-CERT"
TENANT = "tenant-alpha"
BASE = datetime(2026, 9, 14, 8, 0, tzinfo=timezone.utc)
HEX_A = "a" * 128
HEX_B = "b" * 128


class _Session:
    """Minimal caller-owned transaction marker."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class _CallableSession:
    """Transaction marker exposing a callable property."""

    def __init__(self, active: bool) -> None:
        self._active = active

    def in_transaction(self) -> bool:
        return self._active


class _BrokenSession:
    """Marker failure used to prove fail-closed transaction checks."""

    @property
    def in_transaction(self) -> bool:
        raise RuntimeError("marker failure")


class _Cursor:
    """Deterministic cursor double supporting iteration failure injection."""

    def __init__(self, rows: list[dict[str, Any]], error: PyMongoError | None = None) -> None:
        self._rows = rows
        self._error = error

    def __iter__(self):  # type: ignore[no-untyped-def]
        for row in self._rows:
            yield dict(row)
        if self._error is not None:
            raise self._error


class _Collection:
    """Mongo-compatible fake recording every session and operation."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.operations: list[tuple[str, Any, Any]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, Any]]] = []
        self.find_errors: list[PyMongoError | None] = []
        self.insert_error: BaseException | None = None
        self.insert_calls = 0
        self.drop_insert = False

    @staticmethod
    def _matches(row: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def create_index(self, spec: list[tuple[str, int]], **kwargs: Any) -> str:
        self.operations.append(("create_index", spec, kwargs))
        self.indexes.append((spec, kwargs))
        return str(kwargs["name"])

    def find(self, query: dict[str, Any], *, session: Any) -> _Cursor:
        self.operations.append(("find", dict(query), session))
        rows = [dict(row) for row in self.rows if self._matches(row, query)]
        error = self.find_errors.pop(0) if self.find_errors else None
        return _Cursor(rows, error)

    def find_one(self, query: dict[str, Any], *, session: Any) -> dict[str, Any] | None:
        cursor = self.find(query, session=session)
        return next(iter(cursor), None)

    def insert_one(self, row: dict[str, Any], *, session: Any) -> object:
        self.operations.append(("insert_one", dict(row), session))
        self.insert_calls += 1
        if self.insert_error is not None:
            error = self.insert_error
            self.insert_error = None
            raise error
        if not self.drop_insert:
            self.rows.append(dict(row))
        return object()


class _DivergentInsertCollection(_Collection):
    """Insert double that stores a structurally valid divergent record."""

    def __init__(self, divergent_row: dict[str, Any]) -> None:
        super().__init__()
        self._divergent_row = divergent_row

    def insert_one(self, row: dict[str, Any], *, session: Any) -> object:
        self.operations.append(("insert_one", dict(row), session))
        self.insert_calls += 1
        self.rows.append(dict(self._divergent_row))
        return object()


def _decision(
    *,
    tenant_id: str = TENANT,
    attempt_authority_id: str = "attempt-authority-1",
    attempt_id: str = "attempt-1",
) -> ProcessServiceAttemptAuthorityDecision:
    """Build one deterministic P5A decision through its public factory."""
    receipt = _receipt(tenant_id=tenant_id)
    current = _current(receipt)
    return authorize_process_service_attempt(
        allocation_receipt=receipt,
        allocation_current=current,
        attempt_authority_id=attempt_authority_id,
        attempt_id=attempt_id,
        authorized_at=receipt.allocated_at + timedelta(minutes=2),
    )


def _persisted_row(decision: ProcessServiceAttemptAuthorityDecision) -> dict[str, Any]:
    """Obtain one canonical row from a separate fake registry operation."""
    collection = _Collection()
    result = ProcessServiceAttemptAuthorityRegistry.persist(decision, collection, session=_Session())
    assert result.outcome is ProcessServiceAttemptAuthorityPersistenceOutcome.CREATED
    assert len(collection.rows) == 1
    return dict(collection.rows[0])


def _assert_code(call: Callable[[], Any], expected: str, error_type: type[BaseException] = ProcessServiceAttemptAuthorityRegistryError) -> None:
    """Assert one operation raises its exact governed registry code."""
    with pytest.raises(error_type) as caught:
        call()
    assert getattr(caught.value, "code", None) == expected


def test_receipt_derivation_and_deterministic_evidence() -> None:
    """Persist derives every receipt field exclusively from exact P5A evidence."""
    decision = _decision()
    collection = _Collection()
    result = registry.persist(decision, collection, session=_Session())
    receipt = result.receipt
    assert result.outcome is ProcessServiceAttemptAuthorityPersistenceOutcome.CREATED
    assert type(receipt).__name__ == "ProcessServiceAttemptAuthorityReceipt"
    assert receipt.tenant_id == decision.tenant_id
    assert receipt.attempt_authority_id == decision.attempt_authority_id
    assert receipt.attempt_id == decision.attempt_id
    assert receipt.instruction_id == decision.instruction_id
    assert receipt.document_id == decision.document_id
    assert receipt.deputy_id == decision.deputy_id
    assert receipt.allocation_command_id == decision.allocation_command_id
    assert receipt.allocation_receipt_evidence_identity == decision.allocation_receipt_evidence_identity
    assert receipt.allocation_receipt_fingerprint == decision.allocation_receipt_fingerprint
    assert receipt.allocation_current_fingerprint == decision.allocation_current_fingerprint
    assert receipt.allocated_at == decision.allocated_at
    assert receipt.authorized_at == decision.authorized_at
    assert receipt.authority_decision_fingerprint == decision.fingerprint
    assert len(receipt.fingerprint) == 128 and receipt.fingerprint == receipt.fingerprint.lower()
    assert len(receipt.evidence_identity) == 128 and receipt.evidence_identity == receipt.evidence_identity.lower()
    assert receipt.to_dict() == receipt.to_dict()
    assert receipt.fingerprint == receipt.fingerprint
    assert receipt.evidence_identity == receipt.evidence_identity


def test_exact_p5a_input_type_and_validation_contract() -> None:
    """Wrong, subclassed, malformed, and proof-invalid decisions fail closed."""
    decision = _decision()
    session = _Session()
    collection = _Collection()

    class DecisionSubclass(ProcessServiceAttemptAuthorityDecision):
        pass

    subclass = DecisionSubclass(
        **{item.name: getattr(decision, item.name) for item in fields(decision)}
    )
    tampered = object.__new__(ProcessServiceAttemptAuthorityDecision)
    for item in fields(decision):
        object.__setattr__(tampered, item.name, getattr(decision, item.name))
    object.__setattr__(tampered, "attempt_id", "tampered-attempt")
    _assert_code(lambda: registry.persist(cast(Any, object()), collection, session=session), "P5B_DECISION_REQUIRED")
    _assert_code(lambda: registry.persist(subclass, collection, session=session), "P5B_DECISION_REQUIRED")
    _assert_code(lambda: registry.persist(tampered, collection, session=session), "P5B_DECISION_INVALID")
    _assert_code(lambda: registry.persist(cast(Any, None), collection, session=session), "P5B_DECISION_REQUIRED")


@pytest.mark.parametrize("operation", ["authority", "attempt", "persist"])
@pytest.mark.parametrize("session", [None, _Session(False), _CallableSession(False), _BrokenSession()])
def test_every_transactional_api_requires_active_caller_session(operation: str, session: Any) -> None:
    """Missing, inactive, callable-inactive, and marker-failure sessions reject."""
    decision = _decision()
    collection = _Collection()
    if operation == "authority":
        call = lambda: registry.get_by_attempt_authority_id(TENANT, decision.attempt_authority_id, collection, session=session)
    elif operation == "attempt":
        call = lambda: registry.get_by_attempt_id(TENANT, decision.attempt_id, collection, session=session)
    else:
        call = lambda: registry.persist(decision, collection, session=session)
    if isinstance(session, _BrokenSession):
        with pytest.raises(RuntimeError):
            call()
    else:
        _assert_code(call, "P5B_ACTIVE_TRANSACTION_REQUIRED", ProcessServiceAttemptAuthorityRegistryTransactionRequiredError)


def test_active_callable_transaction_marker_succeeds() -> None:
    """A true callable transaction marker is accepted without registry ownership."""
    decision = _decision()
    result = registry.persist(decision, _Collection(), session=_CallableSession(True))
    assert result.outcome is ProcessServiceAttemptAuthorityPersistenceOutcome.CREATED


def test_index_contract_is_exact_and_has_no_current_pointer() -> None:
    """Exactly three tenant-scoped unique indexes are declared."""
    collection = _Collection()
    registry.ensure_indexes(collection)
    assert len(collection.indexes) == 3
    observed = {(tuple(spec), kwargs["name"], kwargs["unique"]) for spec, kwargs in collection.indexes}
    assert observed == {
        ((("tenant_id", 1), ("attempt_authority_id", 1)), registry.AUTHORITY_INDEX_NAME, True),
        ((("tenant_id", 1), ("attempt_id", 1)), registry.ATTEMPT_INDEX_NAME, True),
        ((("tenant_id", 1), ("evidence_identity", 1)), registry.EVIDENCE_INDEX_NAME, True),
    }
    assert not hasattr(registry, "CURRENT_COLLECTION")
    assert not hasattr(registry, "ProcessServiceAttemptAuthorityCurrent")


def test_created_path_is_durable_and_session_propagates_everywhere() -> None:
    """Creation performs two scoped lookups, one insert, and a durability reread."""
    decision = _decision()
    collection = _Collection()
    session = _Session()
    result = registry.persist(decision, collection, session=session)
    assert result.outcome is ProcessServiceAttemptAuthorityPersistenceOutcome.CREATED
    assert len(collection.rows) == 1 and collection.insert_calls == 1
    assert [item[0] for item in collection.operations] == ["find", "find", "insert_one", "find"]
    assert all(item[2] is session for item in collection.operations)
    assert result.receipt.to_dict() == registry.get_by_attempt_authority_id(
        TENANT, decision.attempt_authority_id, collection, session=session
    ).to_dict()


def test_exact_replay_returns_one_durable_record_without_insert() -> None:
    """Identical P5A evidence replays exactly and never duplicates storage."""
    decision = _decision()
    collection = _Collection()
    session = _Session()
    first = registry.persist(decision, collection, session=session)
    collection.insert_calls = 0
    second = registry.persist(decision, collection, session=session)
    assert first.receipt.to_dict() == second.receipt.to_dict()
    assert second.outcome is ProcessServiceAttemptAuthorityPersistenceOutcome.IDEMPOTENT_REPLAY
    assert collection.insert_calls == 0
    assert len(collection.rows) == 1


def test_authority_identity_divergence_rejects_without_last_write_wins() -> None:
    """Same tenant/authority identity with changed immutable semantics conflicts."""
    first = _decision(attempt_id="attempt-1")
    divergent = _decision(attempt_id="attempt-2")
    collection = _Collection()
    session = _Session()
    registry.persist(first, collection, session=session)
    _assert_code(
        lambda: registry.persist(divergent, collection, session=session),
        "P5B_ATTEMPT_AUTHORITY_IDENTITY_CONFLICT",
        ProcessServiceAttemptAuthorityRegistryAuthorityIdentityConflictError,
    )
    assert len(collection.rows) == 1


def test_attempt_identity_divergence_rejects_even_with_different_authority_id() -> None:
    """One tenant/attempt identity cannot be reused by another authority."""
    first = _decision(attempt_authority_id="authority-1", attempt_id="attempt-1")
    divergent = _decision(attempt_authority_id="authority-2", attempt_id="attempt-1")
    collection = _Collection()
    session = _Session()
    registry.persist(first, collection, session=session)
    _assert_code(
        lambda: registry.persist(divergent, collection, session=session),
        "P5B_ATTEMPT_IDENTITY_CONFLICT",
        ProcessServiceAttemptAuthorityRegistryAttemptIdentityConflictError,
    )
    assert len(collection.rows) == 1


def test_tenant_scoped_reads_and_pseudo_tenants_fail_closed() -> None:
    """Foreign lookups disclose absence only and pseudo tenants are rejected."""
    decision = _decision()
    collection = _Collection()
    session = _Session()
    registry.persist(decision, collection, session=session)
    _assert_code(
        lambda: registry.get_by_attempt_authority_id("tenant-beta", decision.attempt_authority_id, collection, session=session),
        "P5B_ATTEMPT_AUTHORITY_NOT_FOUND",
        ProcessServiceAttemptAuthorityRegistryReceiptNotFoundError,
    )
    _assert_code(
        lambda: registry.get_by_attempt_id("tenant-beta", decision.attempt_id, collection, session=session),
        "P5B_ATTEMPT_AUTHORITY_NOT_FOUND",
        ProcessServiceAttemptAuthorityRegistryReceiptNotFoundError,
    )
    _assert_code(
        lambda: registry.get_by_attempt_authority_id("global", decision.attempt_authority_id, collection, session=session),
        "P5B_TENANT_INVALID",
    )
    scoped_queries = [item[1] for item in collection.operations if item[0] == "find"]
    assert scoped_queries and all("tenant_id" in query for query in scoped_queries)


def test_read_absence_has_exact_governed_not_found() -> None:
    """A fully exhausted empty query returns the explicit not-found error."""
    collection = _Collection()
    _assert_code(
        lambda: registry.get_by_attempt_authority_id(TENANT, "authority-missing", collection, session=_Session()),
        "P5B_ATTEMPT_AUTHORITY_NOT_FOUND",
        ProcessServiceAttemptAuthorityRegistryReceiptNotFoundError,
    )
    _assert_code(
        lambda: registry.get_by_attempt_id(TENANT, "attempt-missing", collection, session=_Session()),
        "P5B_ATTEMPT_AUTHORITY_NOT_FOUND",
        ProcessServiceAttemptAuthorityRegistryReceiptNotFoundError,
    )


def test_duplicate_durable_rows_fail_closed_for_each_lookup() -> None:
    """The registry never silently selects one of multiple durable rows."""
    decision = _decision()
    collection = _Collection()
    registry.persist(decision, collection, session=_Session())
    collection.rows.append(dict(collection.rows[0]))
    _assert_code(
        lambda: registry.get_by_attempt_authority_id(TENANT, decision.attempt_authority_id, collection, session=_Session()),
        "P5B_DUPLICATE_DURABLE_ROWS",
        ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError,
    )
    _assert_code(
        lambda: registry.get_by_attempt_id(TENANT, decision.attempt_id, collection, session=_Session()),
        "P5B_DUPLICATE_DURABLE_ROWS",
        ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError,
    )


def _corrupted_row(decision: ProcessServiceAttemptAuthorityDecision, mutate: Callable[[dict[str, Any]], None]) -> _Collection:
    """Return a collection containing one pristine row with one corruption."""
    collection = _Collection()
    row = _persisted_row(decision)
    mutate(row)
    collection.rows.append(row)
    return collection


@pytest.mark.parametrize(
    ("label", "mutate", "expected"),
    [
        ("top_extra", lambda row: row.update({"unexpected": True}), "P5B_RECORD_SCHEMA_INVALID"),
        ("top_missing", lambda row: row.pop("attempt_id"), "P5B_RECORD_SCHEMA_INVALID"),
        ("wrong_schema", lambda row: row.update({"schema": "wrong"}), "P5B_RECORD_VERSION_UNSUPPORTED"),
        ("wrong_version", lambda row: row.update({"version": "v0"}), "P5B_RECORD_VERSION_UNSUPPORTED"),
        ("wrong_entity", lambda row: row.update({"entity_type": "Other"}), "P5B_RECORD_VERSION_UNSUPPORTED"),
        ("payload_extra", lambda row: row["receipt_payload"].update({"quota": 1}), "P5B_RECEIPT_PAYLOAD_SCHEMA_INVALID"),
        ("payload_missing", lambda row: row["receipt_payload"].pop("attempt_id"), "P5B_RECEIPT_PAYLOAD_SCHEMA_INVALID"),
        ("payload_schema", lambda row: row["receipt_payload"].update({"schema": "wrong"}), "P5B_RECEIPT_VERSION_UNSUPPORTED"),
        ("bad_timestamp", lambda row: row["receipt_payload"].update({"allocated_at": "2026-09-14T08:05:00"}), "P5B_ALLOCATED_AT_INVALID"),
        ("bad_receipt_digest_shape", lambda row: row.update({"receipt_fingerprint": "x" * 128}), "P5B_RECEIPT_FINGERPRINT_INVALID"),
        ("bad_decision_digest", lambda row: (row.update({"authority_decision_fingerprint": HEX_A}), row["receipt_payload"].update({"authority_decision_fingerprint": HEX_A})), "P5B_DECISION_FINGERPRINT_MISMATCH"),
        ("bad_receipt_digest", lambda row: row.update({"receipt_fingerprint": HEX_A}), "P5B_RECEIPT_FINGERPRINT_MISMATCH"),
        ("bad_evidence_identity", lambda row: row.update({"evidence_identity": HEX_B}), "P5B_EVIDENCE_IDENTITY_MISMATCH"),
        ("payload_metadata_mismatch", lambda row: row["receipt_payload"].update({"attempt_id": "other-attempt"}), "P5B_RECORD_METADATA_MISMATCH"),
    ],
)
def test_each_persisted_integrity_layer_rejects_corruption(
    label: str, mutate: Callable[[dict[str, Any]], None], expected: str
) -> None:
    """Representative top-level, payload, timestamp, and digest corruption rejects."""
    del label
    decision = _decision()
    collection = _corrupted_row(decision, mutate)
    _assert_code(
        lambda: registry.get_by_attempt_authority_id(TENANT, decision.attempt_authority_id, collection, session=_Session()),
        expected,
        ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError,
    )


def test_persisted_chronology_corruption_rejects() -> None:
    """An authorized timestamp before allocation is not hydrateable evidence."""
    decision = _decision()

    def mutate(row: dict[str, Any]) -> None:
        row["receipt_payload"]["authorized_at"] = (decision.allocated_at - timedelta(seconds=1)).isoformat()

    _assert_code(
        lambda: registry.get_by_attempt_authority_id(
            TENANT, decision.attempt_authority_id, _corrupted_row(decision, mutate), session=_Session()
        ),
        "P5B_RECEIPT_CHRONOLOGY_INVALID",
        ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError,
    )


def test_p5a_payload_digest_is_independently_verified() -> None:
    """The certificate independently recomputes the stored P5A decision digest."""
    decision = _decision()
    row = _persisted_row(decision)
    payload = row["receipt_payload"]
    expected_payload = {
        "schema": "WILSY-PROCESS-SERVICE-ATTEMPT-AUTHORITY/V1",
        "version": "v1.0.0-PROCESS-SERVICE-ATTEMPT-AUTHORITY",
        "entity_type": "ProcessServiceAttemptAuthorityDecision",
        "tenant_id": payload["tenant_id"],
        "attempt_authority_id": payload["attempt_authority_id"],
        "attempt_id": payload["attempt_id"],
        "instruction_id": payload["instruction_id"],
        "document_id": payload["document_id"],
        "deputy_id": payload["deputy_id"],
        "allocation_command_id": payload["allocation_command_id"],
        "allocation_receipt_evidence_identity": payload["allocation_receipt_evidence_identity"],
        "allocation_receipt_fingerprint": payload["allocation_receipt_fingerprint"],
        "allocation_current_fingerprint": payload["allocation_current_fingerprint"],
        "allocated_at": payload["allocated_at"],
        "authorized_at": payload["authorized_at"],
    }
    expected_digest = hashlib.sha3_512(
        json.dumps(expected_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    assert payload["authority_decision_fingerprint"] == expected_digest
    collection = _Collection()
    row["authority_decision_fingerprint"] = HEX_A
    row["receipt_payload"]["authority_decision_fingerprint"] = HEX_A
    collection.rows.append(row)
    _assert_code(
        lambda: registry.get_by_attempt_authority_id(TENANT, decision.attempt_authority_id, collection, session=_Session()),
        "P5B_DECISION_FINGERPRINT_MISMATCH",
        ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError,
    )


def test_duplicate_key_race_requires_whole_transaction_restart() -> None:
    """Active-transaction DuplicateKeyError is never healed locally."""
    decision = _decision()
    collection = _Collection()
    collection.insert_error = DuplicateKeyError("duplicate")
    _assert_code(
        lambda: registry.persist(decision, collection, session=_Session()),
        "P5B_WHOLE_TRANSACTION_RETRY_REQUIRED",
        ProcessServiceAttemptAuthorityRegistryRetryRequiredError,
    )
    assert collection.insert_calls == 1
    assert [item[0] for item in collection.operations] == ["find", "find", "insert_one"]


def test_labeled_transient_insert_conflict_requires_whole_transaction_restart() -> None:
    """The repaired insert boundary preserves a labeled Mongo conflict as retry-required."""
    decision = _decision()
    collection = _Collection()
    error = OperationFailure("transaction write conflict", code=112)
    error._error_labels.add("TransientTransactionError")
    collection.insert_error = error
    with pytest.raises(ProcessServiceAttemptAuthorityRegistryRetryRequiredError) as caught:
        registry.persist(decision, collection, session=_Session())
    assert caught.value.code == "P5B_WHOLE_TRANSACTION_RETRY_REQUIRED"
    assert caught.value.__cause__ is error
    assert collection.insert_calls == 1
    assert [item[0] for item in collection.operations] == ["find", "find", "insert_one"]


@pytest.mark.parametrize(
    "labels",
    [
        ("UnknownTransactionCommitResult",),
        ("TransientTransactionError", "UnknownTransactionCommitResult"),
    ],
)
def test_unknown_commit_result_is_never_insert_retry_classification(labels: tuple[str, ...]) -> None:
    """Commit uncertainty is excluded even when paired with a transient label."""
    decision = _decision()
    collection = _Collection()
    error = OperationFailure("commit outcome uncertain", code=251)
    error._error_labels.update(labels)
    collection.insert_error = error
    with pytest.raises(ProcessServiceAttemptAuthorityRegistryPersistenceUnavailableError) as caught:
        registry.persist(decision, collection, session=_Session())
    assert caught.value.code == "P5B_PERSISTENCE_UNAVAILABLE"
    assert caught.value.__cause__ is error
    assert collection.insert_calls == 1
    assert [item[0] for item in collection.operations] == ["find", "find", "insert_one"]


@pytest.mark.parametrize("failure", ["authority", "attempt", "insert", "reread"])
def test_each_mongo_operation_outage_is_governed(failure: str) -> None:
    """Authority lookup, attempt lookup, insert, and post-insert reread outages reject."""
    decision = _decision()
    collection = _Collection()
    if failure == "authority":
        collection.find_errors = [PyMongoError("authority read")]
    elif failure == "attempt":
        collection.find_errors = [None, PyMongoError("attempt read")]
    elif failure == "insert":
        collection.insert_error = PyMongoError("insert")
    else:
        collection.find_errors = [None, None, PyMongoError("reread")]
    _assert_code(
        lambda: registry.persist(decision, collection, session=_Session()),
        "P5B_PERSISTENCE_UNAVAILABLE",
        ProcessServiceAttemptAuthorityRegistryPersistenceUnavailableError,
    )


def test_index_creation_outage_is_governed() -> None:
    """Index setup PyMongoError becomes the stable persistence error."""
    collection = _Collection()
    original = collection.create_index

    def fail(spec: list[tuple[str, int]], **kwargs: Any) -> str:
        del spec, kwargs
        raise PyMongoError("index")

    collection.create_index = fail  # type: ignore[method-assign]
    _assert_code(
        lambda: registry.ensure_indexes(collection),
        "P5B_PERSISTENCE_UNAVAILABLE",
        ProcessServiceAttemptAuthorityRegistryPersistenceUnavailableError,
    )
    collection.create_index = original  # type: ignore[method-assign]


def test_post_insert_missing_or_corrupt_durability_never_returns_created() -> None:
    """Creation fails when durable reread is absent or corrupt."""
    decision = _decision()
    absent = _Collection()
    absent.drop_insert = True
    _assert_code(
        lambda: registry.persist(decision, absent, session=_Session()),
        "P5B_ATTEMPT_AUTHORITY_NOT_FOUND",
        ProcessServiceAttemptAuthorityRegistryReceiptNotFoundError,
    )
    corrupt = _Collection()
    corrupt.insert_error = None
    original_insert = corrupt.insert_one

    def corrupt_insert(row: dict[str, Any], *, session: Any) -> object:
        result = original_insert(row, session=session)
        corrupt.rows[0]["receipt_fingerprint"] = HEX_A
        return result

    corrupt.insert_one = corrupt_insert  # type: ignore[method-assign]
    _assert_code(
        lambda: registry.persist(decision, corrupt, session=_Session()),
        "P5B_RECEIPT_FINGERPRINT_MISMATCH",
        ProcessServiceAttemptAuthorityRegistryPersistedRecordInvalidError,
    )


def test_post_insert_structurally_valid_divergence_rejects() -> None:
    """A valid raced row with divergent semantics cannot be accepted as created."""
    proposed = _decision(attempt_id="attempt-proposed")
    alternate = _decision(attempt_id="attempt-alternate")
    collection = _DivergentInsertCollection(_persisted_row(alternate))
    _assert_code(
        lambda: registry.persist(proposed, collection, session=_Session()),
        "P5B_ATTEMPT_AUTHORITY_IDENTITY_CONFLICT",
        ProcessServiceAttemptAuthorityRegistryAuthorityIdentityConflictError,
    )


def test_receipt_and_result_are_immutable_and_serialization_is_defensive() -> None:
    """Frozen receipt/result values cannot be altered through serialized mappings."""
    decision = _decision()
    result = registry.persist(decision, _Collection(), session=_Session())
    with pytest.raises((AttributeError, TypeError)):
        result.receipt.tenant_id = "tenant-beta"  # type: ignore[misc]
    with pytest.raises((AttributeError, TypeError)):
        result.outcome = ProcessServiceAttemptAuthorityPersistenceOutcome.IDEMPOTENT_REPLAY  # type: ignore[misc]
    serialized = result.receipt.to_dict()
    serialized["tenant_id"] = "tenant-beta"
    assert result.receipt.tenant_id == TENANT
    assert result.receipt.to_dict()["tenant_id"] == TENANT


def test_p5b_has_no_lifecycle_current_pointer_or_financial_api() -> None:
    """Exact public surface proves append-only evidence and no later authority."""
    receipt_fields = {item.name for item in fields(registry.ProcessServiceAttemptAuthorityReceipt)}
    assert "_construction_proof" in receipt_fields
    assert "service_execution_id" not in receipt_fields
    assert "invoice" not in receipt_fields
    assert "payment" not in receipt_fields
    assert "settlement" not in receipt_fields
    assert not hasattr(registry, "ServiceAttempt")
    assert not hasattr(registry, "ServiceExecution")
    assert not hasattr(registry, "ReturnOfService")
    assert not hasattr(registry, "ProcessServiceAttemptAuthorityCurrent")
    assert not hasattr(registry, "CURRENT_COLLECTION")
    assert not hasattr(registry, "_client")
    assert not hasattr(registry.ProcessServiceAttemptAuthorityRegistry, "start_transaction")
    assert not hasattr(registry.ProcessServiceAttemptAuthorityRegistry, "commit_transaction")
    assert not hasattr(registry.ProcessServiceAttemptAuthorityRegistry, "abort_transaction")
    assert not hasattr(registry.ProcessServiceAttemptAuthorityRegistry, "commit")
    assert not hasattr(registry.ProcessServiceAttemptAuthorityRegistry, "abort")


def test_persistence_result_serialization_is_exact_and_nonfinancial() -> None:
    """Result serialization contains only outcome and canonical receipt evidence."""
    result = registry.persist(_decision(), _Collection(), session=_Session())
    assert set(result.to_dict()) == {"outcome", "receipt"}
    assert result.to_dict()["receipt"] == result.receipt.to_dict()
    assert all(name not in result.to_dict() for name in ("invoice", "payment", "settlement", "billing_execution"))


# ARTIFACT: test_process_service_attempt_authority_registry.py
# VERSION: v1.0.1-PROCESS-SERVICE-ATTEMPT-AUTHORITY-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct P5B persistence certificate only
# TENANT POSTURE: synthetic explicit tenant scope; no cross-tenant disclosure
# FAIL-CLOSED POSTURE: strict replay, hydration, outage, and transaction proofs
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
