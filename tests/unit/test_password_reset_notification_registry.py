"""Direct certificate for the WILSY OS reset-notification registry.

TITLE: WILSY OS Password Reset Notification Registry Direct Certificate
VERSION: v1.0.0-R10G4-PASSWORD-RESET-NOTIFICATION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies tenant-scoped, secret-free notification persistence,
         caller-session propagation, retryable failure CAS, terminal SENT CAS,
         corruption rejection, replay conflicts, and stable persistence errors.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_reset_notification_registry.py
COLLABORATION / OWNERSHIP: Exercises password_reset_notification_registry.py
                           against one deterministic PyMongo-shaped fake only.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10G4-PASSWORD-RESET-NOTIFICATION-REGISTRY-CERT — Adds direct
           evidence for exact indexes, pristine insert-only creation, tenant
           isolation, exact reads, session forwarding, failed-attempt updates,
           terminal SENT evidence, stale/replay rejection, corruption handling,
           and database-failure mapping.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic identifiers/timestamps only; no address,
                            password, token, digest, JWT, SMTP, or message body.
TENANT BOUNDARY: Every tested read/mutation remains exactly tenant-scoped.
AUTHORITY BOUNDARY: Persistence test evidence only; no reset/delivery authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.auth.password_reset_notification import (
    PasswordResetNotification,
    PasswordResetNotificationStatus,
)
from tools.eos.saas.auth.password_reset_notification_registry import (
    PasswordResetNotificationAlreadyExistsError,
    PasswordResetNotificationLifecycleConflictError,
    PasswordResetNotificationNotFoundError,
    PasswordResetNotificationPersistedRecordInvalidError,
    PasswordResetNotificationPersistenceError,
    PasswordResetNotificationRegistry,
    PasswordResetNotificationRegistryError,
)

TENANT = "WILSY-TENANT-R10G-REGISTRY"
PRINCIPAL = "WILSY-PRINCIPAL-R10G-REGISTRY"
NOTICE_ID = "WILSYRESETNOTICE-R10G-REGISTRY"
OCCURRED = datetime(2026, 9, 22, 20, 30, tzinfo=timezone.utc)


def _notice(
    *,
    notification_id: str = NOTICE_ID,
    tenant_id: str = TENANT,
    principal_id: str = PRINCIPAL,
) -> PasswordResetNotification:
    return PasswordResetNotification.issue(
        notification_id=notification_id,
        tenant_id=tenant_id,
        principal_id=principal_id,
        occurred_at=OCCURRED,
    )


class _FakeCollection:
    """Deterministic collection implementing only the registry-used surface."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, object]]] = []
        self.calls: list[tuple[str, object | None]] = []
        self.fail_indexes = False
        self.fail_insert = False
        self.fail_read = False
        self.fail_update = False

    def create_index(self, keys, **kwargs):
        if self.fail_indexes:
            raise PyMongoError("index failure")
        self.indexes.append((list(keys), dict(kwargs)))
        return kwargs.get("name")

    @staticmethod
    def _matches(row: dict[str, object], query: dict[str, object]) -> bool:
        return all(row.get(key) == value for key, value in query.items())

    def insert_one(self, document, **kwargs):
        if self.fail_insert:
            raise PyMongoError("insert failure")
        self.calls.append(("insert", kwargs.get("session")))
        incoming = deepcopy(document)
        if any(row.get("notification_id") == incoming.get("notification_id") for row in self.rows):
            raise DuplicateKeyError("duplicate")
        self.rows.append(incoming)
        return object()

    def find_one(self, query, **kwargs):
        if self.fail_read:
            raise PyMongoError("read failure")
        self.calls.append(("find_one", kwargs.get("session")))
        for row in self.rows:
            if self._matches(row, query):
                return deepcopy(row)
        return None

    def find_one_and_update(self, query, update, *, return_document=None, **kwargs):
        del return_document
        if self.fail_update:
            raise PyMongoError("update failure")
        self.calls.append(("update", kwargs.get("session")))
        for row in self.rows:
            if self._matches(row, query):
                row.update(deepcopy(update.get("$set", {})))
                return deepcopy(row)
        return None


