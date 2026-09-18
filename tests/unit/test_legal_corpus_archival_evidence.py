"""Direct certificate for the truth-preserving archival evidence domain.

TITLE: WILSY OS Legal Corpus Archival Evidence Direct Certificate
VERSION: v1.1.0-R1D-B0F-B4-R8O-P3A-R1-C1-LEGAL-CORPUS-ARCHIVAL-EVIDENCE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies the complete immutable P1-P9 archival evidence contract,
         deterministic fingerprints, historical limitations, and pure-domain
         boundary without performing production capture.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_archival_evidence.py
COLLABORATION / OWNERSHIP: Direct certificate for the P3A domain artifact;
                            the P3C authenticity verifier and later capture
                            gate remain separate owners.
CERTIFICATION / UPDATE DATE: 2026-09-18
CHANGELOG: v1.1.0-R1D-B0F-B4-R8O-P3A-R1-C1 recertifies the repaired
           multiline document-content contract, exact round trips, canonical
           digest reuse, package determinism, and prior authority boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Deterministic synthetic public fixtures only;
                            no production authorization, secrets, signer,
                            network, filesystem, or database access.
TENANT BOUNDARY: PLATFORM archival evidence only; no tenant/principal state.
AUTHORITY BOUNDARY: Certificate evidence only; P3A representation cannot
                    authorize, admit, issue, sign, approve, or mutate.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Schema, enum, timestamp, digest, fingerprint, ledger,
                     and authority-boundary drift fails the certificate.
"""
from __future__ import annotations

import ast
import base64
import hashlib
import json
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, cast

import pytest

from tools.eos.legal_operations.domain import legal_corpus_archival_evidence as archival
from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    canonical_document_digest,
)
from tools.eos.legal_operations.domain.legal_corpus_operator_authorization import (
    SCHEMA as AUTHORIZATION_SCHEMA,
    LegalCorpusOperatorAuthorizationOperation,
    LegalCorpusOperatorAuthorizationScope,
)
from tools.eos.legal_operations.domain.legal_corpus_operator_trust_root import (
    AUTHORITY_DOMAIN,
    ED25519_ALGORITHM,
    LegalCorpusOperatorKeyStatus,
    LegalCorpusOperatorTrustedKey,
    TRUST_ROOT_PROVENANCE,
    TRUST_ROOT_SCOPE,
)
from tools.eos.legal_operations.domain.legal_corpus_provisioning_authority import (
    AUTHORITY_SOURCE_VERSION,
    LegalCorpusProvisioningAuthorityEvidence,
    LegalCorpusProvisioningAuthorityScope,
    LegalCorpusProvisioningAuthoritySource,
    LegalCorpusProvisioningOperation,
)


PRODUCTION_PATH = Path(
    "tools/eos/legal_operations/domain/legal_corpus_archival_evidence.py"
)
EXPECTED_SOURCE_BYTES = 50659
EXPECTED_SOURCE_SHA3_512 = (
    "899af341f899c16c68b1e92e9d7ee6ce2528e492c9de3244aa52ccb23cb481132b8b0b90f4372a36f8ff1964386042cd6ab7d2f4343eb70a4e70d3c9a6d7ca32"
)
NOW = datetime(2026, 9, 18, 12, 0, tzinfo=timezone.utc)
VALID_FROM = datetime(2026, 9, 18, 11, 0, tzinfo=timezone.utc)
VALID_UNTIL = datetime(2026, 9, 19, 11, 0, tzinfo=timezone.utc)
PACKAGE_ID = "123e4567-e89b-42d3-a456-426614174000"
KEY_ID = "prdca-key:synthetic-archival-c1"
PUBLIC_KEY = base64.urlsafe_b64encode(bytes(range(32))).decode("ascii").rstrip("=")
ISSUER = "WILSY_OS_SYNTHETIC_RELEASE_AUTHORITY:V1"
SOURCE_IDENTITY = (
    "repo=/synthetic/repository|path=trust-root.py|version=v1|bytes=32"
)
SOURCE_FINGERPRINT = "ab" * 64
AUTHORIZATION_ID = "synthetic-authorization-c1"
DOCUMENT_ID = "WILSY-OS-SYNTHETIC-CHARTER"
DOCUMENT_VERSION = "1.0.0-DRAFT"
CONTENT_REFERENCE = "wilsy-os://synthetic/legal-corpus/1.0.0-draft"
CONTENT = "Synthetic public Charter content for the direct archival certificate."


