"""Canonical operator command for one governed legal-corpus draft admission.

TITLE: WILSY OS Legal Corpus Operator Command
VERSION: v1.1.0-R9B-P7-A2-R1-LEGAL-CORPUS-OPERATOR-COMMAND
AUTHORITY: Wilsy OS Core Governance
EPITOME: Consumes one externally signed public D1 authorization and owns the
         session, transaction, retry, commit, and unknown-commit boundaries for
         one server-owned Institutional Charter DRAFT admission.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/legal_corpus_operator_command.py
COLLABORATION / OWNERSHIP: D1 authenticates the public signed envelope, C1
                           supplies the source-owned public trust root, R8D
                           supplies immutable evidence, R8H composes the two
                           staged writes, and this command owns Mongo lifecycle
                           and durability classification.
CERTIFICATION / UPDATE DATE: 2026-09-18
CHANGELOG: v1.1.0-R9B-P7-A2-R1 generalizes the command's canonical readback and
           CLI description to every closed platform draft while retaining its
           transaction-owner and fail-closed durability boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only a public signed authorization file path is
                            accepted. Private keys, passphrases, caller trust,
                            caller document truth, and raw envelope contents
                            never enter the command boundary or output.
TENANT BOUNDARY: PLATFORM scope only; no tenant or principal authority.
AUTHORITY BOUNDARY: Consumes already-issued D1 authority and derives R8D only
                    after D1 verification. This command does not sign, issue,
                    approve, review, accept, or authenticate a human operator.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
TRANSACTION BOUNDARY: This command owns sessions, transactions, commit,
                      abort, whole-transaction retry, and uncertain-commit
                      reconciliation. R8H remains caller-neutral and receives
                      one active session only.
FAIL-CLOSED POSTURE: Unknown commit, unavailable readback, partial durability,
                     divergence, unlabelled failures, and retry exhaustion do
                     not become success.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Final, Mapping

from tools.eos.kernel import db as kernel_db
from tools.eos.legal_operations.domain.legal_corpus_operator_authorization import (
    LegalCorpusOperatorAuthorization,
    LegalCorpusOperatorAuthorizationError,
    resolve_canonical_legal_corpus_document,
)
from tools.eos.legal_operations.domain.legal_corpus_operator_trust_root import (
    LegalCorpusOperatorTrustRoot,
    LegalCorpusOperatorTrustRootError,
)
from tools.eos.legal_operations.registry.legal_corpus_provisioning_authority_registry import (
    COLLECTION as AUTHORITY_COLLECTION,
    LegalCorpusProvisioningAuthorityRegistry,
)
from tools.eos.legal_operations.registry.legal_document_registry import (
    COLLECTION as DOCUMENT_COLLECTION,
    LegalDocumentRegistry,
)
from tools.eos.legal_operations.service.legal_corpus_provisioning_service import (
    LegalCorpusProvisioningResult,
    LegalCorpusProvisioningResultState,
    LegalCorpusProvisioningService,
    LegalCorpusProvisioningServiceError,
)


VERSION: Final[str] = "v1.1.0-R9B-P7-A2-R1-LEGAL-CORPUS-OPERATOR-COMMAND"
SCHEMA: Final[str] = "WILSY-LEGAL-CORPUS-OPERATOR-COMMAND-RESULT/V1"
TRANSACTION_ATTEMPT_LIMIT: Final[int] = 3
TRANSACTION_RETRY_LIMIT: Final[int] = 2
TRANSACTION_RETRY_BACKOFF_POLICY: Final[str] = "NONE"
TRANSIENT_TRANSACTION_ERROR: Final[str] = "TransientTransactionError"
UNKNOWN_TRANSACTION_COMMIT_RESULT: Final[str] = "UnknownTransactionCommitResult"


class _AuthorityGateFailure(RuntimeError):
    """Internal bounded failure for a fresh transaction authority gate."""

    def __init__(self, code: str, result: str) -> None:
        self.code = code
        self.result = result
        super().__init__(code)


class _TransientAttempt(RuntimeError):
    """Internal marker for a labelled whole-transaction retry."""

    def __init__(self, cause: BaseException) -> None:
        self.cause = cause
        super().__init__("TRANSIENT_TRANSACTION_ERROR")


class _UnknownCommit(RuntimeError):
    """Internal marker for a commit whose outcome must be read back."""

    def __init__(self, cause: BaseException) -> None:
        self.cause = cause
        super().__init__("UNKNOWN_TRANSACTION_COMMIT_RESULT")


@dataclass(frozen=True, slots=True)
class _Readback:
    """Non-secret classification of the two durable registry observations."""

    state: str
    document: Any = None
    evidence: Any = None


def _utc_now() -> datetime:
    """Return the private transaction-authority clock in UTC."""
    return datetime.now(timezone.utc)


def _has_error_label(error: BaseException, label: str) -> bool:
    """Inspect driver labels and bounded causal context without exposing data."""
    current: BaseException | None = error
    visited: set[int] = set()
    for _ in range(8):
        if current is None or id(current) in visited:
            return False
        visited.add(id(current))
        has_label = getattr(current, "has_error_label", None)
        if callable(has_label):
            try:
                if bool(has_label(label)):
                    return True
            except Exception:
                return False
        current = current.__cause__
    return False


def _safe_abort(session: Any) -> None:
    """Abort only an active caller-visible transaction during failure cleanup."""
    if getattr(session, "in_transaction", False) is True:
        session.abort_transaction()


def _json_line(payload: Mapping[str, object]) -> str:
    """Serialize bounded command output deterministically and compactly."""
    return json.dumps(dict(payload), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _base_payload(
    *,
    result: str,
    durability: str,
    attempts: int,
    authorization: LegalCorpusOperatorAuthorization | None = None,
    evidence: Any = None,
) -> dict[str, object]:
    """Build redacted output without serializing a signed envelope or error text."""
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "command_version": VERSION,
        "result": result,
        "durability_classification": durability,
        "transaction_attempts": attempts,
    }
    if authorization is not None:
        payload.update(
            {
                "authorization_id": authorization.authorization_id,
                "idempotency_key": authorization.idempotency_key,
                "key_id": authorization.key_id,
            }
        )
    if evidence is not None:
        payload.update(
            {
                "authority_evidence_id": evidence.authority_evidence_id,
                "authority_evidence_fingerprint": evidence.evidence_fingerprint,
                "document_id": evidence.source_document_id,
                "document_version": evidence.source_version,
                "document_sha3_512": evidence.source_sha3_512,
            }
        )
    return payload


def _load_authorization(path: Path) -> LegalCorpusOperatorAuthorization:
    """Read one UTF-8 JSON object and hydrate it through canonical D1 only."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise _AuthorityGateFailure("AUTHORIZATION_FILE_INVALID", "AUTHORIZATION_INVALID") from error
    if not isinstance(raw, dict):
        raise _AuthorityGateFailure("AUTHORIZATION_JSON_OBJECT_REQUIRED", "AUTHORIZATION_INVALID")
    try:
        return LegalCorpusOperatorAuthorization.from_document(raw)
    except LegalCorpusOperatorAuthorizationError as error:
        raise _AuthorityGateFailure(getattr(error, "code", "AUTHORIZATION_INVALID"), "AUTHORIZATION_INVALID") from error


