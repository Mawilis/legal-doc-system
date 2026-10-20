"""
WILSY OS — ENGINEERING MERKLE CHECKPOINT HISTORY CONTRACT
VERSION: 1.0.0-EMP-P15
AUTHORITY: Engineering Kernel checkpoint-domain verification.
EPITOME: Ordered evidence history and exact prefix consistency.
ABSOLUTE CANONICAL PATH: tests/unit/test_engineering_merkle_checkpoint.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: 1.0.0-EMP-P15 — Initial checkpoint red contract.
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-007.
SECURITY: Reject reordered, truncated and substituted history.
TENANT BOUNDARY: Explicit institution and log identity.
AUTHORITY BOUNDARY: No signing, approvals or external anchoring.
FINANCIAL AUTHORITY BOUNDARY: None.
"""

from dataclasses import FrozenInstanceError
import hashlib

import pytest

from tools.eos.kernel.engineering_merkle_proof import merkle_root
from tools.eos.kernel.engineering_merkle_checkpoint import (
    EngineeringMerkleCheckpoint,
    verify_checkpoint_extension,
)

INSTITUTION = "wilsy-engineering"
LOG = "engineering-release-evidence"


def evidence():
    return [b"release-A", b"release-B", b"release-C"]


def create(events, previous=None):
    return EngineeringMerkleCheckpoint.create(
        institution_id=INSTITUTION,
        log_id=LOG,
        events=events,
        previous_checkpoint=previous,
    )


def test_initial_checkpoint_commits_to_exact_ordered_events():
    value = create(evidence()[:2])
    assert value.institution_id == INSTITUTION
    assert value.log_id == LOG
    assert value.leaf_count == 2
    assert value.merkle_root == merkle_root(evidence()[:2])
    assert len(value.checkpoint_hash) == 64
    assert value.previous_checkpoint_hash is None


def test_checkpoint_is_immutable_and_roundtrips():
    value = create(evidence()[:2])
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        value.leaf_count = 99
    assert EngineeringMerkleCheckpoint.from_dict(value.to_dict()) == value


def test_extension_commits_to_predecessor_and_extended_root():
    old = create(evidence()[:2])
    new = create(evidence(), previous=old)
    assert new.leaf_count == 3
    assert new.merkle_root == merkle_root(evidence())
    assert new.previous_checkpoint_hash == old.checkpoint_hash
    assert verify_checkpoint_extension(
        old, new, evidence()[:2], evidence()
    ) is True


def test_unmodified_checkpoint_is_not_an_extension():
    old = create(evidence()[:2])
    assert verify_checkpoint_extension(
        old, old, evidence()[:2], evidence()[:2]
    ) is False


def test_reordered_history_is_not_a_consistent_extension():
    old = create(evidence()[:2])
    reordered = [b"release-B", b"release-A", b"release-C"]
    # A separately created root is not a valid extension of old.
    new = create(reordered)
    assert verify_checkpoint_extension(
        old, new, evidence()[:2], reordered
    ) is False


def test_substituted_prefix_is_not_a_consistent_extension():
    old = create(evidence()[:2])
    altered = [b"release-A", b"altered", b"release-C"]
    # A separately created root cannot establish prefix consistency.
    new = create(altered)
    assert verify_checkpoint_extension(
        old, new, evidence()[:2], altered
    ) is False


def test_wrong_predecessor_cannot_verify():
    old = create(evidence()[:2])
    unrelated = create([b"other", b"records"])
    # The unrelated history cannot be admitted as a predecessor.
    with pytest.raises(ValueError):
        create(evidence(), previous=unrelated)


def test_cross_institution_checkpoint_link_rejected():
    old = create(evidence()[:2])
    with pytest.raises((TypeError, ValueError)):
        EngineeringMerkleCheckpoint.create(
            institution_id="another-institution",
            log_id=LOG,
            events=evidence(),
            previous_checkpoint=old,
        )


def test_cross_log_checkpoint_link_rejected():
    old = create(evidence()[:2])
    with pytest.raises((TypeError, ValueError)):
        EngineeringMerkleCheckpoint.create(
            institution_id=INSTITUTION,
            log_id="different-log",
            events=evidence(),
            previous_checkpoint=old,
        )


@pytest.mark.parametrize("field", [
    "leaf_count",
    "merkle_root",
    "checkpoint_hash",
])
def test_corrupt_persisted_checkpoint_rejected(field):
    value = create(evidence()[:2])
    data = value.to_dict()
    if field == "leaf_count":
        data[field] = 999
    else:
        data[field] = "f" * 64
    with pytest.raises((TypeError, ValueError)):
        EngineeringMerkleCheckpoint.from_dict(data)


def test_untrusted_extra_authority_fields_rejected():
    data = create(evidence()[:2]).to_dict()
    data["institutionally_signed"] = True
    with pytest.raises((TypeError, ValueError)):
        EngineeringMerkleCheckpoint.from_dict(data)


def test_checkpoint_does_not_claim_external_anchoring():
    data = create(evidence()[:2]).to_dict()
    assert "signature" not in data
    assert "approved" not in data
    assert "externally_anchored" not in data


# ARTIFACT: ENGINEERING MERKLE CHECKPOINT HISTORY CONTRACT
# VERSION: 1.0.0-EMP-P15
# AUTHORITY BOUNDARY: HISTORY VERIFICATION ONLY
# TENANT POSTURE: EXPLICIT INSTITUTION AND LOG
# FAIL-CLOSED POSTURE: REORDER, FORGERY, HISTORY REWRITE REJECTED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
