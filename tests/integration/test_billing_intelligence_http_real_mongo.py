"""M14-P6 host certificate for the canonical billing-intelligence HTTP path.

TITLE: WILSY OS Billing Intelligence HTTP Real-Mongo Certificate
VERSION: v1.1.0-M14-P6-BILLING-INTELLIGENCE-HTTP-REAL-MONGO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify the production FastAPI billing-intelligence evidence route
         with authorized-context tenant scope and durable evidence replay.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_billing_intelligence_http_real_mongo.py
COLLABORATION / OWNERSHIP: Host certificate for billing_router.py; the
                            authorization dependency owns tenant authority and
                            BillingIntelligenceRegistry owns durable evidence.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: 2026-09-13 v1.1.0-M14-P6 re-anchors the host fixture to the exact
           M14-P5 authorization dependency and synthetic context contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: UUID-isolated synthetic data only; no provider,
                             secret, KMS, customer, payment, or settlement data.
TENANT BOUNDARY: Canonical route tenant scope comes only from the authorized
                 TenantAuthorizationContext; query/header claims cannot replace it.
AUTHORITY BOUNDARY: Host HTTP composition certificate only; no new billing,
                    execution, payment, settlement, or paid-state authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
FAIL-CLOSED DECLARATION: Authorization, source corruption, and persistence
                         failures remain explicit HTTP failures.
"""
from datetime import datetime, timezone
import importlib
import os
import sys
import types
from typing import Any, Iterator, cast
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.saas.billing.billing_intelligence_registry import (
    COLLECTION as EVIDENCE_COLLECTION,
    BillingIntelligenceRegistry,
)
from tools.eos.saas.billing.commercial_receivable_registry import CommercialReceivableRegistry
from tools.eos.saas.domain.commercial_receivable import (
    CommercialReceivable,
    ReceivableFamily,
    ReceivableStatus,
)
from tools.eos.saas.domain.commercial_receivable_aging import CommercialReceivableAging
from tools.eos.saas.domain.commercial_receivable_dunning import CommercialReceivableDunning


MONGO_URI = os.getenv(
    "TEST_VENDOR_MONGO_URI",
    "mongodb://127.0.0.1:27027/?replicaSet=wilsyVendorCertRS",
)
EXPECTED_REPLICA_SET = "wilsyVendorCertRS"
AS_OF = datetime(2026, 9, 12, 12, tzinfo=timezone.utc)
AUTHORIZED_TENANT = "tenant-http-real"


def _authorized_context(tenant_id: str) -> TenantAuthorizationContext:
    """Build synthetic authorization evidence for the host-only test seam."""
    identity = types.SimpleNamespace(identity_id=f"principal-{tenant_id}")
    decision = types.SimpleNamespace(authorized=True)
    return TenantAuthorizationContext(
        identity=cast(Any, identity),
        tenant_id=tenant_id,
        decision=cast(Any, decision),
    )


def _source_values(
    tenant: str,
) -> tuple[CommercialReceivable, CommercialReceivableAging, CommercialReceivableDunning]:
    receivable = CommercialReceivable(
        tenant_id=tenant,
        receivable_family=ReceivableFamily.CLIENT,
        receivable_id="r-http-1",
        source_invoice_id="invoice-http-1",
        currency="ZAR",
        original_amount_minor=1250,
        adjustment_amount_minor=0,
        outstanding_amount_minor=1250,
        source_invoice_fingerprint="a" * 128,
        status=ReceivableStatus.OPEN,
    )
    aging = CommercialReceivableAging.from_receivable(
        receivable,
        due_at=datetime(2026, 8, 1, tzinfo=timezone.utc),
        as_of=AS_OF,
    )
    return receivable, aging, CommercialReceivableDunning.from_aging(aging, effective_at=AS_OF)


@pytest.fixture
def http_context() -> Iterator[tuple[Any, Any, Any]]:
    """Yield a UUID-isolated writable replica-set database for host execution."""
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000, retryWrites=True)
    database = None
    try:
        hello = client.admin.command("hello")
        assert hello.get("setName") == EXPECTED_REPLICA_SET
        assert hello.get("isWritablePrimary") is True
        database = client[f"m14p6_billing_http_{uuid.uuid4().hex}"]
        options = {
            "write_concern": WriteConcern(w="majority", j=True),
            "read_concern": ReadConcern("majority"),
        }
        collections = (
            database.get_collection("commercial_receivables", **options),
            database.get_collection("commercial_receivable_aging", **options),
            database.get_collection("commercial_receivable_dunning", **options),
            database.get_collection(EVIDENCE_COLLECTION, **options),
        )
        BillingIntelligenceRegistry.ensure_indexes(collections[3])
        yield client, database, collections
    finally:
        if database is not None:
            client.drop_database(database.name)
        client.close()


def _app(database: Any) -> TestClient:
    """Mount the production router with only its canonical auth seam overridden."""
    import tools.eos.api.billing_router as module

    module._require_db = lambda: database
    app = FastAPI()
    app.include_router(module.router)
    app.dependency_overrides[module._BILLING_INTELLIGENCE_EVIDENCE_READ_AUTHORIZATION] = (
        lambda: _authorized_context(AUTHORIZED_TENANT)
    )
    return TestClient(app)


