"""Caller-owned service for immutable legal-corpus approval promotion.

TITLE: WILSY OS Legal Corpus Approval Service
VERSION: v1.0.0-R1D-B0F-R9B-P4-P1-LEGAL-CORPUS-APPROVAL-SERVICE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Promotes one durable reviewed DRAFT legal-document version to the
         exact APPROVED successor bound by an already-verified approval proof,
         while persisting the proof's immutable approval evidence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_corpus_approval_service.py
COLLABORATION / OWNERSHIP: The approval verifier owns cryptographic trust and
                           signature verification. The document and approval
                           registries own immutable persistence. The caller
                           owns Mongo sessions, transactions, commit/abort,
                           retry, and unknown-commit adjudication.
CERTIFICATION / UPDATE DATE: 2026-09-19
CHANGELOG: v1.0.0 establishes source-bound APPROVED promotion, pair-state
           preflight, exact replay, same-session forwarding, and fail-closed
           race reconciliation without transaction ownership.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Only an already-verified immutable proof is
                            accepted. No request context, secret, key,
                            filesystem, network, or current-role inference is
                            used by this service.
TENANT BOUNDARY: PLATFORM legal-corpus authority only; tenant and principal
                 acceptance remain separate evidence planes.
AUTHORITY BOUNDARY: This service composes an already-authorized approval into
                    durable document/evidence state. It does not issue,
                    verify, review, accept, sign, execute, or settle authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
FAIL-CLOSED POSTURE: Missing source, source/target drift, partial pairs,
                     divergent or split evidence, invalid readback, and write
                     failures reject without compensation or inferred commit.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Final, NoReturn, Type

from tools.eos.legal_operations.domain.legal_acceptance import (
    LegalDocumentStatus,
    LegalDocumentVersion,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_authority import (
    LegalCorpusApprovalAuthorityError,
)
from tools.eos.legal_operations.domain.legal_corpus_approval_authorization import (
    VerifiedLegalCorpusApprovalAuthorization,
)
from tools.eos.legal_operations.registry.legal_corpus_approval_registry import (
    LegalCorpusApprovalAdmissionResult,
    LegalCorpusApprovalAdmissionState,
    LegalCorpusApprovalPreflight,
    LegalCorpusApprovalPreflightState,
    LegalCorpusApprovalRegistry,
    LegalCorpusApprovalRegistryError,
)
from tools.eos.legal_operations.registry.legal_document_registry import (
    LegalDocumentRegistry,
    LegalDocumentRegistryError,
)


VERSION: Final[str] = "v1.0.0-R1D-B0F-R9B-P4-P1-LEGAL-CORPUS-APPROVAL-SERVICE"


class LegalCorpusApprovalServiceError(RuntimeError):
    """Stable, non-sensitive service failure with preserved causal context."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalCorpusApprovalResultState(StrEnum):
    """Truthful service outcomes; neither state claims transaction commit."""

    CREATED = "CREATED"
    EXACT_REPLAY = "EXACT_REPLAY"


@dataclass(frozen=True, slots=True)
class LegalCorpusApprovalResult:
    """Immutable approved-document/evidence result for the caller.

    ``CREATED`` means both insert calls returned successfully inside the
    caller's transaction boundary; it does not claim commit or durable
    success. ``EXACT_REPLAY`` means both durable sides were observed exact.
    """

    state: LegalCorpusApprovalResultState
    approved_document: LegalDocumentVersion
    approval_result: LegalCorpusApprovalAdmissionResult

    @property
    def approval_record(self) -> Any:
        """Return the immutable registry read model carried by the result."""
        return self.approval_result.record

    @property
    def approval_evidence(self) -> Any:
        """Return the immutable evidence bound by the verified proof."""
        return self.approval_result.record.authorization.approval_evidence


@dataclass(frozen=True, slots=True)
class _PairObservation:
    """Internal immutable view of source, target, and approval preflight."""

    source: LegalDocumentVersion
    target: LegalDocumentVersion | None
    approval: LegalCorpusApprovalPreflight


def _service_error(code: str, cause: BaseException | None = None) -> NoReturn:
    """Raise one bounded service error while retaining its cause."""
    error = LegalCorpusApprovalServiceError(code)
    if cause is None:
        raise error
    raise error from cause


def _registry_error_code(error: BaseException) -> str:
    """Read a bounded dependency code without exposing exception internals."""
    code = getattr(error, "code", None)
    return code if isinstance(code, str) and code else str(error)


