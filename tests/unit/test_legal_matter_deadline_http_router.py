"""Direct certificate for the D3B1 legal matter deadline HTTP router.

TITLE: Wilsy OS Legal Matter Deadline HTTP Router Certificate
VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D3B1-DEADLINE-HTTP-ROUTER-CERT
AUTHORITY: Direct ASGI certificate for transport, authorization seams, and D3A delegation.
EPITOME: Proves exact route topology, strict request shape, transaction/session
         propagation, bounded projections, and service-error translation.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_matter_deadline_http_router.py
COLLABORATION / OWNERSHIP: Certificate owns synthetic transport fixtures only.
CERTIFICATION / UPDATE DATE: 2026-10-11
CHANGELOG: 2026-10-11 v1.0.0-LEGAL-OPS-COMPLETION-D3B1-DEADLINE-HTTP-ROUTER-CERT
           establishes isolated FastAPI evidence for the unmounted D3B1 router.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic opaque values only; no real customer data.
TENANT BOUNDARY: Dependency overrides supply one exact authorized tenant context.
AUTHORITY BOUNDARY: Transport certificate only; no domain, persistence, AI, or finance authority.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Extra authority fields, wrong matter correlation, conflicts,
                         outages, and unexpected transport failures reject.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import tools.eos.api.legal_matter_deadline_router as deadline_api
from tools.eos.api.tenant_authorization_http import TenantAuthorizationContext
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)
from tools.eos.legal_operations.domain.legal_matter_deadline import (
    LegalMatterDeadline,
    LegalMatterDeadlineKind,
    LegalMatterDeadlineSourceType,
    LegalMatterDeadlineStatus,
)
from tools.eos.legal_operations.service.legal_matter_deadline_service import (
    LegalMatterDeadlineServiceError,
)


TENANT = "tenant-deadline-http"
MATTER = "matter-deadline-http"
DEADLINE = "deadline-http-1"
NOW = datetime(2026, 10, 11, 10, 0, tzinfo=timezone.utc)
DUE = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)
FP = "a" * 128


def _context() -> TenantAuthorizationContext:
    identity = SovereignIdentity(
        identity_id="principal-deadline-http",
        tenant_id=TENANT,
        username="operator",
        email="operator@example.test",
        auth_method="TEST",
        status=PrincipalStatus.ACTIVE,
    )
    return TenantAuthorizationContext(
        identity=identity,
        tenant_id=TENANT,
        decision=TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
            "tenant_legal_partner",
            "LEGAL_PARTNER",
        ),
    )


def _deadline(*, matter: str = MATTER, deadline_id: str = DEADLINE) -> LegalMatterDeadline:
    return LegalMatterDeadline(
        tenant_id=TENANT,
        case_matter_id=matter,
        deadline_id=deadline_id,
        deadline_kind=LegalMatterDeadlineKind.FILING,
        title="Evidenced filing deadline",
        due_at=DUE,
        source_type=LegalMatterDeadlineSourceType.COURT_ORDER,
        source_reference="evidence://court-order/1",
        source_evidence_fingerprint=FP,
        jurisdiction_reference="jurisdiction://court/example",
        created_at=NOW,
        status=LegalMatterDeadlineStatus.ACTIVE,
    )


def _payload() -> dict[str, Any]:
    return {
        "deadline_id": DEADLINE,
        "deadline_kind": "FILING",
        "title": "Evidenced filing deadline",
        "due_at": DUE.isoformat(),
        "source_type": "COURT_ORDER",
        "source_reference": "evidence://court-order/1",
        "source_evidence_fingerprint": FP,
        "jurisdiction_reference": "jurisdiction://court/example",
        "created_at": NOW.isoformat(),
        "status": "ACTIVE",
    }


class _Session:
    def __init__(self) -> None:
        self.in_transaction = False
        self.events: list[str] = []

    def __enter__(self) -> "_Session":
        self.events.append("enter")
        return self

    def __exit__(self, *_args: object) -> None:
        self.events.append("exit")

    def start_transaction(self) -> None:
        self.in_transaction = True
        self.events.append("start")

    def commit_transaction(self) -> None:
        self.events.append("commit")
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.events.append("abort")
        self.in_transaction = False


class _Client:
    def __init__(self, session: _Session) -> None:
        self.session = session

    def start_session(self) -> _Session:
        return self.session


class _Database:
    def get_collection(self, name: str) -> str:
        return name


def _client(monkeypatch: pytest.MonkeyPatch, session: _Session | None = None) -> tuple[TestClient, _Session]:
    tx = session or _Session()
    monkeypatch.setattr(deadline_api, "_db_handles", lambda: (_Client(tx), _Database()))
    app = FastAPI()
    app.dependency_overrides[deadline_api._WRITE] = _context
    app.dependency_overrides[deadline_api._READ] = _context
    app.include_router(deadline_api.router, prefix="/api")
    return TestClient(app), tx


def test_router_topology_and_authorization_bindings_are_exact() -> None:
    assert deadline_api.router.prefix == "/legal-operations"
    assert deadline_api._WRITE.permission_id == "legal_operations:matter_deadline:write"
    assert deadline_api._WRITE.operation == "legal_matter_deadline_write"
    assert deadline_api._READ.permission_id == "legal_operations:matter_deadline:read"
    assert deadline_api._READ.operation == "legal_matter_deadline_read"
    routes = {
        (
            getattr(route, "path", ""),
            tuple(sorted(getattr(route, "methods", set()) or set())),
        )
        for route in deadline_api.router.routes
    }
    assert routes == {
        ("/legal-operations/matters/{case_matter_id}/deadlines", ("GET",)),
        ("/legal-operations/matters/{case_matter_id}/deadlines", ("POST",)),
        ("/legal-operations/matters/{case_matter_id}/deadlines/{deadline_id}", ("GET",)),
    }


def test_valid_post_delegates_exactly_once_with_same_active_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, session = _client(monkeypatch)
    calls: list[dict[str, Any]] = []

    def record(**kwargs: Any) -> LegalMatterDeadline:
        calls.append(kwargs)
        assert kwargs["tenant_id"] == TENANT
        assert kwargs["case_matter_id"] == MATTER
        assert kwargs["session"] is session
        assert session.in_transaction is True
        return _deadline()

    monkeypatch.setattr(deadline_api, "record_legal_matter_deadline", record)
    response = client.post(
        f"/api/legal-operations/matters/{MATTER}/deadlines",
        json=_payload(),
    )
    assert response.status_code == 200, response.text
    assert len(calls) == 1
    assert session.events == ["enter", "start", "commit", "exit"]
    assert response.json()["data"] == {
        "deadline_id": DEADLINE,
        "case_matter_id": MATTER,
        "deadline_kind": "FILING",
        "title": "Evidenced filing deadline",
        "due_at": DUE.isoformat(),
        "source_type": "COURT_ORDER",
        "jurisdiction_reference": "jurisdiction://court/example",
        "created_at": NOW.isoformat(),
        "supersedes_deadline_id": None,
        "status": "ACTIVE",
    }


@pytest.mark.parametrize("field", ("principal_id", "role", "permissions", "tenant_id", "payment_state", "ai_confidence"))
def test_post_rejects_extra_authority_fields(
    monkeypatch: pytest.MonkeyPatch,
    field: str,
) -> None:
    client, _ = _client(monkeypatch)
    payload = _payload()
    payload[field] = "forbidden"
    response = client.post(
        f"/api/legal-operations/matters/{MATTER}/deadlines",
        json=payload,
    )
    assert response.status_code == 422


def test_post_invalid_naive_time_maps_to_bounded_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, session = _client(monkeypatch)

    def record(**_kwargs: Any) -> LegalMatterDeadline:
        raise LegalMatterDeadlineServiceError("DEADLINE_INVALID")

    monkeypatch.setattr(deadline_api, "record_legal_matter_deadline", record)
    payload = _payload()
    payload["due_at"] = "2026-10-20T10:00:00"
    response = client.post(
        f"/api/legal-operations/matters/{MATTER}/deadlines",
        json=payload,
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "LEGAL_MATTER_DEADLINE_INVALID"}
    assert "abort" in session.events


@pytest.mark.parametrize(
    ("code", "status_code", "detail"),
    (
        ("DEADLINE_MATTER_NOT_AVAILABLE", 404, "LEGAL_MATTER_DEADLINE_NOT_AVAILABLE"),
        ("DEADLINE_CONFLICT", 409, "LEGAL_MATTER_DEADLINE_CONFLICT"),
        ("DEADLINE_PERSISTENCE_FAILURE", 503, "LEGAL_MATTER_DEADLINE_UNAVAILABLE"),
        ("DEADLINE_CORRUPT", 503, "LEGAL_MATTER_DEADLINE_UNAVAILABLE"),
    ),
)
def test_post_service_errors_are_bounded(
    monkeypatch: pytest.MonkeyPatch,
    code: str,
    status_code: int,
    detail: str,
) -> None:
    client, session = _client(monkeypatch)

    def record(**_kwargs: Any) -> LegalMatterDeadline:
        raise LegalMatterDeadlineServiceError(code)

    monkeypatch.setattr(deadline_api, "record_legal_matter_deadline", record)
    response = client.post(
        f"/api/legal-operations/matters/{MATTER}/deadlines",
        json=_payload(),
    )
    assert response.status_code == status_code
    assert response.json() == {"detail": detail}
    assert "abort" in session.events
    assert "commit" not in session.events


def test_list_delegates_exact_tenant_matter_and_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, session = _client(monkeypatch)
    calls: list[tuple[str, str, object]] = []

    def list_values(**kwargs: Any) -> tuple[LegalMatterDeadline, ...]:
        calls.append((kwargs["tenant_id"], kwargs["case_matter_id"], kwargs["session"]))
        return (_deadline(),)

    monkeypatch.setattr(deadline_api, "list_legal_matter_deadlines", list_values)
    response = client.get(f"/api/legal-operations/matters/{MATTER}/deadlines")
    assert response.status_code == 200
    assert calls == [(TENANT, MATTER, session)]
    assert response.json()["data"][0]["deadline_id"] == DEADLINE


def test_detail_delegates_exact_tenant_deadline_and_rechecks_matter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, session = _client(monkeypatch)
    calls: list[tuple[str, str, object]] = []

    def get_value(**kwargs: Any) -> LegalMatterDeadline:
        calls.append((kwargs["tenant_id"], kwargs["deadline_id"], kwargs["session"]))
        return _deadline()

    monkeypatch.setattr(deadline_api, "get_legal_matter_deadline", get_value)
    response = client.get(
        f"/api/legal-operations/matters/{MATTER}/deadlines/{DEADLINE}"
    )
    assert response.status_code == 200
    assert calls == [(TENANT, DEADLINE, session)]

    monkeypatch.setattr(
        deadline_api,
        "get_legal_matter_deadline",
        lambda **_kwargs: _deadline(matter="matter-other"),
    )
    bounded = client.get(
        f"/api/legal-operations/matters/{MATTER}/deadlines/{DEADLINE}"
    )
    assert bounded.status_code == 404
    assert bounded.json() == {"detail": "LEGAL_MATTER_DEADLINE_NOT_AVAILABLE"}


def test_wrong_method_rejects_and_projection_excludes_sensitive_internal_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, _ = _client(monkeypatch)
    monkeypatch.setattr(
        deadline_api,
        "list_legal_matter_deadlines",
        lambda **_kwargs: (_deadline(),),
    )
    response = client.get(f"/api/legal-operations/matters/{MATTER}/deadlines")
    assert response.status_code == 200
    item = response.json()["data"][0]
    assert "source_reference" not in item
    assert "source_evidence_fingerprint" not in item
    assert "fingerprint" not in item
    assert "_id" not in item
    assert client.put(f"/api/legal-operations/matters/{MATTER}/deadlines").status_code == 405


def test_router_source_has_no_direct_collection_write_or_financial_ai_surface() -> None:
    source = deadline_api.__file__
    assert source is not None
    text = open(source, encoding="utf-8").read()
    for forbidden in (
        "insert_one(",
        "update_one(",
        "replace_one(",
        "delete_one(",
        "payment_state",
        "settlement_state",
        "ai_generated",
        "ai_inferred_due_at",
    ):
        assert forbidden not in text.lower()


# ARTIFACT: test_legal_matter_deadline_http_router.py
# VERSION: v1.0.0-LEGAL-OPS-COMPLETION-D3B1-DEADLINE-HTTP-ROUTER-CERT
# AUTHORITY BOUNDARY: isolated HTTP transport certificate only; D1/D2/D3A and durable IAM remain canonical
# TENANT POSTURE: synthetic exact tenant context only; no cross-tenant fallback
# FAIL-CLOSED POSTURE: extra authority, wrong matter, conflict, absence, outage, and unexpected errors reject
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
