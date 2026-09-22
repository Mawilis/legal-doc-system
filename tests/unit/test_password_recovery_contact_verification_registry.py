"""Direct certificate for WILSY OS recovery-contact verification persistence.

TITLE: WILSY OS Recovery Contact Verification Registry Direct Certificate
VERSION: v1.0.0-R10E31-RECOVERY-CONTACT-VERIFICATION-REGISTRY-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies digest-only verification persistence, uniqueness, exact
         tenant/token lookup, caller-session propagation, lifecycle CAS,
         replay rejection, and persisted-time integrity.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_recovery_contact_verification_registry.py
COLLABORATION / OWNERSHIP: Exercises the R10E16 registry against one deterministic
                           PyMongo-shaped fake; no real Mongo or network.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.0-R10E31-RECOVERY-CONTACT-VERIFICATION-REGISTRY-CERT introduces
           direct evidence for indexes, insert-only uniqueness, tenant/token
           lookup, session forwarding, consume/revoke/expire compare-and-set,
           replay/expiry conflicts, metadata corruption rejection, and stable
           persistence failures.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic digests only; raw email/token excluded.
TENANT BOUNDARY: Every lookup and transition remains exact-tenant scoped.
AUTHORITY BOUNDARY: Persistence test evidence only; no contact creation,
                    password reset, delivery, session, JWT, MFA, or HTTP authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.auth.password_recovery_contact_verification import (
    RecoveryContactVerification,
    RecoveryContactVerificationStatus,
)
from tools.eos.saas.auth.password_recovery_contact_verification_registry import (
    INDEX_DEFINITIONS,
    RecoveryContactVerificationAlreadyExistsError,
    RecoveryContactVerificationLifecycleConflictError,
    RecoveryContactVerificationNotFoundError,
    RecoveryContactVerificationPersistedRecordInvalidError,
    RecoveryContactVerificationPersistenceError,
    RecoveryContactVerificationRegistry,
)

TENANT = "WILSY-TENANT-VERIFY-REG-CERT"
PRINCIPAL = "WILSY-PRINCIPAL-VERIFY-REG-CERT"
ISSUED = datetime(2026, 9, 22, 18, 0, tzinfo=timezone.utc)
EXPIRES = ISSUED + timedelta(minutes=30)
ADDRESS_DIGEST = hashlib.sha3_512(b"verified.user@example.com").hexdigest()
TOKEN_DIGEST = hashlib.sha3_512(b"verification-token").hexdigest()


def _verification(
    *,
    verification_id: str = "WILSYVERIFY-REG-CERT-1",
    token_digest: str = TOKEN_DIGEST,
    tenant_id: str = TENANT,
) -> RecoveryContactVerification:
    return RecoveryContactVerification.issue(
        verification_id=verification_id,
        tenant_id=tenant_id,
        principal_id=PRINCIPAL,
        address_digest=ADDRESS_DIGEST,
        token_digest=token_digest,
        issued_at=ISSUED,
        expires_at=EXPIRES,
    )


class _FakeCollection:
    """Deterministic subset of the PyMongo collection API used by R10E16."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, object]]] = []
        self.calls: list[tuple[str, object | None]] = []
        self.fail_indexes = False
        self.fail_insert = False
        self.fail_read = False
        self.fail_update = False

    @staticmethod
    def _matches(row: dict[str, object], query: dict[str, object]) -> bool:
        for key, expected in query.items():
            actual = row.get(key)
            if isinstance(expected, dict):
                if "$gt" in expected and not (actual is not None and actual > expected["$gt"]):
                    return False
                if "$lte" in expected and not (actual is not None and actual <= expected["$lte"]):
                    return False
            elif actual != expected:
                return False
        return True

    def create_index(self, keys, **kwargs):
        if self.fail_indexes:
            raise PyMongoError("index failure")
        self.indexes.append((list(keys), dict(kwargs)))
        return kwargs.get("name")

    def insert_one(self, document, **kwargs):
        if self.fail_insert:
            raise PyMongoError("insert failure")
        self.calls.append(("insert", kwargs.get("session")))
        incoming = deepcopy(document)
        for row in self.rows:
            if row.get("verification_id") == incoming.get("verification_id"):
                raise DuplicateKeyError("verification duplicate")
            if row.get("token_digest") == incoming.get("token_digest"):
                raise DuplicateKeyError("token duplicate")
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


