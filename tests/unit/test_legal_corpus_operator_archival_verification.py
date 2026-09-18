"""Direct certificate for the authenticity-only archival verifier.

TITLE: WILSY OS Legal Corpus Archival Authenticity Verifier Certificate
VERSION: v1.0.0-R1D-B0F-B4-R8O-P3C-C1-LEGAL-CORPUS-ARCHIVAL-AUTHENTICITY-VERIFIER-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies P1, P2, and P7 re-verification over deterministic public
         archival snapshots, exact D1 preimage reuse, fail-closed tamper
         handling, immutable results, and the absence of mutation authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_operator_archival_verification.py
COLLABORATION / OWNERSHIP: Direct certificate for P3C; P3A, D1, the public
                            trust root, R8D, and production capture remain
                            separately governed artifacts.
CERTIFICATION / UPDATE DATE: 2026-09-18
CHANGELOG: v1.0.0-R1D-B0F-B4-R8O-P3C-C1 certifies synthetic in-memory
           Ed25519 interoperability, exact D1 canonical signing semantics,
           issuance-time boundaries, snapshot integrity, and non-authority
           limitations without production data or persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic public fixtures and ephemeral test-only
                            private keys exist only in memory; no production
                            authorization, signer, secret, network, or Mongo
                            surface is accessed.
TENANT BOUNDARY: PLATFORM archival evidence only; no tenant or principal data.
AUTHORITY BOUNDARY: Certificate evidence only; P3C cannot authorize, admit,
                    sign, approve, persist, execute, or promote evidence.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Every malformed, tampered, temporally invalid, or
                     authority-ambiguous fixture must raise the bounded P3C
                     verification error; no skip or xfail path exists.
"""
from __future__ import annotations

import ast
import base64
from dataclasses import FrozenInstanceError, dataclass, replace
from datetime import datetime, timedelta, timezone
import hashlib
import inspect
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from tools.eos.legal_operations.domain import legal_corpus_archival_evidence as archival
from tools.eos.legal_operations.domain import legal_corpus_operator_archival_verification as verifier
from tools.eos.legal_operations.domain import legal_corpus_operator_trust_root as trust_domain
from tools.eos.legal_operations.domain.legal_acceptance import LegalAgreementType, LegalDocumentStatus
from tools.eos.legal_operations.domain.legal_corpus_operator_authorization import (
    AUTHORITY_MECHANISM,
    AUTHORITY_MECHANISM_VERSION,
    SCHEMA as AUTHORIZATION_SCHEMA,
    LegalCorpusOperatorAuthorization,
    LegalCorpusOperatorAuthorizationError,
    LegalCorpusOperatorAuthorizationOperation,
    LegalCorpusOperatorAuthorizationScope,
)
from tools.eos.legal_operations.domain.legal_corpus_operator_trust_root import (
    AUTHORITY_DOMAIN,
    AUTHORIZED_OPERATION,
    ED25519_ALGORITHM,
    LegalCorpusOperatorKeyStatus,
    LegalCorpusOperatorTrustedKey,
    TRUST_ROOT_PROVENANCE,
    TRUST_ROOT_SCOPE,
)


P3A_PATH = Path("tools/eos/legal_operations/domain/legal_corpus_archival_evidence.py")
P3C_PATH = Path("tools/eos/legal_operations/domain/legal_corpus_operator_archival_verification.py")
EXPECTED_P3A_BYTES = 50369
EXPECTED_P3A_SHA3_512 = "0bf3a923508526afaacd5ae1445db21fbbed82909643a71479551a54eba39dd230df76207e3013c50077f1b2e80375fc2d561b3df74ae710f6bec092a255489d"
EXPECTED_P3C_BYTES = 17325
EXPECTED_P3C_SHA3_512 = "a9400439baa9cf4f34f371b45032f908d4dfc04ac16fb95e9bde670edbbcdfdcf21c8fdc23afe26c9328280369c436e34a93c266e5d03f3c6585f19e10269484"
NOW = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
KEY_ID = "prdca-key:synthetic-archival-c1"
AUTHORIZATION_ID = "synthetic-authorization-c1"
ISSUER = "WILSY_OS_SYNTHETIC_RELEASE_AUTHORITY:V1"
PRIVATE_SEED = bytes(range(32))
PUBLIC_KEY = base64.urlsafe_b64encode(
    Ed25519PrivateKey.from_private_bytes(PRIVATE_SEED)
    .public_key()
    .public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
).decode("ascii").rstrip("=")
DOCUMENT_ID = "WILSY-OS-SYNTHETIC-CHARTER"
DOCUMENT_VERSION = "1.0.0-DRAFT"
CONTENT_REFERENCE = "wilsy-os://synthetic/legal-corpus/1.0.0-draft"
SOURCE_DIGEST = "11" * 64
FILE_DIGEST = "22" * 64


