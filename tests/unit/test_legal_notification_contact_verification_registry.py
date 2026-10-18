"""Direct certificate for Legal notification-contact verification persistence.

TITLE: Legal Notification Contact Verification Registry Direct Certificate
VERSION: v1.0.0-L8-8H7C-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance / Python EOS Legal Operations
EPITOME: Certify H7C digest-only persistence, exact tenant scoping, index
         topology, caller-owned active transaction enforcement, exact replay,
         corruption rejection, microsecond preservation and lifecycle CAS.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_notification_contact_verification_registry.py
COLLABORATION / OWNERSHIP: Exercises H7C against one deterministic
                           PyMongo-shaped fake only. H7A remains immutable
                           verification authority; H7B is not created here.
CERTIFICATION / UPDATE DATE: 2026-10-12
CHANGELOG: v1.0.0-L8-8H7C-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-REGISTRY-CERT
           establishes direct unit evidence for indexes/no-TTL, digest-only
           persistence, exact replay, tenant/token/principal reads, mandatory
           active transactions, microsecond-safe hydration, lifecycle CAS,
           exact transition replay, stale-source rejection, corruption
           rejection and stable persistence failures.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic digests only. No raw email or raw
                             verification token is persisted or asserted.
TENANT BOUNDARY: Every operational read/write is exact tenant scoped.
AUTHORITY BOUNDARY: H7C persistence evidence only. No H7B contact authority,
                    IAM, HTTP, SMTP, dispatch, delivery or Court authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.legal_operations.domain.legal_notification_contact_verification import (
    LegalNotificationContactChannel,
    LegalNotificationContactVerification,
    LegalNotificationContactVerificationStatus,
)
from tools.eos.legal_operations.registry.legal_notification_contact_verification_registry import (
    IDENTITY_INDEX,
    PRINCIPAL_SCOPE_INDEX,
    TOKEN_INDEX,
    LegalNotificationContactVerificationRegistry,
    LegalNotificationContactVerificationRegistryConflictError,
    LegalNotificationContactVerificationRegistryPersistedRecordInvalidError,
    LegalNotificationContactVerificationRegistryPersistenceError,
    LegalNotificationContactVerificationRegistryRetryTransactionError,
    LegalNotificationContactVerificationRegistryTransactionRequiredError,
)


TENANT = "tenant-legal-a"
OTHER_TENANT = "tenant-legal-b"
PRINCIPAL = "principal-1"
ISSUED = datetime(2026, 10, 12, 18, 45, 12, 654321, tzinfo=timezone.utc)
EXPIRES = ISSUED + timedelta(minutes=30)
ADDRESS_DIGEST = "a" * 128
TOKEN_DIGEST = "b" * 128


class _Session:
    """Minimal caller-owned transaction surface used by H7C."""

    def __init__(self, *, active: bool = True) -> None:
        self.in_transaction = active


class _Cursor:
    """Deterministic sortable fake cursor."""

    def __init__(self, rows: list[dict[str, object]]) -> None:
        self.rows = rows

    def sort(self, keys):
        for field, direction in reversed(list(keys)):
            self.rows.sort(
                key=lambda row: str(row[field]),
                reverse=direction < 0,
            )
        return self

    def __iter__(self):
        return iter(self.rows)


class _FakeCollection:
    """Deterministic PyMongo-shaped collection used only by this certificate."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[dict[str, object]] = []
        self.calls: list[tuple[str, object | None]] = []
        self.fail_indexes = False
        self.fail_read = False
        self.fail_insert = False
        self.fail_replace = False

    @staticmethod
    def _matches(
        row: dict[str, object],
        query: dict[str, object],
    ) -> bool:
        return all(row.get(key) == expected for key, expected in query.items())

    def create_index(self, keys, *, unique=False, name=None, **kwargs):
        if self.fail_indexes:
            raise PyMongoError("index failure")
        self.indexes.append(
            {
                "keys": tuple(keys),
                "unique": unique,
                "name": name,
                **kwargs,
            }
        )
        return name

    def find_one(self, query, *, session=None):
        if self.fail_read:
            raise PyMongoError("read failure")
        self.calls.append(("find_one", session))
        for row in self.rows:
            if self._matches(row, query):
                return deepcopy(row)
        return None

    def find(self, query, *, session=None):
        if self.fail_read:
            raise PyMongoError("read failure")
        self.calls.append(("find", session))
        return _Cursor(
            [
                deepcopy(row)
                for row in self.rows
                if self._matches(row, query)
            ]
        )

    def insert_one(self, document, *, session=None):
        if self.fail_insert:
            raise PyMongoError("insert failure")

        self.calls.append(("insert_one", session))
        incoming = deepcopy(document)

        for row in self.rows:
            same_identity = (
                row.get("tenant_id") == incoming.get("tenant_id")
                and row.get("verification_id")
                == incoming.get("verification_id")
            )
            same_token = (
                row.get("tenant_id") == incoming.get("tenant_id")
                and row.get("token_digest") == incoming.get("token_digest")
            )
            if same_identity or same_token:
                raise DuplicateKeyError("duplicate")

        self.rows.append(incoming)
        return object()

    def find_one_and_replace(
        self,
        query,
        replacement,
        *,
        return_document=None,
        session=None,
    ):
        del return_document
        if self.fail_replace:
            raise PyMongoError("replace failure")

        self.calls.append(("find_one_and_replace", session))

        for index, row in enumerate(self.rows):
            if self._matches(row, query):
                self.rows[index] = deepcopy(replacement)
                return deepcopy(self.rows[index])

        return None


