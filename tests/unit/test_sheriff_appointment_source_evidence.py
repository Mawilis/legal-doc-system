"""TITLE: Sheriff Appointment Source Evidence Unit Certificate
VERSION: v1.0.0-SHERIFF-APPOINTMENT-SOURCE-EVIDENCE-UNIT-CERT
AUTHORITY: Pure immutable source-evidence contract certification only.
EPITOME: Prove statutory capacity/basis/issuer constraints, supporting Board
    evidence, canonical fingerprints, tenant scope and authority exclusions.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_sheriff_appointment_source_evidence.py
COLLABORATION / OWNERSHIP: Unit certificate for the Sheriff appointment
    source-evidence domain only; no IAM, registry, route or external trust root.
CERTIFICATION / UPDATE DATE: 2026-11-02
CHANGELOG:
    2026-11-02 v1.0.0-SHERIFF-APPOINTMENT-SOURCE-EVIDENCE-UNIT-CERT
    Establishes adversarial statutory-shape, source-provenance, fingerprint,
    lineage and no-authority unit coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and test fingerprints.
TENANT BOUNDARY: Exact tenant only; pseudo tenants reject.
AUTHORITY BOUNDARY: No statutory appointment, IAM, office access or execution.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.sheriff_appointment_source_evidence import (
    SheriffAppointmentCapacity,
    SheriffAppointmentIssuerAuthority,
    SheriffAppointmentSourceEvidence,
    SheriffAppointmentSourceEvidenceError,
    SheriffAppointmentStatutoryBasis,
    SheriffSourceObservationState,
    SheriffSourceVerificationMethod,
)


NOW = datetime(2026, 11, 2, 10, 0, tzinfo=timezone.utc)
INSTRUMENT_FP = "a" * 128
BOARD_FP = "b" * 128
CONDITIONS_FP = "c" * 128


def evidence(**overrides: object) -> SheriffAppointmentSourceEvidence:
    """Build one synthetic section 2(1) Sheriff appointment observation."""
    values: dict[str, object] = {
        "tenant_id": "tenant-a",
        "evidence_id": "appointment-evidence-1",
        "revision": 1,
        "principal_id": "principal-sheriff",
        "verified_subject_reference": "person-subject-1",
        "sheriff_office_id": "office-jhb",
        "district_id": "district-jhb",
        "court_reference": "court-magistrates-jhb",
        "service_area_references": ("area-jhb-central",),
        "capacity": SheriffAppointmentCapacity.SHERIFF,
        "statutory_basis": SheriffAppointmentStatutoryBasis.SECTION_2_1,
        "issuer_authority": SheriffAppointmentIssuerAuthority.MINISTER,
        "instrument_reference": "ministerial-appointment-1",
        "instrument_fingerprint": INSTRUMENT_FP,
        "source_uri": "https://www.justice.gov.za/notice/appointment-1",
        "source_observation_state": SheriffSourceObservationState.HUMAN_OBSERVED_PUBLIC_RECORD,
        "source_verification_method": SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION,
        "source_verification_reference": "observation-1",
        "verified_by_principal_id": "independent-verifier",
        "observed_at": NOW,
        "effective_from": NOW - timedelta(days=1),
        "effective_until": None,
    }
    values.update(overrides)
    return SheriffAppointmentSourceEvidence(**values)  # type: ignore[arg-type]


def test_exact_source_observation_is_immutable_and_non_authorizing() -> None:
    item = evidence()
    assert item.tenant_id == "tenant-a"
    assert item.capacity is SheriffAppointmentCapacity.SHERIFF
    assert item.fingerprint == item.to_dict()["fingerprint"]
    assert len(item.fingerprint) == 128
    assert item.permits_operational_access is False
    assert item.permits_legal_execution is False
    assert item.is_authenticated_appointment is False
    with pytest.raises(FrozenInstanceError):
        item.tenant_id = "tenant-b"  # type: ignore[misc]


def test_semantic_fingerprint_is_deterministic_and_changes_with_scope() -> None:
    first = evidence()
    replay = evidence()
    changed = evidence(service_area_references=("area-jhb-north",))
    assert first.fingerprint == replay.fingerprint
    assert first.fingerprint != changed.fingerprint


@pytest.mark.parametrize("tenant", ["default", "global", "root", "*"])
def test_pseudo_tenant_is_rejected(tenant: str) -> None:
    with pytest.raises(SheriffAppointmentSourceEvidenceError) as error:
        evidence(tenant_id=tenant)
    assert error.value.code == "SHERIFF_SOURCE_TENANT_ID_INVALID"


@pytest.mark.parametrize(
    ("capacity", "basis", "issuer"),
    [
        (
            SheriffAppointmentCapacity.SHERIFF,
            SheriffAppointmentStatutoryBasis.SECTION_5_1,
            SheriffAppointmentIssuerAuthority.MINISTER,
        ),
        (
            SheriffAppointmentCapacity.DEPUTY_SHERIFF,
            SheriffAppointmentStatutoryBasis.SECTION_2_1,
            SheriffAppointmentIssuerAuthority.MINISTER,
        ),
        (
            SheriffAppointmentCapacity.SECTION_6A_DESIGNEE,
            SheriffAppointmentStatutoryBasis.SECTION_6A_1,
            SheriffAppointmentIssuerAuthority.SHERIFF,
        ),
        (
            SheriffAppointmentCapacity.SECTION_6B_FUNCTION_APPOINTMENT,
            SheriffAppointmentStatutoryBasis.SECTION_6B_1,
            SheriffAppointmentIssuerAuthority.MINISTER,
        ),
    ],
)
def test_capacity_basis_and_issuer_must_match(
    capacity: SheriffAppointmentCapacity,
    basis: SheriffAppointmentStatutoryBasis,
    issuer: SheriffAppointmentIssuerAuthority,
) -> None:
    with pytest.raises(SheriffAppointmentSourceEvidenceError) as error:
        evidence(capacity=capacity, statutory_basis=basis, issuer_authority=issuer)
    assert error.value.code in {
        "SHERIFF_SOURCE_CAPACITY_BASIS_MISMATCH",
        "SHERIFF_SOURCE_ISSUER_CAPACITY_MISMATCH",
        "SHERIFF_SOURCE_DEPUTY_ISSUER_INVALID",
        "SHERIFF_SOURCE_SECTION_6B_BOARD_CONSULTATION_REQUIRED",
    }


def test_deputy_sheriff_requires_appointing_sheriff_and_board_approval() -> None:
    values = {
        "capacity": SheriffAppointmentCapacity.DEPUTY_SHERIFF,
        "statutory_basis": SheriffAppointmentStatutoryBasis.SECTION_6_1,
        "issuer_authority": SheriffAppointmentIssuerAuthority.SHERIFF,
    }
    with pytest.raises(SheriffAppointmentSourceEvidenceError) as missing:
        evidence(**values)
    assert missing.value.code == "SHERIFF_SOURCE_DEPUTY_BOARD_APPROVAL_REQUIRED"

    item = evidence(
        **values,
        appointing_principal_id="principal-appointing-sheriff",
        board_approval_reference="sabfs-approval-1",
        board_approval_fingerprint=BOARD_FP,
    )
    assert item.capacity is SheriffAppointmentCapacity.DEPUTY_SHERIFF
    assert item.permits_operational_access is False

    with pytest.raises(SheriffAppointmentSourceEvidenceError) as self_appointed:
        evidence(
            **values,
            appointing_principal_id="principal-sheriff",
            board_approval_reference="sabfs-approval-1",
            board_approval_fingerprint=BOARD_FP,
        )
    assert self_appointed.value.code == "SHERIFF_SOURCE_DEPUTY_SELF_APPOINTMENT_FORBIDDEN"


@pytest.mark.parametrize(
    ("basis", "extra", "expected"),
    [
        (
            SheriffAppointmentStatutoryBasis.SECTION_2_3,
            {},
            "SHERIFF_SOURCE_SECTION_2_3_BOARD_CONFIRMATION_REQUIRED",
        ),
        (
            SheriffAppointmentStatutoryBasis.SECTION_5_1,
            {},
            "SHERIFF_SOURCE_SECTION_5_1_BOARD_CONFIRMATION_REQUIRED",
        ),
        (
            SheriffAppointmentStatutoryBasis.SECTION_6B_1,
            {},
            "SHERIFF_SOURCE_SECTION_6B_BOARD_CONSULTATION_REQUIRED",
        ),
    ],
)
def test_special_statutory_paths_require_board_evidence(
    basis: SheriffAppointmentStatutoryBasis,
    extra: dict[str, object],
    expected: str,
) -> None:
    capacity = (
        SheriffAppointmentCapacity.SHERIFF
        if basis is SheriffAppointmentStatutoryBasis.SECTION_2_3
        else SheriffAppointmentCapacity.ACTING_SHERIFF
        if basis is SheriffAppointmentStatutoryBasis.SECTION_5_1
        else SheriffAppointmentCapacity.SECTION_6B_FUNCTION_APPOINTMENT
    )
    with pytest.raises(SheriffAppointmentSourceEvidenceError) as error:
        evidence(
            capacity=capacity,
            statutory_basis=basis,
            issuer_authority=SheriffAppointmentIssuerAuthority.MINISTER,
            **extra,
        )
    assert error.value.code == expected


def test_section_6a_designee_is_distinct_and_has_no_section_30_claim() -> None:
    item = evidence(
        capacity=SheriffAppointmentCapacity.SECTION_6A_DESIGNEE,
        statutory_basis=SheriffAppointmentStatutoryBasis.SECTION_6A_1,
        issuer_authority=SheriffAppointmentIssuerAuthority.MINISTER,
        effective_until=NOW + timedelta(days=7),
    )
    assert item.capacity is SheriffAppointmentCapacity.SECTION_6A_DESIGNEE
    assert item.effective_until == NOW + timedelta(days=7)
    assert item.is_authenticated_appointment is False


def test_self_attestation_and_invalid_source_fingerprint_reject() -> None:
    with pytest.raises(SheriffAppointmentSourceEvidenceError) as self_attested:
        evidence(verified_by_principal_id="principal-sheriff")
    assert self_attested.value.code == "SHERIFF_SOURCE_SELF_ATTESTATION_FORBIDDEN"

    with pytest.raises(SheriffAppointmentSourceEvidenceError) as bad_digest:
        evidence(instrument_fingerprint="not-a-digest")
    assert bad_digest.value.code == "SHERIFF_SOURCE_INSTRUMENT_FINGERPRINT_INVALID"


def test_source_observation_method_pair_must_be_consistent() -> None:
    with pytest.raises(SheriffAppointmentSourceEvidenceError) as error:
        evidence(
            source_observation_state=SheriffSourceObservationState.AUTHENTICATED_RESPONSE,
            source_verification_method=SheriffSourceVerificationMethod.PUBLIC_WEB_OBSERVATION,
        )
    assert error.value.code == "SHERIFF_SOURCE_OBSERVATION_METHOD_MISMATCH"


def test_effective_window_and_service_area_are_required() -> None:
    with pytest.raises(SheriffAppointmentSourceEvidenceError) as window:
        evidence(effective_until=NOW - timedelta(days=2))
    assert window.value.code == "SHERIFF_SOURCE_EFFECTIVE_WINDOW_INVALID"

    with pytest.raises(SheriffAppointmentSourceEvidenceError) as areas:
        evidence(service_area_references=())
    assert areas.value.code == "SHERIFF_SOURCE_SERVICE_AREA_REFERENCE_INVALID"


def test_append_only_revision_requires_predecessor() -> None:
    with pytest.raises(SheriffAppointmentSourceEvidenceError) as missing:
        evidence(revision=2)
    assert missing.value.code == "SHERIFF_SOURCE_SUCCESSOR_REQUIRED"

    predecessor = evidence()
    successor = evidence(
        revision=2,
        supersedes_fingerprint=predecessor.fingerprint,
        effective_from=NOW + timedelta(days=1),
        observed_at=NOW,
    )
    assert successor.supersedes_fingerprint == predecessor.fingerprint


def test_supplied_fingerprint_cannot_be_replaced_or_forged() -> None:
    item = evidence()
    with pytest.raises(SheriffAppointmentSourceEvidenceError) as error:
        replace(item, fingerprint="0" * 128)
    assert error.value.code == "SHERIFF_SOURCE_FINGERPRINT_MISMATCH"


# WILSY OS SOVEREIGN ARTIFACT SEAL
# ARTIFACT: tests/unit/test_sheriff_appointment_source_evidence.py
# VERSION: v1.0.0-SHERIFF-APPOINTMENT-SOURCE-EVIDENCE-UNIT-CERT
# AUTHORITY BOUNDARY: pure source-evidence contract certification only
# TENANT POSTURE: exact tenant; pseudo tenant values reject
# FAIL-CLOSED POSTURE: statutory mismatch, missing Board evidence, self-attestation,
# malformed source, invalid chronology and fingerprint forgery reject
# FINANCIAL EXECUTION AUTHORITY: NONE; KENNEL EOS EXCLUSIVELY
# END OF WILSY OS SOVEREIGN ARTIFACT
