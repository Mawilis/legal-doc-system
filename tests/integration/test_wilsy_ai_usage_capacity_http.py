"""WILSY OS M13-P6D direct HTTP certificate for WILSY AI capacity evidence.

TITLE: WILSY AI Usage-Capacity HTTP/Application Contract Certificate
VERSION: v1.0.0-M13-P6D-WILSY-AI-CAPACITY-HTTP-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certify the authorized FastAPI transport seam over P6C with
         deterministic caller-owned session/transaction behavior and strict
         fail-closed translation, without contacting MongoDB.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_wilsy_ai_usage_capacity_http.py
COLLABORATION / OWNERSHIP: Direct application certificate for billing_router.py;
                            P4/P6B/P6A/P6C remain the domain authorities.
CERTIFICATION / UPDATE DATE: 2026-09-13
CHANGELOG: v1.0.0-M13-P6D establishes the direct HTTP/application contract
           certificate for the own-tenant WILSY AI capacity evidence route.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identities and inert persistence seams;
                             no Mongo, secrets, clients, or providers.
TENANT BOUNDARY: Tenant scope is supplied only by TenantAuthorizationContext.
AUTHORITY BOUNDARY: HTTP/session composition certificate only; P6C/P6A own
                    composition and capacity semantics.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution/settlement.
REAL-MONGO BOUNDARY: Deliberately excluded; a separate host certificate owns it.
FAIL-CLOSED DECLARATION: Domain failures never become fabricated HTTP 200.
"""

from __future__ import annotations

import ast
import importlib
from datetime import datetime, timezone
from pathlib import Path
import sys
import types
from typing import Any, Iterator, cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext


ROUTER_MODULE = "tools.eos.api.billing_router"
REGISTRY_MODULE = "tools.eos.saas.billing.billing_registry"
ROUTER_PATH = Path("tools/eos/api/billing_router.py")
EXPECTED_ROUTER_VERSION = "v1.9.0-M13-P6D-WILSY-AI-CAPACITY-HTTP"
TEST_VERSION = "v1.0.0-M13-P6D-WILSY-AI-CAPACITY-HTTP-CERT"
AS_OF = "2026-09-13T12:00:00+00:00"
AS_OF_QUERY = AS_OF.replace("+", "%2B")
TENANT = "tenant-p6d-http"


@pytest.fixture()
def router_module() -> Iterator[Any]:
    """Import the production router with only its legacy registry inert."""
    previous_registry = sys.modules.get(REGISTRY_MODULE)
    previous_router = sys.modules.pop(ROUTER_MODULE, None)
    stub = types.ModuleType(REGISTRY_MODULE)
    setattr(stub, "BillingRegistry", type("BillingRegistry", (), {}))
    setattr(stub, "get_billing_registry", lambda: object())
    setattr(stub, "db", {})
    setattr(stub, "client", object())
    setattr(stub, "platform_invoices_coll", object())
    setattr(stub, "client_invoices_coll", object())
    setattr(stub, "payments_coll", object())
    sys.modules[REGISTRY_MODULE] = stub
    try:
        yield importlib.import_module(ROUTER_MODULE)
    finally:
        sys.modules.pop(ROUTER_MODULE, None)
        if previous_router is not None:
            sys.modules[ROUTER_MODULE] = previous_router
        if previous_registry is not None:
            sys.modules[REGISTRY_MODULE] = previous_registry
        else:
            sys.modules.pop(REGISTRY_MODULE, None)


class _Session:
    """Deterministic fake Mongo session exposing caller lifecycle ownership."""

    def __init__(self) -> None:
        self.events: list[str] = []
        self.in_transaction = False

    def __enter__(self) -> "_Session":
        self.events.append("enter")
        return self

    def __exit__(self, *args: object) -> None:
        self.events.append("exit")

    def start_transaction(self) -> None:
        assert self.in_transaction is False
        self.events.append("start")
        self.in_transaction = True

    def commit_transaction(self) -> None:
        assert self.in_transaction is True
        self.events.append("commit")
        self.in_transaction = False

    def abort_transaction(self) -> None:
        assert self.in_transaction is True
        self.events.append("abort")
        self.in_transaction = False


class _Client:
    """Fake client proving exactly one router-opened session."""

    def __init__(self) -> None:
        self.session = _Session()
        self.open_count = 0

    def start_session(self) -> _Session:
        self.open_count += 1
        return self.session


class _Database:
    """Fake database recording the exact injected P4/P6B collection names."""

    def __init__(self) -> None:
        self.collection_names: list[str] = []

    def __getitem__(self, name: str) -> object:
        self.collection_names.append(name)
        return object()


