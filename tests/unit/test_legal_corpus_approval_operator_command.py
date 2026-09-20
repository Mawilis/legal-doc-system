"""Direct certificate for the reviewed-successor approval command.

TITLE: WILSY OS Legal Corpus Approval Operator Command Certificate
VERSION: v1.1.0-R1D-B0F-R9B-P7-A3-LEGAL-CORPUS-APPROVAL-OPERATOR-COMMAND-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Independently certifies the closed five-document selector, canonical
         source/target derivation, external-signature handoff, hydration, and
         verifier/operator boundary without approving or persisting production.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_approval_operator_command.py
COLLABORATION / OWNERSHIP: Tests the command adapter against the source-owned
                            production catalog and closed approval contracts.
CERTIFICATION / UPDATE DATE: 2026-09-20
CHANGELOG: v1.1.0 replaces the historical Charter-only certificate with
           bounded coverage for exactly five reviewed 1.1.0-DRAFT successors.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic signatures and temporary public artifacts
                            only; no production secret or database is used.
TENANT BOUNDARY: PLATFORM command only; no tenant or principal evidence.
AUTHORITY BOUNDARY: Certificate evidence only; no approval is issued.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Historical, unknown, divergent, unsigned, or forged
                     inputs reject before any operator call.
"""
from __future__ import annotations

import ast
import base64
import inspect
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tools.eos.legal_operations import legal_corpus_approval_operator_command as command
from tools.eos.legal_operations.domain.legal_corpus_approval_authorization import canonical_signed_payload
from tools.eos.legal_operations.domain.legal_corpus_approval_trust_root import PRODUCTION_APPROVAL_TRUST_ROOT
from tools.eos.legal_operations.domain.legal_acceptance import canonical_document_digest
from tools.eos.legal_operations.production_legal_corpus import (
    INSTITUTIONAL_CHARTER_DRAFT,
    PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS,
)

UTC = timezone.utc
APPROVED_AT = "2026-09-19T12:00:00Z"
EFFECTIVE_FROM = "2026-10-01T00:00:00Z"
SOURCE_PATH = Path(command.__file__).resolve()


def _prepare(tmp_path: Path, document_id: str) -> tuple[Path, Path, dict[str, Any]]:
    original = command._utc_now
    command._utc_now = lambda: datetime(2026, 9, 19, 11, 0, tzinfo=UTC)
    try:
        unsigned, payload = command.prepare_reviewed_successor(
            document_id=document_id, output_directory=tmp_path, approved_at=APPROVED_AT,
            effective_from=EFFECTIVE_FROM, human_authority_representation="human-governance:successor-001",
            provenance_reference="host://reviewed-successor/ceremony-001",
        )
    finally:
        command._utc_now = original
    return unsigned, payload, json.loads(unsigned.read_text(encoding="utf-8"))


@pytest.mark.parametrize("source", PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS)
def test_prepare_binds_each_exact_server_successor_and_derives_target(tmp_path: Path, source):
    unsigned, payload, document = _prepare(tmp_path, source.document_id)
    evidence = cast(dict[str, Any], document["approval_evidence"])
    assert unsigned.stat().st_mode & 0o777 == payload.stat().st_mode & 0o777 == 0o600
    assert evidence["source_document_id"] == source.document_id
    assert evidence["source_agreement_type"] == source.agreement_type.value
    assert evidence["source_version"] == evidence["approved_version"].replace("APPROVED", "DRAFT")
    assert evidence["source_status"] == "DRAFT_REVIEW_REQUIRED"
    assert evidence["source_content"] == source.content
    assert evidence["source_content_reference"] == source.content_reference
    assert evidence["source_sha3_512"] == source.sha3_512
    assert evidence["approved_document_id"] == source.document_id
    assert evidence["approved_agreement_type"] == source.agreement_type.value
    assert evidence["approved_title"] == source.title
    assert evidence["approved_jurisdiction"] == source.jurisdiction
    assert evidence["approved_locale"] == source.locale
    assert evidence["approved_version"] == "1.1.0-APPROVED"
    assert evidence["approved_status"] == "APPROVED"
    assert evidence["approved_content"] == source.content
    assert evidence["approved_content_reference"] == source.content_reference.replace("1.1.0-draft", "1.1.0-approved")
    assert evidence["approved_sha3_512"] == canonical_document_digest(
        source.content, evidence["approved_content_reference"]
    )
    assert evidence["approved_supersedes_document_id"] == source.document_id
    assert evidence["approved_effective_from"] == "2026-10-01T00:00:00.000000+00:00"
    assert evidence["approved_created_at"] == evidence["approved_at"]
    assert document["key_id"] == PRODUCTION_APPROVAL_TRUST_ROOT.all_keys()[0].key_id
    assert len(base64.urlsafe_b64decode(cast(str, document["nonce"]) + "==")) == 32
    assert payload.read_bytes() == canonical_signed_payload(command._authorization_from_payload(document))


