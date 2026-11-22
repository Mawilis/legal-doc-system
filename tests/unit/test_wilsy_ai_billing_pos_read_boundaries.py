"""WILSY OS governed financial-source read certification.

TITLE: Billing and POS Read-Only AI Source Contract Tests
VERSION: v1.0.0-FINANCIAL-SOURCE-READ-NEGATIVE-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Verify canonical Billing evidence and POS location counts cannot
         grant source access or assert electronic settlement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_wilsy_ai_billing_pos_read_boundaries.py
CERTIFICATION / UPDATE DATE: 2026-11-22
CHANGELOG: v1.0.0-FINANCIAL-SOURCE-READ-NEGATIVE-CERT validates read-only
           authenticated Billing evidence and exact-tenant POS location.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Pure mock collections; no real money or credentials.
TENANT BOUNDARY: Scope tested across principal, tenant and POS location.
AUTHORITY BOUNDARY: No grants, admission bypass or mutation.
FINANCIAL AUTHORITY BOUNDARY: Kennel executes settlements exclusively.
FAIL-CLOSED DECLARATION: Inconsistent source evidence rejects before reply.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from tools.eos.api import billing_router, pos_workspace_router
from tools.eos.saas.billing.pos_workspace_service import (
    POSWorkspaceService, POSWorkspaceServiceError,
)


class CountSales:
    def __init__(self, records):
        self.records = records
        self.queries = []

    def count_documents(self, query, *, session):
        assert session is not None
        self.queries.append(dict(query))
        return sum(
            1 for record in self.records
            if all(record.get(key) == value for key, value in query.items())
        )


def _pos_service(monkeypatch, records):
    service = object.__new__(POSWorkspaceService)
    service._sales = CountSales(records)
    admission = Mock()
    monkeypatch.setattr(POSWorkspaceService, "_admit", admission)
    return service, admission


def test_pos_summary_requires_live_source_admission_and_never_claims_settlement(monkeypatch):
    service, admitted = _pos_service(monkeypatch, [
        {"tenant_id": "TENANT_A", "location_id": "BRANCH_1", "status": "COMPLETED_COMMERCIAL"},
        {"tenant_id": "TENANT_A", "location_id": "BRANCH_1", "status": "OPEN"},
        {"tenant_id": "TENANT_A", "location_id": "BRANCH_2", "status": "VOIDED"},
        {"tenant_id": "TENANT_B", "location_id": "BRANCH_1", "status": "COMPLETED_COMMERCIAL"},
    ])
    session = object()
    result = service.read_commercial_summary(
        tenant_id="TENANT_A", principal_id="PRINCIPAL_A", location_id="BRANCH_1",
        session=session,
    )
    admitted.assert_called_once_with(
        tenant_id="TENANT_A", principal_id="PRINCIPAL_A",
        location_id="BRANCH_1", session=session,
    )
    assert result["tenant_id"] == "TENANT_A"
    assert result["principal_id"] == "PRINCIPAL_A"
    assert result["location_id"] == "BRANCH_1"
    assert result["counts"] == {
        "total": 2, "DRAFT": 0, "OPEN": 1, "COMPLETED_COMMERCIAL": 1,
        "VOIDED": 0,
    }
    assert result["authority"]["settlement_not_asserted"] is True
    assert result["authority"]["financial_execution"] is False
    assert all(query["tenant_id"] == "TENANT_A" and query["location_id"] == "BRANCH_1"
               for query in service._sales.queries)


def test_pos_summary_rejects_unknown_sale_status(monkeypatch):
    service, _ = _pos_service(monkeypatch, [
        {"tenant_id": "TENANT_A", "location_id": "BRANCH_1", "status": "SETTLED"},
    ])
    with pytest.raises(POSWorkspaceServiceError, match="POS_COMMERCIAL_SUMMARY_INCONSISTENT"):
        service.read_commercial_summary(
            tenant_id="TENANT_A", principal_id="PRINCIPAL_A",
            location_id="BRANCH_1", session=object(),
        )


def test_pos_summary_rejects_revoked_location_at_admission(monkeypatch):
    service, admitted = _pos_service(monkeypatch, [])
    admitted.side_effect = POSWorkspaceServiceError("POS_LOCATION_ACCESS_DENIED")
    with pytest.raises(POSWorkspaceServiceError, match="POS_LOCATION_ACCESS_DENIED"):
        service.read_commercial_summary(
            tenant_id="TENANT_A", principal_id="PRINCIPAL_A",
            location_id="BRANCH_1", session=object(),
        )
    assert service._sales.queries == []


def test_pos_router_requires_canonical_pos_read_dependency():
    route = next(
        route for route in pos_workspace_router.router.routes
        if getattr(route, "path", "") == "/pos/locations/{location_id}/commercial-summary"
    )
    assert "GET" in route.methods
    assert any(dependency.call is pos_workspace_router._READ
               for dependency in route.dependant.dependencies)


def test_billing_verified_evidence_read_is_immutable(monkeypatch):
    identity = "a" * 128
    observed = []
    def get_evidence(tenant_id, evidence_identity, collection):
        observed.append((tenant_id, evidence_identity, collection))
        return object()
    monkeypatch.setattr(billing_router.BillingIntelligenceRegistry, "get", get_evidence)
    monkeypatch.setattr(
        billing_router.BillingIntelligenceOrchestrator,
        "response_payload",
        lambda value: {"tenant_id": "TENANT_A", "evidence_identity": identity},
    )
    collection = object()
    monkeypatch.setattr(
        billing_router, "_require_db",
        lambda: {billing_router.BILLING_INTELLIGENCE_EVIDENCE_COLLECTION: collection},
    )
    auth = SimpleNamespace(
        tenant_id="TENANT_A",
        identity=SimpleNamespace(identity_id="PRINCIPAL_A"),
    )
    result = asyncio.run(billing_router.read_verified_billing_intelligence_evidence(
        identity, authorization=auth,
    ))
    assert observed == [("TENANT_A", identity, collection)]
    assert result["schema"] == "WILSY-BILLING-VERIFIED-EVIDENCE-READ/V1"
    assert result["principal_id"] == "PRINCIPAL_A"
    assert result["authority"]["financial_execution"] is False
    assert result["authority"]["settlement_not_asserted"] is True


def test_billing_rejects_mismatched_source_identity(monkeypatch):
    identity = "a" * 128
    monkeypatch.setattr(billing_router.BillingIntelligenceRegistry, "get", lambda *args: object())
    monkeypatch.setattr(
        billing_router.BillingIntelligenceOrchestrator,
        "response_payload",
        lambda value: {"tenant_id": "TENANT_B", "evidence_identity": identity},
    )
    monkeypatch.setattr(
        billing_router, "_require_db",
        lambda: {billing_router.BILLING_INTELLIGENCE_EVIDENCE_COLLECTION: object()},
    )
    auth = SimpleNamespace(
        tenant_id="TENANT_A", identity=SimpleNamespace(identity_id="PRINCIPAL_A"),
    )
    with pytest.raises(HTTPException) as error:
        asyncio.run(billing_router.read_verified_billing_intelligence_evidence(
            identity, authorization=auth,
        ))
    assert error.value.status_code == 503
    assert error.value.detail == "BILLING_EVIDENCE_NOT_VERIFIED"


def test_billing_route_does_not_collect_or_persist():
    source = Path(billing_router.__file__).read_text(encoding="utf-8")
    start = source.index("async def read_verified_billing_intelligence_evidence")
    end = source.index('@router.get("/intelligence/evidence"', start)
    route_body = source[start:end]
    assert "collect_and_persist" not in route_body.split('    except BillingIntelligenceRegistryError')[0]
    assert "BillingIntelligenceRegistry.get(" in route_body
    route = next(
        route for route in billing_router.router.routes
        if getattr(route, "path", "") == "/billing/intelligence/verified-evidence/{evidence_identity}"
    )
    assert "GET" in route.methods
    assert any(dependency.call is billing_router._BILLING_INTELLIGENCE_EVIDENCE_READ_AUTHORIZATION
               for dependency in route.dependant.dependencies)


# ARTIFACT: test_wilsy_ai_billing_pos_read_boundaries.py
# VERSION: v1.0.0-FINANCIAL-SOURCE-READ-NEGATIVE-CERT
# TENANT BOUNDARY: Exact tenant, principal and POS location.
# AUTHORITY BOUNDARY: Read-only evidence, no financial execution.
# FAIL-CLOSED POSTURE: Invalid and cross-tenant sources rejected.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
