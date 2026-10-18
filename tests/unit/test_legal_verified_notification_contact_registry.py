"""Direct unit certificate for the H7D verified Legal contact registry.

TITLE: WILSY OS Verified Legal Notification Contact Registry Unit Certificate
VERSION: v1.0.0-L8-8H7D-VERIFIED-LEGAL-NOTIFICATION-CONTACT-REGISTRY-CERT
AUTHORITY: Direct deterministic certification of H7D registry behavior.
EPITOME: Prove exact indexes, digest-only persistence, consumed-verification
         provenance uniqueness, replay, tenant isolation, ACTIVE scope,
         caller-owned transaction propagation, corruption rejection and
         atomic ACTIVE-to-REVOKED compare-and-set semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_verified_notification_contact_registry.py
AUTHORITY BOUNDARY: H7D persistence/read/revocation evidence only.
TENANT POSTURE: Every operational lookup is exact tenant scoped.
TRANSACTION POSTURE: Every operational database call receives the exact
                     caller-owned active transaction.
FAIL-CLOSED POSTURE: Divergence, corruption, duplicate races, stale CAS and
                     persistence failures reject.
FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, Iterable, Mapping, cast

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_notification_contact_verification import (
    LegalNotificationContactChannel,
    LegalNotificationContactVerification,
)
from tools.eos.legal_operations.domain.legal_verified_notification_contact import (
    VerifiedLegalNotificationContact,
    VerifiedLegalNotificationContactStatus,
)
from tools.eos.legal_operations.registry.legal_verified_notification_contact_registry import (
    ACTIVE_SCOPE_INDEX,
    CONTACT_ID_INDEX,
    PRINCIPAL_SCOPE_INDEX,
    VERIFICATION_INDEX,
    VerifiedLegalNotificationContactRegistry,
    VerifiedLegalNotificationContactRegistryConflictError,
    VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError,
    VerifiedLegalNotificationContactRegistryPersistenceError,
    VerifiedLegalNotificationContactRegistryRetryTransactionError,
    VerifiedLegalNotificationContactRegistryTransactionRequiredError,
)


NOW = datetime(2026, 10, 12, 20, 0, 0, 654321, tzinfo=timezone.utc)
CONSUMED = NOW + timedelta(minutes=5)
VERIFIED = CONSUMED
EXPIRES = NOW + timedelta(minutes=30)

TENANT = "tenant-legal-a"
PRINCIPAL = "principal-1"
CONTACT_ID = "legal-contact-1"
ADDRESS_DIGEST = "a" * 128
TOKEN_DIGEST = "b" * 128


class _Session:
    def __init__(self, active: bool = True) -> None:
        self.in_transaction = active


class _Result:
    acknowledged = True


class _Cursor:
    def __init__(self, rows: Iterable[Mapping[str, object]]) -> None:
        self.rows = [deepcopy(dict(row)) for row in rows]
        self._limit: int | None = None

    def sort(self, keys: list[tuple[str, int]]) -> "_Cursor":
        for field, direction in reversed(keys):
            self.rows.sort(
                key=lambda row: str(row[field]),
                reverse=direction < 0,
            )
        return self

    def limit(self, value: int) -> "_Cursor":
        self._limit = value
        return self

    def __iter__(self) -> Any:
        rows = self.rows
        if self._limit is not None:
            rows = rows[: self._limit]
        return iter(deepcopy(rows))


class _FakeCollection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, object]]] = []
        self.calls: list[tuple[str, object | None]] = []

        self.fail_index = False
        self.fail_read = False
        self.fail_write = False
        self.fail_transition = False
        self.force_duplicate = False
        self.transition_result_override: dict[str, object] | None = None

    def create_index(
        self,
        keys: list[tuple[str, int]],
        **kwargs: object,
    ) -> str:
        self.calls.append(("create_index", None))
        if self.fail_index:
            raise PyMongoError("index-failure")
        self.indexes.append((list(keys), dict(kwargs)))
        return str(kwargs.get("name", "index"))

    def find_one(
        self,
        query: Mapping[str, object],
        *,
        session: object,
    ) -> dict[str, object] | None:
        self.calls.append(("find_one", session))
        if self.fail_read:
            raise PyMongoError("read-failure")

        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                return deepcopy(row)
        return None

    def find(
        self,
        query: Mapping[str, object],
        *,
        session: object,
    ) -> _Cursor:
        self.calls.append(("find", session))
        if self.fail_read:
            raise PyMongoError("read-failure")

        return _Cursor(
            row
            for row in self.rows
            if all(row.get(key) == value for key, value in query.items())
        )

    def insert_one(
        self,
        document: Mapping[str, object],
        *,
        session: object,
    ) -> _Result:
        self.calls.append(("insert_one", session))
        if self.force_duplicate:
            raise DuplicateKeyError("duplicate")
        if self.fail_write:
            raise PyMongoError("write-failure")

        self.rows.append(deepcopy(dict(document)))
        return _Result()

    def find_one_and_replace(
        self,
        selector: Mapping[str, object],
        replacement: Mapping[str, object],
        *,
        return_document: object,
        session: object,
    ) -> dict[str, object] | None:
        del return_document

        self.calls.append(("find_one_and_replace", session))

        if self.fail_transition:
            raise PyMongoError("transition-failure")

        for index, row in enumerate(self.rows):
            if all(row.get(key) == value for key, value in selector.items()):
                self.rows[index] = deepcopy(dict(replacement))
                if self.transition_result_override is not None:
                    return deepcopy(self.transition_result_override)
                return deepcopy(self.rows[index])

        return None


def _active_verification(
    *,
    tenant: str = TENANT,
    verification_id: str = "legal-verification-1",
    principal_id: str = PRINCIPAL,
    address_digest: str = ADDRESS_DIGEST,
    token_digest: str = TOKEN_DIGEST,
) -> LegalNotificationContactVerification:
    return LegalNotificationContactVerification.issue(
        tenant_id=tenant,
        verification_id=verification_id,
        principal_id=principal_id,
        channel=LegalNotificationContactChannel.EMAIL,
        address_digest=address_digest,
        token_digest=token_digest,
        issued_at=NOW,
        expires_at=EXPIRES,
    )


def _consumed_verification(
    **overrides: object,
) -> LegalNotificationContactVerification:
    verification = _active_verification(
        **cast(dict[str, Any], overrides)
    )
    return verification.consume(CONSUMED)


def _contact(
    *,
    contact_id: str = CONTACT_ID,
    verification: LegalNotificationContactVerification | None = None,
    verified_at: datetime = VERIFIED,
) -> VerifiedLegalNotificationContact:
    source = verification or _consumed_verification()
    return VerifiedLegalNotificationContact.from_consumed_verification(
        contact_id=contact_id,
        verification=source,
        verified_at=verified_at,
    )


def test_index_contract_is_exact_partial_unique_and_has_no_ttl() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)

    registry.ensure_indexes()

    assert len(collection.indexes) == 4

    by_name = {
        cast(str, kwargs["name"]): (keys, kwargs)
        for keys, kwargs in collection.indexes
    }

    assert set(by_name) == {
        CONTACT_ID_INDEX,
        VERIFICATION_INDEX,
        ACTIVE_SCOPE_INDEX,
        PRINCIPAL_SCOPE_INDEX,
    }

    contact_keys, contact_options = by_name[CONTACT_ID_INDEX]
    assert contact_keys == [
        ("tenant_id", 1),
        ("contact_id", 1),
    ]
    assert contact_options["unique"] is True

    verification_keys, verification_options = by_name[VERIFICATION_INDEX]
    assert verification_keys == [
        ("tenant_id", 1),
        ("verification_fingerprint", 1),
    ]
    assert verification_options["unique"] is True

    active_keys, active_options = by_name[ACTIVE_SCOPE_INDEX]
    assert active_keys == [
        ("tenant_id", 1),
        ("principal_id", 1),
        ("channel", 1),
        ("address_digest", 1),
    ]
    assert active_options["unique"] is True
    assert active_options["partialFilterExpression"] == {
        "revoked_at": None,
    }

    principal_keys, principal_options = by_name[PRINCIPAL_SCOPE_INDEX]
    assert principal_keys == [
        ("tenant_id", 1),
        ("principal_id", 1),
        ("channel", 1),
        ("verified_at", 1),
    ]
    assert principal_options["unique"] is False

    assert all(
        "expireAfterSeconds" not in kwargs
        for _, kwargs in collection.indexes
    )


def test_create_is_digest_only_exact_replay_and_forwards_transaction() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()
    value = _contact()

    created = registry.create(value, session=session)
    replay = registry.create(value, session=session)

    assert created == value
    assert replay == value
    assert len(collection.rows) == 1

    row = collection.rows[0]
    assert row == value.to_dict()

    assert "email" not in row
    assert "address" not in row
    assert "raw_email" not in row
    assert "raw_token" not in row
    assert "token_digest" not in row

    assert all(
        supplied is session
        for operation, supplied in collection.calls
        if operation in {"find_one", "insert_one"}
    )


def test_divergent_same_identity_replay_fails_closed() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()

    original = _contact()
    registry.create(original, session=session)

    divergent_verification = _consumed_verification(
        verification_id="legal-verification-2",
        token_digest="c" * 128,
    )
    divergent = _contact(
        contact_id=original.contact_id,
        verification=divergent_verification,
    )

    with pytest.raises(
        VerifiedLegalNotificationContactRegistryConflictError
    ) as captured:
        registry.create(divergent, session=session)

    assert captured.value.code == "L8_8H7D_DIVERGENT_REPLAY"
    assert collection.rows == [original.to_dict()]


def test_consumed_verification_provenance_cannot_elevate_twice() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()

    verification = _consumed_verification()
    first = _contact(
        contact_id="legal-contact-1",
        verification=verification,
    )
    second = _contact(
        contact_id="legal-contact-2",
        verification=verification,
    )

    registry.create(first, session=session)

    with pytest.raises(
        VerifiedLegalNotificationContactRegistryConflictError
    ) as captured:
        registry.create(second, session=session)

    assert (
        captured.value.code
        == "L8_8H7D_VERIFICATION_ALREADY_ELEVATED"
    )
    assert collection.rows == [first.to_dict()]


def test_duplicate_race_requires_whole_transaction_retry() -> None:
    collection = _FakeCollection()
    collection.force_duplicate = True
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()

    with pytest.raises(
        VerifiedLegalNotificationContactRegistryRetryTransactionError
    ) as captured:
        registry.create(_contact(), session=session)

    assert (
        captured.value.code
        == "L8_8H7D_DUPLICATE_RACE_RETRY_TRANSACTION"
    )


def test_reads_are_exactly_tenant_scoped() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()

    first = _contact()
    registry.create(first, session=session)

    foreign_verification = _consumed_verification(
        tenant="tenant-legal-b",
        verification_id="legal-verification-b",
        token_digest="d" * 128,
    )
    foreign = _contact(
        contact_id=first.contact_id,
        verification=foreign_verification,
    )
    registry.create(foreign, session=session)

    assert registry.get_by_id(
        TENANT,
        first.contact_id,
        session=session,
    ) == first

    assert registry.get_by_id(
        TENANT,
        "missing-contact",
        session=session,
    ) is None

    assert registry.get_by_verification_fingerprint(
        TENANT,
        first.verification_fingerprint,
        session=session,
    ) == first

    assert registry.get_by_verification_fingerprint(
        TENANT,
        foreign.verification_fingerprint,
        session=session,
    ) is None


def test_get_active_requires_exact_address_scope() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()

    value = _contact()
    registry.create(value, session=session)

    assert registry.get_active(
        TENANT,
        PRINCIPAL,
        LegalNotificationContactChannel.EMAIL,
        ADDRESS_DIGEST,
        session=session,
    ) == value

    assert registry.get_active(
        TENANT,
        PRINCIPAL,
        LegalNotificationContactChannel.EMAIL,
        "e" * 128,
        session=session,
    ) is None

    revoked = value.revoke(VERIFIED + timedelta(minutes=1))
    collection.rows[0] = revoked.to_dict()

    assert registry.get_active(
        TENANT,
        PRINCIPAL,
        LegalNotificationContactChannel.EMAIL,
        ADDRESS_DIGEST,
        session=session,
    ) is None


def test_multiple_active_rows_fail_closed() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()

    first = _contact(contact_id="legal-contact-1")

    second_verification = _consumed_verification(
        verification_id="legal-verification-2",
        token_digest="f" * 128,
    )
    second = _contact(
        contact_id="legal-contact-2",
        verification=second_verification,
    )

    collection.rows.extend(
        [
            first.to_dict(),
            second.to_dict(),
        ]
    )

    with pytest.raises(
        VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError
    ) as captured:
        registry.get_active(
            TENANT,
            PRINCIPAL,
            LegalNotificationContactChannel.EMAIL,
            ADDRESS_DIGEST,
            session=session,
        )

    assert captured.value.code == "L8_8H7D_MULTIPLE_ACTIVE_CONTACTS"


def test_principal_scope_is_exact_and_oldest_first() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()

    first = _contact(contact_id="contact-a")

    second_verification = _active_verification(
        verification_id="legal-verification-2",
        token_digest="1" * 128,
    ).consume(CONSUMED + timedelta(seconds=1))

    second = _contact(
        contact_id="contact-b",
        verification=second_verification,
        verified_at=VERIFIED + timedelta(seconds=1),
    )

    registry.create(first, session=session)
    registry.create(second, session=session)

    values = registry.list_principal_scope(
        TENANT,
        PRINCIPAL,
        LegalNotificationContactChannel.EMAIL,
        session=session,
    )

    assert values == (first, second)


def test_microseconds_survive_persistence_round_trip_exactly() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()
    value = _contact()

    registry.create(value, session=session)

    readback = registry.get_by_id(
        TENANT,
        CONTACT_ID,
        session=session,
    )

    assert readback == value
    assert readback is not None
    assert readback.verification_consumed_at.microsecond == CONSUMED.microsecond
    assert readback.verification_expires_at.microsecond == EXPIRES.microsecond
    assert readback.verified_at.microsecond == VERIFIED.microsecond


def test_active_transaction_is_required_for_operational_methods() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    value = _contact()

    operations = (
        lambda: registry.create(value, session=_Session(False)),
        lambda: registry.get_by_id(
            TENANT,
            CONTACT_ID,
            session=_Session(False),
        ),
        lambda: registry.get_by_verification_fingerprint(
            TENANT,
            value.verification_fingerprint,
            session=_Session(False),
        ),
        lambda: registry.get_active(
            TENANT,
            PRINCIPAL,
            LegalNotificationContactChannel.EMAIL,
            ADDRESS_DIGEST,
            session=_Session(False),
        ),
        lambda: registry.list_principal_scope(
            TENANT,
            PRINCIPAL,
            LegalNotificationContactChannel.EMAIL,
            session=_Session(False),
        ),
        lambda: registry.revoke(
            value,
            VERIFIED + timedelta(minutes=1),
            session=_Session(False),
        ),
    )

    for operation in operations:
        with pytest.raises(
            VerifiedLegalNotificationContactRegistryTransactionRequiredError
        ) as captured:
            operation()

        assert (
            captured.value.code
            == "L8_8H7D_ACTIVE_TRANSACTION_REQUIRED"
        )


def test_revoke_is_atomic_and_exact_transition_replay_is_idempotent() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()

    source = _contact()
    registry.create(source, session=session)

    revoked_at = VERIFIED + timedelta(minutes=1)

    revoked = registry.revoke(
        source,
        revoked_at,
        session=session,
    )

    assert revoked.status is VerifiedLegalNotificationContactStatus.REVOKED
    assert revoked.revoked_at == revoked_at

    replay = registry.revoke(
        source,
        revoked_at,
        session=session,
    )

    assert replay == revoked
    assert collection.rows == [revoked.to_dict()]


def test_stale_divergent_revoke_rejects() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()

    source = _contact()
    registry.create(source, session=session)

    first_revocation = VERIFIED + timedelta(minutes=1)
    registry.revoke(
        source,
        first_revocation,
        session=session,
    )

    with pytest.raises(
        VerifiedLegalNotificationContactRegistryConflictError
    ) as captured:
        registry.revoke(
            source,
            first_revocation + timedelta(microseconds=1),
            session=session,
        )

    assert captured.value.code == "L8_8H7D_STALE_SOURCE_CONFLICT"


def test_persisted_corruption_is_rejected_on_hydration() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()

    value = _contact()
    registry.create(value, session=session)

    collection.rows[0]["principal_id"] = "corrupt-principal"

    with pytest.raises(
        VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError
    ) as captured:
        registry.get_by_id(
            TENANT,
            CONTACT_ID,
            session=session,
        )

    assert captured.value.code == "L8_8H7D_PERSISTED_RECORD_INVALID"


def test_transition_result_corruption_is_rejected() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()

    source = _contact()
    registry.create(source, session=session)

    replacement = source.revoke(
        VERIFIED + timedelta(minutes=1)
    ).to_dict()
    replacement["principal_id"] = "corrupt-principal"

    collection.transition_result_override = replacement

    with pytest.raises(
        VerifiedLegalNotificationContactRegistryPersistedRecordInvalidError
    ):
        registry.revoke(
            source,
            VERIFIED + timedelta(minutes=1),
            session=session,
        )


def test_missing_after_failed_cas_is_not_found_conflict() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()

    source = _contact()

    with pytest.raises(
        VerifiedLegalNotificationContactRegistryConflictError
    ) as captured:
        registry.revoke(
            source,
            VERIFIED + timedelta(minutes=1),
            session=session,
        )

    assert captured.value.code == "L8_8H7D_CONTACT_NOT_FOUND"


def test_index_read_write_and_transition_failures_are_stable() -> None:
    index_collection = _FakeCollection()
    index_collection.fail_index = True

    with pytest.raises(
        VerifiedLegalNotificationContactRegistryPersistenceError
    ) as captured:
        VerifiedLegalNotificationContactRegistry(
            index_collection
        ).ensure_indexes()

    assert captured.value.code == "L8_8H7D_INDEX_PERSISTENCE_FAILURE"

    read_collection = _FakeCollection()
    read_collection.fail_read = True
    read_registry = VerifiedLegalNotificationContactRegistry(read_collection)

    with pytest.raises(
        VerifiedLegalNotificationContactRegistryPersistenceError
    ) as captured:
        read_registry.get_by_id(
            TENANT,
            CONTACT_ID,
            session=_Session(),
        )

    assert captured.value.code == "L8_8H7D_READ_PERSISTENCE_FAILURE"

    write_collection = _FakeCollection()
    write_collection.fail_write = True
    write_registry = VerifiedLegalNotificationContactRegistry(write_collection)

    with pytest.raises(
        VerifiedLegalNotificationContactRegistryPersistenceError
    ) as captured:
        write_registry.create(
            _contact(),
            session=_Session(),
        )

    assert captured.value.code == "L8_8H7D_WRITE_PERSISTENCE_FAILURE"

    transition_collection = _FakeCollection()
    transition_registry = VerifiedLegalNotificationContactRegistry(
        transition_collection
    )
    session = _Session()
    source = _contact()
    transition_registry.create(source, session=session)
    transition_collection.fail_transition = True

    with pytest.raises(
        VerifiedLegalNotificationContactRegistryPersistenceError
    ) as captured:
        transition_registry.revoke(
            source,
            VERIFIED + timedelta(minutes=1),
            session=session,
        )

    assert (
        captured.value.code
        == "L8_8H7D_TRANSITION_PERSISTENCE_FAILURE"
    )


def test_every_operational_database_call_forwards_exact_session() -> None:
    collection = _FakeCollection()
    registry = VerifiedLegalNotificationContactRegistry(collection)
    session = _Session()
    value = _contact()

    registry.create(value, session=session)
    registry.get_by_id(
        TENANT,
        CONTACT_ID,
        session=session,
    )
    registry.get_by_verification_fingerprint(
        TENANT,
        value.verification_fingerprint,
        session=session,
    )
    registry.get_active(
        TENANT,
        PRINCIPAL,
        LegalNotificationContactChannel.EMAIL,
        ADDRESS_DIGEST,
        session=session,
    )
    registry.list_principal_scope(
        TENANT,
        PRINCIPAL,
        LegalNotificationContactChannel.EMAIL,
        session=session,
    )
    registry.revoke(
        value,
        VERIFIED + timedelta(minutes=1),
        session=session,
    )

    operational = {
        "find_one",
        "find",
        "insert_one",
        "find_one_and_replace",
    }

    assert [
        supplied
        for operation, supplied in collection.calls
        if operation in operational
    ]

    assert all(
        supplied is session
        for operation, supplied in collection.calls
        if operation in operational
    )


# ARTIFACT: test_legal_verified_notification_contact_registry.py
# VERSION: v1.0.0-L8-8H7D-VERIFIED-LEGAL-NOTIFICATION-CONTACT-REGISTRY-CERT
# AUTHORITY BOUNDARY: deterministic H7D registry test evidence only
# TENANT POSTURE: exact tenant predicates and active caller transaction required
# FAIL-CLOSED POSTURE: replay/corruption/stale-CAS/race/persistence failures reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