def test_index_contract_matches_exported_definitions() -> None:
    collection = _FakeCollection()
    RecoveryContactVerificationRegistry(collection).ensure_indexes()

    expected = [
        (list(keys), {"unique": unique, "name": name})
        for keys, unique, name in INDEX_DEFINITIONS
    ]
    assert collection.indexes == expected


def test_create_persists_digest_only_metadata_and_forwards_session() -> None:
    collection = _FakeCollection()
    registry = RecoveryContactVerificationRegistry(collection)
    session = object()
    verification = _verification()

    assert registry.create(verification, session=session) == verification

    assert len(collection.rows) == 1
    row = collection.rows[0]
    assert row["tenant_id"] == TENANT
    assert row["principal_id"] == PRINCIPAL
    assert row["address_digest"] == ADDRESS_DIGEST
    assert row["token_digest"] == TOKEN_DIGEST
    assert row["status"] == "ACTIVE"
    assert isinstance(row["_issued_at_epoch_us"], int)
    assert isinstance(row["_expires_at_epoch_us"], int)
    assert "email" not in row
    assert "raw_token" not in row
    assert collection.calls[-1] == ("insert", session)


def test_duplicate_identity_and_token_are_distinct_conflicts() -> None:
    collection = _FakeCollection()
    registry = RecoveryContactVerificationRegistry(collection)
    registry.create(_verification())

    with pytest.raises(RecoveryContactVerificationAlreadyExistsError) as identity:
        registry.create(_verification())
    assert identity.value.code == "RECOVERY_CONTACT_VERIFICATION_ID_DUPLICATE"

    different_id_same_token = _verification(
        verification_id="WILSYVERIFY-REG-CERT-2"
    )
    with pytest.raises(RecoveryContactVerificationAlreadyExistsError) as token:
        registry.create(different_id_same_token)
    assert token.value.code == "RECOVERY_CONTACT_VERIFICATION_TOKEN_DUPLICATE"


def test_exact_tenant_token_lookup_and_cross_tenant_absence() -> None:
    collection = _FakeCollection()
    registry = RecoveryContactVerificationRegistry(collection)
    verification = _verification()
    registry.create(verification)

    assert registry.get_by_token_digest(
        tenant_id=TENANT,
        token_digest=TOKEN_DIGEST,
    ) == verification
    assert registry.get_by_token_digest(
        tenant_id="OTHER-TENANT",
        token_digest=TOKEN_DIGEST,
    ) is None

    with pytest.raises(RecoveryContactVerificationNotFoundError):
        registry.get_by_token_digest(
            tenant_id=" tenant",
            token_digest=TOKEN_DIGEST,
        )


def test_consume_is_atomic_and_second_consume_is_replay_conflict() -> None:
    collection = _FakeCollection()
    registry = RecoveryContactVerificationRegistry(collection)
    verification = _verification()
    registry.create(verification)
    consumed_at = ISSUED + timedelta(minutes=5)

    consumed = registry.consume(verification, consumed_at)

    assert consumed.status is RecoveryContactVerificationStatus.CONSUMED
    assert consumed.consumed_at == consumed_at

    with pytest.raises(RecoveryContactVerificationLifecycleConflictError) as replay:
        registry.consume(verification, consumed_at + timedelta(seconds=1))
    assert replay.value.code == "RECOVERY_CONTACT_VERIFICATION_CONSUMED"


def test_revoke_and_expire_enforce_correct_time_boundaries() -> None:
    revoke_collection = _FakeCollection()
    revoke_registry = RecoveryContactVerificationRegistry(revoke_collection)
    verification = _verification()
    revoke_registry.create(verification)

    revoked = revoke_registry.revoke(
        verification,
        ISSUED + timedelta(minutes=10),
    )
    assert revoked.status is RecoveryContactVerificationStatus.REVOKED

    expire_collection = _FakeCollection()
    expire_registry = RecoveryContactVerificationRegistry(expire_collection)
    expiring = _verification(verification_id="WILSYVERIFY-REG-EXPIRE")
    expire_registry.create(expiring)

    with pytest.raises(RecoveryContactVerificationLifecycleConflictError) as early:
        expire_registry.expire(expiring, EXPIRES - timedelta(microseconds=1))
    assert early.value.code == "RECOVERY_CONTACT_VERIFICATION_EXPIRY_BOUNDARY_NOT_REACHED"

    expired = expire_registry.expire(expiring, EXPIRES)
    assert expired.status is RecoveryContactVerificationStatus.EXPIRED
    assert expired.expired_at == EXPIRES


