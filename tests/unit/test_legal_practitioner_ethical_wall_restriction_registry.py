"""P9-R105-P4G-P4-R2B adversarial wall registry certificate."""
from pathlib import Path
from dataclasses import replace
from typing import Any
import runpy

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.registry import (
    legal_practitioner_ethical_wall_restriction_registry as registry,
)

ROOT = Path(__file__).resolve().parents[2]
MAKE = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_ethical_wall_restriction.py")
)["make"]


class Session:
    in_transaction = True


class Cursor:
    def __init__(self, rows: list[dict[str, Any]]):
        self.rows = rows
    def limit(self, number: int):
        return iter(self.rows[:number])


class Collection:
    def __init__(self):
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[Any] = []
        self.queries: list[dict[str, Any]] = []
        self.fail_read = False
        self.fail_insert = False
        self.duplicate_insert = False
    def create_index(self, fields: Any, **options: Any):
        self.indexes.append((fields, options))
    def find_one(self, query: dict[str, Any], *, session: Any):
        assert session.in_transaction is True
        self.queries.append(dict(query))
        if self.fail_read:
            raise RuntimeError("unavailable")
        found = [
            x for x in self.rows
            if all(x.get(k) == v for k, v in query.items())
        ]
        if len(found) > 1:
            raise RuntimeError("duplicate")
        return dict(found[0]) if found else None
    def find(self, query: dict[str, Any], *, session: Any):
        assert session.in_transaction is True
        self.queries.append(dict(query))
        if self.fail_read:
            raise RuntimeError("unavailable")
        return Cursor([
            dict(x) for x in self.rows
            if all(x.get(k) == v for k, v in query.items())
        ])
    def insert_one(self, document: dict[str, Any], *, session: Any):
        assert session.in_transaction is True
        if self.duplicate_insert:
            raise DuplicateKeyError("collision")
        if self.fail_insert:
            raise RuntimeError("unavailable")
        self.rows.append(dict(document))


def test_unique_indexes_non_ttl_and_scope_reader_index():
    col = Collection()
    registry.ensure_indexes(col)
    assert len(col.indexes) == 3
    assert [x[1]["unique"] for x in col.indexes[:2]] == [True, True]
    assert "unique" not in col.indexes[2][1]
    assert all("expireAfterSeconds" not in x[1] for x in col.indexes)


def test_insert_exact_replay_and_bounded_scope_history():
    item, col, tx = MAKE(), Collection(), Session()
    assert registry.append_restriction(
        restriction=item, collection=col, session=tx
    ) == item
    assert registry.append_restriction(
        restriction=item, collection=col, session=tx
    ) == item
    assert len(col.rows) == 1
    assert registry.get_by_id(
        tenant_id=item.tenant_id, restriction_id=item.restriction_id,
        collection=col, session=tx,
    ) == item
    assert registry.list_restrictions_for_scope(
        tenant_id=item.tenant_id, case_matter_id=item.case_matter_id,
        restricted_practitioner_principal_id=
            item.restricted_practitioner_principal_id,
        collection=col, session=tx,
    ) == (item,)
    assert col.queries[-1] == {
        "tenant_id": item.tenant_id,
        "case_matter_id": item.case_matter_id,
        "restricted_practitioner_principal_id":
            item.restricted_practitioner_principal_id,
    }


def test_divergent_replay_denied():
    col, tx = Collection(), Session()
    registry.append_restriction(
        restriction=MAKE(), collection=col, session=tx,
    )
    with pytest.raises(registry.EthicalWallConflict):
        registry.append_restriction(
            restriction=MAKE(reason_code="CLIENT_CONFIDENTIALITY"),
            collection=col, session=tx,
        )
    assert len(col.rows) == 1


def test_independent_restrictions_append_without_lifting():
    col, tx = Collection(), Session()
    a = MAKE()
    b = MAKE(
        restriction_id="restriction-2",
        reason_code="CLIENT_CONFIDENTIALITY",
    )
    for item in (a, b):
        registry.append_restriction(
            restriction=item, collection=col, session=tx,
        )
    result = registry.list_restrictions_for_scope(
        tenant_id=a.tenant_id, case_matter_id=a.case_matter_id,
        restricted_practitioner_principal_id=
            a.restricted_practitioner_principal_id,
        collection=col, session=tx,
    )
    assert len(result) == 2
    assert set(result) == {a, b}


