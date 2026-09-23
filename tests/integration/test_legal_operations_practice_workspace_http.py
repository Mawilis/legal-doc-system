"""D11 direct HTTP certificate for the Legal Practice workspace.

TITLE: WILSY OS Legal Practice Workspace HTTP Certificate
VERSION: v1.0.0-L8-7D11-LEGAL-PRACTICE-WORKSPACE-HTTP-CERT
AUTHORITY: Direct HTTP certificate for the D11 read-only practice projection.
EPITOME: Prove conjunctive same-principal/tenant/role admission, exact current
         lifecycle field whitelists, deterministic summary counts, opaque
         evidence locators, bounded role denial and no financial truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/integration/test_legal_operations_practice_workspace_http.py
COLLABORATION / OWNERSHIP: Certificate for tools/eos/api/legal_operations_router.py
                            v1.7.0-L8-7D11-LEGAL-PRACTICE-WORKSPACE-API.
CERTIFICATION / UPDATE DATE: 2026-09-23
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque identities only.
TENANT BOUNDARY: Every successful workspace context is exact tenant/principal/
                 published legal-practice business role.
AUTHORITY BOUNDARY: Read projection certificate only; no lifecycle mutation,
                    service execution, return, invoice, payment or settlement.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
FAIL-CLOSED DECLARATION: Scope mismatch, unsupported role and malformed
                         projection reject without fallback or inferred truth.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

import tools.eos.api.legal_operations_router as legal_router
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)


VERSION = "v1.0.0-L8-7D11-LEGAL-PRACTICE-WORKSPACE-HTTP-CERT"
TENANT = "tenant-law"
PRINCIPAL = "principal-law"
EVIDENCE = "a" * 128


class _Value:
    """Minimal current P1-shaped projection double used at the read-model seam."""

    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def to_dict(self) -> dict[str, object]:
        """Return one canonical-like current payload plus one forbidden extra."""
        return {**self._payload, "credentials": "must-not-leak"}


class _Database:
    """Minimal database surface used by the D11 callback."""

    def get_collection(self, name: str) -> object:
        """Return one opaque collection marker."""
        assert name == legal_router.LIFECYCLE_COLLECTION
        return object()


def _context(
    *,
    tenant: str = TENANT,
    principal: str = PRINCIPAL,
    role: str = "tenant_legal_partner",
) -> TenantAuthorizationContext:
    """Build one already-authorized synthetic context."""
    identity = SovereignIdentity(
        identity_id=principal,
        tenant_id=tenant,
        username="operator",
        email="operator@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    decision = TenantAuthorizationDecision(
        authorized=True,
        reason=TenantAuthorizationReason.AUTHORIZED,
        business_role=role,
        authorization_role="LEGAL_PARTNER",
    )
    return TenantAuthorizationContext(
        identity=identity,
        tenant_id=tenant,
        decision=decision,
    )


def _payloads() -> dict[str, dict[str, object]]:
    """Return one current row for every D11 lifecycle family."""
    return {
        "LegalInstruction": {
            "instruction_id": "instruction-1",
            "case_matter_id": "matter-1",
            "document_id": "document-1",
            "registered_at": "2026-09-23T14:00:00+00:00",
            "state": "ACCEPTED",
        },
        "ProcessDocument": {
            "document_id": "document-1",
            "case_matter_id": "matter-1",
            "document_type": "summons",
            "registered_at": "2026-09-23T14:01:00+00:00",
            "state": "ALLOCATED_TO_DEPUTY",
        },
        "ServiceAttempt": {
            "attempt_id": "attempt-1",
            "instruction_id": "instruction-1",
            "document_id": "document-1",
            "deputy_id": "deputy-1",
            "allocated_at": "2026-09-23T14:10:00+00:00",
            "state": "ATTEMPTED",
        },
        "ServiceExecution": {
            "service_execution_id": "execution-1",
            "attempt_id": "attempt-1",
            "instruction_id": "instruction-1",
            "document_id": "document-1",
            "outcome": "COMPLETED",
            "executed_at": "2026-09-23T14:20:00+00:00",
        },
        "ReturnOfService": {
            "return_id": "return-1",
            "instruction_id": "instruction-1",
            "document_id": "document-1",
            "attempt_id": "attempt-1",
            "service_execution_id": "execution-1",
            "service_outcome": "COMPLETED",
            "generated_at": "2026-09-23T14:30:00+00:00",
            "state": "GENERATED",
        },
    }


def _install_projection_seams(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep HTTP composition real while replacing only persistence/read seams."""
    payloads = _payloads()

    def fake_list(**kwargs: Any) -> tuple[object, ...]:
        assert kwargs["tenant_id"] == TENANT
        entity_type = kwargs["entity_type"]
        assert kwargs["session"] == "snapshot-session"
        return (SimpleNamespace(current=_Value(payloads[entity_type])),)

    monkeypatch.setattr(legal_router, "list_entity_read_models", fake_list)
    monkeypatch.setattr(
        legal_router.LegalOperationsLifecycleRegistry,
        "get_snapshot_evidence_identity",
        staticmethod(lambda value, collection, session=None: EVIDENCE),
    )
    monkeypatch.setattr(
        legal_router,
        "_workspace_projection_transaction",
        lambda callback: callback("snapshot-session", _Database()),
    )