def _trust_record_fingerprint(
    *, status: LegalCorpusOperatorKeyStatus = LegalCorpusOperatorKeyStatus.ACTIVE
) -> str:
    return LegalCorpusOperatorTrustedKey.fingerprint_for(
        key_id=KEY_ID,
        algorithm=ED25519_ALGORITHM,
        public_key_base64url=PUBLIC_KEY,
        issuer_identity=ISSUER,
        authority_domain=AUTHORITY_DOMAIN,
        scope=TRUST_ROOT_SCOPE,
        permitted_operations=frozenset({"LEGAL_CORPUS_DRAFT_ADMISSION"}),
        valid_from=VALID_FROM,
        valid_until=VALID_UNTIL,
        status=status,
        revision=1,
        trust_root_provenance=TRUST_ROOT_PROVENANCE,
    )


def _trust_snapshot(**changes: Any) -> archival.LegalCorpusArchivalTrustSnapshot:
    values: dict[str, Any] = {
        "key_id": KEY_ID,
        "algorithm": ED25519_ALGORITHM,
        "issuer": ISSUER,
        "authority_domain": AUTHORITY_DOMAIN,
        "scope": TRUST_ROOT_SCOPE,
        "operation": "LEGAL_CORPUS_DRAFT_ADMISSION",
        "permitted_operations": ("LEGAL_CORPUS_DRAFT_ADMISSION",),
        "public_key": PUBLIC_KEY,
        "valid_from": VALID_FROM,
        "valid_until": VALID_UNTIL,
        "status_observed_at_archival_capture": LegalCorpusOperatorKeyStatus.ACTIVE,
        "revision": 1,
        "trust_root_provenance": TRUST_ROOT_PROVENANCE,
        "trust_record_fingerprint": _trust_record_fingerprint(),
        "snapshot_observed_at": NOW,
        "snapshot_source_identity": SOURCE_IDENTITY,
        "snapshot_source_fingerprint": SOURCE_FINGERPRINT,
    }
    values.update(changes)
    values["snapshot_fingerprint"] = archival.LegalCorpusArchivalTrustSnapshot.fingerprint_for(
        **values
    )
    return archival.LegalCorpusArchivalTrustSnapshot(**values)


def _authorization_snapshot(**changes: Any) -> archival.LegalCorpusArchivalAuthorizationSnapshot:
    values: dict[str, Any] = {
        "schema": AUTHORIZATION_SCHEMA,
        "authorization_id": AUTHORIZATION_ID,
        "key_id": KEY_ID,
        "operation": LegalCorpusOperatorAuthorizationOperation.DRAFT_ADMISSION,
        "scope": LegalCorpusOperatorAuthorizationScope.PLATFORM,
        "source_document_id": DOCUMENT_ID,
        "source_agreement_type": LegalAgreementType.INSTITUTIONAL_CHARTER,
        "source_version": DOCUMENT_VERSION,
        "source_status": LegalDocumentStatus.DRAFT_REVIEW_REQUIRED,
        "source_content_reference": CONTENT_REFERENCE,
        "source_sha3_512": "11" * 64,
        "issued_at": NOW,
        "not_before": NOW - timedelta(minutes=1),
        "expires_at": NOW + timedelta(hours=24),
        "replay_nonce": "synthetic-replay-nonce-c1",
        "idempotency_key": "synthetic-idempotency-c1",
        "authority_mechanism": "HUMAN_GOVERNED_LOCAL_RELEASE_SIGNER",
        "authority_mechanism_version": "V1",
        "signature": "synthetic-public-signature",
        "authorization_file_sha3_512": "22" * 64,
    }
    values.update(changes)
    return archival.LegalCorpusArchivalAuthorizationSnapshot(**values)


