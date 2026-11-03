"""Unit tests for tenant-neutral global principal credential persistence."""
import pytest
from typing import cast, Mapping
from pymongo.client_session import ClientSession
from pymongo.collection import Collection as MongoCollection
from pymongo.errors import DuplicateKeyError

from tools.eos.auth.principal_credential import PrincipalCredential, normalize_principal_email
from tools.eos.auth.principal_credential_repository import (
    PrincipalCredentialAlreadyExistsError,
    PrincipalCredentialNotFoundError,
    PrincipalCredentialPersistedRecordInvalidError,
    PrincipalCredentialRepository,
    PrincipalCredentialRepositoryError,
    PrincipalCredentialRevisionConflictError,
    PrincipalCredentialMfaStateConflictError,
)

HASH_A = "$2b$12$" + "a" * 53
HASH_B = "$2b$12$" + "b" * 53


class Result:
    def __init__(self, matched_count=1):
        self.matched_count = matched_count


class Cursor:
    def __init__(self, rows):
        self.rows = rows
    def limit(self, count):
        self.rows = self.rows[:count]
        return self
    def __iter__(self):
        return iter(self.rows)


class Collection:
    def __init__(self):
        self.rows = []
        self.session = None
        self.indexes = []

    def create_index(self, keys, **kwargs):
        self.indexes.append((keys, kwargs))
        return kwargs.get("name")

    def insert_one(self, document, session=None):
        self.session = session
        if any(row["principal_id"] == document["principal_id"] or row["normalized_email"] == document["normalized_email"] for row in self.rows):
            raise DuplicateKeyError("duplicate")
        self.rows.append(dict(document))

    def find_one(self, query, session=None):
        self.session = session
        return next((dict(row) for row in self.rows if all(row.get(key) == value for key, value in query.items())), None)

    def find(self, query, session=None):
        self.session = session
        return Cursor([
            dict(row) for row in self.rows
            if all(row.get(key) == value for key, value in query.items())
        ])

    def update_one(self, query, update, upsert=False, session=None):
        self.session = session
        for row in self.rows:
            if all(row.get(key) == value for key, value in query.items()):
                row.update(update["$set"])
                for key, value in update["$inc"].items():
                    row[key] = row.get(key, 0) + value
                return Result(1)
        return Result(0)


def credential(principal="principal-1", email="Owner@Example.com", password_hash=HASH_A, revision=0, mfa_enabled=True):
    return PrincipalCredential(
        principal_id=principal,
        normalized_email=normalize_principal_email(email),
        password_hash=password_hash,
        credential_revision=revision,
        mfa_enabled=mfa_enabled,
    )


def collection(value):
    return cast(MongoCollection[Mapping[str, object]], value)


def test_global_credential_has_no_tenant_membership_or_role_fields():
    value = credential()
    assert value.normalized_email == "owner@example.com"
    assert set(value.__dataclass_fields__) == {
        "principal_id", "normalized_email", "password_hash", "credential_revision", "mfa_enabled"
    }
    assert "tenant_id" not in value.__dataclass_fields__
    assert "business_role" not in value.__dataclass_fields__
    assert "permissions" not in value.__dataclass_fields__


def test_unique_principal_and_email_indexes_and_exact_lookups():
    fake = Collection()
    PrincipalCredentialRepository.ensure_indexes(collection(fake))
    assert [item[1]["name"] for item in fake.indexes] == [
        "principal_credential_principal_unique",
        "principal_credential_email_unique",
    ]
    value = credential()
    PrincipalCredentialRepository.insert(value, collection(fake))
    assert PrincipalCredentialRepository.get_by_principal("principal-1", collection(fake)) == value
    assert PrincipalCredentialRepository.get_by_email("OWNER@example.com", collection(fake)) == value
    with pytest.raises(PrincipalCredentialAlreadyExistsError):
        PrincipalCredentialRepository.insert(value, collection(fake))
    with pytest.raises(PrincipalCredentialNotFoundError):
        PrincipalCredentialRepository.get_by_email("unknown@example.com", collection(fake))


def test_duplicate_email_across_distinct_principals_is_rejected():
    fake = Collection()
    PrincipalCredentialRepository.insert(credential(), collection(fake))
    with pytest.raises(PrincipalCredentialAlreadyExistsError):
        PrincipalCredentialRepository.insert(
            credential(principal="principal-2", email="owner@example.com"),
            collection(fake),
        )


def test_password_hash_revision_compare_and_swap_is_exact_and_monotonic():
    fake = Collection()
    PrincipalCredentialRepository.insert(credential(), collection(fake))
    updated = PrincipalCredentialRepository.compare_and_swap_password_hash(
        "principal-1", 0, HASH_B, collection(fake)
    )
    assert updated.password_hash == HASH_B
    assert updated.credential_revision == 1
    with pytest.raises(PrincipalCredentialRevisionConflictError):
        PrincipalCredentialRepository.compare_and_swap_password_hash(
            "principal-1", 0, HASH_A, collection(fake)
        )



def test_mfa_enablement_is_one_time_and_advances_credential_revision():
    fake = Collection()
    PrincipalCredentialRepository.insert(
        credential(mfa_enabled=False), collection(fake)
    )
    updated = PrincipalCredentialRepository.enable_mfa(
        "principal-1", 0, collection(fake)
    )
    assert updated.mfa_enabled is True
    assert updated.credential_revision == 1
    with pytest.raises(PrincipalCredentialMfaStateConflictError):
        PrincipalCredentialRepository.enable_mfa(
            "principal-1", 1, collection(fake)
        )


def test_invalid_hash_and_malformed_persisted_credential_fail_closed():
    fake = Collection()
    with pytest.raises(PrincipalCredentialRepositoryError):
        PrincipalCredentialRepository.compare_and_swap_password_hash(
            "principal-1", 0, "not-a-bcrypt-hash", collection(fake)
        )
    fake.rows.append({
        "principal_id": "principal-1",
        "normalized_email": "owner@example.com",
        "password_hash": "invalid",
        "credential_revision": 0,
        "mfa_enabled": True,
    })
    with pytest.raises(PrincipalCredentialPersistedRecordInvalidError):
        PrincipalCredentialRepository.get_by_principal("principal-1", collection(fake))


def test_repository_forwards_caller_session_without_owning_transaction():
    fake = Collection()
    token = cast(ClientSession, object())
    PrincipalCredentialRepository.insert(credential(), collection(fake), session=token)
    assert fake.session is token
    assert PrincipalCredentialRepository.get_by_email(
        "owner@example.com", collection(fake), session=token
    ) == credential()
    assert fake.session is token


def test_duplicate_persisted_principal_or_email_rows_fail_closed():
    fake = Collection()
    row = {
        "principal_id": "principal-1",
        "normalized_email": "owner@example.com",
        "password_hash": HASH_A,
        "credential_revision": 0,
    }
    fake.rows.extend([dict(row), dict(row)])
    with pytest.raises(PrincipalCredentialPersistedRecordInvalidError):
        PrincipalCredentialRepository.get_by_principal("principal-1", collection(fake))
    with pytest.raises(PrincipalCredentialPersistedRecordInvalidError):
        PrincipalCredentialRepository.get_by_email("owner@example.com", collection(fake))
