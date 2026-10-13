"""Direct certificate for W3B workforce relationship registry."""

from datetime import datetime, timezone
from pathlib import Path

import pytest

from tools.eos.workforce.domain.workforce_relationship import (
    WorkforceRelationship,
    WorkforceRelationshipStatus,
    WorkforceRelationshipType,
    WorkforceScopeKind,
)
from tools.eos.workforce.registry import (
    workforce_relationship_registry as registry,
)


AT = datetime(
    2026,
    10,
    13,
    6,
    0,
    tzinfo=timezone.utc,
)


class FakeSession:
    def __init__(
        self,
        active: bool = True,
    ) -> None:
        self.in_transaction = active


class Result:
    def __init__(self) -> None:
        self.inserted_id = "id"


class Cursor:
    def __init__(self, rows):
        self.rows = list(rows)

    def sort(self, *args):
        if (
            len(args) == 2
            and args[0] == "revision"
        ):
            self.rows.sort(
                key=lambda row: row["revision"]
            )

        elif (
            len(args) == 1
            and isinstance(args[0], list)
        ):
            keys = [
                value[0]
                for value in args[0]
            ]
            self.rows.sort(
                key=lambda row: tuple(
                    row[key]
                    for key in keys
                )
            )

        return self

    def __iter__(self):
        return iter(self.rows)


class FakeCollection:
    def __init__(self) -> None:
        self.rows = []
        self.indexes = []

    def create_index(
        self,
        keys,
        unique=False,
        name=None,
    ):
        self.indexes.append(
            (tuple(keys), unique, name)
        )
        return name

    def find_one(
        self,
        query,
        session=None,
    ):
        for row in self.rows:
            if all(
                row.get(key) == value
                for key, value in query.items()
            ):
                return dict(row)

        return None

    def find(
        self,
        query,
        session=None,
    ):
        rows = [
            dict(row)
            for row in self.rows
            if all(
                row.get(key) == value
                for key, value in query.items()
            )
        ]
        return Cursor(rows)

    def insert_one(
        self,
        document,
        session=None,
    ):
        identity = (
            document["scope_kind"],
            document["scope_id"],
            document["relationship_id"],
            document["revision"],
        )

        for row in self.rows:
            other = (
                row["scope_kind"],
                row["scope_id"],
                row["relationship_id"],
                row["revision"],
            )

            if identity == other:
                from pymongo.errors import DuplicateKeyError
                raise DuplicateKeyError("duplicate")

        self.rows.append(dict(document))
        return Result()


def relationship(
    revision: int = 1,
    *,
    previous=None,
    status=WorkforceRelationshipStatus.ACTIVE,
) -> WorkforceRelationship:
    return WorkforceRelationship(
        relationship_id="rel-001",
        revision=revision,
        scope_kind=WorkforceScopeKind.TENANT,
        scope_id="tenant-001",
        principal_id="principal-001",
        relationship_type=(
            WorkforceRelationshipType.EMPLOYEE
        ),
        status=status,
        effective_from=AT,
        effective_until=None,
        status_effective_at=AT,
        reason_reference=f"evidence-{revision}",
        supersedes_fingerprint=(
            None
            if previous is None
            else previous.fingerprint
        ),
    )


def test_indexes_are_non_ttl_and_exact() -> None:
    collection = FakeCollection()

    registry.ensure_indexes(
        collection
    )

    names = {
        value[2]
        for value in collection.indexes
    }

    assert names == {
        registry.REVISION_INDEX_NAME,
        registry.FINGERPRINT_INDEX_NAME,
        registry.PRINCIPAL_INDEX_NAME,
    }

    assert all(
        "expireAfterSeconds"
        not in repr(value)
        for value in collection.indexes
    )


def test_active_transaction_is_required() -> None:
    with pytest.raises(
        registry.WorkforceRelationshipRegistryTransactionRequiredError
    ):
        registry.persist_revision(
            relationship(),
            collection=FakeCollection(),
            session=FakeSession(False),
        )


def test_create_and_exact_replay() -> None:
    collection = FakeCollection()
    session = FakeSession()

    value = relationship()

    first = registry.persist_revision(
        value,
        collection=collection,
        session=session,
    )
    second = registry.persist_revision(
        value,
        collection=collection,
        session=session,
    )

    assert first == value
    assert second == value
    assert len(collection.rows) == 1


def test_divergent_same_revision_rejects() -> None:
    collection = FakeCollection()
    session = FakeSession()

    value = relationship()

    registry.persist_revision(
        value,
        collection=collection,
        session=session,
    )

    divergent = WorkforceRelationship(
        relationship_id=value.relationship_id,
        revision=1,
        scope_kind=value.scope_kind,
        scope_id=value.scope_id,
        principal_id=value.principal_id,
        relationship_type=(
            WorkforceRelationshipType.CONTRACTOR
        ),
        status=value.status,
        effective_from=value.effective_from,
        effective_until=None,
        status_effective_at=value.status_effective_at,
        reason_reference="different",
        supersedes_fingerprint=None,
    )

    with pytest.raises(
        registry.WorkforceRelationshipRegistryConflictError,
        match="DIVERGENT_REPLAY",
    ):
        registry.persist_revision(
            divergent,
            collection=collection,
            session=session,
        )


