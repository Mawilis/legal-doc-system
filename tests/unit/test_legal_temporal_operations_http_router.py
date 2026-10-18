"""
P4-P2 authenticated Legal Temporal Operations HTTP RED certificate.

Read-only temporal projection. Productive Work is the visibility ceiling.
No new IAM, persistence, deadline calculation, or legal execution authority.
"""
from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient

import tools.eos.api.legal_operations_router as legal_router
from tools.eos.legal_operations.service.legal_temporal_operations_read_service import (
    LegalTemporalOperationsReadServiceError,
)

PATH = "/api/legal-operations/temporal-operations"
NOW = datetime(2026, 10, 18, 15, 30, tzinfo=UTC)


def _context() -> Any:
    return SimpleNamespace(
        tenant_id="tenant-authorized",
        identity=SimpleNamespace(identity_id="principal-authorized"),
    )


def _app() -> FastAPI:
    app = FastAPI()
    app.dependency_overrides[
        legal_router._PRODUCTIVE_WORK_READ
    ] = _context
    app.include_router(legal_router.router, prefix="/api")
    return app


def test_temporal_route_exists_once_and_reuses_exact_iam() -> None:
    matches = [
        route for route in legal_router.router.routes
        if getattr(route, "path", None)
        == "/legal-operations/temporal-operations"
    ]
    assert len(matches) == 1
    assert getattr(matches[0], "methods", None) == {"GET"}

    dependency = legal_router._PRODUCTIVE_WORK_READ
    assert dependency.permission_id == (
        "legal_operations:productive_work:read"
    )
    assert dependency.operation == "legal_productive_work_read"

    dependant = getattr(matches[0], "dependant")
    assert any(
        item.call is dependency
        for item in dependant.dependencies
    ), "TEMPORAL_HTTP_MUST_REUSE_EXACT_IAM_DEPENDENCY"


def test_http_scope_session_and_provenance(
    monkeypatch: Any,
) -> None:
    captured: dict[str, Any] = {}
    session = SimpleNamespace(in_transaction=True)
    database = object()

    class Productive:
        def project(
            self, *, tenant_id: str, principal_id: str,
            as_of: datetime, session: Any,
        ) -> Any:
            captured["tenant"] = tenant_id
            captured["principal"] = principal_id
            captured["as_of"] = as_of
            captured["productive_session"] = session
            return SimpleNamespace(
                tenant_id=tenant_id,
                principal_id=principal_id,
                as_of=as_of,
            )

    class Temporal:
        def project(
            self, *, productive_work: Any, session: Any,
        ) -> Any:
            captured["temporal_session"] = session
            captured["productive_work"] = productive_work
            return SimpleNamespace(
                schema="WILSY-LEGAL-TEMPORAL-OPERATIONS/V1",
                version="v1-test",
                tenant_id=productive_work.tenant_id,
                principal_id=productive_work.principal_id,
                as_of=productive_work.as_of,
                visible_matter_ids=("matter-visible",),
                rows=(
                    SimpleNamespace(
                        case_matter_id="matter-visible",
                        deadline_id="deadline-1",
                        deadline_kind="FILING",
                        title="Evidenced filing",
                        due_at=NOW,
                        source_type="COURT_ORDER",
                        source_reference="evidence:deadline-1",
                        source_evidence_fingerprint="2" * 128,
                        jurisdiction_reference="jurisdiction:ZA",
                        status="OPEN",
                    ),
                ),
            )

    def factory(db: Any) -> tuple[Any, Any]:
        assert db is database
        return Productive(), Temporal()

    monkeypatch.setattr(
        legal_router,
        "_temporal_operations_services",
        factory,
        raising=False,
    )
    monkeypatch.setattr(
        legal_router,
        "_productive_work_projection_transaction",
        lambda callback: callback(session, database),
    )

    with TestClient(_app()) as client:
        response = client.get(
            PATH,
            params={
                "tenant_id": "foreign-tenant",
                "principal_id": "foreign-principal",
                "case_matter_id": "matter-hidden",
            },
        )

    assert response.status_code == 200
    assert captured["tenant"] == "tenant-authorized"
    assert captured["principal"] == "principal-authorized"
    assert captured["productive_session"] is session
    assert captured["temporal_session"] is session
    assert captured["as_of"].tzinfo is not None
    assert captured["productive_work"].tenant_id == "tenant-authorized"

    body = response.json()
    assert body["tenant_id"] == "tenant-authorized"
    assert body["principal_id"] == "principal-authorized"
    assert body["visible_matter_ids"] == ["matter-visible"]
    assert len(body["rows"]) == 1
    row = body["rows"][0]
    assert row["case_matter_id"] == "matter-visible"
    assert row["deadline_id"] == "deadline-1"
    assert row["source_reference"] == "evidence:deadline-1"
    assert row["source_evidence_fingerprint"] == "2" * 128
    assert row["due_at"] == NOW.isoformat()
    assert not any(
        key in body
        for key in ("write_authority", "execution_authority", "billing")
    )