@pytest.mark.parametrize("document_id", ["WILSY-OS-INSTITUTIONAL-CHARTER", "WILSY-OS-USER-TERMS-LEGACY", "UNKNOWN-DOCUMENT"])
def test_prepare_rejects_historical_charter_and_unknown_sources(tmp_path: Path, document_id: str):
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError, match="REVIEWED_SUCCESSOR_DOCUMENT_REQUIRED"):
        command.prepare_reviewed_successor(document_id=document_id, output_directory=tmp_path, approved_at=APPROVED_AT,
                                           effective_from=EFFECTIVE_FROM, human_authority_representation="human", provenance_reference="ref")


def test_prepare_requires_explicit_times_and_governance_inputs(tmp_path: Path):
    document_id = PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS[0].document_id
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError):
        command.prepare_reviewed_successor(document_id=document_id, output_directory=tmp_path, approved_at="2026-09-19T12:00:00",
                                           effective_from=EFFECTIVE_FROM, human_authority_representation="human", provenance_reference="ref")
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError):
        command.prepare_reviewed_successor(document_id=document_id, output_directory=tmp_path, approved_at=APPROVED_AT,
                                           effective_from=EFFECTIVE_FROM, human_authority_representation=" ", provenance_reference="ref")


def test_prepare_rejects_expired_production_issuance_window(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(command, "_utc_now", lambda: datetime(2026, 9, 20, 10, 3, 24, 50718, tzinfo=UTC))
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError, match="CANNOT_ISSUE"):
        command.prepare_reviewed_successor(document_id=PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS[0].document_id,
                                           output_directory=tmp_path, approved_at=APPROVED_AT, effective_from=EFFECTIVE_FROM,
                                           human_authority_representation="human", provenance_reference="ref")


def test_prepare_refuses_overwrite_and_has_no_database_or_caller_document_surface(tmp_path: Path):
    document_id = PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS[0].document_id
    _prepare(tmp_path, document_id)
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError, match="OUTPUT_ALREADY_EXISTS"):
        _prepare(tmp_path, document_id)
    assert set(inspect.signature(command.prepare_reviewed_successor).parameters) == {
        "document_id", "output_directory", "approved_at", "effective_from", "human_authority_representation", "provenance_reference"
    }
    tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))
    calls = [node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
    assert not set(calls) & {"start_session", "start_transaction", "commit_transaction", "abort_transaction"}
    assert not any(isinstance(node, ast.Name) and node.id in {"LegalDocumentRegistry", "MongoClient"} for node in ast.walk(tree))


def test_finalize_requires_exactly_64_public_signature_bytes(tmp_path: Path):
    unsigned, _, _ = _prepare(tmp_path, PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS[0].document_id)
    signature = tmp_path / "signature.bin"
    signature.write_bytes(b"x" * 64)
    output = tmp_path / "signed.json"
    command.finalize_authorization(unsigned, signature, output)
    signed = json.loads(output.read_text(encoding="utf-8"))
    assert signed["signature_base64url"] != command._ZERO_SIGNATURE
    assert len(base64.urlsafe_b64decode(signed["signature_base64url"] + "==")) == 64
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError, match="SIGNATURE_FILE_INVALID"):
        command.finalize_authorization(unsigned, tmp_path / "missing", tmp_path / "other.json")


