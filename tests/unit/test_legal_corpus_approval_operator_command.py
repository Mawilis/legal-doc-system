"""Direct certificate for the governed Charter approval operator command.

TITLE: WILSY OS Legal Corpus Approval Operator Command Certificate
VERSION: v1.0.0-R1D-B0F-R9B-P6-A1-LEGAL-CORPUS-APPROVAL-OPERATOR-COMMAND-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Independently certifies public preparation, external signature
         handoff, closed hydration, verifier proof gating, and operator-only
         execution without approving or persisting the production Charter.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_corpus_approval_operator_command.py
COLLABORATION / OWNERSHIP: Tests the command adapter against the closed
                            authority, trust, verifier, and operator contracts.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.0.0 certifies the three explicit command phases and fail-closed
           source, target, signature, trust, and lifecycle boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic signatures and temporary public artifacts
                            only; no production secret or database is used.
TENANT BOUNDARY: PLATFORM command only; no tenant or principal evidence.
AUTHORITY BOUNDARY: Certificate evidence only; no approval is issued.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Invalid, divergent, expired, unsigned, or forged inputs
                     reject before any operator call.
"""
from __future__ import annotations

import ast
import base64
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from tools.eos.legal_operations import legal_corpus_approval_operator_command as command
from tools.eos.legal_operations.domain.legal_corpus_approval_authorization import (
    canonical_signed_payload,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_trust_root import (
    PRODUCTION_APPROVAL_TRUST_ROOT,
)


UTC = timezone.utc
APPROVED_AT = "2026-09-19T12:00:00Z"
EFFECTIVE_FROM = "2026-10-01T00:00:00Z"
SOURCE_PATH = Path(command.__file__).resolve()


def _prepare(tmp_path: Path) -> tuple[Path, Path, dict[str, Any]]:
    original = command._utc_now
    command._utc_now = lambda: datetime(2026, 9, 19, 11, 0, tzinfo=UTC)
    try:
        unsigned, payload = command.prepare_charter(
            output_directory=tmp_path,
            approved_at=APPROVED_AT,
            effective_from=EFFECTIVE_FROM,
            human_authority_representation="human-governance:ceremony-001",
            provenance_reference="host://charter-approval/ceremony-001",
        )
    finally:
        command._utc_now = original
    document: dict[str, Any] = json.loads(unsigned.read_text(encoding="utf-8"))
    return unsigned, payload, document


def test_prepare_binds_server_charter_and_exact_approved_successor(tmp_path: Path):
    unsigned, payload, document = _prepare(tmp_path)
    evidence = cast(dict[str, Any], document["approval_evidence"])
    assert unsigned.stat().st_mode & 0o777 == 0o600
    assert payload.stat().st_mode & 0o777 == 0o600
    assert evidence["source_document_id"] == "WILSY-OS-INSTITUTIONAL-CHARTER"
    assert evidence["source_version"] == "1.0.0-DRAFT"
    assert evidence["source_status"] == "DRAFT_REVIEW_REQUIRED"
    assert evidence["source_content_reference"] == "wilsy-os://legal/institutional-charter/1.0.0-draft"
    assert evidence["approved_version"] == "1.0.0-APPROVED"
    assert evidence["approved_status"] == "APPROVED"
    assert evidence["approved_content_reference"] == command.APPROVED_REFERENCE
    assert evidence["approved_content"] == evidence["source_content"]
    assert evidence["approved_sha3_512"] != evidence["source_sha3_512"]
    assert evidence["approved_supersedes_document_id"] == evidence["source_document_id"]
    assert evidence["approved_effective_from"] == "2026-10-01T00:00:00.000000+00:00"
    assert evidence["approved_created_at"] == evidence["approved_at"]
    assert document["key_id"] == PRODUCTION_APPROVAL_TRUST_ROOT.all_keys()[0].key_id
    nonce = cast(str, document["nonce"])
    assert len(base64.urlsafe_b64decode(nonce + "==")) == 32
    assert payload.read_bytes() == canonical_signed_payload(command._authorization_from_payload(document))


def test_prepare_requires_explicit_aware_times_and_governance_inputs(tmp_path: Path):
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError):
        command.prepare_charter(
            output_directory=tmp_path,
            approved_at="2026-09-19T12:00:00",
            effective_from=EFFECTIVE_FROM,
            human_authority_representation="human",
            provenance_reference="ref",
        )
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError):
        command.prepare_charter(
            output_directory=tmp_path,
            approved_at=APPROVED_AT,
            effective_from=EFFECTIVE_FROM,
            human_authority_representation=" ",
            provenance_reference="ref",
        )


