"""TITLE: Authentication PrincipalAuthority Real-Mongo Certification.
VERSION: v1.0.2-ACCESS-REVISION-CONTRACT-FIXTURE
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certifies durable PrincipalAuthority lifecycle dominance using a
contract-compliant ACCESS token projection and an isolated credential revision seam.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_authentication_principal_authority_mongo.py
COLLABORATION / OWNERSHIP: Exercises tools.eos.auth.authentication against
PrincipalAuthorityRepository using a disposable local certification Mongo topology.
CERTIFICATION / UPDATE DATE: 2026-11-15.
CHANGELOG:
  v1.0.2-ACCESS-REVISION-CONTRACT-FIXTURE supplies required ACCESS purpose
  and credential revision claims and isolates the tenant credential currentness
  dependency at revision zero. PrincipalAuthority remains backed by real Mongo.
  v1.0.1-SOVEREIGN-REAL-MONGO-CERT establishes canonical metadata and pytest
  monkeypatch restoration for the credential-verification seam.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No Atlas or production database is used; each fixture
uses a UUID-isolated database, cleans it after execution, and emits no credentials.
TENANT BOUNDARY: tenant_id is request context only; this artifact does not certify tenant membership authority.
AUTHORITY BOUNDARY: Certifies credential-shape admission and current durable
PrincipalAuthority lifecycle only. Credential revision is a fixed test seam;
separate AuthRegistry certifications own that durable contract.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

import asyncio
import os
import uuid
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from pymongo import MongoClient
from pymongo.collection import Collection
from starlette.requests import Request

from tools.eos.api.exceptions import UnauthorizedAccessException
from tools.eos.auth import authentication
from tools.eos.auth.jwt_provider import TokenPurpose
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import PrincipalAuthorityRepository
from tools.eos.auth.principal_status import PrincipalStatus

URI = os.getenv("TEST_VENDOR_MONGO_URI")
TENANT_ID = "tenant-cert"
CREDENTIAL_REVISION = 0


@dataclass(frozen=True)
class BoundPrincipalAuthorityReader:
    """Bind exact principal reads and test mutations to one disposable collection."""

    collection: Collection[Any]

    def get(self, principal_id: str) -> PrincipalAuthority:
        """Resolve one principal through the canonical strict Mongo hydrator."""
        return PrincipalAuthorityRepository.get(principal_id, self.collection)


@pytest.fixture()
def authority_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[BoundPrincipalAuthorityReader]:
    """Bind real PrincipalAuthority storage to the approved disposable replica set.

    @institutional The database name is UUID-isolated and dropped after the test;
    a separate currentness seam keeps this certificate scoped to principal lifecycle.
    """
    if not URI:
        pytest.fail("TEST_VENDOR_MONGO_URI is required")
    client = MongoClient(URI, serverSelectionTimeoutMS=5000)
    hello = client.admin.command("hello")
    if hello.get("setName") != "wilsyVendorCertRS":
        client.close()
        pytest.fail("wrong certification replica set")
    database = client[f"auth_projection_{uuid.uuid4().hex}"]
    collection = database["principal_authorities"]
    PrincipalAuthorityRepository.ensure_indexes(collection)
    monkeypatch.setattr(
        authentication.AuthRegistry,
        "get_credential_revision",
        lambda _registry, _tenant_id, _principal_id, session=None: CREDENTIAL_REVISION,
    )
    try:
        yield BoundPrincipalAuthorityReader(collection)
    finally:
        client.drop_database(database.name)
        client.close()


def request() -> Request:
    """Build the minimum HTTP request scope required by authentication."""
    return Request({"type": "http", "method": "GET", "path": "/", "headers": []})


def credentials() -> HTTPAuthorizationCredentials:
    """Return a synthetic bearer whose verifier is replaced in each test."""
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials="synthetic")


def access_payload(principal_id: str) -> dict[str, object]:
    """Project all claims required by the current tenant ACCESS contract."""
    return {
        "identity_id": principal_id,
        "tenant_id": TENANT_ID,
        "token_purpose": TokenPurpose.ACCESS.value,
        "credential_revision": CREDENTIAL_REVISION,
    }


def authenticate(
    repository: Any,
    payload: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
    api_key: str | None = None,
) -> Any:
    """Exercise real durable principal admission while stubbing signature decoding."""
    monkeypatch.setattr(authentication, "verify_access_token", lambda _token: payload)
    return asyncio.run(
        authentication.get_current_identity(
            request(), credentials(), api_key, repository
        )
    )


def test_active_suspended_revoked_and_absent(
    authority_repository: BoundPrincipalAuthorityReader,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Current principal lifecycle dominates an otherwise valid ACCESS token."""
    for status in (
        PrincipalStatus.ACTIVE,
        PrincipalStatus.SUSPENDED,
        PrincipalStatus.REVOKED,
    ):
        principal_id = f"p-{status.value.lower()}"
        PrincipalAuthorityRepository.create(
            PrincipalAuthority(principal_id, status, 0),
            authority_repository.collection,
        )
        if status is PrincipalStatus.ACTIVE:
            identity = authenticate(
                authority_repository, access_payload(principal_id), monkeypatch
            )
            assert identity.status is status
        else:
            with pytest.raises(UnauthorizedAccessException):
                authenticate(
                    authority_repository, access_payload(principal_id), monkeypatch
                )

    with pytest.raises(UnauthorizedAccessException):
        authenticate(
            authority_repository, access_payload("missing-principal"), monkeypatch
        )


