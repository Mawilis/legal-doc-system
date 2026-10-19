"""WILSY P9-R105-P1 append-only evidence registry RED certificate."""

from pathlib import Path
import runpy

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.registry.legal_practitioner_matter_access_registry import (
    append_evidence, get_by_id, ensure_indexes,
    PractitionerMatterAccessTransactionRequired,
    PractitionerMatterAccessConflict,
    PractitionerMatterAccessPersistedInvalid,
    PractitionerMatterAccessPersistenceUnavailable,
)

ROOT = Path(__file__).resolve().parents[2]
MAKE = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_access.py")
)["_make"]


class Session:
    in_transaction = True


class Collection:
    def __init__(self):
        self.rows = []
        self.indexes = []
        self.queries = []
        self.fail_insert = False
        self.fail_find = False
        self.duplicate_insert = False

    def create_index(self, fields, **options):
        self.indexes.append((fields, options))

    def find_one(self, query, *, session):
        assert session.in_transaction is True
        self.queries.append(dict(query))
        if self.fail_find:
            raise RuntimeError("unavailable")
        rows = [
            row for row in self.rows
            if all(row.get(k) == v for k, v in query.items())
        ]
        if len(rows) > 1:
            raise RuntimeError("duplicate identities")
        return dict(rows[0]) if rows else None

    def insert_one(self, document, *, session):
        assert session.in_transaction is True
        if self.duplicate_insert:
            raise DuplicateKeyError("unique collision")
        if self.fail_insert:
            raise RuntimeError("insert unavailable")
        self.rows.append(dict(document))


def test_exact_insert_and_read():
    evidence = MAKE()
    col, tx = Collection(), Session()
    assert append_evidence(
        evidence=evidence, collection=col, session=tx
    ) == evidence
    assert len(col.rows) == 1
    assert get_by_id(
        tenant_id=evidence.tenant_id,
        access_evidence_id=evidence.access_evidence_id,
        collection=col,
        session=tx,
    ) == evidence


def test_exact_replay_one_row():
    item, col, tx = MAKE(), Collection(), Session()
    for _ in range(2):
        assert append_evidence(
            evidence=item, collection=col, session=tx
        ) == item
    assert len(col.rows) == 1


def test_transaction_required_before_database_access():
    item, col = MAKE(), Collection()
    for invalid in (None, object(), type("Inactive", (), {
        "in_transaction": False
    })()):
        with pytest.raises(PractitionerMatterAccessTransactionRequired):
            append_evidence(
                evidence=item, collection=col, session=invalid
            )
    assert not col.rows and not col.queries


def test_exact_tenant_identity_predicate():
    item, col = MAKE(), Collection()
    append_evidence(evidence=item, collection=col, session=Session())
    assert col.queries[0] == {
        "tenant_id": item.tenant_id,
        "access_evidence_id": item.access_evidence_id,
    }


def test_persisted_fingerprint_corruption_rejected():
    item, col = MAKE(), Collection()
    append_evidence(evidence=item, collection=col, session=Session())
    col.rows[0]["fingerprint"] = "0" * 128
    with pytest.raises(PractitionerMatterAccessPersistedInvalid):
        get_by_id(
            tenant_id=item.tenant_id,
            access_evidence_id=item.access_evidence_id,
            collection=col,
            session=Session(),
        )


def test_unique_collision_fails_closed():
    col = Collection()
    col.duplicate_insert = True
    with pytest.raises(PractitionerMatterAccessConflict):
        append_evidence(
            evidence=MAKE(), collection=col, session=Session()
        )
    assert not col.rows


def test_persistence_outage_fails_closed():
    col = Collection()
    col.fail_insert = True
    with pytest.raises(PractitionerMatterAccessPersistenceUnavailable):
        append_evidence(
            evidence=MAKE(), collection=col, session=Session()
        )


def test_indexes_unique_and_no_ttl():
    col = Collection()
    ensure_indexes(col)
    assert len(col.indexes) == 3
    assert all(row[1]["unique"] is True for row in col.indexes)
    assert all("expireAfterSeconds" not in row[1] for row in col.indexes)


def test_no_operational_mutation_interface():
    from tools.eos.legal_operations.registry import (
        legal_practitioner_matter_access_registry as module,
    )
    for forbidden in (
        "grant_access", "reassign", "update", "delete",
        "revoke_operational_access", "issue_policy",
    ):
        assert not hasattr(module, forbidden)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_access_registry.py
# VERSION: v1.0.0-P9-R105-P1-REGISTRY-RED
# END OF WILSY OS SOVEREIGN ARTIFACT
