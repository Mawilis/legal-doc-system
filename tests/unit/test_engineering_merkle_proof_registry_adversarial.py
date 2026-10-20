"""
WILSY OS — ENGINEERING MERKLE REGISTRY ADVERSARIAL CERTIFICATE
VERSION: 1.0.0-EMP-P11
AUTHORITY: Engineering Kernel independent persistence verification.
EPITOME: Fail-closed immutable proof-registry admission and reads.
ABSOLUTE CANONICAL PATH: tests/unit/test_engineering_merkle_proof_registry_adversarial.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: 1.0.0-EMP-P11 — Adversarial registry certificate.
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-007.
SECURITY: Reject corruption, conflicts, invalid scope and storage errors.
TENANT BOUNDARY: Explicit institutional identity.
AUTHORITY BOUNDARY: Persistence verification only.
FINANCIAL AUTHORITY BOUNDARY: None.
"""

import pytest
from pymongo.errors import DuplicateKeyError, OperationFailure

from tools.eos.kernel.engineering_merkle_proof import (
    build_inclusion_proof,
    merkle_root,
)
from tools.eos.kernel.engineering_merkle_proof_record import (
    EngineeringMerkleProofRecord,
)
from tools.eos.kernel.engineering_merkle_proof_registry import (
    EngineeringMerkleProofRegistry,
    EngineeringMerkleProofTransactionRequired,
    EngineeringMerkleProofConflict,
    EngineeringMerkleProofPersistedInvalid,
    EngineeringMerkleProofPersistenceUnavailable,
)


class Session:
    def __init__(self, active=True):
        self.in_transaction = active


class Store:
    def __init__(self):
        self.rows = []
        self.indexes = []
        self.read_error = None
        self.write_error = None
        self.index_error = None

    def create_index(self, keys, **kwargs):
        if self.index_error:
            raise self.index_error
        self.indexes.append((tuple(keys), dict(kwargs)))
        return kwargs.get("name")

    def find_one(self, query, **kwargs):
        if self.read_error:
            raise self.read_error
        for row in self.rows:
            if all(row.get(k) == v for k, v in query.items()):
                return dict(row)
        return None

    def insert_one(self, document, **kwargs):
        if self.write_error:
            raise self.write_error
        self.rows.append(dict(document))
        return object()


def record(
    *,
    institution="wilsy-engineering",
    release="P4C10",
    evidence_id="EVIDENCE-A",
    evidence=b"certified",
):
    entries = [evidence, b"other"]
    return EngineeringMerkleProofRecord.create(
        institution_id=institution,
        release_id=release,
        evidence_id=evidence_id,
        git_head="a" * 40,
        evidence=evidence,
        leaf_index=0,
        leaf_count=2,
        proof=build_inclusion_proof(entries, 0),
        merkle_root=merkle_root(entries),
    )


@pytest.mark.parametrize("value", [
    None, object(), Session(False), Session(0), Session("yes")
])
def test_inactive_or_forged_session_rejects_before_write(value):
    store = Store()
    with pytest.raises(EngineeringMerkleProofTransactionRequired):
        EngineeringMerkleProofRegistry(store).create_or_replay(
            record(), session=value
        )
    assert store.rows == []


def test_exact_replay_preserves_only_one_row():
    store = Store()
    registry = EngineeringMerkleProofRegistry(store)
    first = registry.create_or_replay(record(), session=Session())
    for _ in range(4):
        assert registry.create_or_replay(
            record(), session=Session()
        ) == first
    assert len(store.rows) == 1


def test_cross_institution_and_release_independence():
    store = Store()
    registry = EngineeringMerkleProofRegistry(store)
    for institution, release in (
        ("wilsy-engineering", "P4C10"),
        ("other-institution", "P4C10"),
        ("wilsy-engineering", "P4C11"),
    ):
        registry.create_or_replay(
            record(institution=institution, release=release),
            session=Session()
        )
    assert len(store.rows) == 3
    assert registry.get_by_identity(
        institution_id="other-institution",
        release_id="P4C10",
        evidence_id="EVIDENCE-A",
    ).institution_id == "other-institution"