def test_lifecycle_change_dominates_issued_credential(
    authority_repository: BoundPrincipalAuthorityReader,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A previously valid ACCESS projection cannot outlive lifecycle changes."""
    principal_id = "p-lifecycle"
    PrincipalAuthorityRepository.create(
        PrincipalAuthority(principal_id, PrincipalStatus.ACTIVE, 0),
        authority_repository.collection,
    )
    payload = access_payload(principal_id)
    assert authenticate(authority_repository, payload, monkeypatch).identity_id == principal_id

    PrincipalAuthorityRepository.compare_and_swap(
        PrincipalAuthority(principal_id, PrincipalStatus.SUSPENDED, 1),
        0,
        authority_repository.collection,
    )
    with pytest.raises(UnauthorizedAccessException):
        authenticate(authority_repository, payload, monkeypatch)

    PrincipalAuthorityRepository.compare_and_swap(
        PrincipalAuthority(principal_id, PrincipalStatus.REVOKED, 2),
        1,
        authority_repository.collection,
    )
    with pytest.raises(UnauthorizedAccessException):
        authenticate(authority_repository, payload, monkeypatch)


def test_malformed_authority_and_api_key_fail_closed(
    authority_repository: BoundPrincipalAuthorityReader,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Malformed persisted authority and unsupported API-key authority are denied."""
    authority_repository.collection.insert_one(
        {"principal_id": "p-corrupt", "status": "BROKEN", "revision": 0}
    )
    with pytest.raises(UnauthorizedAccessException):
        authenticate(
            authority_repository, access_payload("p-corrupt"), monkeypatch
        )
    with pytest.raises(UnauthorizedAccessException):
        authenticate(
            authority_repository,
            access_payload("p-api-key-denied"),
            monkeypatch,
            "synthetic-api-key",
        )


# ARTIFACT: test_authentication_principal_authority_mongo.py
# VERSION: v1.0.2-ACCESS-REVISION-CONTRACT-FIXTURE
# AUTHORITY BOUNDARY: Credential-shape admission and durable PrincipalAuthority lifecycle certification only.
# TENANT POSTURE: Tenant claim is request context; tenant membership authority remains separate.
# FAIL-CLOSED POSTURE: Missing, malformed, stale, revoked, or unsupported credentials are denied.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively owns financial execution.
# END OF WILSY OS SOVEREIGN ARTIFACT