@dataclass(frozen=True, slots=True)
class Fixture:
    """Synthetic public snapshots plus an in-memory test-only signer."""

    private_key: Ed25519PrivateKey
    authorization: LegalCorpusOperatorAuthorization
    authorization_snapshot: archival.LegalCorpusArchivalAuthorizationSnapshot
    trust_snapshot: archival.LegalCorpusArchivalTrustSnapshot


def _b64(value: bytes) -> str:
    """Encode bytes as the repository's unpadded base64url primitive."""
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _trust_fingerprint(
    *,
    public_key: str = PUBLIC_KEY,
    issuer: str = ISSUER,
    status: LegalCorpusOperatorKeyStatus = LegalCorpusOperatorKeyStatus.ACTIVE,
    valid_from: datetime = NOW - timedelta(hours=1),
    valid_until: datetime | None = NOW + timedelta(hours=1),
) -> str:
    """Build the exact source-owned trust-record fingerprint."""
    return LegalCorpusOperatorTrustedKey.fingerprint_for(
        key_id=KEY_ID,
        algorithm=ED25519_ALGORITHM,
        public_key_base64url=public_key,
        issuer_identity=issuer,
        authority_domain=AUTHORITY_DOMAIN,
        scope=TRUST_ROOT_SCOPE,
        permitted_operations=frozenset({AUTHORIZED_OPERATION}),
        valid_from=valid_from,
        valid_until=valid_until,
        status=status,
        revision=1,
        trust_root_provenance=TRUST_ROOT_PROVENANCE,
    )


def _trust_snapshot(
    *,
    public_key: str = PUBLIC_KEY,
    issuer: str = ISSUER,
    status: LegalCorpusOperatorKeyStatus = LegalCorpusOperatorKeyStatus.ACTIVE,
    valid_from: datetime = NOW - timedelta(hours=1),
    valid_until: datetime | None = NOW + timedelta(hours=1),
    snapshot_observed_at: datetime = NOW,
    snapshot_source_identity: str = "synthetic-source:trust-root:v1",
    snapshot_source_fingerprint: str = "ab" * 64,
    trust_record_fingerprint: str | None = None,
) -> archival.LegalCorpusArchivalTrustSnapshot:
    """Construct a self-consistent P3A trust snapshot."""
    trust_record = trust_record_fingerprint or _trust_fingerprint(
        public_key=public_key,
        issuer=issuer,
        status=status,
        valid_from=valid_from,
        valid_until=valid_until,
    )
    values: dict[str, Any] = {
        "key_id": KEY_ID,
        "algorithm": ED25519_ALGORITHM,
        "issuer": issuer,
        "authority_domain": AUTHORITY_DOMAIN,
        "scope": TRUST_ROOT_SCOPE,
        "operation": AUTHORIZED_OPERATION,
        "permitted_operations": (AUTHORIZED_OPERATION,),
        "public_key": public_key,
        "valid_from": valid_from,
        "valid_until": valid_until,
        "status_observed_at_archival_capture": status,
        "revision": 1,
        "trust_root_provenance": TRUST_ROOT_PROVENANCE,
        "trust_record_fingerprint": trust_record,
        "snapshot_observed_at": snapshot_observed_at,
        "snapshot_source_identity": snapshot_source_identity,
        "snapshot_source_fingerprint": snapshot_source_fingerprint,
    }
    values["snapshot_fingerprint"] = archival.LegalCorpusArchivalTrustSnapshot.fingerprint_for(**values)
    return archival.LegalCorpusArchivalTrustSnapshot(**values)