@pytest.mark.parametrize("key,value", [
    ("institution_id", ""),
    ("institution_id", " wilsy"),
    ("release_id", "P4C10 "),
    ("evidence_id", ""),
    ("evidence_id", "invalid/evidence"),
])
def test_invalid_query_identity_rejects_before_storage(key, value):
    store = Store()
    kwargs = {
        "institution_id": "wilsy-engineering",
        "release_id": "P4C10",
        "evidence_id": "EVIDENCE-A",
    }
    kwargs[key] = value
    with pytest.raises(ValueError):
        EngineeringMerkleProofRegistry(store).get_by_identity(**kwargs)
    assert store.rows == []


@pytest.mark.parametrize("field", [
    "provenance_hash", "merkle_root", "evidence_digest",
    "leaf_commitment", "git_head"
])
def test_corrupt_persisted_field_fails_closed(field):
    store = Store()
    registry = EngineeringMerkleProofRegistry(store)
    registry.create_or_replay(record(), session=Session())
    store.rows[0][field] = "f" * (40 if field == "git_head" else 64)
    with pytest.raises(EngineeringMerkleProofPersistedInvalid):
        registry.get_by_identity(
            institution_id="wilsy-engineering",
            release_id="P4C10",
            evidence_id="EVIDENCE-A",
        )


def test_extra_storage_field_rejects():
    store = Store()
    registry = EngineeringMerkleProofRegistry(store)
    registry.create_or_replay(record(), session=Session())
    store.rows[0]["untrusted_approved"] = True
    with pytest.raises(EngineeringMerkleProofPersistedInvalid):
        registry.get_by_identity(
            institution_id="wilsy-engineering",
            release_id="P4C10",
            evidence_id="EVIDENCE-A",
        )


def test_duplicate_key_race_fails_closed():
    store = Store()
    store.write_error = DuplicateKeyError("unique identity collision")
    with pytest.raises(EngineeringMerkleProofConflict):
        EngineeringMerkleProofRegistry(store).create_or_replay(
            record(), session=Session()
        )
    assert store.rows == []


@pytest.mark.parametrize("operation", ["read", "write", "index"])
def test_storage_failures_are_typed(operation):
    store = Store()
    failure = OperationFailure("simulated Mongo unavailable", code=91)
    setattr(store, operation + "_error", failure)
    registry = EngineeringMerkleProofRegistry(store)
    with pytest.raises(EngineeringMerkleProofPersistenceUnavailable):
        if operation == "index":
            registry.ensure_indexes()
        elif operation == "read":
            registry.get_by_identity(
                institution_id="wilsy-engineering",
                release_id="P4C10",
                evidence_id="EVIDENCE-A",
            )
        else:
            registry.create_or_replay(record(), session=Session())
    assert store.rows == []


def test_divergent_identity_replay_cannot_overwrite():
    store = Store()
    registry = EngineeringMerkleProofRegistry(store)
    original = record()
    registry.create_or_replay(original, session=Session())
    with pytest.raises(EngineeringMerkleProofConflict):
        registry.create_or_replay(
            record(evidence=b"different"),
            session=Session()
        )
    assert store.rows == [original.to_dict()]


def test_no_mutating_or_anchor_apis_exposed():
    for name in (
        "update", "delete", "replace", "approve",
        "sign", "declare_anchored", "issue_checkpoint",
    ):
        assert not hasattr(EngineeringMerkleProofRegistry, name)


# ARTIFACT: ENGINEERING MERKLE REGISTRY ADVERSARIAL CERTIFICATE
# VERSION: 1.0.0-EMP-P11
# AUTHORITY BOUNDARY: TESTS ONLY; NO REGISTRATION OR ANCHOR GRANT
# TENANT POSTURE: INSTITUTIONAL SCOPE IS EXPLICIT
# FAIL-CLOSED POSTURE: PERSISTENCE ERRORS AND COLLISIONS REJECTED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