def test_finalize_preserves_canonical_payload_and_refuses_overwrite(tmp_path: Path):
    unsigned, payload, _ = _prepare(tmp_path, PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS[1].document_id)
    signature = tmp_path / "signature.bin"
    signature.write_bytes(b"y" * 64)
    output = tmp_path / "signed.json"
    command.finalize_authorization(unsigned, signature, output)
    signed = command._authorization_from_payload(json.loads(output.read_text(encoding="utf-8")))
    assert canonical_signed_payload(signed) == payload.read_bytes()
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError, match="OUTPUT_ALREADY_EXISTS"):
        command.finalize_authorization(unsigned, signature, output)


def test_execute_forwards_selected_exact_source_to_verifier_and_operator(tmp_path: Path, monkeypatch):
    source = PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS[2]
    unsigned, _, document = _prepare(tmp_path, source.document_id)
    signature = tmp_path / "signature.bin"
    signature.write_bytes(b"z" * 64)
    signed_path = tmp_path / "signed.json"
    command.finalize_authorization(unsigned, signature, signed_path)
    calls: list[object] = []
    proof = object()
    def verifier(*args, **kwargs):
        calls.append((args, kwargs))
        return proof
    class FakeOperator:
        def execute(self, value):
            assert value is proof
            return SimpleNamespace(state=command.LegalCorpusApprovalOperatorResultState.COMMITTED_CREATED, attempts=1)
    monkeypatch.setattr(command, "verify_legal_corpus_approval_authorization", verifier)
    monkeypatch.setattr(command, "LegalCorpusApprovalOperator", FakeOperator)
    assert command.execute_authorization(signed_path).value == "COMMITTED_CREATED"
    call = cast(tuple[tuple[Any, ...], dict[str, Any]], calls[0])
    assert call[1]["source_document"] == source
    assert cast(dict[str, Any], document["approval_evidence"])["approved_version"] == "1.1.0-APPROVED"


@pytest.mark.parametrize("field,value", [("source_document_id", "OTHER"), ("approved_version", "1.1.0-OTHER"),
                                          ("approved_content", "changed"), ("approved_content_reference", "wilsy-os://caller-controlled")])
def test_hydration_rejects_source_or_target_divergence(tmp_path: Path, field: str, value: str):
    _, _, document = _prepare(tmp_path, PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS[0].document_id)
    evidence = cast(dict[str, Any], document["approval_evidence"])
    evidence[field] = value
    evidence["evidence_fingerprint"] = "0" * 128
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError):
        command._authorization_from_payload(document)


def test_execute_rejects_expired_artifact(tmp_path: Path, monkeypatch):
    unsigned, _, _ = _prepare(tmp_path, PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS[0].document_id)
    signed = tmp_path / "signed.json"
    signature = tmp_path / "signature.bin"
    signature.write_bytes(b"q" * 64)
    command.finalize_authorization(unsigned, signature, signed)
    monkeypatch.setattr(command, "_utc_now", lambda: datetime(2026, 9, 20, 10, 4, tzinfo=UTC))
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError, match="VERIFICATION_FAILED"):
        command.execute_authorization(signed)


def test_help_and_source_leakage_audit():
    with pytest.raises(SystemExit) as error:
        command.main(["--help"])
    assert error.value.code == 0
    source = SOURCE_PATH.read_text(encoding="utf-8")
    assert "prepare-reviewed-successor" in source
    assert "prepare-charter" not in source
    assert "INSTITUTIONAL_CHARTER_DRAFT" not in source
    for forbidden in ("Ed25519PrivateKey", "BEGIN PRIVATE KEY", "BEGIN ENCRYPTED PRIVATE KEY", "private.pem", "~/.wilsy",
                      "/Users/wilsonkhanyezi/.wilsy", "passphrase prompt", "serialization.load_pem_private_key", "sign(", "MongoClient"):
        assert forbidden not in source


# ARTIFACT: test_legal_corpus_approval_operator_command.py
# VERSION: v1.1.0-R1D-B0F-R9B-P7-A3-LEGAL-CORPUS-APPROVAL-OPERATOR-COMMAND-CERT
# AUTHORITY BOUNDARY: direct command evidence only; no production approval
# TENANT POSTURE: PLATFORM-only synthetic certificate data
# FAIL-CLOSED POSTURE: invalid command artifacts and authority drift reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
