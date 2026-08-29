"""TITLE: Authentication PrincipalAuthority Real-Mongo Certification.
VERSION: v1.0.1-SOVEREIGN-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Real Mongo certification of credential verification and durable
PrincipalAuthority lifecycle dominance, without changing authentication semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_authentication_principal_authority_mongo.py
COLLABORATION / OWNERSHIP: This integration artifact exercises tools.eos.auth.authentication
against PrincipalAuthorityRepository and a disposable local certification Mongo topology.
CERTIFICATION/UPDATE DATE: 2026-08-29.
CHANGELOG:
  v1.0.1-SOVEREIGN-REAL-MONGO-CERT: Establishes canonical certification metadata and
  deterministic pytest monkeypatch restoration for the credential-verification seam.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: No Atlas or production database is used; each fixture uses a
UUID-isolated database, cleans it after execution, and emits no credential values.
TENANT BOUNDARY: tenant_id is request context only; this artifact does not certify tenant membership authority.
AUTHORITY BOUNDARY: This file certifies credential verification and current durable
PrincipalAuthority lifecycle dominance against real Mongo only. It does not certify
tenant membership, governed role assignment, authorization decisions, credential
issuance, Node authentication runtime, or financial execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""

VERSION = "v1.0.1-SOVEREIGN-REAL-MONGO-CERT"
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
def run(repo, payload, monkeypatch, api_key=None):
    monkeypatch.setattr(authentication, "verify_access_token", lambda _: payload)
    return asyncio.run(authentication.get_current_identity(request(), creds(), api_key, repo))

def test_active_suspended_revoked_and_absent(authority_repository, monkeypatch):
    for status in (PrincipalStatus.ACTIVE, PrincipalStatus.SUSPENDED, PrincipalStatus.REVOKED):
        principal = f"p-{status.value.lower()}"
        collection = authority_repository.__class__.get.__closure__[0].cell_contents
        PrincipalAuthorityRepository.create(PrincipalAuthority(principal, status, 0), collection)
        payload = {"identity_id": principal, "tenant_id": "tenant-cert"}
        if status is PrincipalStatus.ACTIVE:
            assert run(authority_repository, payload, monkeypatch).status is status
        else:
            with pytest.raises(UnauthorizedAccessException): run(authority_repository, payload, monkeypatch)
    with pytest.raises(UnauthorizedAccessException): run(authority_repository, {"identity_id": "missing", "tenant_id": "tenant-cert"}, monkeypatch)

def test_lifecycle_change_dominates_issued_credential(authority_repository, monkeypatch):
    collection = authority_repository.__class__.get.__closure__[0].cell_contents
    principal = "p-lifecycle"
    PrincipalAuthorityRepository.create(PrincipalAuthority(principal, PrincipalStatus.ACTIVE, 0), collection)
    payload = {"identity_id": principal, "tenant_id": "tenant-cert"}
    assert run(authority_repository, payload, monkeypatch).identity_id == principal
    PrincipalAuthorityRepository.compare_and_swap(PrincipalAuthority(principal, PrincipalStatus.SUSPENDED, 1), 0, collection)
    with pytest.raises(UnauthorizedAccessException): run(authority_repository, payload, monkeypatch)
    PrincipalAuthorityRepository.compare_and_swap(PrincipalAuthority(principal, PrincipalStatus.REVOKED, 2), 1, collection)
    with pytest.raises(UnauthorizedAccessException): run(authority_repository, payload, monkeypatch)

def test_malformed_authority_and_api_key_fail_closed(authority_repository, monkeypatch):
    collection = authority_repository.__class__.get.__closure__[0].cell_contents
    collection.insert_one({"principal_id": "corrupt", "status": "BROKEN", "revision": 0})
    with pytest.raises(UnauthorizedAccessException): run(authority_repository, {"identity_id": "corrupt", "tenant_id": "tenant-cert"}, monkeypatch)
    with pytest.raises(UnauthorizedAccessException): run(authority_repository, {"identity_id": "p", "tenant_id": "tenant-cert"}, monkeypatch, "WILSY-OS-MASTER-API-KEY-2026")


# ARTIFACT: test_authentication_principal_authority_mongo.py
# VERSION: v1.0.1-SOVEREIGN-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: Credential verification and durable PrincipalAuthority lifecycle certification only.
# TENANT POSTURE: tenant_id is request context; tenant membership authority remains separate.
# FAIL-CLOSED POSTURE: Missing, malformed, stale, revoked, or bypass credentials are denied.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