class LegalCorpusApprovalService:
    """Promote one verified reviewed draft without owning transactions.

    The optional registry and collection arguments are dependency seams for
    deterministic certificates; production callers use the closed registries.
    The only authority-bearing input is a
    ``VerifiedLegalCorpusApprovalAuthorization``. Source and target content
    cannot be supplied separately by a caller.
    """

    def __init__(
        self,
        *,
        document_collection: Any = None,
        approval_collection: Any = None,
        document_registry: Type[LegalDocumentRegistry] = LegalDocumentRegistry,
        approval_registry: Type[LegalCorpusApprovalRegistry] = LegalCorpusApprovalRegistry,
    ) -> None:
        """Wire persistence dependencies without opening clients or sessions."""
        self.document_collection = document_collection
        self.approval_collection = approval_collection
        self.document_registry = document_registry
        self.approval_registry = approval_registry

    def _observe(
        self,
        proof: VerifiedLegalCorpusApprovalAuthorization,
        session: Any,
    ) -> _PairObservation:
        """Read source, target, and evidence preflight before every write."""
        evidence = proof.approval_evidence
        try:
            source = self.document_registry.get(
                evidence.source_document_id,
                evidence.source_version,
                self.document_collection,
                session=session,
            )
        except LegalDocumentRegistryError as error:
            _service_error("LEGAL_CORPUS_APPROVAL_SOURCE_READ_FAILED", error)
        if source is None:
            _service_error("LEGAL_CORPUS_APPROVAL_SOURCE_MISSING")
        if not isinstance(source, LegalDocumentVersion):
            _service_error("LEGAL_CORPUS_APPROVAL_SOURCE_INVALID")
        if source.status is not LegalDocumentStatus.DRAFT_REVIEW_REQUIRED:
            _service_error("LEGAL_CORPUS_APPROVAL_SOURCE_NOT_REVIEWED_DRAFT")
        try:
            evidence.verify_against(source, evidence.approved_document)
        except LegalCorpusApprovalAuthorityError as error:
            _service_error("LEGAL_CORPUS_APPROVAL_SOURCE_BINDING_MISMATCH", error)
        try:
            target = self.document_registry.get(
                evidence.approved_document_id,
                evidence.approved_version,
                self.document_collection,
                session=session,
            )
            approval = self.approval_registry.preflight_verified_approval(
                proof,
                self.approval_collection,
                session=session,
            )
        except LegalDocumentRegistryError as error:
            _service_error("LEGAL_CORPUS_APPROVAL_TARGET_READ_FAILED", error)
        except LegalCorpusApprovalRegistryError as error:
            _service_error("LEGAL_CORPUS_APPROVAL_EVIDENCE_PREFLIGHT_FAILED", error)
        return _PairObservation(source, target, approval)

    @staticmethod
    def _target_is_exact(
        target: LegalDocumentVersion | None,
        proof: VerifiedLegalCorpusApprovalAuthorization,
    ) -> bool:
        """Require exact immutable target equality, including digest/content."""
        return target is not None and target == proof.approval_evidence.approved_document

    def _exact_result(
        self,
        proof: VerifiedLegalCorpusApprovalAuthorization,
        observation: _PairObservation,
    ) -> LegalCorpusApprovalResult:
        """Build exact replay only from two exact durable sides."""
        if not self._target_is_exact(observation.target, proof):
            _service_error("LEGAL_CORPUS_APPROVAL_TARGET_DIVERGENT")
        if observation.approval.state is not LegalCorpusApprovalPreflightState.EXACT:
            _service_error("LEGAL_CORPUS_APPROVAL_EVIDENCE_NOT_EXACT")
        record = observation.approval.matched_record
        if record is None:
            _service_error("LEGAL_CORPUS_APPROVAL_EVIDENCE_INVALID")
        replay = LegalCorpusApprovalAdmissionResult(
            LegalCorpusApprovalAdmissionState.EXACT_REPLAY,
            record,
        )
        return LegalCorpusApprovalResult(
            LegalCorpusApprovalResultState.EXACT_REPLAY,
            proof.approval_evidence.approved_document,
            replay,
        )

    def _classify_before_write(
        self,
        proof: VerifiedLegalCorpusApprovalAuthorization,
        observation: _PairObservation,
    ) -> str:
        """Classify the complete target/evidence pair before mutation."""
        if observation.target is None:
            if observation.approval.state is LegalCorpusApprovalPreflightState.ABSENT:
                return "BOTH_ABSENT"
            if observation.approval.state is LegalCorpusApprovalPreflightState.EXACT:
                return "PARTIAL"
            if observation.approval.state is LegalCorpusApprovalPreflightState.DIVERGENT:
                return "DIVERGENT"
            return "SPLIT_OR_INVALID"
        if observation.target is not None and not self._target_is_exact(observation.target, proof):
            return "DIVERGENT"
        if observation.approval.state is LegalCorpusApprovalPreflightState.EXACT:
            return "BOTH_EXACT"
        if observation.approval.state is LegalCorpusApprovalPreflightState.DIVERGENT:
            return "DIVERGENT"
        if observation.approval.state is not LegalCorpusApprovalPreflightState.ABSENT:
            return "SPLIT_OR_INVALID"
        return "PARTIAL"

    def _reconcile_after_write_error(
        self,
        proof: VerifiedLegalCorpusApprovalAuthorization,
        session: Any,
        original: BaseException,
        failure_code: str,
    ) -> LegalCorpusApprovalResult:
        """Read back the whole pair; only an exact pair may replay."""
        try:
            observation = self._observe(proof, session)
        except LegalCorpusApprovalServiceError as error:
            _service_error(f"{failure_code}_READBACK_FAILED", error)
        if self._classify_before_write(proof, observation) == "BOTH_EXACT":
            return self._exact_result(proof, observation)
        _service_error(f"{failure_code}_RACE_NOT_EXACT", original)

    def admit(
        self,
        proof: VerifiedLegalCorpusApprovalAuthorization,
        *,
        session: Any = None,
    ) -> LegalCorpusApprovalResult:
        """Promote or replay one proof using a caller-owned session.

        The caller must provide the session used by both registries. This
        method never starts, commits, aborts, retries, or infers a transaction.
        """
        if not isinstance(proof, VerifiedLegalCorpusApprovalAuthorization):
            _service_error("LEGAL_CORPUS_APPROVAL_VERIFIED_PROOF_REQUIRED")
        observation = self._observe(proof, session)
        state = self._classify_before_write(proof, observation)
        if state == "BOTH_EXACT":
            return self._exact_result(proof, observation)
        if state == "PARTIAL":
            _service_error("LEGAL_CORPUS_APPROVAL_PARTIAL_STATE")
        if state == "DIVERGENT":
            _service_error("LEGAL_CORPUS_APPROVAL_TARGET_DIVERGENT")
        if state == "SPLIT_OR_INVALID":
            _service_error("LEGAL_CORPUS_APPROVAL_EVIDENCE_SPLIT_OR_INVALID")

        target = proof.approval_evidence.approved_document
        try:
            registered_target = self.document_registry.register(
                target,
                self.document_collection,
                session=session,
            )
        except LegalDocumentRegistryError as error:
            return self._reconcile_after_write_error(
                proof, session, error, "LEGAL_CORPUS_APPROVAL_TARGET_WRITE_FAILED"
            )
        if not isinstance(registered_target, LegalDocumentVersion) or registered_target != target:
            _service_error("LEGAL_CORPUS_APPROVAL_TARGET_WRITE_DIVERGENT")
        try:
            admission = self.approval_registry.admit_verified_approval(
                proof,
                self.approval_collection,
                session=session,
            )
        except LegalCorpusApprovalRegistryError as error:
            return self._reconcile_after_write_error(
                proof, session, error, "LEGAL_CORPUS_APPROVAL_EVIDENCE_WRITE_FAILED"
            )
        if admission.state is LegalCorpusApprovalAdmissionState.EXACT_REPLAY:
            observation = self._observe(proof, session)
            if self._classify_before_write(proof, observation) != "BOTH_EXACT":
                _service_error("LEGAL_CORPUS_APPROVAL_EVIDENCE_RACE_NOT_EXACT")
            return self._exact_result(proof, observation)
        if admission.state is not LegalCorpusApprovalAdmissionState.CREATED:
            _service_error("LEGAL_CORPUS_APPROVAL_ADMISSION_RESULT_INVALID")
        return LegalCorpusApprovalResult(
            LegalCorpusApprovalResultState.CREATED,
            target,
            admission,
        )


__all__ = [
    "LegalCorpusApprovalResult",
    "LegalCorpusApprovalResultState",
    "LegalCorpusApprovalService",
    "LegalCorpusApprovalServiceError",
    "VERSION",
]


# ARTIFACT: legal_corpus_approval_service.py
# VERSION: v1.0.0-R1D-B0F-R9B-P4-P1-LEGAL-CORPUS-APPROVAL-SERVICE
# AUTHORITY BOUNDARY: caller-owned promotion of an already-verified approval
# TENANT POSTURE: PLATFORM corpus only; no tenant/principal acceptance authority
# FAIL-CLOSED POSTURE: source, pair-state, race, and immutable-target checks reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
