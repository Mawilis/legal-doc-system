"""TITLE: WILSY OS Source-Owned Project Work Purpose Certificate
VERSION: v1.2.0-AUDITED-UNCLASSIFIED-REVERT-CERT
AUTHORITY: Test-only proof of canonical Projects work purpose commands.
EPITOME: No-network immutable audit, current source, CAS, replay and denial.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_work_purpose_registry.py
COLLABORATION / OWNERSHIP: ProjectWorkPurposeRegistry; Projects router
remains responsible for live exact-tenant and project:update admission.
CERTIFICATION / UPDATE DATE: 2026-11-23
CHANGELOG: v1.2.0-AUDITED-UNCLASSIFIED-REVERT-CERT proves
audited reasoned clearance to UNCLASSIFIED without inventing live
source-verified category, and later source-owner reclassification.
CHANGELOG: v1.1.1-AUDIT-ACTOR-TAMPER-REJECTION-CERT
proves immutable event actor drift or forged recorded time is rejected in
both direct and batch readback, even when source snapshot remains valid.
CHANGELOG: v1.1.0-BOUNDED-AUDITED-PURPOSE-BATCH-CERT proves
511 admitted work records use three bounded purpose source queries and one
immutable-event proof query, with visible unclassified rows and no foreign
or invalid audit acceptance.
CHANGELOG: v1.0.1-STALE-PURPOSE-RECOVERY-AUDIT-CERT
verifies stale task revisions preserve exact audited metadata CAS while
returning UNCLASSIFIED, supports explicit reclassification after task edits,
and checks identical replay without opaque fingerprint inference.
CHANGELOG: v1.0.0-PROJECT-WORK-PURPOSE-CAS-AUDIT-CERT certifies
one atomic synthetic classification, source-only proof, independent metadata
revision, replay, divergent mutation rejection, task drift and audit tampering.
COMPLIANCE: AGENTS.md; POPIA section 19; GDPR Article 32; SOC2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers, no network, no PII.
TENANT BOUNDARY: Exact project/task/tenant query required.
AUTHORITY BOUNDARY: No role assignment or source mutation in this test.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from tools.eos.saas.projects.project_work_purpose_registry import (
    ProjectWorkPurposeRegistry, WorkPurposeConflict, WorkPurposeError,
)

NOW = datetime(2026, 11, 23, 0, 0, tzinfo=timezone.utc)
TENANT = "WILSYTENANT-4CD2FZ4O"
PROJECT = "prj-" + "a" * 48
TASK = "ptk-" + "b" * 48
ACTOR = "synthetic-project-owner"


class Collection:
    """Synthetic source collection honoring exact filtered equality and CAS."""

    def __init__(self):
        """Initialize a standalone in-memory transactional double."""
        self.rows = []
        self.indexes = []

    def create_index(self, fields, **kwargs):
        """Store exact index contract without opening Mongo connections."""
        self.indexes.append((fields, kwargs))

    def find_one(self, query, session):
        """Read one exact match, excluding transient Mongo document internals."""
        assert session == "caller-session"
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return deepcopy(row)
        return None

    def find(self, query, session):
        """Apply bounded equality, $in and $or batch matching."""
        assert session == "caller-session"
        self.batch_reads = getattr(self, "batch_reads", 0) + 1

        def matches(row, criteria):
            return all(
                any(matches(row, option) for option in expected)
                if key == "$or" else (
                    row.get(key) in expected["$in"]
                    if isinstance(expected, dict) and "$in" in expected
                    else row.get(key) == expected
                )
                for key, expected in criteria.items()
            )

        return [deepcopy(row) for row in self.rows if matches(row, query)]

    def insert_one(self, row, session):
        """Insert once; caller owns transaction and retry policy."""
        assert session == "caller-session"
        self.rows.append(deepcopy(row))

    def replace_one(self, query, row, session):
        """Simulate exact compare-and-set with matched_count."""
        assert session == "caller-session"
        for index, prior in enumerate(self.rows):
            if all(prior.get(key) == value for key, value in query.items()):
                self.rows[index] = deepcopy(row)
                return SimpleNamespace(matched_count=1)
        return SimpleNamespace(matched_count=0)


@pytest.fixture
def source():
    """Return isolated registry, current and audit fake collections."""
    current, events = Collection(), Collection()
    ProjectWorkPurposeRegistry.ensure_indexes(current, events)
    return ProjectWorkPurposeRegistry(current, events), current, events


def task(revision=3):
    """Use only source-owned task coordinates; never accept client tenant."""
    return SimpleNamespace(tenant_id=TENANT, project_id=PROJECT,
                           task_id=TASK, revision=revision)


def command(source, **overrides):
    """Submit one strictly scoped project-owner purpose classification."""
    registry = source[0]
    values = dict(task=task(), actor_principal_id=ACTOR,
                  audience="PLATFORM_BUILD", reason="Source owner verified engineering delivery.",
                  expected_task_revision=3, expected_purpose_revision=0,
                  idempotency_key="synthetic-command-1", session="caller-session", now=NOW)
    values.update(overrides)
    return registry.classify(**values)


def test_canonical_index_names_and_exact_scope(source):
    """Metadata DDL is explicitly caller-owned, not performed by reads."""
    _, current, events = source
    assert [x[1]["name"] for x in current.indexes] == ["wilsy_project_work_purpose_unique"]
    assert [x[1]["name"] for x in events.indexes] == [
        "wilsy_project_work_purpose_replay_unique",
        "wilsy_project_work_purpose_event_revision_unique",
    ]
    assert all(x[1]["unique"] for col in (current, events) for x in col.indexes)


def test_purpose_commit_readback_and_identical_replay(source):
    """Exact current task binds source-owned audit, digest and immutable event."""
    registry, current, events = source
    assert registry.current_for_task(task=task(), session="caller-session") is None
    initial = command(source)
    assert initial["revision"] == 1
    assert len(current.rows) == len(events.rows) == 1
    claim = registry.current_for_task(task=task(), session="caller-session")
    assert claim["audience"] == "PLATFORM_BUILD"
    assert claim["purpose_revision"] == 1
    assert claim["source_revision"] == 3
    assert claim["critical_gate"] is False
    assert claim["source_verified"] is True
    replay = command(source)
    assert replay["revision"] == initial["revision"] == 1
    assert replay["evidence_ref"] == initial["evidence_ref"]
    assert len(current.rows) == len(events.rows) == 1


def test_explicit_unclassification_is_audited_and_can_be_reclassified(source):
    """Clearing purpose is an explicit actor CAS event, not an invisible delete."""
    command(source)
    cleared = command(
        source, audience="UNCLASSIFIED",
        reason="Business purpose needs independent source review.",
        expected_purpose_revision=1, idempotency_key="synthetic-clear-2",
    )
    assert cleared["revision"] == 2
    claim = source[0].current_for_task(task=task(), session="caller-session")
    assert claim["audience"] == "UNCLASSIFIED"
    assert claim["purpose_revision"] == 2
    assert claim["evidence_ref"] is None
    assert len(source[1].rows) == 1
    assert len(source[2].rows) == 2
    classified = command(
        source, expected_purpose_revision=2,
        idempotency_key="synthetic-reclassify-3",
    )
    assert classified["revision"] == 3
    assert source[0].current_for_task(
        task=task(), session="caller-session",
    )["audience"] == "PLATFORM_BUILD"


def test_new_revision_and_stale_task_go_unclassified(source):
    """Current source category is not inherited across independent task edits."""
    command(source)
    second = command(source, audience="OPERATING",
                     reason="Source owner verified operating delivery.",
                     expected_purpose_revision=1, idempotency_key="synthetic-command-2")
    assert second["revision"] == 2
    assert source[0].current_for_task(task=task(), session="caller-session")["audience"] == "OPERATING"
    stale = source[0].current_for_task(task=task(4), session="caller-session")
    assert stale["audience"] == "UNCLASSIFIED"
    assert stale["purpose_revision"] == 2
    assert stale["evidence_ref"] is None
    assert len(source[2].rows) == 2
    recovered = command(source, task=task(4), expected_task_revision=4,
                        expected_purpose_revision=2,
                        idempotency_key="synthetic-command-3",
                        reason="Reclassified after exact task revision changed.")
    assert recovered["revision"] == 3
    assert source[0].current_for_task(task=task(4), session="caller-session")["audience"] == "PLATFORM_BUILD"


@pytest.mark.parametrize("overrides,expected", [
    ({"audience": "UNKNOWN"}, "PROJECT_WORK_PURPOSE_COMMAND_INVALID"),
    ({"reason": "short"}, "PROJECT_WORK_PURPOSE_COMMAND_INVALID"),
    ({"expected_task_revision": 4}, "PROJECT_WORK_PURPOSE_TASK_REVISION_CONFLICT"),
    ({"expected_purpose_revision": 1}, "PROJECT_WORK_PURPOSE_REVISION_CONFLICT"),
])
def test_invalid_or_stale_source_claims_do_not_write(source, overrides, expected):
    """Reject unknown categories and both independent revision conflicts."""
    with pytest.raises((WorkPurposeError, WorkPurposeConflict), match=expected):
        command(source, **overrides)
    assert source[1].rows == []
    assert source[2].rows == []


def test_511_source_items_read_in_bounded_batch_with_one_audit(source):
    """Source reading has no task-wise Mongo N+1; 511 is still complete."""
    command(source)
    all_tasks = [task()] + [
        SimpleNamespace(tenant_id=TENANT, project_id=PROJECT,
                        task_id="ptk-" + format(i + 1, "048x"), revision=1)
        for i in range(510)
    ]
    claims = source[0].current_for_tasks(tasks=all_tasks, session="caller-session")
    assert len(claims) == 511
    assert claims[TASK]["audience"] == "PLATFORM_BUILD"
    assert sum(value is None for value in claims.values()) == 510
    assert source[1].batch_reads == 3
    assert source[2].batch_reads == 1
    stale = source[0].current_for_tasks(tasks=[task(revision=4)], session="caller-session")
    assert stale[TASK]["audience"] == "UNCLASSIFIED"
    assert stale[TASK]["purpose_revision"] == 1


def test_batch_rejects_foreign_and_tampered_evidence(source):
    """Foreign source, missing audit and altered current digest fail closed."""
    command(source)
    with pytest.raises(WorkPurposeError, match="PROJECT_WORK_PURPOSE_BATCH_SCOPE_INVALID"):
        source[0].current_for_tasks(
            tasks=[task(), SimpleNamespace(tenant_id="foreign", project_id=PROJECT,
                                           task_id="ptk-" + "e" * 48, revision=1)],
            session="caller-session")
    source[2].rows.clear()
    with pytest.raises(WorkPurposeError, match="PROJECT_WORK_PURPOSE_AUDIT_INVALID"):
        source[0].current_for_tasks(tasks=[task()], session="caller-session")


def test_divergent_replay_and_missing_audit_are_denied(source):
    """Idempotency cannot rewrite classification or mint unobserved evidence."""
    command(source)
    with pytest.raises(WorkPurposeConflict, match="PROJECT_WORK_PURPOSE_REPLAY_CONFLICT"):
        command(source, audience="OPERATING")
    source[2].rows.clear()
    with pytest.raises(WorkPurposeError, match="PROJECT_WORK_PURPOSE_AUDIT_INVALID"):
        source[0].current_for_task(task=task(), session="caller-session")


@pytest.mark.parametrize("field,value", [
    ("actor_principal_id", "another-project-owner"),
    ("recorded_at", "2026-11-25T00:00:00+00:00"),
    ("event_type", "WORK_PURPOSE_UNRELATED"),
    ("request_fingerprint", "tampered"),
])
def test_immutable_audit_actor_or_event_drift_denied(source, field, value):
    """Event metadata is checked independently of current source fingerprint."""
    command(source)
    source[2].rows[0][field] = value
    with pytest.raises(WorkPurposeError, match="PROJECT_WORK_PURPOSE_AUDIT_INVALID"):
        source[0].current_for_task(task=task(), session="caller-session")
    with pytest.raises(WorkPurposeError, match="PROJECT_WORK_PURPOSE_AUDIT_INVALID"):
        source[0].current_for_tasks(tasks=[task()], session="caller-session")


def test_tampered_source_fingerprint_is_rejected(source):
    """Unverified current snapshot cannot be projected into My Work."""
    command(source)
    source[1].rows[0]["audience"] = "OPERATING"
    with pytest.raises(WorkPurposeError, match="PROJECT_WORK_PURPOSE_SOURCE_INVALID"):
        source[0].current_for_task(task=task(), session="caller-session")


# ARTIFACT: test_project_work_purpose_registry.py
# VERSION: v1.2.0-AUDITED-UNCLASSIFIED-REVERT-CERT
# AUTHORITY BOUNDARY: Synthetic source registry proof, no IAM.
# TENANT POSTURE: Strict coordinates and CAS, no cross-tenant read.
# FAIL-CLOSED POSTURE: Divergent replay/tampered evidence deny.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
