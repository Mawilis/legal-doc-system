"""Adversarial unit tests for purpose-bound process-service GPS evidence.

ARTIFACT: test_process_service_location_evidence_authority.py
VERSION: v1.0.0-PROCESS-SERVICE-LOCATION-EVIDENCE-TESTS
AUTHORITY BOUNDARY: synthetic unit evidence only; no legal service or runtime authority.
TENANT POSTURE: isolated synthetic tenant and exact allocation/attempt binding.
FAIL-CLOSED POSTURE: permission, chronology, device, coordinate and integrity drift reject.
FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ServiceAttempt,
    ServiceAttemptState,
)
from tools.eos.legal_operations.domain.process_service_location_evidence_authority import (
    LOCATION_PURPOSE,
    ProcessServiceLocationEvidenceAuthorityError,
    ProcessServiceLocationObservation,
    ProcessServiceLocationPermissionGrant,
    create_location_permission_grant,
    create_process_service_location_observation,
)
from tools.eos.legal_operations.registry.process_service_allocation_registry import (
    ProcessServiceAllocationCurrent,
    ProcessServiceAllocationReceipt,
)

BASE = datetime(2026, 10, 30, 8, 0, tzinfo=timezone.utc)
HASH = "a" * 128


def context():
    attempt = ServiceAttempt(
        tenant_id="tenant-a", attempt_id="attempt-1",
        instruction_id="instruction-1", document_id="document-1",
        deputy_id="deputy-1", allocated_at=BASE,
        allocation_evidence_reference="allocation",
    ).transition_to(
        ServiceAttemptState.ATTEMPTED, evidence_reference="attempt-proof",
        evidence_fingerprint=HASH, occurred_at=BASE + timedelta(minutes=1),
    )
    receipt = ProcessServiceAllocationReceipt(
        tenant_id="tenant-a", allocation_command_id="allocation-command",
        idempotency_key="allocation-key", instruction_id="instruction-1",
        case_matter_id="matter-1", document_id="document-1", district_id="district-1",
        sheriff_office_id="office-1", deputy_id="deputy-1",
        assignment_decision_id="assignment-1", assignment_decision_fingerprint=HASH,
        source_instruction_fingerprint=HASH, source_document_fingerprint=HASH,
        source_district_fingerprint=HASH, source_sheriff_office_fingerprint=HASH,
        source_deputy_fingerprint=HASH, prior_custody_chain_fingerprint=HASH,
        prior_custody_head_event_id="head-1", prior_custody_head_fingerprint=HASH,
        prior_custody_head_sequence_number=1, from_holder_reference="office-1",
        to_holder_reference="deputy-1", allocation_custody_event_id="allocation-event",
        allocation_evidence_reference="allocation", allocated_at=BASE,
        allocated_document_fingerprint=HASH, allocation_custody_event_fingerprint=HASH,
        result_custody_chain_fingerprint=HASH,
    )
    current = ProcessServiceAllocationCurrent(
        tenant_id="tenant-a", document_id="document-1",
        process_document_fingerprint=HASH, custody_chain_fingerprint=HASH,
        custody_head_event_id="allocation-event", custody_head_fingerprint=HASH,
        custody_head_sequence_number=2, current_holder_reference="deputy-1",
        authority_evidence_reference="allocation-command",
        authority_evidence_fingerprint=receipt.fingerprint,
    )
    return attempt, receipt, current


def grant(*, allowed: bool = True, device: str = "device-1"):
    attempt, receipt, current = context()
    return create_location_permission_grant(
        attempt=attempt, allocation_receipt=receipt, allocation_current=current,
        grant_id="grant-1", device_id=device, permission_granted=allowed,
        purpose=LOCATION_PURPOSE, permission_evidence_reference="consent-1",
        permission_evidence_fingerprint=HASH, granted_at=BASE + timedelta(minutes=2),
        expires_at=BASE + timedelta(hours=1),
    )


def observation(**changes):
    attempt, receipt, current = context()
    values = {
        "attempt": attempt, "allocation_receipt": receipt,
        "allocation_current": current, "permission_grant": grant(),
        "observation_id": "observation-1", "device_id": "device-1",
        "latitude": -26.2041, "longitude": 28.0473,
        "horizontal_accuracy_m": 12.5,
        "captured_at": BASE + timedelta(minutes=3),
        "device_provenance_reference": "device-attestation-1",
        "device_provenance_fingerprint": HASH,
        "evidence_reference": "gps-evidence-1",
    }
    values.update(changes)
    return create_process_service_location_observation(**values)


def test_explicit_permission_and_exact_attempt_binding() -> None:
    value = observation()
    assert value.attempt_id == "attempt-1"
    assert value.deputy_id == "deputy-1"
    assert value.sheriff_office_id == "office-1"
    assert value.purpose == LOCATION_PURPOSE
    assert len(value.fingerprint) == 128
    assert value.to_dict()["latitude"] == -26.2041


def test_permission_denial_and_wrong_purpose_fail_closed() -> None:
    attempt, receipt, current = context()
    with pytest.raises(ProcessServiceLocationEvidenceAuthorityError):
        create_location_permission_grant(
            attempt=attempt, allocation_receipt=receipt, allocation_current=current,
            grant_id="grant-1", device_id="device-1", permission_granted=False,
            purpose=LOCATION_PURPOSE, permission_evidence_reference="consent",
            permission_evidence_fingerprint=HASH, granted_at=BASE + timedelta(minutes=2),
            expires_at=BASE + timedelta(hours=1),
        )
    with pytest.raises(ProcessServiceLocationEvidenceAuthorityError):
        create_location_permission_grant(
            attempt=attempt, allocation_receipt=receipt, allocation_current=current,
            grant_id="grant-1", device_id="device-1", permission_granted=True,
            purpose="BACKGROUND_TRACKING", permission_evidence_reference="consent",
            permission_evidence_fingerprint=HASH, granted_at=BASE + timedelta(minutes=2),
            expires_at=BASE + timedelta(hours=1),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("latitude", 91.0), ("latitude", float("nan")),
        ("longitude", -181.0), ("longitude", float("inf")),
        ("horizontal_accuracy_m", 0.0), ("horizontal_accuracy_m", 10001.0),
        ("device_id", "other-device"),
        ("captured_at", BASE + timedelta(hours=2)),
    ],
)
def test_invalid_location_and_scope_are_rejected(field: str, value: object) -> None:
    with pytest.raises(ProcessServiceLocationEvidenceAuthorityError):
        observation(**{field: value})


def test_direct_construction_is_rejected_and_no_service_authority_is_exposed() -> None:
    value = observation()
    with pytest.raises(ProcessServiceLocationEvidenceAuthorityError):
        ProcessServiceLocationObservation(
            tenant_id=value.tenant_id, observation_id=value.observation_id,
            grant_id=value.grant_id, attempt_id=value.attempt_id,
            deputy_id=value.deputy_id, device_id=value.device_id,
            district_id=value.district_id, sheriff_office_id=value.sheriff_office_id,
            source_attempt_fingerprint=value.source_attempt_fingerprint,
            purpose=value.purpose, latitude=value.latitude, longitude=value.longitude,
            horizontal_accuracy_m=value.horizontal_accuracy_m, captured_at=value.captured_at,
            device_provenance_reference=value.device_provenance_reference,
            device_provenance_fingerprint=value.device_provenance_fingerprint,
            permission_grant_fingerprint=value.permission_grant_fingerprint,
            evidence_reference=value.evidence_reference,
        )
    with pytest.raises(ProcessServiceLocationEvidenceAuthorityError):
        ProcessServiceLocationPermissionGrant(
            tenant_id="tenant-a", grant_id="grant", attempt_id="attempt-1",
            deputy_id="deputy-1", device_id="device-1", purpose=LOCATION_PURPOSE,
            permission_evidence_reference="consent",
            permission_evidence_fingerprint=HASH, granted_at=BASE,
            expires_at=BASE + timedelta(hours=1),
        )
    assert not hasattr(
        __import__(
            "tools.eos.legal_operations.domain.process_service_location_evidence_authority",
            fromlist=["x"],
        ),
        "ServiceExecution",
    )
