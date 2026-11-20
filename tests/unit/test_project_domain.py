"""TITLE: WILSY OS tenant project domain tests
VERSION: v1.1.0-IMMUTABLE-PROJECT-BASELINE-CERT
AUTHORITY: Verification of the pure Python EOS Projects aggregate.
EPITOME: Certifies project schema, tenant-bound fingerprints, timestamp rules,
         update revisions, status transitions, and soft-archive invariants.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_domain.py
COLLABORATION / OWNERSHIP: Project domain artifact and Python EOS test suite.
CERTIFICATION / UPDATE DATE: 2026-11-16.
CHANGELOG:
v1.1.0-IMMUTABLE-PROJECT-BASELINE-CERT proves that saved code and
start dates cannot be changed or cleared, while legacy unset facts can be
initialized exactly once and then become immutable.
v1.0.0-TENANT-PROJECT-DOMAIN-TESTS — Governance metadata synchronized with unchanged executable behavior. v1.0.0 establishes focused tests for the initial Projects domain.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic unit values only; no credentials or live tenant records.
TENANT BOUNDARY: Proves explicit tenant inclusion in canonical project serialization.
AUTHORITY BOUNDARY: Pure domain tests; no access grants or persistence are exercised.
FINANCIAL AUTHORITY BOUNDARY: No financial execution behavior is represented.
"""
from datetime import date, datetime, timedelta, timezone

import pytest

from tools.eos.saas.domain.project import (
    Project,
    ProjectError,
    ProjectSourceType,
    ProjectStatus,
)


NOW = datetime(2026, 11, 16, 12, 0, tzinfo=timezone.utc)


def project(**changes: object) -> Project:
    """Construct one isolated canonical fixture for pure domain tests."""
    values: dict[str, object] = {
        "project_id": "project-test-001",
        "tenant_id": "tenant-test-a",
        "name": "Internal delivery",
        "code": "DEL-001",
        "summary": "Bounded project summary.",
        "status": ProjectStatus.PLANNED,
        "owner_principal_id": None,
        "department_id": None,
        "start_date": date(2026, 11, 1),
        "target_date": date(2026, 12, 1),
        "source_type": ProjectSourceType.INTERNAL,
        "external_source_reference": None,
        "created_by_principal_id": "principal-test-a",
        "created_at": NOW,
        "updated_by_principal_id": "principal-test-a",
        "updated_at": NOW,
    }
    values.update(changes)
    return Project(**values)  # type: ignore[arg-type]


def test_project_round_trips_exact_persisted_shape_and_fingerprint() -> None:
    value = project()
    restored = Project.from_dict(value.to_dict())
    assert restored == value
    assert len(value.fingerprint) == 128


def test_project_fingerprint_binds_tenant_and_rejects_tampering() -> None:
    value = project()
    payload = value.to_dict()
    payload["tenant_id"] = "tenant-test-b"
    with pytest.raises(ProjectError, match="FINGERPRINT_MISMATCH"):
        Project.from_dict(payload)


def test_unknown_persisted_field_is_rejected() -> None:
    payload = project().to_dict()
    payload["unreviewed_authority"] = True
    with pytest.raises(ProjectError, match="PERSISTED_SCHEMA_INVALID"):
        Project.from_dict(payload)


def test_schedule_rejects_target_before_start() -> None:
    with pytest.raises(ProjectError, match="TARGET_BEFORE_START"):
        project(start_date=date(2026, 12, 2), target_date=date(2026, 12, 1))


def test_timestamps_must_be_aware_and_mutations_must_be_monotonic() -> None:
    with pytest.raises(ProjectError, match="CREATED_AT_TIMESTAMP_INVALID"):
        project(created_at=datetime(2026, 11, 16, 12, 0))
    with pytest.raises(ProjectError, match="TIMESTAMP_ORDER_INVALID"):
        project().update(
            actor_principal_id="principal-test-a",
            updated_at=NOW - timedelta(seconds=1),
            expected_revision=1,
            changes={"name": "Earlier timestamp"},
        )


def test_update_advances_revision_preserves_scope_and_allows_explicit_clear() -> None:
    changed = project().update(
        actor_principal_id="principal-test-a",
        updated_at=NOW + timedelta(seconds=1),
        expected_revision=1,
        changes={"summary": None, "owner_principal_id": "principal-test-b"},
    )
    assert changed.revision == 2
    assert changed.summary is None
    assert changed.owner_principal_id == "principal-test-b"
    assert changed.tenant_id == "tenant-test-a"
    assert changed.updated_by_principal_id == "principal-test-a"


