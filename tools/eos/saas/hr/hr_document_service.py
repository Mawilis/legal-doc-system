"""WILSY OS HR Document Orchestration Service.

TITLE: HR Document Orchestration Service
VERSION: v1.0.0-P0-C12F6F-HR-DOCUMENT-ORCHESTRATION-SERVICE
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Own the bounded two-plane HR document ingestion workflow: exact employee
binding, one certified provider write, immutable HrDocument construction,
Mongo metadata commit lifecycle, and durable commit-uncertainty escalation.

EPITOME:
EXACT EMPLOYEE BINDING
+ ONE PROVIDER WRITE
+ VERIFIED OBJECT EVIDENCE
+ HR DOCUMENT DOMAIN
+ F6F-OWNED MONGO TRANSACTION LIFECYCLE
-> COMMITTED OR RECONCILIATION_REQUIRED

TRANSACTION OWNER:
F6F owns Mongo session creation, transaction start, commit, abort, bounded
whole-transaction retry, primary unknown-commit classification, and the
separate durable uncertainty-persistence transaction.

TWO-PLANE BOUNDARY:
Provider operations are outside Mongo transactions. Once provider completion
is proven, Mongo retry never repeats provider begin/write/complete.

UNKNOWN-COMMIT BOUNDARY:
An unknown primary metadata commit never synthesizes COMMITTED. Exact F6C
uncertainty is persisted through F6D in a fresh transaction and the result is
RECONCILIATION_REQUIRED.

RECONCILIATION BOUNDARY:
F6F records uncertainty but never resolves it. F6E3 remains the exclusive
certified commit-reconciliation owner.

AUTHORITY BOUNDARY:
No provider deletion, orphan determination, IAM issuance, HTTP authority,
retention/disposal execution, payroll payment, billing, settlement or
financial execution authority.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/hr/hr_document_service.py

CERTIFICATION / UPDATE DATE: 2026-10-05

CHANGELOG:
2026-10-05 v1.0.0-P0-C12F6F-HR-DOCUMENT-ORCHESTRATION-SERVICE
establishes bounded two-plane HR document ingestion orchestration.

FAIL-CLOSED DECLARATION:
Invalid scope, provider failure, corrupted provider evidence, divergent domain
state, exhausted Mongo retry, unproven commit, or uncertainty persistence
failure rejects or returns explicit RECONCILIATION_REQUIRED; never synthetic
success.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hmac
from typing import Any, Final, NoReturn

from tools.eos.saas.domain.hr_document import (
    HrDocument,
    HrDocumentClass,
    HrDocumentDomainError,
)
from tools.eos.saas.domain.hr_document_commit_uncertainty import (
    HrDocumentCommitUncertainty,
    HrDocumentCommitUncertaintyError,
    open_hr_document_commit_uncertainty,
)
from tools.eos.saas.hr.hr_document_commit_uncertainty_registry import (
    HrDocumentCommitUncertaintyRegistry,
    HrDocumentCommitUncertaintyRegistryError,
    HrDocumentCommitUncertaintyRegistryRetryRequiredError,
)
from tools.eos.saas.hr.hr_document_registry import (
    HrDocumentRegistryError,
    HrDocumentRegistryRetryRequiredError,
    persist_document,
)
from tools.eos.saas.hr.hr_document_storage import (
    HrDocumentBinaryObjectEvidence,
    HrDocumentBinaryStoragePort,
    HrDocumentBinaryStoragePortError,
    HrDocumentBinaryWriteIntent,
    StreamingSHA3512,
    validate_completed_binary_object,
    validate_object_evidence_for_intent,
    validate_write_session_for_intent,
)


VERSION: Final[str] = (
    "v1.0.0-P0-C12F6F-"
    "HR-DOCUMENT-ORCHESTRATION-SERVICE"
)

DEFAULT_MAX_TRANSACTION_ATTEMPTS: Final[int] = 3

MAX_TRANSACTION_ATTEMPTS: Final[int] = 8


class HrDocumentIngestionStatus(
    StrEnum
):
    """Closed F6F caller-visible ingestion result state."""

    COMMITTED = "COMMITTED"

    RECONCILIATION_REQUIRED = (
        "RECONCILIATION_REQUIRED"
    )


@dataclass(
    frozen=True,
    slots=True,
)
class HrDocumentIngestionResult:
    """Bounded ingestion result without reconciliation authority."""

    status: HrDocumentIngestionStatus
    document: HrDocument
    uncertainty: HrDocumentCommitUncertainty | None


class HrDocumentServiceError(
    RuntimeError
):
    """Base fail-closed F6F service error."""

    default_code = (
        "P0_C12F6F_SERVICE_ERROR"
    )

    def __init__(
        self,
        code: str | None = None,
    ) -> None:
        self.code = (
            code
            or self.default_code
        )

        super().__init__(
            self.code
        )


class HrDocumentServiceInputError(
    HrDocumentServiceError
):
    default_code = (
        "P0_C12F6F_INPUT_INVALID"
    )


class HrDocumentServiceScopeError(
    HrDocumentServiceError
):
    default_code = (
        "P0_C12F6F_EMPLOYEE_SCOPE_INVALID"
    )


class HrDocumentServiceProviderError(
    HrDocumentServiceError
):
    default_code = (
        "P0_C12F6F_PROVIDER_WRITE_FAILED"
    )


class HrDocumentServicePersistenceError(
    HrDocumentServiceError
):
    default_code = (
        "P0_C12F6F_METADATA_PERSISTENCE_FAILED"
    )


class HrDocumentServiceTransactionRetryExhaustedError(
    HrDocumentServiceError
):
    default_code = (
        "P0_C12F6F_TRANSACTION_RETRY_EXHAUSTED"
    )


class HrDocumentServiceUncertaintyPersistenceError(
    HrDocumentServiceError
):
    default_code = (
        "P0_C12F6F_UNCERTAINTY_PERSISTENCE_FAILED"
    )


def _raise(
    error_type: type[
        HrDocumentServiceError
    ],
    code: str | None = None,
    cause: BaseException | None = None,
) -> NoReturn:
    error = error_type(
        code
    )

    if cause is None:
        raise error

    raise error from cause


def _has_label(
    error: BaseException,
    label: str,
) -> bool:
    """Inspect one causal chain for an exact PyMongo-style label."""

    seen: set[int] = set()

    current: BaseException | None = error

    while current is not None:
        marker = id(
            current
        )

        if marker in seen:
            break

        seen.add(
            marker
        )

        checker = getattr(
            current,
            "has_error_label",
            None,
        )

        if callable(
            checker
        ):
            try:
                if checker(
                    label
                ) is True:
                    return True

            except Exception:
                pass

        current = (
            current.__cause__
            or current.__context__
        )

    return False


def _abort_if_active(
    session: Any,
) -> None:
    try:
        marker = getattr(
            session,
            "in_transaction",
            False,
        )

        active = (
            marker()
            if callable(
                marker
            )
            else marker
        )

        if active is True:
            session.abort_transaction()

    except Exception:
        # Never replace the original transaction failure with abort noise.
        pass


def _transaction_attempts(
    value: object,
) -> int:
    if (
        isinstance(
            value,
            bool,
        )
        or not isinstance(
            value,
            int,
        )
        or value < 1
        or value > MAX_TRANSACTION_ATTEMPTS
    ):
        _raise(
            HrDocumentServiceInputError,
            "P0_C12F6F_MAX_TRANSACTION_ATTEMPTS_INVALID",
        )

    return value


def _employee_binding(
    *,
    intent: HrDocumentBinaryWriteIntent,
    employee_registry: Any,
) -> None:
    if employee_registry is None:
        _raise(
            HrDocumentServiceInputError,
            "P0_C12F6F_EMPLOYEE_REGISTRY_REQUIRED",
        )

    try:
        employee = (
            employee_registry.get_employee_by_id(
                intent.employee_id,
                intent.tenant_id,
            )
        )

    except Exception as error:
        _raise(
            HrDocumentServiceScopeError,
            "P0_C12F6F_EMPLOYEE_LOOKUP_FAILED",
            error,
        )

    if employee is None:
        _raise(
            HrDocumentServiceScopeError,
            "P0_C12F6F_EMPLOYEE_NOT_FOUND",
        )

    if (
        getattr(
            employee,
            "employeeId",
            None,
        )
        != intent.employee_id
        or getattr(
            employee,
            "tenantId",
            None,
        )
        != intent.tenant_id
    ):
        _raise(
            HrDocumentServiceScopeError,
            "P0_C12F6F_EMPLOYEE_BINDING_MISMATCH",
        )


def _provider_write_once(
    *,
    intent: HrDocumentBinaryWriteIntent,
    chunks: tuple[bytes, ...],
    storage: HrDocumentBinaryStoragePort | Any,
) -> HrDocumentBinaryObjectEvidence:
    if storage is None:
        _raise(
            HrDocumentServiceInputError,
            "P0_C12F6F_STORAGE_REQUIRED",
        )

    if (
        not isinstance(
            chunks,
            tuple,
        )
        or not chunks
    ):
        _raise(
            HrDocumentServiceInputError,
            "P0_C12F6F_CHUNKS_REQUIRED",
        )

    provider_session: Any = None
    provider_completed = False

    try:
        provider_session = storage.begin(
            intent
        )

        validate_write_session_for_intent(
            intent=intent,
            session=provider_session,
        )

        stream = StreamingSHA3512()

        chunk_evidence = []

        for sequence, chunk in enumerate(
            chunks
        ):
            if (
                not isinstance(
                    chunk,
                    bytes,
                )
                or not chunk
            ):
                _raise(
                    HrDocumentServiceInputError,
                    "P0_C12F6F_CHUNK_BYTES_REQUIRED",
                )

            stream.update(
                chunk
            )

            evidence = storage.write_chunk(
                intent,
                provider_session,
                sequence=sequence,
                chunk=chunk,
            )

            chunk_evidence.append(
                evidence
            )

        observed_length, observed_fingerprint = (
            stream.finalize()
        )

        completed = storage.complete(
            intent,
            provider_session,
            tuple(
                chunk_evidence
            ),
            observed_length=(
                observed_length
            ),
            observed_fingerprint=(
                observed_fingerprint
            ),
        )

        provider_completed = True

        validate_completed_binary_object(
            intent=intent,
            chunks=tuple(
                chunk_evidence
            ),
            evidence=completed,
            observed_length=(
                observed_length
            ),
            observed_fingerprint=(
                observed_fingerprint
            ),
        )

        inspected = storage.inspect(
            intent,
            completed,
        )

        validate_object_evidence_for_intent(
            intent=intent,
            evidence=inspected,
        )

        if (
            inspected != completed
            or inspected.content_length
            != observed_length
            or not hmac.compare_digest(
                inspected.content_fingerprint,
                observed_fingerprint,
            )
        ):
            _raise(
                HrDocumentServiceProviderError,
                "P0_C12F6F_PROVIDER_INSPECTION_MISMATCH",
            )

        return inspected

    except HrDocumentServiceError:
        raise

    except (
        HrDocumentBinaryStoragePortError,
        Exception,
    ) as error:
        if (
            provider_session is not None
            and provider_completed is False
        ):
            try:
                storage.abort(
                    intent,
                    provider_session,
                )

            except Exception:
                pass

        _raise(
            HrDocumentServiceProviderError,
            cause=error,
        )


def _build_document(
    *,
    intent: HrDocumentBinaryWriteIntent,
    evidence: HrDocumentBinaryObjectEvidence,
    document_class: HrDocumentClass,
    created_at: datetime,
    created_by_principal_id: str,
    retention_until: datetime | None,
    legal_hold: bool,
    supersedes_version_id: str | None,
) -> HrDocument:
    try:
        return HrDocument.from_binary_evidence(
            intent=intent,
            evidence=evidence,
            document_class=document_class,
            created_at=created_at,
            created_by_principal_id=(
                created_by_principal_id
            ),
            retention_until=retention_until,
            legal_hold=legal_hold,
            supersedes_version_id=(
                supersedes_version_id
            ),
        )

    except HrDocumentDomainError as error:
        _raise(
            HrDocumentServiceInputError,
            "P0_C12F6F_DOCUMENT_DOMAIN_INVALID",
            error,
        )


def _primary_metadata_commit(
    *,
    document: HrDocument,
    mongo_client: Any,
    document_collection: Any,
    attempts: int,
) -> str:
    """Return COMMITTED or UNKNOWN; never replay provider work."""

    for attempt in range(
        1,
        attempts + 1,
    ):
        try:
            with mongo_client.start_session() as session:
                session.start_transaction()

                try:
                    persisted = persist_document(
                        document,
                        document_collection,
                        session=session,
                    )

                    if persisted != document:
                        _raise(
                            HrDocumentServicePersistenceError,
                            "P0_C12F6F_DOCUMENT_POST_WRITE_MISMATCH",
                        )

                except HrDocumentRegistryRetryRequiredError as error:
                    _abort_if_active(
                        session
                    )

                    if attempt < attempts:
                        continue

                    _raise(
                        HrDocumentServiceTransactionRetryExhaustedError,
                        cause=error,
                    )

                except HrDocumentRegistryError as error:
                    if _has_label(
                        error,
                        "TransientTransactionError",
                    ):
                        _abort_if_active(
                            session
                        )

                        if attempt < attempts:
                            continue

                        _raise(
                            HrDocumentServiceTransactionRetryExhaustedError,
                            cause=error,
                        )

                    _abort_if_active(
                        session
                    )

                    _raise(
                        HrDocumentServicePersistenceError,
                        cause=error,
                    )

                try:
                    session.commit_transaction()

                except Exception as error:
                    if _has_label(
                        error,
                        "UnknownTransactionCommitResult",
                    ):
                        # Primary commit truth is unproven. Do not retry the
                        # provider write and do not synthesize COMMITTED.
                        return "UNKNOWN"

                    if _has_label(
                        error,
                        "TransientTransactionError",
                    ):
                        _abort_if_active(
                            session
                        )

                        if attempt < attempts:
                            continue

                        _raise(
                            HrDocumentServiceTransactionRetryExhaustedError,
                            cause=error,
                        )

                    _abort_if_active(
                        session
                    )

                    _raise(
                        HrDocumentServicePersistenceError,
                        "P0_C12F6F_PRIMARY_COMMIT_FAILED",
                        error,
                    )

                return "COMMITTED"

        except HrDocumentServiceError:
            raise

        except Exception as error:
            if _has_label(
                error,
                "TransientTransactionError",
            ):
                if attempt < attempts:
                    continue

                _raise(
                    HrDocumentServiceTransactionRetryExhaustedError,
                    cause=error,
                )

            _raise(
                HrDocumentServicePersistenceError,
                "P0_C12F6F_PRIMARY_TRANSACTION_FAILED",
                error,
            )

    _raise(
        HrDocumentServiceTransactionRetryExhaustedError
    )


def _persist_uncertainty(
    *,
    uncertainty: HrDocumentCommitUncertainty,
    mongo_client: Any,
    uncertainty_collection: Any,
    attempts: int,
) -> HrDocumentCommitUncertainty:
    """Persist uncertainty in a fresh independent transaction."""

    for attempt in range(
        1,
        attempts + 1,
    ):
        try:
            with mongo_client.start_session() as session:
                session.start_transaction()

                registry = (
                    HrDocumentCommitUncertaintyRegistry(
                        uncertainty_collection
                    )
                )

                try:
                    persisted = registry.create_or_replay(
                        uncertainty,
                        session=session,
                    )

                    if persisted != uncertainty:
                        _raise(
                            HrDocumentServiceUncertaintyPersistenceError,
                            "P0_C12F6F_UNCERTAINTY_POST_WRITE_MISMATCH",
                        )

                except HrDocumentCommitUncertaintyRegistryRetryRequiredError as error:
                    _abort_if_active(
                        session
                    )

                    if attempt < attempts:
                        continue

                    _raise(
                        HrDocumentServiceUncertaintyPersistenceError,
                        "P0_C12F6F_UNCERTAINTY_RETRY_EXHAUSTED",
                        error,
                    )

                except HrDocumentCommitUncertaintyRegistryError as error:
                    if _has_label(
                        error,
                        "TransientTransactionError",
                    ):
                        _abort_if_active(
                            session
                        )

                        if attempt < attempts:
                            continue

                    _abort_if_active(
                        session
                    )

                    _raise(
                        HrDocumentServiceUncertaintyPersistenceError,
                        cause=error,
                    )

                # Unknown uncertainty-commit results are retried on the same
                # commit operation; provider execution is never revisited.
                commit_attempts = 0

                while True:
                    commit_attempts += 1

                    try:
                        session.commit_transaction()
                        return persisted

                    except Exception as error:
                        if (
                            _has_label(
                                error,
                                "UnknownTransactionCommitResult",
                            )
                            and commit_attempts < attempts
                        ):
                            continue

                        if _has_label(
                            error,
                            "TransientTransactionError",
                        ):
                            _abort_if_active(
                                session
                            )

                            if attempt < attempts:
                                break

                        _raise(
                            HrDocumentServiceUncertaintyPersistenceError,
                            "P0_C12F6F_UNCERTAINTY_COMMIT_UNPROVEN",
                            error,
                        )

        except HrDocumentServiceError:
            raise

        except Exception as error:
            if (
                _has_label(
                    error,
                    "TransientTransactionError",
                )
                and attempt < attempts
            ):
                continue

            _raise(
                HrDocumentServiceUncertaintyPersistenceError,
                cause=error,
            )

    _raise(
        HrDocumentServiceUncertaintyPersistenceError,
        "P0_C12F6F_UNCERTAINTY_RETRY_EXHAUSTED",
    )


def orchestrate_hr_document_ingestion(
    *,
    intent: HrDocumentBinaryWriteIntent,
    chunks: tuple[bytes, ...],
    document_class: HrDocumentClass,
    created_at: datetime,
    created_by_principal_id: str,
    retention_until: datetime | None,
    legal_hold: bool,
    supersedes_version_id: str | None,
    storage: HrDocumentBinaryStoragePort | Any,
    employee_registry: Any,
    mongo_client: Any,
    document_collection: Any,
    uncertainty_collection: Any,
    max_transaction_attempts: int = DEFAULT_MAX_TRANSACTION_ATTEMPTS,
) -> HrDocumentIngestionResult:
    """Execute one bounded HR document ingestion across provider and Mongo."""

    if type(
        intent
    ) is not HrDocumentBinaryWriteIntent:
        _raise(
            HrDocumentServiceInputError,
            "P0_C12F6F_WRITE_INTENT_REQUIRED",
        )

    if mongo_client is None:
        _raise(
            HrDocumentServiceInputError,
            "P0_C12F6F_MONGO_CLIENT_REQUIRED",
        )

    if document_collection is None:
        _raise(
            HrDocumentServiceInputError,
            "P0_C12F6F_DOCUMENT_COLLECTION_REQUIRED",
        )

    if uncertainty_collection is None:
        _raise(
            HrDocumentServiceInputError,
            "P0_C12F6F_UNCERTAINTY_COLLECTION_REQUIRED",
        )

    attempts = _transaction_attempts(
        max_transaction_attempts
    )

    # Scope is proven before any provider execution.
    _employee_binding(
        intent=intent,
        employee_registry=employee_registry,
    )

    # Provider execution occurs once and only once.
    evidence = _provider_write_once(
        intent=intent,
        chunks=chunks,
        storage=storage,
    )

    document = _build_document(
        intent=intent,
        evidence=evidence,
        document_class=document_class,
        created_at=created_at,
        created_by_principal_id=(
            created_by_principal_id
        ),
        retention_until=retention_until,
        legal_hold=legal_hold,
        supersedes_version_id=(
            supersedes_version_id
        ),
    )

    primary = _primary_metadata_commit(
        document=document,
        mongo_client=mongo_client,
        document_collection=(
            document_collection
        ),
        attempts=attempts,
    )

    if primary == "COMMITTED":
        return HrDocumentIngestionResult(
            status=(
                HrDocumentIngestionStatus
                .COMMITTED
            ),
            document=document,
            uncertainty=None,
        )

    # Primary Mongo commit truth is unproven after provider completion.
    # Persist restart-safe uncertainty independently; do not resolve it here.
    try:
        uncertainty = (
            open_hr_document_commit_uncertainty(
                intent=intent,
                object_evidence=evidence,
                document_class=document_class,
                created_at=created_at,
                created_by_principal_id=(
                    created_by_principal_id
                ),
                retention_until=(
                    retention_until
                ),
                legal_hold=legal_hold,
                supersedes_version_id=(
                    supersedes_version_id
                ),
                # Deterministic and valid: F6C permits detection equal to
                # creation. Avoids creating divergent evidence on replay.
                detected_at=created_at,
            )
        )

    except HrDocumentCommitUncertaintyError as error:
        _raise(
            HrDocumentServiceUncertaintyPersistenceError,
            "P0_C12F6F_UNCERTAINTY_DOMAIN_INVALID",
            error,
        )

    persisted_uncertainty = _persist_uncertainty(
        uncertainty=uncertainty,
        mongo_client=mongo_client,
        uncertainty_collection=(
            uncertainty_collection
        ),
        attempts=attempts,
    )

    return HrDocumentIngestionResult(
        status=(
            HrDocumentIngestionStatus
            .RECONCILIATION_REQUIRED
        ),
        document=document,
        uncertainty=(
            persisted_uncertainty
        ),
    )


__all__ = [
    "VERSION",
    "DEFAULT_MAX_TRANSACTION_ATTEMPTS",
    "MAX_TRANSACTION_ATTEMPTS",
    "HrDocumentIngestionStatus",
    "HrDocumentIngestionResult",
    "HrDocumentServiceError",
    "HrDocumentServiceInputError",
    "HrDocumentServiceScopeError",
    "HrDocumentServiceProviderError",
    "HrDocumentServicePersistenceError",
    "HrDocumentServiceTransactionRetryExhaustedError",
    "HrDocumentServiceUncertaintyPersistenceError",
    "HrDocumentRegistryRetryRequiredError",
    "HrDocumentCommitUncertaintyRegistry",
    "persist_document",
    "orchestrate_hr_document_ingestion",
]


# ARTIFACT: tools/eos/saas/hr/hr_document_service.py
# VERSION: v1.0.0-P0-C12F6F-HR-DOCUMENT-ORCHESTRATION-SERVICE
# TRANSACTION OWNER: F6F
# PROVIDER WRITE: exactly once outside Mongo transactions
# PRIMARY MONGO TX: bounded fresh whole-transaction retry
# UNKNOWN PRIMARY COMMIT: never synthetic success
# UNCERTAINTY: F6C/F6D persisted in fresh independent transaction
# RECONCILIATION: F6E3 exclusively owns resolution
# PROVIDER DELETE AUTHORITY: none
# ORPHAN PROOF AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
