"""Governed external-signer adapter for reviewed successor approvals.

TITLE: WILSY OS Legal Corpus Approval Operator Command
VERSION: v1.1.0-R1D-B0F-R9B-P7-A3-LEGAL-CORPUS-APPROVAL-OPERATOR-COMMAND
AUTHORITY: Wilsy OS Core Governance
EPITOME: Separates public reviewed-successor approval-envelope preparation,
         external signature completion, and verified production execution
         without becoming a new legal authority or owning Mongo lifecycle.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/legal_corpus_approval_operator_command.py
COLLABORATION / OWNERSHIP: The production corpus owns the five reviewed
                            successor sources; the approval authority and verifier own evidence and
                            signature semantics; LegalCorpusApprovalOperator
                            alone owns database sessions and transactions.
CERTIFICATION / UPDATE DATE: 2026-09-20
CHANGELOG: v1.1.0 replaces Charter-only preparation with a closed selector for
           exactly five server-owned 1.1.0-DRAFT reviewed successors; finalize
           and execute remain separate and historical Charter approval is not
           reopened.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only public metadata and externally supplied
                            signature bytes are handled. No key material,
                            credentials, request context, or secret loading is
                            permitted.
TENANT BOUNDARY: PLATFORM corpus only; no tenant or principal authority.
AUTHORITY BOUNDARY: Adapter orchestration only. It cannot approve, review,
                    sign, accept, bind an organisation, or invent source truth.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Closed schema, canonical source/target, trust eligibility,
                     signature verification, and operator-result checks reject.
TRANSACTION BOUNDARY: EXECUTE delegates lifecycle exclusively to the existing
                       LegalCorpusApprovalOperator.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import secrets
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Final, Mapping, Sequence

from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalAgreementType,
    LegalDocumentStatus,
    LegalDocumentVersion,
    canonical_document_digest,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_authority import (
    APPROVAL_AUTHORITY_MECHANISM,
    APPROVAL_AUTHORITY_MECHANISM_VERSION,
    APPROVAL_AUTHORITY_SOURCE,
    APPROVAL_EVIDENCE_SCHEMA_VERSION,
    APPROVAL_OPERATION,
    APPROVAL_SCOPE,
    APPROVAL_SIGNING_MECHANISM,
    APPROVAL_SIGNING_MECHANISM_VERSION,
    LegalCorpusApprovalAuthorityEvidence,
    LegalCorpusApprovalAuthorityMechanism,
    LegalCorpusApprovalAuthorityScope,
    LegalCorpusApprovalAuthoritySource,
    LegalCorpusApprovalDecision,
    LegalCorpusApprovalOperation,
    LegalCorpusApprovalSigningMechanism,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_authorization import (
    AUTHORIZED_OPERATION,
    AUTHORITY_SCOPE,
    LegalCorpusApprovalAuthorization,
    LegalCorpusApprovalAuthorizationError,
    LegalCorpusApprovalAuthorizationOperation,
    LegalCorpusApprovalAuthorizationScope,
    VerifiedLegalCorpusApprovalAuthorization,
    canonical_signed_payload,
    verify_legal_corpus_approval_authorization,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_trust_root import (
    APPROVAL_AUTHORITY_DOMAIN,
    APPROVAL_AUTHORITY_ROLE,
    APPROVAL_ISSUER_IDENTITY,
    ED25519_ALGORITHM,
    PRODUCTION_APPROVAL_TRUST_ROOT,
)
from tools.eos.legal_operations.service.legal_corpus_approval_operator import (
    LegalCorpusApprovalOperator,
    LegalCorpusApprovalOperatorResultState,
)
from tools.eos.legal_operations.production_legal_corpus import (
    PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS,
)


VERSION: Final[str] = "v1.1.0-R1D-B0F-R9B-P7-A3-LEGAL-CORPUS-APPROVAL-OPERATOR-COMMAND"
REVIEWED_SUCCESSOR_SOURCE_VERSION: Final[str] = "1.1.0-DRAFT"
REVIEWED_SUCCESSOR_APPROVED_VERSION: Final[str] = "1.1.0-APPROVED"
APPROVED_VERSION: Final[str] = REVIEWED_SUCCESSOR_APPROVED_VERSION
REVIEWED_SUCCESSOR_DOCUMENT_IDS: Final[frozenset[str]] = frozenset(
    document.document_id for document in PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS
)
APPROVAL_TRUSTED_KEY_ID: Final[str] = "prdca-key:legal-corpus-approval-f8bc464615e8047f008909c36750348b"
AUTHORIZATION_LIFETIME: Final[timedelta] = timedelta(minutes=10)
SIGNATURE_REFERENCE_PREFIX: Final[str] = "wilsy-os://legal/approval-signature/"
_ZERO_SIGNATURE: Final[str] = base64.urlsafe_b64encode(b"\x00" * 64).rstrip(b"=").decode("ascii")


class LegalCorpusApprovalOperatorCommandError(ValueError):
    """Bounded, non-sensitive command failure."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


