# -*- coding: utf-8 -*-
"""Real-Mongo certification for PrincipalAuthorityRepository.

VERSION: v1.0.0-WILSY-PRINCIPAL-AUTHORITY-REPOSITORY-MONGO-CERT
CHANGELOG: v1.0.0 certifies durable snapshots, caller sessions, CAS, and terminal stale-write protection.
"""
import os
import uuid
from typing import Any

import pytest
from pymongo import MongoClient

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    COLLECTION,
    PrincipalAuthorityAlreadyExistsError,
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRevisionConflictError,
)
from tools.eos.auth.principal_status import PrincipalStatus


@pytest.fixture()
def collection() -> Any:
    uri = os.getenv("TEST_VENDOR_MONGO_URI")
    if not uri:
        pytest.fail("TEST_VENDOR_MONGO_URI is required for real-Mongo certification")
    client = MongoClient(uri, serverSelectionTimeoutMS=5000, retryWrites=True)
    hello = client.admin.command("hello")
    if hello.get("isWritablePrimary") is not True or hello.get("setName") != "wilsyVendorCertRS":
        client.close()
        pytest.fail("dedicated writable replica-set authority is required")
    database = client["principal_authority_cert_" + uuid.uuid4().hex]
    target = database[COLLECTION]
    PrincipalAuthorityRepository.ensure_indexes(target)
    try:
        yield target
    finally:
        client.drop_database(database.name)
        client.close()


def item(status: PrincipalStatus = PrincipalStatus.ACTIVE, revision: int = 0) -> PrincipalAuthority:
    return PrincipalAuthority("principal-" + uuid.uuid4().hex, status, revision)


def test_create_get_duplicate_and_absence(collection: Any) -> None:
    value = item()
    assert PrincipalAuthorityRepository.create(value, collection) == value
    assert PrincipalAuthorityRepository.get(value.principal_id, collection) == value
    with pytest.raises(PrincipalAuthorityAlreadyExistsError):
        PrincipalAuthorityRepository.create(value, collection)
    with pytest.raises(PrincipalAuthorityNotFoundError):
        PrincipalAuthorityRepository.get("missing", collection)


def test_cas_revision_and_abort_commit_session(collection: Any) -> None:
    value = item()
    PrincipalAuthorityRepository.create(value, collection)
    client = collection.database.client
    with client.start_session() as session:
        session.start_transaction()
        updated = PrincipalAuthority(value.principal_id, PrincipalStatus.SUSPENDED, 1)
        PrincipalAuthorityRepository.compare_and_swap(updated, 0, collection, session=session)
        assert PrincipalAuthorityRepository.get(value.principal_id, collection, session=session) == updated
        session.abort_transaction()
    assert PrincipalAuthorityRepository.get(value.principal_id, collection) == value
    with client.start_session() as session:
        session.start_transaction()
        updated = PrincipalAuthority(value.principal_id, PrincipalStatus.SUSPENDED, 1)
        PrincipalAuthorityRepository.compare_and_swap(updated, 0, collection, session=session)
        session.commit_transaction()
    assert PrincipalAuthorityRepository.get(value.principal_id, collection) == updated


def test_stale_cas_and_revoked_terminal_protection(collection: Any) -> None:
    value = item()
    PrincipalAuthorityRepository.create(value, collection)
    revoked = PrincipalAuthority(value.principal_id, PrincipalStatus.REVOKED, 1)
    PrincipalAuthorityRepository.compare_and_swap(revoked, 0, collection)
    for stale in (PrincipalAuthority(value.principal_id, PrincipalStatus.ACTIVE, 1), PrincipalAuthority(value.principal_id, PrincipalStatus.SUSPENDED, 1)):
        with pytest.raises(PrincipalAuthorityRevisionConflictError):
            PrincipalAuthorityRepository.compare_and_swap(stale, 0, collection)
    assert PrincipalAuthorityRepository.get(value.principal_id, collection) == revoked


def test_persisted_shape_has_no_other_authority(collection: Any) -> None:
    value = item()
    PrincipalAuthorityRepository.create(value, collection)
    row = collection.find_one({"principal_id": value.principal_id})
    assert set(row) == {"_id", "principal_id", "status", "revision"}
    assert row["status"] == "ACTIVE"


# ARTIFACT: test_principal_authority_repository_mongo.py
# VERSION: v1.0.0-WILSY-PRINCIPAL-AUTHORITY-REPOSITORY-MONGO-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
