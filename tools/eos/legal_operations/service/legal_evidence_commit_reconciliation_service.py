"""WILSY OS Legal Evidence commit-uncertainty reconciliation service.

TITLE: Legal Evidence Commit Reconciliation Service
VERSION: v1.0.0-L10A2R-C4C-COMMIT-RECONCILIATION-SERVICE
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations

PURPOSE:
    Reconcile one durable C4B commit uncertainty against canonical C2 metadata,
    P5 reservation state and P3 usage evidence, using C3 exact replay only when
    the durable control plane proves that recovery is admissible.

EPITOME:
    C4B DURABLE UNCERTAINTY
    + EXACT ORIGINAL WRITE INTENT
    + CURRENT C2 / P5 / P3 CONTROL-PLANE STATE
    -> COMMIT RECONCILIATION

    METADATA PRESENT + RESERVATION CONSUMED + USAGE PRESENT
    -> COMMITTED_CONFIRMED

    METADATA ABSENT + RESERVATION ACTIVE BEFORE EXPIRY
    -> C3 EXACT RECOVERY COMMIT
    -> COMMIT_RECOVERED

    METADATA ABSENT + RESERVATION ACTIVE AT/AFTER EXPIRY
    -> P5D EXPIRE
    -> PROVIDER_OBJECT_UNRESOLVED

    METADATA ABSENT + RESERVATION RELEASED/EXPIRED
    -> PROVIDER_OBJECT_UNRESOLVED

    PARTIAL OR CONTRADICTORY CONTROL-PLANE STATE
    -> FAIL CLOSED

    PROVIDER_OBJECT_UNRESOLVED
    != ORPHAN PROVEN
    != PROVIDER DELETE AUTHORIZED
    != RETENTION SATISFIED
    != LEGAL HOLD CLEARED
    != AUTHORIZED AVAILABILITY

TRANSACTION:
    Caller owns one already-active Mongo transaction spanning every read and any
    C3/P5D reconciliation mutation. This service never starts, commits, aborts
    or retries the transaction.

PROVIDER:
    No provider IO exists here. Provider-object evidence is reconstructed only
    from immutable C4A/C4B uncertainty evidence.

REPLAY:
    Existing committed state is verified without invoking C3. Missing metadata
    may invoke C3 only while the exact reservation remains ACTIVE and unexpired.
    Contradictory durable state is never healed.

AUTHORITY BOUNDARY:
    Commit-state reconciliation only. No provider deletion, retention/legal-hold
    decision, IAM, availability publication, billing, payment or settlement.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hmac
from typing import Any, Final

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
    LegalEvidenceCapacityReservationStatus,
)
from tools.eos.legal_operations.domain.legal_evidence_commit_uncertainty import (
    LegalEvidenceCommitUncertainty,
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
from tools.eos.legal_operations.domain.legal_evidence_usage_observation import (
    LegalEvidenceUsageObservation,
    observe_legal_evidence_usage,
)
from tools.eos.legal_operations.registry.legal_evidence_object_metadata_registry import (
    LegalEvidenceObjectMetadataRegistryNotFoundError,
)
from tools.eos.legal_operations.registry.legal_evidence_usage_observation_registry import (
    LegalEvidenceUsageObservationNotFoundError,
)
from tools.eos.legal_operations.service.legal_evidence_binary_storage_port import (
    LegalEvidenceBinaryObjectEvidence,
    LegalEvidenceBinaryStoragePortError,
    LegalEvidenceBinaryWriteIntent,
    validate_object_evidence_for_intent,
)
from tools.eos.legal_operations.service.legal_evidence_two_plane_commit_service import (
    LegalEvidenceTwoPlaneCommitResult,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4C-COMMIT-RECONCILIATION-SERVICE"
)


class LegalEvidenceCommitReconciliationOutcome(StrEnum):
    """Closed C4C reconciliation outcome vocabulary."""

    COMMITTED_CONFIRMED = "COMMITTED_CONFIRMED"
    COMMIT_RECOVERED = "COMMIT_RECOVERED"
    PROVIDER_OBJECT_UNRESOLVED = "PROVIDER_OBJECT_UNRESOLVED"


class LegalEvidenceCommitReconciliationError(RuntimeError):
    """Stable fail-closed C4C reconciliation error."""


class LegalEvidenceCommitReconciliationTransactionRequiredError(
    LegalEvidenceCommitReconciliationError
):
    """Caller did not provide one already-active transaction."""


def _active_transaction(
    session: Any,
) -> Any:
    if session is None:
        raise LegalEvidenceCommitReconciliationTransactionRequiredError(
            "L10A2R_C4C_TRANSACTION_REQUIRED"
        )

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
        raise LegalEvidenceCommitReconciliationTransactionRequiredError(
            "L10A2R_C4C_TRANSACTION_REQUIRED"
        )

    return session


def _utc(
    name: str,
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
        raise LegalEvidenceCommitReconciliationError(
            f"L10A2R_C4C_{name.upper()}_INVALID"
        )

    return value.astimezone(
        timezone.utc
    )


@dataclass(
    frozen=True,
    slots=True,
)
class LegalEvidenceCommitReconciliationResult:
    """Immutable bounded result of one C4C reconciliation attempt."""

    outcome: LegalEvidenceCommitReconciliationOutcome
    uncertainty: LegalEvidenceCommitUncertainty
    reservation: LegalEvidenceCapacityReservation
    content: LegalEvidenceContent | None = None
    metadata: LegalEvidenceObjectMetadata | None = None
    available: bool = False
    authorized_availability: bool = False
    orphan_proven: bool = False
    provider_delete_authorized: bool = False

    def __post_init__(
        self,
    ) -> None:
        if type(self.uncertainty) is not LegalEvidenceCommitUncertainty:
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_RESULT_UNCERTAINTY_INVALID"
            )

        if type(self.reservation) is not LegalEvidenceCapacityReservation:
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_RESULT_RESERVATION_INVALID"
            )

        if (
            self.available is not False
            or self.authorized_availability is not False
            or self.orphan_proven is not False
            or self.provider_delete_authorized is not False
        ):
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_LATER_AUTHORITY_FORBIDDEN"
            )

        committed = self.outcome in {
            LegalEvidenceCommitReconciliationOutcome.COMMITTED_CONFIRMED,
            LegalEvidenceCommitReconciliationOutcome.COMMIT_RECOVERED,
        }

        if committed:
            if (
                type(self.content) is not LegalEvidenceContent
                or type(self.metadata) is not LegalEvidenceObjectMetadata
                or self.reservation.status
                is not LegalEvidenceCapacityReservationStatus.CONSUMED
            ):
                raise LegalEvidenceCommitReconciliationError(
                    "L10A2R_C4C_COMMITTED_RESULT_INVALID"
                )
        else:
            if (
                self.content is not None
                or self.metadata is not None
            ):
                raise LegalEvidenceCommitReconciliationError(
                    "L10A2R_C4C_UNRESOLVED_RESULT_INVALID"
                )


class LegalEvidenceCommitReconciliationService:
    """Reconcile C4 uncertainty from canonical control-plane evidence."""

    __slots__ = (
        "_uncertainty_registry",
        "_metadata_registry",
        "_reservation_registry",
        "_usage_registry",
        "_lifecycle_service",
        "_two_plane_commit_service",
    )

    def __init__(
        self,
        *,
        uncertainty_registry: Any,
        metadata_registry: Any,
        reservation_registry: Any,
        usage_registry: Any,
        lifecycle_service: Any,
        two_plane_commit_service: Any,
    ) -> None:
        dependencies = {
            "uncertainty_registry":
                uncertainty_registry,
            "metadata_registry":
                metadata_registry,
            "reservation_registry":
                reservation_registry,
            "usage_registry":
                usage_registry,
            "lifecycle_service":
                lifecycle_service,
            "two_plane_commit_service":
                two_plane_commit_service,
        }

        for name, dependency in dependencies.items():
            if dependency is None:
                raise LegalEvidenceCommitReconciliationError(
                    "L10A2R_C4C_"
                    + name.upper()
                    + "_REQUIRED"
                )

        self._uncertainty_registry = (
            uncertainty_registry
        )
        self._metadata_registry = (
            metadata_registry
        )
        self._reservation_registry = (
            reservation_registry
        )
        self._usage_registry = (
            usage_registry
        )
        self._lifecycle_service = (
            lifecycle_service
        )
        self._two_plane_commit_service = (
            two_plane_commit_service
        )

    @staticmethod
    def _object_evidence(
        uncertainty: LegalEvidenceCommitUncertainty,
    ) -> LegalEvidenceBinaryObjectEvidence:
        try:
            return LegalEvidenceBinaryObjectEvidence(
                provider_name=uncertainty.provider_name,
                storage_reference=uncertainty.storage_reference,
                object_version_reference=(
                    uncertainty.object_version_reference
                ),
                provider_integrity_reference=(
                    uncertainty.provider_integrity_reference
                ),
                write_intent_fingerprint=(
                    uncertainty.write_intent_fingerprint
                ),
                content_length=uncertainty.content_length,
                content_fingerprint=(
                    uncertainty.content_fingerprint
                ),
            )
        except LegalEvidenceBinaryStoragePortError as error:
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_UNCERTAINTY_OBJECT_EVIDENCE_INVALID"
            ) from error

    @staticmethod
    def _validate_intent(
        *,
        uncertainty: LegalEvidenceCommitUncertainty,
        intent: LegalEvidenceBinaryWriteIntent,
        object_evidence: LegalEvidenceBinaryObjectEvidence,
    ) -> None:
        if type(intent) is not LegalEvidenceBinaryWriteIntent:
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_WRITE_INTENT_REQUIRED"
            )

        if (
            intent.tenant_id
            != uncertainty.tenant_id
            or intent.case_matter_id
            != uncertainty.case_matter_id
            or intent.document_id
            != uncertainty.document_id
            or intent.ingestion_reference
            != uncertainty.ingestion_intent_id
            or not hmac.compare_digest(
                intent.fingerprint,
                uncertainty.write_intent_fingerprint,
            )
        ):
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_WRITE_INTENT_MISMATCH"
            )

        try:
            validate_object_evidence_for_intent(
                intent=intent,
                evidence=object_evidence,
            )
        except LegalEvidenceBinaryStoragePortError as error:
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_OBJECT_SCOPE_MISMATCH"
            ) from error

        if not object_evidence.proves_stream(
            observed_length=uncertainty.content_length,
            observed_fingerprint=uncertainty.content_fingerprint,
        ):
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_OBJECT_CONTENT_MISMATCH"
            )

    @staticmethod
    def _content(
        *,
        uncertainty: LegalEvidenceCommitUncertainty,
        intent: LegalEvidenceBinaryWriteIntent,
        registered_at: datetime,
    ) -> LegalEvidenceContent:
        try:
            return register_observed_legal_evidence_content(
                tenant_id=uncertainty.tenant_id,
                case_matter_id=uncertainty.case_matter_id,
                document_id=uncertainty.document_id,
                media_type=intent.media_type,
                original_filename=intent.original_filename,
                observed_content_length=(
                    uncertainty.content_length
                ),
                observed_content_fingerprint=(
                    uncertainty.content_fingerprint
                ),
                source_evidence_reference=(
                    uncertainty.source_evidence_reference
                ),
                source_evidence_fingerprint=(
                    uncertainty.source_evidence_fingerprint
                ),
                registered_at=registered_at,
            )
        except LegalEvidenceContentError as error:
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_CONTENT_RECONSTRUCTION_INVALID"
            ) from error

    @staticmethod
    def _expected_metadata(
        *,
        content: LegalEvidenceContent,
        intent: LegalEvidenceBinaryWriteIntent,
        object_evidence: LegalEvidenceBinaryObjectEvidence,
    ) -> LegalEvidenceObjectMetadata:
        try:
            return bind_legal_evidence_object_metadata(
                content=content,
                intent=intent,
                object_evidence=object_evidence,
            )
        except LegalEvidenceObjectMetadataError as error:
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_METADATA_RECONSTRUCTION_INVALID"
            ) from error

    def reconcile(
        self,
        *,
        tenant_id: str,
        uncertainty_id: str,
        intent: LegalEvidenceBinaryWriteIntent,
        reconciled_at: datetime,
        session: Any,
    ) -> LegalEvidenceCommitReconciliationResult:
        """Reconcile one durable C4B uncertainty from canonical Mongo state."""
        tx = _active_transaction(
            session
        )
        observed_at = _utc(
            "reconciled_at",
            reconciled_at,
        )

        uncertainty = (
            self._uncertainty_registry.get(
                tenant_id=tenant_id,
                uncertainty_id=uncertainty_id,
                session=tx,
            )
        )

        if (
            type(uncertainty)
            is not LegalEvidenceCommitUncertainty
            or uncertainty.tenant_id != tenant_id
            or uncertainty.uncertainty_id
            != uncertainty_id
        ):
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_UNCERTAINTY_SCOPE_MISMATCH"
            )

        if observed_at < uncertainty.detected_at:
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_RECONCILED_AT_PRECEDES_UNCERTAINTY"
            )

        object_evidence = self._object_evidence(
            uncertainty
        )

        self._validate_intent(
            uncertainty=uncertainty,
            intent=intent,
            object_evidence=object_evidence,
        )

        reservation = (
            self._reservation_registry.get(
                tenant_id=uncertainty.tenant_id,
                reservation_id=uncertainty.reservation_id,
                session=tx,
            )
        )

        if (
            type(reservation)
            is not LegalEvidenceCapacityReservation
            or reservation.tenant_id
            != uncertainty.tenant_id
            or reservation.document_id
            != uncertainty.document_id
            or reservation.reservation_id
            != uncertainty.reservation_id
            or reservation.ingestion_intent_id
            != uncertainty.ingestion_intent_id
            or reservation.reserved_storage_bytes
            != uncertainty.content_length
            or reservation.reserved_ingress_bytes
            != uncertainty.content_length
            or reservation.reserved_document_versions
            != 1
        ):
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_RESERVATION_MISMATCH"
            )

        lookup_content = self._content(
            uncertainty=uncertainty,
            intent=intent,
            registered_at=uncertainty.detected_at,
        )

        try:
            metadata = self._metadata_registry.get(
                tenant_id=uncertainty.tenant_id,
                content_reference=(
                    lookup_content.content_reference
                ),
                session=tx,
            )
        except LegalEvidenceObjectMetadataRegistryNotFoundError:
            metadata = None

        if metadata is not None:
            if (
                reservation.status
                is not LegalEvidenceCapacityReservationStatus.CONSUMED
                or reservation.consumed_at is None
            ):
                raise LegalEvidenceCommitReconciliationError(
                    "L10A2R_C4C_CONTROL_PLANE_DIVERGENCE"
                )

            content = self._content(
                uncertainty=uncertainty,
                intent=intent,
                registered_at=metadata.registered_at,
            )

            expected_metadata = self._expected_metadata(
                content=content,
                intent=intent,
                object_evidence=object_evidence,
            )

            if metadata != expected_metadata:
                raise LegalEvidenceCommitReconciliationError(
                    "L10A2R_C4C_METADATA_MISMATCH"
                )

            if (
                reservation.consumed_at
                != content.registered_at
            ):
                raise LegalEvidenceCommitReconciliationError(
                    "L10A2R_C4C_COMMIT_TIME_DIVERGENCE"
                )

            expected_usage = (
                observe_legal_evidence_usage(
                    content=content,
                )
            )

            try:
                durable_usage = (
                    self._usage_registry.get(
                        tenant_id=uncertainty.tenant_id,
                        usage_observation_id=(
                            expected_usage.usage_observation_id
                        ),
                        session=tx,
                    )
                )
            except LegalEvidenceUsageObservationNotFoundError as error:
                raise LegalEvidenceCommitReconciliationError(
                    "L10A2R_C4C_CONTROL_PLANE_DIVERGENCE"
                ) from error

            if (
                type(durable_usage)
                is not LegalEvidenceUsageObservation
                or durable_usage != expected_usage
            ):
                raise LegalEvidenceCommitReconciliationError(
                    "L10A2R_C4C_USAGE_MISMATCH"
                )

            return LegalEvidenceCommitReconciliationResult(
                outcome=(
                    LegalEvidenceCommitReconciliationOutcome
                    .COMMITTED_CONFIRMED
                ),
                uncertainty=uncertainty,
                reservation=reservation,
                content=content,
                metadata=metadata,
            )

        if (
            reservation.status
            is LegalEvidenceCapacityReservationStatus.CONSUMED
        ):
            raise LegalEvidenceCommitReconciliationError(
                "L10A2R_C4C_CONTROL_PLANE_DIVERGENCE"
            )

        if (
            reservation.status
            is LegalEvidenceCapacityReservationStatus.ACTIVE
        ):
            if observed_at >= reservation.expires_at:
                expired = (
                    self._lifecycle_service.expire(
                        tenant_id=reservation.tenant_id,
                        reservation_id=reservation.reservation_id,
                        expired_at=observed_at,
                        session=tx,
                    )
                )

                if (
                    type(expired)
                    is not LegalEvidenceCapacityReservation
                    or expired.status
                    is not LegalEvidenceCapacityReservationStatus.EXPIRED
                ):
                    raise LegalEvidenceCommitReconciliationError(
                        "L10A2R_C4C_EXPIRY_RECONCILIATION_INVALID"
                    )

                return LegalEvidenceCommitReconciliationResult(
                    outcome=(
                        LegalEvidenceCommitReconciliationOutcome
                        .PROVIDER_OBJECT_UNRESOLVED
                    ),
                    uncertainty=uncertainty,
                    reservation=expired,
                )

            recovered = (
                self._two_plane_commit_service.commit(
                    reservation=reservation,
                    intent=intent,
                    object_evidence=object_evidence,
                    observed_content_length=(
                        uncertainty.content_length
                    ),
                    observed_content_fingerprint=(
                        uncertainty.content_fingerprint
                    ),
                    source_evidence_reference=(
                        uncertainty.source_evidence_reference
                    ),
                    source_evidence_fingerprint=(
                        uncertainty.source_evidence_fingerprint
                    ),
                    committed_at=observed_at,
                    session=tx,
                )
            )

            if (
                type(recovered)
                is not LegalEvidenceTwoPlaneCommitResult
                or recovered.reservation.status
                is not LegalEvidenceCapacityReservationStatus.CONSUMED
                or recovered.available is not False
                or recovered.authorized_availability is not False
            ):
                raise LegalEvidenceCommitReconciliationError(
                    "L10A2R_C4C_RECOVERY_RESULT_INVALID"
                )

            return LegalEvidenceCommitReconciliationResult(
                outcome=(
                    LegalEvidenceCommitReconciliationOutcome
                    .COMMIT_RECOVERED
                ),
                uncertainty=uncertainty,
                reservation=recovered.reservation,
                content=recovered.content,
                metadata=recovered.metadata,
            )

        if reservation.status in {
            LegalEvidenceCapacityReservationStatus.RELEASED,
            LegalEvidenceCapacityReservationStatus.EXPIRED,
        }:
            return LegalEvidenceCommitReconciliationResult(
                outcome=(
                    LegalEvidenceCommitReconciliationOutcome
                    .PROVIDER_OBJECT_UNRESOLVED
                ),
                uncertainty=uncertainty,
                reservation=reservation,
            )

        raise LegalEvidenceCommitReconciliationError(
            "L10A2R_C4C_RESERVATION_STATE_INVALID"
        )


__all__ = [
    "VERSION",
    "LegalEvidenceCommitReconciliationError",
    "LegalEvidenceCommitReconciliationOutcome",
    "LegalEvidenceCommitReconciliationResult",
    "LegalEvidenceCommitReconciliationService",
    "LegalEvidenceCommitReconciliationTransactionRequiredError",
]


# ARTIFACT: legal_evidence_commit_reconciliation_service.py
# VERSION: v1.0.0-L10A2R-C4C-COMMIT-RECONCILIATION-SERVICE
# AUTHORITY BOUNDARY: control-plane commit reconciliation only
# UNCERTAINTY POSTURE: durable uncertainty is never orphan proof
# C3 POSTURE: only ACTIVE/unexpired missing-metadata state may invoke exact C3
# PARTIAL STATE POSTURE: contradictory metadata/reservation/usage fails closed
# P5D POSTURE: ACTIVE expired state may reconcile only to EXPIRED
# PROVIDER POSTURE: immutable evidence only; no provider IO or deletion
# RETENTION POSTURE: no retention or legal-hold authority
# AVAILABILITY POSTURE: every result remains unavailable
# TRANSACTION POSTURE: caller owns one already-active transaction
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