def _fixture(
    *,
    issued_at: datetime = NOW,
    not_before: datetime = NOW - timedelta(minutes=1),
    expires_at: datetime = NOW + timedelta(minutes=20),
    trust_valid_from: datetime = NOW - timedelta(hours=1),
    trust_valid_until: datetime | None = NOW + timedelta(hours=1),
    trust_status: LegalCorpusOperatorKeyStatus = LegalCorpusOperatorKeyStatus.ACTIVE,
) -> Fixture:
    """Create one deterministic D1 envelope and matching archival snapshots."""
    private_key = Ed25519PrivateKey.from_private_bytes(PRIVATE_SEED)
    authorization = LegalCorpusOperatorAuthorization(
        authorization_id=AUTHORIZATION_ID,
        key_id=KEY_ID,
        operation=LegalCorpusOperatorAuthorizationOperation.DRAFT_ADMISSION,
        scope=LegalCorpusOperatorAuthorizationScope.PLATFORM,
        source_document_id=DOCUMENT_ID,
        source_agreement_type=LegalAgreementType.INSTITUTIONAL_CHARTER,
        source_version=DOCUMENT_VERSION,
        source_status=LegalDocumentStatus.DRAFT_REVIEW_REQUIRED,
        source_content_reference=CONTENT_REFERENCE,
        source_sha3_512=SOURCE_DIGEST,
        issued_at=issued_at,
        not_before=not_before,
        expires_at=expires_at,
        replay_nonce="synthetic-replay-nonce-c1",
        idempotency_key="synthetic-idempotency-c1",
        authority_mechanism=AUTHORITY_MECHANISM,
        authority_mechanism_version=AUTHORITY_MECHANISM_VERSION,
        signature=_b64(b"\x00" * 64),
    )
    authorization = replace(authorization, signature=_b64(private_key.sign(authorization.canonical_payload_bytes())))
    authorization_snapshot = archival.LegalCorpusArchivalAuthorizationSnapshot(
        schema=AUTHORIZATION_SCHEMA,
        authorization_id=authorization.authorization_id,
        key_id=authorization.key_id,
        operation=authorization.operation,
        scope=authorization.scope,
        source_document_id=authorization.source_document_id,
        source_agreement_type=authorization.source_agreement_type,
        source_version=authorization.source_version,
        source_status=authorization.source_status,
        source_content_reference=authorization.source_content_reference,
        source_sha3_512=authorization.source_sha3_512,
        issued_at=authorization.issued_at,
        not_before=authorization.not_before,
        expires_at=authorization.expires_at,
        replay_nonce=authorization.replay_nonce,
        idempotency_key=authorization.idempotency_key,
        authority_mechanism=authorization.authority_mechanism,
        authority_mechanism_version=authorization.authority_mechanism_version,
        signature=authorization.signature,
        authorization_file_sha3_512=FILE_DIGEST,
    )
    trust_snapshot = _trust_snapshot(
        valid_from=trust_valid_from,
        valid_until=trust_valid_until,
        status=trust_status,
    )
    return Fixture(private_key, authorization, authorization_snapshot, trust_snapshot)


def _verify(fixture: Fixture) -> verifier.LegalCorpusOperatorArchivalVerificationResult:
    """Invoke only the public P3C authenticity API."""
    return verifier.verify_archival_d1_authenticity(fixture.authorization_snapshot, fixture.trust_snapshot)


def test_source_identities_are_frozen_before_certificate_logic() -> None:
    """Require the certified P3A/P3C production artifacts to remain exact."""
    for path, expected_bytes, expected_hash in (
        (P3A_PATH, EXPECTED_P3A_BYTES, EXPECTED_P3A_SHA3_512),
        (P3C_PATH, EXPECTED_P3C_BYTES, EXPECTED_P3C_SHA3_512),
    ):
        data = path.read_bytes()
        assert len(data) == expected_bytes
        assert hashlib.sha3_512(data).hexdigest() == expected_hash


def test_happy_path_proves_p1_and_preserves_identity_and_signed_time() -> None:
    """Real Ed25519 verification proves P1 while preserving signed facts."""
    result = _verify(_fixture())
    assert result.signature_authentic is True
    assert result.authorization_id == AUTHORIZATION_ID
    assert result.key_id == KEY_ID
    assert result.signed_issued_at == NOW
    assert result.authorization_window_contains_issued_at is True
    assert result.trust_validity_interval_contains_issued_at is True


