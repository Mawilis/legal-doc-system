"""Caller-owned transaction operator for legal-corpus approval promotion.

TITLE: WILSY OS Legal Corpus Approval Transaction Operator
VERSION: v1.0.0-R1D-B0F-R9B-P4-P3-LEGAL-CORPUS-APPROVAL-OPERATOR
AUTHORITY: Wilsy OS Core Governance
EPITOME: Owns the Mongo session, transaction, bounded whole-transaction retry,
         and unknown-commit reconciliation around the closed approval service.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_corpus_approval_operator.py
COLLABORATION / OWNERSHIP: The verified-authorization domain owns trust and
                            signature verification. The approval service owns
                            source-bound pair composition. The registries own
                            persistence. This operator alone owns transaction
                            lifecycle and durability classification.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.0.0-R9B-P4-P3 establishes frozen operator outcomes, three-attempt
           labelled retry, and fresh two-sided unknown-commit readback.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only an already-verified immutable proof is
                            accepted. No secret, request context, raw driver
                            state, or caller document truth is serialized.
TENANT BOUNDARY: PLATFORM approval corpus only; no tenant or principal scope.
AUTHORITY BOUNDARY: Execution semantics only. This module never verifies,
                    signs, issues, reviews, accepts, or approves authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Ambiguous, partial, divergent, split, unlabelled, and
                     exhausted outcomes never become durable success.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Final, Type

from tools.eos.kernel import db as kernel_db
from tools.eos.legal_operations.domain.legal_corpus_approval_authorization import (
    VerifiedLegalCorpusApprovalAuthorization,
)
from tools.eos.legal_operations.registry.legal_corpus_approval_registry import (
    COLLECTION as APPROVAL_COLLECTION,
    LegalCorpusApprovalAdmissionResult,
    LegalCorpusApprovalAdmissionState,
    LegalCorpusApprovalPreflightState,
    LegalCorpusApprovalRegistry,
)
from tools.eos.legal_operations.registry.legal_document_registry import (
    COLLECTION as DOCUMENT_COLLECTION,
    LegalDocumentRegistry,
)
from tools.eos.legal_operations.service.legal_corpus_approval_service import (
    LegalCorpusApprovalResult,
    LegalCorpusApprovalResultState,
    LegalCorpusApprovalService,
)


VERSION: Final[str] = "v1.0.0-R1D-B0F-R9B-P4-P3-LEGAL-CORPUS-APPROVAL-OPERATOR"
MAX_TOTAL_TRANSACTION_ATTEMPTS: Final[int] = 3
MAX_TRANSACTION_RETRIES: Final[int] = 2
TRANSIENT_TRANSACTION_ERROR: Final[str] = "TransientTransactionError"
UNKNOWN_TRANSACTION_COMMIT_RESULT: Final[str] = "UnknownTransactionCommitResult"


class LegalCorpusApprovalOperatorError(RuntimeError):
    """Bounded non-sensitive operator failure with preserved cause."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalCorpusApprovalOperatorResultState(StrEnum):
    """Durability outcomes emitted only after known or reconciled commit."""

    COMMITTED_CREATED = "COMMITTED_CREATED"
    COMMITTED_EXACT_REPLAY = "COMMITTED_EXACT_REPLAY"
    RECONCILED_AFTER_UNKNOWN_COMMIT = "RECONCILED_AFTER_UNKNOWN_COMMIT"


@dataclass(frozen=True, slots=True)
class LegalCorpusApprovalOperatorResult:
    """Immutable operator receipt with no mutable session or driver state."""

    state: LegalCorpusApprovalOperatorResultState
    attempts: int
    service_result: LegalCorpusApprovalResult


@dataclass(frozen=True, slots=True)
class _Readback:
    """Fresh durable pair classification after an ambiguous commit."""

    state: str
    approval_result: LegalCorpusApprovalAdmissionResult | None = None


class _RetryAttempt(RuntimeError):
    """Internal marker for a labelled whole-transaction retry."""

    def __init__(self, cause: BaseException) -> None:
        self.cause = cause
        super().__init__("TRANSIENT_TRANSACTION_ERROR")


class _UnknownCommit(RuntimeError):
    """Internal marker for a commit whose result requires fresh readback."""

    def __init__(self, cause: BaseException) -> None:
        self.cause = cause
        super().__init__("UNKNOWN_TRANSACTION_COMMIT_RESULT")


def _has_error_label(error: BaseException, label: str) -> bool:
    """Inspect bounded driver causal context without exposing error text."""
    current: BaseException | None = error
    visited: set[int] = set()
    for _ in range(8):
        if current is None or id(current) in visited:
            return False
        visited.add(id(current))
        checker = getattr(current, "has_error_label", None)
        if callable(checker):
            try:
                if bool(checker(label)):
                    return True
            except Exception:
                return False
        current = current.__cause__
    return False


def _abort_if_active(session: Any) -> None:
    """Abort only an active transaction; lifecycle remains operator-owned."""
    if getattr(session, "in_transaction", False) is True:
        session.abort_transaction()


