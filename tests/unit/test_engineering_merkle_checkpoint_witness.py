"""
WILSY OS — ENGINEERING MERKLE INDEPENDENT WITNESS CONTRACT
VERSION: 1.0.0-EMP-P30
AUTHORITY: Verify independently authenticated checkpoint witness receipts.
EPITOME: Checkpoint and witness provenance cryptographically separated.
ABSOLUTE CANONICAL PATH: tests/unit/test_engineering_merkle_checkpoint_witness.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-007.
SECURITY: Detached Ed25519 signatures and independently pinned witness trust.
AUTHORITY BOUNDARY: Verification only; test-only keys; no publication.
FINANCIAL EXECUTION AUTHORITY: None.
"""

import base64
import hashlib
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.eos.kernel.engineering_merkle_checkpoint import (
    EngineeringMerkleCheckpoint,
)
from tools.eos.kernel.engineering_merkle_checkpoint_witness import (
    EngineeringCheckpointWitnessKey,
    EngineeringCheckpointWitnessTrust,
    EngineeringCheckpointWitnessReceipt,
    EngineeringCheckpointWitnessError,
    witness_receipt_message,
    verify_checkpoint_witness_receipt,
)

NOW = datetime(2026, 10, 20, 8, 0, tzinfo=timezone.utc)
WITNESS_DOMAIN = b"WILSY:ENGINEERING:MERKLE:WITNESS:V1\x00"


def encode(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def signer(seed=bytes(range(32))):
    return Ed25519PrivateKey.from_private_bytes(seed)


def checkpoint():
    return EngineeringMerkleCheckpoint.create(
        institution_id="wilsy-engineering",
        log_id="release-evidence",
        events=[b"release-A", b"release-B", b"release-C"],
    )


def fixture():
    cp = checkpoint()
    witness = signer(bytes(reversed(range(32))))
    public = witness.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    key = EngineeringCheckpointWitnessKey(
        witness_id="independent-witness-1",
        key_id="engineering-witness-key:" +
            hashlib.sha3_512(public).hexdigest()[:32],
        public_key_base64url=encode(public),
        valid_from=NOW - timedelta(days=1),
        valid_until=NOW + timedelta(days=1),
        status="ACTIVE",
        provenance="WILSY_ENGINEERING_WITNESS_TRUST/V1",
    )
    unsigned = EngineeringCheckpointWitnessReceipt(
        institution_id=cp.institution_id,
        log_id=cp.log_id,
        checkpoint_hash=cp.checkpoint_hash,
        leaf_count=cp.leaf_count,
        witness_id=key.witness_id,
        key_id=key.key_id,
        observed_at=NOW,
        signature_base64url=encode(bytes(64)),
    )
    receipt = replace(
        unsigned,
        signature_base64url=encode(
            witness.sign(witness_receipt_message(unsigned))
        ),
    )
    return cp, key, receipt


def check(cp, key, receipt):
    return verify_checkpoint_witness_receipt(
        checkpoint=cp,
        receipt=receipt,
        trust=EngineeringCheckpointWitnessTrust((key,)),
        verified_at=NOW,
    )


def test_independent_receipt_is_cryptographically_valid():
    cp, key, receipt = fixture()
    assert check(cp, key, receipt) is True


def test_witness_message_domain_separated():
    _, _, receipt = fixture()
    message = witness_receipt_message(receipt)
    assert message.startswith(WITNESS_DOMAIN)
    assert receipt.checkpoint_hash.encode("ascii") in message


def test_witness_receipt_cannot_be_substituted():
    cp, key, receipt = fixture()
    changed = EngineeringMerkleCheckpoint.create(
        institution_id=cp.institution_id,
        log_id=cp.log_id,
        events=[b"OTHER"],
    )
    with pytest.raises(EngineeringCheckpointWitnessError):
        check(changed, key, receipt)


def test_forged_receipt_signature_rejected():
    cp, key, receipt = fixture()
    forged = replace(
        receipt,
        signature_base64url=encode(bytes(64)),
    )
    with pytest.raises(EngineeringCheckpointWitnessError):
        check(cp, key, forged)


def test_unknown_witness_key_rejected():
    cp, key, receipt = fixture()
    foreign = replace(
        receipt,
        key_id="engineering-witness-key:" + "f" * 32,
    )
    with pytest.raises(EngineeringCheckpointWitnessError):
        check(cp, key, foreign)


@pytest.mark.parametrize("status", ["REVOKED", "RETIRED"])
def test_nonactive_witness_rejected(status):
    cp, key, receipt = fixture()
    with pytest.raises(EngineeringCheckpointWitnessError):
        check(cp, replace(key, status=status), receipt)


def test_expired_witness_rejected():
    cp, key, receipt = fixture()
    with pytest.raises(EngineeringCheckpointWitnessError):
        check(cp, replace(
            key,
            valid_until=NOW - timedelta(hours=1),
        ), receipt)


def test_wrong_witness_identity_rejected():
    cp, key, receipt = fixture()
    changed = replace(receipt, witness_id="another-witness")
    with pytest.raises(EngineeringCheckpointWitnessError):
        check(cp, key, changed)


def test_duplicate_witness_keys_rejected():
    _, key, _ = fixture()
    with pytest.raises(EngineeringCheckpointWitnessError):
        EngineeringCheckpointWitnessTrust((key, key))


def test_no_signing_or_external_publication_authority():
    import tools.eos.kernel.engineering_merkle_checkpoint_witness as module
    for name in (
        "sign_witness_receipt",
        "create_institutional_key",
        "publish_external_anchor",
        "authorize_release",
    ):
        assert not hasattr(module, name)


# ARTIFACT: ENGINEERING MERKLE WITNESS VERIFICATION CONTRACT
# VERSION: 1.0.0-EMP-P30
# KEYS: SYNTHETIC TEST FIXTURES ONLY
# PRODUCTION WITNESS AND EXTERNAL PUBLICATION: NOT AUTHORIZED
# END OF WILSY OS SOVEREIGN ARTIFACT
