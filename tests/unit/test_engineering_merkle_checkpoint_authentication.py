"""
WILSY OS — ENGINEERING MERKLE CHECKPOINT AUTHENTICATION CONTRACT
VERSION: 1.0.0-EMP-P26
AUTHORITY: Public-key-only cryptographic verification.
EPITOME: Scope-bound Ed25519 verification independent of MongoDB.
ABSOLUTE CANONICAL PATH: tests/unit/test_engineering_merkle_checkpoint_authentication.py
COLLABORATION: Sovereign Python/EOS Engineering Kernel.
CERTIFICATION DATE: 2026-10-20
CHANGELOG: Test-first independent checkpoint authentication.
COMPLIANCE: EK-001, EK-002, EK-003, EK-005, EK-007.
SECURITY: Key identity, provenance, status, validity and signature checks.
TENANT BOUNDARY: Exact institution and log scope.
AUTHORITY BOUNDARY: Synthetic signing permitted in tests only.
FINANCIAL AUTHORITY BOUNDARY: None.
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
from tools.eos.kernel.engineering_merkle_checkpoint_authentication import (
    EngineeringCheckpointTrustedKey,
    EngineeringCheckpointTrustRoot,
    EngineeringCheckpointSignature,
    EngineeringCheckpointAuthenticationError,
    checkpoint_signature_message,
    verify_checkpoint_signature,
)


NOW = datetime(2026, 10, 20, 8, 0, tzinfo=timezone.utc)
DOMAIN = "WILSY:ENGINEERING:MERKLE:CHECKPOINT:AUTH:V1"
KEY_PREFIX = "engineering-checkpoint-key:"


def encoded(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def private(seed=bytes(range(32))):
    return Ed25519PrivateKey.from_private_bytes(seed)


def checkpoint(institution="wilsy-engineering", log="release-evidence"):
    return EngineeringMerkleCheckpoint.create(
        institution_id=institution,
        log_id=log,
        events=[b"A", b"B"],
    )


def trusted(private_key=None, **changes):
    signer = private_key if private_key is not None else private()
    raw = signer.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    fields = {
        "key_id": KEY_PREFIX + hashlib.sha3_512(raw).hexdigest()[:32],
        "public_key_base64url": encoded(raw),
        "institution_id": "wilsy-engineering",
        "log_id": "release-evidence",
        "valid_from": NOW - timedelta(days=1),
        "valid_until": NOW + timedelta(days=1),
        "status": "ACTIVE",
        "provenance": "WILSY_ENGINEERING_CHECKPOINT_TRUST/V1",
    }
    fields.update(changes)
    return EngineeringCheckpointTrustedKey(**fields)


def signed(first=None, signing_key=None, trust=None):
    cp = checkpoint() if first is None else first
    signer = private() if signing_key is None else signing_key
    key = trusted(signer) if trust is None else trust
    signature = EngineeringCheckpointSignature(
        checkpoint_hash=cp.checkpoint_hash,
        institution_id=cp.institution_id,
        log_id=cp.log_id,
        key_id=key.key_id,
        signature_base64url=encoded(
            signer.sign(checkpoint_signature_message(cp))
        ),
    )
    return cp, key, signature


def verify(cp, key, signature, at=NOW):
    return verify_checkpoint_signature(
        checkpoint=cp,
        signature=signature,
        trust_root=EngineeringCheckpointTrustRoot((key,)),
        verified_at=at,
    )


def test_synthetic_valid_signature_authenticates():
    cp, key, signature = signed()
    assert verify(cp, key, signature) is True


def test_signature_message_has_domain_separation():
    cp = checkpoint()
    message = checkpoint_signature_message(cp)
    assert type(message) is bytes
    assert message.startswith(DOMAIN.encode("ascii") + b"\x00")
    assert cp.checkpoint_hash.encode("ascii") in message
    assert cp.institution_id.encode("ascii") in message
    assert cp.log_id.encode("ascii") in message


def test_wrong_signer_rejected():
    cp, key, signature = signed()
    alternate = private(bytes(reversed(range(32))))
    wrong_signature = replace(
        signature,
        signature_base64url=encoded(
            alternate.sign(checkpoint_signature_message(cp))
        ),
    )
    with pytest.raises(EngineeringCheckpointAuthenticationError):
        verify(cp, key, wrong_signature)


def test_unknown_key_rejected():
    cp, key, signature = signed()
    with pytest.raises(EngineeringCheckpointAuthenticationError):
        verify_checkpoint_signature(
            checkpoint=cp,
            signature=replace(
                signature,
                key_id=KEY_PREFIX + "f" * 32,
            ),
            trust_root=EngineeringCheckpointTrustRoot((key,)),
            verified_at=NOW,
        )


@pytest.mark.parametrize("status", ["REVOKED", "RETIRED"])
def test_inactive_key_rejected(status):
    cp, _, signature = signed()
    key = trusted(status=status)
    with pytest.raises(EngineeringCheckpointAuthenticationError):
        verify(cp, key, signature)


@pytest.mark.parametrize(
    "at",
    [
        NOW - timedelta(days=2),
        NOW + timedelta(days=1),
    ],
)
def test_key_outside_validity_rejected(at):
    cp, key, signature = signed()
    with pytest.raises(EngineeringCheckpointAuthenticationError):
        verify(cp, key, signature, at=at)


def test_wrong_institution_rejected():
    cp, key, signature = signed()
    foreign = trusted(institution_id="foreign-institution")
    with pytest.raises(EngineeringCheckpointAuthenticationError):
        verify(cp, foreign, signature)


def test_wrong_log_rejected():
    cp, key, signature = signed()
    foreign = trusted(log_id="foreign-log")
    with pytest.raises(EngineeringCheckpointAuthenticationError):
        verify(cp, foreign, signature)


def test_checkpoint_substitution_rejected():
    cp, key, signature = signed()
    substitute = checkpoint(log="release-evidence")
    substitute = EngineeringMerkleCheckpoint.create(
        institution_id=substitute.institution_id,
        log_id=substitute.log_id,
        events=[b"A", b"SUBSTITUTE"],
    )
    assert substitute.checkpoint_hash != cp.checkpoint_hash
    with pytest.raises(EngineeringCheckpointAuthenticationError):
        verify(substitute, key, signature)


def test_invalid_signature_encoding_rejected():
    cp, key, signature = signed()
    with pytest.raises((ValueError, EngineeringCheckpointAuthenticationError)):
        verify(cp, key, replace(signature, signature_base64url="%%%"))


def test_duplicate_trust_key_rejected():
    key = trusted()
    with pytest.raises(EngineeringCheckpointAuthenticationError):
        EngineeringCheckpointTrustRoot((key, key))


def test_no_signing_or_external_authority_exposed():
    import tools.eos.kernel.engineering_merkle_checkpoint_authentication as module

    assert not hasattr(module, "sign_checkpoint")
    assert not hasattr(module, "generate_signing_key")
    assert not hasattr(module, "authorize_release")
    assert not hasattr(module, "publish_external_anchor")


# ARTIFACT: ENGINEERING MERKLE AUTHENTICATION RED CONTRACT
# VERSION: 1.0.0-EMP-P26
# TEST PRIVATE KEYS: SYNTHETIC AND ISOLATED
# PRODUCTION PRIVATE-KEY AUTHORITY: NONE
# EXTERNAL ANCHOR AUTHORITY: NONE
# END OF WILSY OS SOVEREIGN ARTIFACT
