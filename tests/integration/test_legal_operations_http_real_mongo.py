"""TITLE: WILSY OS Legal Operations read API real-Mongo certificate.
VERSION: v1.0.0-L7A-LEGAL-OPERATIONS-READ-API-RM-CERT
AUTHORITY: Host-backed certificate for tenant-authorized canonical projections.
EPITOME: Proves a real P2 LegalInstruction round-trip through the authenticated ASGI read boundary.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_http_real_mongo.py
COLLABORATION / OWNERSHIP: Wilsy Core Engineering; P1/P2 remain canonical authorities.
CERTIFICATION / UPDATE DATE: 2026-09-15
CHANGELOG: v1.0.0 certifies own-tenant visibility, foreign absence, and bounded output on Mongo.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated database and synthetic identifiers; no secrets or provider calls.
TENANT BOUNDARY: Every read predicate includes the exact authorized tenant.
AUTHORITY BOUNDARY: Certificate and read projection only; no lifecycle or command mutation.
TRANSACTION BOUNDARY: This certificate uses no transaction; the registry owns none.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
FAIL-CLOSED DECLARATION: Host availability alone may skip; all post-hello product failures fail.
"""
from __future__ import annotations

from datetime import datetime, timezone
import os
from typing import Any, Iterator
import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

import tools.eos.api.legal_operations_router as legal_router
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import TenantAuthorizationDecision, TenantAuthorizationReason
from tools.eos.legal_operations.domain.legal_operations_lifecycle import LegalInstruction
from tools.eos.legal_operations.registry.legal_operations_lifecycle_registry import (
    COLLECTION,
    LegalOperationsLifecycleRegistry,
)


VERSION = "v1.0.0-L7A-LEGAL-OPERATIONS-READ-API-RM-CERT"
MONGO_URI = os.getenv("TEST_VENDOR_MONGO_URI", "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS")
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
NOW = datetime(2026, 9, 15, 8, 0, tzinfo=timezone.utc)


@pytest.fixture
def mongo_context() -> Iterator[tuple[Any, Any]]:
    """Provide an isolated majority-concern collection; skip only pre-cert host absence."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database = None
    try:
        hello = client.admin.command("hello")
    except PyMongoError as error:
        client.close()
        pytest.skip(f"host Mongo unavailable during hello: {type(error).__name__}")
    if hello.get("setName") != EXPECTED_REPLICA_SET:
        client.close()
        pytest.skip(f"wrong replica set: {hello.get('setName')!r}")
    if hello.get("isWritablePrimary", hello.get("ismaster")) is not True:
        client.close()
        pytest.skip("replica set has no writable primary")
    database = client[f"l7a_legal_{uuid.uuid4().hex}"]
    collection = database.get_collection(
        COLLECTION,
        write_concern=WriteConcern(w="majority", j=True),
        read_concern=ReadConcern("majority"),
    )
    try:
        LegalOperationsLifecycleRegistry.ensure_indexes(collection)
        yield database, collection
    finally:
        if database is not None:
            try:
                client.drop_database(database.name)
            except PyMongoError:
                pass
        client.close()


def _instruction(tenant_id: str) -> LegalInstruction:
    return LegalInstruction(
        tenant_id=tenant_id,
        instruction_id="instruction-1",
        case_matter_id="matter-1",
        document_id="document-1",
        registered_at=NOW,
        evidence_reference="registration-evidence",
    )


def _context(tenant_id: str) -> TenantAuthorizationContext:
    identity = SovereignIdentity(
        identity_id="principal-1",
        tenant_id=tenant_id,
        username="operator",
        email="operator@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    decision = TenantAuthorizationDecision(True, TenantAuthorizationReason.AUTHORIZED, "tenant_legal_partner", "LEGAL_PARTNER")
    return TenantAuthorizationContext(identity=identity, tenant_id=tenant_id, decision=decision)


def _app(collection: Any, context: TenantAuthorizationContext) -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.dependency_overrides[legal_router._INSTRUCTION_READ] = lambda: context
    app.dependency_overrides[legal_router.get_lifecycle_collection] = lambda: collection
    app.include_router(legal_router.router, prefix="/api")
    return app


def test_real_mongo_authorized_projection_and_foreign_absence(mongo_context: tuple[Any, Any]) -> None:
    _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    value = _instruction(tenant)
    persisted = LegalOperationsLifecycleRegistry.create(value, collection)
    assert persisted == value
    with TestClient(_app(collection, _context(tenant))) as client:
        own = client.get("/api/legal-operations/instructions/instruction-1")
    assert own.status_code == 200
    assert own.json()["data"] == value.to_dict()
    foreign_tenant = f"tenant-{uuid.uuid4().hex}"
    with TestClient(_app(collection, _context(foreign_tenant))) as client:
        foreign = client.get("/api/legal-operations/instructions/instruction-1")
    assert foreign.status_code == 404


def test_real_mongo_unknown_resource_is_bounded(mongo_context: tuple[Any, Any]) -> None:
    _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    with TestClient(_app(collection, _context(tenant))) as client:
        response = client.get("/api/legal-operations/instructions/missing")
    assert response.status_code == 404
    assert "stack_trace" not in response.text


def test_real_mongo_projection_has_no_financial_or_mongo_fields(mongo_context: tuple[Any, Any]) -> None:
    _, collection = mongo_context
    tenant = f"tenant-{uuid.uuid4().hex}"
    value = _instruction(tenant)
    LegalOperationsLifecycleRegistry.create(value, collection)
    with TestClient(_app(collection, _context(tenant))) as client:
        response = client.get("/api/legal-operations/instructions/instruction-1")
    assert response.status_code == 200
    payload = response.json()["data"]
    assert "_id" not in payload
    assert not any(token in key.casefold() for key in payload for token in ("payment", "settlement", "invoice", "billing_execution"))


# ARTIFACT: test_legal_operations_http_real_mongo.py
# VERSION: v1.0.0-L7A-LEGAL-OPERATIONS-READ-API-RM-CERT
# AUTHORITY BOUNDARY: real-Mongo read projection certificate only
# TENANT POSTURE: exact tenant predicates and foreign absence
# FAIL-CLOSED POSTURE: post-hello failures are certificate failures
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