class _Capacity:
    """Canonical response fixture with no transport-derived fields."""

    def __init__(self) -> None:
        self.payload = {
            "schema": "WILSY-AI-USAGE-CAPACITY/V1",
            "capacity_version": "v1.0.1-M13-P6A",
            "tenant_id": TENANT,
            "fingerprint": "c" * 128,
        }

    def to_dict(self) -> dict[str, object]:
        return dict(self.payload)


def _authorized_context(tenant_id: str = TENANT) -> TenantAuthorizationContext:
    """Construct synthetic context; authorization remains production-owned."""
    return TenantAuthorizationContext(
        identity=cast(Any, types.SimpleNamespace(identity_id="principal-p6d")),
        tenant_id=tenant_id,
        decision=cast(Any, types.SimpleNamespace(authorized=True)),
    )


def _install_seam(
    module: Any,
    monkeypatch: Any,
    failure: BaseException | None = None,
) -> tuple[_Client, _Database, list[dict[str, Any]]]:
    """Inject inert DB/P6C dependencies while retaining the real endpoint."""
    client = _Client()
    database = _Database()
    calls: list[dict[str, Any]] = []

    class _Orchestrator:
        @classmethod
        def from_collections(cls, **collections: object) -> "_Orchestrator":
            calls.append({"factory": collections})
            return cls()

        def derive_capacity(self, **kwargs: Any) -> _Capacity:
            calls.append({"derive": kwargs})
            assert kwargs["session"] is client.session
            assert client.session.in_transaction is True
            if failure is not None:
                raise failure
            return _Capacity()

    monkeypatch.setattr(module, "_require_db", lambda: database)
    monkeypatch.setattr(module, "_require_mongo_client", lambda: client)
    monkeypatch.setattr(module, "WilsyAIUsageCapacityOrchestrator", _Orchestrator)
    return client, database, calls


def _app(module: Any, context: TenantAuthorizationContext | None) -> FastAPI:
    """Mount the real router and override only its exact P6D dependency."""
    app = FastAPI()
    app.include_router(module.router)
    if context is not None:
        app.dependency_overrides[module._WILSY_AI_CAPACITY_READ_AUTHORIZATION] = (
            lambda: context
        )
    return app


def _effective_p6d_routes(app: FastAPI) -> list[Any]:
    """Traverse FastAPI's effective included-router view across versions."""
    matches: list[Any] = []
    for route in app.routes:
        effective_contexts = getattr(route, "effective_route_contexts", None)
        if callable(effective_contexts):
            for context in cast(Iterator[Any], effective_contexts()):
                candidate = context.original_route
                if getattr(candidate, "path", "") == "/billing/wilsy-ai/usage-capacity/evidence":
                    matches.append(candidate)
        elif getattr(route, "path", "") == "/billing/wilsy-ai/usage-capacity/evidence":
            matches.append(route)
    return matches


def test_production_anchor_route_and_authorization(router_module: Any) -> None:
    """The canonical route and immutable dependency are present exactly once."""
    module = router_module
    assert module.VERSION == EXPECTED_ROUTER_VERSION
    app = _app(module, _authorized_context())
    routes = _effective_p6d_routes(app)
    assert len(routes) == 1
    assert routes[0].methods == {"GET"}
    dependency = module._WILSY_AI_CAPACITY_READ_AUTHORIZATION
    assert dependency.permission_id == "wilsy_ai:usage_capacity:read"
    assert dependency.operation == "wilsy_ai_usage_capacity_read"
    assert any(item.call is dependency for item in routes[0].dependant.dependencies)


def test_authorized_context_and_exact_p6c_arguments(
    router_module: Any,
    monkeypatch: Any,
) -> None:
    """Context tenant wins; only locator, snapshot, and active session cross P6C."""
    module = router_module
    client, database, calls = _install_seam(module, monkeypatch)
    app = _app(module, _authorized_context())
    with TestClient(app) as http:
        response = http.get(
            f"/billing/wilsy-ai/usage-capacity/evidence?entitlement_id=ent-1&as_of={AS_OF_QUERY}"
            "&tenant_id=attacker-query",
        )
    assert response.status_code == 200
    derive = next(item["derive"] for item in calls if "derive" in item)
    assert derive == {
        "tenant_id": TENANT,
        "entitlement_id": "ent-1",
        "as_of": datetime(2026, 9, 13, 12, tzinfo=timezone.utc),
        "session": client.session,
    }
    assert database.collection_names == [
        "wilsy_ai_entitlements",
        "wilsy_ai_usage_observations",
    ]
    assert client.open_count == 1
    assert client.session.events == ["enter", "start", "commit", "exit"]


