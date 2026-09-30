"""Direct certificate for atomic Legal Evidence capacity reservation orchestration.

TITLE: Legal Evidence Capacity Reservation Service Certificate
VERSION: v1.0.0-L10A2Q-P5C-B-ATOMIC-CAPACITY-RESERVATION-SERVICE-CERT
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Freeze the orchestration contract that serializes one tenant admission
    decision, combines canonical P4 remaining capacity with every durable ACTIVE
    P5B reservation, and persists exactly one new reservation only when all
    capacity dimensions remain admissible.

EPITOME:
    EXACT REPLAY
        -> RETURN DURABLE RESERVATION
        != NEW CAPACITY CONSUMPTION

    FRESH INGESTION INTENT
        -> TENANT ADMISSION FENCE
        -> COMPLETE P3C USAGE
        -> P4 REMAINING CAPACITY
        -> ALL ACTIVE P5B RESERVATIONS
        -> THREE-DIMENSION ADMISSION
        -> P5B RESERVATION
        != PROVIDER WRITE
        != USAGE COMMITTED
        != AUTHORIZED AVAILABILITY

CONCURRENCY:
    Fresh admissions MUST advance the one tenant-only P5C-A fence before their
    final capacity snapshot/decision. Exact replay MUST NOT advance that fence.

EXPIRY:
    Every durable ACTIVE P5B reservation consumes admission capacity, including
    ACTIVE rows whose expires_at is in the past. Only a durable P5D lifecycle
    transition releases such capacity.

AUTHORITY BOUNDARY:
    Capacity-admission and reservation orchestration only. No binary provider,
    IAM, retention, usage-commit, billing, payment, settlement or financial
    execution authority.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
)
from tools.eos.legal_operations.domain.legal_evidence_remaining_capacity import (
    LegalEvidenceRemainingCapacity,
)
from tools.eos.legal_operations.service.legal_evidence_capacity_reservation_service import (
    LegalEvidenceCapacityAdmissionError,
    LegalEvidenceCapacityReservationCommand,
    LegalEvidenceCapacityReservationService,
)
from tools.eos.saas.billing.legal_evidence_capacity_policy_contract import (
    LegalEvidenceCapacityProfile,
)
from tools.eos.saas.billing.legal_evidence_capacity_commercial_policy import (
    get_legal_evidence_capacity_policy,
)
from tools.eos.saas.billing.legal_evidence_capacity_tenant_profile_resolver import (
    LegalEvidenceCapacityTenantProfile,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId


AT = datetime(
    2026,
    9,
    30,
    6,
    15,
    0,
    123456,
    tzinfo=timezone.utc,
)
EXPIRES = AT + timedelta(minutes=15)
SHA_A = "a" * 128
SHA_B = "b" * 128
SHA_C = "c" * 128


class Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


def _profile(
    *,
    tenant_id: str = "tenant-p5cb",
    evaluated_at: datetime = AT,
    profile: LegalEvidenceCapacityProfile = (
        LegalEvidenceCapacityProfile.STARTER
    ),
) -> LegalEvidenceCapacityTenantProfile:
    return LegalEvidenceCapacityTenantProfile(
        tenant_id=tenant_id,
        subscription_id="subscription-p5cb",
        plan_id="plan-p5cb",
        plan_catalogue_version=1,
        subscription_proof_hash=SHA_A,
        entitlement_id="entitlement-p5cb",
        entitlement_revision=1,
        entitlement_fingerprint=SHA_B,
        product_id=TenantProductId.LEGAL_OPERATIONS,
        profile=profile,
        evaluated_at=evaluated_at,
    )


def _command(
    *,
    tenant_id: str = "tenant-p5cb",
    document_id: str = "document-p5cb",
    reservation_id: str = "reservation-p5cb",
    ingestion_intent_id: str = "ingestion-p5cb",
    idempotency_key: str = "idem-p5cb",
    storage_bytes: int = 100,
    ingress_bytes: int = 100,
    document_versions: int = 1,
    reserved_at: datetime = AT,
    expires_at: datetime = EXPIRES,
) -> LegalEvidenceCapacityReservationCommand:
    return LegalEvidenceCapacityReservationCommand(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id=reservation_id,
        ingestion_intent_id=ingestion_intent_id,
        idempotency_key=idempotency_key,
        reserved_storage_bytes=storage_bytes,
        reserved_ingress_bytes=ingress_bytes,
        reserved_document_versions=document_versions,
        reserved_at=reserved_at,
        expires_at=expires_at,
    )


def _remaining(
    *,
    tenant_id: str = "tenant-p5cb",
    document_id: str = "document-p5cb",
    storage_remaining: int = 1000,
    ingress_remaining: int = 1000,
    versions_remaining: int = 10,
) -> LegalEvidenceRemainingCapacity:
    return LegalEvidenceRemainingCapacity(
        tenant_id=tenant_id,
        document_id=document_id,
        evaluated_at=AT,
        tenant_profile_fingerprint=SHA_A,
        capacity_policy_fingerprint=SHA_B,
        usage_window_fingerprint=SHA_C,
        tenant_storage_limit_bytes=2000,
        tenant_storage_consumed_bytes=2000 - storage_remaining,
        remaining_storage_bytes=storage_remaining,
        storage_exhausted=storage_remaining == 0,
        monthly_ingress_limit_bytes=2000,
        monthly_ingress_consumed_bytes=2000 - ingress_remaining,
        remaining_ingress_bytes=ingress_remaining,
        ingress_exhausted=ingress_remaining == 0,
        max_document_versions=20,
        document_versions_consumed=20 - versions_remaining,
        remaining_document_versions=versions_remaining,
        versions_exhausted=versions_remaining == 0,
    )


def _reservation(
    *,
    tenant_id: str = "tenant-p5cb",
    document_id: str = "document-p5cb",
    reservation_id: str = "reservation-existing",
    ingestion_intent_id: str = "ingestion-existing",
    remaining_capacity_fingerprint: str = SHA_A,
    storage_bytes: int = 100,
    ingress_bytes: int = 100,
    document_versions: int = 1,
    reserved_at: datetime = AT - timedelta(minutes=10),
    expires_at: datetime = AT + timedelta(minutes=5),
) -> LegalEvidenceCapacityReservation:
    return LegalEvidenceCapacityReservation(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id=reservation_id,
        ingestion_intent_id=ingestion_intent_id,
        remaining_capacity_fingerprint=remaining_capacity_fingerprint,
        reserved_storage_bytes=storage_bytes,
        reserved_ingress_bytes=ingress_bytes,
        reserved_document_versions=document_versions,
        reserved_at=reserved_at,
        expires_at=expires_at,
    )


def _service() -> tuple[
    LegalEvidenceCapacityReservationService,
    MagicMock,
    MagicMock,
    MagicMock,
    MagicMock,
]:
    fence = MagicMock()
    usage = MagicMock()
    reservations = MagicMock()
    derive = MagicMock()
    service = LegalEvidenceCapacityReservationService(
        fence_registry=fence,
        usage_registry=usage,
        reservation_registry=reservations,
        remaining_capacity_deriver=derive,
    )
    return service, fence, usage, reservations, derive


def test_exact_replay_returns_without_advancing_fence_or_recomputing_capacity() -> None:
    service, fence, usage, reservations, derive = _service()
    command = _command()
    persisted = _reservation(
        reservation_id=command.reservation_id,
        ingestion_intent_id=command.ingestion_intent_id,
        storage_bytes=command.reserved_storage_bytes,
        ingress_bytes=command.reserved_ingress_bytes,
        document_versions=command.reserved_document_versions,
        reserved_at=command.reserved_at,
        expires_at=command.expires_at,
    )

    reservations.get.return_value = persisted
    reservations.create_or_replay.return_value = persisted

    result = service.reserve(
        command=command,
        tenant_profile=_profile(),
        session=Session(),
    )

    assert result == persisted
    reservations.create_or_replay.assert_called_once_with(
        persisted,
        idempotency_key=command.idempotency_key,
        session=reservations.create_or_replay.call_args.kwargs["session"],
    )
    fence.get.assert_not_called()
    fence.advance.assert_not_called()
    usage.get_complete_window_for_p4.assert_not_called()
    derive.assert_not_called()
    reservations.list_active_reservations.assert_not_called()


def test_divergent_existing_reservation_identity_rejects_before_fence() -> None:
    service, fence, usage, reservations, derive = _service()
    command = _command()
    reservations.get.return_value = _reservation(
        reservation_id=command.reservation_id,
        ingestion_intent_id="different-ingestion",
    )

    with pytest.raises(
        LegalEvidenceCapacityAdmissionError,
        match="L10A2Q_P5CB_REPLAY_COMMAND_MISMATCH",
    ):
        service.reserve(
            command=command,
            tenant_profile=_profile(),
            session=Session(),
        )

    fence.advance.assert_not_called()
    usage.get_complete_window_for_p4.assert_not_called()
    derive.assert_not_called()


def test_fresh_admission_advances_tenant_fence_before_capacity_reads() -> None:
    service, fence, usage, reservations, derive = _service()
    command = _command()

    from tools.eos.legal_operations.registry.legal_evidence_capacity_reservation_registry import (
        LegalEvidenceCapacityReservationNotFoundError,
    )
    reservations.get.side_effect = (
        LegalEvidenceCapacityReservationNotFoundError(
            "L10A2Q_P5B_RESERVATION_NOT_FOUND"
        )
    )

    fence.get.side_effect = Exception("STOP_AFTER_FENCE_GET")

    with pytest.raises(Exception, match="STOP_AFTER_FENCE_GET"):
        service.reserve(
            command=command,
            tenant_profile=_profile(),
            session=Session(),
        )

    fence.get.assert_called_once()
    usage.get_complete_window_for_p4.assert_not_called()
    derive.assert_not_called()


def test_outstanding_active_reservations_reduce_all_three_dimensions() -> None:
    service, fence, usage, reservations, derive = _service()
    command = _command(
        storage_bytes=700,
        ingress_bytes=700,
        document_versions=7,
    )

    from tools.eos.legal_operations.registry.legal_evidence_capacity_admission_fence_registry import (
        LegalEvidenceCapacityAdmissionFenceNotFoundError,
    )
    from tools.eos.legal_operations.registry.legal_evidence_capacity_reservation_registry import (
        LegalEvidenceCapacityReservationNotFoundError,
    )

    reservations.get.side_effect = (
        LegalEvidenceCapacityReservationNotFoundError(
            "L10A2Q_P5B_RESERVATION_NOT_FOUND"
        )
    )
    fence.get.side_effect = (
        LegalEvidenceCapacityAdmissionFenceNotFoundError(
            "L10A2Q_P5CA_FENCE_NOT_FOUND"
        )
    )
    fence.advance.return_value = MagicMock(revision=1)

    usage_window = MagicMock(
        tenant_id=command.tenant_id,
        document_id=command.document_id,
        as_of=AT,
    )
    usage.get_complete_window_for_p4.return_value = usage_window

    remaining = _remaining(
        storage_remaining=1000,
        ingress_remaining=1000,
        versions_remaining=10,
    )
    derive.return_value = remaining

    reservations.list_active_reservations.return_value = (
        _reservation(
            reservation_id="reservation-other-1",
            ingestion_intent_id="ingestion-other-1",
            storage_bytes=400,
            ingress_bytes=400,
            document_versions=4,
        ),
    )

    with pytest.raises(
        LegalEvidenceCapacityAdmissionError,
        match="L10A2Q_P5CB_STORAGE_CAPACITY_EXCEEDED",
    ):
        service.reserve(
            command=command,
            tenant_profile=_profile(),
            session=Session(),
        )

    reservations.create_or_replay.assert_not_called()


def test_wall_clock_expired_but_still_active_reservation_remains_outstanding() -> None:
    service, fence, usage, reservations, derive = _service()
    command = _command(
        storage_bytes=700,
    )

    from tools.eos.legal_operations.registry.legal_evidence_capacity_admission_fence_registry import (
        LegalEvidenceCapacityAdmissionFenceNotFoundError,
    )
    from tools.eos.legal_operations.registry.legal_evidence_capacity_reservation_registry import (
        LegalEvidenceCapacityReservationNotFoundError,
    )

    reservations.get.side_effect = (
        LegalEvidenceCapacityReservationNotFoundError(
            "L10A2Q_P5B_RESERVATION_NOT_FOUND"
        )
    )
    fence.get.side_effect = (
        LegalEvidenceCapacityAdmissionFenceNotFoundError(
            "L10A2Q_P5CA_FENCE_NOT_FOUND"
        )
    )
    fence.advance.return_value = MagicMock(revision=1)
    usage.get_complete_window_for_p4.return_value = MagicMock(
        tenant_id=command.tenant_id,
        document_id=command.document_id,
        as_of=AT,
    )
    derive.return_value = _remaining(
        storage_remaining=1000,
    )

    reservations.list_active_reservations.return_value = (
        _reservation(
            reservation_id="reservation-expired-active",
            ingestion_intent_id="ingestion-expired-active",
            storage_bytes=400,
            expires_at=AT - timedelta(seconds=1),
            reserved_at=AT - timedelta(minutes=20),
        ),
    )

    with pytest.raises(
        LegalEvidenceCapacityAdmissionError,
        match="L10A2Q_P5CB_STORAGE_CAPACITY_EXCEEDED",
    ):
        service.reserve(
            command=command,
            tenant_profile=_profile(),
            session=Session(),
        )

    reservations.create_or_replay.assert_not_called()


@pytest.mark.parametrize(
    ("storage", "ingress", "versions", "code"),
    [
        (1001, 1, 1, "L10A2Q_P5CB_STORAGE_CAPACITY_EXCEEDED"),
        (1, 1001, 1, "L10A2Q_P5CB_INGRESS_CAPACITY_EXCEEDED"),
        (1, 1, 11, "L10A2Q_P5CB_DOCUMENT_VERSION_CAPACITY_EXCEEDED"),
    ],
)
def test_each_capacity_dimension_fails_closed(
    storage: int,
    ingress: int,
    versions: int,
    code: str,
) -> None:
    service, fence, usage, reservations, derive = _service()

    from tools.eos.legal_operations.registry.legal_evidence_capacity_admission_fence_registry import (
        LegalEvidenceCapacityAdmissionFenceNotFoundError,
    )
    from tools.eos.legal_operations.registry.legal_evidence_capacity_reservation_registry import (
        LegalEvidenceCapacityReservationNotFoundError,
    )

    command = _command(
        storage_bytes=storage,
        ingress_bytes=ingress,
        document_versions=versions,
    )
    reservations.get.side_effect = (
        LegalEvidenceCapacityReservationNotFoundError(
            "L10A2Q_P5B_RESERVATION_NOT_FOUND"
        )
    )
    fence.get.side_effect = (
        LegalEvidenceCapacityAdmissionFenceNotFoundError(
            "L10A2Q_P5CA_FENCE_NOT_FOUND"
        )
    )
    fence.advance.return_value = MagicMock(revision=1)
    usage.get_complete_window_for_p4.return_value = MagicMock(
        tenant_id=command.tenant_id,
        document_id=command.document_id,
        as_of=AT,
    )
    derive.return_value = _remaining()
    reservations.list_active_reservations.return_value = ()

    with pytest.raises(
        LegalEvidenceCapacityAdmissionError,
        match=code,
    ):
        service.reserve(
            command=command,
            tenant_profile=_profile(),
            session=Session(),
        )

    reservations.create_or_replay.assert_not_called()


def test_single_file_policy_ceiling_rejects_before_p5b_create() -> None:
    service, fence, usage, reservations, derive = _service()

    from tools.eos.legal_operations.registry.legal_evidence_capacity_admission_fence_registry import (
        LegalEvidenceCapacityAdmissionFenceNotFoundError,
    )
    from tools.eos.legal_operations.registry.legal_evidence_capacity_reservation_registry import (
        LegalEvidenceCapacityReservationNotFoundError,
    )

    profile = _profile()
    policy = get_legal_evidence_capacity_policy(profile.profile)
    command = _command(
        storage_bytes=policy.single_file_max_bytes + 1,
        ingress_bytes=1,
    )

    reservations.get.side_effect = (
        LegalEvidenceCapacityReservationNotFoundError(
            "L10A2Q_P5B_RESERVATION_NOT_FOUND"
        )
    )
    with pytest.raises(
        LegalEvidenceCapacityAdmissionError,
        match="L10A2Q_P5CB_SINGLE_FILE_LIMIT_EXCEEDED",
    ):
        service.reserve(
            command=command,
            tenant_profile=profile,
            session=Session(),
        )

    # Single-file capacity is canonical P1 policy truth and must reject before
    # serializing the tenant or reading aggregate usage/reservation capacity.
    fence.get.assert_not_called()
    fence.advance.assert_not_called()
    usage.get_complete_window_for_p4.assert_not_called()
    derive.assert_not_called()
    reservations.list_active_reservations.assert_not_called()
    reservations.create_or_replay.assert_not_called()


def test_successful_fresh_admission_persists_exact_p5a_reservation() -> None:
    service, fence, usage, reservations, derive = _service()

    from tools.eos.legal_operations.registry.legal_evidence_capacity_admission_fence_registry import (
        LegalEvidenceCapacityAdmissionFenceNotFoundError,
    )
    from tools.eos.legal_operations.registry.legal_evidence_capacity_reservation_registry import (
        LegalEvidenceCapacityReservationNotFoundError,
    )

    command = _command()
    profile = _profile()

    reservations.get.side_effect = (
        LegalEvidenceCapacityReservationNotFoundError(
            "L10A2Q_P5B_RESERVATION_NOT_FOUND"
        )
    )
    fence.get.side_effect = (
        LegalEvidenceCapacityAdmissionFenceNotFoundError(
            "L10A2Q_P5CA_FENCE_NOT_FOUND"
        )
    )
    fence.advance.return_value = MagicMock(revision=1)

    usage.get_complete_window_for_p4.return_value = MagicMock(
        tenant_id=command.tenant_id,
        document_id=command.document_id,
        as_of=AT,
    )
    remaining = _remaining()
    derive.return_value = remaining
    reservations.list_active_reservations.return_value = ()
    reservations.create_or_replay.side_effect = (
        lambda reservation, **_: reservation
    )

    result = service.reserve(
        command=command,
        tenant_profile=profile,
        session=Session(),
    )

    assert result.tenant_id == command.tenant_id
    assert result.document_id == command.document_id
    assert result.reservation_id == command.reservation_id
    assert result.ingestion_intent_id == command.ingestion_intent_id
    assert (
        result.remaining_capacity_fingerprint
        == remaining.fingerprint
    )
    assert result.reserved_storage_bytes == command.reserved_storage_bytes
    assert result.reserved_ingress_bytes == command.reserved_ingress_bytes
    assert result.reserved_document_versions == command.reserved_document_versions
    assert result.reserved_at == command.reserved_at
    assert result.expires_at == command.expires_at

    reservations.create_or_replay.assert_called_once()


def test_cross_tenant_profile_rejects_before_fence() -> None:
    service, fence, usage, reservations, derive = _service()

    with pytest.raises(
        LegalEvidenceCapacityAdmissionError,
        match="L10A2Q_P5CB_TENANT_PROFILE_MISMATCH",
    ):
        service.reserve(
            command=_command(),
            tenant_profile=_profile(
                tenant_id="tenant-neighbor",
            ),
            session=Session(),
        )

    fence.get.assert_not_called()
    fence.advance.assert_not_called()
    usage.get_complete_window_for_p4.assert_not_called()
    reservations.create_or_replay.assert_not_called()


def test_surface_has_no_provider_iam_usage_commit_or_financial_authority() -> None:
    forbidden = {
        "upload",
        "provider",
        "iam",
        "retain",
        "delete",
        "commit_usage",
        "invoice",
        "bill",
        "payment",
        "settlement",
        "execute",
    }
    public = {
        name.lower()
        for name in dir(
            LegalEvidenceCapacityReservationService
        )
        if not name.startswith("_")
    }
    assert forbidden.isdisjoint(public)


# ARTIFACT: test_legal_evidence_capacity_reservation_service.py
# VERSION: v1.0.0-L10A2Q-P5C-B-ATOMIC-CAPACITY-RESERVATION-SERVICE-CERT
# AUTHORITY BOUNDARY: atomic capacity-admission/reservation orchestration only
# TENANT POSTURE: exact tenant/profile/usage/reservation agreement required
# REPLAY POSTURE: exact durable replay consumes no additional capacity
# EXPIRY POSTURE: ACTIVE remains outstanding until durable P5D transition
# PROVIDER POSTURE: no binary-provider operation exists in this service
# RECONCILIATION POSTURE: P5D remains semantic lifecycle/reconciliation owner
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
