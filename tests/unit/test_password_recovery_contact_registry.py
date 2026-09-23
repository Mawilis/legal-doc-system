"""Direct certificate for the WILSY OS verified recovery-contact registry.

TITLE: WILSY OS Verified Recovery Contact Registry Direct Certificate
VERSION: v1.0.1-R10E50-VERIFIED-RECOVERY-CONTACT-REGISTRY-CORRUPTION-CLOSURE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies digest-only tenant/principal recovery-contact persistence,
         single-ACTIVE authority, exact lookup, caller-session forwarding,
         corruption rejection, and atomic revocation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_password_recovery_contact_registry.py
COLLABORATION / OWNERSHIP: Exercises password_recovery_contact_registry.py
                           against one deterministic PyMongo-shaped fake.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG: v1.0.1-R10E50-VERIFIED-RECOVERY-CONTACT-REGISTRY-CORRUPTION-CLOSURE introduces
           direct evidence for indexes, insert-only creation, single ACTIVE
           principal/address constraints, tenant isolation, exact ACTIVE reads,
           session propagation, durable revocation, replay/conflict handling,
           corruption rejection, and persistence failures.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic SHA3-512 digests only; no raw addresses.
TENANT BOUNDARY: Every read/mutation remains exactly tenant-scoped.
AUTHORITY BOUNDARY: Persistence test evidence only; no address verification,
                    token issuance, reset, delivery, JWT, session, or MFA.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import hashlib
from copy import deepcopy
from datetime import datetime, timedelta, timezone

import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.saas.auth.password_recovery_contact import (
    VerifiedRecoveryContact,
    VerifiedRecoveryContactChannel,
    VerifiedRecoveryContactStatus,
)
from tools.eos.saas.auth.password_recovery_contact_registry import (
    VerifiedRecoveryContactAlreadyExistsError,
    VerifiedRecoveryContactLifecycleConflictError,
    VerifiedRecoveryContactNotFoundError,
    VerifiedRecoveryContactPersistedRecordInvalidError,
    VerifiedRecoveryContactPersistenceError,
    VerifiedRecoveryContactRegistry,
)

TENANT = "WILSY-TENANT-CONTACT-CERT"
PRINCIPAL = "WILSY-PRINCIPAL-CONTACT-CERT"
DIGEST = hashlib.sha3_512(b"verified.user@example.com").hexdigest()
VERIFIED_AT = datetime(2026, 9, 22, 17, 0, tzinfo=timezone.utc)


def _contact(
    *,
    contact_id: str = "WILSYCONTACT-CERT-1",
    tenant_id: str = TENANT,
    principal_id: str = PRINCIPAL,
    digest: str = DIGEST,
) -> VerifiedRecoveryContact:
    return VerifiedRecoveryContact.issue(
        contact_id=contact_id,
        tenant_id=tenant_id,
        principal_id=principal_id,
        channel=VerifiedRecoveryContactChannel.EMAIL,
        address_digest=digest,
        verified_at=VERIFIED_AT,
    )


class _FakeCollection:
    """Small deterministic collection implementing the registry's used surface."""

    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []
        self.indexes: list[tuple[list[tuple[str, int]], dict[str, object]]] = []
        self.fail_indexes = False
        self.fail_insert = False
        self.fail_read = False
        self.fail_update = False
        self.calls: list[tuple[str, object | None]] = []

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
        for row in self.rows:
            same_identity = row.get("contact_id") == incoming.get("contact_id")
            same_active_address = (
                row.get("tenant_id") == incoming.get("tenant_id")
                and row.get("channel") == incoming.get("channel")
                and row.get("address_digest") == incoming.get("address_digest")
                and row.get("status") == "ACTIVE"
                and incoming.get("status") == "ACTIVE"
            )
            same_active_principal = (
                row.get("tenant_id") == incoming.get("tenant_id")
                and row.get("principal_id") == incoming.get("principal_id")
                and row.get("channel") == incoming.get("channel")
                and row.get("status") == "ACTIVE"
                and incoming.get("status") == "ACTIVE"
            )
            if same_identity or same_active_address or same_active_principal:
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


