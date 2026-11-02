"""Adversarial tests for source, signature, recovery and replay validation."""
from __future__ import annotations

import base64
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from tools.eos.auth.tenant_ownership_provider_ports import (
    RecoveryDecisionLookup, RecoveryDecisionReceipt, RegistrySnapshot,
    SigningReceipt, SigningRequest,
)
from tools.eos.auth.tenant_ownership_provider_validation import (
    OwnershipProviderEvidenceError, RegistryFreshnessPolicy, VerificationKey,
    assess_registry_lineage, invoke_provider_fail_closed, validate_recovery_decision,
    verify_provider_signature, recovery_decision_signing_payload,
    signing_request_payload, validate_signing_receipt,
)


NOW = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)
FP = "a" * 64


def snapshot(ref: str, *, supersedes: str | None = None, status: str = "ACTIVE",
             retrieved: datetime = NOW) -> RegistrySnapshot:
    return RegistrySnapshot(
        source_id="cipc", record_reference="entity-1", filing_reference=ref,
        filing_revision=ref, jurisdiction="ZA", entity_type="company",
        record_status=status, retrieved_at=retrieved, effective_at=retrieved,
        source_fingerprint=FP, attributes_fingerprint="b" * 64,
        supersedes_filing_reference=supersedes,
    )


def lookup() -> RecoveryDecisionLookup:
    return RecoveryDecisionLookup("tenant-1", "entity-1", "case-1", FP, "successor-1", NOW)


def receipt() -> RecoveryDecisionReceipt:
    return RecoveryDecisionReceipt(
        authority_id="independent-board", trust_root_reference="root-1",
        trust_root_fingerprint=FP, decision_reference="decision-1",
        decision_fingerprint="c" * 64, recovery_case_reference="case-1",
        recovery_case_fingerprint=FP, successor_principal_id="successor-1",
        quorum_fingerprint="d" * 64, conflict_check_fingerprint="e" * 64,
        notice_and_objection_fingerprint="f" * 64, appeal_status="FINAL",
        issued_at=NOW - timedelta(minutes=1), valid_until=NOW + timedelta(days=1),
        revocation_reference="revocation-check-1",
    )


def test_registry_supersession_selects_only_active_terminal_filing() -> None:
    result = assess_registry_lineage(
        [snapshot("filing-1", status="SUPERSEDED"),
         snapshot("filing-2", supersedes="filing-1")],
        evaluated_at=NOW,
    )
    assert result.current_filing_reference == "filing-2"
    assert result.observed_filing_references == ("filing-1", "filing-2")


@pytest.mark.parametrize("items,code", [
    ([snapshot("old", retrieved=NOW - timedelta(days=3))], "REGISTRY_SNAPSHOT_STALE"),
    ([snapshot("a"), snapshot("b")], "REGISTRY_CURRENT_FILING_AMBIGUOUS"),
    ([snapshot("a", supersedes="missing")], "REGISTRY_SUPERSESSION_LINEAGE_INVALID"),
    ([snapshot("a"), snapshot("b", supersedes="a")], "REGISTRY_SUPERSESSION_STATUS_CONFLICT"),
    ([snapshot("a", supersedes="b", status="SUPERSEDED"), snapshot("b", supersedes="a", status="SUPERSEDED")], "REGISTRY_SUPERSESSION_CYCLE"),
    ([snapshot("a"), replace(snapshot("a"), attributes_fingerprint="9" * 64)],
     "REGISTRY_FILING_FINGERPRINT_CONFLICT"),
    ([snapshot("a", status="WITHDRAWN")], "REGISTRY_CURRENT_RECORD_NOT_ACTIVE"),
])
def test_registry_adversarial_lineage_is_rejected(items, code: str) -> None:
    with pytest.raises(OwnershipProviderEvidenceError) as caught:
        assess_registry_lineage(items, evaluated_at=NOW)
    assert caught.value.code == code


