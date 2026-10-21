"""WILSY P47-R95-G37 — Practitioner-specific clearance domain tests.

The recorded decision is immutable evidence, NOT verified authority.
Only a future source-verifying transactional service may establish
operational clearance. Recording a CLEAR decision never grants matter
access, bypasses IAM, waives conflicts or defeats an ethical wall.
"""

from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone
import re

import pytest

from tools.eos.legal_operations.domain.legal_work_practitioner_confidentiality_clearance import (
    PractitionerConfidentialityClearanceError,
    PractitionerConfidentialityClearanceEvent,
    PractitionerConfidentialityClearanceState,
    project_practitioner_confidentiality_clearance,
)

NOW = datetime(2026, 10, 21, 10, 0, tzinfo=timezone.utc)


def clearance(**overrides):
    values = {
        "tenant_id": "tenant-a",
        "case_matter_id": "matter-a",
        "practitioner_principal_id": "practitioner-a",
        "clearance_event_id": "clearance-a",
        "predecessor_event_id": None,
        "decision": "CLEARED",
        "effective_at": NOW,
        "expires_at": NOW + timedelta(days=30),
        "issuer_principal_id": "partner-a",
        "issuer_authorization_evidence_reference": "iam-a",
        "conflict_provenance_fingerprint": "a" * 128,
        "confidentiality_decision_reference": "review-a",
    }
    values.update(overrides)
    return PractitionerConfidentialityClearanceEvent(**values)


def project(*events, tenant="tenant-a", matter="matter-a",
            practitioner="practitioner-a", at=NOW):
    return project_practitioner_confidentiality_clearance(
        tenant_id=tenant,
        case_matter_id=matter,
        practitioner_principal_id=practitioner,
        evaluation_time=at,
        events=events,
    )


def test_clearance_event_is_frozen():
    event = clearance()
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        setattr(event, "decision", "REVOKED")


def test_clearance_fingerprint_is_lowercase_sha3_512():
    event = clearance()
    assert re.fullmatch(r"[0-9a-f]{128}", event.fingerprint)


def test_exact_replay_is_deterministic():
    assert clearance().fingerprint == clearance().fingerprint


@pytest.mark.parametrize("field,value", [
    ("tenant_id", "tenant-b"),
    ("case_matter_id", "matter-b"),
    ("practitioner_principal_id", "practitioner-b"),
    ("issuer_principal_id", "partner-b"),
    ("confidentiality_decision_reference", "review-b"),
])
def test_every_scope_or_authority_change_changes_digest(field, value):
    assert clearance(**{field: value}).fingerprint != clearance().fingerprint


@pytest.mark.parametrize("field,value", [
    ("tenant_id", ""),
    ("tenant_id", "tenant-a "),
    ("case_matter_id", "*"),
    ("practitioner_principal_id", ""),
    ("issuer_authorization_evidence_reference", ""),
    ("conflict_provenance_fingerprint", "unverified"),
])
def test_noncanonical_evidence_rejected(field, value):
    with pytest.raises((PractitionerConfidentialityClearanceError,
                        ValueError, TypeError)):
        clearance(**{field: value})


def test_naive_time_rejected():
    with pytest.raises((PractitionerConfidentialityClearanceError,
                        ValueError, TypeError)):
        clearance(effective_at=NOW.replace(tzinfo=None))


def test_nonpositive_validity_window_rejected():
    with pytest.raises((PractitionerConfidentialityClearanceError,
                        ValueError, TypeError)):
        clearance(expires_at=NOW)


def test_no_record_is_not_cleared():
    state = project().state
    assert state is PractitionerConfidentialityClearanceState.NO_CLEARANCE


def test_recorded_clearance_is_unverified_not_operational_permission():
    current = project(clearance())
    assert current.state is (
        PractitionerConfidentialityClearanceState.CLEARED_UNVERIFIED
    )
    assert current.permits_operational_access is False


def test_foreign_tenant_event_fails_closed():
    current = project(clearance(tenant_id="tenant-b"))
    assert current.permits_operational_access is False
    assert current.state is (
        PractitionerConfidentialityClearanceState.CORRUPT_BLOCKED
    )


def test_clearance_expires_without_resurrection():
    current = project(
        clearance(),
        at=NOW + timedelta(days=31),
    )
    assert current.permits_operational_access is False


def test_caller_supplied_clearance_boolean_is_not_part_of_domain():
    with pytest.raises((TypeError, PractitionerConfidentialityClearanceError)):
        clearance(ethical_wall_cleared=True)


def test_event_has_no_operational_grant_method():
    assert not hasattr(clearance(), "authorize_matter_read")
    assert not hasattr(clearance(), "grant_assignment")


# P47-R95-G40 — adversarial lineage and historical integrity.
# A documentary CLEARED state is never operational access authorization.

def test_g40_tampered_event_digest_corrupt_blocked():
    event = clearance()
    object.__setattr__(event, "fingerprint", "f" * 128)
    current = project(event)
    assert current.state is (
        PractitionerConfidentialityClearanceState.CORRUPT_BLOCKED
    )
    assert current.permits_operational_access is False


def test_g40_future_revocation_not_retroactive_at_prior_evaluation():
    from datetime import timedelta
    root = clearance()
    successor = clearance(
        clearance_event_id="revocation-1",
        predecessor_event_id=root.clearance_event_id,
        decision="REVOKED",
        effective_at=NOW + timedelta(days=1),
        expires_at=NOW + timedelta(days=30),
    )
    before = project(root, successor, at=NOW + timedelta(hours=1))
    after = project(root, successor, at=NOW + timedelta(days=2))
    assert before.state is (
        PractitionerConfidentialityClearanceState.CLEARED_UNVERIFIED
    )
    assert after.state is (
        PractitionerConfidentialityClearanceState.REVOKED_BLOCKED
    )
    assert before.permits_operational_access is False
    assert after.permits_operational_access is False