def _verification(
    *,
    tenant_id: str = TENANT,
    verification_id: str = "legal-verification-1",
    principal_id: str = PRINCIPAL,
    token_digest: str = TOKEN_DIGEST,
    issued_at: datetime = ISSUED,
    expires_at: datetime = EXPIRES,
) -> LegalNotificationContactVerification:
    """Create one canonical synthetic H7A verification."""

    return LegalNotificationContactVerification.issue(
        tenant_id=tenant_id,
        verification_id=verification_id,
        principal_id=principal_id,
        channel=LegalNotificationContactChannel.EMAIL,
        address_digest=ADDRESS_DIGEST,
        token_digest=token_digest,
        issued_at=issued_at,
        expires_at=expires_at,
    )


def test_index_contract_is_exact_and_has_no_ttl() -> None:
    collection = _FakeCollection()
    LegalNotificationContactVerificationRegistry(collection).ensure_indexes()

    assert {entry["name"] for entry in collection.indexes} == {
        IDENTITY_INDEX,
        TOKEN_INDEX,
        PRINCIPAL_SCOPE_INDEX,
    }
    assert len(collection.indexes) == 3

    identity = next(
        entry for entry in collection.indexes
        if entry["name"] == IDENTITY_INDEX
    )
    token = next(
        entry for entry in collection.indexes
        if entry["name"] == TOKEN_INDEX
    )
    principal = next(
        entry for entry in collection.indexes
        if entry["name"] == PRINCIPAL_SCOPE_INDEX
    )

    assert identity["keys"] == (
        ("tenant_id", 1),
        ("verification_id", 1),
    )
    assert identity["unique"] is True

    assert token["keys"] == (
        ("tenant_id", 1),
        ("token_digest", 1),
    )
    assert token["unique"] is True

    assert principal["keys"] == (
        ("tenant_id", 1),
        ("principal_id", 1),
        ("channel", 1),
        ("issued_at", 1),
    )
    assert principal["unique"] is False

    assert all("expireAfterSeconds" not in entry for entry in collection.indexes)


def test_create_is_digest_only_exact_replay_and_forwards_transaction() -> None:
    collection = _FakeCollection()
    registry = LegalNotificationContactVerificationRegistry(collection)
    session = _Session()
    verification = _verification()

    assert registry.create(verification, session=session) == verification
    assert len(collection.rows) == 1

    row = collection.rows[0]
    assert row == verification.to_dict()
    assert row["tenant_id"] == TENANT
    assert row["principal_id"] == PRINCIPAL
    assert row["address_digest"] == ADDRESS_DIGEST
    assert row["token_digest"] == TOKEN_DIGEST
    assert "email" not in row
    assert "address" not in row
    assert "raw_email" not in row
    assert "raw_token" not in row
    assert "token" not in row
    assert collection.calls[-1] == ("insert_one", session)

    assert registry.create(verification, session=session) == verification
    assert len(collection.rows) == 1


