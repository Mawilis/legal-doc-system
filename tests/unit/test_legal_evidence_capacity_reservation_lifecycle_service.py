"""Direct certificate for semantic Legal Evidence reservation lifecycle.

TITLE: Legal Evidence Capacity Reservation Lifecycle Service Certificate
VERSION: v1.0.0-L10A2Q-P5D-SEMANTIC-RESERVATION-LIFECYCLE-CERT
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Freeze semantic consume, release, expiry and replay/reconciliation behavior
    around the already-certified P5A/P5B reservation lifecycle and P5C tenant
    admission fence.

EPITOME:
    ACTIVE RESERVATION
    + TENANT ADMISSION FENCE
    + CANONICAL CONTENT WHEN CONSUMING
    -> DURABLE TERMINAL RESERVATION

    CONSUMED
    -> EXACT P3 USAGE EVIDENCE REQUIRED

    RELEASED / EXPIRED
    -> NO USAGE EVIDENCE

    TERMINAL REPLAY
    -> EXACT RECONCILIATION
    != NEW FENCE ADVANCE
    != NEW USAGE
    != PROVIDER EXECUTION

TRANSACTION:
    Caller owns one already-active Mongo transaction. This service does not
    start, commit, abort or retry transactions.

CONCURRENCY:
    Every fresh terminal transition advances the same tenant-only P5C-A fence
    used by fresh admission before changing reservation/usage state.

CONSUMPTION:
    Canonical LegalEvidenceContent must agree with the reserved tenant,
    document and exact dimensions. Storage bytes and ingress bytes equal
    content_length and document versions equal one.

REPLAY:
    Exact terminal state and exact terminal timestamp reconcile without a new
    fence mutation. CONSUMED replay additionally requires exact deterministic
    P3 usage replay for the supplied canonical content.

AUTHORITY BOUNDARY:
    Reservation lifecycle and usage reconciliation only. No provider, IAM,
    retention, legal-hold, billing, payment, settlement or finance authority.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
    LegalEvidenceCapacityReservationStatus,
)
from tools.eos.legal_operations.domain.legal_evidence_content import (
    LegalEvidenceContent,
    register_legal_evidence_content,
)
from tools.eos.legal_operations.domain.legal_evidence_usage_observation import (
    observe_legal_evidence_usage,
)
from tools.eos.legal_operations.service.legal_evidence_capacity_reservation_lifecycle_service import (
    LegalEvidenceCapacityReservationLifecycleError,
    LegalEvidenceCapacityReservationLifecycleService,
    LegalEvidenceCapacityReservationLifecycleTransactionRequiredError,
)


AT = datetime(
    2026,
    9,
    30,
    7,
    0,
    0,
    123456,
    tzinfo=timezone.utc,
)
REGISTERED_AT = AT + timedelta(minutes=2)
CONSUMED_AT = AT + timedelta(minutes=3)
RELEASED_AT = AT + timedelta(minutes=3)
EXPIRES_AT = AT + timedelta(minutes=10)
EXPIRED_AT = EXPIRES_AT
SHA_A = "a" * 128


class Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


def _active_reservation(
    *,
    tenant_id: str = "tenant-p5d",
    document_id: str = "document-p5d",
    reservation_id: str = "reservation-p5d",
    content_length: int = 1,
) -> LegalEvidenceCapacityReservation:
    return LegalEvidenceCapacityReservation(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id=reservation_id,
        ingestion_intent_id="ingestion-p5d",
        remaining_capacity_fingerprint=SHA_A,
        reserved_storage_bytes=content_length,
        reserved_ingress_bytes=content_length,
        reserved_document_versions=1,
        reserved_at=AT,
        expires_at=EXPIRES_AT,
    )


def _content(
    *,
    tenant_id: str = "tenant-p5d",
    document_id: str = "document-p5d",
    registered_at: datetime = REGISTERED_AT,
    content: bytes = b"x",
) -> LegalEvidenceContent:
    return register_legal_evidence_content(
        tenant_id=tenant_id,
        case_matter_id="matter-p5d",
        document_id=document_id,
        media_type="application/pdf",
        original_filename="evidence.pdf",
        content=content,
        source_evidence_reference="source-p5d",
        source_evidence_fingerprint=SHA_A,
        registered_at=registered_at,
    )


def _service() -> tuple[
    LegalEvidenceCapacityReservationLifecycleService,
    MagicMock,
    MagicMock,
    MagicMock,
]:
    fence = MagicMock()
    reservations = MagicMock()
    usage = MagicMock()

    service = LegalEvidenceCapacityReservationLifecycleService(
        fence_registry=fence,
        reservation_registry=reservations,
        usage_registry=usage,
    )

    return service, fence, reservations, usage


def test_requires_caller_owned_active_transaction_before_database_read() -> None:
    service, fence, reservations, usage = _service()

    with pytest.raises(
        LegalEvidenceCapacityReservationLifecycleTransactionRequiredError,
        match="L10A2Q_P5D_TRANSACTION_REQUIRED",
    ):
        service.release(
            tenant_id="tenant-p5d",
            reservation_id="reservation-p5d",
            released_at=RELEASED_AT,
            session=Session(False),
        )

    reservations.get.assert_not_called()
    fence.get.assert_not_called()
    usage.create_or_replay.assert_not_called()


def test_consume_validates_canonical_content_before_fence() -> None:
    service, fence, reservations, usage = _service()
    reservation = _active_reservation()

    reservations.get.return_value = reservation

    with pytest.raises(
        LegalEvidenceCapacityReservationLifecycleError,
        match="L10A2Q_P5D_CONTENT_TENANT_MISMATCH",
    ):
        service.consume(
            tenant_id=reservation.tenant_id,
            reservation_id=reservation.reservation_id,
            content=_content(
                tenant_id="tenant-neighbor",
            ),
            consumed_at=CONSUMED_AT,
            session=Session(),
        )

    fence.get.assert_not_called()
    fence.advance.assert_not_called()
    usage.create_or_replay.assert_not_called()
    reservations.consume.assert_not_called()


@pytest.mark.parametrize(
    ("content_bytes", "reserved_bytes", "reserved_versions", "code"),
    [
        (
            b"xx",
            1,
            1,
            "L10A2Q_P5D_CONTENT_DIMENSION_MISMATCH",
        ),
        (
            b"x",
            1,
            2,
            "L10A2Q_P5D_CONTENT_DIMENSION_MISMATCH",
        ),
    ],
)
def test_consume_requires_exact_reserved_content_dimensions(
    content_bytes: bytes,
    reserved_bytes: int,
    reserved_versions: int,
    code: str,
) -> None:
    service, fence, reservations, usage = _service()

    reservation = LegalEvidenceCapacityReservation(
        tenant_id="tenant-p5d",
        document_id="document-p5d",
        reservation_id="reservation-p5d",
        ingestion_intent_id="ingestion-p5d",
        remaining_capacity_fingerprint=SHA_A,
        reserved_storage_bytes=reserved_bytes,
        reserved_ingress_bytes=reserved_bytes,
        reserved_document_versions=reserved_versions,
        reserved_at=AT,
        expires_at=EXPIRES_AT,
    )
    reservations.get.return_value = reservation

    with pytest.raises(
        LegalEvidenceCapacityReservationLifecycleError,
        match=code,
    ):
        service.consume(
            tenant_id=reservation.tenant_id,
            reservation_id=reservation.reservation_id,
            content=_content(
                content=content_bytes,
            ),
            consumed_at=CONSUMED_AT,
            session=Session(),
        )

    fence.advance.assert_not_called()
    usage.create_or_replay.assert_not_called()
    reservations.consume.assert_not_called()


@pytest.mark.parametrize(
    "registered_at",
    [
        AT - timedelta(microseconds=1),
        CONSUMED_AT + timedelta(microseconds=1),
    ],
)
def test_consume_requires_content_commit_inside_reservation_consume_window(
    registered_at: datetime,
) -> None:
    service, fence, reservations, usage = _service()
    reservation = _active_reservation()
    reservations.get.return_value = reservation

    with pytest.raises(
        LegalEvidenceCapacityReservationLifecycleError,
        match="L10A2Q_P5D_CONTENT_TIME_MISMATCH",
    ):
        service.consume(
            tenant_id=reservation.tenant_id,
            reservation_id=reservation.reservation_id,
            content=_content(
                registered_at=registered_at,
            ),
            consumed_at=CONSUMED_AT,
            session=Session(),
        )

    fence.advance.assert_not_called()
    usage.create_or_replay.assert_not_called()
    reservations.consume.assert_not_called()


def test_fresh_consume_advances_fence_then_persists_usage_then_consumes() -> None:
    service, fence, reservations, usage = _service()
    reservation = _active_reservation()
    content = _content()
    observation = observe_legal_evidence_usage(
        content=content,
    )
    successor = reservation.consume(
        CONSUMED_AT,
    )
    events: list[str] = []

    reservations.get.side_effect = lambda **_: (
        events.append("reservation_get")
        or reservation
    )
    fence.get.side_effect = Exception(
        "STOP_AFTER_FENCE_GET"
    )

    with pytest.raises(
        Exception,
        match="STOP_AFTER_FENCE_GET",
    ):
        service.consume(
            tenant_id=reservation.tenant_id,
            reservation_id=reservation.reservation_id,
            content=content,
            consumed_at=CONSUMED_AT,
            session=Session(),
        )

    assert events == [
        "reservation_get",
    ]

    fence.get.reset_mock()
    fence.get.side_effect = None
    fence.get.return_value = MagicMock(
        revision=4,
    )

    fence.advance.side_effect = lambda **_: (
        events.append("fence_advance")
        or MagicMock(revision=5)
    )
    usage.create_or_replay.side_effect = lambda value, **_: (
        events.append("usage_create")
        or value
    )
    reservations.consume.side_effect = lambda value, when, **_: (
        events.append("reservation_consume")
        or successor
    )

    result = service.consume(
        tenant_id=reservation.tenant_id,
        reservation_id=reservation.reservation_id,
        content=content,
        consumed_at=CONSUMED_AT,
        session=Session(),
    )

    assert result == successor

    assert events[-3:] == [
        "fence_advance",
        "usage_create",
        "reservation_consume",
    ]

    usage.create_or_replay.assert_called_once()
    supplied_observation = (
        usage.create_or_replay.call_args.args[0]
    )
    assert supplied_observation == observation

    assert (
        usage.create_or_replay.call_args.kwargs[
            "idempotency_key"
        ]
        == "legal-evidence-capacity-consume:reservation-p5d"
    )


def test_exact_consumed_replay_requires_usage_replay_and_no_fence() -> None:
    service, fence, reservations, usage = _service()
    active = _active_reservation()
    terminal = active.consume(
        CONSUMED_AT,
    )
    content = _content()
    observation = observe_legal_evidence_usage(
        content=content,
    )

    reservations.get.return_value = terminal
    usage.create_or_replay.return_value = observation

    result = service.consume(
        tenant_id=terminal.tenant_id,
        reservation_id=terminal.reservation_id,
        content=content,
        consumed_at=CONSUMED_AT,
        session=Session(),
    )

    assert result == terminal

    usage.create_or_replay.assert_called_once_with(
        observation,
        idempotency_key=(
            "legal-evidence-capacity-consume:"
            "reservation-p5d"
        ),
        session=usage.create_or_replay.call_args.kwargs[
            "session"
        ],
    )

    fence.get.assert_not_called()
    fence.advance.assert_not_called()
    reservations.consume.assert_not_called()


def test_divergent_terminal_consume_replay_rejects_without_fence() -> None:
    service, fence, reservations, usage = _service()
    terminal = _active_reservation().consume(
        CONSUMED_AT,
    )
    reservations.get.return_value = terminal

    with pytest.raises(
        LegalEvidenceCapacityReservationLifecycleError,
        match="L10A2Q_P5D_TERMINAL_REPLAY_MISMATCH",
    ):
        service.consume(
            tenant_id=terminal.tenant_id,
            reservation_id=terminal.reservation_id,
            content=_content(),
            consumed_at=CONSUMED_AT + timedelta(seconds=1),
            session=Session(),
        )

    fence.advance.assert_not_called()
    usage.create_or_replay.assert_not_called()
    reservations.consume.assert_not_called()


@pytest.mark.parametrize(
    ("operation", "observed_at", "terminal_status"),
    [
        (
            "release",
            RELEASED_AT,
            LegalEvidenceCapacityReservationStatus.RELEASED,
        ),
        (
            "expire",
            EXPIRED_AT,
            LegalEvidenceCapacityReservationStatus.EXPIRED,
        ),
    ],
)
def test_release_and_expire_advance_same_fence_without_usage(
    operation: str,
    observed_at: datetime,
    terminal_status: LegalEvidenceCapacityReservationStatus,
) -> None:
    service, fence, reservations, usage = _service()
    active = _active_reservation()
    reservations.get.return_value = active
    fence.get.return_value = MagicMock(
        revision=7,
    )
    fence.advance.return_value = MagicMock(
        revision=8,
    )

    successor = (
        active.release(observed_at)
        if operation == "release"
        else active.expire(observed_at)
    )

    getattr(
        reservations,
        operation,
    ).return_value = successor

    result = getattr(
        service,
        operation,
    )(
        tenant_id=active.tenant_id,
        reservation_id=active.reservation_id,
        **{
            (
                "released_at"
                if operation == "release"
                else "expired_at"
            ): observed_at,
        },
        session=Session(),
    )

    assert result.status is terminal_status
    fence.advance.assert_called_once()
    usage.create_or_replay.assert_not_called()


@pytest.mark.parametrize(
    ("operation", "observed_at"),
    [
        (
            "release",
            RELEASED_AT,
        ),
        (
            "expire",
            EXPIRED_AT,
        ),
    ],
)
def test_exact_release_and_expire_replay_do_not_advance_fence(
    operation: str,
    observed_at: datetime,
) -> None:
    service, fence, reservations, usage = _service()
    active = _active_reservation()

    terminal = (
        active.release(observed_at)
        if operation == "release"
        else active.expire(observed_at)
    )
    reservations.get.return_value = terminal

    result = getattr(
        service,
        operation,
    )(
        tenant_id=terminal.tenant_id,
        reservation_id=terminal.reservation_id,
        **{
            (
                "released_at"
                if operation == "release"
                else "expired_at"
            ): observed_at,
        },
        session=Session(),
    )

    assert result == terminal
    fence.get.assert_not_called()
    fence.advance.assert_not_called()
    usage.create_or_replay.assert_not_called()
    getattr(
        reservations,
        operation,
    ).assert_not_called()


def test_terminal_operation_mismatch_rejects_without_mutation() -> None:
    service, fence, reservations, usage = _service()
    released = _active_reservation().release(
        RELEASED_AT,
    )
    reservations.get.return_value = released

    with pytest.raises(
        LegalEvidenceCapacityReservationLifecycleError,
        match="L10A2Q_P5D_TERMINAL_REPLAY_MISMATCH",
    ):
        service.expire(
            tenant_id=released.tenant_id,
            reservation_id=released.reservation_id,
            expired_at=EXPIRED_AT,
            session=Session(),
        )

    fence.advance.assert_not_called()
    usage.create_or_replay.assert_not_called()
    reservations.expire.assert_not_called()


def test_surface_has_no_provider_iam_retention_or_financial_authority() -> None:
    forbidden = {
        "upload",
        "provider",
        "iam",
        "retention",
        "legal_hold",
        "invoice",
        "bill",
        "payment",
        "settlement",
        "execute_payment",
    }

    public = {
        name.lower()
        for name in dir(
            LegalEvidenceCapacityReservationLifecycleService
        )
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(public)


# ARTIFACT: test_legal_evidence_capacity_reservation_lifecycle_service.py
# VERSION: v1.0.0-L10A2Q-P5D-SEMANTIC-RESERVATION-LIFECYCLE-CERT
# AUTHORITY BOUNDARY: semantic reservation lifecycle/reconciliation only
# TENANT POSTURE: exact reservation/content tenant and document agreement
# CONCURRENCY POSTURE: fresh terminal mutation advances P5C-A tenant fence
# CONSUMPTION POSTURE: CONSUMED requires exact durable P3 usage evidence
# RELEASE POSTURE: RELEASED never fabricates usage
# EXPIRY POSTURE: EXPIRED never fabricates usage
# REPLAY POSTURE: exact terminal replay advances no fence
# PROVIDER POSTURE: no binary-provider operation exists
# TRANSACTION POSTURE: caller owns one already-active transaction
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
