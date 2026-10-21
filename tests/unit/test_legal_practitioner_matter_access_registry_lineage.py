"""WILSY P9-R105-P4B first-revision lineage adversarial certificate."""
from dataclasses import replace
from pathlib import Path
import runpy

import pytest

from tools.eos.legal_operations.registry import (
    legal_practitioner_matter_access_registry as registry,
)

ROOT = Path(__file__).resolve().parents[2]
REGISTRY_TESTS = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_access_registry.py")
)
DOMAIN_TESTS = runpy.run_path(
    str(ROOT / "tests/unit/test_legal_practitioner_matter_access.py")
)
Collection = REGISTRY_TESTS["Collection"]
Session = REGISTRY_TESTS["Session"]
MAKE = DOMAIN_TESTS["_make"]


def test_second_first_revision_different_identity_denied():
    collection, tx = Collection(), Session()
    first = MAKE()
    competing = _p47_replace_evidence(
        first, access_evidence_id="different-first-revision",
        fingerprint="",
    )
    assert registry.append_evidence(
        evidence=first, collection=collection, session=tx
    ) == first
    with pytest.raises(registry.PractitionerMatterAccessConflict):
        registry.append_evidence(
            evidence=competing, collection=collection, session=tx
        )
    assert len(collection.rows) == 1
    assert collection.rows[0]["fingerprint"] == first.fingerprint


def test_same_first_revision_exact_replay_preserved():
    collection, tx = Collection(), Session()
    item = MAKE()
    for _ in range(3):
        assert registry.append_evidence(
            evidence=item, collection=collection, session=tx
        ) == item
    assert len(collection.rows) == 1


def test_successor_revision_blocked_before_insert():
    collection, tx = Collection(), Session()
    first = MAKE()
    successor = _p47_replace_evidence(
        first,
        access_evidence_id="successor-2",
        revision=2,
        supersedes_fingerprint=first.fingerprint,
        fingerprint="",
    )
    with pytest.raises(registry.PractitionerMatterAccessConflict):
        registry.append_evidence(
            evidence=successor, collection=collection, session=tx
        )
    assert collection.rows == []


def test_scope_read_outage_denies_without_insert():
    collection = Collection()
    collection.fail_find = True
    with pytest.raises(
        registry.PractitionerMatterAccessPersistenceUnavailable
    ):
        registry.append_evidence(
            evidence=MAKE(), collection=collection, session=Session()
        )
    assert collection.rows == []


def test_first_revision_scope_predicate_is_exact():
    collection = Collection()
    item = MAKE()
    registry.append_evidence(
        evidence=item, collection=collection, session=Session()
    )
    assert collection.queries[-1] == {
        "tenant_id": item.tenant_id,
        "case_matter_id": item.case_matter_id,
        "practitioner_principal_id": item.practitioner_principal_id,
        "revision": 1,
    }


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_legal_practitioner_matter_access_registry_lineage.py
# VERSION: v1.0.0-P9-R105-P4B-LINEAGE-RED
# END OF WILSY OS SOVEREIGN ARTIFACT

def _p47_replace_evidence(evidence, **changes):
    from dataclasses import fields
    from tools.eos.legal_operations.service.legal_practitioner_matter_access_codec import (
        create_practitioner_matter_access,
    )
    values = {
        field.name: getattr(evidence, field.name)
        for field in fields(evidence)
        if field.name != "fingerprint"
    }
    values.update(changes)
    return create_practitioner_matter_access(**values)
