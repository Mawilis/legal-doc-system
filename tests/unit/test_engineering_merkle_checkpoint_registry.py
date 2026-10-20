"""
WILSY OS — ENGINEERING MERKLE CHECKPOINT REGISTRY CONTRACT
VERSION: 1.0.0-EMP-P20
AUTHORITY: Engineering Kernel transactional history certification.
EPITOME: One canonical head per institutional evidence log.
ABSOLUTE CANONICAL PATH: tests/unit/test_engineering_merkle_checkpoint_registry.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: Initial test-first current-head and history CAS contract.
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-007.
SECURITY: Immutable revisions, strict replay, fail-closed CAS.
TENANT BOUNDARY: Explicit institution_id and log_id.
TRANSACTION BOUNDARY: Caller-owned active MongoDB transaction.
AUTHORITY BOUNDARY: No issuance, signature, approval or external anchoring.
FINANCIAL AUTHORITY BOUNDARY: None.
"""

from copy import deepcopy

import pytest

from tools.eos.kernel.engineering_merkle_checkpoint import (
    EngineeringMerkleCheckpoint,
)
from tools.eos.kernel.engineering_merkle_checkpoint_registry import (
    EngineeringMerkleCheckpointRegistry,
    EngineeringMerkleCheckpointTransactionRequired,
    EngineeringMerkleCheckpointConflict,
    EngineeringMerkleCheckpointPersistedInvalid,
)


class Session:
    def __init__(self, active=True):
        self.in_transaction = active


class Result:
    def __init__(self, matched_count=0):
        self.matched_count = matched_count


class Collection:
    def __init__(self):
        self.rows = []
        self.indexes = []

    def create_index(self, keys, **kwargs):
        self.indexes.append((tuple(keys), dict(kwargs)))
        return kwargs.get("name")

    def find_one(self, query, **kwargs):
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return deepcopy(row)
        return None

    def find(self, query, **kwargs):
        return [
            deepcopy(row)
            for row in self.rows
            if all(row.get(key) == value for key, value in query.items())
        ]

    def insert_one(self, document, **kwargs):
        from pymongo.errors import DuplicateKeyError
        row = deepcopy(document)
        # Model the immutable history identity and one current pointer.
        if "checkpoint_hash" in row:
            identity = (
                "institution_id", "log_id", "checkpoint_hash"
            )
        else:
            identity = ("institution_id", "log_id")

        for existing in self.rows:
            if all(existing.get(k) == row.get(k) for k in identity):
                raise DuplicateKeyError("identity collision")

        self.rows.append(row)
        return object()

    def update_one(self, query, update, **kwargs):
        for index, existing in enumerate(self.rows):
            if all(existing.get(k) == v for k, v in query.items()):
                assert set(update) == {"$set"}
                updated = deepcopy(existing)
                updated.update(deepcopy(update["$set"]))
                self.rows[index] = updated
                return Result(1)
        return Result(0)


def checkpoint(events, previous=None, institution="wilsy-engineering"):
    return EngineeringMerkleCheckpoint.create(
        institution_id=institution,
        log_id="release-evidence",
        events=events,
        previous_checkpoint=previous,
    )


def context():
    history = Collection()
    current = Collection()
    registry = EngineeringMerkleCheckpointRegistry(history, current)
    return history, current, registry


def test_indexes_unique_and_never_ttl():
    history, current, registry = context()
    registry.ensure_indexes()
    assert history.indexes
    assert current.indexes
    assert any(
        kwargs.get("unique") is True
        for _, kwargs in history.indexes
    )
    assert any(
        kwargs.get("unique") is True
        for _, kwargs in current.indexes
    )
    for collection in (history, current):
        assert all(
            "expireAfterSeconds" not in kwargs
            for _, kwargs in collection.indexes
        )


@pytest.mark.parametrize("session", [None, Session(False), object()])
def test_genesis_requires_active_transaction(session):
    history, current, registry = context()
    with pytest.raises(EngineeringMerkleCheckpointTransactionRequired):
        registry.create_genesis(
            checkpoint([b"A"]), session=session
        )
    assert history.rows == []
    assert current.rows == []