def test_d1_canonical_preimage_is_reused_and_alternative_encodings_fail() -> None:
    """Only D1's sorted compact payload without signature authenticates."""
    fixture = _fixture()
    payload = fixture.authorization.canonical_payload()
    import json

    alternatives = (
        json.dumps(payload).encode("utf-8"),
        json.dumps({**payload, "signature": fixture.authorization.signature}, sort_keys=True, separators=(",", ":")).encode("utf-8"),
        json.dumps({**payload, "issued_at": NOW.isoformat()}, sort_keys=True, separators=(",", ":")).encode("utf-8"),
    )
    for alternative in alternatives:
        tampered = replace(fixture.authorization_snapshot, signature=_b64(fixture.private_key.sign(alternative)))
        with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError) as caught:
            verifier.verify_archival_d1_authenticity(tampered, fixture.trust_snapshot)
        assert caught.value.code == "SIGNATURE_INVALID"
    assert fixture.authorization.canonical_payload_bytes() != alternatives[0]


@pytest.mark.parametrize("mutation", ["source_version", "authorization_id", "idempotency_key"])
def test_signed_field_tampering_rejects(mutation: str) -> None:
    """Changing any signed semantic field invalidates the Ed25519 payload."""
    fixture = _fixture()
    tampered = replace(fixture.authorization_snapshot, **{mutation: "tampered-value"})
    with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError) as caught:
        _verify(replace(fixture, authorization_snapshot=tampered))
    assert caught.value.code == "SIGNATURE_INVALID"


@pytest.mark.parametrize("signature", ["not-base64", "=", _b64(b"short"), _b64(b"x" * 64) + "="])
def test_signature_encoding_and_wrong_signature_fail_closed(signature: str) -> None:
    """Malformed, padded, wrong-length, and wrong-content signatures reject."""
    fixture = _fixture()
    tampered = replace(fixture.authorization_snapshot, signature=signature)
    with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError) as caught:
        _verify(replace(fixture, authorization_snapshot=tampered))
    assert caught.value.code in {"D1_SNAPSHOT_INVALID", "SIGNATURE_ENCODING_INVALID", "SIGNATURE_INVALID"}


def test_signature_from_different_key_fails() -> None:
    """A valid Ed25519 signature from another in-memory key is not accepted."""
    fixture = _fixture()
    other = Ed25519PrivateKey.from_private_bytes(bytes(reversed(range(32))))
    signature = _b64(other.sign(fixture.authorization.canonical_payload_bytes()))
    tampered = replace(fixture.authorization_snapshot, signature=signature)
    with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError) as caught:
        _verify(replace(fixture, authorization_snapshot=tampered))
    assert caught.value.code == "SIGNATURE_INVALID"


@pytest.mark.parametrize(
    ("issued_at", "not_before", "expires_at"),
    [(NOW, NOW, NOW + timedelta(minutes=1)), (NOW, NOW - timedelta(minutes=1), NOW)],
)
def test_authorization_window_lower_and_upper_boundaries_are_inclusive(
    issued_at: datetime, not_before: datetime, expires_at: datetime
) -> None:
    """D1's inclusive issuance interval boundaries remain accepted."""
    result = _verify(_fixture(issued_at=issued_at, not_before=not_before, expires_at=expires_at))
    assert result.authorization_window_contains_issued_at is True


@pytest.mark.parametrize(
    ("not_before", "expires_at"),
    [(NOW + timedelta(microseconds=1), NOW + timedelta(minutes=1)), (NOW - timedelta(minutes=1), NOW - timedelta(microseconds=1))],
)
def test_authorization_window_outside_boundaries_fails(not_before: datetime, expires_at: datetime) -> None:
    """The P3A/D1 structural boundary rejects issuance outside the interval."""
    with pytest.raises((LegalCorpusOperatorAuthorizationError, archival.LegalCorpusArchivalEvidenceError, verifier.LegalCorpusOperatorArchivalVerificationError)):
        _verify(_fixture(not_before=not_before, expires_at=expires_at))


