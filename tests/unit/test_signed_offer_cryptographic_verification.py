from datetime import datetime, timedelta, timezone
import hashlib

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.eos.saas.hr.signed_offer_cryptographic_verification import (
    CandidateSignerKeyTrustRecord,
    SignerKeyStatus,
    SignedOfferSignatureEnvelope,
    SignedOfferVerificationError,
    canonical_signature_payload,
    encode_signature,
    verify_signed_offer_signature,
)


NOW = datetime(2026, 11, 7, 20, 0, tzinfo=timezone.utc)
TENANT = "WILSYTENANT-4CD2FZ4O"
CANDIDATE = "CAN-SIGNED-001"
OFFER = "OFFER-SIGNED-001"
EVIDENCE = "EVD-SIGNED-001"
VERSION = "VER-SIGNED-001"
KEY_ID = "candidate-key-001"
DIGEST = hashlib.sha3_512(b"exact signed offer bytes").hexdigest()


def key_material():
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    import base64
    encoded = base64.urlsafe_b64encode(public).decode("ascii").rstrip("=")
    trust = CandidateSignerKeyTrustRecord(
        tenant_id=TENANT, candidate_id=CANDIDATE, signer_key_id=KEY_ID,
        public_key_b64url=encoded, key_fingerprint=hashlib.sha3_512(public).hexdigest(),
        valid_from=NOW - timedelta(days=1), valid_until=NOW + timedelta(days=1),
    )
    return private, trust


def envelope_for(private, *, digest=DIGEST, candidate=CANDIDATE, signed_at=NOW - timedelta(minutes=1)):
    payload = canonical_signature_payload(
        tenant_id=TENANT, candidate_id=candidate, offer_id=OFFER,
        evidence_id=EVIDENCE, evidence_version_id=VERSION,
        content_digest_sha3_512=digest, signer_key_id=KEY_ID, signed_at=signed_at,
    )
    return SignedOfferSignatureEnvelope(
        signer_key_id=KEY_ID, signed_at=signed_at,
        signature_b64url=encode_signature(private.sign(payload)),
    )


def verify(envelope, trust, *, digest=DIGEST, candidate=CANDIDATE):
    return verify_signed_offer_signature(
        tenant_id=TENANT, candidate_id=candidate, offer_id=OFFER,
        evidence_id=EVIDENCE, evidence_version_id=VERSION,
        content_digest_sha3_512=digest, envelope=envelope,
        trust=trust, verified_at=NOW,
    )


def test_ed25519_signature_binds_exact_tenant_candidate_offer_and_evidence_digest():
    private, trust = key_material()
    record = verify(envelope_for(private), trust)
    assert record.status.value == "VERIFIED"
    assert record.algorithm == "Ed25519"
    assert record.content_digest_sha3_512 == DIGEST
    assert record.verification_reference.startswith("SOV-")
    assert record.signer_key_fingerprint == trust.key_fingerprint


def test_tampered_evidence_digest_rejects_signature():
    private, trust = key_material()
    envelope = envelope_for(private)
    with pytest.raises(SignedOfferVerificationError, match="SIGNED_OFFER_SIGNATURE_INVALID"):
        verify(envelope, trust, digest=hashlib.sha3_512(b"tampered").hexdigest())


def test_signature_from_another_candidate_is_rejected():
    private, trust = key_material()
    envelope = envelope_for(private)
    with pytest.raises(SignedOfferVerificationError, match="SIGNED_OFFER_SIGNER_TRUST_INVALID"):
        verify(envelope, trust, candidate="CAN-OTHER-001")


def test_revoked_or_expired_signer_key_is_rejected():
    private, trust = key_material()
    revoked = CandidateSignerKeyTrustRecord(
        tenant_id=TENANT, candidate_id=CANDIDATE, signer_key_id=KEY_ID,
        public_key_b64url=trust.public_key_b64url, key_fingerprint=trust.key_fingerprint,
        valid_from=NOW - timedelta(days=1), valid_until=NOW + timedelta(days=1),
        status=SignerKeyStatus.REVOKED, revoked_at=NOW - timedelta(seconds=1),
    )
    with pytest.raises(SignedOfferVerificationError, match="SIGNED_OFFER_SIGNER_TRUST_INVALID"):
        verify(envelope_for(private), revoked)

    expired = CandidateSignerKeyTrustRecord(
        tenant_id=TENANT, candidate_id=CANDIDATE, signer_key_id=KEY_ID,
        public_key_b64url=trust.public_key_b64url, key_fingerprint=trust.key_fingerprint,
        valid_from=NOW - timedelta(days=2), valid_until=NOW - timedelta(days=1),
    )
    with pytest.raises(SignedOfferVerificationError, match="SIGNED_OFFER_SIGNER_TRUST_INVALID"):
        verify(envelope_for(private), expired)


def test_invalid_signature_bytes_reject_without_creating_verification_record():
    private, trust = key_material()
    valid = envelope_for(private)
    tampered = bytearray(__import__("base64").urlsafe_b64decode(valid.signature_b64url + "=="))
    tampered[0] ^= 1
    envelope = SignedOfferSignatureEnvelope(
        signer_key_id=KEY_ID, signed_at=valid.signed_at,
        signature_b64url=encode_signature(bytes(tampered)),
    )
    with pytest.raises(SignedOfferVerificationError, match="SIGNED_OFFER_SIGNATURE_INVALID"):
        verify(envelope, trust)
