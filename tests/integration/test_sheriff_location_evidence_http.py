"""Sheriff GPS read endpoint tests: office scope fails closed and audits access."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import tools.eos.api.legal_operations_router as read_api
from tools.eos.api.errors import register_error_handlers
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)

TENANT, PRINCIPAL, OFFICE, ATTEMPT = (
    "tenant-sheriff-location", "sheriff-principal", "sheriff-office-1", "attempt-sheriff-1"
)


class Session:
    in_transaction = True


class Database:
    def get_collection(self, name: str) -> object:
        return SimpleNamespace(name=name)


def context() -> TenantAuthorizationContext:
    identity = SovereignIdentity(
        identity_id=PRINCIPAL,
        tenant_id=TENANT,
        username="sheriff",
        email="sheriff@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
        session_reference=None,
    )
    decision = TenantAuthorizationDecision(
        True,
        TenantAuthorizationReason.AUTHORIZED,
        "tenant_sheriff",
        "SHERIFF",
    )
    return TenantAuthorizationContext(identity, TENANT, decision)


def app() -> FastAPI:
    value = FastAPI()
    register_error_handlers(value, debug=False)
    value.dependency_overrides[read_api._QUEUE_READ] = context
    value.include_router(read_api.router, prefix="/api")
    return value


def configure_single_office(monkeypatch: pytest.MonkeyPatch, offices: list[Any]) -> list[dict[str, Any]]:
    database, session = Database(), Session()
    accesses: list[dict[str, Any]] = []
    pointer = SimpleNamespace(
        authority_evidence_reference="allocation-command-1",
        authority_evidence_fingerprint="a" * 128,
    )
    receipt = SimpleNamespace(
        fingerprint="a" * 128,
        tenant_id=TENANT,
        document_id="document-1",
        instruction_id="instruction-1",
        deputy_id="deputy-1",
        allocation_evidence_reference="allocation-1",
        sheriff_office_id=OFFICE,
    )
    attempt = SimpleNamespace(
        attempt_id=ATTEMPT,
        document_id="document-1",
        instruction_id="instruction-1",
        deputy_id="deputy-1",
        allocation_evidence_reference="allocation-1",
    )
    monkeypatch.setattr(read_api, "_workspace_projection_transaction", lambda callback: callback(session, database))
    monkeypatch.setattr(read_api, "list_entity_read_models", lambda **kwargs: offices)
    monkeypatch.setattr(read_api, "get_entity_read_model", lambda **kwargs: SimpleNamespace(current=attempt))
    monkeypatch.setattr(
        read_api,
        "ProcessServiceAllocationRegistry",
        SimpleNamespace(
            get_current=lambda *args, **kwargs: pointer,
            get_receipt_by_allocation_command_id=lambda *args, **kwargs: receipt,
        ),
    )
    monkeypatch.setattr(
        read_api,
        "ProcessServiceLocationEvidenceRegistry",
        SimpleNamespace(
            list_observations_for_attempt=lambda *args, **kwargs: (
                {"observation_id": "location-1", "latitude": -26.2, "longitude": 28.0},
            ),
            record_access=lambda **kwargs: accesses.append(kwargs),
        ),
    )
    return accesses


def test_sheriff_location_read_is_scoped_to_one_canonical_office_and_audited(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    office = SimpleNamespace(current=SimpleNamespace(sheriff_office_id=OFFICE))
    accesses = configure_single_office(monkeypatch, [office])
    with TestClient(app()) as client:
        response = client.get(f"/api/legal-operations/sheriff/attempts/{ATTEMPT}/location-evidence")
    assert response.status_code == 200
    body = response.json()
    assert body["sheriff_office_id"] == OFFICE
    assert body["visibility"] == "ONE_CANONICAL_SHERIFF_OFFICE_LOCATION_EVIDENCE"
    assert body["observations"][0]["observation_id"] == "location-1"
    assert len(accesses) == 1
    assert accesses[0]["actor_principal_id"] == PRINCIPAL
    assert accesses[0]["actor_scope"] == "SHERIFF_OFFICE:" + OFFICE
    assert accesses[0]["purpose"] == "SHERIFF_OFFICE_LOCATION_EVIDENCE_READ"


def test_sheriff_location_read_refuses_multi_office_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    first = SimpleNamespace(current=SimpleNamespace(sheriff_office_id="office-1"))
    second = SimpleNamespace(current=SimpleNamespace(sheriff_office_id="office-2"))
    accesses = configure_single_office(monkeypatch, [first, second])
    with TestClient(app()) as client:
        response = client.get(f"/api/legal-operations/sheriff/attempts/{ATTEMPT}/location-evidence")
    assert response.status_code == 403
    assert response.json()["detail"] == "SHERIFF_OFFICE_BINDING_REQUIRED"
    assert accesses == []


def test_sheriff_location_read_refuses_receipt_from_another_office(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    office = SimpleNamespace(current=SimpleNamespace(sheriff_office_id=OFFICE))
    configure_single_office(monkeypatch, [office])
    original = read_api.ProcessServiceAllocationRegistry
    receipt = SimpleNamespace(
        fingerprint="a" * 128, tenant_id=TENANT, document_id="document-1",
        instruction_id="instruction-1", deputy_id="deputy-1",
        allocation_evidence_reference="allocation-1", sheriff_office_id="foreign-office",
    )
    pointer = SimpleNamespace(
        authority_evidence_reference="allocation-command-1",
        authority_evidence_fingerprint="a" * 128,
    )
    monkeypatch.setattr(
        read_api, "ProcessServiceAllocationRegistry",
        SimpleNamespace(
            get_current=lambda *args, **kwargs: pointer,
            get_receipt_by_allocation_command_id=lambda *args, **kwargs: receipt,
        ),
    )
    with TestClient(app()) as client:
        response = client.get(f"/api/legal-operations/sheriff/attempts/{ATTEMPT}/location-evidence")
    assert response.status_code == 404
    assert original is not None


# ARTIFACT: test_sheriff_location_evidence_http.py
# AUTHORITY: Sheriff tenant IAM plus exactly one canonical SheriffOffice; multi-office tenants fail closed.
# AUDIT: Metadata-only access event is appended for every successful location evidence read.
# END OF WILSY OS SOVEREIGN ARTIFACT
