"""Real-Mongo certification for authentication lifecycle dominance."""
import asyncio
import os
import uuid
from fastapi.security import HTTPAuthorizationCredentials
from pymongo import MongoClient
from starlette.requests import Request
import pytest
from tools.eos.auth import authentication
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.api.exceptions import UnauthorizedAccessException

URI = os.getenv("TEST_VENDOR_MONGO_URI")

@pytest.fixture()
def authority_repository():
    if not URI: pytest.fail("TEST_VENDOR_MONGO_URI is required")
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    hello = client.admin.command("hello")
    if hello.get("setName") != "wilsyVendorCertRS": pytest.fail("wrong certification replica set")
    database = client[f"auth_projection_{uuid.uuid4().hex}"]
    collection = database["principal_authorities"]
    PrincipalAuthorityRepository.ensure_indexes(collection)
    class BoundRepository:
        def get(self, principal_id): return PrincipalAuthorityRepository.get(principal_id, collection)
    yield BoundRepository()
    client.drop_database(database.name); client.close()

def request(): return Request({"type": "http", "method": "GET", "path": "/", "headers": []})
def creds(): return HTTPAuthorizationCredentials(scheme="Bearer", credentials="signed")
def run(repo, payload, api_key=None):
    authentication.verify_access_token = lambda _: payload
    return asyncio.run(authentication.get_current_identity(request(), creds(), api_key, repo))

def test_active_suspended_revoked_and_absent(authority_repository):
    for status in (PrincipalStatus.ACTIVE, PrincipalStatus.SUSPENDED, PrincipalStatus.REVOKED):
        principal = f"p-{status.value.lower()}"
        collection = authority_repository.__class__.get.__closure__[0].cell_contents
        PrincipalAuthorityRepository.create(PrincipalAuthority(principal, status, 0), collection)
        payload = {"identity_id": principal, "tenant_id": "tenant-cert"}
        if status is PrincipalStatus.ACTIVE:
            assert run(authority_repository, payload).status is status
        else:
            with pytest.raises(UnauthorizedAccessException): run(authority_repository, payload)
    with pytest.raises(UnauthorizedAccessException): run(authority_repository, {"identity_id": "missing", "tenant_id": "tenant-cert"})

def test_lifecycle_change_dominates_issued_credential(authority_repository):
    collection = authority_repository.__class__.get.__closure__[0].cell_contents
    principal = "p-lifecycle"
    PrincipalAuthorityRepository.create(PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0), collection)
    payload = {"identity_id": principal, "tenant_id": "tenant-cert"}
    assert run(authority_repository, payload).identity_id == principal
    PrincipalAuthorityRepository.compare_and_swap(PrincipalAuthority(principal, PrincipalStatus.SUSPENDED, 1), 0, collection)
    with pytest.raises(UnauthorizedAccessException): run(authority_repository, payload)
    PrincipalAuthorityRepository.compare_and_swap(PrincipalAuthority(principal, PrincipalStatus.REVOKED, 2), 1, collection)
    with pytest.raises(UnauthorizedAccessException): run(authority_repository, payload)

def test_malformed_authority_and_api_key_fail_closed(authority_repository):
    collection = authority_repository.__class__.get.__closure__[0].cell_contents
    collection.insert_one({"principal_id": "corrupt", "status": "BROKEN", "revision": 0})
    with pytest.raises(UnauthorizedAccessException): run(authority_repository, {"identity_id": "corrupt", "tenant_id": "tenant-cert"})
    with pytest.raises(UnauthorizedAccessException): run(authority_repository, {"identity_id": "p", "tenant_id": "tenant-cert"}, "WILSY-OS-MASTER-API-KEY-2026")