def _utc_now() -> datetime:
    """Return the aware UTC instant used only for issuance/verification timing."""
    return datetime.now(timezone.utc)


def _parse_timestamp(value: str, code: str) -> datetime:
    """Parse one explicit RFC3339 timestamp and normalize it to UTC."""
    if not isinstance(value, str) or not value.strip():
        raise LegalCorpusApprovalOperatorCommandError(code)
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except (TypeError, ValueError):
        raise LegalCorpusApprovalOperatorCommandError(code) from None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise LegalCorpusApprovalOperatorCommandError(code)
    return parsed.astimezone(timezone.utc)


def _timestamp(value: object, code: str) -> datetime:
    """Validate a hydrated aware timestamp without reading a clock."""
    if not isinstance(value, str):
        raise LegalCorpusApprovalOperatorCommandError(code)
    return _parse_timestamp(value, code)


def _canonical_json(payload: Mapping[str, object]) -> bytes:
    """Serialize public command artifacts deterministically."""
    try:
        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError):
        raise LegalCorpusApprovalOperatorCommandError("AUTHORIZATION_SERIALIZATION_INVALID") from None


def _write_new(path: Path, data: bytes) -> None:
    """Create one public artifact exactly once with restrictive permissions."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
        os.chmod(path, 0o600)
    except FileExistsError:
        raise LegalCorpusApprovalOperatorCommandError("OUTPUT_ALREADY_EXISTS") from None
    except OSError:
        raise LegalCorpusApprovalOperatorCommandError("OUTPUT_WRITE_FAILED") from None


def _read_json(path: Path) -> dict[str, Any]:
    """Read one bounded JSON object without resolving alternate source files."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise LegalCorpusApprovalOperatorCommandError("AUTHORIZATION_FILE_INVALID") from None
    if not isinstance(value, dict):
        raise LegalCorpusApprovalOperatorCommandError("AUTHORIZATION_SCHEMA_INVALID")
    return value


def _document_from_payload(payload: Mapping[str, Any], prefix: str) -> LegalDocumentVersion:
    """Reconstruct one immutable document from the closed flattened schema."""
    required = {
        f"{prefix}_document_id", f"{prefix}_agreement_type", f"{prefix}_version",
        f"{prefix}_title", f"{prefix}_jurisdiction", f"{prefix}_locale",
        f"{prefix}_effective_from", f"{prefix}_status", f"{prefix}_content_reference",
        f"{prefix}_content", f"{prefix}_sha3_512", f"{prefix}_created_at",
        f"{prefix}_supersedes_document_id",
    }
    if set(payload) & required != required:
        raise LegalCorpusApprovalOperatorCommandError("AUTHORIZATION_SCHEMA_INVALID")
    try:
        return LegalDocumentVersion(
            document_id=payload[f"{prefix}_document_id"],
            agreement_type=LegalAgreementType(payload[f"{prefix}_agreement_type"]),
            version=payload[f"{prefix}_version"],
            title=payload[f"{prefix}_title"],
            jurisdiction=payload[f"{prefix}_jurisdiction"],
            locale=payload[f"{prefix}_locale"],
            effective_from=_timestamp(payload[f"{prefix}_effective_from"], "DOCUMENT_TIMESTAMP_INVALID"),
            status=LegalDocumentStatus(payload[f"{prefix}_status"]),
            content_reference=payload[f"{prefix}_content_reference"],
            content=payload[f"{prefix}_content"],
            sha3_512=payload[f"{prefix}_sha3_512"],
            created_at=_timestamp(payload[f"{prefix}_created_at"], "DOCUMENT_TIMESTAMP_INVALID"),
            supersedes_document_id=payload[f"{prefix}_supersedes_document_id"],
        )
    except (KeyError, TypeError, ValueError):
        raise LegalCorpusApprovalOperatorCommandError("AUTHORIZATION_DOCUMENT_INVALID") from None


