"""WILSY OS semantic Legal Evidence capacity-reservation lifecycle service.

TITLE: Legal Evidence Capacity Reservation Lifecycle Service
VERSION: v1.0.0-L10A2Q-P5D-SEMANTIC-RESERVATION-LIFECYCLE-SERVICE
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Reconcile one durable P5 reservation into CONSUMED, RELEASED or EXPIRED
    state while coordinating through the same tenant-only P5C-A admission
    fence used by fresh reservation admission.

EPITOME:
    ACTIVE RESERVATION
    + TENANT ADMISSION FENCE
    + CANONICAL CONTENT WHEN CONSUMING
    -> DURABLE TERMINAL RESERVATION

    CONSUMED
    -> EXACT P3 USAGE EVIDENCE REQUIRED

    RELEASED / EXPIRED
    -> NO USAGE EVIDENCE

    EXACT TERMINAL REPLAY
    -> NO FENCE ADVANCE
    -> NO SECOND TERMINAL MUTATION

TRANSACTION:
    The caller owns one already-active Mongo transaction spanning every
    registry read/write. This service never starts, commits, aborts or retries
    the transaction.

CONCURRENCY:
    Every fresh terminal transition advances the same tenant-only P5C-A fence
    before usage/reservation state changes, preventing capacity admission from
    racing invisibly with reservation release or consumption.

CONSUMPTION:
    Canonical LegalEvidenceContent must match the reservation tenant/document.
    Reserved storage bytes and ingress bytes must equal content_length.
    Reserved document versions must equal one. Content registration must occur
    no earlier than reservation creation and no later than the consume instant.
    Exact P3 usage evidence is persisted/replayed before ACTIVE -> CONSUMED.

RELEASE / EXPIRY:
    RELEASED and EXPIRED transitions never create usage observations.

REPLAY:
    Exact durable terminal status and terminal timestamp reconcile without
    advancing the tenant fence. CONSUMED replay additionally requires exact
    deterministic P3 usage replay for the supplied canonical content.

AUTHORITY BOUNDARY:
    Reservation lifecycle and usage reconciliation only. No binary provider,
    IAM, retention, legal-hold, billing, payment, settlement or financial
    execution authority.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timezone
import re
from typing import Any, Final

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
    LegalEvidenceCapacityReservationStatus,
)
from tools.eos.legal_operations.domain.legal_evidence_content import (
    LegalEvidenceContent,
)
from tools.eos.legal_operations.domain.legal_evidence_usage_observation import (
    observe_legal_evidence_usage,
)
from tools.eos.legal_operations.registry.legal_evidence_capacity_admission_fence_registry import (
    LegalEvidenceCapacityAdmissionFenceNotFoundError,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2Q-P5D-SEMANTIC-RESERVATION-LIFECYCLE-SERVICE"
)

_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,511}$"
)

_FORBIDDEN_TENANTS: Final[frozenset[str]] = frozenset(
    {
        "default",
        "global",
        "root",
        "*",
        "global_root",
    }
)


class LegalEvidenceCapacityReservationLifecycleError(RuntimeError):
    """Stable fail-closed P5D lifecycle/reconciliation error."""


class LegalEvidenceCapacityReservationLifecycleTransactionRequiredError(
    LegalEvidenceCapacityReservationLifecycleError
):
    """Caller did not provide one already-active transaction."""


def _identity(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceCapacityReservationLifecycleError(
            f"L10A2Q_P5D_{name.upper()}_INVALID"
        )
    return value


def _tenant(
    value: object,
) -> str:
    tenant = _identity(
        "tenant_id",
        value,
    )
    if tenant.lower() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceCapacityReservationLifecycleError(
            "L10A2Q_P5D_TENANT_REQUIRED"
        )
    return tenant


def _utc(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceCapacityReservationLifecycleError(
            f"L10A2Q_P5D_{name.upper()}_INVALID"
        )
    return value.astimezone(
        timezone.utc
    )


def _active_transaction(
    session: Any,
) -> Any:
    if (
        session is None
        or not bool(
            getattr(
                session,
                "in_transaction",
                False,
            )
        )
    ):
        raise (
            LegalEvidenceCapacityReservationLifecycleTransactionRequiredError(
                "L10A2Q_P5D_TRANSACTION_REQUIRED"
            )
        )
    return session


class LegalEvidenceCapacityReservationLifecycleService:
    """Coordinate semantic P5 reservation terminal-state reconciliation."""

    __slots__ = (
        "_fence_registry",
        "_reservation_registry",
        "_usage_registry",
    )

    def __init__(
        self,
        *,
        fence_registry: Any,
        reservation_registry: Any,
        usage_registry: Any,
    ) -> None:
        self._fence_registry = fence_registry
        self._reservation_registry = reservation_registry
        self._usage_registry = usage_registry

    @staticmethod
    def _require_reservation(
        *,
        tenant_id: str,
        reservation_id: str,
        reservation: object,
    ) -> LegalEvidenceCapacityReservation:
        if type(reservation) is not LegalEvidenceCapacityReservation:
            raise LegalEvidenceCapacityReservationLifecycleError(
                "L10A2Q_P5D_RESERVATION_REQUIRED"
            )

        if (
            reservation.tenant_id != tenant_id
            or reservation.reservation_id != reservation_id
        ):
            raise LegalEvidenceCapacityReservationLifecycleError(
                "L10A2Q_P5D_RESERVATION_SCOPE_MISMATCH"
            )

        return reservation

    @staticmethod
    def _validate_content(
        *,
        reservation: LegalEvidenceCapacityReservation,
        content: LegalEvidenceContent,
        consumed_at: datetime,
    ) -> None:
        if type(content) is not LegalEvidenceContent:
            raise LegalEvidenceCapacityReservationLifecycleError(
                "L10A2Q_P5D_CONTENT_REQUIRED"
            )

        if content.tenant_id != reservation.tenant_id:
            raise LegalEvidenceCapacityReservationLifecycleError(
                "L10A2Q_P5D_CONTENT_TENANT_MISMATCH"
            )

        if content.document_id != reservation.document_id:
            raise LegalEvidenceCapacityReservationLifecycleError(
                "L10A2Q_P5D_CONTENT_DOCUMENT_MISMATCH"
            )

        if (
            reservation.reserved_storage_bytes
            != content.content_length
            or reservation.reserved_ingress_bytes
            != content.content_length
            or reservation.reserved_document_versions
            != 1
        ):
            raise LegalEvidenceCapacityReservationLifecycleError(
                "L10A2Q_P5D_CONTENT_DIMENSION_MISMATCH"
            )

        registered_at = content.registered_at.astimezone(
            timezone.utc
        )

        if (
            registered_at
            < reservation.reserved_at.astimezone(timezone.utc)
            or registered_at
            > consumed_at
        ):
            raise LegalEvidenceCapacityReservationLifecycleError(
                "L10A2Q_P5D_CONTENT_TIME_MISMATCH"
            )

    def _advance_fence(
        self,
        *,
        tenant_id: str,
        reservation_id: str,
        observed_at: datetime,
        session: Any,
    ) -> None:
        try:
            current = self._fence_registry.get(
                tenant_id=tenant_id,
                session=session,
            )
        except LegalEvidenceCapacityAdmissionFenceNotFoundError:
            expected_revision = None
        else:
            expected_revision = current.revision

        self._fence_registry.advance(
            tenant_id=tenant_id,
            expected_revision=expected_revision,
            coordination_reference=reservation_id,
            advanced_at=observed_at,
            session=session,
        )

    @staticmethod
    def _terminal_time_matches(
        *,
        reservation: LegalEvidenceCapacityReservation,
        operation: str,
        observed_at: datetime,
    ) -> bool:
        if operation == "consume":
            return (
                reservation.status
                is LegalEvidenceCapacityReservationStatus.CONSUMED
                and reservation.consumed_at == observed_at
            )

        if operation == "release":
            return (
                reservation.status
                is LegalEvidenceCapacityReservationStatus.RELEASED
                and reservation.released_at == observed_at
            )

        if operation == "expire":
            return (
                reservation.status
                is LegalEvidenceCapacityReservationStatus.EXPIRED
                and reservation.expired_at == observed_at
            )

        raise LegalEvidenceCapacityReservationLifecycleError(
            "L10A2Q_P5D_OPERATION_INVALID"
        )

    def consume(
        self,
        *,
        tenant_id: str,
        reservation_id: str,
        content: LegalEvidenceContent,
        consumed_at: datetime,
        session: Any,
    ) -> LegalEvidenceCapacityReservation:
        """Reconcile ACTIVE -> CONSUMED with exact P3 usage evidence."""
        tx = _active_transaction(
            session
        )
        tenant = _tenant(
            tenant_id
        )
        identity = _identity(
            "reservation_id",
            reservation_id,
        )
        observed = _utc(
            "consumed_at",
            consumed_at,
        )

        reservation = self._require_reservation(
            tenant_id=tenant,
            reservation_id=identity,
            reservation=self._reservation_registry.get(
                tenant_id=tenant,
                reservation_id=identity,
                session=tx,
            ),
        )

        self._validate_content(
            reservation=reservation,
            content=content,
            consumed_at=observed,
        )

        observation = observe_legal_evidence_usage(
            content=content,
        )
        usage_idempotency_key = (
            "legal-evidence-capacity-consume:"
            f"{reservation.reservation_id}"
        )

        if (
            reservation.status
            is not LegalEvidenceCapacityReservationStatus.ACTIVE
        ):
            if not self._terminal_time_matches(
                reservation=reservation,
                operation="consume",
                observed_at=observed,
            ):
                raise LegalEvidenceCapacityReservationLifecycleError(
                    "L10A2Q_P5D_TERMINAL_REPLAY_MISMATCH"
                )

            self._usage_registry.create_or_replay(
                observation,
                idempotency_key=usage_idempotency_key,
                session=tx,
            )
            return reservation

        self._advance_fence(
            tenant_id=tenant,
            reservation_id=identity,
            observed_at=observed,
            session=tx,
        )

        self._usage_registry.create_or_replay(
            observation,
            idempotency_key=usage_idempotency_key,
            session=tx,
        )

        return self._reservation_registry.consume(
            reservation,
            observed,
            session=tx,
        )

    def release(
        self,
        *,
        tenant_id: str,
        reservation_id: str,
        released_at: datetime,
        session: Any,
    ) -> LegalEvidenceCapacityReservation:
        """Reconcile ACTIVE -> RELEASED without creating usage evidence."""
        tx = _active_transaction(
            session
        )
        tenant = _tenant(
            tenant_id
        )
        identity = _identity(
            "reservation_id",
            reservation_id,
        )
        observed = _utc(
            "released_at",
            released_at,
        )

        reservation = self._require_reservation(
            tenant_id=tenant,
            reservation_id=identity,
            reservation=self._reservation_registry.get(
                tenant_id=tenant,
                reservation_id=identity,
                session=tx,
            ),
        )

        if (
            reservation.status
            is not LegalEvidenceCapacityReservationStatus.ACTIVE
        ):
            if not self._terminal_time_matches(
                reservation=reservation,
                operation="release",
                observed_at=observed,
            ):
                raise LegalEvidenceCapacityReservationLifecycleError(
                    "L10A2Q_P5D_TERMINAL_REPLAY_MISMATCH"
                )
            return reservation

        self._advance_fence(
            tenant_id=tenant,
            reservation_id=identity,
            observed_at=observed,
            session=tx,
        )

        return self._reservation_registry.release(
            reservation,
            observed,
            session=tx,
        )

    def expire(
        self,
        *,
        tenant_id: str,
        reservation_id: str,
        expired_at: datetime,
        session: Any,
    ) -> LegalEvidenceCapacityReservation:
        """Reconcile ACTIVE -> EXPIRED without creating usage evidence."""
        tx = _active_transaction(
            session
        )
        tenant = _tenant(
            tenant_id
        )
        identity = _identity(
            "reservation_id",
            reservation_id,
        )
        observed = _utc(
            "expired_at",
            expired_at,
        )

        reservation = self._require_reservation(
            tenant_id=tenant,
            reservation_id=identity,
            reservation=self._reservation_registry.get(
                tenant_id=tenant,
                reservation_id=identity,
                session=tx,
            ),
        )

        if (
            reservation.status
            is not LegalEvidenceCapacityReservationStatus.ACTIVE
        ):
            if not self._terminal_time_matches(
                reservation=reservation,
                operation="expire",
                observed_at=observed,
            ):
                raise LegalEvidenceCapacityReservationLifecycleError(
                    "L10A2Q_P5D_TERMINAL_REPLAY_MISMATCH"
                )
            return reservation

        self._advance_fence(
            tenant_id=tenant,
            reservation_id=identity,
            observed_at=observed,
            session=tx,
        )

        return self._reservation_registry.expire(
            reservation,
            observed,
            session=tx,
        )


__all__ = [
    "VERSION",
    "LegalEvidenceCapacityReservationLifecycleError",
    "LegalEvidenceCapacityReservationLifecycleService",
    "LegalEvidenceCapacityReservationLifecycleTransactionRequiredError",
]


# ARTIFACT: legal_evidence_capacity_reservation_lifecycle_service.py
# VERSION: v1.0.0-L10A2Q-P5D-SEMANTIC-RESERVATION-LIFECYCLE-SERVICE
# AUTHORITY BOUNDARY: semantic reservation lifecycle/reconciliation only
# TENANT POSTURE: exact tenant/reservation/content binding
# CONCURRENCY POSTURE: fresh terminal mutation advances P5C-A tenant fence
# CONSUMPTION POSTURE: CONSUMED requires exact durable P3 usage evidence
# RELEASE POSTURE: RELEASED creates no usage evidence
# EXPIRY POSTURE: EXPIRED creates no usage evidence
# REPLAY POSTURE: exact terminal replay advances no fence
# PROVIDER POSTURE: no binary-provider operation exists
# TRANSACTION POSTURE: caller owns one already-active transaction
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
