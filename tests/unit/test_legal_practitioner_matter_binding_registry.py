"""P9-R105-P4G-P6-R7B-P2-R1 transactional binding registry tests."""
from datetime import timedelta
from pathlib import Path
from typing import Any
import runpy
import pytest

from tools.eos.legal_operations.registry import (
    legal_practitioner_matter_binding_registry as reg,
)

ROOT = Path(__file__).resolve().parents[2]
fixture = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_binding.py")
)
make = fixture["make"]
AT = fixture["AT"]


class Session:
    in_transaction = True


class Cursor:
    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def limit(self, count: int) -> list[dict[str, Any]]:
        return self.rows[:count]


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[tuple[Any, dict[str, Any]]] = []
        self.sessions: list[Any] = []
        self.fail_read = False

    def create_index(self, keys: Any, **kw: Any) -> None:
        self.indexes.append((keys, kw))

    def find(self, query: dict[str, str], *, session: Any) -> Cursor:
        self.sessions.append(session)
        if self.fail_read:
            raise RuntimeError("READ_UNAVAILABLE")
        return Cursor([
            dict(row) for row in self.rows
            if all(row.get(key) == value for key, value in query.items())
        ])

    def insert_one(self, row: dict[str, Any], *, session: Any) -> None:
        self.sessions.append(session)
        self.rows.append(dict(row))


def revoke():
    return make().revoke(
        revoked_by_principal_id="partner-2",
        revoked_at=AT + timedelta(hours=1),
        evidence_reference="revocation-evidence",
    )


def test_exact_non_ttl_indexes():
    col = Collection()
    reg.ensure_indexes(col)
    assert len(col.indexes) == 3
    assert sum(x["unique"] for _, x in col.indexes) == 2
    assert all("expireAfterSeconds" not in x for _, x in col.indexes)


def test_exact_replay_revocation_and_no_reactivation():
    col, tx = Collection(), Session()
    active = make()
    assert reg.append_binding(binding=active, collection=col, session=tx) == active
    assert reg.append_binding(binding=active, collection=col, session=tx) == active
    assert reg.resolve_current_binding(
        tenant_id=active.tenant_id, binding_id=active.binding_id,
        collection=col, session=tx,
    ) == active
    revoked = revoke()
    assert reg.append_binding(binding=revoked, collection=col, session=tx) == revoked
    assert reg.append_binding(binding=revoked, collection=col, session=tx) == revoked
    assert len(col.rows) == 2
    assert reg.resolve_current_binding(
        tenant_id=active.tenant_id, binding_id=active.binding_id,
        collection=col, session=tx,
    ) is None
    assert reg.read_binding_history(
        tenant_id=active.tenant_id, binding_id=active.binding_id,
        collection=col, session=tx,
    ) == (active, revoked)
    with pytest.raises(reg.BindingConflict):
        reg.append_binding(binding=active, collection=col, session=tx)
    assert all(item is tx for item in col.sessions)


def test_orphan_revocation_rejected():
    with pytest.raises(reg.BindingConflict):
        reg.append_binding(
            binding=revoke(), collection=Collection(), session=Session()
        )


def test_divergent_grant_and_revoke_rejected():
    col, tx = Collection(), Session()
    active = make()
    reg.append_binding(binding=active, collection=col, session=tx)
    with pytest.raises(reg.BindingConflict):
        reg.append_binding(
            binding=make(practitioner_principal_id="other"),
            collection=col, session=tx,
        )
    reg.append_binding(binding=revoke(), collection=col, session=tx)
    divergent = active.revoke(
        revoked_by_principal_id="partner-3",
        revoked_at=AT + timedelta(hours=2),
        evidence_reference="other-evidence",
    )
    with pytest.raises(reg.BindingConflict):
        reg.append_binding(binding=divergent, collection=col, session=tx)


def test_missing_active_transaction_prevents_storage():
    col = Collection()
    for session in (None, object()):
        with pytest.raises(reg.BindingTransactionRequired):
            reg.append_binding(binding=make(), collection=col, session=session)
        with pytest.raises(reg.BindingTransactionRequired):
            reg.read_binding_history(
                tenant_id="tenant-1", binding_id="binding-1",
                collection=col, session=session,
            )
    assert col.sessions == []


def test_tenant_isolation_and_no_implicit_clearance():
    col = Collection()
    reg.append_binding(binding=make(), collection=col, session=Session())
    assert reg.read_binding_history(
        tenant_id="foreign", binding_id="binding-1",
        collection=col, session=Session(),
    ) == ()
    assert reg.resolve_current_binding(
        tenant_id="foreign", binding_id="binding-1",
        collection=col, session=Session(),
    ) is None


def test_corrupt_persisted_fingerprint_denied():
    col = Collection()
    reg.append_binding(binding=make(), collection=col, session=Session())
    col.rows[0]["practitioner_principal_id"] = "tampered"
    with pytest.raises(reg.BindingPersistedInvalid):
        reg.read_binding_history(
            tenant_id="tenant-1", binding_id="binding-1",
            collection=col, session=Session(),
        )


def test_orphan_and_duplicate_persisted_history_denied():
    col = Collection()
    col.rows = [revoke().to_dict()]
    with pytest.raises(reg.BindingPersistedInvalid):
        reg.read_binding_history(
            tenant_id="tenant-1", binding_id="binding-1",
            collection=col, session=Session(),
        )
    col.rows = [make().to_dict(), make().to_dict()]
    with pytest.raises(reg.BindingPersistedInvalid):
        reg.read_binding_history(
            tenant_id="tenant-1", binding_id="binding-1",
            collection=col, session=Session(),
        )


def test_unavailable_storage_denied():
    col = Collection()
    col.fail_read = True
    with pytest.raises(reg.BindingPersistenceUnavailable):
        reg.read_binding_history(
            tenant_id="tenant-1", binding_id="binding-1",
            collection=col, session=Session(),
        )


def test_no_content_authorization_or_wall_waiver():
    for name in (
        "authorize_access", "grant_content", "waive_wall",
        "reactivate", "delete_binding", "lift_restriction",
    ):
        assert not hasattr(reg, name)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# VERSION: v1.0.0-P9-R105-P4G-P6-R7B-P2-R1
# END OF WILSY OS SOVEREIGN ARTIFACT