def _document_snapshot(**changes: Any) -> archival.LegalCorpusArchivalDocumentSnapshot:
    values: dict[str, Any] = {
        "document_id": DOCUMENT_ID,
        "agreement_type": LegalAgreementType.INSTITUTIONAL_CHARTER,
        "version": DOCUMENT_VERSION,
        "title": "Synthetic Institutional Charter",
        "jurisdiction": "ZA",
        "locale": "en-ZA",
        "effective_from": NOW,
        "status": LegalDocumentStatus.DRAFT_REVIEW_REQUIRED,
        "content_reference": CONTENT_REFERENCE,
        "content": CONTENT,
        "sha3_512": canonical_document_digest(CONTENT, CONTENT_REFERENCE),
        "created_at": NOW,
        "supersedes_document_id": None,
    }
    values.update(changes)
    values["sha3_512"] = canonical_document_digest(
        values["content"], values["content_reference"]
    )
    return archival.LegalCorpusArchivalDocumentSnapshot(**values)


def _r8d_snapshot(**changes: Any) -> archival.LegalCorpusArchivalR8DSnapshot:
    values: dict[str, Any] = {
        "authority_evidence_id": "synthetic-r8d-evidence-c1",
        "scope": LegalCorpusProvisioningAuthorityScope.PLATFORM,
        "operation": LegalCorpusProvisioningOperation.DRAFT_ADMISSION,
        "source_document_id": DOCUMENT_ID,
        "source_agreement_type": LegalAgreementType.INSTITUTIONAL_CHARTER,
        "source_version": DOCUMENT_VERSION,
        "source_status": LegalDocumentStatus.DRAFT_REVIEW_REQUIRED,
        "source_content_reference": CONTENT_REFERENCE,
        "source_sha3_512": canonical_document_digest(CONTENT, CONTENT_REFERENCE),
        "authority_source_id": LegalCorpusProvisioningAuthoritySource.DEPLOYMENT_OPERATOR,
        "authority_source_version": AUTHORITY_SOURCE_VERSION,
        "actor_representation": "synthetic-capture-operator",
        "authorized_at": NOW,
        "authorized_at_semantics": archival.R8D_AUTHORIZED_AT_SEMANTICS,
        "idempotency_key": "synthetic-r8d-idempotency-c1",
    }
    values.update(changes)
    values["authority_evidence_fingerprint"] = LegalCorpusProvisioningAuthorityEvidence.fingerprint_for(
        authority_evidence_id=values["authority_evidence_id"],
        scope=values["scope"],
        operation=values["operation"],
        source_document_id=values["source_document_id"],
        source_agreement_type=values["source_agreement_type"],
        source_version=values["source_version"],
        source_status=values["source_status"],
        source_content_reference=values["source_content_reference"],
        source_sha3_512=values["source_sha3_512"],
        authority_source_id=values["authority_source_id"],
        authority_source_version=values["authority_source_version"],
        actor_representation=values["actor_representation"],
        authorized_at=values["authorized_at"],
        idempotency_key=values["idempotency_key"],
    )
    return archival.LegalCorpusArchivalR8DSnapshot(**values)


def _entry(
    proposition: archival.LegalCorpusArchivalProposition,
    classification: archival.LegalCorpusArchivalClassification,
) -> archival.LegalCorpusArchivalPropositionEntry:
    proven = classification is archival.LegalCorpusArchivalClassification.PROVEN
    return archival.LegalCorpusArchivalPropositionEntry(
        proposition=proposition,
        classification=classification,
        evidence_source="synthetic-direct-certificate",
        evidence_identity=f"synthetic:{proposition.value}",
        limitation_reason="synthetic historical limitation" if not proven else "",
    )


def _ledger() -> tuple[archival.LegalCorpusArchivalPropositionEntry, ...]:
    proven = {
        archival.LegalCorpusArchivalProposition.P1_D1_SIGNATURE_AUTHENTIC,
        archival.LegalCorpusArchivalProposition.P2_D1_VALID_AT_SIGNED_ISSUANCE_TIME,
        archival.LegalCorpusArchivalProposition.P5_R8D_EXACT_AND_INTEGRITY_VALID,
        archival.LegalCorpusArchivalProposition.P6_DOCUMENT_EXACT_AND_CANONICAL,
        archival.LegalCorpusArchivalProposition.P7_PUBLIC_KEY_MATCHES_D1_KEY_ID,
        archival.LegalCorpusArchivalProposition.P8_TRUST_STATUS_OBSERVED_AT_ARCHIVAL_CAPTURE,
    }
    return tuple(
        _entry(
            proposition,
            archival.LegalCorpusArchivalClassification.PROVEN
            if proposition in proven
            else archival.LegalCorpusArchivalClassification.UNPROVEN,
        )
        for proposition in archival.LegalCorpusArchivalProposition
    )