def test_divergent_same_identity_replay_fails_closed() -> None:
    collection = _FakeCollection()
    registry = LegalNotificationContactVerificationRegistry(collection)
    session = _Session()

    first = _verification()
    registry.create(first, session=session)

    divergent = _verification(
        token_digest="c" * 128,
    )

    with pytest.raises(
        LegalNotificationContactVerificationRegistryConflictError
    ) as captured:
        registry.create(divergent, session=session)

    assert captured.value.code == "L8_8H7C_DIVERGENT_REPLAY"


def test_duplicate_race_requires_whole_transaction_retry() -> None:
    class _RaceCollection(_FakeCollection):
        def find_one(self, query, *, session=None):
            self.calls.append(("find_one", session))
            return None

        def insert_one(self, document, *, session=None):
            del document
            self.calls.append(("insert_one", session))
            raise DuplicateKeyError("race")

    registry = LegalNotificationContactVerificationRegistry(_RaceCollection())

    with pytest.raises(
        LegalNotificationContactVerificationRegistryRetryTransactionError
    ) as captured:
        registry.create(_verification(), session=_Session())

    assert (
        captured.value.code
        == "L8_8H7C_DUPLICATE_RACE_RETRY_TRANSACTION"
    )


def test_reads_are_exact_tenant_scoped_and_token_scoped() -> None:
    collection = _FakeCollection()
    registry = LegalNotificationContactVerificationRegistry(collection)
    session = _Session()
    verification = _verification()

    registry.create(verification, session=session)

    assert registry.get_by_id(
        TENANT,
        verification.verification_id,
        session=session,
    ) == verification

    assert registry.get_by_id(
        OTHER_TENANT,
        verification.verification_id,
        session=session,
    ) is None

    assert registry.get_by_token_digest(
        TENANT,
        TOKEN_DIGEST,
        session=session,
    ) == verification

    assert registry.get_by_token_digest(
        OTHER_TENANT,
        TOKEN_DIGEST,
        session=session,
    ) is None


def test_principal_scope_is_exact_and_oldest_first() -> None:
    collection = _FakeCollection()
    registry = LegalNotificationContactVerificationRegistry(collection)
    session = _Session()

    second = _verification(
        verification_id="legal-verification-2",
        token_digest="c" * 128,
        issued_at=ISSUED + timedelta(seconds=2),
        expires_at=EXPIRES + timedelta(seconds=2),
    )
    first = _verification()

    registry.create(second, session=session)
    registry.create(first, session=session)

    assert registry.list_principal_scope(
        TENANT,
        PRINCIPAL,
        LegalNotificationContactChannel.EMAIL,
        session=session,
    ) == (first, second)

    assert registry.list_principal_scope(
        OTHER_TENANT,
        PRINCIPAL,
        LegalNotificationContactChannel.EMAIL,
        session=session,
    ) == ()


def test_microseconds_survive_persistence_round_trip_exactly() -> None:
    collection = _FakeCollection()
    registry = LegalNotificationContactVerificationRegistry(collection)
    session = _Session()
    verification = _verification()

    registry.create(verification, session=session)

    hydrated = registry.get_by_id(
        TENANT,
        verification.verification_id,
        session=session,
    )

    assert hydrated is not None
    assert hydrated == verification
    assert hydrated.issued_at.microsecond == 654321
    assert hydrated.expires_at.microsecond == EXPIRES.microsecond
    assert collection.rows[0]["issued_at"] == verification.to_dict()["issued_at"]
    assert collection.rows[0]["expires_at"] == verification.to_dict()["expires_at"]


