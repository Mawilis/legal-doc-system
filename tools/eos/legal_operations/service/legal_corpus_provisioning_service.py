"""Caller-owned service for composing legal-corpus draft admission.

TITLE: WILSY OS Legal Corpus Draft Provisioning Service
VERSION: v1.2.0-R9B-P7-A3-R2-REVIEWED-SUCCESSOR-PROVISIONING-SERVICE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Composes the server-owned draft corpus, immutable document registry,
         and immutable provisioning-authority registry inside one active
         caller-owned Mongo transaction. It never issues authority itself.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_corpus_provisioning_service.py
COLLABORATION / OWNERSHIP: The operator/deployment command supplies already-
                            issued R8D evidence and owns the Mongo session,
                            transaction, commit/abort, retry, and uncertainty
                            adjudication boundaries. R8I will certify this
                            composition service.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.2.0-R9B-P7-A3-R2 resolves R8D evidence through the source-owned
           eleven-value runtime catalog while retaining pair-state, immutable
           admission, and caller-owned transaction boundaries.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Caller payloads cannot supply legal content,
                            status, digest, path, URL, tenant, or approval
                            authority. Only the server-owned corpus is read.
TENANT BOUNDARY: This is PLATFORM-scoped institutional corpus admission; no
                 tenant/principal authority is accepted or inferred.
AUTHORITY BOUNDARY: Accepts already-issued evidence and composes two immutable
                    writes; it does not authenticate, issue, review, approve,
                    accept, sign, execute, or settle anything.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive for financial
                              execution and settlement truth.
TRANSACTION BOUNDARY: An active caller session/transaction is mandatory, but
                      this service never creates, starts, commits, aborts, or
                      retries it. New writes are PENDING_COMMIT until caller
                      commit; whole-operation retry belongs to the caller.
FAIL-CLOSED POSTURE: Missing/inactive transactions, source mismatch, partial
                     durable state, divergence, and write failures reject
                     without compensation or inferred success.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Final

from tools.eos.legal_operations import production_legal_corpus
from tools.eos.legal_operations.domain.legal_corpus_provisioning_authority import (
    LegalCorpusProvisioningAuthorityEvidence,
    LegalCorpusProvisioningAuthorityError,
)
from tools.eos.legal_operations.registry.legal_corpus_provisioning_authority_registry import (
    LegalCorpusProvisioningAuthorityRegistry,
    LegalCorpusProvisioningAuthorityRegistryError,
)
from tools.eos.legal_operations.registry.legal_document_registry import (
    LegalDocumentRegistry,
    LegalDocumentRegistryError,
)


VERSION: Final[str] = "v1.2.0-R9B-P7-A3-R2-REVIEWED-SUCCESSOR-PROVISIONING-SERVICE"


class LegalCorpusProvisioningServiceError(RuntimeError):
    """Stable, non-sensitive service boundary failure with causal context."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalCorpusProvisioningResultState(StrEnum):
    """Truthful outcomes distinguish staged writes from committed replay."""

    PENDING_COMMIT = "PENDING_COMMIT"
    EXACT_REPLAY = "EXACT_REPLAY"


@dataclass(frozen=True, slots=True)
class LegalCorpusProvisioningResult:
    """Immutable bounded result; it never claims a new transaction is committed."""

    state: LegalCorpusProvisioningResultState
    document_id: str
    document_version: str
    document_sha3_512: str
    authority_evidence_id: str
    authority_evidence_fingerprint: str


def _active_session(session: Any) -> Any:
    """Require the caller's existing session to report an active transaction."""
    if session is None or getattr(session, "in_transaction", False) is not True:
        raise LegalCorpusProvisioningServiceError(
            "LEGAL_CORPUS_PROVISIONING_ACTIVE_TRANSACTION_REQUIRED"
        )
    return session


def _canonical_document_for(evidence: LegalCorpusProvisioningAuthorityEvidence) -> Any:
    """Resolve the closed server-owned draft named by R8D evidence."""
    try:
        return production_legal_corpus.resolve_platform_legal_corpus_draft(
            evidence.source_document_id,
            evidence.source_version,
        )
    except ValueError as error:
        raise LegalCorpusProvisioningServiceError(
            "LEGAL_CORPUS_PROVISIONING_CANONICAL_SOURCE_UNAVAILABLE"
        ) from error


def _document_result(document: Any, evidence: LegalCorpusProvisioningAuthorityEvidence, state: LegalCorpusProvisioningResultState) -> LegalCorpusProvisioningResult:
    """Build a result from canonical values without implying commit success."""
    return LegalCorpusProvisioningResult(
        state=state,
        document_id=document.document_id,
        document_version=document.version,
        document_sha3_512=document.sha3_512,
        authority_evidence_id=evidence.authority_evidence_id,
        authority_evidence_fingerprint=evidence.evidence_fingerprint,
    )


