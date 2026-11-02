"""Adversarial conformance tests for ownership evidence validators."""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from tools.eos.auth.tenant_ownership_evidence_validation import (
    OwnershipEvidenceValidationError, RecoveryDecisionEnvelope,
    RecoveryDecisionReplayRegistry, RegistryAssessment, assess_registry_snapshots,
    recovery_decision_message, signing_message, validate_recovery_decision,
    verify_signing_receipt,
)
from tools.eos.auth.tenant_ownership_provider_ports import (
    RecoveryDecisionLookup, RecoveryDecisionReceipt, RegistrySnapshot,
    SigningReceipt, SigningRequest,
)

NOW = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)


def fp(value: str) -> str:
    return sha256(value.encode()).hexdigest()


def snapshot(ref: str, *, supersedes: str | None = None, effective: datetime = NOW,
             retrieved: datetime = NOW, status: str = "ACTIVE",
             attributes: str = "attributes") -> RegistrySnapshot:
    return RegistrySnapshot(
        source_id="registry", record_reference="entity-1", filing_reference=ref,
        filing_revision=ref, jurisdiction="ZA", entity_type="company",
        record_status=status, retrieved_at=retrieved, effective_at=effective,
        source_fingerprint=fp(ref), attributes_fingerprint=fp(attributes),
        supersedes_filing_reference=supersedes,
    )


def test_registry_selects_latest_unambiguous_superseding_filing() -> None:
    result = assess_registry_snapshots(
        (snapshot("filing-1"), snapshot("filing-2", supersedes="filing-1")),
        evaluated_at=NOW, max_age=timedelta(days=1),
    )
    assert result == RegistryAssessment(
        "VERIFIED_SOURCE_FACT", "filing-2", fp("filing-2"),
        "CURRENT_UNAMBIGUOUS_FILING",
    )


@pytest.mark.parametrize(("rows", "reason"), [
    ((snapshot("old", retrieved=NOW - timedelta(days=3)),), "SOURCE_RECORD_STALE"),
    ((snapshot("future", effective=NOW + timedelta(seconds=1)),), "SOURCE_RECORD_FROM_FUTURE"),
    ((snapshot("a"), snapshot("b")), "CONFLICTING_CURRENT_FILINGS"),
    ((snapshot("a"), snapshot("b", supersedes="missing")), "SUPERSESSION_TARGET_MISSING"),
    ((snapshot("a", supersedes="b"), snapshot("b", supersedes="a")), "FILING_LINEAGE_CYCLE"),
    ((snapshot("a", status="REVOKED"),), "NO_CURRENT_FILING"),
])
def test_registry_adversarial_states_deny(rows: tuple[RegistrySnapshot, ...], reason: str) -> None:
    result = assess_registry_snapshots(rows, evaluated_at=NOW, max_age=timedelta(days=1))
    assert result.status == "DENY"
    assert result.reason == reason


class Keys:
    def __init__(self) -> None:
        self.private = Ed25519PrivateKey.generate()
        self.status = "ACTIVE"

    def key_status(self, key_reference: str, revision: int, at: datetime) -> str:
        return self.status if (key_reference, revision) == ("key-1", 3) else "UNKNOWN"

    def recovery_key_status(self, authority_id: str, trust_root_reference: str,
                            trust_root_fingerprint: str, key_reference: str,
                            revision: int, at: datetime) -> str:
        if (authority_id, trust_root_reference, trust_root_fingerprint) != (
            "independent-recovery", "recovery-root", fp("root")
        ):
            return "UNTRUSTED"
        return self.key_status(key_reference, revision, at)

    def public_key(self, key_reference: str, revision: int):
        if (key_reference, revision) != ("key-1", 3):
            raise KeyError(key_reference)
        return self.private.public_key()


def signing_request() -> SigningRequest:
    return SigningRequest(fp("payload"), "sha256", "key-1", 3, "TENANT_GENESIS",
                          "tenant-1", NOW)


def signed_receipt(request: SigningRequest, keys: Keys) -> SigningReceipt:
    return SigningReceipt(
        provider_id="kms", custody_authority_id="custody", key_reference="key-1",
        key_revision=3, algorithm="Ed25519",
        signature=keys.private.sign(signing_message(request)).hex(),
        payload_digest=request.payload_digest, purpose=request.purpose,
        signed_at=NOW - timedelta(seconds=1), audit_reference="audit-1",
        custody_proof_fingerprint=fp("custody"),
    )


def test_signing_receipt_verifies_exact_digest_scope_and_key_revision() -> None:
    request = signing_request()
    keys = Keys()
    verify_signing_receipt(request, signed_receipt(request, keys), keys)


def test_signing_rejects_payload_substitution_and_wrong_key_revision() -> None:
    request = signing_request()
    keys = Keys()
    receipt = signed_receipt(request, keys)
    with pytest.raises(OwnershipEvidenceValidationError, match="REQUEST_MISMATCH"):
        verify_signing_receipt(replace(request, payload_digest=fp("other")), receipt, keys)
    with pytest.raises(OwnershipEvidenceValidationError, match="NOT_CURRENT_OR_REVOKED"):
        keys.status = "REVOKED"
        verify_signing_receipt(request, receipt, keys)


def test_signing_rejects_tampered_signature() -> None:
    request = signing_request()
    keys = Keys()
    receipt = replace(signed_receipt(request, keys), signature="00" * 64)
    with pytest.raises(OwnershipEvidenceValidationError, match="SIGNATURE_INVALID"):
        verify_signing_receipt(request, receipt, keys)


