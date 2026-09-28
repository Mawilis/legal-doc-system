"""Direct certificate for L9C12-P1 Court Operation Preparation registry.

TITLE: WILSY OS Legal Court Operation Preparation Registry Certificate
VERSION: v1.0.0-L9C12-P1-COURT-OPERATION-PREPARATION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify caller-owned transaction discipline, tenant isolation,
         immutable append-only persistence, exact replay, strict BSON
         hydration, collision handling and bounded preparation history.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_court_operation_preparation_registry.py
COLLABORATION / OWNERSHIP: P1 domain owns preparation truth; this certificate
                            covers persistence only. Orchestration and external
                            Court evidence remain later gates.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: Mongo-like recording fakes; no network or real Mongo.
FAIL-CLOSED DECLARATION: Missing transactions, malformed rows, collisions,
                         cross-tenant reads and mutation surfaces reject.
"""
from __future__ import annotations

import ast
from datetime import timedelta
from pathlib import Path
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_court_operation_preparation import LegalCourtOperationPreparation
from tools.eos.legal_operations.registry.legal_court_operation_preparation_registry import (
    COLLECTION,
    FINGERPRINT_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    MATTER_OPERATION_HISTORY_INDEX_NAME,
    MATTER_REPRESENTATION_HISTORY_INDEX_NAME,
    OPERATION_PREPARATION_ID_INDEX_NAME,
    TARGET_COURT_HISTORY_INDEX_NAME,
    VERSION,
    LegalCourtOperationPreparationRegistryConflictError,
    LegalCourtOperationPreparationRegistryInputError,
    LegalCourtOperationPreparationRegistryNotFoundError,
    LegalCourtOperationPreparationRegistryPersistedRecordInvalidError,
    LegalCourtOperationPreparationRegistryRetryRequiredError,
    LegalCourtOperationPreparationRegistryTransactionRequiredError,
    ensure_indexes,
    get_court_operation_preparation,
    get_court_operation_preparation_by_fingerprint,
    get_court_operation_preparation_by_idempotency_key,
    list_court_operation_preparations_for_matter,
    persist_court_operation_preparation,
)


class Session:
    in_transaction = True


class InactiveSession:
    in_transaction = False


class Cursor:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def sort(self, keys: list[tuple[str, int]]) -> "Cursor":
        for key, direction in reversed(keys):
            self.rows.sort(key=lambda row: cast(Any, row.get(key)), reverse=direction < 0)
        return self

    def limit(self, count: int) -> "Cursor":
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []
        self.calls: list[tuple[str, object, dict[str, object] | None]] = []

    def with_options(self, **_: object) -> "Collection":
        return self

    def create_index(self, keys: list[tuple[str, int]], *, unique: bool, name: str) -> str:
        self.indexes.append({"keys": keys, "unique": unique, "name": name})
        return name

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        self.calls.append(("find", session, dict(query)))
        return Cursor([dict(row) for row in self.rows if all(row.get(key) == value for key, value in query.items())])

    def insert_one(self, document: dict[str, object], *, session: object) -> object:
        self.calls.append(("insert_one", session, None))
        self.rows.append(dict(document))
        return object()


class BsonArrayCollection(Collection):
    def insert_one(self, document: dict[str, object], *, session: object) -> object:
        self.calls.append(("insert_one", session, None))
        stored = dict(document)
        for field in ("document_evidence_lineage", "requested_scope_capabilities"):
            if isinstance(stored[field], tuple):
                stored[field] = list(cast(tuple[object, ...], stored[field]))
        self.rows.append(stored)
        return object()


class DuplicateRaceCollection(Collection):
    def __init__(self, winning: dict[str, object]) -> None:
        super().__init__()
        self.winning = dict(winning)
        self.hidden = True

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        if self.hidden:
            return Cursor([])
        return super().find(query, session=session)

    def insert_one(self, document: dict[str, object], *, session: object) -> object:
        self.hidden = False
        self.rows.append(dict(self.winning))
        raise DuplicateKeyError("synthetic duplicate race")


