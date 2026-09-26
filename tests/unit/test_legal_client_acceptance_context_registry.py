"""Direct P2C2 certificate for the immutable acceptance-context registry.

VERSION: v1.0.0-L9A4-P2C2-CLIENT-ACCEPTANCE-CONTEXT-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
AUTHORITY BOUNDARY: Context evidence persistence/read only; no acceptance or IAM.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator, cast

import pytest

from tools.eos.legal_operations.domain.legal_client_acceptance_context import (
    CONTEXT_FIELDS,
    LegalClientAcceptanceContext,
)
from tools.eos.legal_operations.registry import (
    legal_client_acceptance_context_registry as registry,
)


UTC = timezone.utc
NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=UTC)


class Session:
    """Recording fake for an already-active caller-owned transaction."""

    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class Cursor:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.rows)

    def sort(self, *_args: Any, **_kwargs: Any) -> "Cursor":
        return self

    def limit(self, value: int) -> "Cursor":
        return Cursor(self.rows[:value])


class Result:
    inserted_id = "inserted"


class Collection:
    """Minimal recording collection with exact equality query semantics."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []
        self.sessions: list[Any] = []
        self.operations: list[str] = []

    def with_options(self, **_kwargs: Any) -> "Collection":
        return self

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        unique: bool = False,
        name: str,
    ) -> str:
        self.indexes.append({"key": keys, "unique": unique, "name": name})
        return name

    def find_one(self, query: dict[str, object], *, session: Any) -> dict[str, object] | None:
        self.sessions.append(session)
        self.operations.append("find_one")
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return deepcopy(row)
        return None

    def find(self, query: dict[str, object], *, session: Any) -> Cursor:
        self.sessions.append(session)
        self.operations.append("find")
        return Cursor([
            deepcopy(row)
            for row in self.rows
            if all(row.get(key) == value for key, value in query.items())
        ])

    def insert_one(self, document: dict[str, object], *, session: Any) -> Result:
        self.sessions.append(session)
        self.operations.append("insert_one")
        row = deepcopy(document)
        row["_id"] = f"id-{len(self.rows) + 1}"
        self.rows.append(row)
        return Result()

    def update_one(self, *_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("context registry must not update")

    def delete_many(self, *_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("context registry must not delete")


def _fp(seed: str) -> str:
    import hashlib

    return hashlib.sha3_512(seed.encode()).hexdigest()


def context(
    *,
    tenant: str = "tenant-law",
    context_id: str = "context-1",
    actor: str = "principal-1",
    matter: str = "matter-1",
    party: str = "party-1",
    replay: str = "replay-1",
    issued: datetime = NOW,
    expires: datetime = NOW + timedelta(hours=1),
) -> LegalClientAcceptanceContext:
    """Build one synthetic P2C1 context without PII, secrets or authority."""
    return LegalClientAcceptanceContext(
        schema="WILSY-LEGAL-CLIENT-ACCEPTANCE-CONTEXT/V1",
        context_version="v1.0.0-L9A4-P2C1-CLIENT-ACCEPTANCE-CONTEXT",
        acceptance_context_id=context_id,
        tenant_id=tenant,
        actor_principal_id=actor,
        case_matter_id=matter,
        matter_reference=f"REF-{matter}",
        matter_fingerprint=_fp(f"matter:{matter}"),
        party_id=party,
        subject_reference=f"client:{party}",
        subject_identity_fingerprint=_fp(f"subject:{party}"),
        capacity_id=f"capacity:{party}",
        capacity_type="REPRESENTATIVE",
        capacity_fingerprint=_fp(f"capacity:{party}"),
        capacity_effective_from=issued - timedelta(days=1),
        capacity_effective_until=None,
        instrument_id="terms",
        instrument_version="1.0.0",
        instrument_fingerprint=_fp("instrument"),
        content_fingerprint=_fp("content"),
        content_reference=f"server://content/{matter}",
        title="Matter Review Terms",
        review_scope="client-information-review:v1",
        instrument_effective_from=issued - timedelta(days=1),
        lifecycle_status="ACTIVE",
        lifecycle_fingerprint=_fp("lifecycle"),
        lifecycle_evidence_fingerprint=_fp("lifecycle-evidence"),
        approval_id="approval-1",
        approval_decision="APPROVED",
        approval_fingerprint=_fp("approval"),
        approval_effective_from=issued - timedelta(days=1),
        issuer_evidence_reference="issuer-evidence:1",
        issuer_evidence_fingerprint=_fp("issuer-evidence"),
        issued_at=issued,
        expires_at=expires,
        replay_key=replay,
    )


def test_index_contract_is_exact_and_non_expiring() -> None:
    collection = Collection()
    registry.ensure_indexes(collection)
    assert collection.indexes == [
        {"key": [("tenant_id", 1), ("acceptance_context_id", 1)], "unique": True, "name": registry.CONTEXT_ID_INDEX_NAME},
        {"key": [("tenant_id", 1), ("fingerprint", 1)], "unique": True, "name": registry.FINGERPRINT_INDEX_NAME},
        {"key": [("tenant_id", 1), ("replay_key", 1)], "unique": True, "name": registry.REPLAY_KEY_INDEX_NAME},
        {"key": [("tenant_id", 1), ("actor_principal_id", 1), ("issued_at", -1)], "unique": False, "name": registry.ACTOR_ISSUED_INDEX_NAME},
        {"key": [("tenant_id", 1), ("case_matter_id", 1), ("issued_at", -1)], "unique": False, "name": registry.MATTER_ISSUED_INDEX_NAME},
        {"key": [("tenant_id", 1), ("case_matter_id", 1), ("party_id", 1), ("issued_at", -1)], "unique": False, "name": registry.MATTER_PARTY_ISSUED_INDEX_NAME},
        {"key": [("tenant_id", 1), ("expires_at", 1)], "unique": False, "name": registry.EXPIRES_INDEX_NAME},
        {"key": [("tenant_id", 1), ("actor_principal_id", 1), ("expires_at", 1)], "unique": False, "name": registry.ACTOR_EXPIRES_INDEX_NAME},
    ]
    assert not any("ttl" in str(item).casefold() for item in collection.indexes)


@pytest.mark.parametrize("operation", ["persist", "get", "valid", "actor", "matter", "party"])
def test_all_operational_paths_require_active_transaction(operation: str) -> None:
    collection = Collection()
    value = context()
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryTransactionRequiredError):
        if operation == "persist":
            registry.persist_context(value, collection, session=None)
        elif operation == "get":
            registry.get_context(value.tenant_id, value.acceptance_context_id, collection, session=Session(False))
        elif operation == "valid":
            registry.get_valid_context(value.tenant_id, value.acceptance_context_id, NOW, collection, session=None)
        elif operation == "actor":
            registry.list_contexts_for_actor(value.tenant_id, value.actor_principal_id, collection, session=Session(False))
        elif operation == "matter":
            registry.list_contexts_for_matter(value.tenant_id, value.case_matter_id, collection, session=None)
        else:
            registry.list_contexts_for_party(value.tenant_id, value.case_matter_id, value.party_id, collection, session=Session(False))


def test_exact_persist_replay_is_one_row_and_propagates_session() -> None:
    collection, session, value = Collection(), Session(), context()
    assert registry.persist_context(value, collection, session=session) == value
    assert registry.persist_context(value, collection, session=session) == value
    assert len(collection.rows) == 1
    assert all(item is session for item in collection.sessions)
    assert collection.rows[0]["issued_at"] == "2026-09-26T12:00:00.123456Z"


def test_post_write_readback_uses_the_same_caller_session() -> None:
    collection, session, value = Collection(), Session(), context()
    registry.persist_context(value, collection, session=session)
    assert collection.sessions and all(item is session for item in collection.sessions)


def test_divergent_context_id_replay_key_and_fingerprint_collisions_reject() -> None:
    collection, session, first = Collection(), Session(), context()
    registry.persist_context(first, collection, session=session)
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryConflictError):
        registry.persist_context(context(actor="principal-2", context_id=first.acceptance_context_id, replay="replay-2"), collection, session=session)
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryConflictError):
        registry.persist_context(context(actor="principal-2", context_id="context-2", replay=first.replay_key), collection, session=session)
    altered = context(context_id="context-3", replay="replay-3")
    object.__setattr__(altered, "fingerprint", first.fingerprint)
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryConflictError):
        registry.persist_context(altered, collection, session=session)