def test_trust_validity_lower_boundary_is_inclusive_and_upper_boundary_exclusive() -> None:
    """The source trust interval accepts valid_from and rejects valid_until."""
    assert _verify(_fixture(trust_valid_from=NOW, trust_valid_until=NOW + timedelta(hours=1))).trust_validity_interval_contains_issued_at is True
    with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError) as caught:
        _verify(_fixture(trust_valid_from=NOW + timedelta(microseconds=1), trust_valid_until=NOW + timedelta(hours=1)))
    assert caught.value.code == "TRUST_WINDOW_MISMATCH_AT_ISSUANCE"


def test_key_identity_mismatch_and_malformed_public_key_fail_closed() -> None:
    """P7 key identity and public-key structural rules are fail-closed."""
    fixture = _fixture()
    mismatched = replace(fixture.authorization_snapshot, key_id="prdca-key:other")
    with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError):
        _verify(replace(fixture, authorization_snapshot=mismatched))
    malformed = object.__new__(type(fixture.trust_snapshot))
    for field in fixture.trust_snapshot.__dataclass_fields__:
        object.__setattr__(malformed, field, getattr(fixture.trust_snapshot, field))
    object.__setattr__(malformed, "public_key", "not-base64")
    with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError):
        _verify(replace(fixture, trust_snapshot=malformed))


@pytest.mark.parametrize("status", [LegalCorpusOperatorKeyStatus.RETIRED, LegalCorpusOperatorKeyStatus.REVOKED])
def test_capture_status_is_observed_only_and_unsafe_status_rejects(status: LegalCorpusOperatorKeyStatus) -> None:
    """P3C does not promote capture-time status into historical activity."""
    with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError) as caught:
        _verify(_fixture(trust_status=status))
    assert caught.value.code == "TRUST_STATUS_NOT_ACTIVE_AT_CAPTURE"
    result = _verify(_fixture())
    document = result.to_document()
    assert document["trust_status_observed_at_capture"] == "ACTIVE"
    assert "active_at_issuance" not in document
    assert "active_at_admission" not in document


def test_snapshot_fingerprints_and_file_hash_limitation_fail_closed() -> None:
    """P3A snapshot integrity and authorization-file hash limits are distinct."""
    fixture = _fixture()
    tampered_snapshot = object.__new__(type(fixture.trust_snapshot))
    for field in fixture.trust_snapshot.__dataclass_fields__:
        object.__setattr__(tampered_snapshot, field, getattr(fixture.trust_snapshot, field))
    object.__setattr__(tampered_snapshot, "snapshot_source_identity", "tampered-source")
    with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError) as caught:
        _verify(replace(fixture, trust_snapshot=tampered_snapshot))
    assert caught.value.code == "TRUST_SNAPSHOT_INVALID"
    malformed_file_hash = object.__new__(type(fixture.authorization_snapshot))
    for field in fixture.authorization_snapshot.__dataclass_fields__:
        object.__setattr__(malformed_file_hash, field, getattr(fixture.authorization_snapshot, field))
    object.__setattr__(malformed_file_hash, "authorization_file_sha3_512", "bad")
    with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError) as caught:
        _verify(replace(fixture, authorization_snapshot=malformed_file_hash))
    assert caught.value.code == "AUTHORIZATION_SNAPSHOT_INVALID"


def test_trust_record_fingerprint_is_source_constructed_and_distinct_from_snapshot() -> None:
    """Trust-record tamper is rejected before any authenticity result exists."""
    fixture = _fixture()
    altered_record = _trust_fingerprint(issuer="WILSY_OS_OTHER_AUTHORITY:V1")
    tampered = object.__new__(type(fixture.trust_snapshot))
    for field in fixture.trust_snapshot.__dataclass_fields__:
        object.__setattr__(tampered, field, getattr(fixture.trust_snapshot, field))
    object.__setattr__(tampered, "trust_record_fingerprint", altered_record)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(archival.LegalCorpusArchivalTrustSnapshot, "from_document", classmethod(lambda cls, payload: tampered))
        with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError) as caught:
            _verify(replace(fixture, trust_snapshot=tampered))
    assert caught.value.code == "TRUST_RECORD_FINGERPRINT_MISMATCH"
    assert tampered.trust_record_fingerprint != tampered.snapshot_fingerprint