def _evidence_from_payload(payload: Mapping[str, Any]) -> LegalCorpusApprovalAuthorityEvidence:
    """Reconstruct complete approval evidence using existing domain validation."""
    required = {
        "approval_evidence_id", "schema_version", "scope", "operation", "approval_decision",
        "approval_authority_source", "approval_authority_mechanism", "approval_authority_mechanism_version",
        "human_authority_representation", "approval_signing_mechanism", "approval_signing_mechanism_version",
        "approval_signing_key_id", "approval_signature_reference", "approved_at", "effective_from",
        "idempotency_key", "provenance_reference", "evidence_fingerprint",
    }
    if not required.issubset(payload):
        raise LegalCorpusApprovalOperatorCommandError("AUTHORIZATION_SCHEMA_INVALID")
    try:
        return LegalCorpusApprovalAuthorityEvidence(
            approval_evidence_id=payload["approval_evidence_id"],
            schema_version=payload["schema_version"],
            scope=LegalCorpusApprovalAuthorityScope(payload["scope"]),
            operation=LegalCorpusApprovalOperation(payload["operation"]),
            approval_decision=LegalCorpusApprovalDecision(payload["approval_decision"]),
            approval_authority_source=LegalCorpusApprovalAuthoritySource(payload["approval_authority_source"]),
            approval_authority_mechanism=LegalCorpusApprovalAuthorityMechanism(payload["approval_authority_mechanism"]),
            approval_authority_mechanism_version=payload["approval_authority_mechanism_version"],
            human_authority_representation=payload["human_authority_representation"],
            approval_signing_mechanism=LegalCorpusApprovalSigningMechanism(payload["approval_signing_mechanism"]),
            approval_signing_mechanism_version=payload["approval_signing_mechanism_version"],
            approval_signing_key_id=payload["approval_signing_key_id"],
            approval_signature_reference=payload["approval_signature_reference"],
            source_document=_document_from_payload(payload, "source"),
            approved_document=_document_from_payload(payload, "approved"),
            approved_at=_timestamp(payload["approved_at"], "APPROVED_AT_INVALID"),
            effective_from=_timestamp(payload["effective_from"], "EFFECTIVE_FROM_INVALID"),
            idempotency_key=payload["idempotency_key"],
            provenance_reference=payload["provenance_reference"],
            evidence_fingerprint=payload["evidence_fingerprint"],
        )
    except (KeyError, TypeError, ValueError):
        raise LegalCorpusApprovalOperatorCommandError("AUTHORIZATION_EVIDENCE_INVALID") from None


