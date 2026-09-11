"""WILSY OS M11 R8-R3B-P5 inbound collection authorization registry certificate.
TITLE: Durable Inbound Collection Authorization Registry Certificate
VERSION: v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Directly certifies tenant-scoped persistence, immutable replay, validity, revocation CAS, and exact single-use consumption CAS.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_inbound_collection_authorization_registry.py
COLLABORATION / OWNERSHIP: SaaS authorization-registry certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-09
CHANGELOG: v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE-CERT certifies persisted and strictly hydrated expiry-policy provenance, divergent replay, and unchanged lifecycle CAS behavior; v1.0.0-M11-R8-R3B-P5 certified the durable lifecycle owner.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic tenant-scoped records; no secrets or external provider calls.
TENANT BOUNDARY: Every identity, idempotency predicate, and lifecycle CAS carries tenant_id.
AUTHORITY BOUNDARY: Persistence/current-validity lifecycle only; no authorization or collection-authority issuance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive for outbound financial execution and settlement evidence.
TRANSACTION BOUNDARY: Fake collection only; caller owns session, transaction, commit, abort, and whole-transaction retry.
FAIL-CLOSED DECLARATION: Corrupt immutable/lifecycle records, divergent replay, stale validity, and CAS races reject.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from datetime import datetime, timedelta, timezone
import inspect
from pathlib import Path
from typing import Any

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.saas.domain.commercial_receivable import ReceivableFamily
from tools.eos.saas.domain.inbound_collection_authorization import (
    ClientInboundCollectionAuthorizationSubject,
    InboundCollectionAuthorization,
    OPERATION,
    PlatformInboundCollectionAuthorizationSubject,
)
from tools.eos.saas.billing.inbound_collection_authorization_registry import (
    COLLECTION,
    InboundCollectionAuthorizationLifecycleConflictError,
    InboundCollectionAuthorizationPersistedRecordInvalidError,
    InboundCollectionAuthorizationRecord,
    InboundCollectionAuthorizationRegistry,
    InboundCollectionAuthorizationRegistryError,
    InboundCollectionAuthorizationReplayConflictError,
)


STAMP = datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)
EXPIRY = STAMP + timedelta(hours=1)
HEX_A = "a" * 128
HEX_B = "b" * 128
HEX_C = "c" * 128
POLICY_V1 = "INBOUND_COLLECTION_AUTHORIZATION_EXPIRY_POLICY_V1"


class Session:
    """Minimal caller-owned active transaction marker."""

    in_transaction = True


ACTIVE = Session()


class UpdateResult:
    def __init__(self, matched_count: int) -> None:
        self.matched_count = matched_count


class Cursor:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def limit(self, count: int) -> "Cursor":
        return Cursor(self.rows[:count])

    def __iter__(self):
        return iter(self.rows)


class Collection:
    """Deterministic fake Mongo collection with nested-query and CAS support."""

    def __init__(self) -> None:
        self.documents: list[dict[str, Any]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, Any]]] = []
        self.calls: list[tuple[str, Any, Any]] = []
        self.duplicate_on_insert = False

    @staticmethod
    def _get(document: dict[str, Any], key: str) -> Any:
        value: Any = document
        for part in key.split("."):
            if not isinstance(value, dict):
                return None
            value = value.get(part)
        return value

    def _matches(self, document: dict[str, Any], query: dict[str, Any]) -> bool:
        for key, expected in query.items():
            actual = self._get(document, key)
            if isinstance(expected, dict) and "$lt" in expected:
                if actual is None or not actual < expected["$lt"]:
                    return False
            elif isinstance(expected, dict) and "$lte" in expected:
                if actual is None or not actual <= expected["$lte"]:
                    return False
            elif isinstance(expected, dict) and "$gt" in expected:
                if actual is None or not actual > expected["$gt"]:
                    return False
            elif actual != expected:
                return False
        return True

    def create_index(self, keys: list[tuple[str, int]], **kwargs: Any) -> str:
        self.indexes.append((keys, kwargs))
        return str(kwargs.get("name", "index"))

    def find(self, query: dict[str, Any], *, session: Any = None) -> Cursor:
        self.calls.append(("find", deepcopy(query), session))
        return Cursor([deepcopy(row) for row in self.documents if self._matches(row, query)])

    def insert_one(self, document: dict[str, Any], *, session: Any = None) -> None:
        self.calls.append(("insert_one", deepcopy(document), session))
        if self.duplicate_on_insert:
            raise DuplicateKeyError("duplicate")
        self.documents.append(deepcopy(document))

    def update_one(self, query: dict[str, Any], update: dict[str, Any], *, session: Any = None) -> UpdateResult:
        self.calls.append(("update_one", deepcopy(query), session))
        for document in self.documents:
            if self._matches(document, query):
                for dotted, value in update.get("$set", {}).items():
                    target = document
                    parts = dotted.split(".")
                    for part in parts[:-1]:
                        target = target.setdefault(part, {})
                    target[parts[-1]] = deepcopy(value)
                return UpdateResult(1)
        return UpdateResult(0)


def authorization(**changes: object) -> InboundCollectionAuthorization:
    values: dict[str, Any] = {
        "inbound_collection_authorization_id": "ica-a",
        "tenant_id": "tenant-a",
        "principal_id": "principal-a",
        "operation": OPERATION,
        "subject_authority_kind": ReceivableFamily.CLIENT,
        "subject_authority": ClientInboundCollectionAuthorizationSubject(
            "tenant-a", "receivable-a", "invoice-a", HEX_A, HEX_B, 12500, "ZAR", "customer-a"
        ),
        "tenant_authorization_decision_id": "decision-a",
        "tenant_authorization_evidence_fingerprint": HEX_C,
        "idempotency_key": "idem-a",
        "authorized_at": STAMP,
        "expires_at": EXPIRY,
        "expiry_policy_version": POLICY_V1,
    }
    values.update(changes)
    return InboundCollectionAuthorization(**values)


def platform_authorization(**changes: object) -> InboundCollectionAuthorization:
    values: dict[str, Any] = {
        "inbound_collection_authorization_id": "ica-platform-a",
        "tenant_id": "tenant-a",
        "principal_id": "principal-a",
        "operation": OPERATION,
        "subject_authority_kind": ReceivableFamily.PLATFORM,
        "subject_authority": PlatformInboundCollectionAuthorizationSubject(
            "tenant-a", "receivable-platform-a", "platform-invoice-a", HEX_A, HEX_B, 12500, "ZAR"
        ),
        "tenant_authorization_decision_id": "decision-platform-a",
        "tenant_authorization_evidence_fingerprint": HEX_C,
        "idempotency_key": "idem-platform-a",
        "authorized_at": STAMP,
        "expires_at": EXPIRY,
        "expiry_policy_version": POLICY_V1,
    }
    values.update(changes)
    return InboundCollectionAuthorization(**values)


def stored(collection: Collection, value: InboundCollectionAuthorization, **lifecycle: Any) -> None:
    state = {"revoked_at": None, "revocation_reference": None, "consumed_at": None, "consumed_by_collection_authority_id": None}
    state.update(lifecycle)
    collection.documents.append({**value.to_dict(), "lifecycle": state})


def create_record(value: InboundCollectionAuthorization | None = None, collection: Collection | None = None) -> tuple[Collection, InboundCollectionAuthorizationRecord]:
    target = collection or Collection()
    record = InboundCollectionAuthorizationRegistry.create(value or authorization(), target, session=ACTIVE)
    return target, record


def test_collection_and_exact_two_tenant_scoped_unique_indexes() -> None:
    collection = Collection()
    InboundCollectionAuthorizationRegistry.ensure_indexes(collection)
    assert COLLECTION == "inbound_collection_authorizations"
    assert len(collection.indexes) == 2
    assert all(index[1]["unique"] for index in collection.indexes)
    assert collection.indexes[0][0] == [("tenant_id", 1), ("inbound_collection_authorization_id", 1)]
    assert collection.indexes[1][0] == [("tenant_id", 1), ("idempotency_key", 1)]
    indexed = {key for index, _ in collection.indexes for key, _direction in index}
    assert "source_authority.commercial_receivable_id" not in indexed
    assert "provider" not in indexed and "amount" not in indexed and "customer_id" not in indexed


def test_valid_client_and_platform_create_with_empty_initial_lifecycle() -> None:
    collection, client = create_record()
    _, platform = create_record(platform_authorization(), collection=Collection())
    assert client.authorization.subject_authority_kind is ReceivableFamily.CLIENT
    assert platform.authorization.subject_authority_kind is ReceivableFamily.PLATFORM
    assert client.revoked_at is None and client.revocation_reference is None
    assert client.consumed_at is None and client.consumed_by_collection_authority_id is None


def test_create_persists_and_roundtrips_exact_expiry_policy_version() -> None:
    collection, record = create_record()
    assert collection.documents[0]["expiry_policy_version"] == POLICY_V1
    assert record.authorization.expiry_policy_version == POLICY_V1
    _, platform = create_record(platform_authorization(), collection=Collection())
    assert platform.authorization.expiry_policy_version == POLICY_V1


@pytest.mark.parametrize(
    "mutator",
    [
        lambda payload: payload.pop("expiry_policy_version"),
        lambda payload: payload.update({"expiry_policy_version": None}),
        lambda payload: payload.update({"expiry_policy_version": ""}),
        lambda payload: payload.update({"expiry_policy_version": "   "}),
        lambda payload: payload.update({"expiry_policy_version": 600}),
    ],
)
def test_missing_or_malformed_expiry_policy_version_fails_closed(mutator) -> None:
    payload = {
        **authorization().to_dict(),
        "lifecycle": {
            "revoked_at": None,
            "revocation_reference": None,
            "consumed_at": None,
            "consumed_by_collection_authority_id": None,
        },
    }
    mutator(payload)
    with pytest.raises(InboundCollectionAuthorizationPersistedRecordInvalidError):
        InboundCollectionAuthorizationRegistry._hydrate(payload)


def test_registry_never_defaults_or_infers_expiry_policy_version() -> None:
    payload = {
        **authorization().to_dict(),
        "lifecycle": {
            "revoked_at": None,
            "revocation_reference": None,
            "consumed_at": None,
            "consumed_by_collection_authority_id": None,
        },
    }
    payload.pop("expiry_policy_version")
    with pytest.raises(InboundCollectionAuthorizationPersistedRecordInvalidError):
        InboundCollectionAuthorizationRegistry._hydrate(payload)


def test_policy_version_tamper_with_old_fingerprint_fails_closed() -> None:
    collection = Collection()
    stored(collection, authorization())
    collection.documents[0]["expiry_policy_version"] = "INBOUND_COLLECTION_AUTHORIZATION_EXPIRY_POLICY_V2"
    with pytest.raises(InboundCollectionAuthorizationPersistedRecordInvalidError):
        InboundCollectionAuthorizationRegistry._hydrate(collection.documents[0])


def test_create_has_no_caller_lifecycle_state_api() -> None:
    assert "lifecycle" not in inspect.signature(InboundCollectionAuthorizationRegistry.create).parameters
    with pytest.raises(TypeError):
        InboundCollectionAuthorizationRegistry.create(authorization(), Collection(), session=ACTIVE, lifecycle={})  # type: ignore[call-arg]


def test_exact_replay_returns_current_canonical_record_and_never_resets_lifecycle() -> None:
    collection, _ = create_record()
    consumed = InboundCollectionAuthorizationRegistry.consume("tenant-a", "ica-a", authorization().authorization_evidence_fingerprint, STAMP, "collection-authority-a", collection, session=ACTIVE)
    replay = InboundCollectionAuthorizationRegistry.create(authorization(), collection, session=ACTIVE)
    assert replay == consumed
    assert replay.consumed_by_collection_authority_id == "collection-authority-a"


def test_revoked_replay_never_resets_revocation() -> None:
    collection, _ = create_record()
    revoked = InboundCollectionAuthorizationRegistry.revoke("tenant-a", "ica-a", "revocation-a", STAMP, collection, session=ACTIVE)
    replay = InboundCollectionAuthorizationRegistry.create(authorization(), collection, session=ACTIVE)
    assert replay == revoked and replay.revocation_reference == "revocation-a"


@pytest.mark.parametrize("candidate", [
    authorization(subject_authority=ClientInboundCollectionAuthorizationSubject("tenant-a", "receivable-b", "invoice-a", HEX_A, HEX_B, 12500, "ZAR", "customer-a")),
    authorization(subject_authority=ClientInboundCollectionAuthorizationSubject("tenant-a", "receivable-a", "invoice-a", HEX_A, HEX_B, 12501, "ZAR", "customer-a")),
    authorization(principal_id="principal-b"),
    authorization(expires_at=STAMP + timedelta(hours=2)),
    authorization(expiry_policy_version="INBOUND_COLLECTION_AUTHORIZATION_EXPIRY_POLICY_V2"),
    authorization(tenant_authorization_decision_id="decision-b"),
])
def test_divergent_authorization_id_replay_rejects(candidate: InboundCollectionAuthorization) -> None:
    collection, _ = create_record()
    with pytest.raises(InboundCollectionAuthorizationReplayConflictError):
        InboundCollectionAuthorizationRegistry.create(candidate, collection, session=ACTIVE)


def test_divergent_idempotency_authorization_replay_rejects() -> None:
    collection, _ = create_record()
    with pytest.raises(InboundCollectionAuthorizationReplayConflictError):
        InboundCollectionAuthorizationRegistry.create(authorization(inbound_collection_authorization_id="ica-b"), collection, session=ACTIVE)


def test_disagreeing_id_and_idempotency_facts_fail_closed() -> None:
    collection, value = create_record()
    other = authorization(inbound_collection_authorization_id="ica-b", idempotency_key="idem-b")
    stored(collection, other)
    with pytest.raises(InboundCollectionAuthorizationRegistryError):
        InboundCollectionAuthorizationRegistry.create(authorization(inbound_collection_authorization_id="ica-a", idempotency_key="idem-b"), collection, session=ACTIVE)
    assert value.authorization.tenant_id == "tenant-a"


def test_strict_client_platform_hydration_and_fingerprint_recompute() -> None:
    collection = Collection()
    stored(collection, authorization())
    stored(collection, platform_authorization())
    assert InboundCollectionAuthorizationRegistry.get("tenant-a", "ica-a", collection, session=ACTIVE) is not None
    assert InboundCollectionAuthorizationRegistry.get("tenant-a", "ica-platform-a", collection, session=ACTIVE) is not None
    tampered = deepcopy(collection.documents[0]); tampered["authorization_evidence_fingerprint"] = HEX_B
    with pytest.raises(InboundCollectionAuthorizationPersistedRecordInvalidError):
        InboundCollectionAuthorizationRegistry._hydrate(tampered)


@pytest.mark.parametrize("mutator", [
    lambda payload: payload.pop("principal_id"),
    lambda payload: payload.update({"unknown": True}),
    lambda payload: payload.update({"subject_authority_kind": "UNKNOWN"}),
    lambda payload: payload.update({"subject_authority": platform_authorization().subject_authority.to_dict()}),
])
def test_corrupt_immutable_hydration_fails_closed(mutator) -> None:
    payload = {**authorization().to_dict(), "lifecycle": {"revoked_at": None, "revocation_reference": None, "consumed_at": None, "consumed_by_collection_authority_id": None}}
    mutator(payload)
    with pytest.raises(InboundCollectionAuthorizationPersistedRecordInvalidError):
        InboundCollectionAuthorizationRegistry._hydrate(payload)


@pytest.mark.parametrize("lifecycle", [
    {"revoked_at": STAMP, "revocation_reference": None, "consumed_at": None, "consumed_by_collection_authority_id": None},
    {"revoked_at": None, "revocation_reference": "r", "consumed_at": None, "consumed_by_collection_authority_id": None},
    {"revoked_at": STAMP, "revocation_reference": "r", "consumed_at": STAMP, "consumed_by_collection_authority_id": "ca"},
    {"revoked_at": STAMP - timedelta(seconds=1), "revocation_reference": "r", "consumed_at": None, "consumed_by_collection_authority_id": None},
    {"revoked_at": None, "revocation_reference": None, "consumed_at": EXPIRY, "consumed_by_collection_authority_id": "ca"},
    {"revoked_at": None, "revocation_reference": None, "consumed_at": STAMP, "consumed_by_collection_authority_id": None},
])
def test_lifecycle_corruption_fails_closed(lifecycle: dict[str, Any]) -> None:
    collection = Collection(); stored(collection, authorization(), **lifecycle)
    with pytest.raises(InboundCollectionAuthorizationPersistedRecordInvalidError):
        InboundCollectionAuthorizationRegistry.get("tenant-a", "ica-a", collection, session=ACTIVE)


def test_tenant_scoped_getters_and_idempotency_isolation() -> None:
    collection = Collection(); stored(collection, authorization())
    assert InboundCollectionAuthorizationRegistry.get("tenant-b", "ica-a", collection, session=ACTIVE) is None
    assert InboundCollectionAuthorizationRegistry.get_by_idempotency_key("tenant-b", "idem-a", collection, session=ACTIVE) is None
    assert InboundCollectionAuthorizationRegistry.get_by_idempotency_key("tenant-a", " idem-a ", collection, session=ACTIVE) is not None
    with pytest.raises(InboundCollectionAuthorizationRegistryError):
        InboundCollectionAuthorizationRegistry.get("tenant-a", "ica-a", collection)
    with pytest.raises(InboundCollectionAuthorizationRegistryError):
        InboundCollectionAuthorizationRegistry.get_by_idempotency_key("tenant-a", "idem-a", collection)


def test_lookup_signatures_require_tenant_and_expose_no_inference_helpers() -> None:
    with pytest.raises(TypeError):
        InboundCollectionAuthorizationRegistry.get("ica-a", Collection(), session=ACTIVE)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        InboundCollectionAuthorizationRegistry.get_by_idempotency_key("idem-a", Collection(), session=ACTIVE)  # type: ignore[call-arg]
    public = {name for name in dir(InboundCollectionAuthorizationRegistry) if not name.startswith("_")}
    assert not public.intersection({"latest", "current", "get_current", "get_latest", "get_by_subject", "get_by_amount", "get_by_customer", "get_by_provider"})


def test_current_usability_requires_caller_time_and_window() -> None:
    collection, record = create_record()
    assert record.is_currently_usable(STAMP) is True
    assert record.is_currently_usable(EXPIRY) is False
    assert record.is_currently_usable(STAMP - timedelta(seconds=1)) is False
    with pytest.raises(InboundCollectionAuthorizationRegistryError):
        record.is_currently_usable(datetime(2026, 9, 9, 9, 0))


def test_valid_revoke_cas_forwards_session_and_preserves_immutable_evidence() -> None:
    collection, before = create_record()
    result = InboundCollectionAuthorizationRegistry.revoke("tenant-a", "ica-a", "revocation-a", STAMP, collection, session=ACTIVE, expected_authorization_evidence_fingerprint=before.authorization.authorization_evidence_fingerprint)
    assert result.authorization == before.authorization
    assert result.revoked_at == STAMP and result.revocation_reference == "revocation-a"
    assert collection.calls[-1][0] == "update_one" and collection.calls[-1][2] is ACTIVE
    revoke_query = collection.calls[-1][1]
    assert revoke_query["tenant_id"] == "tenant-a"
    assert revoke_query["inbound_collection_authorization_id"] == "ica-a"
    assert revoke_query["authorization_evidence_fingerprint"] == before.authorization.authorization_evidence_fingerprint
    assert revoke_query["lifecycle.revoked_at"] is None and revoke_query["lifecycle.consumed_at"] is None
    assert revoke_query["authorized_at"] == {"$lte": STAMP.isoformat(timespec="microseconds")}
    assert set(collection.documents[0]) == set(before.authorization.to_dict()) | {"lifecycle"}


def test_naive_revocation_time_is_rejected() -> None:
    collection, _ = create_record()
    with pytest.raises(InboundCollectionAuthorizationRegistryError):
        InboundCollectionAuthorizationRegistry.revoke("tenant-a", "ica-a", "r", datetime(2026, 9, 9, 9, 0), collection, session=ACTIVE)


@pytest.mark.parametrize("reference", ["", " "])
def test_revocation_reference_required(reference: str) -> None:
    collection, _ = create_record()
    with pytest.raises(InboundCollectionAuthorizationRegistryError):
        InboundCollectionAuthorizationRegistry.revoke("tenant-a", "ica-a", reference, STAMP, collection, session=ACTIVE)


def test_second_revoke_and_consumed_revoke_fail_closed() -> None:
    collection, _ = create_record()
    InboundCollectionAuthorizationRegistry.revoke("tenant-a", "ica-a", "revocation-a", STAMP, collection, session=ACTIVE)
    with pytest.raises(InboundCollectionAuthorizationLifecycleConflictError):
        InboundCollectionAuthorizationRegistry.revoke("tenant-a", "ica-a", "revocation-b", STAMP, collection, session=ACTIVE)
    collection2, _ = create_record()
    InboundCollectionAuthorizationRegistry.consume("tenant-a", "ica-a", authorization().authorization_evidence_fingerprint, STAMP, "ca", collection2, session=ACTIVE)
    with pytest.raises(InboundCollectionAuthorizationLifecycleConflictError):
        InboundCollectionAuthorizationRegistry.revoke("tenant-a", "ica-a", "r", STAMP, collection2, session=ACTIVE)


def test_valid_consume_binds_exact_collection_authority_and_forwards_session() -> None:
    collection, before = create_record()
    result = InboundCollectionAuthorizationRegistry.consume("tenant-a", "ica-a", before.authorization.authorization_evidence_fingerprint, STAMP, "collection-authority-a", collection, session=ACTIVE)
    assert result.authorization == before.authorization
    assert result.consumed_at == STAMP and result.consumed_by_collection_authority_id == "collection-authority-a"
    assert collection.documents[0]["lifecycle"]["consumed_by_collection_authority_id"] == "collection-authority-a"
    assert collection.calls[-1][0] == "update_one" and collection.calls[-1][2] is ACTIVE
    consume_query = collection.calls[-1][1]
    assert consume_query["tenant_id"] == "tenant-a"
    assert consume_query["inbound_collection_authorization_id"] == "ica-a"
    assert consume_query["authorization_evidence_fingerprint"] == before.authorization.authorization_evidence_fingerprint
    assert consume_query["lifecycle.revoked_at"] is None and consume_query["lifecycle.consumed_at"] is None
    assert consume_query["authorized_at"] == {"$lte": STAMP.isoformat(timespec="microseconds")}
    assert consume_query["expires_at"] == {"$gt": STAMP.isoformat(timespec="microseconds")}


@pytest.mark.parametrize("consumer", ["", " "])
def test_consumer_identity_required(consumer: str) -> None:
    collection, value = create_record()
    with pytest.raises(InboundCollectionAuthorizationRegistryError):
        InboundCollectionAuthorizationRegistry.consume("tenant-a", "ica-a", value.authorization.authorization_evidence_fingerprint, STAMP, consumer, collection, session=ACTIVE)


def test_consume_requires_exact_fingerprint_and_single_use() -> None:
    collection, value = create_record()
    with pytest.raises(InboundCollectionAuthorizationLifecycleConflictError):
        InboundCollectionAuthorizationRegistry.consume("tenant-a", "ica-a", HEX_B, STAMP, "ca", collection, session=ACTIVE)
    InboundCollectionAuthorizationRegistry.consume("tenant-a", "ica-a", value.authorization.authorization_evidence_fingerprint, STAMP, "ca", collection, session=ACTIVE)
    with pytest.raises(InboundCollectionAuthorizationLifecycleConflictError):
        InboundCollectionAuthorizationRegistry.consume("tenant-a", "ica-a", value.authorization.authorization_evidence_fingerprint, STAMP, "ca", collection, session=ACTIVE)


@pytest.mark.parametrize("when", [STAMP - timedelta(seconds=1), EXPIRY, EXPIRY + timedelta(seconds=1)])
def test_consume_enforces_authorized_at_inclusive_and_expiry_exclusive(when: datetime) -> None:
    collection, value = create_record()
    if when == STAMP:
        expected = True
    else:
        expected = False
    if expected:
        result = InboundCollectionAuthorizationRegistry.consume("tenant-a", "ica-a", value.authorization.authorization_evidence_fingerprint, when, "ca", collection, session=ACTIVE)
        assert result.consumed_at == when
    else:
        with pytest.raises(InboundCollectionAuthorizationLifecycleConflictError):
            InboundCollectionAuthorizationRegistry.consume("tenant-a", "ica-a", value.authorization.authorization_evidence_fingerprint, when, "ca", collection, session=ACTIVE)


def test_revoked_authorization_cannot_consume() -> None:
    collection, value = create_record()
    InboundCollectionAuthorizationRegistry.revoke("tenant-a", "ica-a", "r", STAMP, collection, session=ACTIVE)
    with pytest.raises(InboundCollectionAuthorizationLifecycleConflictError):
        InboundCollectionAuthorizationRegistry.consume("tenant-a", "ica-a", value.authorization.authorization_evidence_fingerprint, STAMP, "ca", collection, session=ACTIVE)


@pytest.mark.parametrize("operation", ["get", "get_by_idempotency_key", "create", "revoke", "consume"])
def test_all_public_operations_require_active_caller_transaction(operation: str) -> None:
    collection = Collection(); value = authorization()
    with pytest.raises(InboundCollectionAuthorizationRegistryError):
        if operation == "get":
            InboundCollectionAuthorizationRegistry.get("tenant-a", "ica-a", collection)
        elif operation == "get_by_idempotency_key":
            InboundCollectionAuthorizationRegistry.get_by_idempotency_key("tenant-a", "idem-a", collection)
        elif operation == "create":
            InboundCollectionAuthorizationRegistry.create(value, collection)
        elif operation == "revoke":
            InboundCollectionAuthorizationRegistry.revoke("tenant-a", "ica-a", "r", STAMP, collection)
        else:
            InboundCollectionAuthorizationRegistry.consume("tenant-a", "ica-a", value.authorization_evidence_fingerprint, STAMP, "ca", collection)


def test_duplicate_key_propagates_without_same_session_recovery() -> None:
    collection = Collection(); collection.duplicate_on_insert = True
    with pytest.raises(DuplicateKeyError):
        InboundCollectionAuthorizationRegistry.create(authorization(), collection, session=ACTIVE)
    assert [call[0] for call in collection.calls] == ["find", "find", "insert_one"]


def test_registry_does_not_start_commit_or_abort_transactions() -> None:
    source = Path(__file__).parents[2] / "tools/eos/saas/billing/inbound_collection_authorization_registry.py"
    text = source.read_text(encoding="utf-8").lower()
    assert "start_transaction" not in text and ".commit_transaction" not in text and ".abort_transaction" not in text
    assert "datetime.now" not in text and "tenantauthorizationdecision" not in text


def test_create_and_reads_forward_caller_session() -> None:
    collection = Collection()
    InboundCollectionAuthorizationRegistry.create(authorization(), collection, session=ACTIVE)
    assert collection.calls[-1][0] == "insert_one" and collection.calls[-1][2] is ACTIVE
    InboundCollectionAuthorizationRegistry.get("tenant-a", "ica-a", collection, session=ACTIVE)
    assert collection.calls[-1][0] == "find" and collection.calls[-1][2] is ACTIVE
    InboundCollectionAuthorizationRegistry.get_by_idempotency_key("tenant-a", "idem-a", collection, session=ACTIVE)
    assert collection.calls[-1][0] == "find" and collection.calls[-1][2] is ACTIVE


def test_registry_has_no_issuance_provider_invoice_ap_or_settlement_dependencies() -> None:
    source = Path(__file__).parents[2] / "tools/eos/saas/billing/inbound_collection_authorization_registry.py"
    text = source.read_text(encoding="utf-8").lower()
    for forbidden in ("payfast", "payshap", "m_payment_id", "pf_payment_id", "merchant_id", "clientinvoice", "platforminvoice", "financialexecutioncommand", "financialexecutionattempt", "vendorbill", "paymentdestination", "payment_confirmation"):
        assert forbidden not in text


def test_registry_record_keeps_immutable_evidence_separate_from_lifecycle() -> None:
    record = InboundCollectionAuthorizationRecord(authorization(), None, None, None, None)
    assert record.authorization.authorization_evidence_fingerprint
    assert set(record.__dataclass_fields__) == {"authorization", "revoked_at", "revocation_reference", "consumed_at", "consumed_by_collection_authority_id"}


# ARTIFACT: test_inbound_collection_authorization_registry.py
# VERSION: v1.1.0-M11-R8-R3B-P6D-EXPIRY-POLICY-PROVENANCE-CERT
# AUTHORITY BOUNDARY: Durable authorization evidence and lifecycle certificate only.
# TENANT POSTURE: Explicit tenant-scoped fake records and CAS predicates.
# FAIL-CLOSED POSTURE: Replay, hydration, expiry, revocation, consumption, and transaction violations reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
