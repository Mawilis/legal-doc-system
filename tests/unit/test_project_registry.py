"""TITLE: WILSY OS tenant project registry tests
VERSION: v1.2.0-NOTE-REVISION-ISOLATION-CERT
AUTHORITY: Verification of tenant-scoped Projects persistence composition.
EPITOME: Exercises tenant predicates, idempotent commands, revisions,
         append-only events, archive filtering and Mongo index contracts.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_project_registry.py
COLLABORATION / OWNERSHIP: Python EOS ProjectRegistry and focused test suite.
CERTIFICATION / UPDATE DATE: 2026-11-17.
CHANGELOG:
v1.2.0-NOTE-REVISION-ISOLATION-CERT — Proves tenant-scoped notes
  creation, exact replay, author-only revisions, CAS conflicts, redaction
  and immutable event evidence with no IAM mutation.
v1.1.1-EXACT-ACTIVE-LIST-INDEX-CERT — Verifies exact compound
  active-list index keys, preserves project/event uniqueness guards and
  confirms the listing index is intentionally nonunique.
v1.1.0-LARGE-TENANT-SUMMARY-REGRESSION — Certifies 511 exact-tenant projects,
  fully counted portfolio truth and consecutive bounded list pages with
  foreign-tenant exclusion.
v1.0.2-BSON-UTC-EVENT-REGRESSION — Proves default PyMongo BSON UTC
  event readback and strict rejection of malformed event timestamps.
v1.0.1-TENANT-PROJECT-REGISTRY-TESTS — Governance metadata synchronized with unchanged executable behavior.
  v1.0.1 fixes the in-memory PyMongo cursor sort overload; assertions and
  production behavior remain unchanged.
  v1.0.0 establishes isolated in-memory registry regression coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic records and in-memory collections only.
TENANT BOUNDARY: Every registry operation is asserted against exact tenant scope.
AUTHORITY BOUNDARY: Persistence tests do not issue IAM grants.
FINANCIAL AUTHORITY BOUNDARY: No financial execution behavior is represented.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

import pytest

from tools.eos.saas.domain.project import Project, ProjectStatus
from tools.eos.saas.projects.project_registry import (
    ProjectNotFound, ProjectRegistry, ProjectRegistryConflict, ProjectRegistryError,
)
from tools.eos.saas.projects.project_notes_registry import (
    ProjectNotesRegistry, ProjectNoteConflict, ProjectNoteNotFound,
)

NOW = datetime(2026, 11, 16, 12, 0, tzinfo=timezone.utc)


class FakeCursor:
    """Minimal deterministic cursor implementing the used PyMongo overloads."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def sort(self, fields: Any, direction: int | None = None) -> FakeCursor:
        if isinstance(fields, str):
            fields = [(fields, direction or 1)]
        for field, order in reversed(fields):
            self.rows.sort(key=lambda row: str(row.get(field, "")), reverse=order < 0)
        return self

    def skip(self, amount: int) -> FakeCursor:
        self.rows = self.rows[amount:]
        return self

    def limit(self, amount: int) -> FakeCursor:
        self.rows = self.rows[:amount]
        return self

    def __iter__(self):
        return iter(self.rows)


class FakeCollection:
    """In-memory collection recording query scope and write arguments."""

    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.indexes: list[tuple[tuple[Any, ...], dict[str, Any]]] = []
        self.last_query: dict[str, object] | None = None
        self.last_session: object | None = None

    def create_index(self, keys: Any, **options: Any) -> str:
        self.indexes.append((tuple(keys), options))
        return str(options.get("name"))

    def find_one(self, query: dict[str, object], *, session: object) -> dict[str, Any] | None:
        self.last_query, self.last_session = query, session
        return next((row.copy() for row in self.rows if _matches(row, query)), None)

    def find(self, query: dict[str, object], *, session: object) -> FakeCursor:
        self.last_query, self.last_session = query, session
        return FakeCursor([row.copy() for row in self.rows if _matches(row, query)])

    def insert_one(self, document: dict[str, object], *, session: object) -> None:
        self.last_session = session
        self.rows.append(dict(document))

    def update_one(self, query: dict[str, object], update: dict[str, Any], *, session: object) -> Any:
        self.last_query, self.last_session = query, session
        for row in self.rows:
            if _matches(row, query):
                row.update(update["$set"])
                return type("UpdateResult", (), {"matched_count": 1})()
        return type("UpdateResult", (), {"matched_count": 0})()


def _matches(row: dict[str, Any], query: dict[str, object]) -> bool:
    return all(row.get(key) == value for key, value in query.items())


