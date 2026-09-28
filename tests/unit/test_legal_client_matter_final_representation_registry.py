"""Direct certificate for L9C11-P24 final Representation registry.

TITLE: WILSY OS Legal Client Matter Final Representation Registry Certificate
VERSION: v1.0.0-L9C11-P24-FINAL-REPRESENTATION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Prove tenant-scoped immutable persistence, strict BSON hydration,
         exact replay/collision handling, bounded history and caller-owned
         transaction semantics with recording fakes only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_final_representation_registry.py
COLLABORATION / OWNERSHIP: P24 domain owns final truth; this certificate
                            covers persistence/read behavior only. Formation,
                            IAM, Court, currentness and finance are excluded.
CERTIFICATION / UPDATE DATE: 2026-09-28
TRANSACTION BOUNDARY: Synthetic Mongo-like fakes; no network or Mongo.
FAIL-CLOSED DECLARATION: Missing sessions, malformed rows, collisions and
                         authority expansion fail certification.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, cast

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_client_matter_final_representation import LegalClientMatterFinalRepresentation
from tools.eos.legal_operations.registry.legal_client_matter_final_representation_registry import (
    COLLECTION, FINGERPRINT_INDEX_NAME, IDEMPOTENCY_INDEX_NAME,
    MATTER_AUTHORITY_HISTORY_INDEX_NAME, MATTER_CLIENT_REPRESENTATIVE_HISTORY_INDEX_NAME,
    MATTER_DECISION_HISTORY_INDEX_NAME, MATTER_EFFECTIVE_HISTORY_INDEX_NAME,
    REPRESENTATION_ID_INDEX_NAME, VERSION,
    LegalClientMatterFinalRepresentationRegistryConflictError,
    LegalClientMatterFinalRepresentationRegistryInputError,
    LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError,
    LegalClientMatterFinalRepresentationRegistryRetryRequiredError,
    LegalClientMatterFinalRepresentationRegistryTransactionRequiredError,
    ensure_indexes, get_final_representation, get_final_representation_by_fingerprint,
    get_final_representation_by_idempotency_key, list_final_representations_for_context,
    persist_final_representation,
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
        if isinstance(stored["representation_scope_capabilities"], tuple):
            stored["representation_scope_capabilities"] = list(cast(tuple[object, ...], stored["representation_scope_capabilities"]))
        self.rows.append(stored)
        return object()


class DuplicateRaceCollection(Collection):
    def __init__(self, winning: dict[str, object]) -> None:
        super().__init__(); self.winning = dict(winning); self.hidden = True

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        if self.hidden:
            return Cursor([])
        return super().find(query, session=session)

    def insert_one(self, document: dict[str, object], *, session: object) -> object:
        self.hidden = False; self.rows.append(dict(self.winning)); raise DuplicateKeyError("synthetic duplicate race")


def value(**overrides: object) -> LegalClientMatterFinalRepresentation:
    from tests.unit.test_legal_client_matter_final_representation import _fixture
    return _fixture(**overrides)


def test_contract_version_collection_indexes_and_no_ttl_or_current_pointer() -> None:
    collection = Collection(); ensure_indexes(collection)
    assert VERSION == "v1.0.0-L9C11-P24-FINAL-REPRESENTATION-REGISTRY"
    assert COLLECTION == "legal_client_matter_final_representations"
    assert {cast(str, row["name"]) for row in collection.indexes} == {
        REPRESENTATION_ID_INDEX_NAME, FINGERPRINT_INDEX_NAME, IDEMPOTENCY_INDEX_NAME,
        MATTER_CLIENT_REPRESENTATIVE_HISTORY_INDEX_NAME, MATTER_AUTHORITY_HISTORY_INDEX_NAME,
        MATTER_DECISION_HISTORY_INDEX_NAME, MATTER_EFFECTIVE_HISTORY_INDEX_NAME,
    }
    assert sum(bool(row["unique"]) for row in collection.indexes) == 3
    assert all("expireAfterSeconds" not in row for row in collection.indexes)
    source = Path("tools/eos/legal_operations/registry/legal_client_matter_final_representation_registry.py").read_text()
    assert "current_pointer" not in source
    assert "project_currentness" not in source
    assert "start_transaction" not in source and "commit_transaction" not in source and "abort_transaction" not in source


def test_active_transaction_is_required_and_domain_type_is_exact() -> None:
    collection = Collection(); item = value()
    with pytest.raises(LegalClientMatterFinalRepresentationRegistryTransactionRequiredError):
        persist_final_representation(item, collection, session=None)
    with pytest.raises(LegalClientMatterFinalRepresentationRegistryTransactionRequiredError):
        get_final_representation(item.tenant_id, item.representation_id, collection, session=InactiveSession())
    with pytest.raises(LegalClientMatterFinalRepresentationRegistryInputError):
        persist_final_representation(cast(Any, item.to_dict()), collection, session=Session())


def test_insert_replay_session_propagation_and_no_transaction_lifecycle() -> None:
    collection = Collection(); session = Session(); item = value()
    assert persist_final_representation(item, collection, session=session) == item
    assert persist_final_representation(item, collection, session=session) == item
    assert len(collection.rows) == 1
    assert all(call[1] is session for call in collection.calls)
    assert all(call[0] not in {"start_transaction", "commit_transaction", "abort_transaction"} for call in collection.calls)


def test_bson_array_round_trip_and_strict_corruption_rejection() -> None:
    collection = BsonArrayCollection(); item = value()
    assert persist_final_representation(item, collection, session=Session()) == item
    assert isinstance(collection.rows[0]["representation_scope_capabilities"], list)
    assert get_final_representation(item.tenant_id, item.representation_id, collection, session=Session()) == item
    collection.rows[0]["representation_scope_capabilities"] = "ADVISORY"
    with pytest.raises(LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError):
        get_final_representation(item.tenant_id, item.representation_id, collection, session=Session())
    collection.rows[0] = {**item.to_dict(), "fingerprint": "0" * 128}
    with pytest.raises(LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError):
        get_final_representation(item.tenant_id, item.representation_id, collection, session=Session())


@pytest.mark.parametrize("identity", ["representation_id", "fingerprint", "idempotency_key"])
def test_divergent_identity_collisions_fail_closed(identity: str) -> None:
    collection = Collection(); first = value(); persist_final_representation(first, collection, session=Session())
    second = value(idempotency_key="idempotency:other")
    object.__setattr__(second, identity, getattr(first, identity))
    with pytest.raises(LegalClientMatterFinalRepresentationRegistryConflictError):
        persist_final_representation(second, collection, session=Session())


def test_duplicate_race_reconciles_exact_only() -> None:
    item = value()
    assert persist_final_representation(item, DuplicateRaceCollection(item.to_dict()), session=Session()) == item
    divergent = value(source_evidence_reference="evidence:divergent-p24")
    object.__setattr__(divergent, "representation_id", item.representation_id)
    with pytest.raises(LegalClientMatterFinalRepresentationRegistryConflictError):
        persist_final_representation(divergent, DuplicateRaceCollection(item.to_dict()), session=Session())
    with pytest.raises(LegalClientMatterFinalRepresentationRegistryRetryRequiredError):
        persist_final_representation(item, DuplicateRaceCollection({}), session=Session())


def test_all_exact_read_apis_are_tenant_scoped() -> None:
    collection = Collection(); item = value(); persist_final_representation(item, collection, session=Session())
    assert get_final_representation(item.tenant_id, item.representation_id, collection, session=Session()) == item
    assert get_final_representation_by_fingerprint(item.tenant_id, item.fingerprint, collection, session=Session()) == item
    assert get_final_representation_by_idempotency_key(item.tenant_id, item.idempotency_key, collection, session=Session()) == item
    with pytest.raises(Exception):
        get_final_representation("tenant-other", item.representation_id, collection, session=Session())
    assert all(call[2] is None or call[2].get("tenant_id") for call in collection.calls)


def test_exact_lineage_history_is_ordered_bounded_and_isolated() -> None:
    collection = Collection(); first = value(); second = value(idempotency_key="idempotency:second", occurred_at=first.occurred_at.replace(minute=8))
    persist_final_representation(second, collection, session=Session()); persist_final_representation(first, collection, session=Session())
    args = (first.tenant_id, first.case_matter_id, first.matter_fingerprint, first.client_party_id, first.subject_identity_fingerprint, first.representative_principal_id, first.representation_authority_id, first.firm_representation_decision_id)
    history = list_final_representations_for_context(*args, collection, session=Session())
    assert history == (first, second)
    assert list_final_representations_for_context("tenant-other", *args[1:], collection, session=Session()) == ()
    with pytest.raises(LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError):
        list_final_representations_for_context(*args, collection, session=Session(), limit=1)


def test_history_query_contains_exact_p1_p2_and_representative_lineage() -> None:
    collection = Collection(); item = value(); persist_final_representation(item, collection, session=Session())
    args = (item.tenant_id, item.case_matter_id, item.matter_fingerprint, item.client_party_id, item.subject_identity_fingerprint, item.representative_principal_id, item.representation_authority_id, item.firm_representation_decision_id)
    list_final_representations_for_context(*args, collection, session=Session())
    query = next(call[2] for call in collection.calls if call[0] == "find" and call[2] and call[2].get("firm_representation_decision_id"))
    assert query == {"tenant_id": item.tenant_id, "case_matter_id": item.case_matter_id, "matter_fingerprint": item.matter_fingerprint, "client_party_id": item.client_party_id, "subject_identity_fingerprint": item.subject_identity_fingerprint, "representative_principal_id": item.representative_principal_id, "representation_authority_id": item.representation_authority_id, "firm_representation_decision_id": item.firm_representation_decision_id}


def test_input_limit_and_persisted_unknown_field_fail_closed() -> None:
    collection = Collection(); item = value(); persist_final_representation(item, collection, session=Session())
    with pytest.raises(LegalClientMatterFinalRepresentationRegistryInputError):
        list_final_representations_for_context(item.tenant_id, item.case_matter_id, item.matter_fingerprint, item.client_party_id, item.subject_identity_fingerprint, item.representative_principal_id, item.representation_authority_id, item.firm_representation_decision_id, collection, session=Session(), limit=0)
    collection.rows[0]["unexpected"] = True
    with pytest.raises(LegalClientMatterFinalRepresentationRegistryPersistedRecordInvalidError):
        get_final_representation(item.tenant_id, item.representation_id, collection, session=Session())


def test_registry_has_no_mutation_or_downstream_authority_surface() -> None:
    source = Path("tools/eos/legal_operations/registry/legal_client_matter_final_representation_registry.py").read_text()
    tree = ast.parse(source)
    imported = " ".join(ast.unparse(node) for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))).lower()
    assert all(term not in imported for term in ("iam", "court", "finance", "currentness", "formation"))
    assert "update_one" not in source and "delete_one" not in source


# ARTIFACT: test_legal_client_matter_final_representation_registry.py
# VERSION: v1.0.0-L9C11-P24-FINAL-REPRESENTATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct immutable P24 registry certificate only
# FAIL-CLOSED POSTURE: transaction, BSON, collision, tenant and history assertions are mandatory
# END OF WILSY OS SOVEREIGN ARTIFACT