def _authorization_from_payload(payload: Mapping[str, Any]) -> LegalCorpusApprovalAuthorization:
    """Reconstruct one exact authorization envelope from canonical JSON."""
    required = {
        "schema", "authorization_id", "issuer_identity", "authority_role", "authority_domain",
        "algorithm", "key_id", "trust_fingerprint", "operation", "scope", "approval_evidence",
        "issued_at", "expires_at", "nonce", "idempotency_key", "signature_base64url",
    }
    if set(payload) != required:
        raise LegalCorpusApprovalOperatorCommandError("AUTHORIZATION_SCHEMA_INVALID")
    evidence_payload = payload["approval_evidence"]
    if not isinstance(evidence_payload, dict):
        raise LegalCorpusApprovalOperatorCommandError("AUTHORIZATION_SCHEMA_INVALID")
    try:
        return LegalCorpusApprovalAuthorization(
            authorization_id=payload["authorization_id"],
            issuer_identity=payload["issuer_identity"],
            authority_role=payload["authority_role"],
            authority_domain=payload["authority_domain"],
            algorithm=payload["algorithm"],
            key_id=payload["key_id"],
            trust_fingerprint=payload["trust_fingerprint"],
            operation=LegalCorpusApprovalAuthorizationOperation(payload["operation"]),
            scope=LegalCorpusApprovalAuthorizationScope(payload["scope"]),
            approval_evidence=_evidence_from_payload(evidence_payload),
            issued_at=_timestamp(payload["issued_at"], "AUTHORIZATION_TIMESTAMP_INVALID"),
            expires_at=_timestamp(payload["expires_at"], "AUTHORIZATION_TIMESTAMP_INVALID"),
            nonce=payload["nonce"],
            idempotency_key=payload["idempotency_key"],
            signature_base64url=payload["signature_base64url"],
            schema=payload["schema"],
        )
    except (KeyError, TypeError, ValueError, LegalCorpusApprovalAuthorizationError):
        raise LegalCorpusApprovalOperatorCommandError("AUTHORIZATION_INVALID") from None


def _reviewed_successor(document_id: str) -> LegalDocumentVersion:
    """Resolve one exact server-owned reviewed successor by document ID."""
    if not isinstance(document_id, str) or document_id not in REVIEWED_SUCCESSOR_DOCUMENT_IDS:
        raise LegalCorpusApprovalOperatorCommandError("REVIEWED_SUCCESSOR_DOCUMENT_REQUIRED")
    matches = tuple(
        document
        for document in PLATFORM_LEGAL_CORPUS_REVIEWED_SUCCESSOR_DRAFTS
        if document.document_id == document_id
    )
    if len(matches) != 1:
        raise LegalCorpusApprovalOperatorCommandError("CANONICAL_SOURCE_INVALID")
    source = matches[0]
    if (
        source.version != REVIEWED_SUCCESSOR_SOURCE_VERSION
        or source.status is not LegalDocumentStatus.DRAFT_REVIEW_REQUIRED
    ):
        raise LegalCorpusApprovalOperatorCommandError("CANONICAL_SOURCE_INVALID")
    return source


def _approved_reference(source: LegalDocumentVersion) -> str:
    """Derive the approved reference from the canonical draft reference."""
    suffix = "/1.1.0-draft"
    if not source.content_reference.endswith(suffix):
        raise LegalCorpusApprovalOperatorCommandError("CANONICAL_SOURCE_INVALID")
    return source.content_reference[: -len(suffix)] + "/1.1.0-approved"


def _approved_target(source: LegalDocumentVersion, effective_from: datetime, approved_at: datetime) -> LegalDocumentVersion:
    """Construct the exact approved successor without changing source prose."""
    if source != _reviewed_successor(source.document_id):
        raise LegalCorpusApprovalOperatorCommandError("CANONICAL_SOURCE_MISMATCH")
    reference = _approved_reference(source)
    return LegalDocumentVersion(
        document_id=source.document_id,
        agreement_type=source.agreement_type,
        version=REVIEWED_SUCCESSOR_APPROVED_VERSION,
        title=source.title,
        jurisdiction=source.jurisdiction,
        locale=source.locale,
        effective_from=effective_from,
        status=LegalDocumentStatus.APPROVED,
        content_reference=reference,
        content=source.content,
        sha3_512=canonical_document_digest(source.content, reference),
        created_at=approved_at,
        supersedes_document_id=source.document_id,
    )


