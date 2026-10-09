"""WILSY OS Legal Evidence two-plane commit orchestration service.

TITLE: Legal Evidence Two-Plane Commit Service
VERSION: v1.0.0-L10A2R-C3-TWO-PLANE-COMMIT-SERVICE
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Compose already-certified provider-object evidence, WILSY-observed stream
    identity, canonical LegalEvidenceContent, immutable C1 object metadata,
    C2 metadata durability, and P5D reservation/usage reconciliation.

EPITOME:
    ACTIVE RESERVATION
    + VERIFIED PROVIDER OBJECT EVIDENCE
    + WILSY STREAM LENGTH / SHA3-512
    -> CANONICAL CONTENT
    -> C1 OBJECT METADATA
    -> C2 METADATA COMMIT
    -> P5D RESERVATION / USAGE COMMIT
    -> TWO-PLANE COMMITTED RESULT

    TWO-PLANE COMMITTED
    != AUTHORIZED AVAILABILITY
    != IAM AUTHORIZED
    != RETENTION AUTHORIZED
    != LEGAL HOLD CLEARED
    != BILLING / PAYMENT / SETTLEMENT

PROVIDER BOUNDARY:
    Provider execution has already occurred before this service is called.
    This service never begins, uploads, completes, inspects, aborts, deletes or
    otherwise executes provider operations.

TRANSACTION:
    The caller owns one already-active Mongo transaction spanning C2 metadata
    durability and P5D usage/reservation reconciliation. This service never
    starts, commits, aborts or retries that transaction.

REPLAY:
    C2 owns exact immutable metadata replay. P5D owns exact consumed reservation
    and P3 usage replay. This service accepts only exact returned values from
    those certified components and rejects divergence.

FAIL CLOSED:
    Missing transaction, wrong domain types, tenant/document/ingestion scope
    mismatch, reservation-dimension mismatch, provider-object/write-intent
    mismatch, WILSY stream mismatch, metadata replay divergence or lifecycle
    reconciliation divergence rejects without manufacturing commit success.

AUTHORITY BOUNDARY:
    Exact two-plane commit composition only. No authenticated HTTP authority,
    IAM grant, retention/legal-hold decision, availability publication, Court,
    Legal lifecycle advancement, billing, payment, execution or settlement.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hmac
import re
from typing import Any, Final

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
    LegalEvidenceCapacityReservationStatus,
)
from tools.eos.legal_operations.domain.legal_evidence_content import (
    LegalEvidenceContent,
    LegalEvidenceContentError,
    register_observed_legal_evidence_content,
)
from tools.eos.legal_operations.domain.legal_evidence_object_metadata import (
    LegalEvidenceObjectMetadata,
    LegalEvidenceObjectMetadataError,
    bind_legal_evidence_object_metadata,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryStoragePortError,
    LegalEvidenceBinaryWriteIntent,
    validate_object_evidence_for_intent,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C3-TWO-PLANE-COMMIT-SERVICE"
)

_IDENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:@/-]{0,511}$"
)
_SHA3_RE: Final[re.Pattern[str]] = re.compile(
    r"^[0-9a-f]{128}$"
)


class LegalEvidenceTwoPlaneCommitError(RuntimeError):
    """Stable fail-closed C3 orchestration error."""


class LegalEvidenceTwoPlaneCommitTransactionRequiredError(
    LegalEvidenceTwoPlaneCommitError
):
    """Caller did not provide one already-active Mongo transaction."""


def _active_transaction(
    session: Any,
) -> Any:
    marker = getattr(
        session,
        "in_transaction",
        False,
    )

    try:
        active = (
            marker()
            if callable(marker)
            else marker
        )
    except (
        AttributeError,
        TypeError,
    ):
        active = False

    if active is not True:
        raise (
            LegalEvidenceTwoPlaneCommitTransactionRequiredError(
                "L10A2R_C3_TRANSACTION_REQUIRED"
            )
        )

    return session


def _identity(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or value != value.strip()
        or _IDENTITY_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceTwoPlaneCommitError(
            f"L10A2R_C3_{name.upper()}_INVALID"
        )

    return value


def _sha3(
    name: str,
    value: object,
) -> str:
    if (
        not isinstance(value, str)
        or _SHA3_RE.fullmatch(value) is None
    ):
        raise LegalEvidenceTwoPlaneCommitError(
            f"L10A2R_C3_{name.upper()}_INVALID"
        )

    return value


def _positive_int(
    name: str,
    value: object,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value <= 0
    ):
        raise LegalEvidenceTwoPlaneCommitError(
            f"L10A2R_C3_{name.upper()}_INVALID"
        )

    return value


def _utc(
    name: str,
    value: object,
) -> datetime:
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceTwoPlaneCommitError(
            f"L10A2R_C3_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidenceTwoPlaneCommitResult:
    """Immutable result proving only the bounded C3 commit composition."""

    content: LegalEvidenceContent
    metadata: LegalEvidenceObjectMetadata
    reservation: LegalEvidenceCapacityReservation
    available: bool = False
    authorized_availability: bool = False

    def __post_init__(
        self,
    ) -> None:
        if type(self.content) is not LegalEvidenceContent:
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_RESULT_CONTENT_INVALID"
            )

        if type(self.metadata) is not LegalEvidenceObjectMetadata:
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_RESULT_METADATA_INVALID"
            )

        if type(self.reservation) is not LegalEvidenceCapacityReservation:
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_RESULT_RESERVATION_INVALID"
            )

        if (
            self.reservation.status
            is not LegalEvidenceCapacityReservationStatus.CONSUMED
        ):
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_RESULT_RESERVATION_NOT_CONSUMED"
            )

        if (
            self.available is not False
            or self.authorized_availability is not False
        ):
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_AVAILABILITY_AUTHORITY_FORBIDDEN"
            )

        if (
            self.content.tenant_id
            != self.metadata.tenant_id
            or self.content.case_matter_id
            != self.metadata.case_matter_id
            or self.content.document_id
            != self.metadata.document_id
            or self.content.content_reference
            != self.metadata.content_reference
            or self.content.content_length
            != self.metadata.content_length
            or not hmac.compare_digest(
                self.content.content_fingerprint,
                self.metadata.content_fingerprint,
            )
        ):
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_RESULT_METADATA_MISMATCH"
            )

        if (
            self.reservation.tenant_id
            != self.content.tenant_id
            or self.reservation.document_id
            != self.content.document_id
        ):
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_RESULT_RESERVATION_SCOPE_MISMATCH"
            )


class LegalEvidenceTwoPlaneCommitService:
    """Compose C3 canonical metadata commit and P5D consumption atomically."""

    __slots__ = (
        "_metadata_registry",
        "_lifecycle_service",
    )

    def __init__(
        self,
        *,
        metadata_registry: Any,
        lifecycle_service: Any,
    ) -> None:
        if metadata_registry is None:
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_METADATA_REGISTRY_REQUIRED"
            )

        if lifecycle_service is None:
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_LIFECYCLE_SERVICE_REQUIRED"
            )

        self._metadata_registry = metadata_registry
        self._lifecycle_service = lifecycle_service

    @staticmethod
    def _validate_reservation_scope(
        *,
        reservation: LegalEvidenceCapacityReservation,
        intent: LegalEvidenceBinaryWriteIntent,
    ) -> None:
        if (
            reservation.tenant_id
            != intent.tenant_id
            or reservation.document_id
            != intent.document_id
            or reservation.ingestion_intent_id
            != intent.ingestion_reference
        ):
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_RESERVATION_SCOPE_MISMATCH"
            )

    @staticmethod
    def _validate_reservation_dimensions(
        *,
        reservation: LegalEvidenceCapacityReservation,
        observed_content_length: int,
    ) -> None:
        if (
            reservation.reserved_storage_bytes
            != observed_content_length
            or reservation.reserved_ingress_bytes
            != observed_content_length
            or reservation.reserved_document_versions
            != 1
        ):
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_RESERVATION_DIMENSION_MISMATCH"
            )

    @staticmethod
    def _validate_object(
        *,
        intent: LegalEvidenceBinaryWriteIntent,
        object_evidence: LegalEvidenceBinaryObjectEvidence,
        observed_content_length: int,
        observed_content_fingerprint: str,
    ) -> None:
        try:
            validate_object_evidence_for_intent(
                intent=intent,
                evidence=object_evidence,
            )
        except LegalEvidenceBinaryStoragePortError as error:
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_OBJECT_SCOPE_MISMATCH"
            ) from error

        if not object_evidence.proves_stream(
            observed_length=observed_content_length,
            observed_fingerprint=observed_content_fingerprint,
        ):
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_OBJECT_CONTENT_MISMATCH"
            )

    def commit(
        self,
        *,
        reservation: LegalEvidenceCapacityReservation,
        intent: LegalEvidenceBinaryWriteIntent,
        object_evidence: LegalEvidenceBinaryObjectEvidence,
        observed_content_length: int,
        observed_content_fingerprint: str,
        source_evidence_reference: str,
        source_evidence_fingerprint: str,
        committed_at: datetime,
        session: Any,
    ) -> LegalEvidenceTwoPlaneCommitResult:
        """Commit canonical metadata then consume reservation/usage evidence."""
        tx = _active_transaction(
            session
        )

        if type(reservation) is not LegalEvidenceCapacityReservation:
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_RESERVATION_REQUIRED"
            )

        if type(intent) is not LegalEvidenceBinaryWriteIntent:
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_WRITE_INTENT_REQUIRED"
            )

        if type(object_evidence) is not LegalEvidenceBinaryObjectEvidence:
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_OBJECT_EVIDENCE_REQUIRED"
            )

        observed_length = _positive_int(
            "observed_content_length",
            observed_content_length,
        )
        observed_fingerprint = _sha3(
            "observed_content_fingerprint",
            observed_content_fingerprint,
        )
        source_reference = _identity(
            "source_evidence_reference",
            source_evidence_reference,
        )
        source_fingerprint = _sha3(
            "source_evidence_fingerprint",
            source_evidence_fingerprint,
        )
        observed_at = _utc(
            "committed_at",
            committed_at,
        )

        self._validate_reservation_scope(
            reservation=reservation,
            intent=intent,
        )

        self._validate_reservation_dimensions(
            reservation=reservation,
            observed_content_length=observed_length,
        )

        if observed_length > intent.admitted_max_content_length:
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_INTENT_CONTENT_LIMIT_EXCEEDED"
            )

        self._validate_object(
            intent=intent,
            object_evidence=object_evidence,
            observed_content_length=observed_length,
            observed_content_fingerprint=observed_fingerprint,
        )

        try:
            content = register_observed_legal_evidence_content(
                tenant_id=intent.tenant_id,
                case_matter_id=intent.case_matter_id,
                document_id=intent.document_id,
                media_type=intent.media_type,
                original_filename=intent.original_filename,
                observed_content_length=observed_length,
                observed_content_fingerprint=observed_fingerprint,
                source_evidence_reference=source_reference,
                source_evidence_fingerprint=source_fingerprint,
                registered_at=observed_at,
            )
        except LegalEvidenceContentError as error:
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_CONTENT_IDENTITY_INVALID"
            ) from error

        try:
            metadata = bind_legal_evidence_object_metadata(
                content=content,
                intent=intent,
                object_evidence=object_evidence,
            )
        except LegalEvidenceObjectMetadataError as error:
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_METADATA_BINDING_INVALID"
            ) from error

        persisted_metadata = (
            self._metadata_registry.create_or_replay(
                metadata,
                session=tx,
            )
        )

        if (
            type(persisted_metadata)
            is not LegalEvidenceObjectMetadata
            or persisted_metadata != metadata
        ):
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_METADATA_REPLAY_MISMATCH"
            )

        consumed_reservation = (
            self._lifecycle_service.consume(
                tenant_id=reservation.tenant_id,
                reservation_id=reservation.reservation_id,
                content=content,
                consumed_at=observed_at,
                session=tx,
            )
        )

        if (
            type(consumed_reservation)
            is not LegalEvidenceCapacityReservation
        ):
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_RESERVATION_RECONCILIATION_INVALID"
            )

        if (
            consumed_reservation.tenant_id
            != reservation.tenant_id
            or consumed_reservation.document_id
            != reservation.document_id
            or consumed_reservation.reservation_id
            != reservation.reservation_id
            or consumed_reservation.ingestion_intent_id
            != reservation.ingestion_intent_id
            or consumed_reservation.status
            is not LegalEvidenceCapacityReservationStatus.CONSUMED
            or consumed_reservation.consumed_at
            != observed_at
        ):
            raise LegalEvidenceTwoPlaneCommitError(
                "L10A2R_C3_RESERVATION_RECONCILIATION_MISMATCH"
            )

        return LegalEvidenceTwoPlaneCommitResult(
            content=content,
            metadata=persisted_metadata,
            reservation=consumed_reservation,
            available=False,
            authorized_availability=False,
        )


__all__ = [
    "VERSION",
    "LegalEvidenceTwoPlaneCommitError",
    "LegalEvidenceTwoPlaneCommitResult",
    "LegalEvidenceTwoPlaneCommitService",
    "LegalEvidenceTwoPlaneCommitTransactionRequiredError",
]


# ARTIFACT: legal_evidence_two_plane_commit_service.py
# VERSION: v1.0.0-L10A2R-C3-TWO-PLANE-COMMIT-SERVICE
# AUTHORITY BOUNDARY: exact two-plane commit composition only
# PROVIDER POSTURE: accepts verified immutable evidence; performs no provider IO
# TRANSACTION POSTURE: caller owns active transaction spanning C2 + P5D
# METADATA POSTURE: C2 metadata commit precedes P5D usage/reservation consume
# STREAM POSTURE: exact WILSY-observed length/SHA3 is canonical content identity
# REPLAY POSTURE: exact C2 + P5D replay only; divergence fails closed
# AVAILABILITY POSTURE: committed result remains unavailable
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