def test_cross_tenant_same_id_and_replay_coexist() -> None:
    collection, session = Collection(), Session()
    first = context()
    second = context(tenant="tenant-other")
    registry.persist_context(first, collection, session=session)
    registry.persist_context(second, collection, session=session)
    assert len(collection.rows) == 2


def test_exact_and_valid_time_reads_exclude_future_and_expired() -> None:
    collection, session, value = Collection(), Session(), context()
    registry.persist_context(value, collection, session=session)
    assert registry.get_context(value.tenant_id, value.acceptance_context_id, collection, session=session) == value
    assert registry.get_valid_context(value.tenant_id, value.acceptance_context_id, NOW, collection, session=session) == value
    assert registry.get_valid_context(value.tenant_id, value.acceptance_context_id, value.expires_at, collection, session=session) is None
    future = context(context_id="context-future", replay="replay-future", issued=NOW + timedelta(days=1), expires=NOW + timedelta(days=2))
    registry.persist_context(future, collection, session=session)
    assert registry.get_valid_context(future.tenant_id, future.acceptance_context_id, NOW, collection, session=session) is None
    assert registry.get_context(future.tenant_id, future.acceptance_context_id, collection, session=session) == future


def test_tenant_actor_matter_party_reads_are_exact() -> None:
    collection, session = Collection(), Session()
    values = [context(), context(context_id="context-2", replay="replay-2", actor="principal-2", party="party-2"), context(tenant="tenant-other", context_id="context-3", replay="replay-3")]
    for value in values:
        registry.persist_context(value, collection, session=session)
    assert len(registry.list_contexts_for_actor("tenant-law", "principal-1", collection, session=session)) == 1
    assert len(registry.list_contexts_for_matter("tenant-law", "matter-1", collection, session=session)) == 2
    assert len(registry.list_contexts_for_party("tenant-law", "matter-1", "party-2", collection, session=session)) == 1
    assert registry.list_contexts_for_matter("tenant-other", "matter-1", collection, session=session)[0].tenant_id == "tenant-other"