def _package(**changes: Any) -> archival.LegalCorpusArchivalEvidencePackage:
    values: dict[str, Any] = {
        "package_id": PACKAGE_ID,
        "propositions": _ledger(),
        "historical_event_time_source": archival.HISTORICAL_EVENT_TIME_SOURCE,
        "historical_event_time_recovery": archival.HISTORICAL_EVENT_TIME_RECOVERY,
        "d1_to_r8d_identity_binding_source": archival.D1_BINDING_SOURCE,
        "d1_to_r8d_binding_recovery": archival.D1_BINDING_RECOVERY,
        "d1_r8d_relationship_classification": archival.D1_R8D_RELATIONSHIP,
        "trust_snapshot": _trust_snapshot(),
        "authorization_snapshot": _authorization_snapshot(),
        "r8d_snapshot": _r8d_snapshot(),
        "document_snapshot": _document_snapshot(),
    }
    values.update(changes)
    values["package_fingerprint"] = archival.LegalCorpusArchivalEvidencePackage.fingerprint_for(
        **values
    )
    return archival.LegalCorpusArchivalEvidencePackage(**values)


def _raises(code: str, callback: Any) -> None:
    with pytest.raises(archival.LegalCorpusArchivalEvidenceError, match=code) as caught:
        callback()
    assert caught.value.code == code


def test_source_identity_is_the_frozen_p3a_artifact() -> None:
    payload = PRODUCTION_PATH.read_bytes()
    assert len(payload) == EXPECTED_SOURCE_BYTES
    assert hashlib.sha3_512(payload).hexdigest() == EXPECTED_SOURCE_SHA3_512
    assert archival.VERSION == "v1.0.1-R1D-B0F-B4-R8O-P3A-R1-LEGAL-CORPUS-ARCHIVAL-EVIDENCE"


def test_proposition_enum_and_classification_contract_are_complete() -> None:
    assert len(archival.LegalCorpusArchivalProposition) == 9
    assert len({item.value for item in archival.LegalCorpusArchivalProposition}) == 9
    assert list(archival.LegalCorpusArchivalClassification) == [
        archival.LegalCorpusArchivalClassification.PROVEN,
        archival.LegalCorpusArchivalClassification.UNPROVEN,
        archival.LegalCorpusArchivalClassification.NOT_APPLICABLE,
    ]
    assert archival.LegalCorpusArchivalClassification.UNPROVEN is not False
    assert archival.LegalCorpusArchivalClassification.PROVEN is not True
    entry = _entry(
        archival.LegalCorpusArchivalProposition.P1_D1_SIGNATURE_AUTHENTIC,
        archival.LegalCorpusArchivalClassification.UNPROVEN,
    )
    assert archival.LegalCorpusArchivalPropositionEntry.from_document(entry.to_document()) == entry
    _raises(
        "PROPOSITION_ID_INVALID",
        lambda: archival.LegalCorpusArchivalPropositionEntry(
            proposition="UNKNOWN",  # type: ignore[arg-type]
            classification=archival.LegalCorpusArchivalClassification.PROVEN,
            evidence_source="source",
            evidence_identity="identity",
            limitation_reason="",
        ),
    )
    _raises(
        "PROPOSITION_CLASSIFICATION_INVALID",
        lambda: archival.LegalCorpusArchivalPropositionEntry(
            proposition=archival.LegalCorpusArchivalProposition.P1_D1_SIGNATURE_AUTHENTIC,
            classification="UNKNOWN",  # type: ignore[arg-type]
            evidence_source="source",
            evidence_identity="identity",
            limitation_reason="",
        ),
    )


