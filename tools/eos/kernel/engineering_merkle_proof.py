"""
WILSY OS — ENGINEERING MERKLE PROOF CRYPTOGRAPHIC DOMAIN
VERSION: 1.0.0-EMP-P4
AUTHORITY: Engineering Kernel cryptographic evidence verification.
EPITOME: Deterministic SHA3-256 commitments and Merkle inclusion proofs.
ABSOLUTE CANONICAL PATH: tools/eos/kernel/engineering_merkle_proof.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: 1.0.0-EMP-P4 — Initial pure cryptographic domain.
COMPLIANCE: EK-001, EK-002, EK-003, EK-006, EK-007.
SECURITY: Versioned domain separation; reject malformed input and proofs.
TENANT BOUNDARY: Pure algorithm; no tenant or principal authority.
AUTHORITY BOUNDARY: No persistence, registration, approval or anchoring.
FINANCIAL AUTHORITY BOUNDARY: None.

PROTOCOL V1:
    LEAF = SHA3-256(LEAF_PREFIX || evidence_bytes)
    NODE = SHA3-256(NODE_PREFIX || left_32_bytes || right_32_bytes)
    EMPTY = SHA3-256(EMPTY_PREFIX)
    Odd final nodes are duplicated at each level.
    Inclusion paths are ordered from leaf level to root level.
    The index and total leaf count are required to verify tree position.

These functions do not prove that any evidence has been durably anchored.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

LEAF_PREFIX = b"WILSY:ENGINEERING:MERKLE:LEAF:V1\x00"
NODE_PREFIX = b"WILSY:ENGINEERING:MERKLE:NODE:V1\x00"
EMPTY_PREFIX = b"WILSY:ENGINEERING:MERKLE:EMPTY:V1\x00"
_HEX_DIGEST = re.compile(r"[0-9a-f]{64}", re.ASCII)


def _canonical_value(value: Any, active: set[int]) -> Any:
    """Validate strict JSON values without lossy conversions or cycles."""
    if value is None or type(value) in (str, bool, int):
        return value

    if type(value) is list or type(value) is dict:
        identity = id(value)
        if identity in active:
            raise ValueError("CYCLIC_EVIDENCE_REJECTED")
        active.add(identity)
        try:
            if isinstance(value, list):
                return [_canonical_value(x, active) for x in value]
            if not isinstance(value, dict):
                raise TypeError("UNSUPPORTED_CANONICAL_JSON_VALUE")
            result: dict[str, Any] = {}
            for key, item in value.items():
                if type(key) is not str:
                    raise TypeError("NONSTRING_JSON_KEY")
                result[key] = _canonical_value(item, active)
            return result
        finally:
            active.remove(identity)

    raise TypeError("UNSUPPORTED_CANONICAL_JSON_VALUE")


def canonical_json_bytes(value: Any) -> bytes:
    """Serialize strict JSON deterministically; never coerce unsupported data."""
    normalized = _canonical_value(value, set())
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _digest_bytes(value: str) -> bytes:
    """Require exactly 32 bytes encoded as lowercase hexadecimal."""
    if type(value) is not str or _HEX_DIGEST.fullmatch(value) is None:
        raise ValueError("INVALID_SHA3_256_DIGEST")
    return bytes.fromhex(value)


def _evidence_bytes(value: bytes) -> bytes:
    """Accept immutable evidence bytes only."""
    if type(value) is not bytes:
        raise TypeError("IMMUTABLE_EVIDENCE_BYTES_REQUIRED")
    return value


def leaf_hash(evidence: bytes) -> str:
    """Commit to exact evidence bytes with the V1 leaf domain separator."""
    return hashlib.sha3_256(
        LEAF_PREFIX + _evidence_bytes(evidence)
    ).hexdigest()


def parent_hash(left: str, right: str) -> str:
    """Commit to ordered child digests using their binary representations."""
    return hashlib.sha3_256(
        NODE_PREFIX + _digest_bytes(left) + _digest_bytes(right)
    ).hexdigest()


def _leaves(evidence: list[bytes]) -> list[str]:
    """Validate every leaf before constructing a tree."""
    if type(evidence) is not list:
        raise TypeError("EVIDENCE_LIST_REQUIRED")
    return [leaf_hash(item) for item in evidence]


def _next_level(level: list[str]) -> list[str]:
    """Build one deterministic tree level, duplicating an unmatched tail."""
    result: list[str] = []
    for pos in range(0, len(level), 2):
        left = level[pos]
        right = level[pos + 1] if pos + 1 < len(level) else left
        result.append(parent_hash(left, right))
    return result


def merkle_root(evidence: list[bytes]) -> str:
    """Compute the V1 root; an empty tree has a separate commitment."""
    level = _leaves(evidence)
    if not level:
        return hashlib.sha3_256(EMPTY_PREFIX).hexdigest()
    while len(level) > 1:
        level = _next_level(level)
    return level[0]


def build_inclusion_proof(
    evidence: list[bytes],
    index: int,
) -> tuple[str, ...]:
    """Return ordered sibling digests for an existing evidence position."""
    level = _leaves(evidence)
    if (
        type(index) is not int
        or index < 0
        or index >= len(level)
    ):
        raise ValueError("INVALID_INCLUSION_INDEX")

    siblings: list[str] = []
    position = index

    while len(level) > 1:
        sibling_index = position ^ 1
        if sibling_index >= len(level):
            sibling_index = position
        siblings.append(level[sibling_index])
        level = _next_level(level)
        position //= 2

    return tuple(siblings)


def verify_inclusion_proof(
    evidence: bytes,
    index: int,
    leaf_count: int,
    proof: tuple[str, ...] | list[str],
    expected_root: str,
) -> bool:
    """Verify exact leaf position, tree shape and root without persistence.

    Malformed or altered proofs fail closed and never establish authority.
    """
    try:
        if (
            type(index) is not int
            or type(leaf_count) is not int
            or leaf_count < 1
            or not 0 <= index < leaf_count
            or type(proof) not in (tuple, list)
        ):
            return False

        expected = _digest_bytes(expected_root)
        current = leaf_hash(evidence)
        position = index
        width = leaf_count
        step = 0

        while width > 1:
            if step >= len(proof):
                return False

            sibling = proof[step]
            _digest_bytes(sibling)

            if position % 2 == 0:
                if position + 1 >= width and sibling != current:
                    return False
                current = parent_hash(current, sibling)
            else:
                current = parent_hash(sibling, current)

            position //= 2
            width = (width + 1) // 2
            step += 1

        return (
            step == len(proof)
            and bytes.fromhex(current) == expected
        )
    except (TypeError, ValueError, OverflowError):
        return False


# ARTIFACT: ENGINEERING MERKLE PROOF CRYPTOGRAPHIC DOMAIN
# VERSION: 1.0.0-EMP-P4
# AUTHORITY BOUNDARY: PURE CRYPTOGRAPHY; NO REGISTRY OR APPROVAL
# TENANT POSTURE: NO TENANT DATA ACCESS OR AUTHORIZATION
# FAIL-CLOSED POSTURE: MALFORMED EVIDENCE AND PROOFS REJECTED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
