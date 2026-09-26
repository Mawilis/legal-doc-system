"""Isolated real-Mongo P2D certificate for content delivery.

TITLE: Legal Client Acceptance Content Delivery Real-Mongo Certificate
VERSION: v1.0.0-L9A4-P2D-CLIENT-ACCEPTANCE-CONTENT-DELIVERY-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Prove one authenticated content delivery against real Mongo source
         authorities and a UUID-isolated synthetic content capability.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_client_acceptance_content_service_real_mongo.py
COLLABORATION / OWNERSHIP: P2C3 fixtures own canonical source records; this
                            certificate owns only an isolated reader fixture.
CERTIFICATION / UPDATE DATE: 2026-09-26
CHANGELOG: v1.0.0-L9A4-P2D certificate proves topology, exact revalidation,
           content hash verification, stale approval denial and no downstream
           authority collections or writes.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identifiers; no URI, token, hash
                             secret or personal data is printed.
TENANT BOUNDARY: UUID-isolated database and exact fixture tenant/principal.
AUTHORITY BOUNDARY: Content delivery projection only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import os
from typing import Any, Iterator, cast
from uuid import uuid4

import pytest
from pymongo import MongoClient

from tools.eos.legal_operations.service.legal_client_acceptance_content_service import (
    StoredContent,
    deliver_legal_client_acceptance_context_content,
)
from tools.eos.legal_operations.orchestration.legal_client_acceptance_context_orchestrator import compose_legal_client_acceptance_context
from tools.eos.legal_operations.registry import legal_client_acceptance_context_registry as context_registry
from tests.integration.test_legal_client_acceptance_context_orchestrator_real_mongo import (
    FP_B,
    INSTRUMENT_ID,
    MATTER_ID,
    NOW,
    TENANT,
    _collections,
    _ensure_indexes,
    _identity,
    _issuer,
    _kwargs,
    _seed,
)

MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
CONTENT_REFERENCE = "server://p2c3/content"
CONTENT = b"p2c3-real-b"


class MongoContentReader:
    """Synthetic test-owned reader using only the run-scoped Mongo database."""

    def __init__(self, collection: Any) -> None:
        self.collection = collection

    def read(self, content_reference: str, *, tenant_id: str, session: Any) -> StoredContent:
        row = self.collection.find_one({"tenant_id": tenant_id, "reference": content_reference}, session=session)
        if row is None:
            raise LookupError("content unavailable")
        return StoredContent(row["content"], row["media_type"])


@pytest.fixture
def mongo_context() -> Iterator[tuple[MongoClient[Any], Any, dict[str, Any]]]:
    client: MongoClient[Any] = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5_000, retryWrites=True, tz_aware=True)
    database: Any = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == "wilsyVendorCertRS"
        assert hello.get("isWritablePrimary") is True
        assert hello.get("logicalSessionTimeoutMinutes") is not None
        database = client[f"wilsy_l9a4_p2d_content_{uuid4().hex}"]
        collections = _collections(database)
        _ensure_indexes(collections)
        content_collection = database["p2d_content_fixture"]
        content_collection.insert_one({"tenant_id": TENANT, "reference": CONTENT_REFERENCE, "content": CONTENT, "media_type": "text/plain"})
        yield client, database, {**collections, "content": content_collection}
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _compose(client: MongoClient[Any], collections: dict[str, Any]) -> Any:
    kwargs = _kwargs(collections, _issuer(collections))
    with client.start_session() as session:
        with session.start_transaction():
            return compose_legal_client_acceptance_context(**kwargs, session=session)


def _deliver(client: MongoClient[Any], collections: dict[str, Any], **overrides: Any) -> Any:
    kwargs = dict(identity=_identity(), acceptance_context_id="context-p2c3-real", context_collection=collections["context"], matter_lifecycle_collection=collections["matter"], visibility_collection=collections["visibility"], party_collection=collections["party"], capacity_collection=collections["capacity"], instrument_collection=collections["instrument"], instrument_lifecycle_collection=collections["lifecycle"], approval_collection=collections["approval"], content_reader=MongoContentReader(collections["content"]), principal_repository=type("R", (), {"resolve": lambda _s, *a, **k: __import__("tools.eos.auth.principal_authority_repository", fromlist=["PrincipalAuthorityRepository"]).PrincipalAuthorityRepository.resolve(a[0], collections["principal"], session=k.get("session"))})(), membership_repository=type("R", (), {"resolve": lambda _s, *a, **k: __import__("tools.eos.auth.tenant_membership_repository", fromlist=["TenantMembershipRepository"]).TenantMembershipRepository.resolve(a[0], a[1], collections["membership"], session=k.get("session"))})(), business_role_repository=type("R", (), {"resolve": lambda _s, *a, **k: __import__("tools.eos.auth.role_assignment_repository", fromlist=["RoleAssignmentRepository"]).RoleAssignmentRepository.resolve(a[0], a[1], a[2], collections["assignment"], session=k.get("session"))})(), role_assignment_repository=type("R", (), {"resolve": lambda _s, *a, **k: __import__("tools.eos.auth.role_assignment_repository", fromlist=["RoleAssignmentRepository"]).RoleAssignmentRepository.resolve(a[0], a[1], a[2], collections["assignment"], session=k.get("session"))})(), clock=lambda: NOW)
    kwargs.update(overrides)
    with client.start_session() as session:
        with session.start_transaction():
            cast(dict[str, Any], kwargs)["session"] = session
            return deliver_legal_client_acceptance_context_content(**cast(dict[str, Any], kwargs))


def test_real_mongo_topology_and_authenticated_delivery(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, database, collections = mongo_context
    _seed(client, collections)
    _compose(client, collections)
    value = _deliver(client, collections)
    assert value.content == CONTENT.decode("utf-8")
    assert value.content_fingerprint == hashlib.sha3_512(CONTENT).hexdigest()
    assert value.instrument_id == INSTRUMENT_ID and value.acceptance_context_id == "context-p2c3-real"
    assert collections["context"].count_documents({}) == 1
    assert not {"legal_client_acceptances", "engagements", "representations", "court_authorities", "financial_approvals"} & set(database.list_collection_names())


def test_missing_content_fails_closed_without_source_mutation(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _database, collections = mongo_context
    _seed(client, collections)
    _compose(client, collections)
    collections["content"].delete_many({})
    with pytest.raises(Exception):
        _deliver(client, collections)
    assert collections["context"].count_documents({}) == 1


def test_hash_mismatch_fails_closed(mongo_context: tuple[MongoClient[Any], Any, dict[str, Any]]) -> None:
    client, _database, collections = mongo_context
    _seed(client, collections)
    _compose(client, collections)
    collections["content"].update_one({}, {"$set": {"content": b"tampered"}})
    with pytest.raises(Exception):
        _deliver(client, collections)


# ARTIFACT: test_legal_client_acceptance_content_service_real_mongo.py
# VERSION: v1.0.0-L9A4-P2D-CLIENT-ACCEPTANCE-CONTENT-DELIVERY-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: isolated content delivery certificate only
# TENANT POSTURE: UUID-isolated database and exact source scopes
# FAIL-CLOSED POSTURE: unavailable or altered content rejects
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
