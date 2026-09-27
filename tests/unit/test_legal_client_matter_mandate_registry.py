"""Direct certificate for the immutable client-matter mandate registry.

TITLE: WILSY OS Legal Client Matter Mandate Registry Certificate
VERSION: v1.0.0-L9B11-CLIENT-MATTER-MANDATE-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify tenant-scoped append-only mandate persistence, exact replay,
         semantic grant/acknowledgment uniqueness, strict hydration and caller
         transaction ownership without granting currentness or execution power.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_matter_mandate_registry.py
COLLABORATION / OWNERSHIP: This certificate covers only the mandate registry;
                            domain formation, currentness, lifecycle,
                            Engagement, Representation, Court and finance stay
                            separate authorities.
CERTIFICATION / UPDATE DATE: 2026-09-27
CHANGELOG: v1.0.0-L9B11 certifies indexes, immutable writes, replay/collision
           behavior, exact pair uniqueness, history, tenant isolation,
           corruption rejection and authority exclusions.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque evidence only; no secrets, PII,
                             tokens, network or canonical Mongo access.
TENANT BOUNDARY: Every operation is explicitly tenant-scoped.
AUTHORITY BOUNDARY: Caller-owned persistence only; no currentness or IAM.
FINANCIAL AUTHORITY BOUNDARY: No payment or settlement authority; Kennel EOS.
FAIL-CLOSED DECLARATION: Invalid sessions, divergent evidence and corruption
                         are rejected without repair or hidden retries.
"""
from __future__ import annotations

import ast
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

import pytest

import tools.eos.legal_operations.domain.legal_client_matter_mandate as mandate_domain

from tools.eos.legal_operations.registry.legal_client_matter_mandate_registry import (
    COLLECTION,
    FINGERPRINT_INDEX_NAME,
    HISTORY_INDEX_NAME,
    IDEMPOTENCY_INDEX_NAME,
    MANDATE_ID_INDEX_NAME,
    PAIR_INDEX_NAME,
    LegalClientMatterMandateRegistryConflictError,
    LegalClientMatterMandateRegistryNotFoundError,
    LegalClientMatterMandateRegistryPersistedRecordInvalidError,
    LegalClientMatterMandateRegistryTransactionRequiredError,
    ensure_indexes,
    get_mandate,
    get_mandate_by_fingerprint,
    list_mandates_for_matter,
    persist_mandate,
)
from tests.unit.test_legal_client_matter_mandate import mandate, matter, party


class _Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active
        self.commit_calls = 0
        self.abort_calls = 0

    def commit_transaction(self) -> None:
        self.commit_calls += 1

    def abort_transaction(self) -> None:
        self.abort_calls += 1


class _Cursor:
    def __init__(self, rows: Iterable[Mapping[str, Any]]) -> None:
        self.rows = list(rows)

    def sort(self, fields: list[tuple[str, int]]) -> "_Cursor":
        for field, direction in reversed(fields):
            self.rows.sort(key=lambda row: repr(row.get(field)), reverse=direction < 0)
        return self

    def limit(self, count: int) -> "_Cursor":
        self.rows = self.rows[:count]
        return self

    def __iter__(self):
        return iter(self.rows)


class _Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, Any]]] = []
        self.sessions: list[Any] = []

    def with_options(self, **_: Any) -> "_Collection":
        return self

    def create_index(self, fields: list[tuple[str, int]], **kwargs: Any) -> str:
        self.indexes.append((fields, kwargs))
        return str(kwargs["name"])

    def find(self, query: Mapping[str, Any], *, session: Any) -> _Cursor:
        self.sessions.append(session)
        return _Cursor(row for row in self.rows if all(row.get(k) == v for k, v in query.items()))

    def insert_one(self, document: Mapping[str, Any], *, session: Any) -> None:
        self.sessions.append(session)
        self.rows.append(dict(document))


def _write(collection: _Collection, value: Any, session: _Session | None = None) -> Any:
    active = session or _Session()
    return persist_mandate(value, collection, session=active)


def test_collection_and_indexes_are_exact_and_have_no_ttl() -> None:
    collection = _Collection()
    ensure_indexes(collection)
    assert COLLECTION == "legal_client_matter_mandates"
    assert {kwargs["name"] for _, kwargs in collection.indexes} == {
        MANDATE_ID_INDEX_NAME,
        FINGERPRINT_INDEX_NAME,
        IDEMPOTENCY_INDEX_NAME,
        HISTORY_INDEX_NAME,
        PAIR_INDEX_NAME,
    }
    assert all("expireAfterSeconds" not in kwargs for _, kwargs in collection.indexes)
    unique = {kwargs["name"]: (fields, kwargs["unique"]) for fields, kwargs in collection.indexes}
    assert unique[MANDATE_ID_INDEX_NAME][0] == [("tenant_id", 1), ("mandate_id", 1)]
    assert unique[FINGERPRINT_INDEX_NAME][0] == [("tenant_id", 1), ("fingerprint", 1)]
    assert unique[IDEMPOTENCY_INDEX_NAME][0] == [("tenant_id", 1), ("idempotency_key", 1)]
    assert unique[PAIR_INDEX_NAME][0] == [
        ("tenant_id", 1), ("client_grant_fingerprint", 1),
        ("firm_acknowledgment_fingerprint", 1),
    ]
    assert unique[HISTORY_INDEX_NAME][1] is False