def test_canonical_response_and_no_router_aggregation(
    router_module: Any,
    monkeypatch: Any,
) -> None:
    """The response is exactly P6A serialization, with no HTTP-added fields."""
    module = router_module
    _install_seam(module, monkeypatch)
    with TestClient(_app(module, _authorized_context())) as http:
        response = http.get(
            f"/billing/wilsy-ai/usage-capacity/evidence?entitlement_id=ent-1&as_of={AS_OF_QUERY}"
        )
    assert response.status_code == 200
    assert response.json() == _Capacity().to_dict()
    source = ROUTER_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    endpoint = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.AsyncFunctionDef)
        and node.name == "get_wilsy_ai_usage_capacity_evidence"
    )
    derive_calls = [
        node
        for node in ast.walk(endpoint)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "derive_capacity"
    ]
    assert len(derive_calls) == 1
    assert {
        keyword.arg for keyword in derive_calls[0].keywords if keyword.arg
    } == {"tenant_id", "entitlement_id", "as_of", "session"}
    assert any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "to_dict"
        for node in ast.walk(endpoint)
    )
    names = {node.id for node in ast.walk(endpoint) if isinstance(node, ast.Name)}
    assert "get_tenant_id" not in names
    assert names.isdisjoint(
        {
            "module_id",
            "entitlement_revision",
            "entitlement_fingerprint",
            "usage_totals",
            "limits",
            "quota",
            "price",
            "overage",
        }
    )


def test_domain_failure_aborts_without_commit(
    router_module: Any,
    monkeypatch: Any,
) -> None:
    """A governed domain failure aborts exactly once and never returns success."""
    module = router_module
    client, _, _ = _install_seam(
        module,
        monkeypatch,
        module.WilsyAIUsageCapacityError("M13P6A_EVIDENCE_REQUIRED"),
    )
    with TestClient(_app(module, _authorized_context())) as http:
        response = http.get(
            f"/billing/wilsy-ai/usage-capacity/evidence?entitlement_id=ent-1&as_of={AS_OF_QUERY}"
        )
    assert response.status_code == 409
    assert response.json() == {"detail": "M13P6A_EVIDENCE_REQUIRED"}
    assert client.session.events == ["enter", "start", "abort", "exit"]


@pytest.mark.parametrize("as_of", ["2026-09-13T12:00:00", "not-a-time"])
def test_malformed_or_naive_as_of_fails_400(
    router_module: Any,
    monkeypatch: Any,
    as_of: str,
) -> None:
    """Explicit aware snapshots are mandatory and malformed values stop early."""
    module = router_module
    client, _, _ = _install_seam(module, monkeypatch)
    with TestClient(_app(module, _authorized_context())) as http:
        response = http.get(
            f"/billing/wilsy-ai/usage-capacity/evidence?entitlement_id=ent-1&as_of={as_of}"
        )
    assert response.status_code == 400
    assert client.open_count == 0


@pytest.mark.parametrize("entitlement_id", ["", " "])
def test_blank_entitlement_locator_fails_400(
    router_module: Any,
    monkeypatch: Any,
    entitlement_id: str,
) -> None:
    """The locator is explicit and cannot be normalized into another identity."""
    module = router_module
    client, _, _ = _install_seam(module, monkeypatch)
    with TestClient(_app(module, _authorized_context())) as http:
        response = http.get(
            "/billing/wilsy-ai/usage-capacity/evidence"
            f"?entitlement_id={entitlement_id}&as_of={AS_OF_QUERY}"
        )
    assert response.status_code == 400
    assert client.open_count == 0


