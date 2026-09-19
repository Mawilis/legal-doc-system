"""Direct certificate for the R8O-P4-R7-R3 signed operator authorization domain.

TITLE: WILSY OS R8O-P4-R7-R3 Signed Legal-Corpus Operator Authorization Certificate
VERSION: v1.3.0-R1D-B0F-B4-R8O-P4-R7-R3-LEGAL-CORPUS-OPERATOR-AUTHORIZATION-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the one-key production trust root after its governed
         RETIRED/revision-2 transition, while retaining test-owned ACTIVE
         authorization coverage, the signed envelope, canonical Charter, and
         deterministic R8D evidence boundaries.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_operator_authorization.py
COLLABORATION / OWNERSHIP: Certifies the E1 domain artifact against C1's
                           current one-key resolver; production RETIRED
                           rejection and test-owned ACTIVE paths remain
                           separate evidence. R8D authority, corpus source,
                           and PRDCA crypto certificates remain separate.
CERTIFICATION / UPDATE DATE: 2026-09-18
CHANGELOG: v1.3.0-R1D-B0F-B4-R8O-P4-R7-R3-LEGAL-CORPUS-OPERATOR-AUTHORIZATION-CERT
           certifies the exact production RETIRED/revision-2 record and its
           fail-closed operational rejection, preserves generic ACTIVE and
           RETIRED/REVOKED coverage, and isolates this certificate from
           trust-root importlib.reload identity replacement.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Test-only key material is deterministic and local;
                            no production secret, environment trust, file key,
                            network, Mongo, or request context is used.
TENANT BOUNDARY: PLATFORM-only corpus authority; no tenant or principal input.
AUTHORITY BOUNDARY: Certificate evidence only; this test does not issue,
                    approve, persist, consume, or execute legal authority.
                    A RETIRED production key cannot authorize fresh D1 work.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Every invalid, untrusted, divergent, expired, or
                     partially valid authorization path must reject; public
                     RETIRED production trust is known but non-operational;
                     public trust resolution is not authorization issuance.
"""
from __future__ import annotations

import ast
import base64
from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timedelta, timezone
import hashlib
import importlib
import inspect
import json
from pathlib import Path
from typing import Any, Callable

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

import tools.eos.legal_operations.domain.legal_corpus_operator_authorization as authorization_module
from tools.eos.legal_operations.domain.legal_corpus_operator_authorization import (
    AUTHORITY_MECHANISM,
    AUTHORITY_MECHANISM_VERSION,
    AUTHORITY_SCOPE,
    AUTHORIZED_OPERATION,
    MAX_AUTHORIZATION_LIFETIME,
    R8D_EVIDENCE_ID_PREFIX,
    SCHEMA,
    LegalCorpusOperatorAuthorization,
    LegalCorpusOperatorAuthorizationError,
    LegalCorpusOperatorAuthorizationCanonicalDocumentError,
    LegalCorpusOperatorAuthorizationExpiredError,
    LegalCorpusOperatorAuthorizationKeyValidityError,
    LegalCorpusOperatorAuthorizationNotYetValidError,
    LegalCorpusOperatorAuthorizationOperation,
    LegalCorpusOperatorAuthorizationOperationError,
    LegalCorpusOperatorAuthorizationScope,
    LegalCorpusOperatorAuthorizationSchemaError,
    LegalCorpusOperatorAuthorizationShapeError,
    LegalCorpusOperatorAuthorizationSignatureEncodingError,
    LegalCorpusOperatorAuthorizationSignatureError,
    LegalCorpusOperatorAuthorizationUnknownKeyError,
    LegalCorpusOperatorAuthorizationUntrustedKeyError,
)
from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
)
from tools.eos.legal_operations.domain.legal_corpus_operator_trust_root import (
    AUTHORITY_DOMAIN,
    ED25519_ALGORITHM,
    LegalCorpusOperatorKeyStatus,
    LegalCorpusOperatorTrustRoot,
    LegalCorpusOperatorTrustRootError,
    LegalCorpusOperatorTrustedKey,
    TRUST_ROOT_PROVENANCE,
    TRUST_ROOT_SCOPE,
)
from tools.eos.legal_operations.domain.legal_corpus_provisioning_authority import (
    AUTHORITY_SOURCE_ID,
    AUTHORITY_SOURCE_VERSION,
)
from tools.eos.legal_operations.production_legal_corpus import get_institutional_charter_draft


NOW = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
KEY_ID = "prdca-key:r8j-d2-test"
PRODUCTION_KEY_ID = "prdca-key:legal-corpus-69c7c3e9a67c7e552057d4c0670623be"
PRODUCTION_PUBLIC_KEY = "jfG0IANHA_tSNyjyurpBtTId98fG2l_LhifnfQJ2cXg"
RETIRED_PRODUCTION_KEY_FINGERPRINT = "1ea7ec1e18355b4181d6b652c05be296deb2bb02cf0d5504e1e2ede82278572ee66178df141a4f98cf280af122fb2f55eebedb44262fa552f215c38a5bec2e38"
ISSUER_IDENTITY = "issuer:r8j-d2-test"
TEST_SEED = bytes(range(32))
WRONG_TEST_SEED = bytes(range(1, 33))