def value(**overrides: object) -> LegalCourtOperationPreparation:
    from tests.unit.test_legal_court_operation_preparation import preparation

    return preparation(**overrides)


def test_contract_version_collection_indexes_and_no_ttl_or_current_pointer() -> None:
    collection = Collection()
    ensure_indexes(collection)
    assert VERSION == "v1.0.0-L9C12-P1-COURT-OPERATION-PREPARATION-REGISTRY"
    assert COLLECTION == "legal_court_operation_preparations"
    assert {cast(str, row["name"]) for row in collection.indexes} == {
        OPERATION_PREPARATION_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        MATTER_OPERATION_HISTORY_INDEX_NAME,
        MATTER_REPRESENTATION_HISTORY_INDEX_NAME,
        TARGET_COURT_HISTORY_INDEX_NAME,
    }
    assert sum(bool(row["unique"]) for row in collection.indexes) == 3
    assert all("expireAfterSeconds" not in row for row in collection.indexes)
    source = Path("tools/eos/legal_operations/registry/legal_court_operation_preparation_registry.py").read_text()
    assert "current_pointer" not in source
    assert "latest_wins" not in source
    assert "start_transaction" not in source and "commit_transaction" not in source and "abort_transaction" not in source


def test_active_transaction_is_required_and_domain_type_is_exact() -> None:
    collection = Collection()
    item = value()
    with pytest.raises(LegalCourtOperationPreparationRegistryTransactionRequiredError):
        persist_court_operation_preparation(item, collection, session=None)
    with pytest.raises(LegalCourtOperationPreparationRegistryTransactionRequiredError):
        get_court_operation_preparation(item.tenant_id, item.operation_preparation_id, collection, session=InactiveSession())
    with pytest.raises(LegalCourtOperationPreparationRegistryInputError):
        persist_court_operation_preparation(cast(Any, item.to_dict()), collection, session=Session())


def test_insert_replay_session_propagation_and_no_transaction_lifecycle() -> None:
    collection = Collection()
    session = Session()
    item = value()
    assert persist_court_operation_preparation(item, collection, session=session) == item
    assert persist_court_operation_preparation(item, collection, session=session) == item
    assert len(collection.rows) == 1
    assert all(call[1] is session for call in collection.calls)
    assert all(call[0] not in {"start_transaction", "commit_transaction", "abort_transaction"} for call in collection.calls)


def test_bson_array_round_trip_and_strict_corruption_rejection() -> None:
    collection = BsonArrayCollection()
    item = value()
    assert persist_court_operation_preparation(item, collection, session=Session()) == item
    assert isinstance(collection.rows[0]["document_evidence_lineage"], list)
    assert get_court_operation_preparation(item.tenant_id, item.operation_preparation_id, collection, session=Session()) == item
    collection.rows[0]["document_evidence_lineage"] = "document:invalid"
    with pytest.raises(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError):
        get_court_operation_preparation(item.tenant_id, item.operation_preparation_id, collection, session=Session())
    collection.rows[0] = {**item.to_dict(), "fingerprint": "0" * 128}
    with pytest.raises(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError):
        get_court_operation_preparation(item.tenant_id, item.operation_preparation_id, collection, session=Session())


@pytest.mark.parametrize("identity", ["operation_preparation_id", "fingerprint", "idempotency_key"])
def test_divergent_identity_collisions_fail_closed(identity: str) -> None:
    collection = Collection()
    first = value()
    persist_court_operation_preparation(first, collection, session=Session())
    second = value(idempotency_key="idempotency:other", target_court_reference="court:other")
    object.__setattr__(second, identity, getattr(first, identity))
    with pytest.raises(LegalCourtOperationPreparationRegistryConflictError):
        persist_court_operation_preparation(second, collection, session=Session())