def test_next_revision_requires_predecessor() -> None:
    with pytest.raises(
        registry.WorkforceRelationshipRegistryConflictError,
        match="PREDECESSOR_REQUIRED",
    ):
        registry.persist_revision(
            WorkforceRelationship(
                relationship_id="rel-001",
                revision=2,
                scope_kind=WorkforceScopeKind.TENANT,
                scope_id="tenant-001",
                principal_id="principal-001",
                relationship_type=(
                    WorkforceRelationshipType.EMPLOYEE
                ),
                status=(
                    WorkforceRelationshipStatus.SUSPENDED
                ),
                effective_from=AT,
                effective_until=None,
                status_effective_at=AT,
                reason_reference="evidence-2",
                supersedes_fingerprint="a" * 128,
            ),
            collection=FakeCollection(),
            session=FakeSession(),
        )


def test_history_is_ordered_and_contiguous() -> None:
    collection = FakeCollection()
    session = FakeSession()

    first = relationship()

    registry.persist_revision(
        first,
        collection=collection,
        session=session,
    )

    second = relationship(
        2,
        previous=first,
        status=WorkforceRelationshipStatus.SUSPENDED,
    )

    registry.persist_revision(
        second,
        collection=collection,
        session=session,
    )

    values = registry.list_history(
        "TENANT",
        "tenant-001",
        "rel-001",
        collection=collection,
        session=session,
    )

    assert values == (
        first,
        second,
    )


def test_next_revision_cannot_change_effective_start() -> None:
    collection = FakeCollection()
    session = FakeSession()

    first = relationship()

    registry.persist_revision(
        first,
        collection=collection,
        session=session,
    )

    changed = WorkforceRelationship(
        relationship_id=first.relationship_id,
        revision=2,
        scope_kind=first.scope_kind,
        scope_id=first.scope_id,
        principal_id=first.principal_id,
        relationship_type=first.relationship_type,
        status=WorkforceRelationshipStatus.SUSPENDED,
        effective_from=AT.replace(hour=7),
        effective_until=None,
        status_effective_at=AT.replace(hour=7),
        reason_reference="changed-start",
        supersedes_fingerprint=first.fingerprint,
    )

    with pytest.raises(
        registry.WorkforceRelationshipRegistryConflictError,
        match="EFFECTIVE_FROM_CHANGED",
    ):
        registry.persist_revision(
            changed,
            collection=collection,
            session=session,
        )


def test_next_revision_cannot_regress_status_time() -> None:
    collection = FakeCollection()
    session = FakeSession()

    first = WorkforceRelationship(
        relationship_id="time-rel",
        revision=1,
        scope_kind=WorkforceScopeKind.TENANT,
        scope_id="tenant-001",
        principal_id="principal-001",
        relationship_type=(
            WorkforceRelationshipType.EMPLOYEE
        ),
        status=WorkforceRelationshipStatus.ACTIVE,
        effective_from=AT,
        effective_until=None,
        status_effective_at=AT.replace(hour=7),
        reason_reference="time-1",
        supersedes_fingerprint=None,
    )

    registry.persist_revision(
        first,
        collection=collection,
        session=session,
    )

    regressed = WorkforceRelationship(
        relationship_id=first.relationship_id,
        revision=2,
        scope_kind=first.scope_kind,
        scope_id=first.scope_id,
        principal_id=first.principal_id,
        relationship_type=first.relationship_type,
        status=WorkforceRelationshipStatus.SUSPENDED,
        effective_from=AT,
        effective_until=None,
        status_effective_at=AT.replace(hour=6, minute=30),
        reason_reference="time-regression",
        supersedes_fingerprint=first.fingerprint,
    )

    with pytest.raises(
        registry.WorkforceRelationshipRegistryConflictError,
        match="STATUS_TIME_REGRESSION",
    ):
        registry.persist_revision(
            regressed,
            collection=collection,
            session=session,
        )


def test_ended_relationship_cannot_be_resurrected() -> None:
    collection = FakeCollection()
    session = FakeSession()

    first = relationship()

    registry.persist_revision(
        first,
        collection=collection,
        session=session,
    )

    ended = relationship(
        2,
        previous=first,
        status=WorkforceRelationshipStatus.ENDED,
    )

    registry.persist_revision(
        ended,
        collection=collection,
        session=session,
    )

    resurrection = relationship(
        3,
        previous=ended,
        status=WorkforceRelationshipStatus.ACTIVE,
    )

    with pytest.raises(
        registry.WorkforceRelationshipRegistryConflictError,
        match="ENDED_RELATIONSHIP_TERMINAL",
    ):
        registry.persist_revision(
            resurrection,
            collection=collection,
            session=session,
        )


def test_registry_exposes_no_update_delete_api() -> None:
    assert not hasattr(
        registry,
        "update_relation",
    )
    assert not hasattr(
        registry,
        "delete_relation",
    )


def test_registry_source_contains_no_iam_authority() -> None:
    source = Path(
        "tools/eos/workforce/registry/"
        "workforce_relationship_registry.py"
    ).read_text()

    assert "authorize_tenant_operation(" not in source
    assert "revoke_sessions(" not in source
    assert "financial_execution(" not in source