def test_registry_rejects_naive_and_future_source_timestamps() -> None:
    with pytest.raises(OwnershipProviderEvidenceError, match="REGISTRY_RETRIEVED_AT_MUST_BE_TIMEZONE_AWARE"):
        assess_registry_lineage([replace(snapshot("a"), retrieved_at=datetime(2026, 11, 2))], evaluated_at=NOW)
    with pytest.raises(OwnershipProviderEvidenceError) as caught:
        assess_registry_lineage([snapshot("a", retrieved=NOW + timedelta(hours=1))], evaluated_at=NOW)
    assert caught.value.code == "REGISTRY_SNAPSHOT_FROM_FUTURE"


def test_ed25519_signature_verifies_exact_payload_and_key_revision() -> None:
    private = ed25519.Ed25519PrivateKey.generate()
    public_pem = private.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    message = b"tenant=tenant-1;purpose=ownership-evidence;digest=abc"
    signature = base64.b64encode(private.sign(message)).decode("ascii")
    key = VerificationKey("kms-key-1", 3, "ED25519", public_pem,
                          NOW - timedelta(days=1), NOW + timedelta(days=1))
    assert verify_provider_signature(message=message, signature_b64=signature, key=key,
                                      evaluated_at=NOW) == __import__("hashlib").sha256(message).hexdigest()
    with pytest.raises(OwnershipProviderEvidenceError, match="SIGNATURE_INVALID"):
        verify_provider_signature(message=message + b"!", signature_b64=signature, key=key,
                                  evaluated_at=NOW)


def test_key_rotation_and_revocation_are_fail_closed() -> None:
    private = ed25519.Ed25519PrivateKey.generate()
    public_pem = private.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    signature = base64.b64encode(private.sign(b"payload")).decode("ascii")
    base = VerificationKey("key", 2, "ED25519", public_pem,
                           NOW - timedelta(days=1), NOW + timedelta(days=1))
    for key, code in [
        (replace(base, revoked_at=NOW - timedelta(seconds=1)), "SIGNING_KEY_REVOKED"),
        (replace(base, superseded_at=NOW - timedelta(seconds=1)), "SIGNING_KEY_SUPERSEDED"),
        (replace(base, valid_until=NOW), "SIGNING_KEY_NOT_CURRENT"),
    ]:
        with pytest.raises(OwnershipProviderEvidenceError) as caught:
            verify_provider_signature(message=b"payload", signature_b64=signature,
                                      key=key, evaluated_at=NOW)
        assert caught.value.code == code


def test_recovery_decision_requires_exact_case_successor_and_finality() -> None:
    validate_recovery_decision(lookup(), receipt(), evaluated_at=NOW)
    variants = [
        (replace(receipt(), successor_principal_id="attacker"), "RECOVERY_DECISION_SCOPE_MISMATCH"),
        (replace(receipt(), recovery_case_fingerprint="9" * 64), "RECOVERY_DECISION_SCOPE_MISMATCH"),
        (replace(receipt(), appeal_status="PENDING"), "RECOVERY_DECISION_NOT_FINAL"),
        (replace(receipt(), valid_until=NOW), "RECOVERY_DECISION_NOT_CURRENT"),
        (replace(receipt(), revoked_at=NOW - timedelta(seconds=1)), "RECOVERY_DECISION_REVOKED"),
    ]
    for changed, code in variants:
        with pytest.raises(OwnershipProviderEvidenceError) as caught:
            validate_recovery_decision(lookup(), changed, evaluated_at=NOW)
        assert caught.value.code == code


def test_recovery_decision_rejects_naive_timestamps() -> None:
    with pytest.raises(OwnershipProviderEvidenceError) as caught:
        validate_recovery_decision(lookup(), replace(receipt(), issued_at=datetime(2026, 11, 2)),
                                   evaluated_at=NOW)
    assert caught.value.code == "RECOVERY_DECISION_ISSUED_AT_MUST_BE_TIMEZONE_AWARE"