def _initial_authority(authorization: LegalCorpusOperatorAuthorization) -> Any:
    """Verify D1 and derive R8D before any database bootstrap or connection."""
    try:
        authorization.verify()
        return authorization.derive_provisioning_authority_evidence()
    except LegalCorpusOperatorAuthorizationError as error:
        raise _AuthorityGateFailure(getattr(error, "code", "AUTHORIZATION_INVALID"), "AUTHORIZATION_INVALID") from error


def _attempt_authority(
    authorization: LegalCorpusOperatorAuthorization,
    transaction_start_at: datetime,
) -> Any:
    """Reverify D1, C1 validity, the signed window, and rederive R8D once."""
    try:
        trusted_key = authorization.verify()
        trusted_key = LegalCorpusOperatorTrustRoot.resolve(authorization.key_id)
    except (LegalCorpusOperatorAuthorizationError, LegalCorpusOperatorTrustRootError) as error:
        code = getattr(error, "code", "AUTHORIZATION_INVALID")
        result = "NEW_KEY_CEREMONY_AND_ADMISSION_REQUIRED" if "KEY" in code or "TRUSTED" in code else "NEW_AUTHORIZATION_REQUIRED"
        raise _AuthorityGateFailure(code, result) from error
    if not trusted_key.can_verify_at(authorization.operation.value, transaction_start_at):
        raise _AuthorityGateFailure("TRUSTED_KEY_NOT_VALID_AT_TRANSACTION_START", "NEW_KEY_CEREMONY_AND_ADMISSION_REQUIRED")
    if not authorization.not_before <= transaction_start_at <= authorization.expires_at:
        raise _AuthorityGateFailure("AUTHORIZATION_NOT_VALID_AT_TRANSACTION_START", "NEW_AUTHORIZATION_REQUIRED")
    try:
        return authorization.derive_provisioning_authority_evidence()
    except LegalCorpusOperatorAuthorizationError as error:
        code = getattr(error, "code", "AUTHORIZATION_INVALID")
        result = "NEW_KEY_CEREMONY_AND_ADMISSION_REQUIRED" if "KEY" in code or "TRUSTED" in code else "NEW_AUTHORIZATION_REQUIRED"
        raise _AuthorityGateFailure(code, result) from error