def test_active_transaction_is_required_for_operational_methods() -> None:
    collection = _FakeCollection()
    registry = LegalNotificationContactVerificationRegistry(collection)
    inactive = _Session(active=False)
    verification = _verification()

    operations = (
        lambda: registry.create(verification, session=inactive),
        lambda: registry.get_by_id(
            TENANT,
            verification.verification_id,
            session=inactive,
        ),
        lambda: registry.get_by_token_digest(
            TENANT,
            TOKEN_DIGEST,
            session=inactive,
        ),
        lambda: registry.list_principal_scope(
            TENANT,
            PRINCIPAL,
            LegalNotificationContactChannel.EMAIL,
            session=inactive,
        ),
        lambda: registry.consume(
            verification,
            ISSUED + timedelta(minutes=1),
            session=inactive,
        ),
    )

    for operation in operations:
        with pytest.raises(
            LegalNotificationContactVerificationRegistryTransactionRequiredError
        ) as captured:
            operation()
        assert captured.value.code == "L8_8H7C_ACTIVE_TRANSACTION_REQUIRED"


def test_consume_is_atomic_and_exact_transition_replay_is_idempotent() -> None:
    collection = _FakeCollection()
    registry = LegalNotificationContactVerificationRegistry(collection)
    session = _Session()
    verification = _verification()

    registry.create(verification, session=session)
    consumed_at = ISSUED + timedelta(minutes=1, microseconds=123456)

    consumed = registry.consume(
        verification,
        consumed_at,
        session=session,
    )

    assert consumed.status is LegalNotificationContactVerificationStatus.CONSUMED
    assert consumed.consumed_at == consumed_at
    assert consumed.fingerprint != verification.fingerprint

    replay = registry.consume(
        verification,
        consumed_at,
        session=session,
    )
    assert replay == consumed

    with pytest.raises(
        LegalNotificationContactVerificationRegistryConflictError
    ) as captured:
        registry.consume(
            verification,
            consumed_at + timedelta(microseconds=1),
            session=session,
        )

    assert captured.value.code == "L8_8H7C_STALE_SOURCE_CONFLICT"


def test_revoke_and_expire_are_atomic_terminal_transitions() -> None:
    session = _Session()

    revoke_collection = _FakeCollection()
    revoke_registry = LegalNotificationContactVerificationRegistry(
        revoke_collection
    )
    revoking = _verification()
    revoke_registry.create(revoking, session=session)

    revoked_at = ISSUED + timedelta(minutes=2)
    revoked = revoke_registry.revoke(
        revoking,
        revoked_at,
        session=session,
    )

    assert revoked.status is LegalNotificationContactVerificationStatus.REVOKED
    assert revoked.revoked_at == revoked_at

    expire_collection = _FakeCollection()
    expire_registry = LegalNotificationContactVerificationRegistry(
        expire_collection
    )
    expiring = _verification(
        verification_id="legal-verification-expire",
        token_digest="d" * 128,
    )
    expire_registry.create(expiring, session=session)

    expired = expire_registry.expire(
        expiring,
        EXPIRES,
        session=session,
    )

    assert expired.status is LegalNotificationContactVerificationStatus.EXPIRED
    assert expired.expired_at == EXPIRES


def test_persisted_corruption_is_rejected_on_hydration() -> None:
    collection = _FakeCollection()
    registry = LegalNotificationContactVerificationRegistry(collection)
    session = _Session()
    verification = _verification()

    registry.create(verification, session=session)
    collection.rows[0]["principal_id"] = "corrupt-principal"

    with pytest.raises(
        LegalNotificationContactVerificationRegistryPersistedRecordInvalidError
    ) as captured:
        registry.get_by_id(
            TENANT,
            verification.verification_id,
            session=session,
        )

    assert captured.value.code == "L8_8H7C_PERSISTED_RECORD_INVALID"


def test_transition_result_corruption_is_rejected() -> None:
    class _CorruptTransitionCollection(_FakeCollection):
        def find_one_and_replace(
            self,
            query,
            replacement,
            *,
            return_document=None,
            session=None,
        ):
            row = super().find_one_and_replace(
                query,
                replacement,
                return_document=return_document,
                session=session,
            )
            if row is not None:
                row["principal_id"] = "corrupt-principal"
            return row

    collection = _CorruptTransitionCollection()
    registry = LegalNotificationContactVerificationRegistry(collection)
    session = _Session()
    verification = _verification()

    registry.create(verification, session=session)

    with pytest.raises(
        LegalNotificationContactVerificationRegistryPersistedRecordInvalidError
    ) as captured:
        registry.consume(
            verification,
            ISSUED + timedelta(minutes=1),
            session=session,
        )

    assert captured.value.code == "L8_8H7C_PERSISTED_RECORD_INVALID"