def _public_key_text(signing_key: Ed25519PrivateKey) -> str:
    """Encode deterministic test-only raw Ed25519 public bytes canonically."""
    raw = signing_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _trusted_key(
    signing_key: Ed25519PrivateKey,
    *,
    status: LegalCorpusOperatorKeyStatus | None = None,
    valid_from: datetime = NOW - timedelta(days=1),
    valid_until: datetime | None = NOW + timedelta(days=2),
    issuer_identity: str = ISSUER_IDENTITY,
) -> LegalCorpusOperatorTrustedKey:
    """Construct one immutable C1-compatible test trust record in memory."""
    if status is None:
        status = LegalCorpusOperatorKeyStatus.ACTIVE
    public_key = _public_key_text(signing_key)
    fingerprint = LegalCorpusOperatorTrustedKey.fingerprint_for(
        key_id=KEY_ID,
        algorithm=ED25519_ALGORITHM,
        public_key_base64url=public_key,
        issuer_identity=issuer_identity,
        authority_domain=AUTHORITY_DOMAIN,
        scope=TRUST_ROOT_SCOPE,
        permitted_operations=frozenset({AUTHORIZED_OPERATION}),
        valid_from=valid_from,
        valid_until=valid_until,
        status=status,
        revision=1,
        trust_root_provenance=TRUST_ROOT_PROVENANCE,
    )
    return LegalCorpusOperatorTrustedKey(
        key_id=KEY_ID,
        algorithm=ED25519_ALGORITHM,
        public_key_base64url=public_key,
        issuer_identity=issuer_identity,
        authority_domain=AUTHORITY_DOMAIN,
        scope=TRUST_ROOT_SCOPE,
        permitted_operations=frozenset({AUTHORIZED_OPERATION}),
        valid_from=valid_from,
        valid_until=valid_until,
        status=status,
        revision=1,
        trust_root_provenance=TRUST_ROOT_PROVENANCE,
        fingerprint=fingerprint,
    )


def _patch_test_trust(monkeypatch: pytest.MonkeyPatch, trusted_key: LegalCorpusOperatorTrustedKey) -> None:
    """Patch only D1's private resolver seam; never alter C1 source data."""
    def resolve(requested_key_id: str) -> LegalCorpusOperatorTrustedKey:
        if requested_key_id != trusted_key.key_id:
            raise LegalCorpusOperatorTrustRootError("UNKNOWN_TRUSTED_KEY")
        return trusted_key

    monkeypatch.setattr(LegalCorpusOperatorTrustRoot, "resolve", staticmethod(resolve))


def _patch_clock(monkeypatch: pytest.MonkeyPatch, value: datetime) -> None:
    """Patch D1's private UTC clock seam without exposing caller clock authority."""
    monkeypatch.setattr(authorization_module, "_utc_now", lambda: value)


def _authorization(signing_key: Ed25519PrivateKey, **changes: Any) -> LegalCorpusOperatorAuthorization:
    """Create a signed test envelope using the actual D1 canonical payload API."""
    document = get_institutional_charter_draft()
    values: dict[str, Any] = {
        "authorization_id": "r8j-d2-auth-001",
        "key_id": KEY_ID,
        "operation": LegalCorpusOperatorAuthorizationOperation.DRAFT_ADMISSION,
        "scope": LegalCorpusOperatorAuthorizationScope.PLATFORM,
        "source_document_id": document.document_id,
        "source_agreement_type": document.agreement_type,
        "source_version": document.version,
        "source_status": document.status,
        "source_content_reference": document.content_reference,
        "source_sha3_512": document.sha3_512,
        "issued_at": NOW,
        "not_before": NOW - timedelta(minutes=1),
        "expires_at": NOW + timedelta(minutes=5),
        "replay_nonce": "r8j-d2-replay-001",
        "idempotency_key": "r8j-d2-idempotency-001",
        "authority_mechanism": AUTHORITY_MECHANISM,
        "authority_mechanism_version": AUTHORITY_MECHANISM_VERSION,
        "signature": base64.urlsafe_b64encode(b"x" * 64).rstrip(b"=").decode("ascii"),
    }
    values.update(changes)
    unsigned = LegalCorpusOperatorAuthorization(**values)
    values["signature"] = base64.urlsafe_b64encode(signing_key.sign(unsigned.canonical_payload_bytes())).rstrip(b"=").decode("ascii")
    return LegalCorpusOperatorAuthorization(**values)


def _expect_code(error_type: type[LegalCorpusOperatorAuthorizationError], operation: Callable[[], object]) -> None:
    """Assert one exact bounded D1 error family without accepting success."""
    with pytest.raises(error_type):
        operation()