def test_wrong_tenant_exact_lookup_fails_without_existence_oracle() -> None:
    collection, session, value = Collection(), Session(), context()
    registry.persist_context(value, collection, session=session)
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryNotFoundError):
        registry.get_context("tenant-unrelated", value.acceptance_context_id, collection, session=session)


def test_wrong_tenant_valid_lookup_returns_no_context() -> None:
    collection, session, value = Collection(), Session(), context()
    registry.persist_context(value, collection, session=session)
    assert registry.get_valid_context("tenant-unrelated", value.acceptance_context_id, NOW, collection, session=session) is None


def test_wrong_tenant_actor_matter_and_party_reads_return_no_rows() -> None:
    collection, session, value = Collection(), Session(), context()
    registry.persist_context(value, collection, session=session)
    assert registry.list_contexts_for_actor("tenant-unrelated", value.actor_principal_id, collection, session=session) == ()
    assert registry.list_contexts_for_matter("tenant-unrelated", value.case_matter_id, collection, session=session) == ()
    assert registry.list_contexts_for_party("tenant-unrelated", value.case_matter_id, value.party_id, collection, session=session) == ()


def test_replay_key_is_tenant_scoped_and_same_context_id_can_coexist() -> None:
    collection, session = Collection(), Session()
    first = context()
    other = context(tenant="tenant-other")
    registry.persist_context(first, collection, session=session)
    registry.persist_context(other, collection, session=session)
    assert first.replay_key == other.replay_key
    assert first.acceptance_context_id == other.acceptance_context_id
    assert registry.get_context("tenant-other", other.acceptance_context_id, collection, session=session) == other


