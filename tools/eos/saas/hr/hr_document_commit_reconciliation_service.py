"""WILSY OS HR Document Commit-Reconciliation Service.

TITLE: HR Document Commit-Reconciliation Service
VERSION: v1.0.0-P0-C12F6E3-HR-DOCUMENT-COMMIT-RECONCILIATION-SERVICE
AUTHORITY: Wilsy OS Core Governance / Python EOS

PURPOSE:
Reconcile one durable HR document commit uncertainty against exact HR document
metadata and immutable terminal reconciliation-outcome evidence.

EPITOME:
DURABLE F6D UNCERTAINTY
+ EXACT RECONSTRUCTED HR DOCUMENT
+ F4 DOCUMENT REGISTRY
+ F6E2 TERMINAL OUTCOME REGISTRY
+ CALLER-OWNED ACTIVE MONGO TRANSACTION
-> EXACT CONFIRMED OR RECOVERED OUTCOME

AUTHORITY BOUNDARY:
Bounded reconciliation orchestration only. This service grants no provider IO,
provider deletion, orphan determination, original-commit-failure truth,
retention/disposal authority, IAM, HTTP, payroll, billing, payment, settlement,
or financial execution authority.

TRANSACTION BOUNDARY:
The caller owns one already-active Mongo session and transaction, including
start, commit, abort, whole-transaction retry, and unknown-commit handling.
This service owns none of those lifecycle operations.

CONSISTENCY BOUNDARY:
COMMIT_RECOVERED is created only after the exact reconstructed HrDocument is
persisted using the same active caller session, followed by the terminal
outcome insert using that same session. Until the caller commits that
transaction, neither operation constitutes a durable commit claim.

REPLAY BOUNDARY:
An already durable terminal outcome is never regenerated with a new timestamp.
It may be replayed only after the uncertainty fingerprint and exact current
HrDocument fingerprint are independently correlated.

ABSOLUTE CANONICAL PATH:
/Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/hr/hr_document_commit_reconciliation_service.py

CERTIFICATION / UPDATE DATE: 2026-10-05

CHANGELOG:
2026-10-05 v1.0.0-P0-C12F6E3-HR-DOCUMENT-COMMIT-RECONCILIATION-SERVICE
establishes bounded HR document commit reconciliation orchestration.

FAIL-CLOSED DECLARATION:
Missing/inactive transaction, absent uncertainty, malformed evidence,
divergent document state, contradictory durable outcome, registry corruption,
persistence conflict, and unknown persistence state reject without synthesizing
success.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hmac
from typing import Any, Final, NoReturn, cast

from tools.eos.saas.domain.hr_document import (
    HrDocument,
)
from tools.eos.saas.domain.hr_document_commit_reconciliation_outcome import (
    HrDocumentCommitReconciliationOutcome,
    HrDocumentCommitReconciliationOutcomeEvidence,
    HrDocumentCommitReconciliationOutcomeError,
    record_hr_document_commit_reconciliation_outcome,
)
from tools.eos.saas.domain.hr_document_commit_uncertainty import (
    HrDocumentCommitUncertainty,
)
from tools.eos.saas.hr.hr_document_commit_reconciliation_outcome_registry import (
    HrDocumentCommitReconciliationOutcomeRegistry,
    HrDocumentCommitReconciliationOutcomeRegistryError,
    HrDocumentCommitReconciliationOutcomeRegistryNotFoundError,
)
from tools.eos.saas.hr.hr_document_commit_uncertainty_registry import (
    HrDocumentCommitUncertaintyRegistry,
    HrDocumentCommitUncertaintyRegistryError,
)
from tools.eos.saas.hr.hr_document_registry import (
    HrDocumentRegistryConflictError,
    HrDocumentRegistryError,
    HrDocumentRegistryNotFoundError,
    get_document_version,
    persist_document,
)


VERSION: Final[str] = (
    "v1.0.0-P0-C12F6E3-"
    "HR-DOCUMENT-COMMIT-RECONCILIATION-SERVICE"
)


class HrDocumentCommitReconciliationServiceError(
    RuntimeError
):
    """Base fail-closed F6E3 service error."""

    default_code = (
        "P0_C12F6E3_SERVICE_ERROR"
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


class HrDocumentCommitReconciliationServiceInputError(
    HrDocumentCommitReconciliationServiceError
):
    default_code = (
        "P0_C12F6E3_INPUT_INVALID"
    )


class HrDocumentCommitReconciliationServiceTransactionRequiredError(
    HrDocumentCommitReconciliationServiceError
):
    default_code = (
        "P0_C12F6E3_ACTIVE_TRANSACTION_REQUIRED"
    )


class HrDocumentCommitReconciliationServiceConflictError(
    HrDocumentCommitReconciliationServiceError
):
    default_code = (
        "P0_C12F6E3_RECONCILIATION_CONFLICT"
    )


class HrDocumentCommitReconciliationServiceUnavailableError(
    HrDocumentCommitReconciliationServiceError
):
    default_code = (
        "P0_C12F6E3_RECONCILIATION_UNAVAILABLE"
    )


def _raise(
    error_type: type[
        HrDocumentCommitReconciliationServiceError
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


def _active_transaction(
    session: Any,
) -> Any:
    if session is None:
        _raise(
            HrDocumentCommitReconciliationServiceTransactionRequiredError
        )

    marker = getattr(
        session,
        "in_transaction",
        None,
    )

    try:
        active = (
            marker()
            if callable(
                marker
            )
            else marker
        )

    except (
        AttributeError,
        TypeError,
    ):
        active = False

    if active is not True:
        _raise(
            HrDocumentCommitReconciliationServiceTransactionRequiredError
        )

    return session


def _text(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(
            value,
            str,
        )
        or not value
        or value != value.strip()
        or len(
            value
        ) > 2048
    ):
        _raise(
            HrDocumentCommitReconciliationServiceInputError,
            f"P0_C12F6E3_{name.upper()}_INVALID",
        )

    return cast(
        str,
        value,
    )


def _utc(
    value: object,
) -> datetime:
    if (
        not isinstance(
            value,
            datetime,
        )
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        _raise(
            HrDocumentCommitReconciliationServiceInputError,
            "P0_C12F6E3_RECONCILED_AT_UTC_REQUIRED",
        )

    return cast(
        datetime,
        value,
    ).astimezone(
        timezone.utc
    )


def _same_document(
    observed: HrDocument,
    expected: HrDocument,
) -> bool:
    if (
        type(
            observed
        )
        is not HrDocument
        or type(
            expected
        )
        is not HrDocument
    ):
        return False

    try:
        observed.__post_init__()
        expected.__post_init__()

    except Exception:
        return False

    return (
        observed == expected
        and observed.tenant_id
        == expected.tenant_id
        and observed.document_version_id
        == expected.document_version_id
        and hmac.compare_digest(
            observed.fingerprint,
            expected.fingerprint,
        )
    )


def _validate_existing_outcome(
    *,
    existing: HrDocumentCommitReconciliationOutcomeEvidence,
    uncertainty: HrDocumentCommitUncertainty,
    expected_document: HrDocument,
    observed_document: HrDocument,
) -> None:
    if (
        type(
            existing
        )
        is not HrDocumentCommitReconciliationOutcomeEvidence
    ):
        _raise(
            HrDocumentCommitReconciliationServiceConflictError,
            "P0_C12F6E3_EXISTING_OUTCOME_INVALID",
        )

    try:
        existing.__post_init__()

    except Exception as error:
        _raise(
            HrDocumentCommitReconciliationServiceConflictError,
            "P0_C12F6E3_EXISTING_OUTCOME_CORRUPT",
            error,
        )

    if (
        existing.tenant_id
        != uncertainty.tenant_id
        or existing.uncertainty_id
        != uncertainty.uncertainty_id
        or not hmac.compare_digest(
            existing.uncertainty_fingerprint,
            uncertainty.fingerprint,
        )
        or existing.document_version_id
        != expected_document.document_version_id
        or not hmac.compare_digest(
            existing.document_fingerprint,
            expected_document.fingerprint,
        )
    ):
        _raise(
            HrDocumentCommitReconciliationServiceConflictError,
            "P0_C12F6E3_EXISTING_OUTCOME_BINDING_MISMATCH",
        )

    if not _same_document(
        observed_document,
        expected_document,
    ):
        _raise(
            HrDocumentCommitReconciliationServiceConflictError,
            "P0_C12F6E3_EXISTING_OUTCOME_DOCUMENT_MISMATCH",
        )


def reconcile_hr_document_commit_uncertainty(
    *,
    tenant_id: str,
    uncertainty_id: str,
    reconciled_at: datetime,
    uncertainty_registry: HrDocumentCommitUncertaintyRegistry | Any,
    outcome_registry: HrDocumentCommitReconciliationOutcomeRegistry | Any,
    document_collection: Any,
    session: Any,
) -> HrDocumentCommitReconciliationOutcomeEvidence:
    """Reconcile one durable HR commit uncertainty inside caller transaction."""

    # Must fail before touching any registry.
    tx = _active_transaction(
        session
    )

    tenant = _text(
        "tenant_id",
        tenant_id,
    )

    uncertainty_identity = _text(
        "uncertainty_id",
        uncertainty_id,
    )

    reconciled = _utc(
        reconciled_at
    )

    if uncertainty_registry is None:
        _raise(
            HrDocumentCommitReconciliationServiceInputError,
            "P0_C12F6E3_UNCERTAINTY_REGISTRY_REQUIRED",
        )

    if outcome_registry is None:
        _raise(
            HrDocumentCommitReconciliationServiceInputError,
            "P0_C12F6E3_OUTCOME_REGISTRY_REQUIRED",
        )

    if document_collection is None:
        _raise(
            HrDocumentCommitReconciliationServiceInputError,
            "P0_C12F6E3_DOCUMENT_COLLECTION_REQUIRED",
        )

    # --------------------------------------------------------
    # 1. LOAD DURABLE UNCERTAINTY
    # --------------------------------------------------------

    try:
        uncertainty = uncertainty_registry.get(
            tenant_id=tenant,
            uncertainty_id=uncertainty_identity,
            session=tx,
        )

    except HrDocumentCommitUncertaintyRegistryError as error:
        _raise(
            HrDocumentCommitReconciliationServiceUnavailableError,
            "P0_C12F6E3_UNCERTAINTY_READ_FAILED",
            error,
        )

    if (
        type(
            uncertainty
        )
        is not HrDocumentCommitUncertainty
        or uncertainty.tenant_id != tenant
        or uncertainty.uncertainty_id
        != uncertainty_identity
    ):
        _raise(
            HrDocumentCommitReconciliationServiceConflictError,
            "P0_C12F6E3_UNCERTAINTY_SCOPE_MISMATCH",
        )

    try:
        uncertainty.__post_init__()
        expected_document = (
            uncertainty.to_hr_document()
        )

    except Exception as error:
        _raise(
            HrDocumentCommitReconciliationServiceConflictError,
            "P0_C12F6E3_UNCERTAINTY_CORRUPT",
            error,
        )

    # --------------------------------------------------------
    # 2. LOOK FOR PREVIOUS TERMINAL OUTCOME
    # --------------------------------------------------------

    existing_outcome: (
        HrDocumentCommitReconciliationOutcomeEvidence
        | None
    )

    try:
        existing_outcome = (
            outcome_registry.get_by_uncertainty(
                tenant_id=tenant,
                uncertainty_id=(
                    uncertainty_identity
                ),
                session=tx,
            )
        )

    except HrDocumentCommitReconciliationOutcomeRegistryNotFoundError:
        existing_outcome = None

    except HrDocumentCommitReconciliationOutcomeRegistryError as error:
        _raise(
            HrDocumentCommitReconciliationServiceUnavailableError,
            "P0_C12F6E3_OUTCOME_READ_FAILED",
            error,
        )

    # --------------------------------------------------------
    # 3. READ CURRENT HR DOCUMENT VERSION
    # --------------------------------------------------------

    observed_document: HrDocument | None

    try:
        observed_document = (
            get_document_version(
                tenant,
                expected_document.document_version_id,
                document_collection,
                session=tx,
            )
        )

    except HrDocumentRegistryNotFoundError:
        observed_document = None

    except HrDocumentRegistryError as error:
        _raise(
            HrDocumentCommitReconciliationServiceUnavailableError,
            "P0_C12F6E3_DOCUMENT_READ_FAILED",
            error,
        )

    # --------------------------------------------------------
    # 4. HISTORICAL TERMINAL OUTCOME REPLAY
    # --------------------------------------------------------

    if existing_outcome is not None:

        if observed_document is None:
            _raise(
                HrDocumentCommitReconciliationServiceConflictError,
                "P0_C12F6E3_TERMINAL_OUTCOME_DOCUMENT_MISSING",
            )

        _validate_existing_outcome(
            existing=existing_outcome,
            uncertainty=uncertainty,
            expected_document=expected_document,
            observed_document=observed_document,
        )

        # Never regenerate using the new caller timestamp.
        return existing_outcome

    # --------------------------------------------------------
    # 5. EXACT DOCUMENT ALREADY PRESENT
    # --------------------------------------------------------

    if observed_document is not None:

        if not _same_document(
            observed_document,
            expected_document,
        ):
            _raise(
                HrDocumentCommitReconciliationServiceConflictError,
                "P0_C12F6E3_DOCUMENT_VERSION_OCCUPIED_BY_DIVERGENT_DOCUMENT",
            )

        try:
            confirmed = (
                record_hr_document_commit_reconciliation_outcome(
                    uncertainty=uncertainty,
                    document=expected_document,
                    outcome=(
                        HrDocumentCommitReconciliationOutcome
                        .COMMITTED_CONFIRMED
                    ),
                    reconciled_at=reconciled,
                )
            )

            return outcome_registry.create_or_replay(
                confirmed,
                session=tx,
            )

        except HrDocumentCommitReconciliationOutcomeError as error:
            _raise(
                HrDocumentCommitReconciliationServiceConflictError,
                "P0_C12F6E3_CONFIRMED_OUTCOME_INVALID",
                error,
            )

        except HrDocumentCommitReconciliationOutcomeRegistryError as error:
            _raise(
                HrDocumentCommitReconciliationServiceUnavailableError,
                "P0_C12F6E3_CONFIRMED_OUTCOME_PERSIST_FAILED",
                error,
            )

    # --------------------------------------------------------
    # 6. DOCUMENT ABSENT: EXACT CONTROL-PLANE RECOVERY
    # --------------------------------------------------------

    try:
        recovered_document = persist_document(
            expected_document,
            document_collection,
            session=tx,
        )

    except HrDocumentRegistryConflictError as error:
        _raise(
            HrDocumentCommitReconciliationServiceConflictError,
            "P0_C12F6E3_RECOVERED_DOCUMENT_CONFLICT",
            error,
        )

    except HrDocumentRegistryError as error:
        _raise(
            HrDocumentCommitReconciliationServiceUnavailableError,
            "P0_C12F6E3_RECOVERED_DOCUMENT_PERSIST_FAILED",
            error,
        )

    if not _same_document(
        recovered_document,
        expected_document,
    ):
        _raise(
            HrDocumentCommitReconciliationServiceConflictError,
            "P0_C12F6E3_RECOVERED_DOCUMENT_CORRELATION_INVALID",
        )

    try:
        recovered = (
            record_hr_document_commit_reconciliation_outcome(
                uncertainty=uncertainty,
                document=expected_document,
                outcome=(
                    HrDocumentCommitReconciliationOutcome
                    .COMMIT_RECOVERED
                ),
                reconciled_at=reconciled,
            )
        )

        return outcome_registry.create_or_replay(
            recovered,
            session=tx,
        )

    except HrDocumentCommitReconciliationOutcomeError as error:
        _raise(
            HrDocumentCommitReconciliationServiceConflictError,
            "P0_C12F6E3_RECOVERED_OUTCOME_INVALID",
            error,
        )

    except HrDocumentCommitReconciliationOutcomeRegistryError as error:
        _raise(
            HrDocumentCommitReconciliationServiceUnavailableError,
            "P0_C12F6E3_RECOVERED_OUTCOME_PERSIST_FAILED",
            error,
        )


__all__ = [
    "VERSION",
    "HrDocumentCommitReconciliationServiceError",
    "HrDocumentCommitReconciliationServiceInputError",
    "HrDocumentCommitReconciliationServiceTransactionRequiredError",
    "HrDocumentCommitReconciliationServiceConflictError",
    "HrDocumentCommitReconciliationServiceUnavailableError",
    "HrDocumentCommitReconciliationOutcomeRegistryNotFoundError",
    "HrDocumentRegistryNotFoundError",
    "get_document_version",
    "persist_document",
    "reconcile_hr_document_commit_uncertainty",
]


# ARTIFACT: tools/eos/saas/hr/hr_document_commit_reconciliation_service.py
# VERSION: v1.0.0-P0-C12F6E3-HR-DOCUMENT-COMMIT-RECONCILIATION-SERVICE
# AUTHORITY: bounded HR document commit reconciliation orchestration only
# TRANSACTION: caller owns start/commit/abort/retry/unknown-commit handling
# COMMITTED_CONFIRMED: exact pre-existing HrDocument only
# COMMIT_RECOVERED: exact HrDocument + terminal outcome in same active session
# EXISTING OUTCOME: immutable replay only after exact correlation
# PROVIDER IO AUTHORITY: none
# ORPHAN PROOF AUTHORITY: none
# PROVIDER DELETE AUTHORITY: none
# RETENTION/DISPOSAL AUTHORITY: none
# IAM / HTTP AUTHORITY: none
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