def _project(tenant: str = "tenant-a", project_id: str = "project-001", **changes: object) -> Project:
    values: dict[str, object] = {
        "tenant_id": tenant, "project_id": project_id, "name": "Delivery workstream",
        "code": "DEL-001", "summary": "Bounded project summary.",
        "status": ProjectStatus.PLANNED, "owner_principal_id": None, "department_id": None,
        "start_date": date(2026, 11, 1), "target_date": date(2026, 12, 1),
        "source_type": "internal", "external_source_reference": None,
        "created_by_principal_id": "principal-a", "created_at": NOW,
        "updated_by_principal_id": "principal-a", "updated_at": NOW,
    }
    values.update(changes)
    return Project(**values)  # type: ignore[arg-type]


@pytest.fixture
def registry() -> tuple[ProjectRegistry, FakeCollection, FakeCollection, object]:
    projects, events, session = FakeCollection(), FakeCollection(), object()
    return ProjectRegistry(projects, events), projects, events, session


def _create(store: ProjectRegistry, value: Project, session: object, key: str) -> Project:
    return store.create_or_replay(
        project=value, actor_principal_id=value.created_by_principal_id,
        idempotency_key=key, occurred_at=NOW, session=session,
    )


def test_create_replay_is_exact_and_persists_immutable_event(registry) -> None:
    store, projects, events, session = registry
    value = _project()
    assert _create(store, value, session, "create-1") == value
    assert _create(store, value, session, "create-1") == value
    assert len(projects.rows) == len(events.rows) == 1
    assert events.rows[0]["actor_principal_id"] == "principal-a"
    assert events.rows[0]["event_type"] == "PROJECT_CREATED"
    assert events.rows[0]["result_snapshot"]["tenant_id"] == "tenant-a"
    assert events.last_session is session


def test_same_idempotency_key_with_different_payload_conflicts(registry) -> None:
    store, _, _, session = registry
    _create(store, _project(), session, "create-1")
    with pytest.raises(ProjectRegistryConflict, match="DIVERGENT_REPLAY"):
        _create(store, _project(name="Different project"), session, "create-1")


def test_get_and_list_are_exact_tenant_scoped(registry) -> None:
    store, projects, _, session = registry
    _create(store, _project("tenant-a", "project-a"), session, "create-a")
    _create(store, _project("tenant-b", "project-b", code="DEL-002"), session, "create-b")
    assert [item.project_id for item in store.list_for_tenant(tenant_id="tenant-a", session=session)] == ["project-a"]
    assert projects.last_query == {"tenant_id": "tenant-a", "archived_at": None}
    with pytest.raises(ProjectNotFound, match="PROJECT_NOT_FOUND"):
        store.get(tenant_id="tenant-a", project_id="project-b", session=session)
    assert projects.last_query == {
        "tenant_id": "tenant-a", "project_id": "project-b", "archived_at": None,
    }


def test_update_and_transition_advance_revision_and_audit(registry) -> None:
    store, projects, events, session = registry
    _create(store, _project(), session, "create-1")
    revised = store.update(
        tenant_id="tenant-a", project_id="project-001", actor_principal_id="principal-a",
        expected_revision=1, changes={"summary": "Updated"}, idempotency_key="update-1",
        occurred_at=NOW + timedelta(seconds=1), session=session,
    )
    active = store.transition(
        tenant_id="tenant-a", project_id="project-001", actor_principal_id="principal-a",
        expected_revision=2, resulting_status=ProjectStatus.ACTIVE,
        idempotency_key="transition-1", occurred_at=NOW + timedelta(seconds=2), session=session,
    )
    assert revised.revision == 2 and revised.summary == "Updated"
    assert active.revision == 3 and active.status is ProjectStatus.ACTIVE
    assert projects.rows[0]["revision"] == 3
    assert [event["revision"] for event in events.rows] == [1, 2, 3]
    assert [event["actor_principal_id"] for event in events.rows] == ["principal-a"] * 3


def test_stale_revision_fails_closed(registry) -> None:
    store, _, _, session = registry
    _create(store, _project(), session, "create-1")
    store.update(
        tenant_id="tenant-a", project_id="project-001", actor_principal_id="principal-a",
        expected_revision=1, changes={"summary": "Updated"}, idempotency_key="update-1",
        occurred_at=NOW + timedelta(seconds=1), session=session,
    )
    with pytest.raises(ProjectRegistryConflict, match="PROJECT_REVISION_CONFLICT"):
        store.update(
            tenant_id="tenant-a", project_id="project-001", actor_principal_id="principal-a",
            expected_revision=1, changes={"name": "Stale"}, idempotency_key="update-2",
            occurred_at=NOW + timedelta(seconds=2), session=session,
        )