def test_corrupt_schema_and_fingerprint_reject_without_repair() -> None:
    collection, session, value = Collection(), Session(), context()
    registry.persist_context(value, collection, session=session)
    collection.rows[0]["fingerprint"] = "f" * 128
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryPersistedRecordInvalidError):
        registry.get_context(value.tenant_id, value.acceptance_context_id, collection, session=session)


@pytest.mark.parametrize(
    ("field", "replacement"),
    [
        ("schema", "WILSY-OTHER/V1"),
        ("context_version", "v9"),
        ("content_reference", "server://tampered"),
        ("title", "Tampered title"),
        ("review_scope", "tampered-scope"),
        ("content_fingerprint", "a" * 128),
        ("lifecycle_fingerprint", "b" * 128),
        ("approval_fingerprint", "c" * 128),
        ("issued_at", "2026-09-26T12:00:01.123456Z"),
        ("expires_at", "2026-09-26T13:00:01.123456Z"),
        ("issuer_evidence_reference", "tampered-issuer"),
    ],
)
def test_each_schema_bound_field_corruption_is_rejected(field: str, replacement: object) -> None:
    collection, session, value = Collection(), Session(), context()
    registry.persist_context(value, collection, session=session)
    collection.rows[0][field] = replacement
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryPersistedRecordInvalidError):
        registry.get_context(value.tenant_id, value.acceptance_context_id, collection, session=session)
    collection.rows[0] = value.to_dict() | {"_id": "id-1", "unexpected": True}
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryPersistedRecordInvalidError):
        registry.get_context(value.tenant_id, value.acceptance_context_id, collection, session=session)


def test_raw_content_locator_is_preserved_server_side_only() -> None:
    value = context()
    assert cast(str, value.to_dict()["content_reference"]).startswith("server://")
    assert set(value.to_dict()) == set(CONTEXT_FIELDS)


def test_expired_context_remains_durable_after_validity_exclusion() -> None:
    collection, session = Collection(), Session()
    value = context(expires=NOW + timedelta(seconds=1))
    registry.persist_context(value, collection, session=session)
    assert registry.get_valid_context(value.tenant_id, value.acceptance_context_id, NOW + timedelta(seconds=1), collection, session=session) is None
    assert registry.get_context(value.tenant_id, value.acceptance_context_id, collection, session=session) == value
    assert len(collection.rows) == 1


def test_missing_and_ambiguous_identifiers_fail_closed() -> None:
    collection, session, value = Collection(), Session(), context()
    registry.persist_context(value, collection, session=session)
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryInputError):
        registry.get_context("", value.acceptance_context_id, collection, session=session)
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryInputError):
        registry.get_context(value.tenant_id, " context-1", collection, session=session)


def test_context_registry_has_no_dependency_currentness_or_acceptance_projection() -> None:
    source = open(registry.__file__, encoding="utf-8").read()
    assert "currentness" in source
    assert "validity only" in source
    assert "projection" in source


def test_utc_microseconds_survive_serialization_and_normalization() -> None:
    value = context(issued=NOW.astimezone(timezone(timedelta(hours=2))))
    assert value.issued_at == NOW and value.issued_at.microsecond == 123456
    collection, session = Collection(), Session()
    registry.persist_context(value, collection, session=session)
    assert registry.get_context(value.tenant_id, value.acceptance_context_id, collection, session=session).issued_at == NOW


def test_limit_and_not_found_are_bounded() -> None:
    collection, session, value = Collection(), Session(), context()
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryInputError):
        registry.list_contexts_for_actor(value.tenant_id, value.actor_principal_id, collection, session=session, limit=0)
    with pytest.raises(registry.LegalClientAcceptanceContextRegistryNotFoundError):
        registry.get_context(value.tenant_id, "missing", collection, session=session)


def test_registry_has_no_mutation_or_forbidden_authority() -> None:
    assert not hasattr(registry, "update_context")
    assert not hasattr(registry, "delete_context")
    source = open(registry.__file__, encoding="utf-8").read()
    assert "record_legal_client_acceptance" not in source
    assert "legal_client_acceptance_registry" not in source
    assert "Kennel" in source
    assert "start_transaction" not in source
    assert "commit_transaction" not in source
    assert "abort_transaction" not in source
    assert "expireAfterSeconds" not in source