def test_proposition_entry_evidence_and_limitation_rules_fail_closed() -> None:
    proposition = archival.LegalCorpusArchivalProposition.P1_D1_SIGNATURE_AUTHENTIC
    _raises(
        "PROPOSITION_EVIDENCE_SOURCE_INVALID",
        lambda: _entry(proposition, archival.LegalCorpusArchivalClassification.PROVEN).__class__(
            proposition=proposition,
            classification=archival.LegalCorpusArchivalClassification.PROVEN,
            evidence_source="",
            evidence_identity="identity",
            limitation_reason="",
        ),
    )
    _raises(
        "PROPOSITION_EVIDENCE_IDENTITY_INVALID",
        lambda: archival.LegalCorpusArchivalPropositionEntry(
            proposition=proposition,
            classification=archival.LegalCorpusArchivalClassification.PROVEN,
            evidence_source="source",
            evidence_identity="",
            limitation_reason="",
        ),
    )
    _raises(
        "UNPROVEN_PROPOSITION_LIMITATION_REQUIRED",
        lambda: archival.LegalCorpusArchivalPropositionEntry(
            proposition=proposition,
            classification=archival.LegalCorpusArchivalClassification.UNPROVEN,
            evidence_source="source",
            evidence_identity="identity",
            limitation_reason="",
        ),
    )
    _raises(
        "NOT_APPLICABLE_PROPOSITION_REASON_REQUIRED",
        lambda: archival.LegalCorpusArchivalPropositionEntry(
            proposition=proposition,
            classification=archival.LegalCorpusArchivalClassification.NOT_APPLICABLE,
            evidence_source="source",
            evidence_identity="identity",
            limitation_reason="",
        ),
    )


def test_complete_ledger_is_exactly_p1_through_p9_and_canonicalized() -> None:
    package = _package()
    propositions = [item.proposition for item in package.propositions]
    assert set(propositions) == set(archival.LegalCorpusArchivalProposition)
    assert len(propositions) == len(set(propositions)) == 9
    canonical_propositions = cast(tuple[dict[str, object], ...], package.canonical_payload()["propositions"])
    assert [item["proposition"] for item in canonical_propositions] == sorted(
        item.value for item in archival.LegalCorpusArchivalProposition
    )
    missing = tuple(item for item in package.propositions if item.proposition is not archival.LegalCorpusArchivalProposition.P9_TRUST_ACTIVE_AT_ORIGINAL_ADMISSION_EVENT)
    _raises(
        "PROPOSITION_LEDGER_INCOMPLETE_OR_DUPLICATE",
        lambda: _package(propositions=missing),
    )
    duplicate = package.propositions[:-1] + (package.propositions[0],)
    _raises(
        "PROPOSITION_LEDGER_INCOMPLETE_OR_DUPLICATE",
        lambda: _package(propositions=duplicate),
    )


def test_historical_limitations_are_structural_and_unproven_is_not_false() -> None:
    package = _package()
    assert package.historical_event_time_source == "NONE"
    assert package.historical_event_time_recovery == "IMPOSSIBLE_FROM_CURRENT_CANONICAL_EVIDENCE"
    assert package.d1_to_r8d_identity_binding_source == "NONE"
    assert package.d1_to_r8d_binding_recovery == "IMPOSSIBLE_FROM_CURRENT_CANONICAL_EVIDENCE"
    assert package.d1_r8d_relationship_classification == "CONSISTENT_BUT_NOT_IDENTITY_BOUND"
    assert "status_at_admission_event" not in package.trust_snapshot.to_document()
    assert "status_at_admission_event" not in package.document_snapshot.to_document()
    tampered = package.to_document()
    tampered["historical_event_time_source"] = "ADMISSION_EVENT_CLOCK"
    _raises("HISTORICAL_LIMITATION_INVALID", lambda: archival.LegalCorpusArchivalEvidencePackage.from_document(tampered))