def test_indexes_are_exact_and_secret_free() -> None:
    collection = _FakeCollection()
    PasswordResetNotificationRegistry(collection).ensure_indexes()

    assert [options["name"] for _, options in collection.indexes] == [
        "password_reset_notification_identity_unique",
        "password_reset_notification_tenant_principal_status",
        "password_reset_notification_tenant_delivery_queue",
    ]
    assert collection.indexes[0][1]["unique"] is True
    assert collection.indexes[1][1]["unique"] is False
    assert collection.indexes[2][1]["unique"] is False

    indexed_fields = {
        field
        for keys, _ in collection.indexes
        for field, _direction in keys
    }
    assert {"email", "address", "password", "token", "digest"}.isdisjoint(indexed_fields)


def test_create_persists_only_pristine_pending_and_forwards_session() -> None:
    collection = _FakeCollection()
    registry = PasswordResetNotificationRegistry(collection)
    session = object()
    notice = _notice()

    assert registry.create(notice, session=session) is notice
    assert collection.calls[-1] == ("insert", session)
    assert len(collection.rows) == 1

    row = collection.rows[0]
    assert row["tenant_id"] == TENANT
    assert row["principal_id"] == PRINCIPAL
    assert row["status"] == "PENDING"
    assert row["attempt_count"] == 0
    assert row["last_attempt_at"] is None
    assert row["delivered_at"] is None
    assert {"email", "address", "password", "token", "digest"}.isdisjoint(row)


def test_create_rejects_non_pristine_state_and_duplicate_identity() -> None:
    collection = _FakeCollection()
    registry = PasswordResetNotificationRegistry(collection)
    notice = _notice()
    registry.create(notice)

    with pytest.raises(PasswordResetNotificationAlreadyExistsError) as duplicate:
        registry.create(notice)
    assert duplicate.value.code == "PASSWORD_RESET_NOTIFICATION_DUPLICATE"

    dirty = _notice(notification_id="WILSYRESETNOTICE-DIRTY").record_failure(
        OCCURRED + timedelta(seconds=1)
    )
    with pytest.raises(PasswordResetNotificationRegistryError) as invalid:
        registry.create(dirty)
    assert invalid.value.code == "PASSWORD_RESET_NOTIFICATION_CREATE_REQUIRES_PRISTINE_PENDING"


def test_get_is_exactly_tenant_scoped_and_forwards_session() -> None:
    collection = _FakeCollection()
    registry = PasswordResetNotificationRegistry(collection)
    session = object()
    notice = _notice()
    registry.create(notice, session=session)

    assert registry.get(
        tenant_id=TENANT,
        notification_id=NOTICE_ID,
        session=session,
    ) == notice
    assert registry.get(
        tenant_id="OTHER-TENANT",
        notification_id=NOTICE_ID,
        session=session,
    ) is None

    with pytest.raises(PasswordResetNotificationNotFoundError) as captured:
        registry.get(tenant_id=" bad", notification_id=NOTICE_ID)
    assert captured.value.code == "PASSWORD_RESET_NOTIFICATION_NOT_FOUND"


def test_record_failure_is_exact_cas_retryable_and_session_bound() -> None:
    collection = _FakeCollection()
    registry = PasswordResetNotificationRegistry(collection)
    session = object()
    notice = _notice()
    registry.create(notice, session=session)

    attempted_at = OCCURRED + timedelta(minutes=1)
    failed = registry.record_failure(notice, attempted_at, session=session)

    assert failed.status is PasswordResetNotificationStatus.PENDING
    assert failed.attempt_count == 1
    assert failed.last_attempt_at == attempted_at
    assert failed.delivered_at is None
    assert collection.calls[-1] == ("update", session)

    second = registry.record_failure(
        failed,
        OCCURRED + timedelta(minutes=2),
        session=session,
    )
    assert second.attempt_count == 2


def test_mark_sent_is_terminal_exact_cas_and_replay_rejects() -> None:
    collection = _FakeCollection()
    registry = PasswordResetNotificationRegistry(collection)
    notice = _notice()
    registry.create(notice)

    sent_at = OCCURRED + timedelta(minutes=1)
    sent = registry.mark_sent(notice, sent_at)

    assert sent.status is PasswordResetNotificationStatus.SENT
    assert sent.attempt_count == 1
    assert sent.last_attempt_at == sent_at
    assert sent.delivered_at == sent_at

    with pytest.raises(PasswordResetNotificationLifecycleConflictError) as captured:
        registry.mark_sent(notice, sent_at + timedelta(minutes=1))
    assert captured.value.code == "PASSWORD_RESET_NOTIFICATION_ALREADY_SENT"


