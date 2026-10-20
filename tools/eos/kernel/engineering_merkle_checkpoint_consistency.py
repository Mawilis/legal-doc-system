"""
WILSY OS — ENGINEERING MERKLE COMPACT CONSISTENCY
VERSION: 1.0.0-EMP-P29
AUTHORITY: Independent append-only checkpoint consistency verification.
EPITOME: Canonical logarithmic dyadic subtree frontier.
ABSOLUTE CANONICAL PATH: tools/eos/kernel/engineering_merkle_checkpoint_consistency.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-007.
SECURITY: Strict proof shape, exact roots, checkpoint scope and hash binding.
ALGORITHM: Existing duplicate-last binary Merkle tree; not RFC6962.
TENANT BOUNDARY: Exact institution_id and log_id.
AUTHORITY BOUNDARY: No private-key, release, financial or anchor authority.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from tools.eos.kernel.engineering_merkle_checkpoint import (
    EngineeringMerkleCheckpoint,
)
from tools.eos.kernel.engineering_merkle_proof import parent_hash

_HEX = re.compile(r"[0-9a-f]{64}", re.ASCII)


class EngineeringCheckpointConsistencyError(ValueError):
    """A consistency proof cannot establish the claimed append-only extension."""


def _blocks(start: int, end: int) -> tuple[tuple[int, int], ...]:
    """Canonical maximal aligned binary decomposition of [start, end)."""
    result: list[tuple[int, int]] = []
    while start < end:
        width = 1
        while (
            start % (width * 2) == 0
            and start + width * 2 <= end
        ):
            width *= 2
        result.append((start, width))
        start += width
    return tuple(result)


def _subtree(commitments: tuple[str, ...]) -> str:
    if not commitments:
        raise EngineeringCheckpointConsistencyError(
            "EMPTY_PROOF_SUBTREE"
        )
    level = list(commitments)
    while len(level) > 1:
        level = [
            parent_hash(level[i], level[i + 1])
            for i in range(0, len(level), 2)
        ]
    return level[0]


def _frontier(
    commitments: tuple[str, ...],
    blocks: tuple[tuple[int, int], ...],
) -> tuple[str, ...]:
    return tuple(
        _subtree(commitments[start:start + width])
        for start, width in blocks
    )


def _fold(
    blocks: tuple[tuple[int, int], ...],
    hashes: tuple[str, ...],
) -> str:
    """Fold aligned blocks with the existing rightmost-duplication rule."""
    if len(blocks) != len(hashes) or not blocks:
        raise EngineeringCheckpointConsistencyError(
            "PROOF_FRONTIER_SHAPE_INVALID"
        )

    stack: list[tuple[str, int]] = []
    for (_, width), digest in zip(blocks, hashes):
        if type(digest) is not str or _HEX.fullmatch(digest) is None:
            raise EngineeringCheckpointConsistencyError(
                "PROOF_HASH_INVALID"
            )
        stack.append((digest, width))
        while len(stack) >= 2 and stack[-1][1] == stack[-2][1]:
            right, width_right = stack.pop()
            left, width_left = stack.pop()
            stack.append((parent_hash(left, right), width_left * 2))

    while len(stack) > 1:
        right, right_width = stack.pop()
        left, left_width = stack.pop()
        if right_width > left_width:
            raise EngineeringCheckpointConsistencyError(
                "PROOF_FRONTIER_ORDER_INVALID"
            )
        while right_width < left_width:
            right = parent_hash(right, right)
            right_width *= 2
        stack.append((parent_hash(left, right), left_width * 2))
    return stack[0][0]


def _validated(
    value: EngineeringMerkleCheckpoint,
) -> EngineeringMerkleCheckpoint:
    if type(value) is not EngineeringMerkleCheckpoint:
        raise EngineeringCheckpointConsistencyError(
            "CHECKPOINT_TYPE_INVALID"
        )
    try:
        return EngineeringMerkleCheckpoint.from_dict(value.to_dict())
    except (ValueError, TypeError, KeyError) as exc:
        raise EngineeringCheckpointConsistencyError(
            "CHECKPOINT_INTEGRITY_INVALID"
        ) from exc


@dataclass(frozen=True, slots=True)
class EngineeringCheckpointConsistencyProof:
    institution_id: str
    log_id: str
    old_checkpoint_hash: str
    new_checkpoint_hash: str
    old_count: int
    new_count: int
    prefix_hashes: tuple[str, ...]
    suffix_hashes: tuple[str, ...]


def build_checkpoint_consistency_proof(
    old: EngineeringMerkleCheckpoint,
    new: EngineeringMerkleCheckpoint,
) -> EngineeringCheckpointConsistencyProof:
    prior = _validated(old)
    current = _validated(new)
    if (
        prior.institution_id != current.institution_id
        or prior.log_id != current.log_id
        or prior.leaf_count < 1
        or current.leaf_count <= prior.leaf_count
        or current.previous_checkpoint_hash != prior.checkpoint_hash
        or current.leaf_commitments[:prior.leaf_count]
        != prior.leaf_commitments
    ):
        raise EngineeringCheckpointConsistencyError(
            "CHECKPOINT_EXTENSION_INVALID"
        )

    m, n = prior.leaf_count, current.leaf_count
    return EngineeringCheckpointConsistencyProof(
        institution_id=prior.institution_id,
        log_id=prior.log_id,
        old_checkpoint_hash=prior.checkpoint_hash,
        new_checkpoint_hash=current.checkpoint_hash,
        old_count=m,
        new_count=n,
        prefix_hashes=_frontier(
            prior.leaf_commitments, _blocks(0, m)
        ),
        suffix_hashes=_frontier(
            current.leaf_commitments, _blocks(m, n)
        ),
    )


def verify_checkpoint_consistency_proof(
    old: EngineeringMerkleCheckpoint,
    new: EngineeringMerkleCheckpoint,
    proof: EngineeringCheckpointConsistencyProof,
) -> bool:
    prior = _validated(old)
    current = _validated(new)
    if type(proof) is not EngineeringCheckpointConsistencyProof:
        raise EngineeringCheckpointConsistencyError(
            "PROOF_TYPE_INVALID"
        )

    m, n = prior.leaf_count, current.leaf_count
    if (
        m < 1
        or n <= m
        or proof.old_count != m
        or proof.new_count != n
        or proof.institution_id != prior.institution_id
        or proof.log_id != prior.log_id
        or current.institution_id != prior.institution_id
        or current.log_id != prior.log_id
        or proof.old_checkpoint_hash != prior.checkpoint_hash
        or proof.new_checkpoint_hash != current.checkpoint_hash
        or current.previous_checkpoint_hash != prior.checkpoint_hash
        or type(proof.prefix_hashes) is not tuple
        or type(proof.suffix_hashes) is not tuple
    ):
        raise EngineeringCheckpointConsistencyError(
            "CONSISTENCY_SCOPE_OR_LINK_INVALID"
        )

    prefix_blocks = _blocks(0, m)
    suffix_blocks = _blocks(m, n)

    if (
        len(proof.prefix_hashes) != len(prefix_blocks)
        or len(proof.suffix_hashes) != len(suffix_blocks)
        or len(proof.prefix_hashes) + len(proof.suffix_hashes)
        > 2 * n.bit_length() + 2
    ):
        raise EngineeringCheckpointConsistencyError(
            "CONSISTENCY_PROOF_SHAPE_INVALID"
        )

    old_root = _fold(prefix_blocks, proof.prefix_hashes)
    new_root = _fold(
        prefix_blocks + suffix_blocks,
        proof.prefix_hashes + proof.suffix_hashes,
    )

    if (
        old_root != prior.merkle_root
        or new_root != current.merkle_root
    ):
        raise EngineeringCheckpointConsistencyError(
            "CONSISTENCY_ROOT_MISMATCH"
        )
    return True


# ARTIFACT: ENGINEERING MERKLE COMPACT CONSISTENCY
# VERSION: 1.0.0-EMP-P29
# SOURCE ALGORITHM: DUPLICATE-LAST BINARY MERKLE
# FULL HISTORY TRANSFER IN PROOF: NONE
# SIGNING, RELEASE AND EXTERNAL ANCHOR AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
