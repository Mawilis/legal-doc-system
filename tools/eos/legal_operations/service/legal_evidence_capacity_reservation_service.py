"""WILSY OS atomic Legal Evidence capacity-reservation orchestration.

TITLE: Legal Evidence Capacity Reservation Service
VERSION: v1.0.0-L10A2Q-P5C-B-ATOMIC-CAPACITY-RESERVATION-SERVICE
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Serialize one tenant Legal Evidence capacity-admission decision, derive
    current remaining capacity from canonical evidence, subtract every durable
    ACTIVE reservation, and persist exactly one P5B reservation only when all
    capacity dimensions remain admissible.

EPITOME:
    EXACT DURABLE REPLAY
        -> VERIFY ORIGINAL CREATION COMMAND
        -> RETURN CURRENT DURABLE RESERVATION STATE
        != NEW CAPACITY CONSUMPTION

    FRESH INGESTION INTENT
        -> TENANT ADMISSION FENCE
        -> COMPLETE P3C USAGE WINDOW
        -> P4 REMAINING CAPACITY
        -> ALL ACTIVE P5B RESERVATIONS
        -> SINGLE-FILE + THREE-DIMENSION ADMISSION
        -> P5B RESERVATION
        != PROVIDER WRITE
        != USAGE COMMITTED
        != AUTHORIZED AVAILABILITY

TRANSACTION:
    The caller owns one already-active Mongo transaction spanning every
    registry operation. This service never starts, commits, aborts or retries a
    transaction. A caller handling a transient Mongo conflict must retry the
    entire transaction from a fresh snapshot.

REPLAY:
    Exact replay is resolved before the tenant admission fence is advanced.
    The original ACTIVE creation command is reconstructed from immutable
    persisted creation fields and the caller idempotency key, allowing P5B to
    verify exact replay even if the durable reservation has since entered a
    terminal lifecycle state.

CONCURRENCY:
    Every fresh admission advances the one tenant-only P5C-A fence before the
    complete usage and outstanding-reservation capacity decision. Competing
    transactions therefore cannot independently commit aggregate capacity
    decisions from the same tenant snapshot without a Mongo conflict.

EXPIRY:
    Every durable ACTIVE P5B reservation is outstanding capacity. Wall-clock
    expiry alone never releases capacity. P5D must durably transition the row
    before later admissions stop counting it.

TIME:
    command.reserved_at, tenant_profile.evaluated_at and the P3C/P4 evaluation
    instant are one exact UTC instant.

AUTHORITY BOUNDARY:
    Capacity admission and reservation orchestration only. No provider write,
    usage commit, IAM, retention execution, billing, payment, settlement or
    financial execution authority.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import re
from typing import Any, Callable, Final

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
    LegalEvidenceCapacityReservationStatus,
)
from tools.eos.legal_operations.domain.legal_evidence_remaining_capacity import (
    LegalEvidenceRemainingCapacity,
    derive_legal_evidence_remaining_capacity,
)
from tools.eos.legal_operations.registry.legal_evidence_capacity_admission_fence_registry import (
    LegalEvidenceCapacityAdmissionFenceNotFoundError,
)
from tools.eos.legal_operations.registry.legal_evidence_capacity_reservation_registry import (
    LegalEvidenceCapacityReservationNotFoundError,
)
from tools.eos.saas.billing.legal_evidence_capacity_commercial_policy import (
    get_legal_evidence_capacity_policy,
)
from tools.eos.saas.billing.legal_evidence_capacity_tenant_profile_resolver import (
    LegalEvidenceCapacityTenantProfile,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2Q-P5C-B-ATOMIC-CAPACITY-RESERVATION-SERVICE"
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


class LegalEvidenceCapacityReservationServiceError(RuntimeError):
    """Base P5C-B orchestration error."""


class LegalEvidenceCapacityAdmissionError(
    LegalEvidenceCapacityReservationServiceError
):
    """Fresh or replayed capacity admission failed closed."""


class LegalEvidenceCapacityTransactionRequiredError(
    LegalEvidenceCapacityReservationServiceError
):
    """Caller did not provide one already-active transaction."""


def _identity(name: str, value: object) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceCapacityAdmissionError(
            f"L10A2Q_P5CB_{name.upper()}_INVALID"
        )
    return value


def _tenant(value: object) -> str:
    tenant = _identity("tenant_id", value)
    if tenant.lower() in _FORBIDDEN_TENANTS:
        raise LegalEvidenceCapacityAdmissionError(
            "L10A2Q_P5CB_TENANT_REQUIRED"
        )
    return tenant


def _positive(name: str, value: object) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        raise LegalEvidenceCapacityAdmissionError(
            f"L10A2Q_P5CB_{name.upper()}_INVALID"
        )
    return value


def _utc(name: str, value: object) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceCapacityAdmissionError(
            f"L10A2Q_P5CB_{name.upper()}_INVALID"
        )
    return value.astimezone(timezone.utc)


def _active_transaction(session: Any) -> Any:
    if (
        session is None
        or not bool(
            getattr(session, "in_transaction", False)
        )
    ):
        raise LegalEvidenceCapacityTransactionRequiredError(
            "L10A2Q_P5CB_TRANSACTION_REQUIRED"
        )
    return session


@dataclass(frozen=True, slots=True)
class LegalEvidenceCapacityReservationCommand:
    """Immutable caller intent for exactly one capacity reservation."""

    tenant_id: str
    document_id: str
    reservation_id: str
    ingestion_intent_id: str
    idempotency_key: str
    reserved_storage_bytes: int
    reserved_ingress_bytes: int
    reserved_document_versions: int
    reserved_at: datetime
    expires_at: datetime

    def __post_init__(self) -> None:
        tenant = _tenant(self.tenant_id)
        document = _identity(
            "document_id",
            self.document_id,
        )
        reservation = _identity(
            "reservation_id",
            self.reservation_id,
        )
        intent = _identity(
            "ingestion_intent_id",
            self.ingestion_intent_id,
        )
        idempotency = _identity(
            "idempotency_key",
            self.idempotency_key,
        )

        storage = _positive(
            "reserved_storage_bytes",
            self.reserved_storage_bytes,
        )
        ingress = _positive(
            "reserved_ingress_bytes",
            self.reserved_ingress_bytes,
        )
        versions = _positive(
            "reserved_document_versions",
            self.reserved_document_versions,
        )

        reserved_at = _utc(
            "reserved_at",
            self.reserved_at,
        )
        expires_at = _utc(
            "expires_at",
            self.expires_at,
        )

        if expires_at <= reserved_at:
            raise LegalEvidenceCapacityAdmissionError(
                "L10A2Q_P5CB_EXPIRY_INVALID"
            )

        object.__setattr__(
            self,
            "tenant_id",
            tenant,
        )
        object.__setattr__(
            self,
            "document_id",
            document,
        )
        object.__setattr__(
            self,
            "reservation_id",
            reservation,
        )
        object.__setattr__(
            self,
            "ingestion_intent_id",
            intent,
        )
        object.__setattr__(
            self,
            "idempotency_key",
            idempotency,
        )
        object.__setattr__(
            self,
            "reserved_storage_bytes",
            storage,
        )
        object.__setattr__(
            self,
            "reserved_ingress_bytes",
            ingress,
        )
        object.__setattr__(
            self,
            "reserved_document_versions",
            versions,
        )
        object.__setattr__(
            self,
            "reserved_at",
            reserved_at,
        )
        object.__setattr__(
            self,
            "expires_at",
            expires_at,
        )


class LegalEvidenceCapacityReservationService:
    """Coordinate exact replay or one serialized fresh capacity reservation."""

    __slots__ = (
        "_fence_registry",
        "_usage_registry",
        "_reservation_registry",
        "_remaining_capacity_deriver",
    )

    def __init__(
        self,
        *,
        fence_registry: Any,
        usage_registry: Any,
        reservation_registry: Any,
        remaining_capacity_deriver: Callable[..., LegalEvidenceRemainingCapacity] = (
            derive_legal_evidence_remaining_capacity
        ),
    ) -> None:
        self._fence_registry = fence_registry
        self._usage_registry = usage_registry
        self._reservation_registry = reservation_registry
        self._remaining_capacity_deriver = remaining_capacity_deriver

    @staticmethod
    def _validate_profile(
        command: LegalEvidenceCapacityReservationCommand,
        tenant_profile: LegalEvidenceCapacityTenantProfile,
    ) -> None:
        if type(tenant_profile) is not LegalEvidenceCapacityTenantProfile:
            raise LegalEvidenceCapacityAdmissionError(
                "L10A2Q_P5CB_TENANT_PROFILE_REQUIRED"
            )

        if tenant_profile.tenant_id != command.tenant_id:
            raise LegalEvidenceCapacityAdmissionError(
                "L10A2Q_P5CB_TENANT_PROFILE_MISMATCH"
            )

        if (
            tenant_profile.evaluated_at.astimezone(timezone.utc)
            != command.reserved_at.astimezone(timezone.utc)
        ):
            raise LegalEvidenceCapacityAdmissionError(
                "L10A2Q_P5CB_EVALUATION_TIME_MISMATCH"
            )

    @staticmethod
    def _replay_probe(
        command: LegalEvidenceCapacityReservationCommand,
        persisted: LegalEvidenceCapacityReservation,
    ) -> LegalEvidenceCapacityReservation:
        if (
            persisted.tenant_id != command.tenant_id
            or persisted.document_id != command.document_id
            or persisted.reservation_id != command.reservation_id
            or persisted.ingestion_intent_id != command.ingestion_intent_id
            or persisted.reserved_storage_bytes
            != command.reserved_storage_bytes
            or persisted.reserved_ingress_bytes
            != command.reserved_ingress_bytes
            or persisted.reserved_document_versions
            != command.reserved_document_versions
            or persisted.reserved_at != command.reserved_at
            or persisted.expires_at != command.expires_at
        ):
            raise LegalEvidenceCapacityAdmissionError(
                "L10A2Q_P5CB_REPLAY_COMMAND_MISMATCH"
            )

        return LegalEvidenceCapacityReservation(
            tenant_id=persisted.tenant_id,
            document_id=persisted.document_id,
            reservation_id=persisted.reservation_id,
            ingestion_intent_id=persisted.ingestion_intent_id,
            remaining_capacity_fingerprint=(
                persisted.remaining_capacity_fingerprint
            ),
            reserved_storage_bytes=persisted.reserved_storage_bytes,
            reserved_ingress_bytes=persisted.reserved_ingress_bytes,
            reserved_document_versions=persisted.reserved_document_versions,
            reserved_at=persisted.reserved_at,
            expires_at=persisted.expires_at,
            status=LegalEvidenceCapacityReservationStatus.ACTIVE,
        )

    def reserve(
        self,
        *,
        command: LegalEvidenceCapacityReservationCommand,
        tenant_profile: LegalEvidenceCapacityTenantProfile,
        session: Any,
    ) -> LegalEvidenceCapacityReservation:
        """Return exact replay or atomically participate in one fresh admission."""
        tx = _active_transaction(session)

        if type(command) is not LegalEvidenceCapacityReservationCommand:
            raise LegalEvidenceCapacityAdmissionError(
                "L10A2Q_P5CB_COMMAND_REQUIRED"
            )

        self._validate_profile(
            command,
            tenant_profile,
        )

        # Replay is checked before any fence advancement or capacity read. The
        # P5B creation-command fingerprint remains the final authority on whether
        # the supplied idempotency key is an exact original-command replay.
        try:
            persisted = self._reservation_registry.get(
                tenant_id=command.tenant_id,
                reservation_id=command.reservation_id,
                session=tx,
            )
        except LegalEvidenceCapacityReservationNotFoundError:
            persisted = None

        if persisted is not None:
            if type(persisted) is not LegalEvidenceCapacityReservation:
                raise LegalEvidenceCapacityAdmissionError(
                    "L10A2Q_P5CB_REPLAY_RECORD_INVALID"
                )

            probe = self._replay_probe(
                command,
                persisted,
            )
            return self._reservation_registry.create_or_replay(
                probe,
                idempotency_key=command.idempotency_key,
                session=tx,
            )

        policy = get_legal_evidence_capacity_policy(
            tenant_profile.profile
        )

        if (
            command.reserved_storage_bytes
            > policy.single_file_max_bytes
        ):
            raise LegalEvidenceCapacityAdmissionError(
                "L10A2Q_P5CB_SINGLE_FILE_LIMIT_EXCEEDED"
            )

        # A fresh admission must first advance the one tenant-only serialization
        # fence. Missing fence means this transaction attempts revision 1.
        try:
            current_fence = self._fence_registry.get(
                tenant_id=command.tenant_id,
                session=tx,
            )
        except LegalEvidenceCapacityAdmissionFenceNotFoundError:
            expected_revision = None
        else:
            expected_revision = current_fence.revision

        self._fence_registry.advance(
            tenant_id=command.tenant_id,
            expected_revision=expected_revision,
            coordination_reference=command.reservation_id,
            advanced_at=command.reserved_at,
            session=tx,
        )

        usage_window = (
            self._usage_registry.get_complete_window_for_p4(
                tenant_id=command.tenant_id,
                document_id=command.document_id,
                as_of=tenant_profile.evaluated_at,
                session=tx,
            )
        )

        remaining = self._remaining_capacity_deriver(
            tenant_profile=tenant_profile,
            policy=policy,
            usage_window=usage_window,
        )

        if type(remaining) is not LegalEvidenceRemainingCapacity:
            raise LegalEvidenceCapacityAdmissionError(
                "L10A2Q_P5CB_REMAINING_CAPACITY_REQUIRED"
            )

        if (
            remaining.tenant_id != command.tenant_id
            or remaining.document_id != command.document_id
            or remaining.evaluated_at.astimezone(timezone.utc)
            != command.reserved_at.astimezone(timezone.utc)
        ):
            raise LegalEvidenceCapacityAdmissionError(
                "L10A2Q_P5CB_REMAINING_CAPACITY_SCOPE_MISMATCH"
            )

        active = self._reservation_registry.list_active_reservations(
            tenant_id=command.tenant_id,
            session=tx,
        )

        outstanding_storage = 0
        outstanding_ingress = 0
        outstanding_document_versions = 0

        for reservation in active:
            if type(reservation) is not LegalEvidenceCapacityReservation:
                raise LegalEvidenceCapacityAdmissionError(
                    "L10A2Q_P5CB_ACTIVE_RESERVATION_INVALID"
                )

            if reservation.tenant_id != command.tenant_id:
                raise LegalEvidenceCapacityAdmissionError(
                    "L10A2Q_P5CB_ACTIVE_RESERVATION_TENANT_MISMATCH"
                )

            if (
                reservation.status
                is not LegalEvidenceCapacityReservationStatus.ACTIVE
            ):
                raise LegalEvidenceCapacityAdmissionError(
                    "L10A2Q_P5CB_ACTIVE_RESERVATION_STATE_INVALID"
                )

            outstanding_storage += (
                reservation.reserved_storage_bytes
            )
            outstanding_ingress += (
                reservation.reserved_ingress_bytes
            )

            if reservation.document_id == command.document_id:
                outstanding_document_versions += (
                    reservation.reserved_document_versions
                )

        available_storage = max(
            0,
            remaining.remaining_storage_bytes
            - outstanding_storage,
        )
        available_ingress = max(
            0,
            remaining.remaining_ingress_bytes
            - outstanding_ingress,
        )
        available_versions = max(
            0,
            remaining.remaining_document_versions
            - outstanding_document_versions,
        )

        if command.reserved_storage_bytes > available_storage:
            raise LegalEvidenceCapacityAdmissionError(
                "L10A2Q_P5CB_STORAGE_CAPACITY_EXCEEDED"
            )

        if command.reserved_ingress_bytes > available_ingress:
            raise LegalEvidenceCapacityAdmissionError(
                "L10A2Q_P5CB_INGRESS_CAPACITY_EXCEEDED"
            )

        if command.reserved_document_versions > available_versions:
            raise LegalEvidenceCapacityAdmissionError(
                "L10A2Q_P5CB_DOCUMENT_VERSION_CAPACITY_EXCEEDED"
            )

        reservation = LegalEvidenceCapacityReservation(
            tenant_id=command.tenant_id,
            document_id=command.document_id,
            reservation_id=command.reservation_id,
            ingestion_intent_id=command.ingestion_intent_id,
            remaining_capacity_fingerprint=remaining.fingerprint,
            reserved_storage_bytes=command.reserved_storage_bytes,
            reserved_ingress_bytes=command.reserved_ingress_bytes,
            reserved_document_versions=command.reserved_document_versions,
            reserved_at=command.reserved_at,
            expires_at=command.expires_at,
        )

        return self._reservation_registry.create_or_replay(
            reservation,
            idempotency_key=command.idempotency_key,
            session=tx,
        )


__all__ = [
    "VERSION",
    "LegalEvidenceCapacityAdmissionError",
    "LegalEvidenceCapacityReservationCommand",
    "LegalEvidenceCapacityReservationService",
    "LegalEvidenceCapacityReservationServiceError",
    "LegalEvidenceCapacityTransactionRequiredError",
]


# ARTIFACT: legal_evidence_capacity_reservation_service.py
# VERSION: v1.0.0-L10A2Q-P5C-B-ATOMIC-CAPACITY-RESERVATION-SERVICE
# AUTHORITY BOUNDARY: atomic capacity-admission/reservation orchestration only
# TENANT POSTURE: exact tenant/profile/usage/reservation agreement required
# REPLAY POSTURE: exact durable replay advances no fence and consumes no capacity
# TIME POSTURE: P2/P3C/P4/P5 reservation admission instant is exact
# EXPIRY POSTURE: ACTIVE remains outstanding until durable P5D transition
# PROVIDER POSTURE: no binary-provider operation exists in this service
# TRANSACTION POSTURE: caller owns one already-active transaction and retry scope
# RECONCILIATION POSTURE: P5D remains semantic lifecycle/reconciliation owner
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