class LegalCorpusProvisioningService:
    """Compose one exact platform draft admission in a caller transaction.

    ``admit_draft`` accepts only R8D authority evidence. The canonical Charter
    is resolved from the server-owned corpus module. Before either write, both
    registries are read under the same active session. A both-absent pair stages
    document then authority-evidence writes and returns ``PENDING_COMMIT``;
    a both-present exact pair returns ``EXACT_REPLAY`` without writes. Any
    one-sided or divergent pair fails closed. The caller remains responsible
    for commit, abort, and fresh whole-transaction retry.
    """

    def __init__(
        self,
        document_collection: Any = None,
        authority_collection: Any = None,
    ) -> None:
        """Wire persistence collections only; corpus source is never injectable."""
        self.document_collection = document_collection
        self.authority_collection = authority_collection
        self.document_registry = LegalDocumentRegistry
        self.authority_registry = LegalCorpusProvisioningAuthorityRegistry

    def admit_draft(
        self,
        authority_evidence: LegalCorpusProvisioningAuthorityEvidence,
        *,
        session: Any = None,
    ) -> LegalCorpusProvisioningResult:
        """Stage or replay one canonical draft admission under an active session.

        The method performs no transaction lifecycle action. New writes are
        only staged until the caller commits; a second-write failure is raised
        with its cause preserved and is never compensated here.
        """
        transaction = _active_session(session)
        if not isinstance(authority_evidence, LegalCorpusProvisioningAuthorityEvidence):
            raise LegalCorpusProvisioningServiceError(
                "LEGAL_CORPUS_PROVISIONING_AUTHORITY_INPUT_INVALID"
            )
        try:
            canonical = _canonical_document_for(authority_evidence)
        except LegalCorpusProvisioningServiceError as error:
            raise LegalCorpusProvisioningServiceError(
                "LEGAL_CORPUS_PROVISIONING_AUTHORITY_MISMATCH"
            ) from error
        try:
            authority_evidence.verify_against(canonical)
        except LegalCorpusProvisioningAuthorityError as error:
            raise LegalCorpusProvisioningServiceError(
                "LEGAL_CORPUS_PROVISIONING_AUTHORITY_MISMATCH"
            ) from error

        try:
            persisted_document = self.document_registry.get(
                canonical.document_id,
                canonical.version,
                self.document_collection,
                session=transaction,
            )
            persisted_evidence = self.authority_registry.get_by_source(
                canonical.document_id,
                canonical.version,
                self.authority_collection,
                session=transaction,
            )
        except (LegalDocumentRegistryError, LegalCorpusProvisioningAuthorityRegistryError) as error:
            raise LegalCorpusProvisioningServiceError(
                "LEGAL_CORPUS_PROVISIONING_PAIR_PREFLIGHT_FAILED"
            ) from error
        except Exception as error:
            raise LegalCorpusProvisioningServiceError(
                "LEGAL_CORPUS_PROVISIONING_PAIR_PREFLIGHT_FAILED"
            ) from error

        if persisted_document is None and persisted_evidence is None:
            return self._stage_new(canonical, authority_evidence, transaction)
        if persisted_document is None:
            raise LegalCorpusProvisioningServiceError(
                "LEGAL_CORPUS_PROVISIONING_PARTIAL_DOCUMENT_ABSENT"
            )
        if persisted_evidence is None:
            raise LegalCorpusProvisioningServiceError(
                "LEGAL_CORPUS_PROVISIONING_PARTIAL_AUTHORITY_ABSENT"
            )
        try:
            document_matches = persisted_document.to_document() == canonical.to_document()
        except Exception as error:
            raise LegalCorpusProvisioningServiceError(
                "LEGAL_CORPUS_PROVISIONING_DOCUMENT_DIVERGENCE"
            ) from error
        if not document_matches:
            raise LegalCorpusProvisioningServiceError(
                "LEGAL_CORPUS_PROVISIONING_DOCUMENT_DIVERGENCE"
            )
        try:
            authority_matches = persisted_evidence.to_document() == authority_evidence.to_document()
            persisted_evidence.verify_against(canonical)
        except (AttributeError, LegalCorpusProvisioningAuthorityError) as error:
            raise LegalCorpusProvisioningServiceError(
                "LEGAL_CORPUS_PROVISIONING_AUTHORITY_DIVERGENCE"
            ) from error
        if not authority_matches:
            raise LegalCorpusProvisioningServiceError(
                "LEGAL_CORPUS_PROVISIONING_AUTHORITY_DIVERGENCE"
            )
        return _document_result(canonical, persisted_evidence, LegalCorpusProvisioningResultState.EXACT_REPLAY)

    def _stage_new(
        self,
        canonical: Any,
        authority_evidence: LegalCorpusProvisioningAuthorityEvidence,
        session: Any,
    ) -> LegalCorpusProvisioningResult:
        """Stage document then authority evidence; caller owns rollback/commit."""
        try:
            self.document_registry.register(
                canonical,
                self.document_collection,
                session=session,
            )
        except (LegalDocumentRegistryError, Exception) as error:
            if isinstance(error, LegalCorpusProvisioningServiceError):
                raise
            raise LegalCorpusProvisioningServiceError(
                "LEGAL_CORPUS_PROVISIONING_DOCUMENT_WRITE_FAILED"
            ) from error
        try:
            self.authority_registry.create_or_replay(
                authority_evidence,
                self.authority_collection,
                session=session,
            )
        except Exception as error:
            raise LegalCorpusProvisioningServiceError(
                "LEGAL_CORPUS_PROVISIONING_AUTHORITY_WRITE_FAILED"
            ) from error
        return _document_result(canonical, authority_evidence, LegalCorpusProvisioningResultState.PENDING_COMMIT)


__all__ = [
    "LegalCorpusProvisioningResult",
    "LegalCorpusProvisioningResultState",
    "LegalCorpusProvisioningService",
    "LegalCorpusProvisioningServiceError",
    "VERSION",
]


# ARTIFACT: legal_corpus_provisioning_service.py
# VERSION: v1.2.0-R9B-P7-A3-R2-REVIEWED-SUCCESSOR-PROVISIONING-SERVICE
# AUTHORITY BOUNDARY: caller-owned composition of draft document and authority evidence only
# TENANT POSTURE: PLATFORM-scoped corpus; no tenant/principal authority
# FAIL-CLOSED POSTURE: active transaction, pair state, source identity, and writes reject safely
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