def test_indexes_enforce_single_active_address_and_principal() -> None:
    collection = _FakeCollection()
    VerifiedRecoveryContactRegistry(collection).ensure_indexes()

    assert [options["name"] for _, options in collection.indexes] == [
        "verified_recovery_contact_identity_unique",
        "verified_recovery_contact_active_address_unique",
        "verified_recovery_contact_active_principal_unique",
        "verified_recovery_contact_tenant_principal_status",
    ]
    assert collection.indexes[1][1]["unique"] is True
    assert collection.indexes[1][1]["partialFilterExpression"] == {"status": "ACTIVE"}
    assert collection.indexes[2][1]["unique"] is True
    assert collection.indexes[2][1]["partialFilterExpression"] == {"status": "ACTIVE"}


def test_create_persists_digest_only_active_contact_and_forwards_session() -> None:
    collection = _FakeCollection()
    registry = VerifiedRecoveryContactRegistry(collection)
    session = object()
    contact = _contact()

    returned = registry.create(contact, session=session)

    assert returned is contact
    assert len(collection.rows) == 1
    row = collection.rows[0]
    assert row["tenant_id"] == TENANT
    assert row["principal_id"] == PRINCIPAL
    assert row["address_digest"] == DIGEST
    assert row["status"] == "ACTIVE"
    assert "email" not in row
    assert "address" not in row
    assert collection.calls[-1] == ("insert", session)


def test_duplicate_identity_active_address_and_active_principal_fail_closed() -> None:
    collection = _FakeCollection()
    registry = VerifiedRecoveryContactRegistry(collection)
    registry.create(_contact())

    with pytest.raises(VerifiedRecoveryContactAlreadyExistsError) as identity_error:
        registry.create(_contact())
    assert identity_error.value.code == "RECOVERY_CONTACT_ID_DUPLICATE"

    other_principal = _contact(
        contact_id="WILSYCONTACT-CERT-2",
        principal_id="OTHER-PRINCIPAL",
    )
    with pytest.raises(VerifiedRecoveryContactAlreadyExistsError) as address_error:
        registry.create(other_principal)
    assert address_error.value.code == "RECOVERY_CONTACT_ACTIVE_ADDRESS_DUPLICATE"

    other_digest = hashlib.sha3_512(b"other@example.com").hexdigest()
    same_principal = _contact(
        contact_id="WILSYCONTACT-CERT-3",
        digest=other_digest,
    )
    with pytest.raises(VerifiedRecoveryContactAlreadyExistsError) as principal_error:
        registry.create(same_principal)
    assert principal_error.value.code == "RECOVERY_CONTACT_DUPLICATE_CONFLICT"


def test_active_lookup_by_digest_and_principal_is_tenant_scoped() -> None:
    collection = _FakeCollection()
    registry = VerifiedRecoveryContactRegistry(collection)
    contact = _contact()
    registry.create(contact)

    by_digest = registry.get_active_by_address_digest(
        tenant_id=TENANT,
        channel=VerifiedRecoveryContactChannel.EMAIL,
        address_digest=DIGEST,
    )
    by_principal = registry.get_active_by_principal(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
    )

    assert by_digest == contact
    assert by_principal == contact
    assert registry.get_active_by_address_digest(
        tenant_id="OTHER-TENANT",
        channel=VerifiedRecoveryContactChannel.EMAIL,
        address_digest=DIGEST,
    ) is None
    assert registry.get_active_by_principal(
        tenant_id="OTHER-TENANT",
        principal_id=PRINCIPAL,
    ) is None


def test_lookup_rejects_malformed_selector_without_broadening() -> None:
    registry = VerifiedRecoveryContactRegistry(_FakeCollection())

    with pytest.raises(VerifiedRecoveryContactNotFoundError) as tenant_error:
        registry.get_active_by_address_digest(
            tenant_id=" tenant",
            channel=VerifiedRecoveryContactChannel.EMAIL,
            address_digest=DIGEST,
        )
    assert tenant_error.value.code == "RECOVERY_CONTACT_NOT_FOUND"

    with pytest.raises(VerifiedRecoveryContactNotFoundError) as digest_error:
        registry.get_active_by_address_digest(
            tenant_id=TENANT,
            channel=VerifiedRecoveryContactChannel.EMAIL,
            address_digest="0" * 127,
        )
    assert digest_error.value.code == "RECOVERY_CONTACT_NOT_FOUND"