def _build_unsigned(
    *,
    document_id: str,
    approved_at: datetime,
    effective_from: datetime,
    human_authority_representation: str,
    provenance_reference: str,
) -> LegalCorpusApprovalAuthorization:
    """Build public unsigned evidence; construction is not authorization."""
    source = _reviewed_successor(document_id)
    now = _utc_now()
    trusted_key = PRODUCTION_APPROVAL_TRUST_ROOT.resolve(APPROVAL_TRUSTED_KEY_ID)
    issued_at = now
    expires_at = issued_at + AUTHORIZATION_LIFETIME
    if not trusted_key.can_issue(AUTHORIZED_OPERATION, AUTHORITY_SCOPE, issued_at):
        raise LegalCorpusApprovalOperatorCommandError("APPROVAL_KEY_CANNOT_ISSUE_AT_CURRENT_TIME")
    if not isinstance(human_authority_representation, str) or not human_authority_representation.strip():
        raise LegalCorpusApprovalOperatorCommandError("HUMAN_AUTHORITY_REQUIRED")
    if not isinstance(provenance_reference, str) or not provenance_reference.strip():
        raise LegalCorpusApprovalOperatorCommandError("PROVENANCE_REFERENCE_REQUIRED")
    authorization_id = str(uuid.uuid4())
    target = _approved_target(source, effective_from, approved_at)
    evidence_values: dict[str, Any] = {
        "approval_evidence_id": str(uuid.uuid4()),
        "schema_version": APPROVAL_EVIDENCE_SCHEMA_VERSION,
        "scope": LegalCorpusApprovalAuthorityScope.PLATFORM,
        "operation": LegalCorpusApprovalOperation.DOCUMENT_APPROVAL,
        "approval_decision": LegalCorpusApprovalDecision.APPROVE,
        "approval_authority_source": LegalCorpusApprovalAuthoritySource.HUMAN_GOVERNED,
        "approval_authority_mechanism": LegalCorpusApprovalAuthorityMechanism.HUMAN_APPROVAL_RECORD,
        "approval_authority_mechanism_version": APPROVAL_AUTHORITY_MECHANISM_VERSION,
        "human_authority_representation": human_authority_representation.strip(),
        "approval_signing_mechanism": LegalCorpusApprovalSigningMechanism.EXTERNAL_GOVERNED_SIGNER,
        "approval_signing_mechanism_version": APPROVAL_SIGNING_MECHANISM_VERSION,
        "approval_signing_key_id": trusted_key.key_id,
        "approval_signature_reference": SIGNATURE_REFERENCE_PREFIX + authorization_id,
        "source_document": source,
        "approved_document": target,
        "approved_at": approved_at,
        "effective_from": effective_from,
        "idempotency_key": str(uuid.uuid4()),
        "provenance_reference": provenance_reference.strip(),
    }
    evidence_values["evidence_fingerprint"] = LegalCorpusApprovalAuthorityEvidence.fingerprint_for(**evidence_values)
    evidence = LegalCorpusApprovalAuthorityEvidence(**evidence_values)
    return LegalCorpusApprovalAuthorization(
        authorization_id=authorization_id,
        issuer_identity=APPROVAL_ISSUER_IDENTITY,
        authority_role=APPROVAL_AUTHORITY_ROLE,
        authority_domain=APPROVAL_AUTHORITY_DOMAIN,
        algorithm=ED25519_ALGORITHM,
        key_id=trusted_key.key_id,
        trust_fingerprint=trusted_key.trust_fingerprint,
        operation=LegalCorpusApprovalAuthorizationOperation.DOCUMENT_APPROVAL,
        scope=LegalCorpusApprovalAuthorizationScope.PLATFORM,
        approval_evidence=evidence,
        issued_at=issued_at,
        expires_at=expires_at,
        nonce=base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode("ascii"),
        idempotency_key=str(uuid.uuid4()),
        signature_base64url=_ZERO_SIGNATURE,
    )


def _assert_canonical_authorization(authorization: LegalCorpusApprovalAuthorization) -> None:
    """Reject every source or target outside the five reviewed successors."""
    evidence = authorization.approval_evidence
    source = evidence.source_document
    target = evidence.approved_document
    canonical_source = _reviewed_successor(source.document_id)
    if source != canonical_source:
        raise LegalCorpusApprovalOperatorCommandError("CANONICAL_SOURCE_MISMATCH")
    expected = _approved_target(source, evidence.effective_from, evidence.approved_at)
    if target != expected:
        raise LegalCorpusApprovalOperatorCommandError("APPROVED_TARGET_MISMATCH")
    if authorization.key_id != PRODUCTION_APPROVAL_TRUST_ROOT.all_keys()[0].key_id:
        raise LegalCorpusApprovalOperatorCommandError("PRODUCTION_APPROVAL_KEY_REQUIRED")