def test_genesis_sets_exact_current_head():
    history, current, registry = context()
    first = checkpoint([b"A"])
    assert registry.create_genesis(first, session=Session()) == first
    assert registry.get_current(
        institution_id="wilsy-engineering",
        log_id="release-evidence",
    ) == first
    assert len(history.rows) == 1
    assert len(current.rows) == 1


def test_exact_genesis_replay_is_idempotent():
    history, current, registry = context()
    first = checkpoint([b"A"])
    registry.create_genesis(first, session=Session())
    assert registry.create_genesis(first, session=Session()) == first
    assert len(history.rows) == 1
    assert len(current.rows) == 1


def test_divergent_genesis_rejected():
    history, current, registry = context()
    registry.create_genesis(checkpoint([b"A"]), session=Session())
    with pytest.raises(EngineeringMerkleCheckpointConflict):
        registry.create_genesis(
            checkpoint([b"OTHER"]), session=Session()
        )
    assert len(history.rows) == 1
    assert len(current.rows) == 1


def test_extension_advances_head_and_retains_history():
    history, current, registry = context()
    first = checkpoint([b"A"])
    second = checkpoint([b"A", b"B"], previous=first)

    registry.create_genesis(first, session=Session())
    assert registry.advance(
        second,
        expected_checkpoint_hash=first.checkpoint_hash,
        session=Session(),
    ) == second

    assert registry.get_current(
        institution_id=first.institution_id,
        log_id=first.log_id,
    ) == second
    assert registry.get_history(
        institution_id=first.institution_id,
        log_id=first.log_id,
    ) == (first, second)
    assert len(history.rows) == 2
    assert len(current.rows) == 1


def test_stale_expected_head_rejected():
    _, _, registry = context()
    first = checkpoint([b"A"])
    second = checkpoint([b"A", b"B"], previous=first)
    registry.create_genesis(first, session=Session())
    registry.advance(
        second,
        expected_checkpoint_hash=first.checkpoint_hash,
        session=Session(),
    )
    third = checkpoint([b"A", b"B", b"C"], previous=second)
    with pytest.raises(EngineeringMerkleCheckpointConflict):
        registry.advance(
            third,
            expected_checkpoint_hash=first.checkpoint_hash,
            session=Session(),
        )


def test_competing_successors_cannot_both_advance():
    history, current, registry = context()
    first = checkpoint([b"A"])
    left = checkpoint([b"A", b"B"], previous=first)
    right = checkpoint([b"A", b"OTHER"], previous=first)

    registry.create_genesis(first, session=Session())
    registry.advance(
        left,
        expected_checkpoint_hash=first.checkpoint_hash,
        session=Session(),
    )

    with pytest.raises(EngineeringMerkleCheckpointConflict):
        registry.advance(
            right,
            expected_checkpoint_hash=first.checkpoint_hash,
            session=Session(),
        )

    assert len(history.rows) == 2
    assert len(current.rows) == 1


def test_foreign_institution_has_independent_log():
    _, _, registry = context()
    left = checkpoint([b"A"])
    right = checkpoint([b"B"], institution="another-institution")
    registry.create_genesis(left, session=Session())
    registry.create_genesis(right, session=Session())

    assert registry.get_current(
        institution_id=right.institution_id,
        log_id=right.log_id,
    ) == right


def test_corrupt_history_fails_closed():
    history, _, registry = context()
    first = checkpoint([b"A"])
    registry.create_genesis(first, session=Session())
    history.rows[0]["checkpoint_hash"] = "f" * 64
    with pytest.raises(EngineeringMerkleCheckpointPersistedInvalid):
        registry.get_history(
            institution_id=first.institution_id,
            log_id=first.log_id,
        )


def test_no_unapproved_mutation_authority():
    for name in (
        "delete", "replace", "approve", "sign",
        "issue_external_anchor", "declare_anchored",
    ):
        assert not hasattr(EngineeringMerkleCheckpointRegistry, name)


# ARTIFACT: ENGINEERING MERKLE CHECKPOINT REGISTRY CONTRACT
# VERSION: 1.0.0-EMP-P20
# AUTHORITY BOUNDARY: TRANSACTIONAL CHECKPOINT REGISTRY ONLY
# TENANT POSTURE: EXPLICIT INSTITUTION AND LOG SCOPE
# FAIL-CLOSED POSTURE: STALE HEADS AND CORRUPTION REJECTED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