def test_g40_duplicate_roots_corrupt_blocked():
    current = project(
        clearance(),
        clearance(clearance_event_id="clearance-other"),
    )
    assert current.state is (
        PractitionerConfidentialityClearanceState.CORRUPT_BLOCKED
    )


def test_g40_orphan_successor_corrupt_blocked():
    current = project(clearance(
        clearance_event_id="revocation-orphan",
        predecessor_event_id="missing-root",
        decision="REVOKED",
    ))
    assert current.state is (
        PractitionerConfidentialityClearanceState.CORRUPT_BLOCKED
    )


def test_g40_successor_fork_corrupt_blocked():
    from datetime import timedelta
    root = clearance()
    one = clearance(
        clearance_event_id="deny-1",
        predecessor_event_id=root.clearance_event_id,
        decision="DENIED",
        effective_at=NOW + timedelta(hours=1),
    )
    two = clearance(
        clearance_event_id="revoke-2",
        predecessor_event_id=root.clearance_event_id,
        decision="REVOKED",
        effective_at=NOW + timedelta(hours=2),
    )
    assert project(root, one, two).state is (
        PractitionerConfidentialityClearanceState.CORRUPT_BLOCKED
    )


def test_g40_backdated_successor_corrupt_blocked():
    from datetime import timedelta
    root = clearance()
    backdated = clearance(
        clearance_event_id="deny-backdated",
        predecessor_event_id=root.clearance_event_id,
        decision="DENIED",
        effective_at=NOW - timedelta(days=1),
        expires_at=NOW + timedelta(days=1),
    )
    assert project(root, backdated).state is (
        PractitionerConfidentialityClearanceState.CORRUPT_BLOCKED
    )


# P47-R95-G42: terminal lifecycle, integrity, and temporal boundaries.
# A CLEARED_UNVERIFIED projection still never permits operational access.


@pytest.mark.parametrize("field,new_value", [
    ("tenant_id", "tenant-forged"),
    ("case_matter_id", "matter-forged"),
    ("practitioner_principal_id", "practitioner-forged"),
    ("issuer_principal_id", "partner-forged"),
])
def test_g42_mutated_identity_rejected(field, new_value):
    event = clearance()
    object.__setattr__(event, field, new_value)
    result = project(event)
    assert result.state is (
        PractitionerConfidentialityClearanceState.CORRUPT_BLOCKED
    )
    assert result.permits_operational_access is False


def test_g42_mutated_decision_rejected():
    event = clearance()
    object.__setattr__(event, "decision", "DENIED")
    assert project(event).state is (
        PractitionerConfidentialityClearanceState.CORRUPT_BLOCKED
    )


def test_g42_mutated_expiry_rejected():
    event = clearance()
    object.__setattr__(
        event, "expires_at", NOW + timedelta(days=90)
    )
    assert project(event).state is (
        PractitionerConfidentialityClearanceState.CORRUPT_BLOCKED
    )


@pytest.mark.parametrize("terminal", ["REVOKED", "DENIED"])
def test_g42_terminal_successor_cannot_reactivate_clearance(terminal):
    root = clearance()
    terminal_event = clearance(
        clearance_event_id="terminal-event",
        predecessor_event_id=root.clearance_event_id,
        decision=terminal,
        effective_at=NOW + timedelta(days=1),
    )
    unlawful_reclearance = clearance(
        clearance_event_id="reactivation-event",
        predecessor_event_id=terminal_event.clearance_event_id,
        decision="CLEARED",
        effective_at=NOW + timedelta(days=2),
    )
    assert project(root, terminal_event, unlawful_reclearance).state is (
        PractitionerConfidentialityClearanceState.CORRUPT_BLOCKED
    )


@pytest.mark.parametrize("terminal,expected", [
    ("REVOKED", PractitionerConfidentialityClearanceState.REVOKED_BLOCKED),
    ("DENIED", PractitionerConfidentialityClearanceState.DENIED_BLOCKED),
])
def test_g42_terminal_currentness_persists_after_expiry(terminal, expected):
    root = clearance()
    terminal_event = clearance(
        clearance_event_id="terminal-end",
        predecessor_event_id=root.clearance_event_id,
        decision=terminal,
        effective_at=NOW + timedelta(days=1),
    )
    current = project(
        root, terminal_event,
        at=NOW + timedelta(days=60),
    )
    assert current.state is expected
    assert current.permits_operational_access is False


def test_g42_expiry_is_exclusive_boundary():
    root = clearance()
    at_expiry = project(
        root, at=NOW + timedelta(days=30)
    )
    assert at_expiry.state is (
        PractitionerConfidentialityClearanceState.EXPIRED_BLOCKED
    )
    assert at_expiry.permits_operational_access is False


def test_g42_future_root_not_yet_effective():
    root = clearance(
        effective_at=NOW + timedelta(days=1),
    )
    at = project(root, at=NOW)
    assert at.state is (
        PractitionerConfidentialityClearanceState.NO_CLEARANCE
    )
    assert at.permits_operational_access is False


def test_g42_duplicate_event_identity_rejected():
    root = clearance()
    repeated = clearance()
    assert project(root, repeated).state is (
        PractitionerConfidentialityClearanceState.CORRUPT_BLOCKED
    )


def test_g42_noncanonical_reconstructed_event_rejected():
    event = clearance()
    object.__setattr__(event, "tenant_id", "tenant-a ")
    assert project(event).state is (
        PractitionerConfidentialityClearanceState.CORRUPT_BLOCKED
    )
