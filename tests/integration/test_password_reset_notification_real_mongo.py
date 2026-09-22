"""Real-Mongo certificate for password-reset notification persistence.

TITLE: WILSY OS Password Reset Notification Real-Mongo Certificate
VERSION: v1.0.0-R10G15-PASSWORD-RESET-NOTIFICATION-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies R10G3 against a writable loopback MongoDB replica set using
         UUID-scoped disposable databases: indexes, tenant isolation, caller
         session rollback, retryable failure evidence, terminal SENT CAS,
         replay rejection, and corruption handling.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_password_reset_notification_real_mongo.py
COLLABORATION / OWNERSHIP: Exercises R10G1/R10G3 only; no SMTP, HTTP, password
                           reset mutation, recovery capability, or production DB.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10G15-PASSWORD-RESET-NOTIFICATION-REAL-MONGO-CERT — Adds
           executable replica-set evidence for notification persistence and CAS.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers only; durable rows
                            contain no recipient, password, token, digest, JWT,
                            session credential, MFA secret, or SMTP material.
TENANT BOUNDARY: Every read/mutation is exact tenant-scoped; cross-tenant reads
                 return absence without disclosing another tenant's evidence.
AUTHORITY BOUNDARY: Disposable Mongo persistence evidence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Tests use real caller-owned ClientSession/transactions.
FAIL-CLOSED POSTURE: Unavailable/non-loopback/non-primary Mongo fails the suite;
                     no skip/xfail converts missing infrastructure into PASS.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Iterator
from urllib.parse import urlparse

import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.saas.auth.password_reset_notification import (
    PasswordResetNotification,
    PasswordResetNotificationStatus,
)
from tools.eos.saas.auth.password_reset_notification_registry import (
    COLLECTION,
    PasswordResetNotificationLifecycleConflictError,
    PasswordResetNotificationPersistedRecordInvalidError,
    PasswordResetNotificationRegistry,
)


VERSION = "v1.0.0-R10G15-PASSWORD-RESET-NOTIFICATION-REAL-MONGO-CERT"
URI_ENV = "R10G_PASSWORD_RESET_NOTIFICATION_MONGO_URI"
FALLBACK_URI_ENV = "TEST_VENDOR_MONGO_URI"
DEFAULT_URI = "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS"
REPLICA_SET = "wilsyVendorCertRS"
DATABASE_PREFIX = "wilsy_r10g_reset_notification_"
TENANT = "tenant-r10g-notification"
OTHER_TENANT = "tenant-r10g-notification-other"
PRINCIPAL = "principal-r10g-notification"
OCCURRED = datetime(2026, 9, 22, 21, 30, tzinfo=timezone.utc)


def _runtime_uri() -> str:
    """Resolve only a loopback disposable Mongo URI."""

    value = os.environ.get(URI_ENV) or os.environ.get(FALLBACK_URI_ENV) or DEFAULT_URI
    parsed = urlparse(value)
    if parsed.scheme != "mongodb" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise RuntimeError("R10G15 requires a loopback mongodb URI")
    if parsed.path.strip("/") in {"wilsy", "wilsy/"} or "mongodb.net" in value.lower():
        raise RuntimeError("R10G15 rejects canonical or hosted Mongo")
    return value


def _open_runtime() -> MongoClient[Any]:
    """Connect to and prove the expected writable replica-set primary."""

    client: MongoClient[Any] = MongoClient(
        _runtime_uri(),
        replicaSet=REPLICA_SET,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
        retryWrites=True,
    )
    try:
        hello = client.admin.command("hello")
        if hello.get("setName") != REPLICA_SET or hello.get("isWritablePrimary") is not True:
            raise RuntimeError("R10G15 requires a writable replica-set primary")
        if client.address != ("127.0.0.1", 27027):
            raise RuntimeError("R10G15 connected address is not loopback port 27027")
        return client
    except BaseException:
        client.close()
        raise


@pytest.fixture(scope="module")
def mongo_client() -> Iterator[MongoClient[Any]]:
    client = _open_runtime()
    try:
        yield client
    finally:
        client.close()


@pytest.fixture()
def collection(mongo_client: MongoClient[Any]) -> Iterator[Any]:
    database_name = DATABASE_PREFIX + uuid.uuid4().hex
    database = mongo_client.get_database(
        database_name,
        read_concern=ReadConcern("majority"),
        write_concern=WriteConcern(w="majority", j=True),
    )
    source = database[COLLECTION]
    try:
        yield source
    finally:
        mongo_client.drop_database(database_name)
        assert database_name not in mongo_client.list_database_names()


def _notice(
    suffix: str,
    *,
    tenant_id: str = TENANT,
    principal_id: str = PRINCIPAL,
) -> PasswordResetNotification:
    return PasswordResetNotification.issue(
        notification_id=f"WILSYRESETNOTICE-R10G15-{suffix}",
        tenant_id=tenant_id,
        principal_id=principal_id,
        occurred_at=OCCURRED,
    )


def test_real_indexes_are_exact_and_secret_free(collection: Any) -> None:
    registry = PasswordResetNotificationRegistry(collection)
    registry.ensure_indexes()

    indexes = {entry["name"]: entry for entry in collection.list_indexes()}
    assert indexes["password_reset_notification_identity_unique"]["unique"] is True
    assert list(indexes["password_reset_notification_identity_unique"]["key"].items()) == [
        ("notification_id", 1)
    ]
    assert list(indexes["password_reset_notification_tenant_principal_status"]["key"].items()) == [
        ("tenant_id", 1),
        ("principal_id", 1),
        ("status", 1),
        ("occurred_at", 1),
    ]
    assert list(indexes["password_reset_notification_tenant_delivery_queue"]["key"].items()) == [
        ("tenant_id", 1),
        ("status", 1),
        ("last_attempt_at", 1),
        ("occurred_at", 1),
    ]
    indexed_fields = {
        field
        for entry in indexes.values()
        for field in entry["key"].keys()
    }
    assert {"email", "recipient", "address", "password", "token", "digest"}.isdisjoint(
        indexed_fields
    )


def test_real_create_and_tenant_scoped_read(collection: Any) -> None:
    registry = PasswordResetNotificationRegistry(collection)
    registry.ensure_indexes()
    notice = _notice("tenant")

    assert registry.create(notice) == notice
    assert registry.get(
        tenant_id=TENANT,
        notification_id=notice.notification_id,
    ) == notice
    assert registry.get(
        tenant_id=OTHER_TENANT,
        notification_id=notice.notification_id,
    ) is None

    row = collection.find_one({"notification_id": notice.notification_id})
    assert row is not None
    forbidden = {
        "email",
        "recipient",
        "address",
        "password",
        "recovery_token",
        "token",
        "token_digest",
        "capability_digest",
        "jwt",
        "refresh_token",
        "mfa_secret",
    }
    assert forbidden.isdisjoint(row)


def test_real_caller_transaction_abort_rolls_back_create(
    collection: Any,
    mongo_client: MongoClient[Any],
) -> None:
    registry = PasswordResetNotificationRegistry(collection)
    registry.ensure_indexes()
    notice = _notice("rollback")

    with pytest.raises(RuntimeError, match="synthetic abort"):
        with mongo_client.start_session() as session:
            with session.start_transaction():
                registry.create(notice, session=session)
                assert registry.get(
                    tenant_id=TENANT,
                    notification_id=notice.notification_id,
                    session=session,
                ) == notice
                raise RuntimeError("synthetic abort")

    assert registry.get(
        tenant_id=TENANT,
        notification_id=notice.notification_id,
    ) is None


def test_real_retry_failure_then_sent_transition(collection: Any) -> None:
    registry = PasswordResetNotificationRegistry(collection)
    registry.ensure_indexes()
    notice = _notice("delivery")
    registry.create(notice)

    failed_at = OCCURRED + timedelta(minutes=1)
    sent_at = OCCURRED + timedelta(minutes=2)
    failed = registry.record_failure(notice, failed_at)
    assert failed.status is PasswordResetNotificationStatus.PENDING
    assert failed.attempt_count == 1
    assert failed.last_attempt_at == failed_at

    sent = registry.mark_sent(failed, sent_at)
    assert sent.status is PasswordResetNotificationStatus.SENT
    assert sent.attempt_count == 2
    assert sent.delivered_at == sent_at

    persisted = registry.get(
        tenant_id=TENANT,
        notification_id=notice.notification_id,
    )
    assert persisted == sent


def test_real_stale_and_terminal_replay_fail_closed(collection: Any) -> None:
    registry = PasswordResetNotificationRegistry(collection)
    registry.ensure_indexes()
    notice = _notice("replay")
    registry.create(notice)

    failed = registry.record_failure(notice, OCCURRED + timedelta(minutes=1))

    with pytest.raises(PasswordResetNotificationLifecycleConflictError) as stale:
        registry.record_failure(notice, OCCURRED + timedelta(minutes=2))
    assert stale.value.code == "PASSWORD_RESET_NOTIFICATION_LIFECYCLE_CONFLICT"

    sent = registry.mark_sent(failed, OCCURRED + timedelta(minutes=2))
    with pytest.raises(PasswordResetNotificationLifecycleConflictError) as replay:
        registry.mark_sent(failed, OCCURRED + timedelta(minutes=3))
    assert replay.value.code == "PASSWORD_RESET_NOTIFICATION_ALREADY_SENT"
    assert registry.get(
        tenant_id=TENANT,
        notification_id=notice.notification_id,
    ) == sent


def test_real_corrupt_row_is_rejected(collection: Any) -> None:
    registry = PasswordResetNotificationRegistry(collection)
    notice = _notice("corrupt")
    row = notice.to_document()
    row["schema"] = "CORRUPT"
    collection.insert_one(row)

    with pytest.raises(PasswordResetNotificationPersistedRecordInvalidError) as captured:
        registry.get(
            tenant_id=TENANT,
            notification_id=notice.notification_id,
        )
    assert captured.value.code == "PASSWORD_RESET_NOTIFICATION_PERSISTED_RECORD_INVALID"


# ARTIFACT: test_password_reset_notification_real_mongo.py
# VERSION: v1.0.0-R10G15-PASSWORD-RESET-NOTIFICATION-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: disposable real-Mongo notification persistence evidence only
# TENANT POSTURE: exact tenant-scoped reads/CAS; cross-tenant absence certified
# FAIL-CLOSED POSTURE: unavailable Mongo, stale/replay, and corrupt state fail
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
