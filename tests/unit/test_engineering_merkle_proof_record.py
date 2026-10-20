"""
WILSY OS — ENGINEERING MERKLE IMMUTABLE PROOF RECORD TESTS
VERSION: 1.0.0-EMP-P6
AUTHORITY: Engineering Kernel evidence-record contract.
EPITOME: Immutable, scoped and independently verifiable Merkle evidence.
ABSOLUTE CANONICAL PATH: tests/unit/test_engineering_merkle_proof_record.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: 1.0.0-EMP-P6 — Initial test-first proof-record contract.
COMPLIANCE: EK-001, EK-002, EK-003, EK-006, EK-007.
SECURITY: Fail closed on corruption, identity ambiguity and replay drift.
TENANT BOUNDARY: Institutional engineering scope; no tenant inference.
AUTHORITY BOUNDARY: Record validation, not approval or persistence.
FINANCIAL AUTHORITY BOUNDARY: None.
"""

from dataclasses import FrozenInstanceError, replace
import hashlib

import pytest

from tools.eos.kernel.engineering_merkle_proof import (
    build_inclusion_proof,
    merkle_root,
)
from tools.eos.kernel.engineering_merkle_proof_record import (
    EngineeringMerkleProofRecord,
)


GIT_HEAD = "a" * 40


def valid_record():
    evidence = [b"release-evidence-A", b"release-evidence-B"]
    return EngineeringMerkleProofRecord.create(
        institution_id="wilsy-engineering",
        release_id="P4C10",
        evidence_id="P4C10-ROUTER-UNIT",
        git_head=GIT_HEAD,
        evidence=evidence[0],
        leaf_index=0,
        leaf_count=len(evidence),
        proof=build_inclusion_proof(evidence, 0),
        merkle_root=merkle_root(evidence),
    )


def test_identity_and_provenance_are_bound():
    value = valid_record()
    assert value.institution_id == "wilsy-engineering"
    assert value.release_id == "P4C10"
    assert value.evidence_id == "P4C10-ROUTER-UNIT"
    assert value.git_head == GIT_HEAD
    assert value.evidence_digest == hashlib.sha3_256(
        b"release-evidence-A"
    ).hexdigest()
    assert isinstance(value.provenance_hash, str)
    assert len(value.provenance_hash) == 64


def test_record_is_immutable():
    value = valid_record()
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        value.evidence_id = "forged"


def test_record_round_trip_preserves_verification():
    value = valid_record()
    hydrated = EngineeringMerkleProofRecord.from_dict(value.to_dict())
    assert hydrated == value
    assert hydrated.verify(b"release-evidence-A") is True


def test_changed_evidence_cannot_verify():
    assert valid_record().verify(b"tampered") is False


@pytest.mark.parametrize(
    "changed",
    (
        {"institution_id": "other-institution"},
        {"release_id": "OTHER-RELEASE"},
        {"evidence_id": "OTHER-EVIDENCE"},
        {"git_head": "b" * 40},
        {"merkle_root": "f" * 64},
        {"provenance_hash": "f" * 64},
    ),
)
def test_forged_persisted_fields_reject(changed):
    document = valid_record().to_dict()
    document.update(changed)
    with pytest.raises((TypeError, ValueError)):
        EngineeringMerkleProofRecord.from_dict(document)


def test_extra_persisted_fields_reject():
    document = valid_record().to_dict()
    document["untrusted_authority"] = "approved"
    with pytest.raises((TypeError, ValueError)):
        EngineeringMerkleProofRecord.from_dict(document)


def test_broken_proof_rejected_at_creation():
    value = valid_record()
    with pytest.raises((TypeError, ValueError)):
        EngineeringMerkleProofRecord.create(
            institution_id=value.institution_id,
            release_id=value.release_id,
            evidence_id=value.evidence_id,
            git_head=value.git_head,
            evidence=b"release-evidence-A",
            leaf_index=value.leaf_index,
            leaf_count=value.leaf_count,
            proof=(),
            merkle_root=value.merkle_root,
        )


def test_invalid_identity_rejects():
    document = valid_record().to_dict()
    document["git_head"] = "not-a-git-commit"
    with pytest.raises((TypeError, ValueError)):
        EngineeringMerkleProofRecord.from_dict(document)


def test_digest_record_does_not_claim_institutional_anchoring():
    record = valid_record()
    document = record.to_dict()
    assert "anchored" not in document
    assert "approved" not in document
    assert "signature" not in document


# ARTIFACT: ENGINEERING MERKLE IMMUTABLE PROOF RECORD TESTS
# VERSION: 1.0.0-EMP-P6
# AUTHORITY BOUNDARY: PURE RECORD CONTRACT, NOT INSTITUTIONAL ANCHOR
# TENANT POSTURE: EXPLICIT INSTITUTIONAL SCOPE
# FAIL-CLOSED POSTURE: INVALID RECORDS AND PROOFS REJECTED
# FINANCIAL EXECUTION AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