def test_missing_after_failed_cas_is_not_found_conflict() -> None:
    collection = _FakeCollection()
    registry = LegalNotificationContactVerificationRegistry(collection)
    session = _Session()
    verification = _verification()

    with pytest.raises(
        LegalNotificationContactVerificationRegistryConflictError
    ) as captured:
        registry.consume(
            verification,
            ISSUED + timedelta(minutes=1),
            session=session,
        )

    assert captured.value.code == "L8_8H7C_VERIFICATION_NOT_FOUND"


def test_index_read_write_and_transition_failures_are_stable() -> None:
    index_collection = _FakeCollection()
    index_collection.fail_indexes = True

    with pytest.raises(
        LegalNotificationContactVerificationRegistryPersistenceError
    ) as captured:
        LegalNotificationContactVerificationRegistry(
            index_collection
        ).ensure_indexes()
    assert captured.value.code == "L8_8H7C_INDEX_PERSISTENCE_FAILURE"

    read_collection = _FakeCollection()
    read_collection.fail_read = True
    read_registry = LegalNotificationContactVerificationRegistry(
        read_collection
    )

    with pytest.raises(
        LegalNotificationContactVerificationRegistryPersistenceError
    ) as captured:
        read_registry.get_by_id(
            TENANT,
            "legal-verification-1",
            session=_Session(),
        )
    assert captured.value.code == "L8_8H7C_READ_PERSISTENCE_FAILURE"

    insert_collection = _FakeCollection()
    insert_collection.fail_insert = True
    insert_registry = LegalNotificationContactVerificationRegistry(
        insert_collection
    )

    with pytest.raises(
        LegalNotificationContactVerificationRegistryPersistenceError
    ) as captured:
        insert_registry.create(
            _verification(),
            session=_Session(),
        )
    assert captured.value.code == "L8_8H7C_WRITE_PERSISTENCE_FAILURE"

    replace_collection = _FakeCollection()
    replace_registry = LegalNotificationContactVerificationRegistry(
        replace_collection
    )
    session = _Session()
    verification = _verification()
    replace_registry.create(verification, session=session)
    replace_collection.fail_replace = True

    with pytest.raises(
        LegalNotificationContactVerificationRegistryPersistenceError
    ) as captured:
        replace_registry.consume(
            verification,
            ISSUED + timedelta(minutes=1),
            session=session,
        )
    assert captured.value.code == "L8_8H7C_TRANSITION_PERSISTENCE_FAILURE"


def test_every_operational_database_call_forwards_exact_session() -> None:
    collection = _FakeCollection()
    registry = LegalNotificationContactVerificationRegistry(collection)
    session = _Session()
    verification = _verification()

    registry.create(verification, session=session)
    registry.get_by_id(
        TENANT,
        verification.verification_id,
        session=session,
    )
    registry.get_by_token_digest(
        TENANT,
        TOKEN_DIGEST,
        session=session,
    )
    registry.list_principal_scope(
        TENANT,
        PRINCIPAL,
        LegalNotificationContactChannel.EMAIL,
        session=session,
    )
    registry.consume(
        verification,
        ISSUED + timedelta(minutes=1),
        session=session,
    )

    forwarded = [
        forwarded_session
        for operation, forwarded_session in collection.calls
        if operation
        in {
            "find_one",
            "find",
            "insert_one",
            "find_one_and_replace",
        }
    ]

    assert forwarded
    assert all(forwarded_session is session for forwarded_session in forwarded)


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_legal_notification_contact_verification_registry.py
# VERSION: v1.0.0-L8-8H7C-LEGAL-NOTIFICATION-CONTACT-VERIFICATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: deterministic H7C registry test evidence only
# TENANT POSTURE: exact tenant predicates and active caller transaction required
# FAIL-CLOSED POSTURE: replay, corruption, stale CAS, race and persistence fail
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