class LegalCorpusApprovalOperator:
    """Execute one verified approval through a caller-owned Mongo transaction.

    ``client``, ``database``, ``service``, and registry classes are optional
    deterministic seams for direct certificates. Production execution resolves
    the canonical Kernel DB lazily, so importing or constructing this class is
    side-effect free. The operator never receives raw document or authority
    fields and never invokes verification or signing APIs.
    """

    def __init__(
        self,
        *,
        client: Any = None,
        database: Any = None,
        service: LegalCorpusApprovalService | None = None,
        document_registry: Type[LegalDocumentRegistry] = LegalDocumentRegistry,
        approval_registry: Type[LegalCorpusApprovalRegistry] = LegalCorpusApprovalRegistry,
    ) -> None:
        """Wire lifecycle dependencies without opening a client or session."""
        self.client = client
        self.database = database
        self.service = service
        self.document_registry = document_registry
        self.approval_registry = approval_registry

    def _runtime(self) -> tuple[Any, Any, LegalCorpusApprovalService]:
        """Resolve canonical Kernel DB handles and the closed service lazily."""
        client = self.client
        database = self.database
        if client is None or database is None:
            connected = kernel_db.connect_db()
            if not isinstance(connected, tuple) or not connected or connected[0] is not True:
                raise LegalCorpusApprovalOperatorError("DATABASE_CONNECTION_UNAVAILABLE")
            client = kernel_db.get_client()
            database = kernel_db.get_database()
        if client is None or database is None:
            raise LegalCorpusApprovalOperatorError("DATABASE_HANDLE_UNAVAILABLE")
        service = self.service
        if service is None:
            service = LegalCorpusApprovalService(
                document_collection=database[DOCUMENT_COLLECTION],
                approval_collection=database[APPROVAL_COLLECTION],
                document_registry=self.document_registry,
                approval_registry=self.approval_registry,
            )
        return client, database, service

    @staticmethod
    def _validate_staged(value: Any) -> LegalCorpusApprovalResult:
        """Accept only the closed immutable service result contract."""
        if not isinstance(value, LegalCorpusApprovalResult):
            raise LegalCorpusApprovalOperatorError("SERVICE_RESULT_INVALID")
        if value.state not in (
            LegalCorpusApprovalResultState.CREATED,
            LegalCorpusApprovalResultState.EXACT_REPLAY,
        ):
            raise LegalCorpusApprovalOperatorError("SERVICE_RESULT_STATE_INVALID")
        return value

    def _fresh_readback(
        self,
        client: Any,
        database: Any,
        proof: VerifiedLegalCorpusApprovalAuthorization,
    ) -> _Readback:
        """Read target and evidence with a fresh session after unknown commit."""
        try:
            with client.start_session() as session:
                target = self.document_registry.get(
                    proof.approval_evidence.approved_document_id,
                    proof.approval_evidence.approved_version,
                    database[DOCUMENT_COLLECTION],
                    session=session,
                )
                preflight = self.approval_registry.preflight_verified_approval(
                    proof,
                    database[APPROVAL_COLLECTION],
                    session=session,
                )
        except Exception as error:
            raise LegalCorpusApprovalOperatorError("UNKNOWN_COMMIT_READBACK_FAILED") from error
        if target is None and preflight.state is LegalCorpusApprovalPreflightState.ABSENT:
            return _Readback("BOTH_ABSENT")
        if target is None:
            return _Readback("SPLIT_OR_INVALID")
        if target != proof.approval_evidence.approved_document:
            return _Readback("DIVERGENT")
        if preflight.state is not LegalCorpusApprovalPreflightState.EXACT:
            return _Readback("SPLIT_OR_INVALID")
        record = preflight.matched_record
        if record is None or record.authorization.to_document() != proof.authorization.to_document():
            return _Readback("DIVERGENT")
        return _Readback(
            "BOTH_EXACT",
            LegalCorpusApprovalAdmissionResult(
                LegalCorpusApprovalAdmissionState.EXACT_REPLAY,
                record,
            ),
        )

    def _attempt(
        self,
        client: Any,
        service: LegalCorpusApprovalService,
        proof: VerifiedLegalCorpusApprovalAuthorization,
    ) -> LegalCorpusApprovalResult:
        """Run exactly one fresh transaction attempt."""
        with client.start_session() as session:
            session.start_transaction()
            try:
                staged = self._validate_staged(service.admit(proof, session=session))
            except Exception as error:
                try:
                    _abort_if_active(session)
                except Exception as abort_error:
                    raise LegalCorpusApprovalOperatorError("TRANSACTION_ABORT_FAILED") from abort_error
                if _has_error_label(error, TRANSIENT_TRANSACTION_ERROR):
                    raise _RetryAttempt(error) from error
                raise LegalCorpusApprovalOperatorError("APPROVAL_SERVICE_FAILED") from error
            try:
                session.commit_transaction()
            except Exception as error:
                if _has_error_label(error, UNKNOWN_TRANSACTION_COMMIT_RESULT):
                    raise _UnknownCommit(error) from error
                try:
                    _abort_if_active(session)
                except Exception as abort_error:
                    raise LegalCorpusApprovalOperatorError("TRANSACTION_ABORT_FAILED") from abort_error
                if _has_error_label(error, TRANSIENT_TRANSACTION_ERROR):
                    raise _RetryAttempt(error) from error
                raise LegalCorpusApprovalOperatorError("COMMIT_FAILED") from error
            return staged

    def execute(self, proof: VerifiedLegalCorpusApprovalAuthorization) -> LegalCorpusApprovalOperatorResult:
        """Commit or reconcile one verified approval with at most three attempts.

        A service ``CREATED`` result is returned only after commit succeeds.
        Unknown commit outcomes use a new read session and accept only an exact
        durable target/evidence pair; no network or service result is inferred.
        """
        if not isinstance(proof, VerifiedLegalCorpusApprovalAuthorization):
            raise LegalCorpusApprovalOperatorError("VERIFIED_PROOF_REQUIRED")
        client, database, service = self._runtime()
        attempt = 1
        while attempt <= MAX_TOTAL_TRANSACTION_ATTEMPTS:
            try:
                result = self._attempt(client, service, proof)
                state = (
                    LegalCorpusApprovalOperatorResultState.COMMITTED_CREATED
                    if result.state is LegalCorpusApprovalResultState.CREATED
                    else LegalCorpusApprovalOperatorResultState.COMMITTED_EXACT_REPLAY
                )
                return LegalCorpusApprovalOperatorResult(state, attempt, result)
            except _RetryAttempt as retry:
                if attempt >= MAX_TOTAL_TRANSACTION_ATTEMPTS:
                    raise LegalCorpusApprovalOperatorError("TRANSIENT_RETRY_EXHAUSTED") from retry.cause
                attempt += 1
            except _UnknownCommit as unknown:
                observed = self._fresh_readback(client, database, proof)
                if observed.state == "BOTH_EXACT":
                    if observed.approval_result is None:
                        raise LegalCorpusApprovalOperatorError("UNKNOWN_COMMIT_READBACK_INVALID") from unknown.cause
                    return LegalCorpusApprovalOperatorResult(
                        LegalCorpusApprovalOperatorResultState.RECONCILED_AFTER_UNKNOWN_COMMIT,
                        attempt,
                        LegalCorpusApprovalResult(
                            LegalCorpusApprovalResultState.EXACT_REPLAY,
                            proof.approval_evidence.approved_document,
                            observed.approval_result,
                        ),
                    )
                if observed.state == "BOTH_ABSENT":
                    if attempt >= MAX_TOTAL_TRANSACTION_ATTEMPTS:
                        raise LegalCorpusApprovalOperatorError("UNKNOWN_COMMIT_RETRY_EXHAUSTED") from unknown.cause
                    attempt += 1
                    continue
                code = {
                    "DIVERGENT": "UNKNOWN_COMMIT_DIVERGENT",
                    "SPLIT_OR_INVALID": "UNKNOWN_COMMIT_SPLIT_OR_PARTIAL",
                }.get(observed.state, "UNKNOWN_COMMIT_READBACK_FAILED")
                raise LegalCorpusApprovalOperatorError(code) from unknown.cause
            except LegalCorpusApprovalOperatorError:
                raise
            except Exception as error:
                raise LegalCorpusApprovalOperatorError("APPROVAL_OPERATOR_FAILED") from error
        raise LegalCorpusApprovalOperatorError("TRANSACTION_ATTEMPT_BUDGET_EXHAUSTED")

    def admit(self, proof: VerifiedLegalCorpusApprovalAuthorization) -> LegalCorpusApprovalOperatorResult:
        """Compatibility alias for ``execute``; no second authority surface."""
        return self.execute(proof)


__all__ = [
    "APPROVAL_COLLECTION",
    "DOCUMENT_COLLECTION",
    "LegalCorpusApprovalOperator",
    "LegalCorpusApprovalOperatorError",
    "LegalCorpusApprovalOperatorResult",
    "LegalCorpusApprovalOperatorResultState",
    "MAX_TOTAL_TRANSACTION_ATTEMPTS",
    "MAX_TRANSACTION_RETRIES",
    "TRANSIENT_TRANSACTION_ERROR",
    "UNKNOWN_TRANSACTION_COMMIT_RESULT",
    "VERSION",
]


# ARTIFACT: legal_corpus_approval_operator.py
# VERSION: v1.0.0-R1D-B0F-R9B-P4-P3-LEGAL-CORPUS-APPROVAL-OPERATOR
# AUTHORITY BOUNDARY: executes only an already-verified PLATFORM approval proof
# TENANT POSTURE: no tenant/principal acceptance authority
# FAIL-CLOSED POSTURE: labelled retry is bounded; unknown commit requires fresh exact pair readback
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