@pytest.mark.parametrize("failure", [
    TimeoutError("provider timeout"),
    ConnectionError("provider unavailable"),
    ValueError("malformed provider response"),
])
def test_external_provider_failures_are_bounded_and_fail_closed(failure: Exception) -> None:
    def unavailable():
        raise failure
    with pytest.raises(OwnershipProviderEvidenceError) as caught:
        invoke_provider_fail_closed("registry", unavailable)
    assert caught.value.code == "REGISTRY_PROVIDER_UNAVAILABLE"
    assert "provider timeout" not in str(caught.value)


def test_external_provider_success_is_returned_without_trust_elevation() -> None:
    assert invoke_provider_fail_closed("registry", lambda: {"status": "untrusted"}) == {
        "status": "untrusted"
    }


def test_recovery_signature_payload_binds_signing_key_revision() -> None:
    payload = recovery_decision_signing_payload(
        lookup(), receipt(), key_reference="hsm-key-7", key_revision=7,
    )
    rotated = recovery_decision_signing_payload(
        lookup(), receipt(), key_reference="hsm-key-7", key_revision=8,
    )
    substituted = recovery_decision_signing_payload(
        lookup(), receipt(), key_reference="other-key", key_revision=7,
    )
    assert payload != rotated
    assert payload != substituted


def test_signing_receipt_is_bound_to_digest_tenant_purpose_and_key_revision() -> None:
    private = ed25519.Ed25519PrivateKey.generate()
    public_pem = private.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    request = SigningRequest(
        payload_digest=FP, digest_algorithm="SHA-256", key_reference="hsm-key",
        key_revision=4, purpose="TENANT_OWNERSHIP_ISSUER", tenant_id="tenant-1",
        evaluated_at=NOW,
    )
    key = VerificationKey(
        "hsm-key", 4, "ED25519", public_pem,
        NOW - timedelta(days=1), NOW + timedelta(days=1),
    )
    signature = base64.b64encode(private.sign(signing_request_payload(request))).decode("ascii")
    receipt = SigningReceipt(
        provider_id="hsm-provider", custody_authority_id="custody-authority",
        key_reference="hsm-key", key_revision=4, algorithm="ED25519",
        signature=signature, payload_digest=FP, purpose=request.purpose,
        signed_at=NOW, audit_reference="audit-1", custody_proof_fingerprint="b" * 64,
    )
    assert validate_signing_receipt(request, receipt, key, evaluated_at=NOW) == FP
    with pytest.raises(OwnershipProviderEvidenceError, match="SIGNING_RECEIPT_REQUEST_BINDING_MISMATCH"):
        validate_signing_receipt(request, replace(receipt, key_revision=5), key, evaluated_at=NOW)
    with pytest.raises(OwnershipProviderEvidenceError, match="SIGNING_RECEIPT_REQUEST_BINDING_MISMATCH"):
        validate_signing_receipt(request, replace(receipt, purpose="OTHER"), key, evaluated_at=NOW)


def test_signing_receipt_rejects_wrong_payload_signature_and_future_time() -> None:
    private = ed25519.Ed25519PrivateKey.generate()
    public_pem = private.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    request = SigningRequest(FP, "SHA256", "hsm-key", 1, "purpose", "tenant-1", NOW)
    key = VerificationKey("hsm-key", 1, "ED25519", public_pem,
                          NOW - timedelta(days=1), NOW + timedelta(days=1))
    signature = base64.b64encode(private.sign(signing_request_payload(request))).decode("ascii")
    receipt = SigningReceipt("provider", "custodian", "hsm-key", 1, "ED25519",
                             signature, FP, "purpose", NOW, "audit", "c" * 64)
    with pytest.raises(OwnershipProviderEvidenceError, match="SIGNATURE_INVALID"):
        validate_signing_receipt(request, replace(receipt, payload_digest="d" * 64), key, evaluated_at=NOW)
    with pytest.raises(OwnershipProviderEvidenceError, match="SIGNING_RECEIPT_TIME_INVALID"):
        validate_signing_receipt(request, replace(receipt, signed_at=NOW + timedelta(seconds=1)),
                                 key, evaluated_at=NOW)
