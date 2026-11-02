"""Adversarial certificate for Deputy browser-device proof-of-possession.

TITLE: Deputy Device Provenance Authority Unit Certificate
VERSION: v1.0.0-L8-6G-DEPUTY-DEVICE-PROVENANCE-UNIT-CERT
AUTHORITY: Test-only verification of the L8-6G cryptographic domain contract.
TENANT BOUNDARY: Synthetic canonical Deputy binding only.
AUTHORITY BOUNDARY: Browser key possession; no hardware or OS permission claim.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

from tools.eos.legal_operations.domain.deputy_device_provenance_authority import (
    DeputyDeviceProvenance,
    DeputyDeviceProvenanceAuthorityError,
    DeputyDeviceProvenanceChallenge,
)
from tools.eos.legal_operations.domain.deputy_principal_binding import (
    DeputyPrincipalBinding,
)
from tools.eos.legal_operations.domain.legal_operations_lifecycle import Deputy


NOW = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)


def _binding() -> DeputyPrincipalBinding:
    deputy = Deputy(
        tenant_id="tenant-device-test",
        deputy_id="deputy-device-test",
        sheriff_office_id="office-device-test",
        display_name="Synthetic Deputy",
        badge_reference="badge-device-test",
        evidence_reference="deputy-evidence-device-test",
    )
    return DeputyPrincipalBinding.from_deputy(
        principal_id="principal-device-test",
        deputy=deputy,
        bound_at=NOW - timedelta(days=1),
        evidence_reference="binding-evidence-device-test",
    )


def _key_pair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    public_key_der = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return private_key, public_key_der


def _challenge(private_key=None, public_key_der=None, **overrides):
    if private_key is None or public_key_der is None:
        private_key, public_key_der = _key_pair()
    values = {
        "binding": _binding(),
        "session_reference": "session-device-test",
        "challenge_id": "challenge-device-test",
        "public_key_spki_der": public_key_der,
        "nonce": b"n" * 32,
        "issued_at": NOW,
        "expires_at": NOW + timedelta(minutes=2),
    }
    values.update(overrides)
    return private_key, DeputyDeviceProvenanceChallenge.issue(**values)


def _signature(private_key, challenge):
    der = private_key.sign(challenge.signed_payload(), ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der)
    return r.to_bytes(32, "big") + s.to_bytes(32, "big")


def test_valid_webcrypto_p256_proof_binds_exact_deputy_and_session() -> None:
    private_key, challenge = _challenge()
    proof = DeputyDeviceProvenance.verify(
        challenge=challenge,
        signature_p1363=_signature(private_key, challenge),
        verified_at=NOW + timedelta(seconds=1),
    )

    assert proof.tenant_id == "tenant-device-test"
    assert proof.principal_id == "principal-device-test"
    assert proof.deputy_id == "deputy-device-test"
    assert proof.sheriff_office_id == "office-device-test"
    assert proof.session_reference == "session-device-test"
    assert proof.device_id == f"deputy-device:{proof.public_key_fingerprint}"
    assert proof.challenge_id == "challenge-device-test"
    assert proof.signature_fingerprint
    assert proof.fingerprint
    persisted = proof.to_dict()
    assert "private_key" not in persisted
    assert "signature" not in persisted
    assert "latitude" not in persisted
    assert "permission_granted" not in persisted


def test_signature_from_another_private_key_is_rejected() -> None:
    private_key, challenge = _challenge()
    other_private_key, _ = _key_pair()
    with pytest.raises(DeputyDeviceProvenanceAuthorityError) as caught:
        DeputyDeviceProvenance.verify(
            challenge=challenge,
            signature_p1363=_signature(other_private_key, challenge),
            verified_at=NOW + timedelta(seconds=1),
        )
    assert caught.value.code == "L8_6G_SIGNATURE_VERIFICATION_FAILED"


@pytest.mark.parametrize("signature", [b"", b"x" * 63, b"x" * 65, "not-bytes"])
def test_malformed_signature_is_rejected(signature) -> None:
    _private_key, challenge = _challenge()
    with pytest.raises(DeputyDeviceProvenanceAuthorityError) as caught:
        DeputyDeviceProvenance.verify(
            challenge=challenge,
            signature_p1363=signature,
            verified_at=NOW + timedelta(seconds=1),
        )
    assert caught.value.code == "L8_6G_SIGNATURE_INVALID"


def test_expired_or_preissued_proof_is_rejected() -> None:
    private_key, challenge = _challenge()
    signature = _signature(private_key, challenge)
    with pytest.raises(DeputyDeviceProvenanceAuthorityError) as expired:
        DeputyDeviceProvenance.verify(
            challenge=challenge,
            signature_p1363=signature,
            verified_at=challenge.expires_at + timedelta(microseconds=1),
        )
    assert expired.value.code == "L8_6G_CHALLENGE_EXPIRED"

    with pytest.raises(DeputyDeviceProvenanceAuthorityError) as early:
        DeputyDeviceProvenance.verify(
            challenge=challenge,
            signature_p1363=signature,
            verified_at=challenge.issued_at - timedelta(microseconds=1),
        )
    assert early.value.code == "L8_6G_CHALLENGE_EXPIRED"


def test_challenge_window_is_bounded_to_five_minutes() -> None:
    private_key, public_key_der = _key_pair()
    del private_key
    with pytest.raises(DeputyDeviceProvenanceAuthorityError) as caught:
        DeputyDeviceProvenanceChallenge.issue(
            binding=_binding(),
            session_reference="session-device-test",
            challenge_id="challenge-too-long",
            public_key_spki_der=public_key_der,
            nonce=b"n" * 32,
            issued_at=NOW,
            expires_at=NOW + timedelta(minutes=5, microseconds=1),
        )
    assert caught.value.code == "L8_6G_CHALLENGE_WINDOW_INVALID"


def test_non_p256_public_key_is_rejected() -> None:
    private_key = ec.generate_private_key(ec.SECP384R1())
    public_key_der = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    with pytest.raises(DeputyDeviceProvenanceAuthorityError) as caught:
        _challenge(private_key=private_key, public_key_der=public_key_der)
    assert caught.value.code == "L8_6G_P256_PUBLIC_KEY_REQUIRED"


@pytest.mark.parametrize("nonce", [b"", b"short", b"n" * 31, b"n" * 33, "n" * 32])
def test_nonce_must_be_exactly_32_bytes(nonce) -> None:
    _private_key, public_key_der = _key_pair()
    with pytest.raises(DeputyDeviceProvenanceAuthorityError) as caught:
        DeputyDeviceProvenanceChallenge.issue(
            binding=_binding(),
            session_reference="session-device-test",
            challenge_id="challenge-bad-nonce",
            public_key_spki_der=public_key_der,
            nonce=nonce,
            issued_at=NOW,
            expires_at=NOW + timedelta(minutes=1),
        )
    assert caught.value.code == "L8_6G_NONCE_INVALID"


def test_challenge_and_provenance_direct_construction_are_rejected() -> None:
    with pytest.raises(DeputyDeviceProvenanceAuthorityError) as challenge_error:
        DeputyDeviceProvenanceChallenge()
    assert challenge_error.value.code == "L8_6G_CHALLENGE_FACTORY_REQUIRED"

    with pytest.raises(DeputyDeviceProvenanceAuthorityError) as provenance_error:
        DeputyDeviceProvenance()
    assert provenance_error.value.code == "L8_6G_PROVENANCE_FACTORY_REQUIRED"


def test_mutating_signed_session_binding_invalidates_signature() -> None:
    private_key, challenge = _challenge()
    signature = _signature(private_key, challenge)
    object.__setattr__(challenge, "session_reference", "other-session")
    with pytest.raises(DeputyDeviceProvenanceAuthorityError) as caught:
        DeputyDeviceProvenance.verify(
            challenge=challenge,
            signature_p1363=signature,
            verified_at=NOW + timedelta(seconds=1),
        )
    assert caught.value.code == "L8_6G_SIGNATURE_VERIFICATION_FAILED"


# ARTIFACT: tests/unit/test_deputy_device_provenance_authority.py
# VERSION: v1.0.0-L8-6G-DEPUTY-DEVICE-PROVENANCE-UNIT-CERT
# AUTHORITY BOUNDARY: Synthetic P-256 browser-key possession tests only.
# TENANT POSTURE: Exact synthetic tenant and canonical Deputy binding.
# FAIL-CLOSED POSTURE: Invalid key, signature, challenge, window and nonce reject.
# END OF WILSY OS SOVEREIGN ARTIFACT
