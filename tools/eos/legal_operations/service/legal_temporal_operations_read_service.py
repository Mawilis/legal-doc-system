"""
TITLE:
    WILSY OS Legal Temporal Operations Read Service

VERSION:
    v1.0.0-P4-P1-LEGAL-TEMPORAL-OPERATIONS-READ-SERVICE

AUTHORITY:
    Wilsy OS Core Governance / Python EOS Legal Operations

EPITOME:
    Compose exact tenant-scoped canonical deadline evidence for matters
    already visible in the authenticated Productive Work projection.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_temporal_operations_read_service.py

COLLABORATION / OWNERSHIP:
    Productive Work owns admitted matter visibility.
    P4-P0 owns immutable temporal projection composition.
    Existing Legal Matter Deadline service and registry own deadline reads.
    P4-P1 owns read-only service composition, never transaction ownership.

CERTIFICATION / UPDATE DATE:
    2026-10-18

CHANGELOG:
    2026-10-18 v1.0.0-P4-P1-LEGAL-TEMPORAL-OPERATIONS-READ-SERVICE establishes caller-owned
    transaction enforcement, one canonical read per distinct visible matter,
    exact session propagation and fail-closed projection errors.
    R15B-R1 completes institutional metadata without runtime changes.

COMPLIANCE:
    POPIA section 19, GDPR Article 32 and SOC 2 CC7.2 are
    technical-control objectives, not independent legal-compliance claims.

SECURITY / PRIVACY POSTURE:
    Reject missing or inactive transactions and malformed projections.
    Never broaden visibility beyond authenticated Productive Work.
    Preserve canonical deadline provenance and bounded error semantics.

TENANT BOUNDARY:
    The canonical deadline reader receives only the exact Productive Work
    tenant and admitted matter identifiers with the caller-owned session.

AUTHORITY BOUNDARY:
    Read-only composition. No IAM, assignment, supervision, visibility grant,
    deadline creation/mutation, legal-period or overdue inference, court,
    hearing, notification, calendar or AI execution authority.

FINANCIAL AUTHORITY BOUNDARY:
    No subscription, billing, payment or settlement authority.
    Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

from typing import Any, Final, Protocol

from tools.eos.legal_operations.domain.legal_matter_deadline import (
    LegalMatterDeadline,
)
from tools.eos.legal_operations.domain.legal_profile_productive_work import (
    LegalProductiveWorkProjection,
)
from tools.eos.legal_operations.domain.legal_temporal_operations_projection import (
    LegalTemporalOperationsProjection,
    LegalTemporalOperationsProjectionError,
    compose_legal_temporal_operations_projection,
)
from tools.eos.legal_operations.service.legal_matter_deadline_service import (
    list_legal_matter_deadlines,
)


VERSION: Final[str] = (
    "v1.0.0-P4-P1-LEGAL-TEMPORAL-OPERATIONS-READ-SERVICE"
)


class LegalTemporalOperationsReadServiceError(RuntimeError):
    """Fail-closed P4-P1 read-service error."""

    def __init__(
        self,
        code: str,
        cause: BaseException | None = None,
    ) -> None:
        self.code = code
        self.cause = cause
        super().__init__(code)


class LegalTemporalOperationsReadServiceTransactionRequiredError(
    LegalTemporalOperationsReadServiceError
):
    """Caller-owned active transaction is mandatory."""


class _DeadlineReader(Protocol):
    def list_matter_deadlines(
        self,
        *,
        tenant_id: str,
        case_matter_id: str,
        deadline_collection: object,
        session: object,
    ) -> tuple[LegalMatterDeadline, ...]:
        ...


class _CanonicalDeadlineReader:
    """Adapter to the existing certified Legal Matter Deadline service."""

    def list_matter_deadlines(
        self,
        *,
        tenant_id: str,
        case_matter_id: str,
        deadline_collection: object,
        session: object,
    ) -> tuple[LegalMatterDeadline, ...]:
        return list_legal_matter_deadlines(
            tenant_id=tenant_id,
            case_matter_id=case_matter_id,
            deadline_collection=deadline_collection,
            session=session,
        )


def _transaction(
    session: object,
) -> object:
    """Require, but never own, one caller-active transaction."""

    marker = (
        getattr(
            session,
            "in_transaction",
            None,
        )
        if session is not None
        else None
    )

    try:
        active = (
            marker()
            if callable(marker)
            else marker
        )
    except Exception as error:
        raise (
            LegalTemporalOperationsReadServiceTransactionRequiredError(
                "TEMPORAL_READ_TRANSACTION_REQUIRED",
                error,
            )
        ) from error

    if active is not True:
        raise (
            LegalTemporalOperationsReadServiceTransactionRequiredError(
                "TEMPORAL_READ_TRANSACTION_REQUIRED"
            )
        )

    return session


class LegalTemporalOperationsReadService:
    """
    Compose the authenticated principal's v1 temporal operations read model.

    Productive Work is supplied by the already-certified caller. P4-P0 remains
    the sole visibility-admission composer. This service only performs exact
    matter-scoped canonical deadline reads for that admitted matter set.
    """

    def __init__(
        self,
        *,
        deadline_collection: object,
        deadline_reader: _DeadlineReader | None = None,
    ) -> None:
        self._deadline_collection = deadline_collection
        self._deadline_reader: _DeadlineReader = (
            deadline_reader
            if deadline_reader is not None
            else _CanonicalDeadlineReader()
        )

    def project(
        self,
        *,
        productive_work: LegalProductiveWorkProjection,
        session: object,
    ) -> LegalTemporalOperationsProjection:
        tx = _transaction(
            session
        )

        # Ask P4-P0 itself for the authoritative visible-matter ceiling.
        # No visibility logic is independently recreated here.
        try:
            scope = (
                compose_legal_temporal_operations_projection(
                    productive_work=productive_work,
                    deadlines=(),
                )
            )
        except LegalTemporalOperationsProjectionError as error:
            raise LegalTemporalOperationsReadServiceError(
                "TEMPORAL_PROJECTION_FAILED",
                error,
            ) from error

        deadlines: list[
            LegalMatterDeadline
        ] = []

        for case_matter_id in scope.visible_matter_ids:
            try:
                values = (
                    self._deadline_reader.list_matter_deadlines(
                        tenant_id=productive_work.tenant_id,
                        case_matter_id=case_matter_id,
                        deadline_collection=self._deadline_collection,
                        session=tx,
                    )
                )
            except Exception as error:
                raise LegalTemporalOperationsReadServiceError(
                    "TEMPORAL_DEADLINE_READ_FAILED",
                    error,
                ) from error

            deadlines.extend(
                values
            )

        try:
            return (
                compose_legal_temporal_operations_projection(
                    productive_work=productive_work,
                    deadlines=tuple(deadlines),
                )
            )
        except LegalTemporalOperationsProjectionError as error:
            raise LegalTemporalOperationsReadServiceError(
                "TEMPORAL_PROJECTION_FAILED",
                error,
            ) from error


__all__ = [
    "VERSION",
    "LegalTemporalOperationsReadService",
    "LegalTemporalOperationsReadServiceError",
    "LegalTemporalOperationsReadServiceTransactionRequiredError",
]


# ARTIFACT: legal_temporal_operations_read_service.py
# VERSION: v1.0.0-P4-P1-LEGAL-TEMPORAL-OPERATIONS-READ-SERVICE
# AUTHORITY BOUNDARY: read-only composition of existing Productive Work visibility and canonical deadline evidence
# TENANT POSTURE: exact tenant and matter scope from authenticated Productive Work; no scope expansion
# FAIL-CLOSED POSTURE: missing active transaction, read failure, invalid provenance and projection mismatch reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