def _connect_and_prepare() -> tuple[Any, Any, Any, Any]:
    """Connect through Kernel DB and ensure both indexes before any transaction."""
    try:
        connected = kernel_db.connect_db()
        if not isinstance(connected, tuple) or not connected or connected[0] is not True:
            raise RuntimeError("DATABASE_CONNECTION_UNAVAILABLE")
        client = kernel_db.get_client()
        database = kernel_db.get_database()
        if client is None or database is None:
            raise RuntimeError("DATABASE_HANDLE_UNAVAILABLE")
        document_collection = database[DOCUMENT_COLLECTION]
        authority_collection = database[AUTHORITY_COLLECTION]
        LegalDocumentRegistry.ensure_indexes(document_collection)
        LegalCorpusProvisioningAuthorityRegistry.ensure_indexes(authority_collection)
        return client, database, document_collection, authority_collection
    except Exception as error:
        raise RuntimeError("DATABASE_OR_INDEX_READINESS_FAILED") from error


def _service_failure(
    error: LegalCorpusProvisioningServiceError,
    *,
    attempts: int,
    authorization: LegalCorpusOperatorAuthorization,
    evidence: Any,
) -> tuple[dict[str, object], int]:
    """Map bounded R8H errors without flattening their internal cause."""
    code = getattr(error, "code", "LEGAL_CORPUS_PROVISIONING_FAILED")
    if code == "LEGAL_CORPUS_PROVISIONING_AUTHORITY_MISMATCH":
        result, exit_code = "AUTHORITY_REJECTED", 2
    elif "PARTIAL" in code or "DIVERGENCE" in code:
        result, exit_code = "FAIL_CLOSED_DURABILITY", 5
    else:
        result, exit_code = "PROVISIONING_TRANSACTION_FAILED", 3
    payload = _base_payload(
        result=result,
        durability="NOT_CONFIRMED",
        attempts=attempts,
        authorization=authorization,
        evidence=evidence,
    )
    payload["error_code"] = code
    return payload, exit_code


def _run_transaction_attempt(
    *,
    client: Any,
    service: LegalCorpusProvisioningService,
    authorization: LegalCorpusOperatorAuthorization,
    attempt: int,
) -> tuple[dict[str, object], int]:
    """Execute one fresh authority-gated transaction and known commit."""
    with client.start_session() as session:
        transaction_start_at = _utc_now()
        evidence = _attempt_authority(authorization, transaction_start_at)
        session.start_transaction()
        try:
            staged = service.admit_draft(evidence, session=session)
        except Exception as error:
            try:
                _safe_abort(session)
            except Exception as abort_error:
                raise RuntimeError("TRANSACTION_ABORT_FAILED") from abort_error
            if _has_error_label(error, TRANSIENT_TRANSACTION_ERROR):
                raise _TransientAttempt(error) from error
            if isinstance(error, LegalCorpusProvisioningServiceError):
                return _service_failure(error, attempts=attempt, authorization=authorization, evidence=evidence)
            raise RuntimeError("PROVISIONING_TRANSACTION_FAILED") from error
        try:
            session.commit_transaction()
        except Exception as error:
            if _has_error_label(error, UNKNOWN_TRANSACTION_COMMIT_RESULT):
                raise _UnknownCommit(error) from error
            try:
                _safe_abort(session)
            except Exception as abort_error:
                raise RuntimeError("TRANSACTION_ABORT_FAILED") from abort_error
            if _has_error_label(error, TRANSIENT_TRANSACTION_ERROR):
                raise _TransientAttempt(error) from error
            raise RuntimeError("COMMIT_OUTCOME_UNAVAILABLE") from error
        if not isinstance(staged, LegalCorpusProvisioningResult):
            raise RuntimeError("PROVISIONING_RESULT_INVALID")
        if staged.state is LegalCorpusProvisioningResultState.EXACT_REPLAY:
            result = "DURABLE_ADMISSION_ALREADY_PRESENT"
            durability = "EXACT_REPLAY"
        else:
            result = "DURABLE_ADMISSION_CREATED"
            durability = "CONFIRMED_COMMIT"
        payload = _base_payload(
            result=result,
            durability=durability,
            attempts=attempt,
            authorization=authorization,
            evidence=evidence,
        )
        payload.update(
            {
                "document_id": staged.document_id,
                "document_version": staged.document_version,
                "document_sha3_512": staged.document_sha3_512,
                "authority_evidence_id": staged.authority_evidence_id,
            }
        )
        return payload, 0