@pytest.mark.parametrize("session", [None, _Session(False)])
def test_active_caller_transaction_is_required(session: Any) -> None:
    with pytest.raises(LegalClientMatterMandateRegistryTransactionRequiredError):
        persist_mandate(mandate(), _Collection(), session=session)


def test_persist_readback_and_three_exact_replays() -> None:
    collection = _Collection()
    session = _Session()
    value = mandate()
    assert _write(collection, value, session).to_dict() == value.to_dict()
    assert get_mandate(value.tenant_id, value.mandate_id, collection, session=session) == value
    assert get_mandate_by_fingerprint(value.tenant_id, value.fingerprint, collection, session=session) == value
    assert persist_mandate(value, collection, session=session) == value
    assert len(collection.rows) == 1
    assert all(item is session for item in collection.sessions)
    assert session.commit_calls == session.abort_calls == 0


@pytest.mark.parametrize(
    ("variant", "code"),
    [
        ({"scope_fingerprint": "f" * 128}, "L9B11_MANDATE_ID_COLLISION"),
        ({"scope_reference": "different-scope"}, "L9B11_MANDATE_ID_COLLISION"),
        ({"mandate_id": "other-id"}, "L9B11_IDEMPOTENCY_KEY_COLLISION"),
        ({"mandate_id": "other-id", "idempotency_key": "other-key"}, "L9B11_GRANT_ACK_PAIR_COLLISION"),
    ],
)
def test_divergent_identity_and_pair_collisions_fail_closed(variant: dict[str, object], code: str) -> None:
    collection = _Collection()
    value = mandate()
    _write(collection, value)
    with pytest.raises(LegalClientMatterMandateRegistryConflictError) as raised:
        _write(collection, mandate(**variant))
    assert raised.value.code == code
    assert len(collection.rows) == 1


def test_divergent_fingerprint_collision_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    collection = _Collection()
    value = mandate()
    _write(collection, value)
    monkeypatch.setattr(mandate_domain, "_digest", lambda _: value.fingerprint)
    divergent = mandate(mandate_id="fingerprint-collision-id", idempotency_key="fingerprint-collision-key")
    with pytest.raises(LegalClientMatterMandateRegistryConflictError) as raised:
        _write(collection, divergent)
    assert raised.value.code == "L9B11_FINGERPRINT_COLLISION"
    assert len(collection.rows) == 1


def test_distinct_provenance_is_retained_as_history_and_tenant_isolation_holds() -> None:
    collection = _Collection()
    first = mandate()
    second = mandate(
        mandate_id="mandate-l9b3-successor",
        idempotency_key="mandate-idempotency:successor",
        client_grant_fingerprint="1" * 128,
        firm_acknowledgment_fingerprint="2" * 128,
    )
    _write(collection, first)
    _write(collection, second)
    values = list_mandates_for_matter(first.tenant_id, first.case_matter_id, first.client_party_id, collection, session=_Session())
    assert values == (first, second)
    assert len(collection.rows) == 2
    other_matter = matter(tenant_id="tenant-l9b3-b", matter_id="matter-l9b3-b")
    other_party = party(source_matter=other_matter, party_id="party-l9b3-b")
    other_tenant = mandate(
        mandate_id=first.mandate_id,
        idempotency_key="tenant-b-key",
        case_matter=other_matter,
        party=other_party,
    )
    _write(collection, other_tenant)
    with pytest.raises(LegalClientMatterMandateRegistryNotFoundError):
        get_mandate_by_fingerprint(first.tenant_id, other_tenant.fingerprint, collection, session=_Session())
    assert get_mandate(other_tenant.tenant_id, other_tenant.mandate_id, collection, session=_Session()) == other_tenant
    assert list_mandates_for_matter(first.tenant_id, first.case_matter_id, first.client_party_id, collection, session=_Session()) == (first, second)


def test_strict_corruption_rejection_and_no_currentness_surface() -> None:
    collection = _Collection()
    value = mandate()
    _write(collection, value)
    collection.rows[0]["mutable_current"] = True
    with pytest.raises(LegalClientMatterMandateRegistryPersistedRecordInvalidError):
        get_mandate(value.tenant_id, value.mandate_id, collection, session=_Session())
    source = Path(__file__).parents[2] / "tools/eos/legal_operations/registry/legal_client_matter_mandate_registry.py"
    tree = ast.parse(source.read_text())
    names = {node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert not {"get_current_mandate", "is_current", "resolve_current_mandate", "latest_mandate"} & names
    text = source.read_text()
    assert "get_current_mandate" not in text
    assert "latest_mandate" not in text


def test_registry_has_no_upstream_or_downstream_persistence_imports() -> None:
    source = Path(__file__).parents[2] / "tools/eos/legal_operations/registry/legal_client_matter_mandate_registry.py"
    tree = ast.parse(source.read_text())
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    assert all("currentness" not in module for module in imports)
    assert all(not any(term in module for term in ("iam", "engagement", "representation", "court")) for module in imports)


# ARTIFACT: test_legal_client_matter_mandate_registry.py
# VERSION: v1.0.0-L9B11-CLIENT-MATTER-MANDATE-REGISTRY-CERT
# AUTHORITY BOUNDARY: unit certificate only; no production authority
# FAIL-CLOSED POSTURE: adversarial replay, corruption and scope failures fail
# END OF WILSY OS SOVEREIGN ARTIFACT
