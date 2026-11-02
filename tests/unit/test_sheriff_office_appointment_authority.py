"""Sheriff appointment evidence domain certificate.

TITLE: WILSY OS Sheriff Office Appointment Evidence Unit Certificate
VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-UNIT-CERT
AUTHORITY: Pure immutable evidence semantics only.
EPITOME: Prove strict source, jurisdiction, FFC, temporal, fingerprint and lineage contracts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sheriff_office_appointment_authority.py
TENANT BOUNDARY: Synthetic exact-tenant identifiers only.
AUTHORITY BOUNDARY: Does not issue appointment, verify external source authenticity, or grant IAM.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta

import pytest

from tools.eos.legal_operations.domain.sheriff_office_appointment_authority import (
    SCHEMA,
    VERSION,
    SheriffOfficeAppointmentAuthority,
    SheriffOfficeAppointmentAuthorityError,
)

NOW = datetime(2026, 11, 2, 8, 0, tzinfo=UTC)
TENANT = "tenant-sheriff-evidence"
PRINCIPAL = "principal-sheriff-1"
OFFICE = "sheriff-office-1"
DISTRICT = "district-1"


def _authority(**overrides: object) -> SheriffOfficeAppointmentAuthority:
    values: dict[str, object] = {
        "tenant_id": TENANT,
        "appointment_id": "appointment-1",
        "revision": 1,
        "principal_id": PRINCIPAL,
        "sheriff_office_id": OFFICE,
        "district_id": DISTRICT,
        "appointment_kind": "PERMANENT",
        "appointment_instrument_reference": "gazette:notice-123",
        "appointment_instrument_fingerprint": "a" * 128,
        "office_scope_instrument_reference": "gazette:notice-123:schedule",
        "office_scope_instrument_fingerprint": "b" * 128,
        "fidelity_fund_certificate_reference": "sabfs:ffc-2026-123",
        "fidelity_fund_certificate_fingerprint": "c" * 128,
        "certificate_jurisdiction_reference": "ZA-GP-JHB",
        "professional_indemnity_insurance_reference": "insurer:policy-2026-1",
        "professional_indemnity_insurance_fingerprint": "9" * 128,
        "professional_indemnity_insurance_valid_from": NOW - timedelta(days=1),
        "professional_indemnity_insurance_valid_until": NOW + timedelta(days=365),
        "appointment_effective_from": NOW - timedelta(days=30),
        "appointment_effective_until": None,
        "certificate_valid_from": NOW - timedelta(days=10),
        "certificate_valid_until": NOW + timedelta(days=355),
        "verified_by_principal_id": "tenant-admin-1",
        "verified_at": NOW - timedelta(days=1),
        "supersedes_fingerprint": None,
    }
    values.update(overrides)
    return SheriffOfficeAppointmentAuthority(**values)  # type: ignore[arg-type]


def test_exact_immutable_appointment_evidence_round_trips() -> None:
    value = _authority()
    restored = SheriffOfficeAppointmentAuthority.from_dict(value.to_dict())

    assert restored == value
    assert restored.schema == SCHEMA
    assert restored.appointment_version == VERSION
    assert len(restored.fingerprint) == 128
    assert restored.fingerprint == value.fingerprint
    with pytest.raises(FrozenInstanceError):
        value.principal_id = "other-principal"  # type: ignore[misc]


def test_currentness_requires_appointment_certificate_and_prior_verification() -> None:
    value = _authority(
        certificate_valid_from=NOW - timedelta(days=1),
        certificate_valid_until=NOW + timedelta(days=1),
        verified_at=NOW,
    )

    assert value.is_current(NOW)
    assert not value.is_current(NOW - timedelta(seconds=1))
    assert not value.is_current(NOW + timedelta(days=1))
    assert not value.is_current(NOW + timedelta(days=1, seconds=1))


def test_expired_appointment_is_not_current_even_with_current_certificate() -> None:
    value = _authority(
        appointment_effective_until=NOW - timedelta(seconds=1),
        certificate_valid_from=NOW - timedelta(days=1),
        certificate_valid_until=NOW + timedelta(days=1),
    )

    assert not value.is_current(NOW)


def test_acting_appointment_requires_finite_effective_end() -> None:
    with pytest.raises(
        SheriffOfficeAppointmentAuthorityError,
        match="ACTING_APPOINTMENT_END_REQUIRED",
    ):
        _authority(appointment_kind="ACTING")


def test_unsupported_appointment_kind_fails_closed() -> None:
    with pytest.raises(
        SheriffOfficeAppointmentAuthorityError,
        match="APPOINTMENT_KIND_UNSUPPORTED",
    ):
        _authority(appointment_kind="AD_HOC")


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("tenant_id", "root", "TENANT_ID_INVALID"),
        ("principal_id", "", "PRINCIPAL_ID_INVALID"),
        ("sheriff_office_id", " office-1", "SHERIFF_OFFICE_ID_INVALID"),
        ("appointment_instrument_fingerprint", "not-a-hash", "APPOINTMENT_INSTRUMENT_FINGERPRINT_INVALID"),
        ("office_scope_instrument_fingerprint", "A" * 128, "OFFICE_SCOPE_INSTRUMENT_FINGERPRINT_INVALID"),
        ("fidelity_fund_certificate_fingerprint", "d" * 127, "FIDELITY_FUND_CERTIFICATE_FINGERPRINT_INVALID"),
    ],
)
def test_malformed_identity_and_source_evidence_reject(
    field: str,
    value: object,
    code: str,
) -> None:
    with pytest.raises(SheriffOfficeAppointmentAuthorityError, match=code):
        _authority(**{field: value})


def test_invalid_temporal_windows_reject() -> None:
    with pytest.raises(
        SheriffOfficeAppointmentAuthorityError,
        match="EFFECTIVE_WINDOW_INVALID",
    ):
        _authority(
            appointment_effective_until=NOW - timedelta(days=31),
        )

    with pytest.raises(
        SheriffOfficeAppointmentAuthorityError,
        match="CERTIFICATE_WINDOW_INVALID",
    ):
        _authority(
            certificate_valid_from=NOW,
            certificate_valid_until=NOW,
        )


def test_timezone_naive_timestamp_rejects() -> None:
    with pytest.raises(
        SheriffOfficeAppointmentAuthorityError,
        match="APPOINTMENT_EFFECTIVE_FROM_INVALID",
    ):
        _authority(appointment_effective_from=datetime(2026, 10, 1))


def test_revision_lineage_is_mandatory_and_exact() -> None:
    with pytest.raises(
        SheriffOfficeAppointmentAuthorityError,
        match="FIRST_REVISION_SUPERSEDES_FORBIDDEN",
    ):
        _authority(supersedes_fingerprint="d" * 128)

    with pytest.raises(
        SheriffOfficeAppointmentAuthorityError,
        match="SUCCESSOR_SUPERSEDES_REQUIRED",
    ):
        _authority(revision=2)

    successor = _authority(
        revision=2,
        supersedes_fingerprint="d" * 128,
    )
    assert successor.revision == 2


def test_persisted_fingerprint_tampering_rejects() -> None:
    payload = _authority().to_dict()
    payload["principal_id"] = "substituted-principal"

    with pytest.raises(
        SheriffOfficeAppointmentAuthorityError,
        match="FINGERPRINT_MISMATCH",
    ):
        SheriffOfficeAppointmentAuthority.from_dict(payload)


def test_persisted_payload_rejects_extra_fields() -> None:
    payload = _authority().to_dict()
    payload["iam_authorized"] = True

    with pytest.raises(
        SheriffOfficeAppointmentAuthorityError,
        match="PAYLOAD_SCHEMA_INVALID",
    ):
        SheriffOfficeAppointmentAuthority.from_dict(payload)


def test_verification_after_observation_does_not_make_prior_evidence_current() -> None:
    value = _authority(verified_at=NOW + timedelta(minutes=1))
    assert not value.is_current(NOW)
    assert value.is_current(NOW + timedelta(minutes=1))


# ARTIFACT: test_sheriff_office_appointment_authority.py
# VERSION: v1.0.0-L8-SHERIFF-OFFICE-APPOINTMENT-EVIDENCE-UNIT-CERT
# AUTHORITY BOUNDARY: pure immutable appointment/FFC evidence semantics only
# TENANT POSTURE: synthetic exact-tenant scope; no cross-tenant lookup
# FAIL-CLOSED POSTURE: malformed, stale, divergent, or tampered evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
