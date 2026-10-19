"""P5-A Temporal Operations operational observability certificate.

TITLE: Wilsy OS Legal Temporal Operations Observability Certificate
VERSION: v1.0.0-P5-A-TEMPORAL-OPERATIONS-OBSERVABILITY-CERT
AUTHORITY: Read-only transport observability verification only.
EPITOME: Prove bounded post-authorization diagnostics for the certified P4
         Temporal Operations endpoint without exposing Legal evidence or
         changing canonical transaction and HTTP outcomes.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_temporal_operations_observability.py
COLLABORATION / OWNERSHIP: P4 owns temporal truth; P5-A observes transport outcomes.
CERTIFICATION / UPDATE DATE: 2026-10-18
CHANGELOG: 2026-10-18 v1.0.0 establishes RED-first success, abort, correlation,
           sensitive-exception and telemetry-outage boundaries.
COMPLIANCE: POPIA section 19, GDPR Article 32 and SOC 2 CC7.2 technical controls.
SECURITY / PRIVACY POSTURE: Raw tenant, principal, evidence and secret values
                             must never enter observations.
TENANT BOUNDARY: Only authenticated context may supply pseudonymized scope.
AUTHORITY BOUNDARY: Observation cannot grant IAM or Legal workflow authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns execution.
"""
from __future__ import annotations

from datetime import UTC, datetime
import logging
from types import SimpleNamespace
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

import tools.eos.api.legal_operations_router as legal_router
from tools.eos.legal_operations.service.legal_temporal_operations_read_service import (
    LegalTemporalOperationsReadServiceError,
)


PATH = "/api/legal-operations/temporal-operations"
TENANT = "tenant-p5-sensitive"
PRINCIPAL = "principal-p5-sensitive"
MATTER = "matter-p5-sensitive"
SECRET = "Bearer secret-token-p5"
NOW = datetime(2026, 10, 18, 19, 0, tzinfo=UTC)


def _context() -> Any:
    return SimpleNamespace(
        tenant_id=TENANT,
        identity=SimpleNamespace(identity_id=PRINCIPAL),
    )


def _app() -> FastAPI:
    app = FastAPI()
    app.dependency_overrides[legal_router._PRODUCTIVE_WORK_READ] = _context
    app.include_router(legal_router.router, prefix="/api")
    return app


def _projection() -> Any:
    return SimpleNamespace(
        schema="WILSY-LEGAL-TEMPORAL-OPERATIONS-PROJECTION/V1",
        version="v1-test",
        tenant_id=TENANT,
        principal_id=PRINCIPAL,
        as_of=NOW,
        visible_matter_ids=(MATTER,),
        rows=(),
    )


def _services(*, fail: bool = False) -> tuple[Any, Any]:
    class Productive:
        def project(self, **kwargs: Any) -> Any:
            return SimpleNamespace(
                tenant_id=kwargs["tenant_id"],
                principal_id=kwargs["principal_id"],
                as_of=kwargs["as_of"],
            )

    class Temporal:
        def project(self, **_kwargs: Any) -> Any:
            if fail:
                raise LegalTemporalOperationsReadServiceError(
                    f"TEMPORAL_READ_FAILED {MATTER} {SECRET}"
                )
            return _projection()

    return Productive(), Temporal()


def _observations(caplog: Any) -> list[dict[str, Any]]:
    return [
        getattr(record, "wilsy_observation")
        for record in caplog.records
        if hasattr(record, "wilsy_observation")
    ]


def test_success_observed_only_after_commit_with_bounded_fields(
    monkeypatch: Any,
    caplog: Any,
) -> None:
    events: list[str] = []

    class Session:
        in_transaction = False

        def __enter__(self) -> Any:
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def start_transaction(self, **_kwargs: Any) -> None:
            self.in_transaction = True

        def commit_transaction(self) -> None:
            events.append("commit")
            self.in_transaction = False

        def abort_transaction(self) -> None:
            events.append("abort")
            self.in_transaction = False

    class Client:
        def start_session(self) -> Session:
            return Session()

    monkeypatch.setattr(legal_router, "_db_handles", lambda: (Client(), object()))
    monkeypatch.setattr(
        legal_router,
        "_temporal_operations_services",
        lambda _database: _services(),
    )
    monkeypatch.setattr(
        legal_router,
        "_new_temporal_correlation_id",
        lambda: "server-correlation-success",
        raising=False,
    )
    caplog.set_level(
        logging.INFO,
        logger="WilsyOS.API.LegalOperationsRouter",
    )

    with TestClient(_app()) as client:
        response = client.get(PATH, headers={"X-Correlation-ID": "p5-request-001"})

    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == "server-correlation-success"
    assert events == ["commit"]
    observation = _observations(caplog)[0]
    assert observation["event"] == "LEGAL_TEMPORAL_OPERATIONS_HTTP"
    assert observation["outcome"] == "SUCCESS"
    assert observation["transaction_outcome"] == "COMMITTED"
    assert observation["http_status"] == 200
    assert observation["visible_matter_count"] == 1
    assert observation["deadline_count"] == 0
    assert set(observation) == {
        "schema", "version", "event", "operation", "outcome",
        "transaction_outcome", "dependency_class", "tenant_ref",
        "principal_ref", "correlation_ref", "http_status",
        "visible_matter_count", "deadline_count", "latency_bucket",
    }
    assert observation["latency_bucket"] in {
        "LT_10_MS", "LT_50_MS", "LT_250_MS", "LT_1000_MS", "GTE_1000_MS"
    }
    rendered = str(observation)
    for forbidden in (TENANT, PRINCIPAL, MATTER, SECRET, "p5-request-001"):
        assert forbidden not in rendered


