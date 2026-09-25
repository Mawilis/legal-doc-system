"""WILSY OS authorized legal conflict-review issuance orchestration.

TITLE: Legal Conflict Review Issuance Orchestrator
VERSION: v1.0.0-L8-8J-LEGAL-CONFLICT-REVIEW-ISSUANCE
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Compose one immutable human conflict-review determination only after
         re-reading the exact persisted screening and issuing durable canonical
         tenant-authorization decision evidence for that screening under the
         same caller-owned transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/orchestration/legal_conflict_review_orchestrator.py
COLLABORATION / OWNERSHIP: L8-8E owns persisted screening evidence; L8-8G owns
                            human review semantics; L8-8H owns immutable review
                            persistence; generic TenantAuthorizationDecisionEvidence
                            owns durable authorization evidence; L8-8I owns the
                            legal_conflict_review_write permission/role/business
                            eligibility binding. L8-8J owns only their exact
                            transactional composition.
CERTIFICATION / UPDATE DATE: 2026-09-25
CHANGELOG: v1.0.0-L8-8J-LEGAL-CONFLICT-REVIEW-ISSUANCE establishes exact
           persisted-screening admission, server-principal binding, durable
           authorization-evidence issuance/replay over the screening fingerprint,
           deterministic authorization idempotency from review_id, immutable
           L8-8G composition, L8-8H persistence/replay and stable fail-closed
           taxonomy. It creates no waiver, ethical wall, recusal, representation,
           client acceptance, legal advice or conflict-clearance authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Accepts opaque IDs, closed review outcome, bounded
                             evidence references and SHA3-512 evidence only.
                             Raw party PII and privileged narrative are excluded.
TENANT BOUNDARY: Tenant scope is explicit and must match the persisted screening;
                 the reviewer principal is explicit server-authenticated identity.
AUTHORITY BOUNDARY: Authorized human conflict-review determination issuance only.
                    NO_CONFLICT_IDENTIFIED is bounded to the exact screening and
                    is not a waiver, future-conflict warranty, engagement,
                    representation mandate, matter acceptance or legal finding.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller owns the already-active session/transaction and all
                      commit, abort and whole-transaction retry lifecycle. L8-8J
                      starts, commits, aborts and retries nothing.
FAIL-CLOSED DECLARATION: Missing transaction, missing/corrupt screening,
                         authorization denial/evidence conflict, tenant/principal
                         mismatch, incompatible review semantics, review replay
                         divergence and persistence failures reject.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Final, NoReturn

from tools.eos.auth.tenant_authorization_decision_evidence_registry import (
    TenantAuthorizationDecisionEvidenceAuthorizationDeniedError,
    TenantAuthorizationDecisionEvidenceConflictError,
    TenantAuthorizationDecisionEvidencePersistenceError,
    TenantAuthorizationDecisionEvidenceRegistry,
    TenantAuthorizationDecisionEvidenceRegistryError,
    TenantAuthorizationDecisionEvidenceTransactionRequiredError,
)
from tools.eos.legal_operations.domain.legal_conflict_review import (
    LegalConflictReviewDetermination,
    LegalConflictReviewError,
    LegalConflictReviewOutcome,
    determine_legal_conflict_review,
)
from tools.eos.legal_operations.registry.legal_conflict_review_registry import (
    LegalConflictReviewRegistry,
    LegalConflictReviewRegistryConflictError,
    LegalConflictReviewRegistryError,
    LegalConflictReviewRegistryPersistenceUnavailableError,
    LegalConflictReviewRegistryPersistedRecordInvalidError,
    LegalConflictReviewRegistryRetryRequiredError,
)
from tools.eos.legal_operations.registry.legal_conflict_screening_registry import (
    LegalConflictScreeningRegistry,
    LegalConflictScreeningRegistryError,
    LegalConflictScreeningRegistryNotFoundError,
    LegalConflictScreeningRegistryPersistenceUnavailableError,
    LegalConflictScreeningRegistryPersistedRecordInvalidError,
    LegalConflictScreeningRegistryRetryRequiredError,
)


VERSION: Final[str] = "v1.0.0-L8-8J-LEGAL-CONFLICT-REVIEW-ISSUANCE"
PERMISSION: Final[str] = "legal_operations:conflict_review:write"
OPERATION: Final[str] = "legal_conflict_review_write"
SUBJECT_PREFIX: Final[str] = "legal-conflict-screening"


class LegalConflictReviewOrchestrationError(RuntimeError):
    """Stable fail-closed L8-8J orchestration error."""

    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class LegalConflictReviewOrchestrationRetryRequiredError(
    LegalConflictReviewOrchestrationError
):
    """Caller must abort and retry the complete transaction from fresh state."""


def _fail(
    code: str,
    cause: BaseException | None = None,
) -> NoReturn:
    error = LegalConflictReviewOrchestrationError(code)
    if cause is None:
        raise error
    raise error from cause


def _retry(
    code: str,
    cause: BaseException,
) -> NoReturn:
    raise LegalConflictReviewOrchestrationRetryRequiredError(code) from cause


def _text(name: str, value: object) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        _fail(f"L8_8J_{name.upper()}_INVALID")
    return value


def _active_session(session: Any) -> Any:
    if session is None:
        _fail("L8_8J_ACTIVE_TRANSACTION_REQUIRED")
    marker = getattr(session, "in_transaction", None)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        _fail("L8_8J_ACTIVE_TRANSACTION_REQUIRED")
    return session


def _subject_reference(screening_id: str) -> str:
    return f"{SUBJECT_PREFIX}:{screening_id}"


def _authorization_idempotency_key(review_id: str) -> str:
    return f"legal-conflict-review:{review_id}"


def issue_legal_conflict_review(
    *,
    tenant_id: str,
    reviewer_principal_id: str,
    screening_id: str,
    review_id: str,
    outcome: LegalConflictReviewOutcome | str,
    review_reason_reference: str,
    reviewed_at: datetime,
    screening_collection: Any,
    review_collection: Any,
    authorization_evidence_registry: TenantAuthorizationDecisionEvidenceRegistry,
    session: Any,
) -> LegalConflictReviewDetermination:
    """Issue and persist one authorized human review over persisted screening.

    The function performs no HTTP authentication and owns no transaction. Its
    caller must supply one server-authenticated principal identity, exact tenant,
    already-active transaction, canonical screening/review collections, and the
    canonical durable tenant-authorization evidence registry configured with the
    current IAM repositories.

    Authorization evidence is issued against the exact persisted screening
    fingerprint using legal_operations:conflict_review:write and
    legal_conflict_review_write. The resulting durable evidence reference and
    SHA3-512 fingerprint are the only reviewer authorization provenance admitted
    into L8-8G.
    """
    tx = _active_session(session)
    tenant = _text("tenant_id", tenant_id)
    principal = _text("reviewer_principal_id", reviewer_principal_id)
    screening_identity = _text("screening_id", screening_id)
    review_identity = _text("review_id", review_id)
    reason_reference = _text(
        "review_reason_reference",
        review_reason_reference,
    )
    if not isinstance(
        authorization_evidence_registry,
        TenantAuthorizationDecisionEvidenceRegistry,
    ):
        _fail("L8_8J_AUTHORIZATION_EVIDENCE_REGISTRY_REQUIRED")
    if screening_collection is None:
        _fail("L8_8J_SCREENING_COLLECTION_REQUIRED")
    if review_collection is None:
        _fail("L8_8J_REVIEW_COLLECTION_REQUIRED")

    try:
        screening = LegalConflictScreeningRegistry.get_screening(
            tenant,
            screening_identity,
            screening_collection,
            session=tx,
        )
    except LegalConflictScreeningRegistryNotFoundError as error:
        _fail("L8_8J_SCREENING_NOT_FOUND", error)
    except LegalConflictScreeningRegistryRetryRequiredError as error:
        _retry("L8_8J_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except (
        LegalConflictScreeningRegistryPersistedRecordInvalidError,
        LegalConflictScreeningRegistryPersistenceUnavailableError,
        LegalConflictScreeningRegistryError,
    ) as error:
        _fail("L8_8J_SCREENING_AUTHORITY_UNAVAILABLE", error)

    if screening.tenant_id != tenant or screening.screening_id != screening_identity:
        _fail("L8_8J_SCREENING_SCOPE_MISMATCH")

    try:
        authorization = authorization_evidence_registry.issue(
            tenant_id=tenant,
            principal_id=principal,
            operation=OPERATION,
            permission=PERMISSION,
            subject_reference=_subject_reference(screening.screening_id),
            subject_evidence_fingerprint=screening.fingerprint,
            idempotency_key=_authorization_idempotency_key(review_identity),
            session=tx,
        )
    except TenantAuthorizationDecisionEvidenceAuthorizationDeniedError as error:
        _fail("L8_8J_REVIEWER_AUTHORIZATION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceTransactionRequiredError as error:
        _fail("L8_8J_ACTIVE_TRANSACTION_REQUIRED", error)
    except TenantAuthorizationDecisionEvidenceConflictError as error:
        _retry("L8_8J_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except TenantAuthorizationDecisionEvidencePersistenceError as error:
        _fail("L8_8J_AUTHORIZATION_EVIDENCE_UNAVAILABLE", error)
    except TenantAuthorizationDecisionEvidenceRegistryError as error:
        _fail("L8_8J_AUTHORIZATION_EVIDENCE_UNAVAILABLE", error)

    if (
        authorization.tenant_id != tenant
        or authorization.principal_id != principal
        or authorization.operation != OPERATION
        or authorization.permission != PERMISSION
        or authorization.subject_reference
        != _subject_reference(screening.screening_id)
        or authorization.subject_evidence_fingerprint != screening.fingerprint
    ):
        _fail("L8_8J_AUTHORIZATION_EVIDENCE_CORRELATION_INVALID")

    try:
        review = determine_legal_conflict_review(
            screening=screening,
            review_id=review_identity,
            reviewer_principal_id=principal,
            reviewer_authorization_reference=(
                authorization.authorization_evidence_reference
            ),
            reviewer_authorization_fingerprint=(
                authorization.authorization_evidence_fingerprint
            ),
            outcome=outcome,
            review_reason_reference=reason_reference,
            reviewed_at=reviewed_at,
            source_evidence_reference=_subject_reference(
                screening.screening_id
            ),
            source_evidence_fingerprint=screening.fingerprint,
        )
    except LegalConflictReviewError as error:
        _fail("L8_8J_REVIEW_DETERMINATION_INVALID", error)

    try:
        persisted = LegalConflictReviewRegistry.persist_review(
            review,
            review_collection,
            session=tx,
        )
    except LegalConflictReviewRegistryRetryRequiredError as error:
        _retry("L8_8J_WHOLE_TRANSACTION_RETRY_REQUIRED", error)
    except LegalConflictReviewRegistryConflictError as error:
        _fail("L8_8J_REVIEW_CONFLICT", error)
    except (
        LegalConflictReviewRegistryPersistedRecordInvalidError,
        LegalConflictReviewRegistryPersistenceUnavailableError,
        LegalConflictReviewRegistryError,
    ) as error:
        _fail("L8_8J_REVIEW_PERSISTENCE_UNAVAILABLE", error)

    if (
        persisted.to_dict() != review.to_dict()
        or persisted.tenant_id != tenant
        or persisted.screening_id != screening.screening_id
        or persisted.reviewer_principal_id != principal
    ):
        _fail("L8_8J_REVIEW_POST_WRITE_CORRELATION_INVALID")
    return persisted


__all__ = [
    "OPERATION",
    "PERMISSION",
    "SUBJECT_PREFIX",
    "VERSION",
    "LegalConflictReviewOrchestrationError",
    "LegalConflictReviewOrchestrationRetryRequiredError",
    "issue_legal_conflict_review",
]


# ARTIFACT: legal_conflict_review_orchestrator.py
# VERSION: v1.0.0-L8-8J-LEGAL-CONFLICT-REVIEW-ISSUANCE
# AUTHORITY BOUNDARY: authorized immutable human conflict-review issuance only
# TENANT POSTURE: exact tenant + persisted screening + server-principal + durable IAM evidence
# FAIL-CLOSED POSTURE: transaction/screening/IAM/review/persistence divergence rejects; retries remain caller-owned
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