def test_trust_snapshot_round_trip_fingerprint_and_rejection_contract() -> None:
    snapshot = _trust_snapshot()
    assert archival.LegalCorpusArchivalTrustSnapshot.from_document(snapshot.to_document()) == snapshot
    preimage = {
        "key_id": KEY_ID,
        "algorithm": ED25519_ALGORITHM,
        "issuer": ISSUER,
        "authority_domain": AUTHORITY_DOMAIN,
        "scope": TRUST_ROOT_SCOPE,
        "operation": "LEGAL_CORPUS_DRAFT_ADMISSION",
        "permitted_operations": ["LEGAL_CORPUS_DRAFT_ADMISSION"],
        "public_key": PUBLIC_KEY,
        "valid_from": VALID_FROM.isoformat(),
        "valid_until": VALID_UNTIL.isoformat(),
        "status_observed_at_archival_capture": LegalCorpusOperatorKeyStatus.ACTIVE.value,
        "revision": 1,
        "trust_root_provenance": TRUST_ROOT_PROVENANCE,
        "trust_record_fingerprint": _trust_record_fingerprint(),
        "snapshot_observed_at": NOW.isoformat(),
        "snapshot_source_identity": SOURCE_IDENTITY,
        "snapshot_source_fingerprint": SOURCE_FINGERPRINT,
    }
    expected = hashlib.sha3_512(
        json.dumps(preimage, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert snapshot.snapshot_fingerprint == expected
    tampered = snapshot.to_document()
    tampered["snapshot_source_identity"] = "different-source"
    _raises("TRUST_SNAPSHOT_VALUE_INVALID", lambda: archival.LegalCorpusArchivalTrustSnapshot.from_document(tampered))
    tampered = snapshot.to_document()
    tampered["status_observed_at_archival_capture"] = "UNKNOWN"
    _raises("TRUST_SNAPSHOT_VALUE_INVALID", lambda: archival.LegalCorpusArchivalTrustSnapshot.from_document(tampered))
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        snapshot.status_observed_at_archival_capture = LegalCorpusOperatorKeyStatus.RETIRED  # type: ignore[misc]


def test_authorization_snapshot_preserves_public_d1_envelope_without_verification() -> None:
    snapshot = _authorization_snapshot()
    document = snapshot.to_document()
    assert archival.LegalCorpusArchivalAuthorizationSnapshot.from_document(document) == snapshot
    assert set(document) == {
        "schema", "authorization_id", "key_id", "operation", "scope",
        "source_document_id", "source_agreement_type", "source_version",
        "source_status", "source_content_reference", "source_sha3_512",
        "issued_at", "not_before", "expires_at", "replay_nonce",
        "idempotency_key", "authority_mechanism", "authority_mechanism_version",
        "signature", "authorization_file_sha3_512",
    }
    assert not any("private" in name.casefold() for name in document)
    assert not any(name in vars(type(snapshot)) for name in ("sign", "verify", "issue"))
    invalid = dict(document)
    invalid["source_sha3_512"] = "not-a-sha3"
    _raises("AUTHORIZATION_SNAPSHOT_VALUE_INVALID", lambda: archival.LegalCorpusArchivalAuthorizationSnapshot.from_document(invalid))
    invalid = dict(document)
    invalid["source_status"] = LegalDocumentStatus.APPROVED.value
    _raises("AUTHORIZATION_SNAPSHOT_VALUE_INVALID", lambda: archival.LegalCorpusArchivalAuthorizationSnapshot.from_document(invalid))


def test_r8d_snapshot_preserves_issuance_time_copy_and_excludes_d1_identity_claims() -> None:
    snapshot = _r8d_snapshot()
    assert archival.LegalCorpusArchivalR8DSnapshot.from_document(snapshot.to_document()) == snapshot
    document = snapshot.to_document()
    assert document["authorized_at_semantics"] == "AUTHORIZATION_ISSUANCE_TIME_COPY"
    assert not {"authorization_id", "key_id", "signature", "trust_record_fingerprint"}.intersection(document)
    invalid = dict(document)
    invalid["authority_evidence_fingerprint"] = "0" * 128
    _raises("R8D_SNAPSHOT_VALUE_INVALID", lambda: archival.LegalCorpusArchivalR8DSnapshot.from_document(invalid))
    invalid = dict(document)
    invalid["authorized_at_semantics"] = "ADMISSION_EVENT_TIME"
    _raises("R8D_SNAPSHOT_VALUE_INVALID", lambda: archival.LegalCorpusArchivalR8DSnapshot.from_document(invalid))


def test_document_snapshot_is_exact_digest_bound_draft_only_and_immutable() -> None:
    snapshot = _document_snapshot()
    assert archival.LegalCorpusArchivalDocumentSnapshot.from_document(snapshot.to_document()) == snapshot
    assert snapshot.sha3_512 == canonical_document_digest(snapshot.content, snapshot.content_reference)
    invalid = snapshot.to_document()
    invalid["sha3_512"] = "0" * 128
    _raises("DOCUMENT_SNAPSHOT_VALUE_INVALID", lambda: archival.LegalCorpusArchivalDocumentSnapshot.from_document(invalid))
    invalid = snapshot.to_document()
    invalid["status"] = LegalDocumentStatus.APPROVED.value
    _raises("DOCUMENT_SNAPSHOT_VALUE_INVALID", lambda: archival.LegalCorpusArchivalDocumentSnapshot.from_document(invalid))
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        snapshot.status = LegalDocumentStatus.APPROVED  # type: ignore[misc]


def test_multiline_document_content_is_exactly_preserved_and_package_deterministic() -> None:
    for content in ("Line one\nLine two", "Line one\r\nLine two"):
        snapshot = _document_snapshot(content=content)
        hydrated = archival.LegalCorpusArchivalDocumentSnapshot.from_document(snapshot.to_document())
        assert snapshot.content == content
        assert hydrated.content == content
        assert hydrated.to_document() == snapshot.to_document()
        first = _package(document_snapshot=snapshot)
        second = _package(document_snapshot=_document_snapshot(content=content))
        assert first.canonical_bytes() == second.canonical_bytes()
        assert first.package_fingerprint == second.package_fingerprint


def test_document_content_blank_rejection_and_metadata_text_contract_remain_separate() -> None:
    for content in ("", " \n\t "):
        values = _document_snapshot(content="valid content").to_document()
        values["content"] = content
        values["sha3_512"] = "0" * 128
        _raises(
            "DOCUMENT_SNAPSHOT_VALUE_INVALID",
            lambda values=values: archival.LegalCorpusArchivalDocumentSnapshot.from_document(values),
        )

    values = _document_snapshot().to_document()
    values["content_reference"] = "invalid\nreference"
    _raises(
        "DOCUMENT_SNAPSHOT_VALUE_INVALID",
        lambda: archival.LegalCorpusArchivalDocumentSnapshot.from_document(values),
    )

    values = _document_snapshot().to_document()
    values["sha3_512"] = "0" * 128
    _raises(
        "DOCUMENT_SNAPSHOT_VALUE_INVALID",
        lambda: archival.LegalCorpusArchivalDocumentSnapshot.from_document(values),
    )


def test_package_canonical_bytes_hydration_and_independent_fingerprint_are_stable() -> None:
    package = _package()
    first = package.canonical_bytes()
    second = _package().canonical_bytes()
    assert first == second
    assert b"'" not in first
    assert not first.endswith(b"\n")
    assert archival.LegalCorpusArchivalEvidencePackage.from_document(package.to_document()).to_document() == package.to_document()
    independent = hashlib.sha3_512(first).hexdigest()
    assert package.package_fingerprint == independent


def test_each_semantic_package_component_changes_fingerprint() -> None:
    package = _package()
    alternatives = (
        _package(package_id="123e4567-e89b-42d3-a456-426614174001"),
        _package(trust_snapshot=_trust_snapshot(snapshot_source_identity="different-source")),
        _package(authorization_snapshot=_authorization_snapshot(replay_nonce="different-nonce")),
        _package(r8d_snapshot=_r8d_snapshot(actor_representation="different-actor")),
        _package(document_snapshot=_document_snapshot(title="Different title")),
        _package(
            propositions=tuple(
                replace(item, limitation_reason="different historical limitation")
                if item.proposition is archival.LegalCorpusArchivalProposition.P3_D1_VALID_AT_ACTUAL_ADMISSION_EVENT_TIME
                else item
                for item in package.propositions
            )
        ),
    )
    assert all(candidate.package_fingerprint != package.package_fingerprint for candidate in alternatives)
    with pytest.raises(archival.LegalCorpusArchivalEvidenceError, match="HISTORICAL_LIMITATION_INVALID"):
        _package(historical_event_time_source="ADMISSION_EVENT_CLOCK")
    tampered = package.to_document()
    tampered["package_fingerprint"] = "0" * 128
    _raises("PACKAGE_FINGERPRINT_MISMATCH", lambda: archival.LegalCorpusArchivalEvidencePackage.from_document(tampered))


def test_package_id_contract_and_nested_alias_defenses() -> None:
    package = _package()
    assert _package(package_id=PACKAGE_ID.upper()).package_id == PACKAGE_ID
    for invalid_id in ("123e4567-e89b-12d3-a456-426614174000", "not-a-uuid"):
        _raises("PACKAGE_ID_INVALID", lambda invalid_id=invalid_id: _package(package_id=invalid_id))
    serialized = package.to_document()
    serialized_propositions = list(cast(tuple[object, ...], serialized["propositions"]))
    serialized["propositions"] = serialized_propositions
    serialized_propositions.append(serialized_propositions[0])
    assert len(package.propositions) == 9
    assert len(package.to_document()["propositions"]) == 9  # type: ignore[arg-type]
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        package.package_id = "123e4567-e89b-42d3-a456-426614174001"  # type: ignore[misc]


def test_hydration_tampering_is_fail_closed_across_package_surfaces() -> None:
    package = _package()
    cases: tuple[tuple[str, Any], ...] = (
        ("schema", "OTHER-SCHEMA"),
        ("version", "OTHER-VERSION"),
        ("package_id", "not-a-uuid"),
        ("historical_event_time_recovery", "ADMISSION_TIME"),
    )
    for field, value in cases:
        tampered = package.to_document()
        tampered[field] = value
        with pytest.raises(archival.LegalCorpusArchivalEvidenceError):
            archival.LegalCorpusArchivalEvidencePackage.from_document(tampered)
    nested_cases = (
        ("trust_snapshot", "snapshot_source_fingerprint", "0" * 128),
        ("authorization_snapshot", "source_version", "2.0.0-DRAFT"),
        ("r8d_snapshot", "source_version", "2.0.0-DRAFT"),
        ("document_snapshot", "content_reference", "other-reference"),
    )
    for parent, field, value in nested_cases:
        tampered = package.to_document()
        nested = dict(cast(dict[str, object], tampered[parent]))
        nested[field] = value
        tampered[parent] = nested
        with pytest.raises(archival.LegalCorpusArchivalEvidenceError):
            archival.LegalCorpusArchivalEvidencePackage.from_document(tampered)


def test_p3a_is_pure_and_exposes_no_operational_authority_surface() -> None:
    source = PRODUCTION_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert not any(
        token in module.casefold()
        for module in imported
        for token in ("pymongo", "kernel", "registry", "router", "requests", "http")
    )
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in {"open", "connect_db", "MongoClient", "urlopen"}
        for node in ast.walk(tree)
    )
    public_methods = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and not node.name.startswith("_")
    }
    assert public_methods <= {"fingerprint_for", "to_document", "from_document", "canonical_payload", "canonical_bytes"}
    assert not {"authorize", "admit", "execute", "provision", "mutate", "sign", "issue", "approve"}.intersection(public_methods)
    assert not any(name in archival.__all__ for name in ("authorize", "admit", "execute", "provision", "mutate", "sign", "issue", "approve"))
    assert "private_key" not in source.casefold()
    assert "LegalCorpusArchivalEvidencePackage" in archival.__all__


# ARTIFACT: test_legal_corpus_archival_evidence.py
# VERSION: v1.1.0-R1D-B0F-B4-R8O-P3A-R1-C1-LEGAL-CORPUS-ARCHIVAL-EVIDENCE-CERT
# AUTHORITY BOUNDARY: direct certificate evidence for pure archival values only
# TENANT POSTURE: PLATFORM archival evidence; no tenant/principal authority
# FAIL-CLOSED POSTURE: domain drift, tampering, or authority escalation fails
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
