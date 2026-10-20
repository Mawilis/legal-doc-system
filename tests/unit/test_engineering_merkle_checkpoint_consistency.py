"""
WILSY OS — ENGINEERING MERKLE COMPACT CONSISTENCY CONTRACT
VERSION: 1.0.0-EMP-P28
AUTHORITY: Independent append-only consistency verification.
EPITOME: Prove historical prefix preservation without full-history transfer.
ABSOLUTE CANONICAL PATH: tests/unit/test_engineering_merkle_checkpoint_consistency.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-007.
SECURITY: Both roots, history counts, scope and canonical proof binding.
ALGORITHM: Existing duplicate-last binary Merkle tree.
AUTHORITY BOUNDARY: Verification only; no signing or anchoring.
FINANCIAL EXECUTION AUTHORITY: None.
"""

from dataclasses import replace

import pytest

from tools.eos.kernel.engineering_merkle_checkpoint import (
    EngineeringMerkleCheckpoint,
)
from tools.eos.kernel.engineering_merkle_checkpoint_consistency import (
    EngineeringCheckpointConsistencyError,
    build_checkpoint_consistency_proof,
    verify_checkpoint_consistency_proof,
)


def events(count):
    return [
        ("release-evidence-" + str(i)).encode("utf-8")
        for i in range(count)
    ]


def pair(old_count, new_count, institution="wilsy-engineering"):
    old = EngineeringMerkleCheckpoint.create(
        institution_id=institution,
        log_id="release-evidence",
        events=events(old_count),
    )
    new = EngineeringMerkleCheckpoint.create(
        institution_id=institution,
        log_id="release-evidence",
        events=events(new_count),
        previous_checkpoint=old,
    )
    return old, new


@pytest.mark.parametrize(
    ("old_count", "new_count"),
    [
        (1, 2), (1, 3), (2, 3), (2, 5), (3, 4),
        (3, 7), (4, 5), (5, 6), (5, 11),
        (7, 8), (7, 16), (8, 9), (9, 17),
        (15, 16), (16, 17), (31, 64),
        (32, 65), (63, 127), (64, 129),
    ],
)
def test_compact_proof_verifies_exact_history(old_count, new_count):
    old, new = pair(old_count, new_count)
    proof = build_checkpoint_consistency_proof(old, new)

    assert verify_checkpoint_consistency_proof(old, new, proof) is True
    assert (
        len(proof.prefix_hashes) + len(proof.suffix_hashes)
        <= 2 * new_count.bit_length() + 2
    )


def test_proof_has_no_full_evidence_payload():
    old, new = pair(7, 63)
    proof = build_checkpoint_consistency_proof(old, new)
    assert not hasattr(proof, "events")
    assert not hasattr(proof, "leaf_commitments")
    assert len(proof.prefix_hashes) + len(proof.suffix_hashes) < 63


def test_substituted_checkpoint_cannot_verify():
    old, new = pair(3, 7)
    proof = build_checkpoint_consistency_proof(old, new)
    alternate = EngineeringMerkleCheckpoint.create(
        institution_id=old.institution_id,
        log_id=old.log_id,
        events=events(3) + [b"forged"] + events(3),
        previous_checkpoint=old,
    )
    with pytest.raises(EngineeringCheckpointConsistencyError):
        verify_checkpoint_consistency_proof(old, alternate, proof)


def test_wrong_institution_cannot_verify():
    old, new = pair(3, 7)
    proof = build_checkpoint_consistency_proof(old, new)
    foreign_old, foreign_new = pair(3, 7, "another-institution")
    with pytest.raises(EngineeringCheckpointConsistencyError):
        verify_checkpoint_consistency_proof(
            foreign_old, foreign_new, proof
        )


def test_tampered_prefix_hash_cannot_verify():
    old, new = pair(5, 11)
    proof = build_checkpoint_consistency_proof(old, new)
    assert proof.prefix_hashes
    forged = replace(
        proof,
        prefix_hashes=(
            ("f" * 64,) + proof.prefix_hashes[1:]
        ),
    )
    with pytest.raises(EngineeringCheckpointConsistencyError):
        verify_checkpoint_consistency_proof(old, new, forged)


def test_tampered_suffix_hash_cannot_verify():
    old, new = pair(5, 11)
    proof = build_checkpoint_consistency_proof(old, new)
    assert proof.suffix_hashes
    forged = replace(
        proof,
        suffix_hashes=(
            ("f" * 64,) + proof.suffix_hashes[1:]
        ),
    )
    with pytest.raises(EngineeringCheckpointConsistencyError):
        verify_checkpoint_consistency_proof(old, new, forged)


def test_wrong_old_checkpoint_cannot_verify():
    old, new = pair(5, 11)
    proof = build_checkpoint_consistency_proof(old, new)
    unrelated = EngineeringMerkleCheckpoint.create(
        institution_id=old.institution_id,
        log_id=old.log_id,
        events=[b"UNRELATED"] * 5,
    )
    with pytest.raises(EngineeringCheckpointConsistencyError):
        verify_checkpoint_consistency_proof(unrelated, new, proof)


def test_missing_proof_hash_fails_closed():
    old, new = pair(5, 11)
    proof = build_checkpoint_consistency_proof(old, new)
    forged = replace(proof, prefix_hashes=proof.prefix_hashes[:-1])
    with pytest.raises(EngineeringCheckpointConsistencyError):
        verify_checkpoint_consistency_proof(old, new, forged)


def test_reordered_proof_hashes_fail_closed():
    old, new = pair(5, 11)
    proof = build_checkpoint_consistency_proof(old, new)
    forged = replace(
        proof,
        suffix_hashes=tuple(reversed(proof.suffix_hashes)),
    )
    if forged != proof:
        with pytest.raises(EngineeringCheckpointConsistencyError):
            verify_checkpoint_consistency_proof(old, new, forged)


def test_non_extension_generation_rejected():
    old, new = pair(5, 11)
    with pytest.raises(EngineeringCheckpointConsistencyError):
        build_checkpoint_consistency_proof(new, old)


def test_no_external_authority_exposed():
    import tools.eos.kernel.engineering_merkle_checkpoint_consistency as module
    for name in (
        "sign_checkpoint",
        "authorize_release",
        "publish_external_anchor",
        "generate_private_key",
    ):
        assert not hasattr(module, name)


# ARTIFACT: ENGINEERING MERKLE COMPACT CONSISTENCY CONTRACT
# VERSION: 1.0.0-EMP-P28
# SOURCE AUTHORITY: EXISTING DUPLICATE-LAST MERKLE TREE
# SIGNING, FINANCIAL AND EXTERNAL ANCHOR AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
