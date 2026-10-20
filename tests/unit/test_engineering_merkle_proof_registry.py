"""
WILSY OS — ENGINEERING MERKLE REGISTRY TEST-FIRST CONTRACT
VERSION: 1.0.0-EMP-P9
AUTHORITY: Engineering Kernel persistence verification.
EPITOME: Immutable, scoped and transactional Merkle-proof admission.
ABSOLUTE CANONICAL PATH: tests/unit/test_engineering_merkle_proof_registry.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: 1.0.0-EMP-P9 — Durable-registry red contract.
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-007.
SECURITY: Active transaction, exact replay, scope and corruption checks.
TENANT BOUNDARY: Explicit institution_id; no ambient authority.
AUTHORITY BOUNDARY: Persistence only; no approval or signing.
FINANCIAL AUTHORITY BOUNDARY: None.
"""

import pytest

from tools.eos.kernel.engineering_merkle_proof import (
    merkle_root,
    build_inclusion_proof,
)
from tools.eos.kernel.engineering_merkle_proof_record import (
    EngineeringMerkleProofRecord,
)
from tools.eos.kernel.engineering_merkle_proof_registry import (
    EngineeringMerkleProofRegistry,
    EngineeringMerkleProofTransactionRequired,
    EngineeringMerkleProofConflict,
    EngineeringMerkleProofPersistedInvalid,
)


class Session:
    def __init__(self, active=True):
        self.in_transaction = active


class FakeCollection:
    def __init__(self):
        self.rows = []
        self.indexes = []

    def create_index(self, keys, **kwargs):
        self.indexes.append((tuple(keys), kwargs))
        return kwargs.get("name", "unnamed")

    def find_one(self, query, **kwargs):
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return dict(row)
        return None

    def insert_one(self, document, **kwargs):
        self.rows.append(dict(document))
        return object()


def proof_record(evidence_id="EVIDENCE-A", evidence=b"A"):
    leaves = [evidence, b"B"]
    return EngineeringMerkleProofRecord.create(
        institution_id="wilsy-engineering",
        release_id="P4C10",
        evidence_id=evidence_id,
        git_head="a" * 40,
        evidence=evidence,
        leaf_index=0,
        leaf_count=2,
        proof=build_inclusion_proof(leaves, 0),
        merkle_root=merkle_root(leaves),
    )


def test_indexes_are_unique_and_have_no_ttl():
    store = FakeCollection()
    registry = EngineeringMerkleProofRegistry(store)
    registry.ensure_indexes()
    assert store.indexes
    assert any(
        options.get("unique") is True
        for _, options in store.indexes
    )
    assert all(
        "expireAfterSeconds" not in options
        for _, options in store.indexes
    )


def test_missing_or_inactive_transaction_rejected():
    store = FakeCollection()
    registry = EngineeringMerkleProofRegistry(store)
    for session in (None, Session(False)):
        with pytest.raises(EngineeringMerkleProofTransactionRequired):
            registry.create_or_replay(proof_record(), session=session)
    assert store.rows == []


def test_create_and_exact_replay_are_deterministic():
    store = FakeCollection()
    registry = EngineeringMerkleProofRegistry(store)
    record = proof_record()
    first = registry.create_or_replay(record, session=Session())
    second = registry.create_or_replay(record, session=Session())
    assert first == second == record
    assert len(store.rows) == 1


def test_divergent_replay_rejected():
    store = FakeCollection()
    registry = EngineeringMerkleProofRegistry(store)
    registry.create_or_replay(proof_record(), session=Session())
    with pytest.raises(EngineeringMerkleProofConflict):
        registry.create_or_replay(
            proof_record(evidence=b"altered"),
            session=Session(),
        )
    assert len(store.rows) == 1


def test_explicit_institution_and_release_scope_required():
    store = FakeCollection()
    registry = EngineeringMerkleProofRegistry(store)
    record = proof_record()
    registry.create_or_replay(record, session=Session())

    assert registry.get_by_identity(
        institution_id="wilsy-engineering",
        release_id="P4C10",
        evidence_id="EVIDENCE-A",
    ) == record

    assert registry.get_by_identity(
        institution_id="another-institution",
        release_id="P4C10",
        evidence_id="EVIDENCE-A",
    ) is None


def test_corrupt_persisted_record_fails_closed():
    store = FakeCollection()
    registry = EngineeringMerkleProofRegistry(store)
    registry.create_or_replay(proof_record(), session=Session())
    store.rows[0]["provenance_hash"] = "f" * 64
    with pytest.raises(EngineeringMerkleProofPersistedInvalid):
        registry.get_by_identity(
            institution_id="wilsy-engineering",
            release_id="P4C10",
            evidence_id="EVIDENCE-A",
        )


def test_persistence_has_no_approval_or_anchor_authority():
    assert not hasattr(EngineeringMerkleProofRegistry, "approve")
    assert not hasattr(EngineeringMerkleProofRegistry, "sign")
    assert not hasattr(EngineeringMerkleProofRegistry, "declare_anchored")


# ARTIFACT: ENGINEERING MERKLE REGISTRY TEST-FIRST CONTRACT
# VERSION: 1.0.0-EMP-P9
# AUTHORITY BOUNDARY: PERSISTENCE ONLY
# TENANT POSTURE: EXPLICIT INSTITUTIONAL SCOPE
# FAIL-CLOSED POSTURE: NO TRANSACTION, REPLAY DRIFT, CORRUPTION REJECTED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