def _signature_bytes(path: Path) -> str:
    """Read exactly one external 64-byte signature or its canonical encoding."""
    try:
        raw = path.read_bytes()
    except OSError:
        raise LegalCorpusApprovalOperatorCommandError("SIGNATURE_FILE_INVALID") from None
    if len(raw) == 64:
        decoded = raw
    else:
        try:
            text = raw.decode("ascii").strip()
            if not text or "=" in text:
                raise ValueError
            decoded = base64.urlsafe_b64decode(text + "=" * ((4 - len(text) % 4) % 4))
            if base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii") != text:
                raise ValueError
        except (UnicodeError, ValueError, TypeError):
            raise LegalCorpusApprovalOperatorCommandError("SIGNATURE_FILE_INVALID") from None
    if len(decoded) != 64:
        raise LegalCorpusApprovalOperatorCommandError("SIGNATURE_FILE_INVALID")
    return base64.urlsafe_b64encode(decoded).rstrip(b"=").decode("ascii")


def prepare_reviewed_successor(
    *,
    document_id: str,
    output_directory: Path,
    approved_at: str,
    effective_from: str,
    human_authority_representation: str,
    provenance_reference: str,
) -> tuple[Path, Path]:
    """Emit one reviewed-successor unsigned JSON and signing payload."""
    approved_at_value = _parse_timestamp(approved_at, "APPROVED_AT_INVALID")
    effective_value = _parse_timestamp(effective_from, "EFFECTIVE_FROM_INVALID")
    authorization = _build_unsigned(
        document_id=document_id,
        approved_at=approved_at_value,
        effective_from=effective_value,
        human_authority_representation=human_authority_representation,
        provenance_reference=provenance_reference,
    )
    unsigned_path = output_directory / "approval-authorization.unsigned.json"
    payload_path = output_directory / "approval-authorization.payload"
    _write_new(unsigned_path, _canonical_json(authorization.to_document()))
    payload = canonical_signed_payload(authorization)
    _write_new(payload_path, payload)
    print("READY_FOR_EXTERNAL_SIGNATURE=YES")
    print("PRODUCTION_APPROVAL_EXECUTED=NO")
    print(f"PAYLOAD_BYTES={len(payload)}")
    print(f"PAYLOAD_SHA3_512={__import__('hashlib').sha3_512(payload).hexdigest()}")
    return unsigned_path, payload_path


def finalize_authorization(unsigned_authorization_file: Path, signature_file: Path, output_file: Path) -> Path:
    """Attach only externally supplied public signature bytes without verification."""
    unsigned = _authorization_from_payload(_read_json(unsigned_authorization_file))
    _assert_canonical_authorization(unsigned)
    if unsigned.signature_base64url != _ZERO_SIGNATURE:
        raise LegalCorpusApprovalOperatorCommandError("UNSIGNED_AUTHORIZATION_REQUIRED")
    signature = _signature_bytes(signature_file)
    signed = LegalCorpusApprovalAuthorization(
        authorization_id=unsigned.authorization_id,
        issuer_identity=unsigned.issuer_identity,
        authority_role=unsigned.authority_role,
        authority_domain=unsigned.authority_domain,
        algorithm=unsigned.algorithm,
        key_id=unsigned.key_id,
        trust_fingerprint=unsigned.trust_fingerprint,
        operation=unsigned.operation,
        scope=unsigned.scope,
        approval_evidence=unsigned.approval_evidence,
        issued_at=unsigned.issued_at,
        expires_at=unsigned.expires_at,
        nonce=unsigned.nonce,
        idempotency_key=unsigned.idempotency_key,
        signature_base64url=signature,
    )
    _write_new(output_file, _canonical_json(signed.to_document()))
    print("AUTHORIZATION_FINALIZED=YES")
    print("PRODUCTION_APPROVAL_EXECUTED=NO")
    return output_file