def test_no_current_resolver_or_operational_d1_verifier_is_called(monkeypatch: pytest.MonkeyPatch) -> None:
    """P3C uses supplied archival evidence, never live mutation authority."""
    monkeypatch.setattr(trust_domain.LegalCorpusOperatorTrustRoot, "resolve", lambda *_: (_ for _ in ()).throw(AssertionError("live resolver called")))
    monkeypatch.setattr(LegalCorpusOperatorAuthorization, "verify", lambda *_: (_ for _ in ()).throw(AssertionError("operational verifier called")))
    result = _verify(_fixture())
    assert result.signature_authentic is True


def test_api_has_no_admission_time_or_ambiguous_authority_surface() -> None:
    """The public API cannot accept event time or imply mutation authority."""
    parameters = inspect.signature(verifier.verify_archival_d1_authenticity).parameters
    assert set(parameters) == {"authorization_snapshot", "trust_snapshot"}
    result_keys = set(_verify(_fixture()).to_document())
    forbidden = {"transaction_start_at", "admission_event_time", "commit_time", "historical_event_time", "authorization_valid_at_admission_event", "admission_authorized", "mutation_authorized", "is_authorized", "valid_for_mutation", "may_execute", "authorized"}
    assert result_keys.isdisjoint(forbidden)
    assert "d1_to_r8d_identity_binding_established" in result_keys
    assert "can_authorize_new_mutation" in result_keys


def test_result_is_frozen_deterministic_and_alias_safe() -> None:
    """Identical snapshots produce immutable, semantically identical findings."""
    first = _verify(_fixture())
    second = _verify(_fixture())
    assert first.to_document() == second.to_document()
    with pytest.raises(FrozenInstanceError):
        first.authorization_id = "changed"  # type: ignore[misc]
    serialized = first.to_document()
    serialized["authorization_id"] = "changed"
    assert first.authorization_id == AUTHORIZATION_ID


def test_invalid_inputs_use_only_bounded_p3c_errors() -> None:
    """Invalid public inputs never return a silent partial result."""
    fixture = _fixture()
    with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError) as caught:
        verifier.verify_archival_d1_authenticity(object(), fixture.trust_snapshot)  # type: ignore[arg-type]
    assert caught.value.code == "AUTHORIZATION_SNAPSHOT_REQUIRED"
    with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError) as caught:
        verifier.verify_archival_d1_authenticity(fixture.authorization_snapshot, object())  # type: ignore[arg-type]
    assert caught.value.code == "TRUST_SNAPSHOT_REQUIRED"


def test_pure_domain_import_boundary_and_no_r8k_integration() -> None:
    """AST/import evidence confirms no persistence, service, or R8K path."""
    tree = ast.parse(P3C_PATH.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    imported_names = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }
    forbidden_modules = {"pymongo", "tools.eos.kernel.db", "requests", "httpx", "socket", "os", "pathlib"}
    assert imported_modules.isdisjoint(forbidden_modules)
    assert "LegalCorpusOperatorTrustRoot" not in imported_names
    source = P3C_PATH.read_text(encoding="utf-8")
    assert not any((module or "").endswith("legal_corpus_operator_archival_verification") for module in imported_modules)
    assert "datetime.now" not in source


def test_result_boundary_is_explicitly_non_authorizing() -> None:
    """The result preserves the historical limits as concrete false facts."""
    result = _verify(_fixture())
    assert result.historical_admission_event_time_available is False
    assert result.d1_to_r8d_identity_binding_established is False
    assert result.d1_bound_to_r8d is False
    assert result.can_authorize_new_mutation is False
    assert result.to_document()["verification_scope"] == verifier.VERIFICATION_SCOPE


# ARTIFACT: test_legal_corpus_operator_archival_verification.py
# VERSION: v1.0.0-R1D-B0F-B4-R8O-P3C-C1-LEGAL-CORPUS-ARCHIVAL-AUTHENTICITY-VERIFIER-CERT
# AUTHORITY BOUNDARY: direct synthetic certificate evidence only
# TENANT POSTURE: PLATFORM archival evidence; no tenant or principal authority
# FAIL-CLOSED POSTURE: cryptographic, fingerprint, boundary, and import drift fails
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
    with pytest.raises(verifier.LegalCorpusOperatorArchivalVerificationError) as caught:
        _verify(_fixture(trust_valid_from=NOW - timedelta(hours=1), trust_valid_until=NOW))
    assert caught.value.code == "TRUST_WINDOW_MISMATCH_AT_ISSUANCE"
