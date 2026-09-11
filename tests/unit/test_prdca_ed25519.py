"""Direct certificate for the production PRDCA Ed25519 adapter.

TITLE: PRDCA Ed25519 Adapter Direct Certificate
VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3KR5
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves native Ed25519 signing, exact-key resolution, tamper rejection,
         and fail-closed adapter behavior without network or persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_prdca_ed25519.py
COLLABORATION / OWNERSHIP: Direct certificate for prdca_ed25519.py.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3KR5 certifies native Ed25519
           protocol compatibility and the RFC 8032 test vector.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import pytest

from tools.eos.governance.prdca import PRDCAAuthority
from tools.eos.governance.prdca_ed25519 import (
    CryptographyEd25519KeyResolver,
    CryptographyEd25519Signer,
    PRDCAEd25519AdapterError,
)


KEY_ID = "prdca-key:test"
SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")
RFC_PUBLIC_KEY = bytes.fromhex("d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a")
RFC_EMPTY_SIGNATURE = bytes.fromhex("e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b")


def _pair() -> tuple[CryptographyEd25519Signer, CryptographyEd25519KeyResolver]:
    private_key = Ed25519PrivateKey.from_private_bytes(SEED)
    public_key = private_key.public_key()
    return CryptographyEd25519Signer(private_key), CryptographyEd25519KeyResolver({KEY_ID: public_key})


def test_native_ed25519_rfc8032_vector() -> None:
    signer, resolver = _pair()
    signature = signer.sign(b"")
    assert signer._private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw) == RFC_PUBLIC_KEY
    assert signature == RFC_EMPTY_SIGNATURE
    assert resolver.resolve(KEY_ID)(b"", signature) is True


def test_native_ed25519_round_trip_and_tamper_rejection() -> None:
    signer, resolver = _pair()
    message = b"canonical PRDCA envelope"
    signature = signer.sign(message)
    verify = resolver.resolve(KEY_ID)
    assert len(signature) == 64
    assert verify(message, signature) is True
    assert verify(message + b"!", signature) is False
    assert verify(message, signature[:-1] + bytes([signature[-1] ^ 1])) is False


def test_unknown_key_id_fails_closed() -> None:
    _, resolver = _pair()
    with pytest.raises(KeyError):
        resolver.resolve("prdca-key:unknown")


def test_invalid_key_inputs_fail_closed() -> None:
    with pytest.raises(PRDCAEd25519AdapterError):
        CryptographyEd25519Signer(object())  # type: ignore[arg-type]
    with pytest.raises(PRDCAEd25519AdapterError):
        CryptographyEd25519KeyResolver({"not-a-key": Ed25519PrivateKey.from_private_bytes(SEED).public_key()})
    with pytest.raises(PRDCAEd25519AdapterError):
        CryptographyEd25519KeyResolver({KEY_ID: object()})  # type: ignore[arg-type]


def test_malformed_messages_and_signatures_fail_closed() -> None:
    signer, resolver = _pair()
    with pytest.raises(PRDCAEd25519AdapterError):
        signer.sign("not-bytes")  # type: ignore[arg-type]
    verify = resolver.resolve(KEY_ID)
    assert verify("not-bytes", b"x" * 64) is False  # type: ignore[arg-type]
    assert verify(b"message", b"x" * 63) is False


def test_resolver_snapshots_key_mapping() -> None:
    private_key = Ed25519PrivateKey.from_private_bytes(SEED)
    keys = {KEY_ID: private_key.public_key()}
    resolver = CryptographyEd25519KeyResolver(keys)
    keys.clear()
    signature = CryptographyEd25519Signer(private_key).sign(b"stable")
    assert resolver.resolve(KEY_ID)(b"stable", signature) is True


def test_native_adapter_drives_prdca_core() -> None:
    signer, resolver = _pair()
    authority = PRDCAAuthority(
        signer=signer,
        key_resolver=resolver,
        deployment_evidence_key_resolver=resolver,
    )
    certificate = authority.issue_platform_registration_certificate(
        source_identity="source-a",
        source_contract_version="v1",
        implementation_identity="impl:adapter-a",
        capability_class="CREDENTIAL_METADATA",
        campaign_identity="M11-R8-R3B-P8-P3D-P5-R8-P3",
        authority_key_id=KEY_ID,
    )
    authority.verify_platform_registration_certificate(certificate)


# ARTIFACT: test_prdca_ed25519.py
# VERSION: v1.0.0-M11-R8-R3B-P8-P3D-P5-R8-P3KR5
# END OF WILSY OS SOVEREIGN ARTIFACT