def recovery_fixture(keys: Keys):
    lookup = RecoveryDecisionLookup(
        "tenant-1", "entity-1", "case-1", fp("case"), "successor-1", NOW,
    )
    receipt = RecoveryDecisionReceipt(
        authority_id="independent-recovery", trust_root_reference="recovery-root",
        trust_root_fingerprint=fp("root"), decision_reference="decision-1",
        decision_fingerprint=fp("decision"), recovery_case_reference="case-1",
        recovery_case_fingerprint=fp("case"), successor_principal_id="successor-1",
        quorum_fingerprint=fp("quorum"), conflict_check_fingerprint=fp("conflicts"),
        notice_and_objection_fingerprint=fp("notice"), appeal_status="RESOLVED",
        issued_at=NOW - timedelta(minutes=2), valid_until=NOW + timedelta(hours=1),
        revocation_reference="revocation-1",
    )
    message = recovery_decision_message(lookup, receipt, "key-1", 3, "nonce-1")
    envelope = RecoveryDecisionEnvelope(
        receipt, "key-1", 3, "Ed25519", keys.private.sign(message).hex(), "nonce-1",
    )
    return lookup, envelope


def test_independent_recovery_decision_signature_and_exact_successor_binding() -> None:
    keys = Keys()
    lookup, envelope = recovery_fixture(keys)
    validate_recovery_decision(lookup, envelope, keys)
    altered = replace(lookup, successor_principal_id="attacker")
    with pytest.raises(OwnershipEvidenceValidationError, match="SCOPE_MISMATCH"):
        validate_recovery_decision(altered, envelope, keys)


def test_recovery_rejects_untrusted_authority_root() -> None:
    keys = Keys()
    lookup, envelope = recovery_fixture(keys)
    altered = replace(envelope.receipt, trust_root_fingerprint=fp("attacker-root"))
    with pytest.raises(OwnershipEvidenceValidationError, match="KEY_NOT_CURRENT"):
        validate_recovery_decision(lookup, replace(envelope, receipt=altered), keys)


def test_recovery_signature_binds_expiry_and_revocation_reference() -> None:
    keys = Keys()
    lookup, envelope = recovery_fixture(keys)
    altered = replace(envelope.receipt, valid_until=NOW + timedelta(days=30))
    with pytest.raises(OwnershipEvidenceValidationError, match="SIGNATURE_INVALID"):
        validate_recovery_decision(lookup, replace(envelope, receipt=altered), keys)
    altered = replace(envelope.receipt, revocation_reference="substituted-revocation")
    with pytest.raises(OwnershipEvidenceValidationError, match="SIGNATURE_INVALID"):
        validate_recovery_decision(lookup, replace(envelope, receipt=altered), keys)


def test_key_status_provider_timeout_fails_closed() -> None:
    class Unavailable(Keys):
        def key_status(self, key_reference: str, revision: int, at: datetime) -> str:
            raise TimeoutError("provider timeout")

    request = signing_request()
    keys = Unavailable()
    with pytest.raises(OwnershipEvidenceValidationError, match="KEY_STATUS_UNAVAILABLE"):
        verify_signing_receipt(request, signed_receipt(request, keys), keys)


def test_recovery_denies_pending_appeal_expiry_and_revoked_key() -> None:
    keys = Keys()
    lookup, envelope = recovery_fixture(keys)
    with pytest.raises(OwnershipEvidenceValidationError, match="APPEAL_NOT_RESOLVED"):
        pending = replace(envelope.receipt, appeal_status="PENDING")
        bad = replace(envelope, receipt=pending)
        validate_recovery_decision(lookup, bad, keys)
    with pytest.raises(OwnershipEvidenceValidationError, match="NOT_CURRENT"):
        expired = replace(envelope.receipt, valid_until=NOW)
        bad = replace(envelope, receipt=expired)
        validate_recovery_decision(lookup, bad, keys)
    keys.status = "REVOKED"
    with pytest.raises(OwnershipEvidenceValidationError, match="KEY_NOT_CURRENT"):
        validate_recovery_decision(lookup, envelope, keys)


class Session:
    def in_transaction(self) -> bool:
        return True


class Rows:
    def __init__(self):
        self.docs = []
        self.indexes = []

    def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))

    def insert_one(self, doc, *, session):
        assert session.in_transaction()
        if any(row["decision_reference"] == doc["decision_reference"]
               and row["tenant_id"] == doc["tenant_id"] for row in self.docs):
            from pymongo.errors import DuplicateKeyError
            raise DuplicateKeyError("duplicate")
        self.docs.append(dict(doc))


class Database:
    def __init__(self):
        self.rows = Rows()

    def __getitem__(self, name):
        return self.rows


def test_recovery_replay_ledger_requires_transaction_and_rejects_replay() -> None:
    lookup = RecoveryDecisionLookup("tenant-1", "entity-1", "case-1",
                                    fp("case"), "successor-1", NOW)
    _, envelope = recovery_fixture(Keys())
    db = Database()
    registry = RecoveryDecisionReplayRegistry(db)
    with pytest.raises(OwnershipEvidenceValidationError, match="ACTIVE_TRANSACTION_REQUIRED"):
        registry.consume(lookup, envelope.receipt, session=None)
    registry.consume(lookup, envelope.receipt, session=Session())
    with pytest.raises(OwnershipEvidenceValidationError, match="RECOVERY_DECISION_REPLAY"):
        registry.consume(lookup, envelope.receipt, session=Session())
    assert len(db.rows.docs) == 1
    assert len(db.rows.indexes) == 2
