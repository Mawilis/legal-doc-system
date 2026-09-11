"""Direct certificate for the stateless PRDCA core.

TITLE: PRDCA Core Direct Certificate
VERSION: v1.0.4-M11-R8-R3B-P8-P3D-P5-R8-P3KR9
AUTHORITY: Wilsy OS Core Governance
EPITOME: Exercises the frozen signed-envelope and deployment-evidence boundary.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_prdca.py
COLLABORATION / OWNERSHIP: Direct certificate for tools/eos/governance/prdca.py.
CERTIFICATION / UPDATE DATE: 2026-09-10
CHANGELOG: v1.0.4-M11-R8-R3B-P8-P3D-P5-R8-P3KR9 adds literal authority and
           cryptographic-contract assertions across every certificate surface.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Callable, TypedDict, cast

import pytest

import tools.eos.governance.prdca as module
from tools.eos.saas.billing.tenant_inbound_provider_credential_metadata_source_registry import (
    CAPABILITY_CLASS_CREDENTIAL_METADATA,
    TenantInboundCredentialMetadataSourceDescriptor,
    TenantInboundCredentialMetadataSourceRegistrationProvenance,
)

KEY_ID = "prdca-key:test"
EVIDENCE_KEY_ID = "prdca-key:evidence"
CAMPAIGN = "M11-R8-R3B-P8-P3D-P5-R8-P3"
NOW = datetime(2026, 9, 10, 10, 0, 0, tzinfo=timezone.utc)


_ED25519_Q = 2**255 - 19
_ED25519_L = 2**252 + 27742317777372353535851937790883648493
_ED25519_D = (-121665 * pow(121666, _ED25519_Q - 2, _ED25519_Q)) % _ED25519_Q
_ED25519_I = pow(2, (_ED25519_Q - 1) // 4, _ED25519_Q)
_ED25519_BY = (4 * pow(5, _ED25519_Q - 2, _ED25519_Q)) % _ED25519_Q


def _ed25519_xrecover(y: int) -> int:
    xx = (y * y - 1) * pow(_ED25519_D * y * y + 1, _ED25519_Q - 2, _ED25519_Q)
    x = pow(xx, (_ED25519_Q + 3) // 8, _ED25519_Q)
    if (x * x - xx) % _ED25519_Q != 0:
        x = (x * _ED25519_I) % _ED25519_Q
    if x & 1:
        x = _ED25519_Q - x
    return x


def _ed25519_add(left: tuple[int, int], right: tuple[int, int]) -> tuple[int, int]:
    x1, y1 = left
    x2, y2 = right
    product = (_ED25519_D * x1 * x2 * y1 * y2) % _ED25519_Q
    x = ((x1 * y2 + x2 * y1) * pow(1 + product, _ED25519_Q - 2, _ED25519_Q)) % _ED25519_Q
    y = ((y1 * y2 + x1 * x2) * pow(1 - product, _ED25519_Q - 2, _ED25519_Q)) % _ED25519_Q
    return x, y


def _ed25519_scalar_mult(point: tuple[int, int], scalar: int) -> tuple[int, int]:
    result = (0, 1)
    addend = point
    while scalar:
        if scalar & 1:
            result = _ed25519_add(result, addend)
        addend = _ed25519_add(addend, addend)
        scalar >>= 1
    return result


def _ed25519_encode(point: tuple[int, int]) -> bytes:
    x, y = point
    return (y | ((x & 1) << 255)).to_bytes(32, "little")


def _ed25519_decode(encoded: bytes) -> tuple[int, int]:
    if len(encoded) != 32:
        raise ValueError("invalid Ed25519 point length")
    value = int.from_bytes(encoded, "little")
    x_sign = value >> 255
    y = value & ((1 << 255) - 1)
    if y >= _ED25519_Q:
        raise ValueError("non-canonical Ed25519 point")
    x = _ed25519_xrecover(y)
    if (x & 1) != x_sign:
        x = _ED25519_Q - x
    return x, y


_ED25519_BASE = (_ed25519_xrecover(_ED25519_BY), _ED25519_BY)
_ED25519_SEED = bytes.fromhex("9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60")


class Ed25519Signer:
    """Deterministic RFC 8032 Ed25519 signer used only as an injected test backend."""

    def __init__(self, seed: bytes = _ED25519_SEED) -> None:
        if len(seed) != 32:
            raise ValueError("Ed25519 seed must be 32 bytes")
        self._seed = seed
        expanded = hashlib.sha512(seed).digest()
        scalar = int.from_bytes(expanded[:32], "little")
        scalar &= (1 << 254) - 8
        scalar |= 1 << 254
        self.public_key = _ed25519_encode(_ed25519_scalar_mult(_ED25519_BASE, scalar))
        self._prefix = expanded[32:]

    def sign(self, message: bytes) -> bytes:
        scalar = int.from_bytes(hashlib.sha512(self._seed).digest()[:32], "little")
        scalar &= (1 << 254) - 8
        scalar |= 1 << 254
        r = int.from_bytes(hashlib.sha512(self._prefix + message).digest(), "little") % _ED25519_L
        encoded_r = _ed25519_encode(_ed25519_scalar_mult(_ED25519_BASE, r))
        public_key = self.public_key
        challenge = int.from_bytes(hashlib.sha512(encoded_r + public_key + message).digest(), "little") % _ED25519_L
        return encoded_r + ((r + challenge * scalar) % _ED25519_L).to_bytes(32, "little")


class Ed25519Resolver:
    def __init__(self, signer: Ed25519Signer, *key_ids: str) -> None:
        self._public_key = signer.public_key
        self.key_ids = set(key_ids)

    def resolve(self, authority_key_id: str) -> Callable[[bytes, bytes], bool]:
        if authority_key_id not in self.key_ids:
            raise KeyError(authority_key_id)

        def verify(message: bytes, signature: bytes) -> bool:
            if len(signature) != 64:
                return False
            try:
                encoded_r = signature[:32]
                r_point = _ed25519_decode(encoded_r)
                public_point = _ed25519_decode(self._public_key)
                scalar_s = int.from_bytes(signature[32:], "little")
                if scalar_s >= _ED25519_L:
                    return False
                challenge = int.from_bytes(hashlib.sha512(encoded_r + self._public_key + message).digest(), "little") % _ED25519_L
                return _ed25519_encode(_ed25519_scalar_mult(_ED25519_BASE, scalar_s)) == _ed25519_encode(_ed25519_add(r_point, _ed25519_scalar_mult(public_point, challenge)))
            except ValueError:
                return False

        return verify


class FakeResolver:
    def __init__(self, *key_ids: str) -> None:
        self.key_ids = set(key_ids)

    def resolve(self, authority_key_id: str) -> Callable[[bytes, bytes], bool]:
        if authority_key_id not in self.key_ids:
            raise KeyError(authority_key_id)

        def verify(message: bytes, signature: bytes) -> bool:
            return signature == hashlib.sha3_512(message).digest()

        return verify


class FakeClock:
    def now(self) -> datetime:
        return NOW


class ActiveTransaction:
    active = True


class RecordingLedger:
    def __init__(self) -> None:
        self.calls: list[tuple[object, object]] = []

    def append_batch(self, batch: module.PRDCACertificateBatch, session: module.CallerOwnedTransaction) -> None:
        self.calls.append((batch, session))


def _authority(tmp_path: Path, ledger: module.PRDCACertificateLedger | None = None) -> module.PRDCAAuthority:
    signer = Ed25519Signer()
    return module.PRDCAAuthority(
        signer=signer,
        key_resolver=Ed25519Resolver(signer, KEY_ID, EVIDENCE_KEY_ID),
        deployment_evidence_key_resolver=Ed25519Resolver(signer, EVIDENCE_KEY_ID),
        clock=FakeClock(),
        ledger=ledger,
        artifact_root=tmp_path,
    )


def _evidence(tmp_path: Path, **changes: object) -> module.AuthenticatedRuntimeDeploymentEvidence:
    artifact = tmp_path / "artifact.py"
    artifact.write_bytes(b"certified artifact")
    payload: dict[str, object] = {
        "artifact_path": "artifact.py",
        "artifact_version": "v1.0.0",
        "artifact_sha3_512": hashlib.sha3_512(artifact.read_bytes()).hexdigest(),
        "environment": "test",
        "deployment_identity": "deployment-1",
        "deployment_event_identity": "deployment-event-1",
        "deployment_observed_at": "2026-09-10T10:00:00.000000Z",
        "campaign_identity": CAMPAIGN,
        "producer_authority": module.DEPLOYMENT_EVIDENCE_PRODUCER,
        "deployment_status": "SUCCEEDED",
    }
    payload.update(changes)
    raw_payload = json.dumps(payload, ensure_ascii=False, sort_keys=False, separators=(",", ":"), allow_nan=False).encode()
    evidence_id = hashlib.sha3_512(raw_payload).hexdigest()
    envelope: dict[str, object] = {
        "envelope_schema": module.DEPLOYMENT_EVIDENCE_ENVELOPE_SCHEMA,
        "evidence_type": "AuthenticatedRuntimeDeploymentEvidence",
        "evidence_id": evidence_id,
        "payload_schema": module.DEPLOYMENT_EVIDENCE_SCHEMA,
        "payload": payload,
        "producer_authority": module.DEPLOYMENT_EVIDENCE_PRODUCER,
        "attestation_key_id": EVIDENCE_KEY_ID,
        "signature_algorithm": module.SIGNATURE_ALGORITHM,
        "signature": "pending",
        "status": "ACTIVE",
    }
    signing = {key: envelope[key] for key in module._EVIDENCE_ENVELOPE_FIELDS if key != "signature"}
    envelope["signature"] = module._b64(
        Ed25519Signer().sign(json.dumps(signing, ensure_ascii=False, sort_keys=False, separators=(",", ":"), allow_nan=False).encode())
    )
    return module.AuthenticatedRuntimeDeploymentEvidence(
        envelope_schema=str(envelope["envelope_schema"]),
        evidence_type=str(envelope["evidence_type"]),
        evidence_id=evidence_id,
        payload_schema=str(envelope["payload_schema"]),
        payload=module._mapping_proxy(payload),
        producer_authority=module.DEPLOYMENT_EVIDENCE_PRODUCER,
        attestation_key_id=EVIDENCE_KEY_ID,
        signature_algorithm=module.SIGNATURE_ALGORITHM,
        signature=str(envelope["signature"]),
        status="ACTIVE",
    )


class _Context(TypedDict):
    authority: module.PRDCAAuthority
    prc: module.PlatformRegistrationCertificateEnvelope
    evidence: module.AuthenticatedRuntimeDeploymentEvidence
    dcc: module.DeploymentCertificationCertificateEnvelope
    descriptor: TenantInboundCredentialMetadataSourceDescriptor
    receipt: module.DescriptorVerificationReceiptEnvelope


def _context(tmp_path: Path) -> _Context:
    authority = _authority(tmp_path)
    prc = authority.issue_platform_registration_certificate(
        source_identity="source-a",
        source_contract_version="v1",
        implementation_identity="impl:adapter-a",
        capability_class=CAPABILITY_CLASS_CREDENTIAL_METADATA,
        campaign_identity=CAMPAIGN,
        authority_key_id=KEY_ID,
    )
    evidence = _evidence(tmp_path)
    dcc = authority.issue_deployment_certification_certificate(
        platform_registration=prc,
        deployment_evidence=evidence,
        campaign_identity=CAMPAIGN,
        authority_key_id=KEY_ID,
    )
    descriptor = TenantInboundCredentialMetadataSourceDescriptor.create(
        source_identity="source-a",
        source_contract_version="v1",
        implementation_identity="impl:adapter-a",
        capability_class=CAPABILITY_CLASS_CREDENTIAL_METADATA,
        registration_provenance=TenantInboundCredentialMetadataSourceRegistrationProvenance(
            platform_registration_id=prc.artifact_id,
            deployment_certification_id=dcc.artifact_id,
        ),
    )
    receipt = authority.verify_descriptor_binding(
        platform_registration=prc,
        deployment_certification=dcc,
        descriptor=descriptor,
    )
    return {"authority": authority, "prc": prc, "evidence": evidence, "dcc": dcc, "descriptor": descriptor, "receipt": receipt}


def _expect(exc: type[BaseException], fn: Callable[[], object]) -> None:
    with pytest.raises(exc):
        fn()


def _run_case(case_id: int, tmp_path: Path) -> None:
    context = _context(tmp_path)
    authority = context["authority"]
    prc = context["prc"]
    evidence = context["evidence"]
    dcc = context["dcc"]
    descriptor = context["descriptor"]
    receipt = context["receipt"]

    if case_id == 1:
        assert tuple(prc.payload) == module._PRC_FIELDS
    elif case_id == 2:
        assert module._canonical_bytes({"value": "e\u0301"}, ("value",)) == b'{"value":"\xc3\xa9"}'
    elif case_id == 3:
        left = authority.issue_platform_registration_certificate(source_identity="caf\u00e9", source_contract_version="v1", implementation_identity="impl:a", capability_class=CAPABILITY_CLASS_CREDENTIAL_METADATA, campaign_identity=CAMPAIGN, authority_key_id=KEY_ID)
        right = authority.issue_platform_registration_certificate(source_identity="cafe\u0301", source_contract_version="v1", implementation_identity="impl:a", capability_class=CAPABILITY_CLASS_CREDENTIAL_METADATA, campaign_identity=CAMPAIGN, authority_key_id=KEY_ID)
        assert left.artifact_id == right.artifact_id
    elif case_id == 4:
        assert len(prc.artifact_id) == 128 and prc.artifact_id == prc.artifact_id.lower()
    elif case_id == 5:
        _expect(TypeError, lambda: cast(Any, authority).issue_platform_registration_certificate(source_identity="a", source_contract_version="v1", implementation_identity="impl:a", capability_class=CAPABILITY_CLASS_CREDENTIAL_METADATA, campaign_identity=CAMPAIGN, authority_key_id=KEY_ID, platform_registration_id="x"))
    elif case_id == 6:
        authority.verify_platform_registration_certificate(prc)
    elif case_id == 7:
        assert evidence.payload["deployment_status"] == "SUCCEEDED"
    elif case_id == 8:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.issue_deployment_certification_certificate(platform_registration=prc, deployment_evidence=cast(Any, None), campaign_identity=CAMPAIGN, authority_key_id=KEY_ID))
    elif case_id == 9:
        _expect(module.PRDCACanonicalizationError, lambda: module._validate_relative_path("/absolute"))
    elif case_id == 10:
        _expect(module.PRDCACanonicalizationError, lambda: module._text("artifact_version", ""))
    elif case_id == 11:
        assert dcc.payload["artifact_sha3_512"] == evidence.payload["artifact_sha3_512"]
    elif case_id == 12:
        _expect(module.PRDCAIdentifierMismatchError, lambda: authority.issue_deployment_certification_certificate(platform_registration=prc, deployment_evidence=_evidence(tmp_path, artifact_sha3_512="0" * 128), campaign_identity=CAMPAIGN, authority_key_id=KEY_ID))
    elif case_id == 13:
        assert evidence.payload["environment"] == dcc.payload["environment"]
    elif case_id == 14:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.verify_deployment_evidence(cast(Any, None)))
    elif case_id == 15:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.verify_deployment_evidence(replace(evidence, signature=module._b64(b"x" * 64))))
    elif case_id == 16:
        _expect(module.PRDCAIdentifierMismatchError, lambda: authority.verify_deployment_evidence(replace(evidence, evidence_id="0" * 128)))
    elif case_id == 17:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.verify_deployment_evidence(replace(evidence, producer_authority="other")))
    elif case_id == 18:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.verify_deployment_evidence(replace(evidence, attestation_key_id="prdca-key:unknown")))
    elif case_id == 19:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.verify_deployment_evidence(replace(evidence, signature="not-base64")))
    elif case_id == 20:
        _expect(module.PRDCAIdentifierMismatchError, lambda: authority.verify_deployment_evidence(replace(evidence, payload=module._mapping_proxy({**dict(evidence.payload), "environment": "tampered"}))))
    elif case_id == 21:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.verify_platform_registration_certificate(replace(prc, status="REVOKED")))
    elif case_id == 22:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.verify_deployment_evidence(replace(evidence, payload=module._mapping_proxy({**dict(evidence.payload), "deployment_status": "STARTED"}))))
    elif case_id == 23:
        _expect(module.PRDCAIdentifierMismatchError, lambda: authority.issue_deployment_certification_certificate(platform_registration=prc, deployment_evidence=evidence, campaign_identity="other", authority_key_id=KEY_ID))
    elif case_id == 24:
        _expect(module.PRDCAIdentifierMismatchError, lambda: authority.issue_deployment_certification_certificate(platform_registration=prc, deployment_evidence=_evidence(tmp_path, artifact_path="wrong.py"), campaign_identity=CAMPAIGN, authority_key_id=KEY_ID))
    elif case_id == 25:
        _expect(module.PRDCACanonicalizationError, lambda: authority.issue_deployment_certification_certificate(platform_registration=prc, deployment_evidence=_evidence(tmp_path, environment=""), campaign_identity=CAMPAIGN, authority_key_id=KEY_ID))
    elif case_id == 26:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.verify_deployment_evidence(replace(evidence, payload=module._mapping_proxy({**dict(evidence.payload), "producer_authority": "other"}))))
    elif case_id == 27:
        assert "signature" not in evidence.payload and "attestation_key_id" not in evidence.payload
    elif case_id == 28:
        assert "signature" not in module._evidence_signing_view(evidence.to_dict())
    elif case_id == 29:
        assert "signature" not in module._id(dict(evidence.payload), module._EVIDENCE_FIELDS)
    elif case_id == 30:
        assert tuple(receipt.payload) == module._RECEIPT_FIELDS
    elif case_id == 31:
        assert receipt.payload["platform_registration_id"] == prc.artifact_id
    elif case_id == 32:
        assert receipt.payload["deployment_certification_id"] == dcc.artifact_id
    elif case_id == 33:
        assert receipt.payload["entry_fingerprint"] == descriptor.entry_fingerprint
    elif case_id == 34:
        assert tuple(prc.to_dict()) == module._ENVELOPE_FIELDS
    elif case_id == 35:
        forged = dict(prc.to_dict())
        forged["unknown"] = True
        _expect(module.PRDCAUnknownFieldError, lambda: module._verify_prdca_envelope(forged, module.PRC_SCHEMA, "PLATFORM_REGISTRATION_CERTIFICATE", module._PRC_FIELDS, Ed25519Resolver(Ed25519Signer(), KEY_ID)))
    elif case_id == 36:
        _expect(module.PRDCACanonicalizationError, lambda: module._text("x", "bad\x00value"))
    elif case_id == 37:
        _expect(module.PRDCACanonicalizationError, lambda: module._canonical_bytes({"x": float("nan")}, ("x",)))
    elif case_id == 38:
        assert "signature" not in module._envelope_signing_view(prc.to_dict())
    elif case_id == 39:
        authority.verify_platform_registration_certificate(prc)
        vector_signer = Ed25519Signer()
        assert vector_signer.public_key.hex() == "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
        assert vector_signer.sign(b"").hex() == "e5564300c360ac729086e2cc806e828a84877f1eb8e5d974d873e065224901555fb8821590a33bacc61e39701cf9b46bd25bf5f0595bbe24655141438e7a100b"
    elif case_id == 40:
        forged = replace(prc, payload=module._mapping_proxy({**dict(prc.payload), "source_identity": "tampered"}))
        _expect(module.PRDCAIdentifierMismatchError, lambda: authority.verify_platform_registration_certificate(forged))
    elif case_id == 41:
        _expect(module.PRDCAIdentifierMismatchError, lambda: authority.verify_platform_registration_certificate(replace(prc, authority_key_id="prdca-key:unknown")))
    elif case_id == 42:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.verify_platform_registration_certificate(replace(prc, signature="bad")))
    elif case_id == 43:
        _expect(TypeError, lambda: cast(Any, authority).issue_platform_registration_certificate(source_identity="a", source_contract_version="v1", implementation_identity="impl:a", capability_class=CAPABILITY_CLASS_CREDENTIAL_METADATA, campaign_identity=CAMPAIGN, authority_key_id=KEY_ID, signature="x"))
    elif case_id == 44:
        _expect(TypeError, lambda: cast(Any, authority).issue_platform_registration_certificate(source_identity="a", source_contract_version="v1", implementation_identity="impl:a", capability_class=CAPABILITY_CLASS_CREDENTIAL_METADATA, campaign_identity=CAMPAIGN, authority_key_id=KEY_ID, issued_at=NOW))
    elif case_id == 45:
        assert prc.issued_at == "2026-09-10T10:00:00.000000Z"
    elif case_id == 46:
        assert "issued_at" not in module._PRC_FIELDS and "status" not in module._PRC_FIELDS
    elif case_id == 47:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.verify_platform_registration_certificate(replace(prc, issuer_authority="other")))
    elif case_id == 48:
        _expect(module.PRDCAIdentifierMismatchError, lambda: authority.issue_deployment_certification_certificate(platform_registration=prc, deployment_evidence=evidence, campaign_identity="other", authority_key_id=KEY_ID))
    elif case_id == 49:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.verify_platform_registration_certificate(replace(prc, status="PENDING")))
    elif case_id == 50:
        forged = replace(dcc, payload=module._mapping_proxy({**dict(dcc.payload), "platform_registration_id": "0" * 128}))
        _expect(module.PRDCAIdentifierMismatchError, lambda: authority.verify_descriptor_binding(platform_registration=prc, deployment_certification=forged, descriptor=descriptor))
    elif case_id == 51:
        bad = TenantInboundCredentialMetadataSourceDescriptor.create(source_identity="other", source_contract_version="v1", implementation_identity="impl:adapter-a", capability_class=CAPABILITY_CLASS_CREDENTIAL_METADATA, registration_provenance=descriptor.registration_provenance)
        _expect(module.PRDCAIdentifierMismatchError, lambda: authority.verify_descriptor_binding(platform_registration=prc, deployment_certification=dcc, descriptor=bad))
    elif case_id == 52:
        object.__setattr__(descriptor, "entry_fingerprint", "0" * 128)
        _expect(module.PRDCAIdentifierMismatchError, lambda: authority.verify_descriptor_binding(platform_registration=prc, deployment_certification=dcc, descriptor=descriptor))
    elif case_id == 53:
        assert not hasattr(authority, "latest")
    elif case_id == 54:
        _expect(module.PRDCAIdentifierMismatchError, lambda: authority.verify_platform_registration_certificate(replace(prc, authority_key_id="prdca-key:latest")))
    elif case_id == 55:
        ledger = RecordingLedger()
        local = _authority(tmp_path, ledger)
        local.persist_certificate_batch(batch=module.PRDCACertificateBatch(prc, dcc, receipt), session=ActiveTransaction())
        assert len(ledger.calls) == 1
    elif case_id == 56:
        _expect(module.PRDCATransactionOwnershipError, lambda: authority.persist_certificate_batch(batch=module.PRDCACertificateBatch(prc, dcc, receipt), session=ActiveTransaction()))
    elif case_id == 57:
        result = subprocess.run([sys.executable, "-c", "import tools.eos.governance.prdca"], capture_output=True, text=True, check=True)
        assert result.stdout == "" and result.stderr == ""
    elif case_id == 58:
        assert "pymongo" not in sys.modules and "motor" not in sys.modules
    elif case_id == 59:
        assert not hasattr(authority, "produce_deployment_evidence")
    elif case_id == 60:
        assert "client_invoice" not in sys.modules
    elif case_id == 61:
        assert "commercial_receivable" not in sys.modules
    elif case_id == 62:
        assert not any(name.startswith("tools.eos.kennel") for name in sys.modules)
    elif case_id == 63:
        _expect(module.PRDCACanonicalizationError, lambda: module._timestamp(datetime(2026, 9, 10, 10, 0, 0)))
    elif case_id == 64:
        _expect(module.PRDCACanonicalizationError, lambda: module._timestamp("2026-09-10T10:00:00Z"))
    elif case_id == 65:
        _expect(module.PRDCACanonicalizationError, lambda: module._canonicalize({"unsupported"}))
    elif case_id == 66:
        _expect(module.PRDCACanonicalizationError, lambda: module._canonicalize({"nested": {"value": "bad\x00value"}}))
    elif case_id == 67:
        _expect(module.PRDCASignatureVerificationError, lambda: module._unb64("AAAA="))
    elif case_id == 68:
        class BrokenSigner:
            def sign(self, message: bytes) -> bytes:
                raise RuntimeError("signer unavailable")

        _expect(module.PRDCASignatureVerificationError, lambda: module._sign(cast(module.PRDCASigner, BrokenSigner()), b"message"))
    elif case_id == 69:
        class ShortSigner:
            def sign(self, message: bytes) -> bytes:
                return b"short"

        _expect(module.PRDCASignatureVerificationError, lambda: module._sign(cast(module.PRDCASigner, ShortSigner()), b"message"))
    elif case_id == 70:
        _expect(module.PRDCACanonicalizationError, lambda: module._validate_relative_path("../escape"))
    elif case_id == 71:
        _expect(module.PRDCACanonicalizationError, lambda: module._validate_relative_path("nested\\artifact.py"))
    elif case_id == 72:
        _expect(module.PRDCASchemaError, lambda: authority.verify_deployment_evidence(replace(evidence, envelope_schema="wrong")))
    elif case_id == 73:
        corrupted_payload = {**dict(evidence.payload), "unexpected": True}
        _expect(module.PRDCAUnknownFieldError, lambda: authority.verify_deployment_evidence(replace(evidence, payload=module._mapping_proxy(corrupted_payload))))
    elif case_id == 74:
        corrupted_payload = {**dict(prc.payload), "unexpected": True}
        forged = replace(prc, payload=module._mapping_proxy(corrupted_payload))
        _expect(module.PRDCAUnknownFieldError, lambda: authority.verify_platform_registration_certificate(forged))
    elif case_id == 75:
        _expect(module.PRDCAUnknownFieldError, lambda: module._canonical_bytes({"second": "b", "first": "a"}, ("first", "second")))
    elif case_id == 76:
        _expect(module.PRDCACanonicalizationError, lambda: module._canonicalize(float("inf")))
    elif case_id == 77:
        _expect(module.PRDCASignatureVerificationError, lambda: module._unb64("AA"))
    elif case_id == 78:
        _expect(module.PRDCACanonicalizationError, lambda: module._validate_relative_path(""))
    elif case_id == 79:
        _expect(module.PRDCACanonicalizationError, lambda: module._validate_relative_path("."))
    elif case_id == 80:
        _expect(module.PRDCASchemaError, lambda: authority.verify_platform_registration_certificate(replace(prc, envelope_schema="wrong")))
    elif case_id == 81:
        _expect(module.PRDCASchemaError, lambda: authority.verify_platform_registration_certificate(replace(prc, artifact_type="OTHER")))
    elif case_id == 82:
        _expect(module.PRDCASchemaError, lambda: authority.verify_platform_registration_certificate(replace(prc, payload_schema="wrong")))
    elif case_id == 83:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.verify_deployment_evidence(replace(evidence, signature_algorithm="RSA")))
    elif case_id == 84:
        _expect(module.PRDCASignatureVerificationError, lambda: authority.verify_deployment_evidence(replace(evidence, status="REVOKED")))
    elif case_id == 85:
        corrupted_payload = {**dict(evidence.payload), "deployment_observed_at": "not-a-timestamp"}
        _expect(module.PRDCACanonicalizationError, lambda: authority.verify_deployment_evidence(replace(evidence, payload=module._mapping_proxy(corrupted_payload))))
    elif case_id == 86:
        class InactiveTransaction:
            active = False

        batch = module.PRDCACertificateBatch(prc, dcc, receipt)
        _expect(module.PRDCATransactionOwnershipError, lambda: authority.persist_certificate_batch(batch=batch, session=InactiveTransaction()))
    elif case_id == 87:
        assert module.PRDCA_OWNER == "WILSY_PLATFORM_REGISTRATION_AND_DEPLOYMENT_CERTIFICATION_AUTHORITY"
        assert module.PRDCA_ALIAS == "WILSY_PRDCA"
    elif case_id == 88:
        assert module.SIGNED_ENVELOPE_SCHEMA == "WILSY-PRDCA-SIGNED-ENVELOPE/V1"
        assert module.PRC_SCHEMA == "WILSY-PLATFORM-REGISTRATION-CERTIFICATE/V1"
        assert module.DCC_SCHEMA == "WILSY-DEPLOYMENT-CERTIFICATION-CERTIFICATE/V1"
        assert module.RECEIPT_SCHEMA == "WILSY-PRDCA-DESCRIPTOR-VERIFICATION-RECEIPT/V1"
    elif case_id == 89:
        assert module.DEPLOYMENT_EVIDENCE_SCHEMA == "WILSY-AUTHENTICATED-RUNTIME-DEPLOYMENT-EVIDENCE/V1"
        assert module.DEPLOYMENT_EVIDENCE_ENVELOPE_SCHEMA == "WILSY-AUTHENTICATED-RUNTIME-DEPLOYMENT-EVIDENCE-ENVELOPE/V1"
    elif case_id == 90:
        assert module.SIGNATURE_ALGORITHM == "Ed25519"
        assert module.SIGNATURE_ENCODING == "base64url_without_padding"
    elif case_id == 91:
        assert module.ID_ALGORITHM == "SHA3-512"
        assert module.ID_FORMAT == "lowercase_128_hex"
        assert module.CERTIFICATE_STATUS_ACTIVE == "ACTIVE"
        assert module.VERIFICATION_STATUS_VERIFIED == "VERIFIED"
    elif case_id == 92:
        assert prc.payload["issuer_authority"] == module.PRDCA_OWNER
        assert dcc.payload["issuer_authority"] == module.PRDCA_OWNER
    elif case_id == 93:
        assert receipt.payload["verifier_authority"] == module.PRDCA_OWNER
        assert receipt.payload["verification_status"] == module.VERIFICATION_STATUS_VERIFIED
    elif case_id == 94:
        assert module.DEPLOYMENT_EVIDENCE_AUTHORITY == "WILSY_AUTHENTICATED_RUNTIME_DEPLOYMENT_EVIDENCE_AUTHORITY"
        assert evidence.producer_authority == module.DEPLOYMENT_EVIDENCE_PRODUCER
        assert evidence.payload["producer_authority"] == module.DEPLOYMENT_EVIDENCE_PRODUCER
        assert evidence.attestation_key_id == EVIDENCE_KEY_ID
    else:
        raise AssertionError(case_id)


@pytest.mark.parametrize("case_id", range(1, 95), ids=[f"case_{i:02d}" for i in range(1, 95)])
def test_prdca_core_behavior(case_id: int, tmp_path: Path) -> None:
    _run_case(case_id, tmp_path)


# ARTIFACT: test_prdca.py
# VERSION: v1.0.4-M11-R8-R3B-P8-P3D-P5-R8-P3KR9
# END OF WILSY OS SOVEREIGN ARTIFACT