def _app(context: TenantAuthorizationContext) -> FastAPI:
    """Mount the real router with all four D11 authorization dependencies."""
    app = FastAPI()
    for dependency in (
        legal_router._INSTRUCTION_READ,
        legal_router._ALLOCATION_READ,
        legal_router._ATTEMPT_READ,
        legal_router._RETURN_READ,
    ):
        app.dependency_overrides[dependency] = lambda context=context: context
    app.include_router(legal_router.router)
    return app


def test_workspace_http_projects_current_lifecycle_and_summary(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One authorized practice request returns the bounded D11 workspace."""
    _install_projection_seams(monkeypatch)

    response = TestClient(_app(_context())).get("/legal-operations/workspace")

    assert response.status_code == 200
    payload = response.json()
    assert payload["schema"] == "WILSY-LEGAL-OPERATIONS-PRACTICE-WORKSPACE/V1"
    assert payload["version"] == "v1.7.0-L8-7D11-LEGAL-PRACTICE-WORKSPACE-API"
    assert payload["tenant_id"] == TENANT
    assert payload["visibility"] == "LEGAL_PRACTICE_WORKSPACE"
    assert payload["summary"] == {
        "instructions_total": 1,
        "instructions_registered": 0,
        "instructions_accepted": 1,
        "instructions_closed": 0,
        "instructions_cancelled": 0,
        "documents_total": 1,
        "documents_registered": 0,
        "documents_received": 0,
        "documents_allocated": 1,
        "documents_returned": 0,
        "attempts_total": 1,
        "attempts_allocated": 0,
        "attempts_attempted": 1,
        "attempts_completed": 0,
        "attempts_not_completed": 0,
        "attempts_cancelled": 0,
        "executions_total": 1,
        "executions_completed": 1,
        "executions_not_completed": 0,
        "returns_total": 1,
    }
    assert payload["instructions"][0]["evidence_identity"] == EVIDENCE
    assert payload["executions"][0]["outcome"] == "COMPLETED"
    assert payload["returns"][0]["state"] == "GENERATED"

    serialized = str(payload).lower()
    for forbidden in (
        "credentials",
        "client_name",
        "payment",
        "settlement",
        "paid_state",
        "ai_score",
    ):
        assert forbidden not in serialized


@pytest.mark.parametrize(
    "role",
    (
        "tenant_legal_partner",
        "tenant_legal_attorney",
        "tenant_legal_paralegal",
        "tenant_legal_secretary",
    ),
)
def test_workspace_context_accepts_only_published_practice_roles(role: str) -> None:
    """Every published D11 practice role may compose an exact shared context."""
    context = _context(role=role)
    assert legal_router._workspace_context(context, context).decision.business_role == role


@pytest.mark.parametrize(
    "role",
    ("tenant_legal_finance", "tenant_legal_client", "tenant_sheriff", "tenant_deputy"),
)
def test_workspace_context_rejects_non_practice_roles(role: str) -> None:
    """Finance/client/field roles cannot acquire practice workspace by presentation."""
    context = _context(role=role)
    with pytest.raises(HTTPException) as caught:
        legal_router._workspace_context(context)
    assert caught.value.status_code == 403
    assert caught.value.detail == "LEGAL_OPERATIONS_WORKSPACE_DENIED"


def test_workspace_context_rejects_cross_scope_dependencies() -> None:
    """Four permission checks may not be spliced across principals or tenants."""
    first = _context()
    foreign_tenant = _context(tenant="tenant-other")
    foreign_principal = _context(principal="principal-other")

    for other in (foreign_tenant, foreign_principal):
        with pytest.raises(HTTPException) as caught:
            legal_router._workspace_context(first, other)
        assert caught.value.status_code == 403
        assert caught.value.detail == "LEGAL_OPERATIONS_WORKSPACE_SCOPE_MISMATCH"


def test_workspace_row_whitelist_discards_unapproved_current_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Transport exposes only D11 fields plus one opaque evidence locator."""
    _install_projection_seams(monkeypatch)
    rows = legal_router._workspace_rows(
        tenant_id=TENANT,
        entity_type="LegalInstruction",
        collection=object(),
        session="snapshot-session",
    )
    assert rows == [
        {
            "instruction_id": "instruction-1",
            "case_matter_id": "matter-1",
            "document_id": "document-1",
            "registered_at": "2026-09-23T14:00:00+00:00",
            "state": "ACCEPTED",
            "evidence_identity": EVIDENCE,
        }
    ]


def test_workspace_version_and_authority_surface_are_frozen() -> None:
    """D11 remains read-only and bound to the intended production version."""
    assert legal_router.VERSION == "v1.7.0-L8-7D11-LEGAL-PRACTICE-WORKSPACE-API"
    assert VERSION == "v1.0.0-L8-7D11-LEGAL-PRACTICE-WORKSPACE-HTTP-CERT"
    assert not hasattr(legal_router, "insert_one")
    assert not hasattr(legal_router, "update_one")
    assert not hasattr(legal_router, "delete_one")


# ARTIFACT: test_legal_operations_practice_workspace_http.py
# VERSION: v1.0.0-L8-7D11-LEGAL-PRACTICE-WORKSPACE-HTTP-CERT
# AUTHORITY BOUNDARY: D11 read-only practice workspace HTTP certificate
# TENANT POSTURE: same exact tenant/principal/published-practice-role required
# FAIL-CLOSED POSTURE: scope/role/projection drift rejects without fallback
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