def test_archive_is_soft_excluded_from_default_list_and_summary(registry) -> None:
    store, projects, _, session = registry
    _create(store, _project(), session, "create-1")
    archived = store.archive(
        tenant_id="tenant-a", project_id="project-001", actor_principal_id="principal-a",
        expected_revision=1, idempotency_key="archive-1",
        occurred_at=NOW + timedelta(seconds=1), session=session,
    )
    assert archived.archived_at == NOW + timedelta(seconds=1)
    assert store.list_for_tenant(tenant_id="tenant-a", session=session) == ()
    assert store.summary_for_tenant(tenant_id="tenant-a", session=session)["total"] == 0
    assert store.get(tenant_id="tenant-a", project_id="project-001", session=session,
                     include_archived=True) == archived
    assert projects.rows[0]["archived_at"] is not None


def test_summary_and_status_filter_use_authoritative_tenant_records(registry) -> None:
    store, _, _, session = registry
    _create(store, _project("tenant-a", "p1"), session, "c1")
    _create(store, _project("tenant-a", "p2", status=ProjectStatus.ACTIVE, code="DEL-002"), session, "c2")
    _create(store, _project("tenant-b", "p3", code="DEL-003"), session, "c3")
    assert store.summary_for_tenant(tenant_id="tenant-a", session=session) == {
        "total": 2, "active": 1, "planned": 1, "on_hold": 0, "done": 0, "cancelled": 0,
    }
    assert len(store.list_for_tenant(tenant_id="tenant-a", session=session, status="active")) == 1



def test_large_tenant_summary_and_bounded_pages_over_500(registry) -> None:
    """No cap may turn an ordinary >500-project tenant into an unavailable portfolio."""
    store, projects, _, session = registry
    projects.rows.extend([
        {"_id": f"tenant-a:project-{i:04}", **_project(
            "tenant-a", f"project-{i:04}", code=f"CODE-{i:04}",
        ).to_dict()}
        for i in range(511)
    ])
    projects.rows.append({"_id": "tenant-b:foreign", **_project(
        "tenant-b", "foreign", code="FOREIGN",
    ).to_dict()})

    counts = store.summary_for_tenant(tenant_id="tenant-a", session=session)
    assert counts == {
        "total": 511, "active": 0, "planned": 511,
        "on_hold": 0, "done": 0, "cancelled": 0,
    }
    assert projects.last_query == {"tenant_id": "tenant-a", "archived_at": None}
    first = store.list_for_tenant(tenant_id="tenant-a", session=session, limit=500)
    last = store.list_for_tenant(tenant_id="tenant-a", session=session, limit=500, offset=500)
    assert len(first) == 500 and len(last) == 11
    assert {p.project_id for p in first}.isdisjoint({p.project_id for p in last})
    assert all(p.tenant_id == "tenant-a" for p in (*first, *last))




def test_project_notes_create_revise_redact_replay_and_tenant_isolation() -> None:
    """Author-only CAS notes retain immutable revisions without any IAM grants."""
    notes, events, session = FakeCollection(), FakeCollection(), object()
    ProjectNotesRegistry.ensure_indexes(notes, events)
    source = ProjectNotesRegistry(notes, events)
    command = dict(
        tenant_id="tenant-a", project_id="project-a",
        actor_principal_id="principal-a",
    )
    created = source.create(
        **command, body="Foundation note", idempotency_key="note-create",
        occurred_at=NOW, session=session,
    )
    assert created["revision"] == 1
    assert created["body"] == "Foundation note"
    assert source.create(
        **command, body="Foundation note", idempotency_key="note-create",
        occurred_at=NOW + timedelta(seconds=1), session=session,
    ) == created
    assert len(notes.rows) == len(events.rows) == 1
    with pytest.raises(ProjectNoteConflict, match="DIVERGENT_REPLAY"):
        source.create(
            **command, body="Other content", idempotency_key="note-create",
            occurred_at=NOW, session=session,
        )
    assert len(source.list_for_project(
        tenant_id="tenant-a", project_id="project-a", session=session,
    )) == 1
    assert source.list_for_project(
        tenant_id="tenant-b", project_id="project-a", session=session,
    ) == ()
    with pytest.raises(ProjectNoteNotFound):
        source.get(
            tenant_id="tenant-b", project_id="project-a",
            note_id=created["note_id"], session=session,
        )
    with pytest.raises(ProjectNoteConflict, match="AUTHOR_REQUIRED"):
        source.revise(
            tenant_id="tenant-a", project_id="project-a",
            note_id=created["note_id"], actor_principal_id="principal-b",
            expected_revision=1, body="Forbidden", redact=False,
            idempotency_key="foreign-revision", occurred_at=NOW + timedelta(seconds=1),
            session=session,
        )
    revised = source.revise(
        **command, note_id=created["note_id"], expected_revision=1,
        body="Revised with evidence", redact=False,
        idempotency_key="note-revise", occurred_at=NOW + timedelta(seconds=2),
        session=session,
    )
    assert revised["revision"] == 2
    assert revised["body"] == "Revised with evidence"
    assert source.revise(
        **command, note_id=created["note_id"], expected_revision=1,
        body="Revised with evidence", redact=False,
        idempotency_key="note-revise", occurred_at=NOW + timedelta(seconds=2),
        session=session,
    ) == revised
    with pytest.raises(ProjectNoteConflict, match="REVISION_CONFLICT"):
        source.revise(
            **command, note_id=created["note_id"], expected_revision=1,
            body="Old edit", redact=False, idempotency_key="note-stale",
            occurred_at=NOW + timedelta(seconds=3), session=session,
        )
    redacted = source.revise(
        **command, note_id=created["note_id"], expected_revision=2,
        body=None, redact=True, idempotency_key="note-redact",
        occurred_at=NOW + timedelta(seconds=4), session=session,
    )
    assert redacted["revision"] == 3
    assert redacted["body"] == "" and redacted["redacted_at"] is not None
    assert len(events.rows) == 3
    assert [event["event_type"] for event in events.rows] == [
        "PROJECT_NOTE_CREATED", "PROJECT_NOTE_REVISED", "PROJECT_NOTE_REDACTED",
    ]



