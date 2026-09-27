"""Direct certificate for the immutable client mandate-grant formation registry.

TITLE: WILSY OS Legal Client Matter Mandate Grant Registry Certificate
VERSION: v1.0.0-L9B7-CLIENT-MANDATE-GRANT-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify tenant-scoped append-only grant formation persistence,
         exact replay/collision behavior, strict hydration, deterministic
         history reads, and explicit exclusion of lifecycle/currentness.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_grant_registry.py
CERTIFICATION / UPDATE DATE: 2026-09-27
TRANSACTION BOUNDARY: Synthetic collection/session fakes only; no Mongo.
"""
from __future__ import annotations

import ast
from typing import Any

import pytest

from tools.eos.legal_operations.domain.legal_client_matter_mandate_grant import (
    LegalClientMatterMandateGrant,
)
from tools.eos.legal_operations.registry.legal_client_matter_mandate_grant_registry import (
    COLLECTION,
    FINGERPRINT_INDEX_NAME,
    GRANT_ID_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    MATTER_CLIENT_INDEX_NAME,
    MATTER_CLIENT_SCOPE_INDEX_NAME,
    LegalClientMatterMandateGrantRegistryConflictError,
    LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError,
    LegalClientMatterMandateGrantRegistryTransactionRequiredError,
    ensure_indexes,
    get_grant,
    get_grant_by_fingerprint,
    list_grants_for_matter_client,
    persist_grant,
)
from tests.unit.test_legal_client_matter_mandate_grant import grant


class Session:
    """Minimal active caller-owned transaction marker."""

    in_transaction = True


