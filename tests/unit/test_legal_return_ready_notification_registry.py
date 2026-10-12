"""Direct adversarial certificate for Legal return-ready notification registry.

TITLE: Legal Operations Return-Ready Notification Registry Direct Certificate
VERSION: v1.0.0-L8-8F-RETURN-READY-NOTIFICATION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify append-only tenant-scoped RETURN_READY intent persistence,
         deterministic indexes, exact replay, strict hydration, active caller
         transactions, cross-tenant absence and whole-transaction retry races.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_return_ready_notification_registry.py
COLLABORATION / OWNERSHIP: Certificate only. L8-8E owns notification intent
                            semantics; L8-8F owns persistence/read semantics.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: 2026-10-12 v1.0.0-L8-8F-RETURN-READY-NOTIFICATION-REGISTRY-CERT
           establishes direct adversarial coverage for exact indexes/no TTL,
           active transaction enforcement, replay/divergence, duplicate races,
           tenant isolation, strict corruption rejection and return identity.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers and fingerprints only.
TENANT BOUNDARY: Every read/write assertion is exact tenant scoped.
AUTHORITY BOUNDARY: Persistence certificate only; no recipient, channel,
                    provider, transport, delivery, lifecycle, Court or finance.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Missing transaction, corruption, divergence,
                         cross-scope leakage and duplicate races reject.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from pymongo.errors import DuplicateKeyError

from tools.eos.legal_operations.domain.legal_operations_lifecycle import (
    ReturnOfService,
    ServiceAttempt,
    ServiceAttemptState,
    ServiceExecution,
)
from tools.eos.legal_operations.domain.legal_return_ready_notification import (
    LegalReturnReadyNotification,
    create_return_ready_notification,
)
from tools.eos.legal_operations.registry.legal_return_ready_notification_registry import (
    INDEX_TENANT_DOCUMENT_OCCURRED,
    INDEX_TENANT_NOTIFICATION,
    INDEX_TENANT_RETURN,
    LegalReturnReadyNotificationRegistry,
    LegalReturnReadyNotificationRegistryConflictError,
    LegalReturnReadyNotificationRegistryError,
    LegalReturnReadyNotificationRegistryRetryTransactionError,
    LegalReturnReadyNotificationRegistryTransactionRequiredError,
    ensure_indexes,
)


BASE = datetime(2026, 10, 12, 5, 0, tzinfo=timezone.utc)
FP = "a" * 128


class Session:
    in_transaction = True


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, object]]] = []
        self.calls: list[tuple[str, object]] = []
        self.duplicate = False

    def create_index(
        self,
        keys: list[tuple[str, int]],
        **kwargs: object,
    ) -> str:
        self.indexes.append((keys, dict(kwargs)))
        return str(kwargs.get("name"))

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, object] | None:
        self.calls.append(("find_one", session))
        return next(
            (
                row
                for row in self.rows
                if all(row.get(key) == value for key, value in query.items())
            ),
            None,
        )

    def insert_one(
        self,
        row: dict[str, object],
        *,
        session: object = None,
    ) -> None:
        self.calls.append(("insert_one", session))
        if self.duplicate:
            raise DuplicateKeyError("duplicate")
        self.rows.append(deepcopy(row))


def canonical_return(
    *,
    return_id: str = "return-1",
) -> ReturnOfService:
    allocated = ServiceAttempt(
        tenant_id="tenant-a",
        attempt_id="attempt-1",
        instruction_id="instruction-1",
        document_id="document-1",
        deputy_id="deputy-1",
        allocated_at=BASE,
        allocation_evidence_reference="allocation-1",
    )
    attempted = allocated.transition_to(
        ServiceAttemptState.ATTEMPTED,
        evidence_reference="attempt-1",
        occurred_at=BASE + timedelta(minutes=1),
    )
    completed = attempted.transition_to(
        ServiceAttemptState.COMPLETED,
        evidence_reference="service-evidence-1",
        evidence_fingerprint=FP,
        occurred_at=BASE + timedelta(minutes=2),
    )
    execution = ServiceExecution.from_attempt(
        attempt=completed,
        service_execution_id="execution-1",
        executed_at=BASE + timedelta(minutes=3),
    )
    return ReturnOfService.from_service_execution(
        instruction_id="instruction-1",
        service_execution=execution,
        return_id=return_id,
        generated_at=BASE + timedelta(minutes=4),
    )


def notice(
    *,
    notification_id: str = "notification-1",
    return_id: str = "return-1",
) -> LegalReturnReadyNotification:
    return create_return_ready_notification(
        return_of_service=canonical_return(return_id=return_id),
        notification_id=notification_id,
    )


def test_indexes_are_exact_and_have_no_ttl() -> None:
    collection = Collection()
    ensure_indexes(collection)

    by_name = {
        str(options["name"]): (keys, options)
        for keys, options in collection.indexes
    }

    assert by_name[INDEX_TENANT_NOTIFICATION][0] == [
        ("tenant_id", 1),
        ("notification_id", 1),
    ]
    assert by_name[INDEX_TENANT_NOTIFICATION][1]["unique"] is True

    assert by_name[INDEX_TENANT_RETURN][0] == [
        ("tenant_id", 1),
        ("return_id", 1),
    ]
    assert by_name[INDEX_TENANT_RETURN][1]["unique"] is True

    assert by_name[INDEX_TENANT_DOCUMENT_OCCURRED][0] == [
        ("tenant_id", 1),
        ("document_id", 1),
        ("occurred_at", 1),
    ]
    assert by_name[INDEX_TENANT_DOCUMENT_OCCURRED][1].get("unique") is not True

    assert all(
        "expireAfterSeconds" not in options
        for _, options in collection.indexes
    )


def test_active_transaction_is_required_before_any_write() -> None:
    collection = Collection()
    registry = LegalReturnReadyNotificationRegistry(collection)

    with pytest.raises(
        LegalReturnReadyNotificationRegistryTransactionRequiredError,
        match="L8_8F_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(notice(), session=None)

    assert collection.rows == []
    assert collection.calls == []


def test_create_exact_replay_and_session_propagation() -> None:
    collection = Collection()
    registry = LegalReturnReadyNotificationRegistry(collection)
    session = Session()
    value = notice()

    first = registry.create_or_replay(value, session=session)
    replay = registry.create_or_replay(value, session=session)

    assert first == value
    assert replay == value
    assert len(collection.rows) == 1
    assert all(call_session is session for _, call_session in collection.calls)


def test_divergent_notification_identity_rejects() -> None:
    collection = Collection()
    registry = LegalReturnReadyNotificationRegistry(collection)
    session = Session()

    registry.create_or_replay(notice(), session=session)

    divergent = notice(
        notification_id="notification-1",
        return_id="return-2",
    )

    with pytest.raises(
        LegalReturnReadyNotificationRegistryConflictError,
        match="L8_8F_DIVERGENT_NOTIFICATION_IDENTITY",
    ):
        registry.create_or_replay(divergent, session=session)


def test_divergent_return_identity_rejects() -> None:
    collection = Collection()
    registry = LegalReturnReadyNotificationRegistry(collection)
    session = Session()

    registry.create_or_replay(notice(), session=session)

    divergent = notice(
        notification_id="notification-2",
        return_id="return-1",
    )

    with pytest.raises(
        LegalReturnReadyNotificationRegistryConflictError,
        match="L8_8F_DIVERGENT_RETURN_IDENTITY",
    ):
        registry.create_or_replay(divergent, session=session)


def test_duplicate_key_requires_whole_transaction_retry() -> None:
    collection = Collection()
    collection.duplicate = True
    registry = LegalReturnReadyNotificationRegistry(collection)

    with pytest.raises(
        LegalReturnReadyNotificationRegistryRetryTransactionError,
        match="L8_8F_RETRY_TRANSACTION_REQUIRED",
    ):
        registry.create_or_replay(notice(), session=Session())

    assert collection.rows == []


def test_reads_are_exact_tenant_scoped_and_foreign_absence() -> None:
    collection = Collection()
    registry = LegalReturnReadyNotificationRegistry(collection)
    session = Session()
    value = notice()
    registry.create_or_replay(value, session=session)

    assert (
        registry.get_by_notification_id(
            tenant_id="tenant-a",
            notification_id="notification-1",
            session=session,
        )
        == value
    )
    assert (
        registry.get_by_return_id(
            tenant_id="tenant-a",
            return_id="return-1",
            session=session,
        )
        == value
    )

    assert (
        registry.get_by_notification_id(
            tenant_id="tenant-b",
            notification_id="notification-1",
            session=session,
        )
        is None
    )
    assert (
        registry.get_by_return_id(
            tenant_id="tenant-b",
            return_id="return-1",
            session=session,
        )
        is None
    )


def test_corrupt_persisted_row_with_recipient_injection_rejects() -> None:
    collection = Collection()
    registry = LegalReturnReadyNotificationRegistry(collection)
    session = Session()
    value = notice()
    registry.create_or_replay(value, session=session)

    collection.rows[0]["recipient_email"] = "person@example.invalid"

    with pytest.raises(
        LegalReturnReadyNotificationRegistryError,
        match="L8_8F_CORRUPT_NOTIFICATION",
    ):
        registry.get_by_notification_id(
            tenant_id="tenant-a",
            notification_id="notification-1",
            session=session,
        )


def test_corrupt_persisted_fingerprint_rejects() -> None:
    collection = Collection()
    registry = LegalReturnReadyNotificationRegistry(collection)
    session = Session()
    value = notice()
    registry.create_or_replay(value, session=session)

    collection.rows[0]["fingerprint"] = "b" * 128

    with pytest.raises(
        LegalReturnReadyNotificationRegistryError,
        match="L8_8F_CORRUPT_NOTIFICATION",
    ):
        registry.get_by_return_id(
            tenant_id="tenant-a",
            return_id="return-1",
            session=session,
        )


def test_persisted_shape_contains_no_delivery_authority_fields() -> None:
    collection = Collection()
    registry = LegalReturnReadyNotificationRegistry(collection)
    registry.create_or_replay(notice(), session=Session())

    assert len(collection.rows) == 1
    forbidden = {
        "recipient",
        "recipient_id",
        "recipient_email",
        "phone",
        "channel",
        "provider",
        "provider_id",
        "message",
        "message_body",
        "template",
        "attempt_count",
        "last_attempt_at",
        "delivered_at",
        "sent_at",
        "transport_secret",
    }
    assert not forbidden.intersection(collection.rows[0])


# ARTIFACT: test_legal_return_ready_notification_registry.py
# VERSION: v1.0.0-L8-8F-RETURN-READY-NOTIFICATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: direct append-only RETURN_READY intent persistence certificate only
# TENANT POSTURE: exact tenant-scoped replay/read behavior certified
# TRANSACTION POSTURE: active caller transaction required before reads/writes
# DELIVERY POSTURE: no recipient/channel/provider/message/attempt/delivery lifecycle state
# FAIL-CLOSED POSTURE: missing transaction, corruption, divergence and duplicate race reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
