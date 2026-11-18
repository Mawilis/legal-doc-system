"""TITLE: Tenant Ownership Evidence Validation Certificate.
VERSION: v1.0.1-P8-OWNERSHIP-EVIDENCE-VALIDATION-CERT
AUTHORITY: Deterministic source-evidence validation and replay-ledger tests.
EPITOME: Certifies registry-currentness, subject proofing, cryptographic
         signing, independent recovery decisions, and transaction-bound replay
         consumption without issuing tenant ownership or recovery authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_ownership_evidence_validation.py
COLLABORATION / OWNERSHIP: Exercises canonical ownership evidence validation
                           and provider-port contracts.
CERTIFICATION / UPDATE DATE: 2026-11-11
CHANGELOG: v1.0.1-P8-OWNERSHIP-EVIDENCE-VALIDATION-CERT creates the replay
           validation window from the operation's current evaluation instant,
           avoiding collection-time expiry during the full Python suite.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Ephemeral Ed25519 keys and synthetic opaque evidence.
TENANT BOUNDARY: Replay keys and decisions remain exact-tenant scoped.
AUTHORITY BOUNDARY: Validators and replay ledger grant no ownership or recovery action.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
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
    verify_signing_receipt, validate_subject_proofing_receipt,
)
from tools.eos.auth.tenant_ownership_provider_ports import (
    RecoveryDecisionLookup, RecoveryDecisionReceipt, RegistrySnapshot,
    SigningReceipt, SigningRequest, SubjectProofingReceipt, SubjectProofingRequest,
)

NOW = datetime.now(timezone.utc)


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


def test_stale_superseded_filing_does_not_override_fresh_current_filing() -> None:
    result = assess_registry_snapshots(
        (snapshot("historic", retrieved=NOW - timedelta(days=30)),
         snapshot("current", supersedes="historic", retrieved=NOW)),
        evaluated_at=NOW, max_age=timedelta(days=1),
    )
    assert result.status == "VERIFIED_SOURCE_FACT"
    assert result.selected_filing_reference == "current"


@pytest.mark.parametrize(("rows", "reason"), [
    ((snapshot("old", retrieved=NOW - timedelta(days=3)),), "SOURCE_RECORD_STALE"),
    ((snapshot("future", effective=NOW + timedelta(seconds=1)),), "SOURCE_RECORD_FROM_FUTURE"),
    ((snapshot("a"), snapshot("b")), "CONFLICTING_CURRENT_FILINGS"),
    ((snapshot("a"), snapshot("b", supersedes="missing")), "SUPERSESSION_TARGET_MISSING"),
    ((snapshot("a", supersedes="b"), snapshot("b", supersedes="a")), "FILING_LINEAGE_CYCLE"),
    ((snapshot("a", status="REVOKED"),), "SOURCE_RECORD_NOT_ACTIVE"),
])
def test_registry_adversarial_states_deny(rows: tuple[RegistrySnapshot, ...], reason: str) -> None:
    result = assess_registry_snapshots(rows, evaluated_at=NOW, max_age=timedelta(days=1))
    assert result.status == "DENY"
    assert result.reason == reason


class SubjectRevocation:
    def __init__(self, revoked: bool = False, unavailable: bool = False):
        self.revoked = revoked
        self.unavailable = unavailable

    def is_revoked(self, revocation_reference: str, at: datetime) -> bool:
        if self.unavailable:
            raise TimeoutError("revocation provider unavailable")
        return self.revoked


def test_subject_proofing_receipt_is_exact_current_and_revocation_checked() -> None:
    request = SubjectProofingRequest("subject-1", "TENANT_OWNERSHIP", NOW)
    receipt = SubjectProofingReceipt(
        "identity-provider", "independent-verifier", "IAL2",
        "subject-1", "evidence-1", fp("subject-evidence"),
        NOW - timedelta(minutes=1), NOW + timedelta(hours=1), "revocation-1",
    )
    validate_subject_proofing_receipt(request, receipt, SubjectRevocation())
    with pytest.raises(OwnershipEvidenceValidationError, match="SUBJECT_MISMATCH"):
        validate_subject_proofing_receipt(
            request, replace(receipt, subject_reference="attacker"), SubjectRevocation()
        )
    with pytest.raises(OwnershipEvidenceValidationError, match="REVOKED"):
        validate_subject_proofing_receipt(request, receipt, SubjectRevocation(revoked=True))
    with pytest.raises(OwnershipEvidenceValidationError, match="REVOCATION_UNAVAILABLE"):
        validate_subject_proofing_receipt(request, receipt, SubjectRevocation(unavailable=True))


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


def test_signing_rejects_old_key_revision_after_rotation() -> None:
    request = signing_request()
    keys = Keys()
    receipt = signed_receipt(request, keys)
    rotated = replace(request, key_revision=4)
    with pytest.raises(OwnershipEvidenceValidationError, match="REQUEST_MISMATCH"):
        verify_signing_receipt(rotated, receipt, keys)


def test_signing_rejects_tampered_signature() -> None:
    request = signing_request()
    keys = Keys()
    receipt = replace(signed_receipt(request, keys), signature="00" * 64)
    with pytest.raises(OwnershipEvidenceValidationError, match="SIGNATURE_INVALID"):
        verify_signing_receipt(request, receipt, keys)


def recovery_fixture(keys: Keys):
    evaluated_at = datetime.now(timezone.utc)
    lookup = RecoveryDecisionLookup(
        "tenant-1", "entity-1", "case-1", fp("case"), "successor-1", evaluated_at,
    )
    receipt = RecoveryDecisionReceipt(
        authority_id="independent-recovery", trust_root_reference="recovery-root",
        trust_root_fingerprint=fp("root"), decision_reference="decision-1",
        decision_fingerprint=fp("decision"), recovery_case_reference="case-1",
        recovery_case_fingerprint=fp("case"), successor_principal_id="successor-1",
        quorum_fingerprint=fp("quorum"), conflict_check_fingerprint=fp("conflicts"),
        notice_and_objection_fingerprint=fp("notice"), appeal_status="RESOLVED",
        issued_at=evaluated_at - timedelta(minutes=2),
        valid_until=evaluated_at + timedelta(hours=1),
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
    with pytest.raises(OwnershipEvidenceValidationError, match="SIGNING_KEY_STATUS_UNAVAILABLE"):
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
        if any(row["tenant_id"] == doc["tenant_id"] and (
               row["decision_reference"] == doc["decision_reference"] or
               row["recovery_case_reference"] == doc["recovery_case_reference"]
               ) for row in self.docs):
            from pymongo.errors import DuplicateKeyError
            raise DuplicateKeyError("duplicate")
        self.docs.append(dict(doc))


class Database:
    def __init__(self):
        self.rows = Rows()

    def __getitem__(self, name):
        return self.rows


def test_recovery_replay_ledger_requires_validated_receipt_and_transaction() -> None:
    keys = Keys()
    lookup, envelope = recovery_fixture(keys)
    validated = validate_recovery_decision(lookup, envelope, keys)
    db = Database()
    registry = RecoveryDecisionReplayRegistry(db)
    with pytest.raises(OwnershipEvidenceValidationError, match="VALIDATED_RECOVERY_DECISION_REQUIRED"):
        registry.consume_validated(envelope.receipt, session=Session())  # type: ignore[arg-type]
    with pytest.raises(OwnershipEvidenceValidationError, match="ACTIVE_TRANSACTION_REQUIRED"):
        registry.consume_validated(validated, session=None)
    registry.consume_validated(validated, session=Session())
    with pytest.raises(OwnershipEvidenceValidationError, match="RECOVERY_DECISION_REPLAY"):
        registry.consume_validated(validated, session=Session())
    assert len(db.rows.docs) == 1
    assert len(db.rows.indexes) == 2


def test_recovery_validation_receipt_expires_before_transaction_write() -> None:
    keys = Keys()
    lookup, envelope = recovery_fixture(keys)
    validated = validate_recovery_decision(lookup, envelope, keys)
    object.__setattr__(validated, "validation_expires_at", NOW - timedelta(seconds=1))
    registry = RecoveryDecisionReplayRegistry(Database())
    with pytest.raises(OwnershipEvidenceValidationError, match="VALIDATION_WINDOW_EXPIRED"):
        registry.consume_validated(validated, session=Session())


def test_verified_recovery_composition_denies_provider_outage_before_persisting() -> None:
    class Unavailable(Keys):
        def recovery_key_status(self, authority_id: str, trust_root_reference: str,
                                trust_root_fingerprint: str, key_reference: str,
                                revision: int, at: datetime) -> str:
            raise TimeoutError("trust-list unavailable")

    keys = Keys()
    lookup, envelope = recovery_fixture(keys)
    db = Database()
    registry = RecoveryDecisionReplayRegistry(db)
    with pytest.raises(OwnershipEvidenceValidationError, match="RECOVERY_KEY_STATUS_UNAVAILABLE"):
        validate_recovery_decision(lookup, envelope, Unavailable())
    assert db.rows.docs == []
    validated = validate_recovery_decision(lookup, envelope, keys)
    registry.consume_validated(validated, session=Session())
    assert len(db.rows.docs) == 1



def test_registry_rejects_duplicate_filing_identifiers() -> None:
    row = snapshot("duplicate")
    with pytest.raises(OwnershipEvidenceValidationError, match="DUPLICATE_FILING_REFERENCE"):
        assess_registry_snapshots((row, row), evaluated_at=NOW, max_age=timedelta(days=1))


def test_registry_rejects_cross_entity_supersession() -> None:
    original = snapshot("original")
    successor = replace(snapshot("successor", supersedes="original"), record_reference="other-entity")
    result = assess_registry_snapshots((original, successor), evaluated_at=NOW, max_age=timedelta(days=1))
    assert result.status == "DENY"
    assert result.reason == "SUPERSESSION_SCOPE_MISMATCH"


def test_signing_rejects_algorithm_downgrade() -> None:
    request = signing_request()
    keys = Keys()
    receipt = replace(signed_receipt(request, keys), algorithm="RSA-PSS")
    with pytest.raises(OwnershipEvidenceValidationError, match="SIGNING_ALGORITHM_UNSUPPORTED"):
        verify_signing_receipt(request, receipt, keys)


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: test_tenant_ownership_evidence_validation.py
# VERSION: v1.0.1-P8-OWNERSHIP-EVIDENCE-VALIDATION-CERT
# AUTHORITY BOUNDARY: evidence validation and replay persistence tests only
# TENANT POSTURE: exact tenant-bound evidence and replay scopes
# FAIL-CLOSED POSTURE: stale, invalid, replayed, or provider-unavailable evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
