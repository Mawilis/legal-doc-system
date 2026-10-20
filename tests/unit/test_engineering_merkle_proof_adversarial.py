"""
WILSY OS — ENGINEERING MERKLE ADVERSARIAL CERTIFICATION
VERSION: 1.0.0-EMP-P5
AUTHORITY: Engineering Kernel independent cryptographic verification.
EPITOME: Reject forged and malformed Merkle evidence.
ABSOLUTE CANONICAL PATH: tests/unit/test_engineering_merkle_proof_adversarial.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: 1.0.0-EMP-P5 — Adversarial cryptographic proof tests.
COMPLIANCE: EK-001, EK-002, EK-003, EK-006, EK-007.
SECURITY: Reject malformed identities, tampered paths and invalid JSON.
TENANT BOUNDARY: Pure cryptographic tests, no tenant lookup.
AUTHORITY BOUNDARY: Neither persistence nor release approval.
FINANCIAL AUTHORITY BOUNDARY: None.
"""

import hashlib

import pytest

from tools.eos.kernel.engineering_merkle_proof import (
    build_inclusion_proof,
    canonical_json_bytes,
    leaf_hash,
    merkle_root,
    parent_hash,
    verify_inclusion_proof,
)


def independently_computed_root(values):
    """Reference tree algorithm without invoking the production root builder."""
    prefix_leaf = b"WILSY:ENGINEERING:MERKLE:LEAF:V1\x00"
    prefix_node = b"WILSY:ENGINEERING:MERKLE:NODE:V1\x00"
    if not values:
        return hashlib.sha3_256(
            b"WILSY:ENGINEERING:MERKLE:EMPTY:V1\x00"
        ).hexdigest()
    level = [
        hashlib.sha3_256(prefix_leaf + value).digest()
        for value in values
    ]
    while len(level) > 1:
        if len(level) % 2:
            level.append(level[-1])
        level = [
            hashlib.sha3_256(
                prefix_node + level[i] + level[i + 1]
            ).digest()
            for i in range(0, len(level), 2)
        ]
    return level[0].hex()


@pytest.mark.parametrize("count", range(0, 17))
def test_root_matches_independent_algorithm(count):
    values = [f"record:{i}".encode() for i in range(count)]
    assert merkle_root(values) == independently_computed_root(values)


@pytest.mark.parametrize("count", range(1, 17))
def test_every_position_and_tree_shape(count):
    values = [f"entry-{i}".encode() for i in range(count)]
    root = independently_computed_root(values)
    for index, value in enumerate(values):
        proof = build_inclusion_proof(values, index)
        assert verify_inclusion_proof(
            value, index, count, proof, root
        )


def test_odd_tail_requires_exact_duplicate():
    values = [b"A", b"B", b"C"]
    proof = build_inclusion_proof(values, 2)
    assert proof[0] == leaf_hash(b"C")
    assert verify_inclusion_proof(
        b"C", 2, 3, proof, merkle_root(values)
    )
    altered = (leaf_hash(b"not-C"),) + proof[1:]
    assert not verify_inclusion_proof(
        b"C", 2, 3, altered, merkle_root(values)
    )


@pytest.mark.parametrize("invalid", [-1, 3, True, 0.0, "0", None])
def test_invalid_positions_fail_closed(invalid):
    values = [b"a", b"b", b"c"]
    root = merkle_root(values)
    assert not verify_inclusion_proof(
        values[0], invalid, 3,
        build_inclusion_proof(values, 0), root
    )


@pytest.mark.parametrize("invalid", [0, -1, True, 2.0, "3", None])
def test_invalid_leaf_counts_fail_closed(invalid):
    values = [b"a", b"b", b"c"]
    assert not verify_inclusion_proof(
        values[0], 0, invalid,
        build_inclusion_proof(values, 0), merkle_root(values)
    )


def test_wrong_position_and_count_cannot_verify():
    values = [b"a", b"b", b"c", b"d", b"e"]
    proof = build_inclusion_proof(values, 4)
    root = merkle_root(values)
    assert not verify_inclusion_proof(values[4], 0, 5, proof, root)
    assert not verify_inclusion_proof(values[4], 4, 4, proof, root)


def test_extra_and_missing_siblings_are_rejected():
    values = [b"a", b"b", b"c"]
    proof = build_inclusion_proof(values, 1)
    root = merkle_root(values)
    assert not verify_inclusion_proof(values[1], 1, 3, proof[:-1], root)
    assert not verify_inclusion_proof(
        values[1], 1, 3, proof + (leaf_hash(b"extra"),), root
    )


@pytest.mark.parametrize("bad", ["", "0" * 63, "G" * 64, "F" * 64, None, 3])
def test_malformed_proof_digest_rejected(bad):
    values = [b"a", b"b"]
    proof = (bad,)
    assert not verify_inclusion_proof(
        values[0], 0, 2, proof, merkle_root(values)
    )


def test_evidence_and_sibling_tampering_rejected():
    values = [b"a", b"b", b"c", b"d"]
    proof = build_inclusion_proof(values, 1)
    root = merkle_root(values)
    assert not verify_inclusion_proof(b"altered", 1, 4, proof, root)
    corrupt = (leaf_hash(b"forged"),) + proof[1:]
    assert not verify_inclusion_proof(values[1], 1, 4, corrupt, root)


def test_canonical_json_rejects_cycles_and_nonstrict_types():
    cycle = []
    cycle.append(cycle)
    with pytest.raises(ValueError):
        canonical_json_bytes(cycle)

    for value in (
        {"a": {1: "wrong"}},
        {"a": (1, 2)},
        {"a": b"bytes"},
        {"a": float("nan")},
        {"a": float("inf")},
    ):
        with pytest.raises((TypeError, ValueError)):
            canonical_json_bytes(value)


def test_parent_rejects_noncanonical_digest():
    valid = leaf_hash(b"right")
    with pytest.raises((TypeError, ValueError)):
        parent_hash("A" * 64, valid)
    with pytest.raises((TypeError, ValueError)):
        parent_hash(valid[:-1], valid)


def test_immutable_byte_input_required():
    with pytest.raises(TypeError):
        leaf_hash(bytearray(b"mutable"))
    with pytest.raises(TypeError):
        merkle_root([b"valid", bytearray(b"mutable")])


# ARTIFACT: ENGINEERING MERKLE ADVERSARIAL CERTIFICATION
# VERSION: 1.0.0-EMP-P5
# AUTHORITY BOUNDARY: PURE CRYPTOGRAPHIC TESTS ONLY
# TENANT POSTURE: NO DATABASE OR TENANT AUTHORITY
# FAIL-CLOSED POSTURE: FORGED AND MALFORMED PROOFS REJECTED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