@pytest.fixture()
def production_router() -> Iterator[Any]:
    """Import the production router with its legacy registry import isolated."""
    registry_name = "tools.eos.saas.billing.billing_registry"
    router_name = "tools.eos.api.billing_router"
    previous_registry = sys.modules.get(registry_name)
    previous_router = sys.modules.pop(router_name, None)
    stub = types.ModuleType(registry_name)
    setattr(stub, "BillingRegistry", type("BillingRegistry", (), {}))
    setattr(stub, "get_billing_registry", lambda: object())
    setattr(stub, "db", None)
    setattr(stub, "client", None)
    sys.modules[registry_name] = stub
    try:
        yield importlib.import_module(router_name)
    finally:
        sys.modules.pop(router_name, None)
        if previous_router is not None:
            sys.modules[router_name] = previous_router
        if previous_registry is not None:
            sys.modules[registry_name] = previous_registry
        else:
            sys.modules.pop(registry_name, None)


def test_m14_p6_authorization_dependency_identity_and_route_binding(
    production_router: Any,
) -> None:
    """The route uses the exact M14-P5 authorization dependency object."""
    module = production_router
    dependency = module._BILLING_INTELLIGENCE_EVIDENCE_READ_AUTHORIZATION
    assert dependency.permission_id == "billing_intelligence:evidence:read"
    assert dependency.operation == "billing_intelligence_evidence_read"
    routes = [
        route
        for route in module.router.routes
        if getattr(route, "path", "") == "/billing/intelligence/evidence"
    ]
    assert len(routes) == 1
    route = routes[0]
    assert len(route.dependant.dependencies) == 1
    assert route.dependant.dependencies[0].call is dependency


def test_m14_p6_route_requires_production_authorization(
    production_router: Any,
) -> None:
    """Without an override, the production authorization dependency cannot yield 200."""
    app = FastAPI()
    app.include_router(production_router.router)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get(
            "/billing/intelligence/evidence?as_of=2026-09-12T12:00:00%2B00:00"
        )
    assert response.status_code != 200


def test_production_http_composition_persists_and_exactly_replays(http_context: Any) -> None:
    """Authorized-context requests persist and exactly replay durable evidence."""
    _, database, collections = http_context
    receivable, aging, dunning = _source_values(AUTHORIZED_TENANT)
    CommercialReceivableRegistry.ensure_indexes(collections[0])
    CommercialReceivableRegistry.create(receivable, collections[0])
    collections[1].insert_one(aging.to_dict())
    collections[2].insert_one(dunning.to_dict())
    with _app(database) as client:
        path = (
            "/billing/intelligence/evidence?as_of=2026-09-12T12:00:00%2B00:00"
            "&tenant_id=attacker-query"
        )
        first = client.get(path, headers={"X-Tenant-ID": "attacker-header"})
        second = client.get(path, headers={"X-Tenant-ID": "attacker-header"})
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert first.json()["tenant_id"] == AUTHORIZED_TENANT
    assert collections[3].count_documents({"tenant_id": AUTHORIZED_TENANT}) == 1
    durable = collections[3].find_one({"tenant_id": AUTHORIZED_TENANT})
    assert durable is not None
    assert first.json()["evidence_fingerprint"] == durable["evidence_fingerprint"]
    assert first.json()["evidence_identity"] == durable["evidence_identity"]


def test_cross_tenant_and_source_corruption_fail_closed(http_context: Any) -> None:
    """Source corruption remains a governed failure under authorized context."""
    _, database, collections = http_context
    receivable, aging, dunning = _source_values(AUTHORIZED_TENANT)
    CommercialReceivableRegistry.ensure_indexes(collections[0])
    CommercialReceivableRegistry.create(receivable, collections[0])
    collections[1].insert_one(aging.to_dict())
    collections[2].insert_one(dunning.to_dict())
    with _app(database) as client:
        assert (
            client.get(
                "/billing/intelligence/evidence?as_of=2026-09-12T12:00:00%2B00:00"
            ).status_code
            == 200
        )
    collections[0].update_one(
        {"tenant_id": AUTHORIZED_TENANT}, {"$set": {"receivable_fingerprint": "b" * 128}}
    )
    with _app(database) as client:
        response = client.get(
            "/billing/intelligence/evidence?as_of=2026-09-12T12:00:00%2B00:00"
        )
    assert response.status_code == 409
    assert collections[3].count_documents({"tenant_id": AUTHORIZED_TENANT}) == 1


# ARTIFACT: test_billing_intelligence_http_real_mongo.py
# VERSION: v1.1.0-M14-P6-BILLING-INTELLIGENCE-HTTP-REAL-MONGO-CERT
# AUTHORITY BOUNDARY: Host HTTP composition certificate only.
# TENANT POSTURE: canonical route scope comes only from TenantAuthorizationContext.
# FAIL-CLOSED POSTURE: authorization and source corruption cannot produce success.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