def test_temporal_dependency_failure_is_fail_closed(
    monkeypatch: Any,
) -> None:
    session = SimpleNamespace(in_transaction=True)

    class Productive:
        def project(self, **kwargs: Any) -> Any:
            return SimpleNamespace(
                tenant_id="tenant-authorized",
                principal_id="principal-authorized",
                as_of=NOW,
            )

    class Temporal:
        def project(self, **kwargs: Any) -> Any:
            raise LegalTemporalOperationsReadServiceError(
                "TEMPORAL_DEADLINE_READ_FAILED"
            )

    monkeypatch.setattr(
        legal_router,
        "_temporal_operations_services",
        lambda database: (Productive(), Temporal()),
        raising=False,
    )
    monkeypatch.setattr(
        legal_router,
        "_productive_work_projection_transaction",
        lambda callback: callback(session, object()),
    )

    with TestClient(_app()) as client:
        response = client.get(PATH)

    assert response.status_code == 503
    assert response.json() == {
        "detail": "LEGAL_OPERATIONS_TEMPORAL_EVIDENCE_UNAVAILABLE"
    }


@pytest.mark.parametrize("failure", [False, True])
def test_real_transaction_helper_commit_or_abort(
    monkeypatch: Any,
    failure: bool,
) -> None:
    """Exercise the actual router transaction owner and exact session identity."""
    events: list[str] = []
    database = object()

    class Session:
        in_transaction = False

        def __enter__(self) -> Any:
            events.append("session_enter")
            return self

        def __exit__(self, *args: Any) -> None:
            events.append("session_exit")

        def start_transaction(self, *, read_concern: Any) -> None:
            assert read_concern.level == "snapshot"
            assert not self.in_transaction
            self.in_transaction = True
            events.append("snapshot_start")

        def commit_transaction(self) -> None:
            assert self.in_transaction
            events.append("commit")
            self.in_transaction = False

        def abort_transaction(self) -> None:
            assert self.in_transaction
            events.append("abort")
            self.in_transaction = False

    session = Session()

    class Client:
        def start_session(self) -> Any:
            events.append("start_session")
            return session

    class Productive:
        def project(
            self,
            *,
            tenant_id: str,
            principal_id: str,
            as_of: datetime,
            session: Any,
        ) -> Any:
            assert session is observed_session
            assert session.in_transaction is True
            assert tenant_id == "tenant-authorized"
            assert principal_id == "principal-authorized"
            events.append("productive_read")
            return SimpleNamespace(
                tenant_id=tenant_id,
                principal_id=principal_id,
                as_of=as_of,
            )

    class Temporal:
        def project(
            self,
            *,
            productive_work: Any,
            session: Any,
        ) -> Any:
            assert session is observed_session
            assert session.in_transaction is True
            assert productive_work.tenant_id == "tenant-authorized"
            events.append("temporal_read")
            if failure:
                raise LegalTemporalOperationsReadServiceError(
                    "TEMPORAL_DEADLINE_READ_FAILED"
                )
            return SimpleNamespace(
                schema="WILSY-LEGAL-TEMPORAL-OPERATIONS/V1",
                version="v1-test",
                tenant_id=productive_work.tenant_id,
                principal_id=productive_work.principal_id,
                as_of=productive_work.as_of,
                visible_matter_ids=(),
                rows=(),
            )

    observed_session = session

    monkeypatch.setattr(
        legal_router,
        "_db_handles",
        lambda: (Client(), database),
    )
    monkeypatch.setattr(
        legal_router,
        "_temporal_operations_services",
        lambda db: (
            (Productive(), Temporal())
            if db is database
            else (_ for _ in ()).throw(AssertionError("WRONG_DB"))
        ),
    )

    with TestClient(_app()) as client:
        response = client.get(PATH)

    if failure:
        assert response.status_code == 503, response.text
        assert response.json() == {
            "detail": "LEGAL_OPERATIONS_TEMPORAL_EVIDENCE_UNAVAILABLE"
        }
        assert "commit" not in events
        assert events == [
            "start_session",
            "session_enter",
            "snapshot_start",
            "productive_read",
            "temporal_read",
            "abort",
            "session_exit",
        ]
    else:
        assert response.status_code == 200, response.text
        assert response.json()["visible_matter_ids"] == []
        assert response.json()["rows"] == []
        assert "abort" not in events
        assert events == [
            "start_session",
            "session_enter",
            "snapshot_start",
            "productive_read",
            "temporal_read",
            "commit",
            "session_exit",
        ]

    assert session.in_transaction is False


def test_temporal_route_mounted_once_on_production_server() -> None:
    """Use the actual EOS composition root, not a standalone router app."""
    from fastapi.routing import APIRoute, _iter_routes_with_context
    import tools.eos.api.server as server_api

    matches: list[tuple[str, tuple[str, ...]]] = []
    for route, context in _iter_routes_with_context(server_api.app.routes):
        if not isinstance(route, APIRoute):
            continue
        path = context.path if context is not None else route.path
        if path != PATH:
            continue
        methods = context.methods if context is not None else route.methods
        matches.append((path, tuple(sorted(methods or set()))))

    assert matches == [(PATH, ("GET",))]
