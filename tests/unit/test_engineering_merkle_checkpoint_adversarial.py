"""
WILSY OS — ENGINEERING CHECKPOINT ADVERSARIAL ADMISSION TESTS
VERSION: 1.0.0-EMP-P17
AUTHORITY: Engineering Kernel checkpoint integrity verification.
EPITOME: Reject rewritten histories at checkpoint construction.
ABSOLUTE CANONICAL PATH: tests/unit/test_engineering_merkle_checkpoint_adversarial.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: Initial adversarial checkpoint admission tests.
COMPLIANCE: EK-001, EK-002, EK-003, EK-007.
SECURITY: Immutable sequence, canonical predecessor, fail-closed growth.
TENANT BOUNDARY: Explicit institutional and log identity.
AUTHORITY BOUNDARY: Cryptographic validation, not trusted issuance.
FINANCIAL AUTHORITY BOUNDARY: None.
"""

from dataclasses import replace

import pytest

from tools.eos.kernel.engineering_merkle_checkpoint import (
    EngineeringMerkleCheckpoint,
    verify_checkpoint_extension,
)


def checkpoint(events, previous=None):
    return EngineeringMerkleCheckpoint.create(
        institution_id="wilsy-engineering",
        log_id="release-evidence",
        events=events,
        previous_checkpoint=previous,
    )


def test_valid_growth_is_accepted():
    previous = checkpoint([b"A", b"B"])
    current = checkpoint([b"A", b"B", b"C"], previous)
    assert verify_checkpoint_extension(
        previous, current, [b"A", b"B"], [b"A", b"B", b"C"]
    )


@pytest.mark.parametrize("events", [
    [b"B", b"A", b"C"],
    [b"A", b"forged-B", b"C"],
    [b"X", b"Y", b"Z", b"W"],
])
def test_rewritten_prefix_rejected_during_creation(events):
    previous = checkpoint([b"A", b"B"])
    with pytest.raises(ValueError):
        checkpoint(events, previous)


@pytest.mark.parametrize("events", [
    [],
    [b"A"],
    [b"A", b"B"],
])
def test_non_growing_checkpoint_rejected_during_creation(events):
    previous = checkpoint([b"A", b"B"])
    with pytest.raises(ValueError):
        checkpoint(events, previous)


def test_forged_predecessor_hash_rejected():
    previous = checkpoint([b"A"])
    # Frozen checkpoint validation rejects forgery at its earliest boundary.
    with pytest.raises(ValueError, match="CHECKPOINT_PROVENANCE_MISMATCH"):
        replace(previous, checkpoint_hash="f" * 64)


def test_cross_log_and_institution_are_rejected():
    previous = checkpoint([b"A"])
    for institution, log in (
        ("other-institution", "release-evidence"),
        ("wilsy-engineering", "other-log"),
    ):
        with pytest.raises(ValueError):
            EngineeringMerkleCheckpoint.create(
                institution_id=institution,
                log_id=log,
                events=[b"A", b"B"],
                previous_checkpoint=previous,
            )


# ARTIFACT: ENGINEERING CHECKPOINT ADVERSARIAL ADMISSION TESTS
# VERSION: 1.0.0-EMP-P17
# AUTHORITY BOUNDARY: TESTS ONLY; NO SIGNING OR RELEASE APPROVAL
# TENANT POSTURE: EXPLICIT INSTITUTIONAL SCOPE
# FAIL-CLOSED POSTURE: REWRITES AND FORGED PREDECESSORS REJECTED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