def _readback(client: Any, database: Any, authorization: LegalCorpusOperatorAuthorization, evidence: Any) -> _Readback:
    """Read both canonical durable sides in a fresh nontransactional context."""
    try:
        canonical = resolve_canonical_legal_corpus_document(
            evidence.source_document_id,
            evidence.source_version,
        )
        with client.start_session() as session:
            document = LegalDocumentRegistry.get(
                canonical.document_id,
                canonical.version,
                database[DOCUMENT_COLLECTION],
                session=session,
            )
            persisted_evidence = LegalCorpusProvisioningAuthorityRegistry.get_by_source(
                canonical.document_id,
                canonical.version,
                database[AUTHORITY_COLLECTION],
                session=session,
            )
        if document is None and persisted_evidence is None:
            return _Readback("BOTH_ABSENT")
        if document is None:
            return _Readback("EVIDENCE_ONLY", evidence=persisted_evidence)
        if persisted_evidence is None:
            return _Readback("DOCUMENT_ONLY", document=document)
        if document.to_document() != canonical.to_document():
            return _Readback("DIVERGENT", document=document, evidence=persisted_evidence)
        if persisted_evidence.to_document() != evidence.to_document():
            return _Readback("DIVERGENT", document=document, evidence=persisted_evidence)
        persisted_evidence.verify_against(canonical)
        return _Readback("BOTH_EXACT", document=document, evidence=persisted_evidence)
    except Exception:
        return _Readback("READBACK_UNAVAILABLE")


def _unknown_commit_outcome(
    *,
    client: Any,
    database: Any,
    authorization: LegalCorpusOperatorAuthorization,
    evidence: Any,
    attempt: int,
) -> tuple[dict[str, object] | None, int | None]:
    """Classify uncertain commit without inferring success."""
    observed = _readback(client, database, authorization, evidence)
    if observed.state == "BOTH_EXACT":
        return (
            _base_payload(
                result="DURABLE_ADMISSION_RECOGNIZED",
                durability="UNKNOWN_COMMIT_RECONCILED_EXACT",
                attempts=attempt,
                authorization=authorization,
                evidence=evidence,
            ),
            0,
        )
    if observed.state == "BOTH_ABSENT":
        return None, None
    if observed.state == "DOCUMENT_ONLY":
        result, durability = "FAIL_CLOSED_PARTIAL_DURABILITY", "DOCUMENT_ONLY"
    elif observed.state == "EVIDENCE_ONLY":
        result, durability = "FAIL_CLOSED_PARTIAL_DURABILITY", "EVIDENCE_ONLY"
    elif observed.state == "DIVERGENT":
        result, durability = "FAIL_CLOSED_DIVERGENT_DURABILITY", "DIVERGENT"
    else:
        result, durability = "INDETERMINATE_COMMIT", "READBACK_UNAVAILABLE"
    return (
        _base_payload(
            result=result,
            durability=durability,
            attempts=attempt,
            authorization=authorization,
            evidence=evidence,
        ),
        5,
    )