def test_revoke_is_exact_atomic_and_allows_new_active_replacement() -> None:
    collection = _FakeCollection()
    registry = VerifiedRecoveryContactRegistry(collection)
    contact = _contact()
    registry.create(contact)
    revoked_at = VERIFIED_AT + timedelta(hours=1)

    revoked = registry.revoke(contact, revoked_at)

    assert revoked.status is VerifiedRecoveryContactStatus.REVOKED
    assert revoked.revoked_at == revoked_at
    assert registry.get_active_by_principal(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
    ) is None

    replacement_digest = hashlib.sha3_512(b"replacement@example.com").hexdigest()
    replacement = _contact(
        contact_id="WILSYCONTACT-CERT-REPLACEMENT",
        digest=replacement_digest,
    )
    assert registry.create(replacement) == replacement
    assert registry.get_active_by_principal(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
    ) == replacement


def test_second_revoke_is_lifecycle_conflict_not_replay_success() -> None:
    collection = _FakeCollection()
    registry = VerifiedRecoveryContactRegistry(collection)
    contact = _contact()
    registry.create(contact)
    revoked_at = VERIFIED_AT + timedelta(hours=1)
    registry.revoke(contact, revoked_at)

    with pytest.raises(VerifiedRecoveryContactLifecycleConflictError) as captured:
        registry.revoke(contact, revoked_at + timedelta(minutes=1))

    assert captured.value.code == "RECOVERY_CONTACT_REVOKED"


def test_corrupt_persisted_state_is_rejected() -> None:
    collection = _FakeCollection()
    contact = _contact()
    row = contact.to_document()
    row["schema"] = "CORRUPT-SCHEMA"
    collection.rows.append(row)

    with pytest.raises(VerifiedRecoveryContactPersistedRecordInvalidError) as captured:
        VerifiedRecoveryContactRegistry(collection).get_active_by_address_digest(
            tenant_id=TENANT,
            channel=VerifiedRecoveryContactChannel.EMAIL,
            address_digest=DIGEST,
        )

    assert captured.value.code == "RECOVERY_CONTACT_PERSISTED_RECORD_INVALID"


def test_session_is_forwarded_to_reads_and_revocation() -> None:
    collection = _FakeCollection()
    registry = VerifiedRecoveryContactRegistry(collection)
    session = object()
    contact = _contact()
    registry.create(contact, session=session)

    assert registry.get_active_by_principal(
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        session=session,
    ) == contact
    registry.revoke(
        contact,
        VERIFIED_AT + timedelta(minutes=5),
        session=session,
    )

    session_calls = [value for _, value in collection.calls if value is not None]
    assert session_calls
    assert all(value is session for value in session_calls)


def test_index_insert_read_and_update_failures_are_stable() -> None:
    index_collection = _FakeCollection()
    index_collection.fail_indexes = True
    with pytest.raises(VerifiedRecoveryContactPersistenceError) as index_error:
        VerifiedRecoveryContactRegistry(index_collection).ensure_indexes()
    assert index_error.value.code == "RECOVERY_CONTACT_INDEX_CREATION_FAILED"

    insert_collection = _FakeCollection()
    insert_collection.fail_insert = True
    with pytest.raises(VerifiedRecoveryContactPersistenceError) as insert_error:
        VerifiedRecoveryContactRegistry(insert_collection).create(_contact())
    assert insert_error.value.code == "RECOVERY_CONTACT_CREATE_FAILED"

    read_collection = _FakeCollection()
    read_collection.fail_read = True
    with pytest.raises(VerifiedRecoveryContactPersistenceError) as read_error:
        VerifiedRecoveryContactRegistry(read_collection).get_active_by_principal(
            tenant_id=TENANT,
            principal_id=PRINCIPAL,
        )
    assert read_error.value.code == "RECOVERY_CONTACT_READ_FAILED"

    update_collection = _FakeCollection()
    update_registry = VerifiedRecoveryContactRegistry(update_collection)
    contact = _contact()
    update_registry.create(contact)
    update_collection.fail_update = True
    with pytest.raises(VerifiedRecoveryContactPersistenceError) as update_error:
        update_registry.revoke(
            contact,
            VERIFIED_AT + timedelta(minutes=1),
        )
    assert update_error.value.code == "RECOVERY_CONTACT_REVOKE_FAILED"


# =============================================================================
# SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: test_password_recovery_contact_registry.py
# VERSION: v1.0.1-R10E50-VERIFIED-RECOVERY-CONTACT-REGISTRY-CORRUPTION-CLOSURE
# AUTHORITY BOUNDARY: deterministic persistence test evidence only
# TENANT POSTURE: exact tenant/digest/principal isolation certified
# FAIL-CLOSED POSTURE: duplicate, corrupt, replayed, and persistence failure reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