def test_canonical_failure_observed_after_abort_without_exception_content(
    monkeypatch: Any,
    caplog: Any,
) -> None:
    events: list[str] = []

    def transaction(callback: Any) -> Any:
        try:
            return callback(SimpleNamespace(in_transaction=True), object())
        except Exception:
            events.append("abort")
            raise

    monkeypatch.setattr(
        legal_router,
        "_productive_work_projection_transaction",
        transaction,
    )
    monkeypatch.setattr(
        legal_router,
        "_temporal_operations_services",
        lambda _database: _services(fail=True),
    )
    caplog.set_level(
        logging.WARNING,
        logger="WilsyOS.API.LegalOperationsRouter",
    )

    with TestClient(_app()) as client:
        response = client.get(PATH)

    assert response.status_code == 503
    assert events == ["abort"]
    observation = _observations(caplog)[0]
    assert observation["outcome"] == "ERROR"
    assert observation["transaction_outcome"] == "ABORTED"
    assert observation["error_code"] == "TEMPORAL_EVIDENCE_UNAVAILABLE"
    rendered = str(observation)
    for forbidden in (TENANT, PRINCIPAL, MATTER, SECRET):
        assert forbidden not in rendered


def test_injected_correlation_is_replaced_and_never_logged_raw(
    monkeypatch: Any,
    caplog: Any,
) -> None:
    injected = "../../Bearer-injected-secret"
    monkeypatch.setattr(
        legal_router,
        "_temporal_operations_services",
        lambda _database: _services(),
    )
    monkeypatch.setattr(
        legal_router,
        "_productive_work_projection_transaction",
        lambda callback: callback(SimpleNamespace(in_transaction=True), object()),
    )
    monkeypatch.setattr(
        legal_router,
        "_new_temporal_correlation_id",
        lambda: "server-correlation-001",
        raising=False,
    )
    caplog.set_level(logging.INFO, logger="WilsyOS.API.LegalOperationsRouter")

    with TestClient(_app()) as client:
        response = client.get(PATH, headers={"X-Correlation-ID": injected})

    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == "server-correlation-001"
    assert injected not in str(_observations(caplog))
    assert "injected-secret" not in str(_observations(caplog))


def test_observability_backend_failure_never_changes_canonical_result(
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(
        legal_router,
        "_temporal_operations_services",
        lambda _database: _services(),
    )
    monkeypatch.setattr(
        legal_router,
        "_productive_work_projection_transaction",
        lambda callback: callback(SimpleNamespace(in_transaction=True), object()),
    )

    def broken_log(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError(f"logger unavailable {SECRET}")

    monkeypatch.setattr(legal_router.logger, "log", broken_log, raising=False)

    with TestClient(_app()) as client:
        response = client.get(PATH)

    assert response.status_code == 200
    assert response.json()["tenant_id"] == TENANT


def test_temporal_observability_adds_no_new_authorization_or_persistence() -> None:
    dependency = legal_router._PRODUCTIVE_WORK_READ
    assert dependency.permission_id == "legal_operations:productive_work:read"
    assert dependency.operation == "legal_productive_work_read"
    source = open(legal_router.__file__, encoding="utf-8").read()
    observability = source.split(
        "def _observe_temporal_operations(", 1
    )[1].split("def _temporal_operations_services(", 1)[0]
    for forbidden in (
        "insert_one", "update_one", "delete_one", "create_index",
        "source_reference", "source_evidence_fingerprint", "title",
        "assignment_authority", "transition_authority", "payment",
        "settlement",
    ):
        assert forbidden not in observability.lower()


# ARTIFACT: test_legal_temporal_operations_observability.py
# VERSION: v1.0.0-P5-A-TEMPORAL-OPERATIONS-OBSERVABILITY-CERT
# AUTHORITY BOUNDARY: post-authorization transport observation only
# TENANT POSTURE: raw tenant, principal and Legal evidence excluded
# FAIL-CLOSED POSTURE: telemetry cannot alter canonical HTTP outcomes
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