def test_update_rejects_authority_and_identity_fields() -> None:
    with pytest.raises(ProjectError, match="UPDATE_FIELDS_INVALID"):
        project().update(
            actor_principal_id="principal-test-a",
            updated_at=NOW + timedelta(seconds=1),
            expected_revision=1,
            changes={"tenant_id": "tenant-test-b"},
        )


def test_committed_project_code_and_start_date_are_immutable() -> None:
    value = project()
    for changes, rejection in (
        ({"code": "DEL-002"}, "PROJECT_CODE_IMMUTABLE"),
        ({"code": None}, "PROJECT_CODE_IMMUTABLE"),
        ({"start_date": date(2026, 11, 2)}, "PROJECT_START_DATE_IMMUTABLE"),
        ({"start_date": None}, "PROJECT_START_DATE_IMMUTABLE"),
    ):
        with pytest.raises(ProjectError, match=rejection):
            value.update(
                actor_principal_id="principal-test-a",
                updated_at=NOW + timedelta(seconds=1),
                expected_revision=1, changes=changes,
            )


def test_legacy_unset_project_baseline_can_be_initialized_only_once() -> None:
    legacy = project(code=None, start_date=None)
    initial = legacy.update(
        actor_principal_id="principal-test-a",
        updated_at=NOW + timedelta(seconds=1),
        expected_revision=1,
        changes={"code": "MIGRATED-001", "start_date": date(2026, 11, 1)},
    )
    assert initial.code == "MIGRATED-001"
    assert initial.start_date == date(2026, 11, 1)
    with pytest.raises(ProjectError, match="PROJECT_CODE_IMMUTABLE"):
        initial.update(
            actor_principal_id="principal-test-a",
            updated_at=NOW + timedelta(seconds=2),
            expected_revision=2, changes={"code": "REWRITTEN"},
        )


def test_status_transition_graph_and_terminal_states_are_enforced() -> None:
    active = project().transition(
        actor_principal_id="principal-test-a",
        updated_at=NOW + timedelta(seconds=1),
        expected_revision=1,
        resulting_status=ProjectStatus.ACTIVE,
    )
    assert active.status is ProjectStatus.ACTIVE
    with pytest.raises(ProjectError, match="STATUS_TRANSITION_INVALID"):
        active.transition(
            actor_principal_id="principal-test-a",
            updated_at=NOW + timedelta(seconds=2),
            expected_revision=2,
            resulting_status=ProjectStatus.PLANNED,
        )


def test_archive_is_soft_and_prevents_later_mutation() -> None:
    archived = project().archive(
        actor_principal_id="principal-test-a",
        archived_at=NOW + timedelta(seconds=1),
        expected_revision=1,
    )
    assert archived.status is ProjectStatus.PLANNED
    assert archived.archived_at == NOW + timedelta(seconds=1)
    assert Project.from_dict(archived.to_dict()) == archived
    with pytest.raises(ProjectError, match="ARCHIVED_IMMUTABLE"):
        archived.update(
            actor_principal_id="principal-test-a",
            updated_at=NOW + timedelta(seconds=2),
            expected_revision=2,
            changes={"name": "Changed"},
        )


def test_certified_external_source_requires_bounded_source_reference() -> None:
    with pytest.raises(ProjectError, match="EXTERNAL_REFERENCE_REQUIRED"):
        project(source_type=ProjectSourceType.CERTIFIED_EXTERNAL)
    with pytest.raises(ProjectError, match="EXTERNAL_REFERENCE_FORBIDDEN"):
        project(external_source_reference="unverified-source-record")


def test_stale_revision_fails_closed() -> None:
    with pytest.raises(ProjectError, match="REVISION_CONFLICT"):
        project().archive(
            actor_principal_id="principal-test-a",
            archived_at=NOW + timedelta(seconds=1),
            expected_revision=2,
        )


# ARTIFACT: test_project_domain.py
# VERSION: v1.1.0-IMMUTABLE-PROJECT-BASELINE-CERT
# AUTHORITY BOUNDARY: pure domain invariant tests only
# TENANT POSTURE: synthetic exact-tenant fixtures; no live tenant reads
# FAIL-CLOSED POSTURE: domain validation and lifecycle regression assertions are mandatory
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