def test_corrupt_epoch_metadata_is_rejected() -> None:
    collection = _FakeCollection()
    registry = RecoveryContactVerificationRegistry(collection)
    registry.create(_verification())
    collection.rows[0]["_expires_at_epoch_us"] = 0

    with pytest.raises(RecoveryContactVerificationPersistedRecordInvalidError) as captured:
        registry.get_by_token_digest(
            tenant_id=TENANT,
            token_digest=TOKEN_DIGEST,
        )

    assert captured.value.code == "RECOVERY_CONTACT_VERIFICATION_PERSISTED_RECORD_INVALID"


def test_binding_divergence_after_failed_cas_is_conflict() -> None:
    collection = _FakeCollection()
    registry = RecoveryContactVerificationRegistry(collection)
    verification = _verification()
    registry.create(verification)
    collection.rows[0]["principal_id"] = "OTHER-PRINCIPAL"

    with pytest.raises(RecoveryContactVerificationLifecycleConflictError) as captured:
        registry.consume(
            verification,
            ISSUED + timedelta(minutes=1),
        )

    assert captured.value.code == "RECOVERY_CONTACT_VERIFICATION_BINDING_CONFLICT"


def test_session_is_forwarded_to_create_lookup_and_transition() -> None:
    collection = _FakeCollection()
    registry = RecoveryContactVerificationRegistry(collection)
    session = object()
    verification = _verification()
    registry.create(verification, session=session)

    assert registry.get_by_token_digest(
        tenant_id=TENANT,
        token_digest=TOKEN_DIGEST,
        session=session,
    ) == verification

    registry.consume(
        verification,
        ISSUED + timedelta(minutes=1),
        session=session,
    )

    forwarded = [value for _, value in collection.calls if value is not None]
    assert forwarded
    assert all(value is session for value in forwarded)


def test_index_insert_read_and_update_failures_are_stable() -> None:
    index_collection = _FakeCollection()
    index_collection.fail_indexes = True
    with pytest.raises(RecoveryContactVerificationPersistenceError) as index_error:
        RecoveryContactVerificationRegistry(index_collection).ensure_indexes()
    assert index_error.value.code == "RECOVERY_CONTACT_VERIFICATION_INDEX_CREATION_FAILED"

    insert_collection = _FakeCollection()
    insert_collection.fail_insert = True
    with pytest.raises(RecoveryContactVerificationPersistenceError) as insert_error:
        RecoveryContactVerificationRegistry(insert_collection).create(_verification())
    assert insert_error.value.code == "RECOVERY_CONTACT_VERIFICATION_CREATE_FAILED"

    read_collection = _FakeCollection()
    read_collection.fail_read = True
    with pytest.raises(RecoveryContactVerificationPersistenceError) as read_error:
        RecoveryContactVerificationRegistry(read_collection).get_by_token_digest(
            tenant_id=TENANT,
            token_digest=TOKEN_DIGEST,
        )
    assert read_error.value.code == "RECOVERY_CONTACT_VERIFICATION_READ_FAILED"

    update_collection = _FakeCollection()
    update_registry = RecoveryContactVerificationRegistry(update_collection)
    verification = _verification()
    update_registry.create(verification)
    update_collection.fail_update = True
    with pytest.raises(RecoveryContactVerificationPersistenceError) as update_error:
        update_registry.consume(
            verification,
            ISSUED + timedelta(minutes=1),
        )
    assert update_error.value.code == "RECOVERY_CONTACT_VERIFICATION_TRANSITION_FAILED"


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_password_recovery_contact_verification_registry.py
# VERSION: v1.0.0-R10E31-RECOVERY-CONTACT-VERIFICATION-REGISTRY-CERT
# AUTHORITY BOUNDARY: deterministic verification-persistence test evidence only
# TENANT POSTURE: exact tenant/token binding and caller-session propagation
# FAIL-CLOSED POSTURE: duplicate, replayed, expired, corrupt, divergent state rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