@pytest.fixture(autouse=True)
def _rebind_after_trust_root_reload() -> None:
    """Rebind this certificate to the current trust-root module identities.

    The trust-root direct certificate intentionally exercises ``importlib.reload``.
    Reload replaces enum and class identities in the existing module object.
    Rebinding only the authorization module's imported trust-root symbols keeps
    its exception/class identities stable for parametrized tests while restoring
    the production identity checks against the current trust-root objects.
    """
    global LegalCorpusOperatorKeyStatus
    global LegalCorpusOperatorTrustRoot
    global LegalCorpusOperatorTrustRootError
    global LegalCorpusOperatorTrustedKey
    global AUTHORITY_DOMAIN
    global ED25519_ALGORITHM
    global TRUST_ROOT_PROVENANCE
    global TRUST_ROOT_SCOPE

    current_trust_root = importlib.import_module(
        "tools.eos.legal_operations.domain.legal_corpus_operator_trust_root"
    )
    for name in (
        "LegalCorpusOperatorKeyStatus",
        "LegalCorpusOperatorTrustRoot",
        "LegalCorpusOperatorTrustRootError",
        "LegalCorpusOperatorTrustedKey",
        "AUTHORITY_DOMAIN",
        "ED25519_ALGORITHM",
        "TRUST_ROOT_PROVENANCE",
        "TRUST_ROOT_SCOPE",
    ):
        current_value = getattr(current_trust_root, name)
        setattr(authorization_module, name, current_value)
        globals()[name] = current_value