def execute_authorization(authorization_file: Path) -> LegalCorpusApprovalOperatorResultState:
    """Verify a completed artifact and delegate execution to the closed operator."""
    authorization = _authorization_from_payload(_read_json(authorization_file))
    _assert_canonical_authorization(authorization)
    source = _reviewed_successor(authorization.approval_evidence.source_document.document_id)
    try:
        proof = verify_legal_corpus_approval_authorization(
            authorization,
            PRODUCTION_APPROVAL_TRUST_ROOT,
            now=_utc_now(),
            expected_evidence=authorization.approval_evidence,
            source_document=source,
            approved_document=authorization.approval_evidence.approved_document,
        )
    except Exception as error:
        if isinstance(error, LegalCorpusApprovalAuthorizationError):
            raise LegalCorpusApprovalOperatorCommandError("AUTHORIZATION_VERIFICATION_FAILED") from error
        raise LegalCorpusApprovalOperatorCommandError("AUTHORIZATION_VERIFICATION_FAILED") from error
    result = LegalCorpusApprovalOperator().execute(proof)
    if result.state not in (
        LegalCorpusApprovalOperatorResultState.COMMITTED_CREATED,
        LegalCorpusApprovalOperatorResultState.COMMITTED_EXACT_REPLAY,
        LegalCorpusApprovalOperatorResultState.RECONCILED_AFTER_UNKNOWN_COMMIT,
    ):
        raise LegalCorpusApprovalOperatorCommandError("OPERATOR_RESULT_INVALID")
    print(f"EXECUTION_RESULT={result.state.value}")
    print(f"TRANSACTION_ATTEMPTS={result.attempts}")
    return result.state


def _parser() -> argparse.ArgumentParser:
    """Build the bounded three-phase command parser."""
    parser = argparse.ArgumentParser(prog="legal_corpus_approval_operator_command")
    commands = parser.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare-reviewed-successor")
    prepare.add_argument("--document-id", required=True)
    prepare.add_argument("--output-directory", type=Path, required=True)
    prepare.add_argument("--approved-at", required=True)
    prepare.add_argument("--effective-from", required=True)
    prepare.add_argument("--human-authority-representation", required=True)
    prepare.add_argument("--provenance-reference", required=True)
    finalize = commands.add_parser("finalize")
    finalize.add_argument("--unsigned-authorization-file", type=Path, required=True)
    finalize.add_argument("--signature-file", type=Path, required=True)
    finalize.add_argument("--output-file", type=Path, required=True)
    execute = commands.add_parser("execute")
    execute.add_argument("--authorization-file", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run one explicit command phase and return a bounded process status."""
    try:
        args = _parser().parse_args(argv)
        if args.command == "prepare-reviewed-successor":
            prepare_reviewed_successor(
                document_id=args.document_id,
                output_directory=args.output_directory,
                approved_at=args.approved_at,
                effective_from=args.effective_from,
                human_authority_representation=args.human_authority_representation,
                provenance_reference=args.provenance_reference,
            )
        elif args.command == "finalize":
            finalize_authorization(args.unsigned_authorization_file, args.signature_file, args.output_file)
        else:
            execute_authorization(args.authorization_file)
        return 0
    except LegalCorpusApprovalOperatorCommandError as error:
        print(f"ERROR={error.code}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "APPROVED_VERSION",
    "APPROVAL_TRUSTED_KEY_ID",
    "AUTHORIZATION_LIFETIME",
    "LegalCorpusApprovalOperatorCommandError",
    "REVIEWED_SUCCESSOR_APPROVED_VERSION",
    "REVIEWED_SUCCESSOR_DOCUMENT_IDS",
    "REVIEWED_SUCCESSOR_SOURCE_VERSION",
    "VERSION",
    "execute_authorization",
    "finalize_authorization",
    "main",
    "prepare_reviewed_successor",
]


# ARTIFACT: legal_corpus_approval_operator_command.py
# VERSION: v1.1.0-R1D-B0F-R9B-P7-A3-LEGAL-CORPUS-APPROVAL-OPERATOR-COMMAND
# AUTHORITY BOUNDARY: public ceremony adapter; verified proof only at execution
# TENANT POSTURE: PLATFORM corpus; no tenant or principal acceptance authority
# FAIL-CLOSED POSTURE: canonical source, trust, signature, and result checks reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