@pytest.mark.parametrize(
    ("error_factory", "expected_status", "expected_detail"),
    [
        (
            lambda module: module.WilsyAIEntitlementRegistryError(
                "M13P4_ENTITLEMENT_NOT_FOUND"
            ),
            404,
            "M13P4_ENTITLEMENT_NOT_FOUND",
        ),
        (
            lambda module: module.WilsyAIEntitlementRegistryError(
                "M13P4_PERSISTENCE_UNAVAILABLE"
            ),
            503,
            "WILSY AI usage-capacity evidence unavailable",
        ),
        (
            lambda module: module.WilsyAIUsageObservationRegistryError(
                "M13P6B_PERSISTENCE_UNAVAILABLE"
            ),
            503,
            "WILSY AI usage-capacity evidence unavailable",
        ),
        (
            lambda module: module.WilsyAIUsageCapacityOrchestratorError(
                "M13P6C_TRANSACTION_REQUIRED"
            ),
            503,
            "WILSY AI usage-capacity evidence unavailable",
        ),
        (
            lambda module: module.WilsyAIUsageObservationRegistryError(
                "M13P5B_CORRUPT_OBSERVATION"
            ),
            409,
            "M13P5B_CORRUPT_OBSERVATION",
        ),
        (
            lambda module: module.WilsyAIUsageObservationRegistryError(
                "M13P6B_BINDING_CONFLICT"
            ),
            409,
            "M13P6B_BINDING_CONFLICT",
        ),
        (
            lambda module: module.WilsyAIUsageObservationRegistryError(
                "M13P6B_DUPLICATE_EVIDENCE"
            ),
            409,
            "M13P6B_DUPLICATE_EVIDENCE",
        ),
        (
            lambda module: module.WilsyAIUsageCapacityError(
                "M13P6A_EVIDENCE_REQUIRED"
            ),
            409,
            "M13P6A_EVIDENCE_REQUIRED",
        ),
        (
            lambda module: module.WilsyAIUsageCapacityError(
                "M13P6A_ENTITLEMENT_NOT_ACTIVE"
            ),
            409,
            "M13P6A_ENTITLEMENT_NOT_ACTIVE",
        ),
    ],
)
def test_governed_failures_map_without_fabricating_success(
    router_module: Any,
    monkeypatch: Any,
    error_factory: Any,
    expected_status: int,
    expected_detail: str,
) -> None:
    """P4/P6B/P6A/P6C failures retain bounded HTTP semantics."""
    module = router_module
    _install_seam(module, monkeypatch, error_factory(module))
    with TestClient(_app(module, _authorized_context())) as http:
        response = http.get(
            f"/billing/wilsy-ai/usage-capacity/evidence?entitlement_id=ent-1&as_of={AS_OF_QUERY}"
        )
    assert response.status_code == expected_status
    assert response.json() == {"detail": expected_detail}


def test_unexpected_exception_is_generic_503(
    router_module: Any,
    monkeypatch: Any,
) -> None:
    """Unknown internals are unavailable, never disclosed or returned as 200."""
    module = router_module
    _install_seam(module, monkeypatch, RuntimeError("internal-secret-detail"))
    with TestClient(_app(module, _authorized_context())) as http:
        response = http.get(
            f"/billing/wilsy-ai/usage-capacity/evidence?entitlement_id=ent-1&as_of={AS_OF_QUERY}"
        )
    assert response.status_code == 503
    assert response.json() == {
        "detail": "WILSY AI usage-capacity evidence unavailable"
    }
    assert "internal-secret-detail" not in response.text


def test_authorization_cannot_be_bypassed(router_module: Any) -> None:
    """Without the production dependency override, capacity cannot succeed."""
    with TestClient(_app(router_module, None), raise_server_exceptions=False) as http:
        response = http.get(
            f"/billing/wilsy-ai/usage-capacity/evidence?entitlement_id=ent-1&as_of={AS_OF_QUERY}"
        )
    assert response.status_code != 200


def test_existing_financial_firewall_remains_separate() -> None:
    """This certificate does not import or relocate financial-firewall tests."""
    source = Path(
        "tests/integration/test_billing_router_financial_truth_firewall_http.py"
    ).read_text(encoding="utf-8")
    assert "BILLING_EXECUTION_TRUTH_REQUIRES_KENNEL" in source
    assert "BILLING_REFUND_REQUIRES_KENNEL_EXECUTION" in source
    assert "BILLING_PARTIAL_SETTLEMENT_REQUIRES_KENNEL" in source


# =============================================================================
# WILSY OS SOVEREIGN ARTIFACT SEAL
# =============================================================================
# ARTIFACT: tests/integration/test_wilsy_ai_usage_capacity_http.py
# VERSION: v1.0.0-M13-P6D-WILSY-AI-CAPACITY-HTTP-CERT
# AUTHORITY BOUNDARY:
#   Direct HTTP/application certificate only; no domain authority is created.
# TENANT POSTURE:
#   Synthetic authorized context only; no tenant identity is inferred.
# FAIL-CLOSED POSTURE:
#   Domain and transport failures never become fabricated capacity success.
# FINANCIAL EXECUTION AUTHORITY:
#   Kennel EOS exclusively.
# REAL-MONGO:
#   NOT USED BY THIS CERTIFICATE; host-backed certification is a separate gate.
# END OF WILSY OS SOVEREIGN ARTIFACT