def run_command(authorization_path: Path, *, dry_run: bool = False) -> tuple[dict[str, object], int]:
    """Run the governed command with one public authorization file.

    The caller supplies only a filesystem path and an optional dry-run flag;
    no document, hash, trust root, R8D, clock, URI, or database name is an
    authority input. A zero exit means dry-run validation, known commit, exact
    replay, or exact unknown-commit readback. No other state is success.
    """
    try:
        authorization = _load_authorization(authorization_path)
        initial_evidence = _initial_authority(authorization)
    except _AuthorityGateFailure as error:
        payload = _base_payload(result=error.result, durability="NOT_ATTEMPTED", attempts=0)
        payload["error_code"] = error.code
        return payload, 2
    if dry_run:
        return (
            _base_payload(
                result="DRY_RUN_AUTHORITY_VALIDATED",
                durability="NOT_ATTEMPTED",
                attempts=0,
                authorization=authorization,
                evidence=initial_evidence,
            ),
            0,
        )
    try:
        client, database, document_collection, authority_collection = _connect_and_prepare()
        service = LegalCorpusProvisioningService(document_collection, authority_collection)
    except Exception as error:
        payload = _base_payload(
            result="DATABASE_READINESS_FAILED",
            durability="NOT_ATTEMPTED",
            attempts=0,
            authorization=authorization,
            evidence=initial_evidence,
        )
        payload["error_code"] = "DATABASE_OR_INDEX_READINESS_FAILED"
        return payload, 3

    attempt = 1
    while attempt <= TRANSACTION_ATTEMPT_LIMIT:
        try:
            return _run_transaction_attempt(
                client=client,
                service=service,
                authorization=authorization,
                attempt=attempt,
            )
        except _AuthorityGateFailure as error:
            payload = _base_payload(
                result=error.result,
                durability="NOT_ATTEMPTED",
                attempts=attempt,
                authorization=authorization,
            )
            payload["error_code"] = error.code
            return payload, 2
        except _TransientAttempt:
            if attempt >= TRANSACTION_ATTEMPT_LIMIT:
                payload = _base_payload(
                    result="TRANSIENT_RETRY_EXHAUSTED",
                    durability="NOT_CONFIRMED",
                    attempts=attempt,
                    authorization=authorization,
                    evidence=initial_evidence,
                )
                payload["error_code"] = "TRANSIENT_RETRY_EXHAUSTED"
                return payload, 4
            attempt += 1
        except _UnknownCommit as unknown:
            del unknown
            outcome, exit_code = _unknown_commit_outcome(
                client=client,
                database=database,
                authorization=authorization,
                evidence=initial_evidence,
                attempt=attempt,
            )
            if outcome is not None and exit_code is not None:
                return outcome, exit_code
            if attempt >= TRANSACTION_ATTEMPT_LIMIT:
                payload = _base_payload(
                    result="INDETERMINATE_COMMIT",
                    durability="BOTH_ABSENT_NO_RETRY_BUDGET",
                    attempts=attempt,
                    authorization=authorization,
                    evidence=initial_evidence,
                )
                payload["error_code"] = "INDETERMINATE_COMMIT"
                return payload, 5
            attempt += 1
        except Exception:
            payload = _base_payload(
                result="COMMAND_EXECUTION_FAILED",
                durability="NOT_CONFIRMED",
                attempts=attempt,
                authorization=authorization,
                evidence=initial_evidence,
            )
            payload["error_code"] = "COMMAND_EXECUTION_FAILED"
            return payload, 5
    payload = _base_payload(
        result="INDETERMINATE_COMMIT",
        durability="NOT_CONFIRMED",
        attempts=TRANSACTION_ATTEMPT_LIMIT,
        authorization=authorization,
        evidence=initial_evidence,
    )
    payload["error_code"] = "INDETERMINATE_COMMIT"
    return payload, 5


def _parser() -> argparse.ArgumentParser:
    """Build the restricted operator CLI parser."""
    parser = argparse.ArgumentParser(
        prog="legal_corpus_operator_command",
        description="Admit one server-owned platform legal-corpus DRAFT from one signed public authorization.",
        allow_abbrev=False,
    )
    parser.add_argument("--authorization-file", required=True, type=Path, metavar="PATH")
    parser.add_argument("--dry-run", action="store_true", help="Validate authority without Mongo or writes.")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Execute the restricted CLI and emit one deterministic JSON result line."""
    args = _parser().parse_args(argv)
    payload, exit_code = run_command(args.authorization_file, dry_run=args.dry_run)
    print(_json_line(payload))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["SCHEMA", "TRANSACTION_ATTEMPT_LIMIT", "TRANSACTION_RETRY_LIMIT", "VERSION", "main", "run_command"]


# ARTIFACT: legal_corpus_operator_command.py
# VERSION: v1.1.0-R9B-P7-A2-R1-LEGAL-CORPUS-OPERATOR-COMMAND
# AUTHORITY BOUNDARY: consumes externally signed PLATFORM D1 authority only
# TENANT POSTURE: no tenant or principal authority; canonical corpus is platform-scoped
# FAIL-CLOSED POSTURE: no unknown commit, partial state, divergence, or retry exhaustion is success
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
