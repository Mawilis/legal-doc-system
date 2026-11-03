"""Real Mongo replica-set certification for global principal credentials."""
import os
import uuid
from concurrent.futures import ThreadPoolExecutor

import pytest
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from tools.eos.auth.principal_credential import PrincipalCredential
from tools.eos.auth.principal_credential_repository import (
    COLLECTION,
    PrincipalCredentialAlreadyExistsError,
    PrincipalCredentialNotFoundError,
    PrincipalCredentialRepository,
    PrincipalCredentialRevisionConflictError,
    PrincipalCredentialMfaStateConflictError,
)

HASH_A = "$2b$12$" + "d" * 53
HASH_B = "$2b$12$" + "e" * 53


@pytest.fixture()
def mongo_collection():
    uri = os.getenv("TEST_GLOBAL_PRINCIPAL_MONGO_URI")
    if not uri:
        pytest.fail("TEST_GLOBAL_PRINCIPAL_MONGO_URI is required")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    hello = client.admin.command("hello")
    if hello.get("setName") != "wilsyGlobalPrincipalCertRS":
        pytest.fail("wrong global-principal certification replica set")
    database = client[f"principal_credential_{uuid.uuid4().hex}"]
    collection = database[COLLECTION]
    PrincipalCredentialRepository.ensure_indexes(collection)
    try:
        yield client, collection
    finally:
        client.drop_database(database.name)
        client.close()


def credential(principal_id="principal-1", email="owner@example.com", password_hash=HASH_A, revision=0, mfa_enabled=True):
    return PrincipalCredential(
        principal_id=principal_id,
        normalized_email=email,
        password_hash=password_hash,
        credential_revision=revision,
        mfa_enabled=mfa_enabled,
    )


def test_real_mongo_unique_principal_and_normalized_email(mongo_collection):
    _client, collection = mongo_collection
    PrincipalCredentialRepository.insert(credential(), collection)
    with pytest.raises(PrincipalCredentialAlreadyExistsError):
        PrincipalCredentialRepository.insert(credential(principal_id="principal-2"), collection)
    with pytest.raises(PrincipalCredentialAlreadyExistsError):
        PrincipalCredentialRepository.insert(
            credential(principal_id="principal-2", email="owner@example.com"),
            collection,
        )
    assert PrincipalCredentialRepository.get_by_email("OWNER@example.com", collection).principal_id == "principal-1"



def test_real_mongo_mfa_enablement_is_one_time_and_advances_credential_epoch(mongo_collection):
    _client, collection = mongo_collection
    PrincipalCredentialRepository.insert(
        credential(mfa_enabled=False), collection
    )
    enabled = PrincipalCredentialRepository.enable_mfa("principal-1", 0, collection)
    assert enabled.mfa_enabled is True
    assert enabled.credential_revision == 1
    with pytest.raises(PrincipalCredentialMfaStateConflictError):
        PrincipalCredentialRepository.enable_mfa("principal-1", 1, collection)


def test_real_mongo_password_revision_compare_and_swap(mongo_collection):
    _client, collection = mongo_collection
    PrincipalCredentialRepository.insert(credential(), collection)
    result = PrincipalCredentialRepository.compare_and_swap_password_hash(
        "principal-1", 0, HASH_B, collection
    )
    assert result.credential_revision == 1
    assert result.password_hash == HASH_B
    with pytest.raises(PrincipalCredentialRevisionConflictError):
        PrincipalCredentialRepository.compare_and_swap_password_hash(
            "principal-1", 0, HASH_A, collection
        )


def test_real_mongo_concurrent_password_cas_has_one_winner(mongo_collection):
    _client, collection = mongo_collection
    PrincipalCredentialRepository.insert(credential(), collection)

    def attempt(value):
        try:
            PrincipalCredentialRepository.compare_and_swap_password_hash(
                "principal-1", 0, value, collection
            )
            return "UPDATED"
        except PrincipalCredentialRevisionConflictError:
            return "CONFLICT"

    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(attempt, (HASH_A, HASH_B)))
    assert sorted(outcomes) == ["CONFLICT", "UPDATED"]
    assert PrincipalCredentialRepository.get_by_principal("principal-1", collection).credential_revision == 1


def test_real_mongo_caller_transaction_abort_and_commit(mongo_collection):
    client, collection = mongo_collection
    session = client.start_session()
    try:
        session.start_transaction()
        PrincipalCredentialRepository.insert(
            credential(principal_id="aborted", email="aborted@example.com"),
            collection,
            session=session,
        )
        session.abort_transaction()
        with pytest.raises(PrincipalCredentialNotFoundError):
            PrincipalCredentialRepository.get_by_principal("aborted", collection)

        session.start_transaction()
        PrincipalCredentialRepository.insert(
            credential(principal_id="committed", email="committed@example.com"),
            collection,
            session=session,
        )
        session.commit_transaction()
        assert PrincipalCredentialRepository.get_by_principal(
            "committed", collection
        ).principal_id == "committed"
    finally:
        session.end_session()