@pytest.mark.parametrize("invalid", [
    None, object(), type("Inactive", (), {"in_transaction": False})(),
])
def test_transaction_required_before_storage(invalid):
    col = Collection()
    with pytest.raises(registry.EthicalWallTransactionRequired):
        registry.append_restriction(
            restriction=MAKE(), collection=col, session=invalid,
        )
    with pytest.raises(registry.EthicalWallTransactionRequired):
        registry.list_restrictions_for_scope(
            tenant_id="tenant-1", case_matter_id="matter-1",
            restricted_practitioner_principal_id="practitioner-1",
            collection=col, session=invalid,
        )
    assert not col.queries and not col.rows


def test_tenant_isolation_on_id_and_history():
    item, col, tx = MAKE(), Collection(), Session()
    registry.append_restriction(
        restriction=item, collection=col, session=tx,
    )
    assert registry.get_by_id(
        tenant_id="another-tenant", restriction_id=item.restriction_id,
        collection=col, session=tx,
    ) is None
    assert registry.list_restrictions_for_scope(
        tenant_id="another-tenant", case_matter_id=item.case_matter_id,
        restricted_practitioner_principal_id=
            item.restricted_practitioner_principal_id,
        collection=col, session=tx,
    ) == ()


def test_tampered_persisted_evidence_denied():
    item, col, tx = MAKE(), Collection(), Session()
    registry.append_restriction(
        restriction=item, collection=col, session=tx,
    )
    col.rows[0]["reason_code"] = "CLIENT_CONFIDENTIALITY"
    with pytest.raises(registry.EthicalWallPersistedInvalid):
        registry.get_by_id(
            tenant_id=item.tenant_id, restriction_id=item.restriction_id,
            collection=col, session=tx,
        )
    with pytest.raises(registry.EthicalWallPersistedInvalid):
        registry.list_restrictions_for_scope(
            tenant_id=item.tenant_id, case_matter_id=item.case_matter_id,
            restricted_practitioner_principal_id=
                item.restricted_practitioner_principal_id,
            collection=col, session=tx,
        )


def test_foreign_record_from_untrusted_adapter_denied():
    col, tx = Collection(), Session()
    foreign = MAKE(tenant_id="another-tenant").to_dict()
    col.rows.append(foreign)
    # A malicious adapter may return foreign records despite an exact query.
    col.find = lambda query, *, session: Cursor([foreign])
    with pytest.raises(registry.EthicalWallPersistedInvalid):
        registry.list_restrictions_for_scope(
            tenant_id="tenant-1", case_matter_id="matter-1",
            restricted_practitioner_principal_id="practitioner-1",
            collection=col, session=tx,
        )


def test_history_truncation_denied():
    col = Collection()
    col.find = lambda query, *, session: Cursor(
        [MAKE().to_dict()] * (registry.MAX_HISTORY_READS + 1)
    )
    with pytest.raises(registry.EthicalWallHistoryIncomplete):
        registry.list_restrictions_for_scope(
            tenant_id="tenant-1", case_matter_id="matter-1",
            restricted_practitioner_principal_id="practitioner-1",
            collection=col, session=Session(),
        )


def test_duplicate_history_row_denied():
    item, col = MAKE(), Collection()
    col.rows.extend([item.to_dict(), item.to_dict()])
    with pytest.raises(registry.EthicalWallPersistedInvalid):
        registry.list_restrictions_for_scope(
            tenant_id=item.tenant_id, case_matter_id=item.case_matter_id,
            restricted_practitioner_principal_id=
                item.restricted_practitioner_principal_id,
            collection=col, session=Session(),
        )


def test_duplicate_insert_and_outage_denied():
    for flag, error in (
        ("duplicate_insert", registry.EthicalWallConflict),
        ("fail_insert", registry.EthicalWallPersistenceUnavailable),
        ("fail_read", registry.EthicalWallPersistenceUnavailable),
    ):
        col = Collection()
        setattr(col, flag, True)
        with pytest.raises(error):
            registry.append_restriction(
                restriction=MAKE(), collection=col, session=Session(),
            )
        assert col.rows == []


def test_no_lift_waiver_grant_or_delete_interface():
    for name in (
        "waive", "lift", "delete", "update", "grant_access",
        "clear_wall", "reassign", "authorize",
    ):
        assert not hasattr(registry, name)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P4-R2B
# END OF WILSY OS SOVEREIGN ARTIFACT