def test_production_root_resolves_retired_key_and_rejects_fresh_authority(monkeypatch: pytest.MonkeyPatch) -> None:
    """The known production record is retired and cannot authorize fresh D1 work."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    authorization = _authorization(signing_key, key_id=PRODUCTION_KEY_ID)
    production_key = LegalCorpusOperatorTrustRoot.resolve(PRODUCTION_KEY_ID)
    assert LegalCorpusOperatorTrustRoot.production_key_count() == 1
    assert production_key.key_id == PRODUCTION_KEY_ID
    assert production_key.public_key_base64url == PRODUCTION_PUBLIC_KEY
    assert production_key.issuer_identity == "WILSY_OS_LEGAL_CORPUS_RELEASE_AUTHORITY:V1"
    assert production_key.scope == TRUST_ROOT_SCOPE
    assert production_key.permitted_operations == frozenset({AUTHORIZED_OPERATION})
    assert production_key.status is LegalCorpusOperatorKeyStatus.RETIRED
    assert production_key.revision == 2
    assert production_key.fingerprint == RETIRED_PRODUCTION_KEY_FINGERPRINT
    _patch_clock(monkeypatch, NOW)
    _expect_code(
        LegalCorpusOperatorAuthorizationUntrustedKeyError,
        authorization.verify,
    )
    _expect_code(
        LegalCorpusOperatorAuthorizationUntrustedKeyError,
        authorization.derive_provisioning_authority_evidence,
    )


def test_production_key_wrong_signature_matrix_is_not_unknown_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Known RETIRED production trust rejects before signature validation."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    _patch_clock(monkeypatch, NOW)
    authorization = _authorization(signing_key, key_id=PRODUCTION_KEY_ID)
    malformed = _authorization(signing_key, key_id=PRODUCTION_KEY_ID)
    object.__setattr__(malformed, "signature", base64.urlsafe_b64encode(b"m" * 63).rstrip(b"=").decode("ascii"))
    _expect_code(
        LegalCorpusOperatorAuthorizationUntrustedKeyError,
        malformed.verify,
    )
    signature_bytes = bytearray(base64.urlsafe_b64decode(authorization.signature + "=="))
    signature_bytes[0] ^= 1
    bit_flipped = replace(authorization, signature=base64.urlsafe_b64encode(bytes(signature_bytes)).rstrip(b"=").decode("ascii"))
    _expect_code(
        LegalCorpusOperatorAuthorizationUntrustedKeyError,
        bit_flipped.verify,
    )

    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    active_authorization = _authorization(signing_key)
    active_malformed = _authorization(signing_key)
    object.__setattr__(active_malformed, "signature", base64.urlsafe_b64encode(b"m" * 63).rstrip(b"=").decode("ascii"))
    _expect_code(LegalCorpusOperatorAuthorizationSignatureEncodingError, active_malformed.verify)
    active_signature_bytes = bytearray(base64.urlsafe_b64decode(active_authorization.signature + "=="))
    active_signature_bytes[0] ^= 1
    active_bit_flipped = replace(
        active_authorization,
        signature=base64.urlsafe_b64encode(bytes(active_signature_bytes)).rstrip(b"=").decode("ascii"),
    )
    _expect_code(LegalCorpusOperatorAuthorizationSignatureError, active_bit_flipped.verify)


def test_unknown_second_key_remains_distinct_from_production_signature_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """A validly shaped absent key fails at trust resolution, before crypto."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    _patch_clock(monkeypatch, NOW)
    unknown = _authorization(signing_key, key_id="prdca-key:legal-corpus-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    _expect_code(LegalCorpusOperatorAuthorizationUnknownKeyError, unknown.verify)


def test_test_trust_never_becomes_production_trust(monkeypatch: pytest.MonkeyPatch) -> None:
    """A positive TEST-only seam leaves C1's one-key production root unchanged."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    _patch_clock(monkeypatch, NOW)
    authorization = _authorization(signing_key)
    assert authorization.verify().issuer_identity == ISSUER_IDENTITY
    assert LegalCorpusOperatorTrustRoot.production_key_count() == 1
    assert PRODUCTION_KEY_ID in {item.key_id for item in LegalCorpusOperatorTrustRoot.all_keys()}


def test_canonical_payload_has_exact_fields_and_excludes_runtime_authority() -> None:
    """Only frozen signed semantic fields enter the deterministic preimage."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    authorization = _authorization(signing_key)
    expected = {
        "schema", "authorization_id", "key_id", "operation", "scope",
        "source_document_id", "source_agreement_type", "source_version",
        "source_status", "source_content_reference", "source_sha3_512",
        "issued_at", "not_before", "expires_at", "replay_nonce",
        "idempotency_key", "authority_mechanism", "authority_mechanism_version",
    }
    assert set(authorization.canonical_payload()) == expected
    assert "signature" not in authorization.canonical_payload()
    assert "verification_time" not in authorization.canonical_payload()
    assert authorization.canonical_payload_bytes() == authorization.canonical_payload_bytes()
    assert json.loads(authorization.canonical_payload_bytes().decode("utf-8")) == authorization.canonical_payload()
    assert authorization.canonical_payload_bytes().decode("utf-8").encode("utf-8") == authorization.canonical_payload_bytes()
    assert list(authorization.canonical_payload()) == sorted(authorization.canonical_payload())


@pytest.mark.parametrize("field", ["key_id", "source_version", "source_sha3_512", "expires_at", "idempotency_key", "signature"])
def test_authorization_is_immutable(field: str) -> None:
    """Frozen semantics prevent in-place authority or signature rewriting."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    authorization = _authorization(signing_key)
    value: object = authorization.expires_at + timedelta(minutes=1) if field == "expires_at" else "changed"
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        setattr(authorization, field, value)


@pytest.mark.parametrize(
    ("changes", "error_type"),
    [
        ({"authorization_id": ""}, LegalCorpusOperatorAuthorizationShapeError),
        ({"key_id": ""}, LegalCorpusOperatorAuthorizationShapeError),
        ({"key_id": "not-a-key"}, LegalCorpusOperatorAuthorizationShapeError),
        ({"operation": "APPROVE"}, LegalCorpusOperatorAuthorizationOperationError),
        ({"scope": "TENANT"}, LegalCorpusOperatorAuthorizationOperationError),
        ({"source_status": LegalDocumentStatus.APPROVED}, LegalCorpusOperatorAuthorizationOperationError),
        ({"source_status": LegalDocumentStatus.RETIRED}, LegalCorpusOperatorAuthorizationOperationError),
        ({"source_sha3_512": "g" * 128}, LegalCorpusOperatorAuthorizationShapeError),
        ({"replay_nonce": ""}, LegalCorpusOperatorAuthorizationShapeError),
        ({"idempotency_key": ""}, LegalCorpusOperatorAuthorizationShapeError),
        ({"issued_at": datetime(2026, 9, 18, 12)}, LegalCorpusOperatorAuthorizationShapeError),
        ({"not_before": datetime(2026, 9, 18, 12)}, LegalCorpusOperatorAuthorizationShapeError),
        ({"expires_at": datetime(2026, 9, 18, 12)}, LegalCorpusOperatorAuthorizationShapeError),
        ({"not_before": NOW + timedelta(minutes=2)}, LegalCorpusOperatorAuthorizationOperationError),
        ({"expires_at": NOW - timedelta(minutes=2)}, LegalCorpusOperatorAuthorizationOperationError),
        ({"signature": "not-base64"}, LegalCorpusOperatorAuthorizationSignatureEncodingError),
        ({"signature": base64.urlsafe_b64encode(b"x" * 63).rstrip(b"=").decode("ascii")}, LegalCorpusOperatorAuthorizationSignatureEncodingError),
    ],
)
def test_structural_validation_is_fail_closed(changes: dict[str, Any], error_type: type[LegalCorpusOperatorAuthorizationError]) -> None:
    """Actual D1 construction errors reject malformed authority inputs."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    with pytest.raises(error_type):
        _authorization(signing_key, **changes)


def test_ed25519_valid_wrong_key_malformed_and_bit_flipped_signatures(monkeypatch: pytest.MonkeyPatch) -> None:
    """Only the matching Ed25519 public key authenticates canonical bytes."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    wrong_key = Ed25519PrivateKey.from_private_bytes(WRONG_TEST_SEED)
    _patch_clock(monkeypatch, NOW)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    authorization = _authorization(signing_key)
    assert authorization.verify().key_id == KEY_ID
    _patch_test_trust(monkeypatch, _trusted_key(wrong_key))
    _expect_code(LegalCorpusOperatorAuthorizationSignatureError, authorization.verify)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    signature_bytes = bytearray(base64.urlsafe_b64decode(authorization.signature + "=="))
    signature_bytes[0] ^= 1
    bit_flipped = replace(authorization, signature=base64.urlsafe_b64encode(bytes(signature_bytes)).rstrip(b"=").decode("ascii"))
    _expect_code(LegalCorpusOperatorAuthorizationSignatureError, bit_flipped.verify)
    different_payload_signature = base64.urlsafe_b64encode(signing_key.sign(b"different-payload")).rstrip(b"=").decode("ascii")
    different_payload = replace(authorization, signature=different_payload_signature)
    _expect_code(LegalCorpusOperatorAuthorizationSignatureError, different_payload.verify)


def test_signed_field_tampering_rejects_before_r8d_derivation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Changing signed semantics while retaining the original signature fails."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    _patch_clock(monkeypatch, NOW)
    authorization = _authorization(signing_key)
    changes = (
        {"source_document_id": "OTHER-DOCUMENT"},
        {"source_version": "9.9.9-DRAFT"},
        {"source_sha3_512": "0" * 128},
        {"idempotency_key": "different-idempotency"},
        {"expires_at": NOW + timedelta(minutes=10)},
    )
    for change in changes:
        tampered = replace(authorization, **change)
        _expect_code(LegalCorpusOperatorAuthorizationSignatureError, tampered.verify)
        _expect_code(LegalCorpusOperatorAuthorizationSignatureError, tampered.derive_provisioning_authority_evidence)
    for change, error_type in (({"operation": "APPROVE"}, LegalCorpusOperatorAuthorizationOperationError), ({"scope": "TENANT"}, LegalCorpusOperatorAuthorizationOperationError)):
        _expect_code(error_type, lambda change=change: replace(authorization, **change))


def test_trusted_issuer_and_active_permissioned_path(monkeypatch: pytest.MonkeyPatch) -> None:
    """Authenticated actor provenance comes from the trusted C1 record."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    trusted = _trusted_key(signing_key, issuer_identity="issuer:canonical-record")
    _patch_test_trust(monkeypatch, trusted)
    _patch_clock(monkeypatch, NOW)
    authorization = _authorization(signing_key)
    evidence = authorization.derive_provisioning_authority_evidence()
    assert evidence.actor_representation == "issuer:canonical-record"
    assert "actor_representation" not in authorization.canonical_payload()
    assert evidence.authorized_at == authorization.issued_at
    assert evidence.idempotency_key == authorization.idempotency_key


def test_c1_rejects_unsupported_permission_and_scope_records() -> None:
    """C1 construction blocks a key that cannot carry the exact permission/scope."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    with pytest.raises(LegalCorpusOperatorTrustRootError):
        LegalCorpusOperatorTrustedKey.fingerprint_for(
            key_id=KEY_ID,
            algorithm=ED25519_ALGORITHM,
            public_key_base64url=_public_key_text(signing_key),
            issuer_identity=ISSUER_IDENTITY,
            authority_domain=AUTHORITY_DOMAIN,
            scope=TRUST_ROOT_SCOPE,
            permitted_operations=frozenset({"OTHER_OPERATION"}),
            valid_from=NOW - timedelta(days=1),
            valid_until=NOW + timedelta(days=1),
            status=LegalCorpusOperatorKeyStatus.ACTIVE,
            revision=1,
            trust_root_provenance=TRUST_ROOT_PROVENANCE,
        )
    with pytest.raises(LegalCorpusOperatorTrustRootError):
        LegalCorpusOperatorTrustedKey.fingerprint_for(
            key_id=KEY_ID,
            algorithm=ED25519_ALGORITHM,
            public_key_base64url=_public_key_text(signing_key),
            issuer_identity=ISSUER_IDENTITY,
            authority_domain=AUTHORITY_DOMAIN,
            scope="TENANT",
            permitted_operations=frozenset({AUTHORIZED_OPERATION}),
            valid_from=NOW - timedelta(days=1),
            valid_until=NOW + timedelta(days=1),
            status=LegalCorpusOperatorKeyStatus.ACTIVE,
            revision=1,
            trust_root_provenance=TRUST_ROOT_PROVENANCE,
        )


def test_key_lifecycle_and_validity_matrix(monkeypatch: pytest.MonkeyPatch) -> None:
    """ACTIVE authorizes; RETIRED and REVOKED fail closed for new operations."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    _patch_clock(monkeypatch, NOW)
    authorization = _authorization(signing_key)
    active = _trusted_key(signing_key)
    _patch_test_trust(monkeypatch, active)
    assert authorization.verify().status is LegalCorpusOperatorKeyStatus.ACTIVE
    retired = _trusted_key(signing_key, status=LegalCorpusOperatorKeyStatus.RETIRED)
    _patch_test_trust(monkeypatch, retired)
    _expect_code(LegalCorpusOperatorAuthorizationUntrustedKeyError, authorization.verify)
    _expect_code(LegalCorpusOperatorAuthorizationUntrustedKeyError, authorization.derive_provisioning_authority_evidence)
    revoked = _trusted_key(signing_key, status=LegalCorpusOperatorKeyStatus.REVOKED)
    _patch_test_trust(monkeypatch, revoked)
    _expect_code(LegalCorpusOperatorAuthorizationUntrustedKeyError, authorization.verify)
    before = _trusted_key(signing_key, valid_from=NOW + timedelta(minutes=1))
    _patch_test_trust(monkeypatch, before)
    _expect_code(LegalCorpusOperatorAuthorizationKeyValidityError, authorization.verify)
    after = _trusted_key(signing_key, valid_from=NOW - timedelta(days=2), valid_until=NOW - timedelta(minutes=1))
    _patch_test_trust(monkeypatch, after)
    _expect_code(LegalCorpusOperatorAuthorizationKeyValidityError, authorization.verify)
    open_ended = _trusted_key(signing_key, valid_until=None)
    _patch_test_trust(monkeypatch, open_ended)
    assert authorization.verify().status is LegalCorpusOperatorKeyStatus.ACTIVE


def test_authorization_temporal_boundaries_and_maximum_lifetime(monkeypatch: pytest.MonkeyPatch) -> None:
    """E1 enforces PT30M from issued_at with inclusive zero-skew endpoints."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    assert MAX_AUTHORIZATION_LIFETIME == timedelta(minutes=30)
    assert MAX_AUTHORIZATION_LIFETIME.total_seconds() == 1800
    lower = _authorization(signing_key, expires_at=NOW + timedelta(minutes=30))
    _patch_clock(monkeypatch, lower.not_before - timedelta(microseconds=1))
    _expect_code(LegalCorpusOperatorAuthorizationNotYetValidError, lower.verify)
    _patch_clock(monkeypatch, lower.not_before)
    assert lower.verify().key_id == KEY_ID
    _patch_clock(monkeypatch, lower.issued_at)
    assert lower.verify().key_id == KEY_ID
    _patch_clock(monkeypatch, lower.expires_at)
    assert lower.verify().key_id == KEY_ID
    _patch_clock(monkeypatch, lower.expires_at + timedelta(microseconds=1))
    _expect_code(LegalCorpusOperatorAuthorizationExpiredError, lower.verify)


def test_maximum_lifetime_uses_issued_at_not_not_before(monkeypatch: pytest.MonkeyPatch) -> None:
    """A one-minute issued/not-before offset proves the comparison basis."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    _patch_clock(monkeypatch, NOW)
    candidate = _authorization(
        signing_key,
        not_before=NOW - timedelta(minutes=1),
        expires_at=NOW + timedelta(minutes=30),
    )
    assert candidate.expires_at - candidate.issued_at == timedelta(minutes=30)
    assert candidate.expires_at - candidate.not_before == timedelta(minutes=31)
    assert candidate.verify().key_id == KEY_ID


def test_lifetime_boundaries_reject_overlong_even_when_signed(monkeypatch: pytest.MonkeyPatch) -> None:
    """A validly signed overlong payload is rejected before D1 verification."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    for delta in (timedelta(microseconds=1), timedelta(minutes=1)):
        payload = _authorization(signing_key).to_document()
        payload["expires_at"] = (NOW + timedelta(minutes=30) + delta).isoformat(timespec="microseconds")
        unsigned_payload = dict(payload)
        unsigned_payload.pop("signature")
        signed_bytes = json.dumps(unsigned_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        payload["signature"] = base64.urlsafe_b64encode(signing_key.sign(signed_bytes)).rstrip(b"=").decode("ascii")
        with pytest.raises(LegalCorpusOperatorAuthorizationOperationError) as error:
            LegalCorpusOperatorAuthorization.from_document(payload)
        assert error.value.code == "AUTHORIZATION_LIFETIME_EXCEEDED"


@pytest.mark.parametrize(
    ("changes", "code"),
    [
        ({"issued_at": NOW - timedelta(minutes=2), "not_before": NOW - timedelta(minutes=1)}, "AUTHORIZATION_VALIDITY_INTERVAL_INVALID"),
        ({"issued_at": NOW + timedelta(minutes=6), "expires_at": NOW + timedelta(minutes=5)}, "AUTHORIZATION_VALIDITY_INTERVAL_INVALID"),
        ({"not_before": NOW + timedelta(minutes=6), "expires_at": NOW + timedelta(minutes=5)}, "AUTHORIZATION_VALIDITY_INTERVAL_INVALID"),
    ],
)
def test_timestamp_ordering_is_fail_closed(changes: dict[str, Any], code: str) -> None:
    """Issued, not-before, and expiry ordering remains structurally strict."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    with pytest.raises(LegalCorpusOperatorAuthorizationOperationError) as error:
        _authorization(signing_key, **changes)
    assert error.value.code == code


def test_canonical_charter_binding_and_all_mismatch_states(monkeypatch: pytest.MonkeyPatch) -> None:
    """Only the exact server-owned Institutional Charter draft is admissible."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    _patch_clock(monkeypatch, NOW)
    authorization = _authorization(signing_key)
    document = get_institutional_charter_draft()
    assert document.document_id == "WILSY-OS-INSTITUTIONAL-CHARTER"
    assert document.version == "1.0.0-DRAFT"
    assert document.agreement_type is LegalAgreementType.INSTITUTIONAL_CHARTER
    assert document.status is LegalDocumentStatus.DRAFT_REVIEW_REQUIRED
    assert authorization.verify().issuer_identity == ISSUER_IDENTITY
    mismatches = (
        {"source_document_id": "OTHER"},
        {"source_agreement_type": LegalAgreementType.USER_TERMS},
        {"source_version": "2.0.0-DRAFT"},
        {"source_content_reference": "wilsy-os://other"},
        {"source_sha3_512": "a" * 128},
    )
    for change in mismatches:
        _expect_code(LegalCorpusOperatorAuthorizationCanonicalDocumentError, _authorization(signing_key, **change).verify)
    for status in (LegalDocumentStatus.APPROVED, LegalDocumentStatus.RETIRED):
        monkeypatch.setattr(authorization_module, "get_institutional_charter_draft", lambda status=status: replace(document, status=status))
        _expect_code(LegalCorpusOperatorAuthorizationCanonicalDocumentError, authorization.verify)
    monkeypatch.setattr(authorization_module, "get_institutional_charter_draft", lambda: document)


def test_canonical_source_is_not_caller_selectable() -> None:
    """The public verifier accepts no document, corpus, resolver, or clock argument."""
    authorization_fields = {field.name for field in fields(LegalCorpusOperatorAuthorization)}
    assert "document" not in authorization_fields
    assert "tenant_id" not in authorization_fields
    assert "principal_id" not in authorization_fields
    assert set(inspect.signature(LegalCorpusOperatorAuthorization.verify).parameters) == {"self"}
    assert set(inspect.signature(LegalCorpusOperatorAuthorization.derive_provisioning_authority_evidence).parameters) == {"self"}


def test_r8d_derivation_is_exact_and_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    """Successful verification alone yields one stable R8D evidence value."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    trusted = _trusted_key(signing_key, issuer_identity=ISSUER_IDENTITY)
    _patch_test_trust(monkeypatch, trusted)
    _patch_clock(monkeypatch, NOW)
    authorization = _authorization(signing_key)
    first = authorization.derive_provisioning_authority_evidence()
    second = authorization.derive_provisioning_authority_evidence()
    assert first == second
    expected_id = hashlib.sha3_512((R8D_EVIDENCE_ID_PREFIX + authorization.authorization_id).encode("utf-8")).hexdigest()
    assert first.authority_evidence_id == expected_id
    assert first.actor_representation == trusted.issuer_identity
    assert first.authorized_at == authorization.issued_at
    assert first.idempotency_key == authorization.idempotency_key
    assert first.source_document_id == "WILSY-OS-INSTITUTIONAL-CHARTER"
    assert first.source_version == "1.0.0-DRAFT"
    assert first.source_agreement_type is LegalAgreementType.INSTITUTIONAL_CHARTER
    assert first.source_status is LegalDocumentStatus.DRAFT_REVIEW_REQUIRED
    assert first.authority_source_id.value == AUTHORITY_SOURCE_ID
    assert first.authority_source_version == AUTHORITY_SOURCE_VERSION
    different = _authorization(signing_key, authorization_id="r8j-d2-auth-002")
    different_evidence = different.derive_provisioning_authority_evidence()
    assert different_evidence.authority_evidence_id != first.authority_evidence_id
    assert different_evidence.idempotency_key == different.idempotency_key


def test_unknown_signature_temporal_and_canonical_failure_never_derives_r8d(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every failed verification boundary remains upstream of R8D evidence."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    _patch_clock(monkeypatch, NOW)
    valid = _authorization(signing_key)
    failures: tuple[tuple[LegalCorpusOperatorAuthorization, type[LegalCorpusOperatorAuthorizationError]], ...] = (
        (replace(valid, signature=base64.urlsafe_b64encode(b"y" * 64).rstrip(b"=").decode("ascii")), LegalCorpusOperatorAuthorizationSignatureError),
        (_authorization(signing_key, source_version="wrong-version"), LegalCorpusOperatorAuthorizationCanonicalDocumentError),
    )
    for candidate, error_type in failures:
        _expect_code(error_type, candidate.derive_provisioning_authority_evidence)


def test_r8d_derivation_is_gated_for_temporal_and_lifecycle_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    """Overlong, pre-window, expired, retired, and revoked values never reach R8D."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    _patch_clock(monkeypatch, NOW)

    def forbidden_fingerprint(**_: object) -> str:
        raise AssertionError("R8D fingerprint must not run after failed D1 verification")

    monkeypatch.setattr(
        "tools.eos.legal_operations.domain.legal_corpus_provisioning_authority.LegalCorpusProvisioningAuthorityEvidence.fingerprint_for",
        staticmethod(forbidden_fingerprint),
    )
    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    before = _authorization(
        signing_key,
        issued_at=NOW + timedelta(minutes=1),
        not_before=NOW + timedelta(minutes=1),
        expires_at=NOW + timedelta(minutes=5),
    )
    _expect_code(LegalCorpusOperatorAuthorizationNotYetValidError, before.derive_provisioning_authority_evidence)
    expired = _authorization(signing_key, expires_at=NOW - timedelta(microseconds=1), issued_at=NOW - timedelta(minutes=1), not_before=NOW - timedelta(minutes=2))
    _expect_code(LegalCorpusOperatorAuthorizationExpiredError, expired.derive_provisioning_authority_evidence)
    retired = _authorization(signing_key)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key, status=LegalCorpusOperatorKeyStatus.RETIRED))
    _expect_code(LegalCorpusOperatorAuthorizationUntrustedKeyError, retired.derive_provisioning_authority_evidence)
    revoked = _authorization(signing_key)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key, status=LegalCorpusOperatorKeyStatus.REVOKED))
    _expect_code(LegalCorpusOperatorAuthorizationUntrustedKeyError, revoked.derive_provisioning_authority_evidence)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    overlong_payload = _authorization(signing_key).to_document()
    overlong_payload["expires_at"] = (NOW + timedelta(minutes=30, microseconds=1)).isoformat(timespec="microseconds")
    unsigned_payload = dict(overlong_payload)
    unsigned_payload.pop("signature")
    signed_bytes = json.dumps(unsigned_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    overlong_payload["signature"] = base64.urlsafe_b64encode(signing_key.sign(signed_bytes)).rstrip(b"=").decode("ascii")
    with pytest.raises(LegalCorpusOperatorAuthorizationOperationError):
        LegalCorpusOperatorAuthorization.from_document(overlong_payload)


def test_fresh_reverification_after_expiry_rejects_same_signed_value(monkeypatch: pytest.MonkeyPatch) -> None:
    """A value valid for one attempt must be reverified for a later retry."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    authorization = _authorization(signing_key)
    _patch_clock(monkeypatch, NOW)
    assert authorization.verify().key_id == KEY_ID
    _patch_clock(monkeypatch, authorization.expires_at + timedelta(microseconds=1))
    _expect_code(LegalCorpusOperatorAuthorizationExpiredError, authorization.verify)


def test_verification_clock_and_transaction_lifecycle_are_not_public_authority() -> None:
    """D1 exposes no caller clock, session, transaction, commit, or readback API."""
    verify_parameters = set(inspect.signature(LegalCorpusOperatorAuthorization.verify).parameters)
    derive_parameters = set(inspect.signature(LegalCorpusOperatorAuthorization.derive_provisioning_authority_evidence).parameters)
    assert verify_parameters == {"self"}
    assert derive_parameters == {"self"}
    source = Path("tools/eos/legal_operations/domain/legal_corpus_operator_authorization.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    assert not names.intersection({"start_transaction", "commit", "abort", "create_session", "readback"})
    assert "verification_time" not in source


def test_strict_hydration_round_trip_and_parsing_is_not_verification(monkeypatch: pytest.MonkeyPatch) -> None:
    """Envelope hydration is exact and inert until the verifier is called."""
    signing_key = Ed25519PrivateKey.from_private_bytes(TEST_SEED)
    authorization = _authorization(signing_key)
    hydrated = LegalCorpusOperatorAuthorization.from_document(authorization.to_document())
    assert hydrated == authorization
    missing = authorization.to_document()
    missing.pop("signature")
    with pytest.raises(LegalCorpusOperatorAuthorizationSchemaError):
        LegalCorpusOperatorAuthorization.from_document(missing)
    unexpected = authorization.to_document()
    unexpected["extra"] = "reject"
    with pytest.raises(LegalCorpusOperatorAuthorizationSchemaError):
        LegalCorpusOperatorAuthorization.from_document(unexpected)
    malformed_time = authorization.to_document()
    malformed_time["issued_at"] = "not-a-time"
    with pytest.raises(LegalCorpusOperatorAuthorizationShapeError):
        LegalCorpusOperatorAuthorization.from_document(malformed_time)
    _expect_code(LegalCorpusOperatorAuthorizationUnknownKeyError, hydrated.verify)
    _patch_test_trust(monkeypatch, _trusted_key(signing_key))
    _patch_clock(monkeypatch, NOW)
    assert hydrated.verify().key_id == KEY_ID


def test_no_signing_private_loader_or_trust_override_surface() -> None:
    """The D1 module exposes verification only and has no authority loaders."""
    source = Path("tools/eos/legal_operations/domain/legal_corpus_operator_authorization.py").read_text(encoding="utf-8")
    assert "Ed25519PrivateKey" not in source
    assert "def sign(" not in source
    assert "trusted_keys=" not in source
    assert "public_key=" not in source
    assert "resolver=" not in source
    assert "trust_root=" not in source
    assert "os.environ" not in source
    assert "open(" not in source
    public_methods = {
        name for name, value in inspect.getmembers(LegalCorpusOperatorAuthorization, predicate=inspect.isroutine)
        if not name.startswith("__")
    }
    assert not any(name.casefold().startswith("sign") for name in public_methods)


def test_dependency_and_side_effect_boundary_is_pure() -> None:
    """D1 imports only pure domain, corpus, crypto-exception, and stdlib surfaces."""
    path = Path("tools/eos/legal_operations/domain/legal_corpus_operator_authorization.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imports.extend(alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names)
    forbidden = ("pymongo", "kernel", "registry", "fastapi", "http", "client", "browser", "r8f", "r8h", "prdca")
    assert not any(token in module.casefold() for module in imports for token in forbidden)
    assert "LegalDocumentRegistry" not in path.read_text(encoding="utf-8")
    assert "MongoClient" not in path.read_text(encoding="utf-8")
    assert LegalCorpusOperatorTrustRoot.production_key_count() == 1


# ARTIFACT: test_legal_corpus_operator_authorization.py
# VERSION: v1.3.0-R1D-B0F-B4-R8O-P4-R7-R3-LEGAL-CORPUS-OPERATOR-AUTHORIZATION-CERT
# AUTHORITY BOUNDARY: direct certificate evidence only; no authorization issuance
# TENANT POSTURE: PLATFORM corpus scope; no tenant or principal authority
# FAIL-CLOSED POSTURE: malformed, untrusted, divergent, expired, tampered, and retired-production values reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