class Cursor:
    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def sort(self, keys: list[tuple[str, int]]) -> "Cursor":
        for key, direction in reversed(keys):
            self.rows.sort(key=lambda row: str(row.get(key)), reverse=direction < 0)
        return self

    def limit(self, count: int) -> "Cursor":
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class Collection:
    """Recording fake with Mongo-like collection methods used by the registry."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []
        self.calls: list[tuple[str, object]] = []

    def with_options(self, **_: object) -> "Collection":
        return self

    def create_index(self, keys: list[tuple[str, int]], *, unique: bool, name: str) -> str:
        self.indexes.append({"keys": keys, "unique": unique, "name": name})
        return name

    def find_one(self, query: dict[str, object], *, session: object) -> dict[str, object] | None:
        self.calls.append(("find_one", session))
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None

    def find(self, query: dict[str, object], *, session: object) -> Cursor:
        self.calls.append(("find", session))
        return Cursor([dict(row) for row in self.rows if all(row.get(key) == value for key, value in query.items())])

    def insert_one(self, document: dict[str, object], *, session: object) -> object:
        self.calls.append(("insert_one", session))
        self.rows.append(dict(document))
        return object()


def test_collection_and_indexes_have_formation_only_semantics() -> None:
    collection = Collection()
    ensure_indexes(collection)
    assert COLLECTION == "legal_client_matter_mandate_grants"
    assert {index["name"] for index in collection.indexes} == {
        GRANT_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        MATTER_CLIENT_INDEX_NAME,
        MATTER_CLIENT_SCOPE_INDEX_NAME,
    }
    assert not any("expireAfterSeconds" in index for index in collection.indexes)


def test_active_session_is_required_before_collection_work() -> None:
    with pytest.raises(LegalClientMatterMandateGrantRegistryTransactionRequiredError):
        persist_grant(grant(), Collection(), session=None)
    with pytest.raises(LegalClientMatterMandateGrantRegistryTransactionRequiredError):
        persist_grant(grant(), Collection(), session=type("Inactive", (), {"in_transaction": False})())


def test_insert_and_exact_replay_by_id_fingerprint_and_idempotency() -> None:
    collection = Collection()
    value = grant()
    first = persist_grant(value, collection, session=Session())
    assert first.to_dict() == value.to_dict()
    assert persist_grant(value, collection, session=Session()).to_dict() == value.to_dict()
    assert get_grant("tenant-l9b4", value.client_grant_id, collection, session=Session()) == value
    assert get_grant_by_fingerprint("tenant-l9b4", value.fingerprint, collection, session=Session()) == value
    assert len(collection.rows) == 1
    assert all(session is not None for _, session in collection.calls)


def test_divergent_identity_and_idempotency_collisions_fail_closed() -> None:
    collection = Collection()
    value = grant()
    persist_grant(value, collection, session=Session())
    with pytest.raises(LegalClientMatterMandateGrantRegistryConflictError):
        persist_grant(grant(scope_fingerprint="f" * 128), collection, session=Session())
    with pytest.raises(LegalClientMatterMandateGrantRegistryConflictError):
        persist_grant(grant(client_grant_id="other", idempotency_key=value.idempotency_key), collection, session=Session())


def test_list_is_tenant_matter_party_scoped_deterministic_and_keeps_expiry() -> None:
    collection = Collection()
    later = grant(client_grant_id="later", idempotency_key="later-key")
    earlier = grant(client_grant_id="earlier", idempotency_key="earlier-key", effective_from=later.effective_from.replace(hour=13))
    persist_grant(later, collection, session=Session())
    persist_grant(earlier, collection, session=Session())
    values = list_grants_for_matter_client("tenant-l9b4", "matter-l9b4", "party-l9b4", collection, session=Session())
    assert [value.client_grant_id for value in values] == ["earlier", "later"]
    assert values[0].effective_until is not None


def test_tenant_isolation_and_missing_exact_identity() -> None:
    collection = Collection()
    value = grant()
    persist_grant(value, collection, session=Session())
    with pytest.raises(Exception) as raised:
        get_grant("other-tenant", value.client_grant_id, collection, session=Session())
    assert "NOT_FOUND" in str(raised.value)
    assert all(call[0] != "find_one" or call[1] is not None for call in collection.calls)


def test_persisted_corruption_rejects_extra_fields_and_changed_semantics() -> None:
    collection = Collection()
    value = grant()
    raw = value.to_dict()
    raw["unexpected"] = "x"
    collection.rows.append(raw)
    with pytest.raises(LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError):
        get_grant("tenant-l9b4", value.client_grant_id, collection, session=Session())


def test_persisted_duplicate_identity_rejects_without_selection() -> None:
    collection = Collection()
    value = grant()
    collection.rows.extend([value.to_dict(), value.to_dict()])
    with pytest.raises(LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError):
        get_grant("tenant-l9b4", value.client_grant_id, collection, session=Session())
    collection.rows.clear()
    raw = value.to_dict()
    raw["scope_fingerprint"] = "f" * 128
    collection.rows.append(raw)
    with pytest.raises(LegalClientMatterMandateGrantRegistryPersistedRecordInvalidError):
        get_grant("tenant-l9b4", value.client_grant_id, collection, session=Session())


def test_registry_has_no_currentness_or_lifecycle_authority() -> None:
    source = open("tools/eos/legal_operations/registry/legal_client_matter_mandate_grant_registry.py", encoding="utf-8").read()
    tree = ast.parse(source)
    imports = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not any("lifecycle" in module or "current" in module for module in imports)
    assert "get_current_grant" not in source
    assert "is_current" not in source
    assert "expireAfterSeconds" not in source
    assert "PII" in source


def test_no_unrelated_mutation_or_raw_pii_fields() -> None:
    collection = Collection()
    value = grant()
    persist_grant(value, collection, session=Session())
    assert len(collection.rows) == 1
    assert set(collection.rows[0]) == set(value.to_dict())
    assert not any(key in collection.rows[0] for key in ("email", "display_name", "password", "token", "jwt"))


def test_domain_return_type_is_strict() -> None:
    collection = Collection()
    value = grant()
    persist_grant(value, collection, session=Session())
    assert isinstance(get_grant("tenant-l9b4", value.client_grant_id, collection, session=Session()), LegalClientMatterMandateGrant)


# ARTIFACT: test_legal_client_matter_mandate_grant_registry.py
# VERSION: v1.0.0-L9B7-CLIENT-MANDATE-GRANT-REGISTRY-CERT
# RESULT: synthetic unit certificate only; no lifecycle persistence
# END OF WILSY OS SOVEREIGN ARTIFACT