def test_event_read_is_tenant_scoped_and_returns_documented_fields(registry) -> None:
    store, _, events, session = registry
    _create(store, _project(), session, "create-1")
    result = store.list_events(tenant_id="tenant-a", project_id="project-001", session=session)
    assert len(result) == 1
    assert result[0]["event_type"] == "PROJECT_CREATED"
    assert events.last_query == {"tenant_id": "tenant-a", "project_id": "project-001"}


def test_event_readback_accepts_pymongo_default_naive_bson_utc(registry) -> None:
    """Mongo BSON UTC decoded with tz_aware=False must remain valid evidence."""
    store, _, events, session = registry
    _create(store, _project(), session, "create-1")
    # Mimic PyMongo's default BSON datetime decoder, not caller command input.
    events.rows[0]["occurred_at"] = NOW.replace(tzinfo=None)
    result = store.list_events(tenant_id="tenant-a", project_id="project-001", session=session)
    assert len(result) == 1
    assert result[0]["occurred_at"] == NOW
    assert result[0]["occurred_at"].tzinfo is timezone.utc
    # The stored record itself remains immutable.
    assert events.rows[0]["occurred_at"].tzinfo is None


@pytest.mark.parametrize("bad", [None, "2026-11-16T12:00:00Z", 42])
def test_event_readback_rejects_malformed_timestamp(registry, bad) -> None:
    store, _, events, session = registry
    _create(store, _project(), session, "create-1")
    events.rows[0]["occurred_at"] = bad
    with pytest.raises(ProjectRegistryError, match="PROJECT_EVENT_TIMESTAMP_INVALID"):
        store.list_events(tenant_id="tenant-a", project_id="project-001", session=session)


def test_missing_transaction_session_is_rejected(registry) -> None:
    store, _, _, _ = registry
    with pytest.raises(ProjectRegistryError, match="SESSION_REQUIRED"):
        store.list_for_tenant(tenant_id="tenant-a", session=None)


def test_indexes_are_tenant_scoped_and_unique(registry) -> None:
    _, projects, events, _ = registry
    ProjectRegistry.ensure_indexes(projects, events)
    assert [opts["name"] for _, opts in projects.indexes] == [
        "wilsy_project_tenant_identity_unique", "wilsy_project_tenant_code_unique",
        "wilsy_project_tenant_active_recent",
    ]
    active_keys, active_opts = projects.indexes[2]
    assert active_keys == (
        ("tenant_id", 1), ("archived_at", 1), ("updated_at", -1), ("project_id", 1),
    )
    assert "unique" not in active_opts
    assert [opts["name"] for _, opts in events.indexes] == [
        "wilsy_project_event_tenant_identity_unique",
        "wilsy_project_event_tenant_idempotency_unique",
        "wilsy_project_event_tenant_project_revision_unique",
    ]
    assert all(opts["unique"] for _, opts in projects.indexes[:2] + events.indexes)


# ARTIFACT: test_project_registry.py
# VERSION: v1.2.0-NOTE-REVISION-ISOLATION-CERT
# AUTHORITY BOUNDARY: registry unit tests; no IAM or external database authority
# TENANT POSTURE: synthetic in-memory exact-tenant fixtures
# FAIL-CLOSED POSTURE: all tenant, replay, revision, event and index assertions are required
# FINANCIAL EXECUTION AUTHORITY: none
# END OF WILSY OS SOVEREIGN ARTIFACT
