"""Direct certificate for Legal Evidence capacity reservation domain.

TITLE: Legal Evidence Capacity Reservation Direct Certificate
VERSION: v1.0.0-L10A2Q-P5A-LEGAL-EVIDENCE-CAPACITY-RESERVATION-CERT
AUTHORITY: WILSY OS Core Governance

PURPOSE:
    Prove one immutable, tenant/document-scoped reservation lifecycle value
    that can reserve the exact P4 capacity-accounting dimensions without
    granting storage admission, IAM, provider execution, usage consumption,
    billing, payment or settlement authority.

EPITOME:
    REMAINING CAPACITY
    -> CAPACITY RESERVED
    != STORAGE ADMITTED
    != PROVIDER OBJECT WRITTEN
    != USAGE CONSUMED
    != IAM AUTHORIZED
    != BILLING / PAYMENT / SETTLEMENT

LIFECYCLE:
    ACTIVE may transition exactly once to CONSUMED, RELEASED or EXPIRED.
    Terminal states are durable evidence and are never revived.

CERTIFICATION / UPDATE DATE: 2026-09-30
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.legal_evidence_capacity_reservation import (
    LegalEvidenceCapacityReservation,
    LegalEvidenceCapacityReservationError,
    LegalEvidenceCapacityReservationStatus,
)


AT = datetime(2026, 9, 30, 19, 0, tzinfo=timezone.utc)
EXPIRY = AT + timedelta(minutes=15)
SHA = "a" * 128


def _reservation(
    *,
    tenant_id: str = "tenant-p5",
    document_id: str = "document-p5",
    reservation_id: str = "reservation-p5",
    ingestion_intent_id: str = "ingestion-p5",
    reserved_storage_bytes: int = 1024,
    reserved_ingress_bytes: int = 1024,
    reserved_document_versions: int = 1,
    status: LegalEvidenceCapacityReservationStatus = (
        LegalEvidenceCapacityReservationStatus.ACTIVE
    ),
    consumed_at: datetime | None = None,
    released_at: datetime | None = None,
    expired_at: datetime | None = None,
) -> LegalEvidenceCapacityReservation:
    return LegalEvidenceCapacityReservation(
        tenant_id=tenant_id,
        document_id=document_id,
        reservation_id=reservation_id,
        ingestion_intent_id=ingestion_intent_id,
        remaining_capacity_fingerprint=SHA,
        reserved_storage_bytes=reserved_storage_bytes,
        reserved_ingress_bytes=reserved_ingress_bytes,
        reserved_document_versions=reserved_document_versions,
        reserved_at=AT,
        expires_at=EXPIRY,
        status=status,
        consumed_at=consumed_at,
        released_at=released_at,
        expired_at=expired_at,
    )


def test_active_reservation_preserves_exact_scope_and_capacity_dimensions() -> None:
    value = _reservation()

    assert value.tenant_id == "tenant-p5"
    assert value.document_id == "document-p5"
    assert value.reservation_id == "reservation-p5"
    assert value.ingestion_intent_id == "ingestion-p5"
    assert value.remaining_capacity_fingerprint == SHA

    assert value.reserved_storage_bytes == 1024
    assert value.reserved_ingress_bytes == 1024
    assert value.reserved_document_versions == 1

    assert value.reserved_at == AT
    assert value.expires_at == EXPIRY
    assert value.status is LegalEvidenceCapacityReservationStatus.ACTIVE

    assert value.consumed_at is None
    assert value.released_at is None
    assert value.expired_at is None

    assert len(value.fingerprint) == 128
    int(value.fingerprint, 16)


def test_reservation_is_immutable_and_deterministic() -> None:
    first = _reservation()
    second = _reservation()

    assert first == second
    assert first.fingerprint == second.fingerprint

    with pytest.raises(FrozenInstanceError):
        first.reserved_storage_bytes = 0  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("reserved_storage_bytes", 0),
        ("reserved_ingress_bytes", 0),
        ("reserved_document_versions", 0),
        ("reserved_storage_bytes", -1),
        ("reserved_ingress_bytes", -1),
        ("reserved_document_versions", -1),
        ("reserved_storage_bytes", True),
    ],
)
def test_reserved_dimensions_require_positive_integer(
    field: str,
    value: object,
) -> None:
    kwargs: dict[str, object] = {
        "reserved_storage_bytes": 1024,
        "reserved_ingress_bytes": 1024,
        "reserved_document_versions": 1,
    }
    kwargs[field] = value

    with pytest.raises(
        LegalEvidenceCapacityReservationError,
        match="L10A2Q_P5A_",
    ):
        _reservation(**kwargs)  # type: ignore[arg-type]


def test_expiry_must_be_strictly_after_reservation_time() -> None:
    with pytest.raises(
        LegalEvidenceCapacityReservationError,
        match="L10A2Q_P5A_EXPIRY_INVALID",
    ):
        LegalEvidenceCapacityReservation(
            tenant_id="tenant-p5",
            document_id="document-p5",
            reservation_id="reservation-p5",
            ingestion_intent_id="ingestion-p5",
            remaining_capacity_fingerprint=SHA,
            reserved_storage_bytes=1,
            reserved_ingress_bytes=1,
            reserved_document_versions=1,
            reserved_at=AT,
            expires_at=AT,
        )


def test_consume_before_expiry_returns_terminal_immutable_successor() -> None:
    active = _reservation()
    consumed_at = AT + timedelta(minutes=2)

    consumed = active.consume(consumed_at)

    assert consumed.status is LegalEvidenceCapacityReservationStatus.CONSUMED
    assert consumed.consumed_at == consumed_at
    assert consumed.released_at is None
    assert consumed.expired_at is None

    assert consumed.tenant_id == active.tenant_id
    assert consumed.reservation_id == active.reservation_id
    assert consumed.ingestion_intent_id == active.ingestion_intent_id
    assert consumed.reserved_storage_bytes == active.reserved_storage_bytes

    assert consumed != active
    assert consumed.fingerprint != active.fingerprint


def test_release_before_expiry_returns_terminal_immutable_successor() -> None:
    active = _reservation()
    released_at = AT + timedelta(minutes=3)

    released = active.release(released_at)

    assert released.status is LegalEvidenceCapacityReservationStatus.RELEASED
    assert released.released_at == released_at
    assert released.consumed_at is None
    assert released.expired_at is None


def test_expire_at_boundary_returns_terminal_immutable_successor() -> None:
    active = _reservation()

    expired = active.expire(EXPIRY)

    assert expired.status is LegalEvidenceCapacityReservationStatus.EXPIRED
    assert expired.expired_at == EXPIRY
    assert expired.consumed_at is None
    assert expired.released_at is None


def test_consume_or_release_at_or_after_expiry_rejects() -> None:
    active = _reservation()

    for operation in (
        lambda: active.consume(EXPIRY),
        lambda: active.release(EXPIRY),
    ):
        with pytest.raises(
            LegalEvidenceCapacityReservationError,
            match="L10A2Q_P5A_RESERVATION_EXPIRED",
        ):
            operation()


def test_expire_before_expiry_boundary_rejects() -> None:
    with pytest.raises(
        LegalEvidenceCapacityReservationError,
        match="L10A2Q_P5A_EXPIRY_BOUNDARY_NOT_REACHED",
    ):
        _reservation().expire(EXPIRY - timedelta(microseconds=1))


@pytest.mark.parametrize(
    "transition",
    [
        lambda value: value.consume(AT + timedelta(minutes=4)),
        lambda value: value.release(AT + timedelta(minutes=4)),
        lambda value: value.expire(EXPIRY),
    ],
)
def test_terminal_reservations_cannot_transition_again(transition) -> None:
    active = _reservation()

    terminal_values = (
        active.consume(AT + timedelta(minutes=1)),
        active.release(AT + timedelta(minutes=1)),
        active.expire(EXPIRY),
    )

    for terminal in terminal_values:
        with pytest.raises(
            LegalEvidenceCapacityReservationError,
            match="L10A2Q_P5A_TERMINAL_RESERVATION",
        ):
            transition(terminal)


def test_round_trip_preserves_exact_fingerprint() -> None:
    original = _reservation().consume(
        AT + timedelta(minutes=1)
    )

    hydrated = LegalEvidenceCapacityReservation.from_dict(
        original.to_dict()
    )

    assert hydrated == original
    assert hydrated.fingerprint == original.fingerprint


def test_corrupt_fingerprint_rejects() -> None:
    payload = _reservation().to_dict()
    payload["fingerprint"] = "0" * 128

    with pytest.raises(
        LegalEvidenceCapacityReservationError,
        match="L10A2Q_P5A_FINGERPRINT_MISMATCH",
    ):
        LegalEvidenceCapacityReservation.from_dict(payload)


def test_cross_tenant_or_pseudo_tenant_identity_never_normalizes() -> None:
    for tenant in ("default", "global", "root", "*", " global "):
        with pytest.raises(LegalEvidenceCapacityReservationError):
            _reservation(tenant_id=tenant)


def test_surface_contains_no_admission_iam_provider_usage_or_financial_authority() -> None:
    keys = set(_reservation().to_dict())

    forbidden = {
        "admitted",
        "authorized",
        "permission",
        "principal_id",
        "provider",
        "provider_name",
        "storage_reference",
        "object_version",
        "usage_observation_id",
        "billing",
        "price",
        "amount",
        "currency",
        "invoice",
        "payment",
        "settlement",
        "execution",
    }

    assert forbidden.isdisjoint(keys)


# ARTIFACT: test_legal_evidence_capacity_reservation.py
# VERSION: v1.0.0-L10A2Q-P5A-LEGAL-EVIDENCE-CAPACITY-RESERVATION-CERT
# AUTHORITY BOUNDARY: immutable reservation lifecycle evidence only
# TENANT POSTURE: exact tenant/document/ingestion-intent binding
# EXPIRY POSTURE: terminal evidence retained; no TTL deletion semantics
# CONCURRENCY POSTURE: P5B/P5C own persistence and atomic CAS
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
