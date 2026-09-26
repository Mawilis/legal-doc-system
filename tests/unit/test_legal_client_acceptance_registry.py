"""Direct certificate for the durable L9A2 client-acceptance registry.

VERSION: v1.0.0-L9A2-CLIENT-ACCEPTANCE-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_client_acceptance_registry.py
AUTHORITY BOUNDARY: Immutable client-acceptance persistence/read evidence only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Iterator

import pytest

from tools.eos.legal_operations.domain.legal_client_acceptance import (
    ACCEPTANCE_FIELDS,
    LegalClientAcceptance,
    record_legal_client_acceptance,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import CaseMatter
from tools.eos.legal_operations.registry import legal_client_acceptance_registry as registry


NOW = datetime(2026, 9, 26, 12, 0, 0, 123456, tzinfo=timezone.utc)
FP_A = "a" * 128
FP_B = "b" * 128


class Session:
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
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []
        self.sessions: list[Any] = []

    def with_options(self, **_kwargs: Any) -> "Collection":
        return self

    def create_index(
        self,
        keys: list[tuple[str, int]],
        *,
        unique: bool,
        name: str,
    ) -> str:
        self.indexes.append({"key": keys, "unique": unique, "name": name})
        return name

    def find(self, query: dict[str, object], *, session: Any) -> Cursor:
        self.sessions.append(session)
        return Cursor([
            deepcopy(row)
            for row in self.rows
            if all(row.get(key) == value for key, value in query.items())
        ])

    def insert_one(self, document: dict[str, object], *, session: Any) -> Result:
        self.sessions.append(session)
        row = deepcopy(document)
        row["_id"] = f"id-{len(self.rows) + 1}"
        self.rows.append(row)
        return Result()


def matter(tenant: str = "tenant-law", matter_id: str = "matter-1") -> CaseMatter:
    return CaseMatter(
        tenant_id=tenant,
        case_matter_id=matter_id,
        matter_reference=f"REF-{matter_id}",
        opened_at=NOW,
        evidence_reference=f"intake:{matter_id}",
    )


def acceptance(
    *,
    tenant: str = "tenant-law",
    matter_id: str = "matter-1",
    acceptance_id: str = "acceptance-1",
    actor: str = "principal-client-1",
    scope: str = "client-information-review:v1",
) -> LegalClientAcceptance:
    return record_legal_client_acceptance(
        case_matter=matter(tenant, matter_id),
        acceptance_id=acceptance_id,
        party_id="party-1",
        subject_reference="client:acme-1",
        subject_identity_fingerprint=FP_A,
        acceptance_scope=scope,
        actor_principal_id=actor,
        accepted_at=NOW,
        source_evidence_reference="client-evidence:1",
        source_evidence_fingerprint=FP_B,
    )


def test_index_contract_is_exact_tenant_scoped_and_has_no_ttl() -> None:
    collection = Collection()
    registry.ensure_indexes(collection)
    assert collection.indexes == [
        {
            "key": [("tenant_id", 1), ("acceptance_id", 1)],
            "unique": True,
            "name": registry.ACCEPTANCE_ID_INDEX_NAME,
        },
        {
            "key": [("tenant_id", 1), ("fingerprint", 1)],
            "unique": True,
            "name": registry.FINGERPRINT_INDEX_NAME,
        },
        {
            "key": [("tenant_id", 1), ("case_matter_id", 1), ("accepted_at", -1)],
            "unique": False,
            "name": registry.MATTER_LOOKUP_INDEX_NAME,
        },
    ]


@pytest.mark.parametrize(
    "operation",
    ["persist", "get", "fingerprint", "list"],
)
def test_every_operational_path_requires_active_transaction(operation: str) -> None:
    collection = Collection()
    value = acceptance()
    with pytest.raises(registry.LegalClientAcceptanceRegistryTransactionRequiredError):
        if operation == "persist":
            registry.persist_acceptance(value, collection, session=None)
        elif operation == "get":
            registry.get_acceptance(value.tenant_id, value.acceptance_id, collection, session=Session(False))
        elif operation == "fingerprint":
            registry.get_acceptance_by_fingerprint(value.tenant_id, value.fingerprint, collection, session=None)
        else:
            registry.list_matter_acceptances(value.tenant_id, value.case_matter_id, collection, session=Session(False))


def test_exact_persist_replay_preserves_one_row_and_session() -> None:
    collection = Collection()
    session = Session()
    value = acceptance()
    created = registry.persist_acceptance(value, collection, session=session)
    replay = registry.persist_acceptance(value, collection, session=session)
    assert created == replay == value
    assert len(collection.rows) == 1
    assert all(item is session for item in collection.sessions)
    assert collection.rows[0]["accepted_at"] == "2026-09-26T12:00:00.123456Z"


def test_divergent_same_acceptance_identity_fails_without_mutation() -> None:
    collection = Collection()
    session = Session()
    first = acceptance()
    registry.persist_acceptance(first, collection, session=session)
    divergent = acceptance(actor="principal-client-2")
    with pytest.raises(registry.LegalClientAcceptanceRegistryConflictError) as raised:
        registry.persist_acceptance(divergent, collection, session=session)
    assert raised.value.code == "L9A2_ACCEPTANCE_CONFLICT"
    assert len(collection.rows) == 1


def test_tenant_and_matter_reads_are_exact() -> None:
    collection = Collection()
    session = Session()
    values = [
        acceptance(acceptance_id="acceptance-b"),
        acceptance(matter_id="matter-2", acceptance_id="acceptance-a"),
        acceptance(tenant="tenant-other", acceptance_id="acceptance-c"),
    ]
    for value in values:
        registry.persist_acceptance(value, collection, session=session)

    assert registry.get_acceptance("tenant-law", "acceptance-b", collection, session=session) == values[0]
    assert registry.get_acceptance_by_fingerprint("tenant-law", values[0].fingerprint, collection, session=session) == values[0]
    assert [item.acceptance_id for item in registry.list_matter_acceptances("tenant-law", "matter-1", collection, session=session)] == ["acceptance-b"]
    with pytest.raises(registry.LegalClientAcceptanceRegistryNotFoundError):
        registry.get_acceptance("tenant-other", "acceptance-b", collection, session=session)


@pytest.mark.parametrize("field", sorted(ACCEPTANCE_FIELDS - {"fingerprint"}))
def test_corrupt_semantic_field_is_rejected(field: str) -> None:
    collection = Collection()
    session = Session()
    value = acceptance()
    registry.persist_acceptance(value, collection, session=session)
    row = collection.rows[0]
    if field in {"tenant_id", "case_matter_id", "acceptance_id", "party_id", "actor_principal_id"}:
        row[field] = "tampered"
    elif field == "accepted_at":
        row[field] = "2026-09-26T12:00:01.123456Z"
    elif field in {"matter_fingerprint", "subject_identity_fingerprint", "source_evidence_fingerprint"}:
        row[field] = "c" * 128
    elif field == "subject_reference":
        row[field] = "client:tampered"
    elif field == "acceptance_scope":
        row[field] = "client-information-review:v2"
    elif field == "source_evidence_reference":
        row[field] = "client-evidence:2"
    elif field == "schema":
        row[field] = "WILSY-OTHER/V1"
    elif field == "acceptance_version":
        row[field] = "v9"
    query_tenant = str(row["tenant_id"])
    query_acceptance_id = str(row["acceptance_id"])
    with pytest.raises(registry.LegalClientAcceptanceRegistryPersistedRecordInvalidError):
        registry.get_acceptance(query_tenant, query_acceptance_id, collection, session=session)


def test_corrupt_fingerprint_extra_and_missing_fields_are_rejected() -> None:
    collection = Collection()
    session = Session()
    value = acceptance()
    registry.persist_acceptance(value, collection, session=session)
    collection.rows[0]["fingerprint"] = "c" * 128
    with pytest.raises(registry.LegalClientAcceptanceRegistryPersistedRecordInvalidError):
        registry.get_acceptance(value.tenant_id, value.acceptance_id, collection, session=session)

    collection.rows[0] = value.to_dict() | {"_id": "id-1", "unexpected": True}
    with pytest.raises(registry.LegalClientAcceptanceRegistryPersistedRecordInvalidError):
        registry.get_acceptance(value.tenant_id, value.acceptance_id, collection, session=session)

    collection.rows[0] = value.to_dict() | {"_id": "id-1"}
    del collection.rows[0]["source_evidence_reference"]
    with pytest.raises(registry.LegalClientAcceptanceRegistryPersistedRecordInvalidError):
        registry.get_acceptance(value.tenant_id, value.acceptance_id, collection, session=session)


def test_registry_has_no_update_delete_ttl_or_external_authority() -> None:
    assert not hasattr(registry, "update_acceptance")
    assert not hasattr(registry, "delete_acceptance")
    assert not any("ttl" in name.casefold() for name in dir(registry))
    value = acceptance()
    assert set(value.to_dict()) == set(ACCEPTANCE_FIELDS)
    assert not {
        "engagement_active", "representation_active", "court_authorized",
        "financial_authority", "portal_access",
    } & set(value.to_dict())


# ARTIFACT: test_legal_client_acceptance_registry.py
# VERSION: v1.0.0-L9A2-CLIENT-ACCEPTANCE-REGISTRY-CERT
# AUTHORITY BOUNDARY: immutable client-acceptance persistence/read evidence only
# TENANT POSTURE: exact tenant/matter queries and caller-session propagation
# FAIL-CLOSED POSTURE: transaction absence, corruption, divergence and TTL authority reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