def test_stale_failure_cas_is_conflict_not_replay_success() -> None:
    collection = _FakeCollection()
    registry = PasswordResetNotificationRegistry(collection)
    notice = _notice()
    registry.create(notice)
    first = registry.record_failure(notice, OCCURRED + timedelta(minutes=1))

    with pytest.raises(PasswordResetNotificationLifecycleConflictError) as captured:
        registry.record_failure(notice, OCCURRED + timedelta(minutes=2))
    assert captured.value.code == "PASSWORD_RESET_NOTIFICATION_LIFECYCLE_CONFLICT"

    second = registry.record_failure(first, OCCURRED + timedelta(minutes=2))
    assert second.attempt_count == 2


def test_cross_tenant_stale_transition_reports_not_found() -> None:
    collection = _FakeCollection()
    registry = PasswordResetNotificationRegistry(collection)
    notice = _notice()
    registry.create(notice)

    other_tenant_notice = _notice(tenant_id="OTHER-TENANT")
    with pytest.raises(PasswordResetNotificationNotFoundError) as captured:
        registry.mark_sent(other_tenant_notice, OCCURRED + timedelta(minutes=1))
    assert captured.value.code == "PASSWORD_RESET_NOTIFICATION_NOT_FOUND"


def test_corrupt_persisted_state_is_rejected() -> None:
    collection = _FakeCollection()
    row = _notice().to_document()
    row["schema"] = "CORRUPT"
    collection.rows.append(row)

    with pytest.raises(PasswordResetNotificationPersistedRecordInvalidError) as captured:
        PasswordResetNotificationRegistry(collection).get(
            tenant_id=TENANT,
            notification_id=NOTICE_ID,
        )
    assert captured.value.code == "PASSWORD_RESET_NOTIFICATION_PERSISTED_RECORD_INVALID"


def test_session_is_forwarded_across_create_read_and_transitions() -> None:
    collection = _FakeCollection()
    registry = PasswordResetNotificationRegistry(collection)
    session = object()
    notice = _notice()

    registry.create(notice, session=session)
    loaded = registry.get(
        tenant_id=TENANT,
        notification_id=NOTICE_ID,
        session=session,
    )
    assert loaded == notice
    failed = registry.record_failure(
        notice,
        OCCURRED + timedelta(minutes=1),
        session=session,
    )
    registry.mark_sent(
        failed,
        OCCURRED + timedelta(minutes=2),
        session=session,
    )

    non_null_sessions = [value for _operation, value in collection.calls if value is not None]
    assert non_null_sessions
    assert all(value is session for value in non_null_sessions)


def test_persistence_failures_map_to_stable_codes() -> None:
    index_collection = _FakeCollection()
    index_collection.fail_indexes = True
    with pytest.raises(PasswordResetNotificationPersistenceError) as index_error:
        PasswordResetNotificationRegistry(index_collection).ensure_indexes()
    assert index_error.value.code == "PASSWORD_RESET_NOTIFICATION_INDEX_CREATION_FAILED"

    insert_collection = _FakeCollection()
    insert_collection.fail_insert = True
    with pytest.raises(PasswordResetNotificationPersistenceError) as insert_error:
        PasswordResetNotificationRegistry(insert_collection).create(_notice())
    assert insert_error.value.code == "PASSWORD_RESET_NOTIFICATION_CREATE_FAILED"

    read_collection = _FakeCollection()
    read_collection.fail_read = True
    with pytest.raises(PasswordResetNotificationPersistenceError) as read_error:
        PasswordResetNotificationRegistry(read_collection).get(
            tenant_id=TENANT,
            notification_id=NOTICE_ID,
        )
    assert read_error.value.code == "PASSWORD_RESET_NOTIFICATION_READ_FAILED"

    update_collection = _FakeCollection()
    update_registry = PasswordResetNotificationRegistry(update_collection)
    notice = _notice()
    update_registry.create(notice)
    update_collection.fail_update = True
    with pytest.raises(PasswordResetNotificationPersistenceError) as update_error:
        update_registry.mark_sent(notice, OCCURRED + timedelta(minutes=1))
    assert update_error.value.code == "PASSWORD_RESET_NOTIFICATION_SENT_RECORD_FAILED"


# ARTIFACT: test_password_reset_notification_registry.py
# VERSION: v1.0.0-R10G4-PASSWORD-RESET-NOTIFICATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: deterministic persistence evidence only
# TENANT POSTURE: exact tenant-scoped reads and lifecycle CAS certified
# FAIL-CLOSED POSTURE: duplicate, corrupt, stale, replayed, cross-tenant, and persistence failure reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