def test_prepare_rejects_expired_production_issuance_window(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(command, "_utc_now", lambda: datetime(2026, 9, 20, 10, 3, 24, 50718, tzinfo=UTC))
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError, match="CANNOT_ISSUE"):
        command.prepare_charter(
            output_directory=tmp_path,
            approved_at=APPROVED_AT,
            effective_from=EFFECTIVE_FROM,
            human_authority_representation="human",
            provenance_reference="ref",
        )


def test_prepare_refuses_overwrite_and_has_no_database_surface(tmp_path: Path):
    _prepare(tmp_path)
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError, match="OUTPUT_ALREADY_EXISTS"):
        _prepare(tmp_path)
    tree = ast.parse(SOURCE_PATH.read_text(encoding="utf-8"))
    calls = [node.func.attr for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)]
    assert not set(calls) & {"start_session", "start_transaction", "commit_transaction", "abort_transaction"}
    assert not any(isinstance(node, ast.Name) and node.id == "LegalDocumentRegistry" for node in ast.walk(tree))


def test_finalize_requires_exactly_64_public_signature_bytes(tmp_path: Path):
    unsigned, _, _ = _prepare(tmp_path)
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
    unsigned, payload, document = _prepare(tmp_path)
    signature = tmp_path / "signature.bin"
    signature.write_bytes(b"y" * 64)
    output = tmp_path / "signed.json"
    command.finalize_authorization(unsigned, signature, output)
    signed = command._authorization_from_payload(json.loads(output.read_text(encoding="utf-8")))
    assert canonical_signed_payload(signed) == payload.read_bytes()
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError, match="OUTPUT_ALREADY_EXISTS"):
        command.finalize_authorization(unsigned, signature, output)


def test_execute_requires_canonical_source_target_and_real_verifier_proof(tmp_path: Path, monkeypatch):
    unsigned, _, document = _prepare(tmp_path)
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
    assert call[1]["source_document"] == command.INSTITUTIONAL_CHARTER_DRAFT
    final_evidence = cast(dict[str, Any], document["approval_evidence"])
    assert final_evidence["approved_version"] == "1.0.0-APPROVED"


@pytest.mark.parametrize("field,value", [("source_document_id", "OTHER"), ("approved_version", "1.0.0-OTHER"), ("approved_content", "changed")])
def test_execute_rejects_source_or_target_divergence(tmp_path: Path, field: str, value: str):
    _, _, document = _prepare(tmp_path)
    evidence = cast(dict[str, Any], document["approval_evidence"])
    evidence[field] = value
    evidence["evidence_fingerprint"] = "0" * 128
    with pytest.raises(command.LegalCorpusApprovalOperatorCommandError):
        command._authorization_from_payload(document)


def test_execute_rejects_bad_signature_and_expired_artifact(tmp_path: Path, monkeypatch):
    unsigned, _, _ = _prepare(tmp_path)
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
    for forbidden in ("Ed25519PrivateKey", "BEGIN PRIVATE KEY", "BEGIN ENCRYPTED PRIVATE KEY", "private.pem", "~/.wilsy", "/Users/wilsonkhanyezi/.wilsy", "passphrase prompt", "serialization.load_pem_private_key", "sign("):
        assert forbidden not in source


# ARTIFACT: test_legal_corpus_approval_operator_command.py
# VERSION: v1.0.0-R1D-B0F-R9B-P6-A1-LEGAL-CORPUS-APPROVAL-OPERATOR-COMMAND-CERT
# AUTHORITY BOUNDARY: direct command evidence only; no production approval
# TENANT POSTURE: PLATFORM-only synthetic certificate data
# FAIL-CLOSED POSTURE: invalid command artifacts and authority drift reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