def test_duplicate_race_reconciles_exact_only() -> None:
    item = value()
    assert persist_court_operation_preparation(item, DuplicateRaceCollection(item.to_dict()), session=Session()) == item
    divergent = value(source_evidence_reference="evidence:divergent")
    object.__setattr__(divergent, "operation_preparation_id", item.operation_preparation_id)
    with pytest.raises(LegalCourtOperationPreparationRegistryConflictError):
        persist_court_operation_preparation(divergent, DuplicateRaceCollection(item.to_dict()), session=Session())
    with pytest.raises(LegalCourtOperationPreparationRegistryRetryRequiredError):
        persist_court_operation_preparation(item, DuplicateRaceCollection({}), session=Session())


def test_all_exact_read_apis_are_tenant_scoped() -> None:
    collection = Collection()
    item = value()
    persist_court_operation_preparation(item, collection, session=Session())
    assert get_court_operation_preparation(item.tenant_id, item.operation_preparation_id, collection, session=Session()) == item
    assert get_court_operation_preparation_by_fingerprint(item.tenant_id, item.fingerprint, collection, session=Session()) == item
    assert get_court_operation_preparation_by_idempotency_key(item.tenant_id, item.idempotency_key, collection, session=Session()) == item
    with pytest.raises(LegalCourtOperationPreparationRegistryNotFoundError):
        get_court_operation_preparation("tenant-other", item.operation_preparation_id, collection, session=Session())


def test_matter_operation_history_is_ordered_bounded_and_isolated() -> None:
    collection = Collection()
    first = value()
    second = value(idempotency_key="idempotency:second", prepared_at=first.prepared_at + timedelta(minutes=2), occurred_at=first.occurred_at + timedelta(minutes=2))
    persist_court_operation_preparation(second, collection, session=Session())
    persist_court_operation_preparation(first, collection, session=Session())
    history = list_court_operation_preparations_for_matter(first.tenant_id, first.case_matter_id, preparation_collection=collection, session=Session())
    assert history == (first, second)
    assert list_court_operation_preparations_for_matter("tenant-other", first.case_matter_id, preparation_collection=collection, session=Session()) == ()
    with pytest.raises(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError):
        list_court_operation_preparations_for_matter(first.tenant_id, first.case_matter_id, preparation_collection=collection, session=Session(), limit=1)


def test_history_query_contains_exact_tenant_matter_operation_scope() -> None:
    collection = Collection()
    item = value()
    persist_court_operation_preparation(item, collection, session=Session())
    list_court_operation_preparations_for_matter(item.tenant_id, item.case_matter_id, preparation_collection=collection, session=Session())
    query = next(call[2] for call in collection.calls if call[0] == "find" and call[2] and call[2].get("operation_type"))
    assert query == {"tenant_id": item.tenant_id, "case_matter_id": item.case_matter_id, "operation_type": "COURT_FILING_PREPARATION"}


def test_input_limit_unknown_field_and_no_mutation_surface() -> None:
    collection = Collection()
    item = value()
    persist_court_operation_preparation(item, collection, session=Session())
    with pytest.raises(LegalCourtOperationPreparationRegistryInputError):
        list_court_operation_preparations_for_matter(item.tenant_id, item.case_matter_id, preparation_collection=collection, session=Session(), limit=0)
    collection.rows[0]["unexpected"] = True
    with pytest.raises(LegalCourtOperationPreparationRegistryPersistedRecordInvalidError):
        get_court_operation_preparation(item.tenant_id, item.operation_preparation_id, collection, session=Session())
    source = Path("tools/eos/legal_operations/registry/legal_court_operation_preparation_registry.py").read_text()
    tree = ast.parse(source)
    imported = " ".join(ast.unparse(node) for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))).lower()
    assert all(term not in imported for term in ("iam", "finance", "court_online"))
    assert "update_one" not in source and "replace_one" not in source and "delete_one" not in source


# ARTIFACT: test_legal_court_operation_preparation_registry.py
# VERSION: v1.0.0-L9C12-P1-COURT-OPERATION-PREPARATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct immutable preparation-registry certificate only
# FAIL-CLOSED POSTURE: transaction, replay, collision, hydration and tenant assertions are mandatory
# END OF WILSY OS SOVEREIGN ARTIFACT
