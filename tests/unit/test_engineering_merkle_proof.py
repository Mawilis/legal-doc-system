"""
WILSY OS — ENGINEERING MERKLE PROOF DOMAIN CONTRACT TESTS
VERSION: 1.0.0-EMP-P3
AUTHORITY: Engineering Kernel cryptographic evidence verification
EPITOME: Deterministic domain-separated SHA3-256 Merkle commitments.
ABSOLUTE CANONICAL PATH: tests/unit/test_engineering_merkle_proof.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel
CERTIFICATION DATE: 2026-10-20
CHANGELOG: 1.0.0-EMP-P3 — Initial test-first domain contract.
COMPLIANCE: EK-001, EK-002, EK-003, EK-006, EK-007.
SECURITY: Fail closed on malformed evidence and proofs.
TENANT BOUNDARY: Pure cryptographic domain; no tenant resolution.
AUTHORITY BOUNDARY: No persistence, approval or anchoring authority.
FINANCIAL AUTHORITY: None.
"""

import hashlib
import json

import pytest

from tools.eos.kernel.engineering_merkle_proof import (
    canonical_json_bytes,
    leaf_hash,
    parent_hash,
    merkle_root,
    build_inclusion_proof,
    verify_inclusion_proof,
)


def test_canonical_json_is_key_order_independent():
    left = {"branch": "main", "checks": {"b": 2, "a": 1}}
    right = {"checks": {"a": 1, "b": 2}, "branch": "main"}
    assert canonical_json_bytes(left) == canonical_json_bytes(right)
    assert json.loads(canonical_json_bytes(left)) == left


def test_canonical_json_rejects_ambiguous_values():
    for value in (
        float("nan"),
        float("inf"),
        {"x": object()},
        {1: "numeric key"},
    ):
        with pytest.raises((TypeError, ValueError)):
            canonical_json_bytes(value)


def test_leaf_hash_is_domain_separated_sha3_256():
    payload = b"certified-evidence"
    expected = hashlib.sha3_256(
        b"WILSY:ENGINEERING:MERKLE:LEAF:V1\x00" + payload
    ).hexdigest()
    assert leaf_hash(payload) == expected
    assert len(leaf_hash(payload)) == 64


def test_parent_hash_uses_binary_digests():
    left = leaf_hash(b"left")
    right = leaf_hash(b"right")
    expected = hashlib.sha3_256(
        b"WILSY:ENGINEERING:MERKLE:NODE:V1\x00"
        + bytes.fromhex(left)
        + bytes.fromhex(right)
    ).hexdigest()
    assert parent_hash(left, right) == expected
    assert parent_hash(left, right) != parent_hash(right, left)


def test_root_is_deterministic_and_order_sensitive():
    values = [b"one", b"two", b"three"]
    assert merkle_root(values) == merkle_root(list(values))
    assert merkle_root(values) != merkle_root(list(reversed(values)))
    assert len(merkle_root(values)) == 64


def test_empty_tree_has_distinct_commitment():
    expected = hashlib.sha3_256(
        b"WILSY:ENGINEERING:MERKLE:EMPTY:V1\x00"
    ).hexdigest()
    assert merkle_root([]) == expected
    assert merkle_root([]) != leaf_hash(b"")


@pytest.mark.parametrize("index", [0, 1, 2, 3, 4])
def test_each_leaf_has_verifiable_inclusion(index):
    values = [f"evidence-{i}".encode() for i in range(5)]
    proof = build_inclusion_proof(values, index)
    assert verify_inclusion_proof(
        values[index], index, len(values), proof, merkle_root(values)
    ) is True


def test_tampering_fails_verification():
    values = [b"alpha", b"beta", b"gamma"]
    proof = build_inclusion_proof(values, 1)
    assert verify_inclusion_proof(
        b"altered", 1, len(values), proof, merkle_root(values)
    ) is False


def test_wrong_root_fails_verification():
    values = [b"alpha", b"beta"]
    proof = build_inclusion_proof(values, 0)
    assert verify_inclusion_proof(
        values[0], 0, len(values), proof,
        merkle_root([b"x", b"y"])
    ) is False


def test_invalid_index_rejected():
    values = [b"alpha", b"beta"]
    for index in (-1, 2):
        with pytest.raises((ValueError, IndexError)):
            build_inclusion_proof(values, index)


def test_malformed_digest_rejected():
    with pytest.raises((TypeError, ValueError)):
        parent_hash("invalid", leaf_hash(b"right"))


# ARTIFACT: ENGINEERING MERKLE PROOF DOMAIN CONTRACT TESTS
# VERSION: 1.0.0-EMP-P3
# AUTHORITY BOUNDARY: CRYPTOGRAPHIC DOMAIN TESTS ONLY
# TENANT POSTURE: NO TENANT OR PERSISTENCE ACCESS
# FAIL-CLOSED POSTURE: INVALID PROOFS MUST NOT VERIFY
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
