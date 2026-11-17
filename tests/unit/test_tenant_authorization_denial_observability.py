"""Direct certificate for canonical tenant-authorization denial observation.

TITLE: WILSY OS Tenant Authorization Denial Observability Certificate
VERSION: v1.2.0-SCOPED-REQUEST-TIMING-CERT
AUTHORITY: Test-only verification of the existing shared HTTP IAM dependency.
EPITOME: Proves bounded post-decision denial and outage observations without
         changing authentication, authorization, tenant, or persistence truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_authorization_denial_observability.py
COLLABORATION / OWNERSHIP: Wilsy OS Core Governance and Python EOS IAM.
CERTIFICATION / UPDATE DATE: 2026-11-15
CHANGELOG: 2026-11-15 v1.2.0-SCOPED-REQUEST-TIMING-CERT verifies opt-in,
           trace-correlated timing excludes tenant, principal, permission, and
           credential material while leaving authorization outcomes unchanged.
2026-11-14 v1.1.0-PLAIN-LOG-CORRELATION-CERT verifies closed message-only logs preserve safe structured references.
Prior v1.0.0 establishes RED-first denial, outage, privacy,
           correlation, concurrency, sink-failure, and authority-boundary proof.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2 controls.
SECURITY / PRIVACY POSTURE: Synthetic identities only; secrets and raw identity
                            values are forbidden from observation payloads.
TENANT BOUNDARY: X-Tenant-ID remains request scope, never membership authority.
AUTHORITY BOUNDARY: Tests observe existing decisions and grant no access.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

import inspect
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

import tools.eos.api.tenant_authorization_http as boundary
from tools.eos.api.errors import register_error_handlers
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)

_TENANT = "tenant-sensitive-p6"
_PRINCIPAL = "principal-sensitive-p6"
_PERMISSION = "audit:read"
_OPERATION = "audit_read"


def _identity() -> SovereignIdentity:
    return SovereignIdentity(
        identity_id=_PRINCIPAL,
        tenant_id="non-authoritative-token-tenant",
        username="private-user",
        email="private@example.test",
        roles=["projected-role"],
        permissions=["projected-permission"],
        auth_method="test",
        session_reference=None,
        status=PrincipalStatus.ACTIVE,
    )


def _app() -> FastAPI:
    app = FastAPI()
    register_error_handlers(app, debug=False)
    app.dependency_overrides[boundary.get_current_identity] = _identity
    app.dependency_overrides[
        boundary.get_principal_authority_repository
    ] = object
    app.dependency_overrides[
        boundary.get_tenant_membership_repository
    ] = object
    app.dependency_overrides[boundary.get_role_assignment_repository] = object

    @app.get("/cert")
    async def cert(
        _context: boundary.TenantAuthorizationContext = Depends(
            boundary.RequireTenantAuthorization(_PERMISSION, _OPERATION)
        ),
    ) -> dict[str, bool]:
        return {"authorized": True}

    return app


def _set_decision(
    monkeypatch: Any,
    decision: TenantAuthorizationDecision,
) -> None:
    monkeypatch.setattr(
        boundary,
        "authorize_tenant_operation",
        lambda **_kwargs: decision,
    )


def _events(caplog: Any) -> list[dict[str, object]]:
    return [
        getattr(record, "wilsy_authorization_observation")
        for record in caplog.records
        if hasattr(record, "wilsy_authorization_observation")
    ]


def test_denial_emits_one_bounded_private_terminal_observation(
    caplog: Any,
    monkeypatch: Any,
) -> None:
    caplog.set_level(logging.INFO)
    _set_decision(
        monkeypatch,
        TenantAuthorizationDecision(
            False,
            TenantAuthorizationReason.PERMISSION_NOT_GRANTED,
        ),
    )
    app = _app()
    injected = "caller-correlation-must-never-win"
    with TestClient(app) as client:
        response = client.get(
            "/cert",
            headers={
                "X-Tenant-ID": _TENANT,
                "X-Correlation-ID": injected,
                "Authorization": "Bearer secret-must-not-appear",
            },
        )

    assert response.status_code == 403
    events = _events(caplog)
    assert len(events) == 1
    event = events[0]
    assert event["outcome"] == "AUTHORIZATION_DENIED"
    assert event["decision_class"] == "PERMISSION"
    assert event["http_status"] == 403
    assert set(event) == {
        "schema",
        "version",
        "event",
        "outcome",
        "decision_class",
        "tenant_ref",
        "principal_ref",
        "correlation_ref",
        "http_status",
    }
    serialized = repr(event)
    for forbidden in (
        _TENANT,
        _PRINCIPAL,
        injected,
        "secret-must-not-appear",
        _PERMISSION,
        _OPERATION,
        "private@example.test",
        "projected-role",
    ):
        assert forbidden not in serialized


def test_dependency_outage_is_not_misreported_as_permission_denial(
    caplog: Any,
    monkeypatch: Any,
) -> None:
    caplog.set_level(logging.INFO)
    _set_decision(
        monkeypatch,
        TenantAuthorizationDecision(
            False,
            TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE,
        ),
    )
    app = _app()
    with TestClient(app) as client:
        response = client.get("/cert", headers={"X-Tenant-ID": _TENANT})

    assert response.status_code == 503
    events = _events(caplog)
    assert len(events) == 1
    assert events[0]["outcome"] == "DEPENDENCY_UNAVAILABLE"
    assert events[0]["decision_class"] == "MEMBERSHIP"


def test_opt_in_timing_observes_existing_authorization_without_private_data(
    caplog: Any,
    monkeypatch: Any,
) -> None:
    caplog.set_level(logging.INFO)
    monkeypatch.setenv("WILSY_MY_WORK_TIMING", "1")
    _set_decision(
        monkeypatch,
        TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
            "tenant_auditor",
            "AUDITOR",
        ),
    )
    with TestClient(_app()) as client:
        response = client.get(
            "/cert",
            headers={
                "X-Tenant-ID": _TENANT,
                "X-Trace-ID": "TRC-MWHCMCDJ-HR4HXJ",
                "Authorization": "Bearer secret-must-not-appear",
            },
        )

    assert response.status_code == 200
    messages = [
        record.getMessage()
        for record in caplog.records
        if record.getMessage().startswith("WILSY_REQUEST_TIMING")
    ]
    assert any("trace_id=TRC-MWHCMCDJ-HR4HXJ" in message for message in messages)
    assert any("stage=TENANT_OTHER_THREADPOOL_QUEUE" in message for message in messages)
    assert any("stage=TENANT_OTHER_CURRENTNESS" in message for message in messages)
    serialized = "\n".join(messages)
    for private_value in (_TENANT, _PRINCIPAL, _PERMISSION, _OPERATION, "secret-must-not-appear"):
        assert private_value not in serialized


def test_authorized_verdict_and_denied_verdict_survive_logger_failure(
    monkeypatch: Any,
) -> None:
    def fail(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("telemetry secret")

    monkeypatch.setattr(boundary.logger, "log", fail)
    current = {
        "decision":
        TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
            "tenant_auditor",
            "AUDITOR",
        )
    }
    monkeypatch.setattr(
        boundary,
        "authorize_tenant_operation",
        lambda **_kwargs: current["decision"],
    )
    allowed = _app()
    with TestClient(allowed) as client:
        assert client.get("/cert", headers={"X-Tenant-ID": _TENANT}).status_code == 200

    current["decision"] = TenantAuthorizationDecision(
        False,
        TenantAuthorizationReason.MEMBERSHIP_INACTIVE,
    )
    denied = _app()
    with TestClient(denied) as client:
        assert client.get("/cert", headers={"X-Tenant-ID": _TENANT}).status_code == 403


def test_concurrent_denials_have_unique_server_correlation(
    caplog: Any,
    monkeypatch: Any,
) -> None:
    caplog.set_level(logging.INFO)
    _set_decision(
        monkeypatch,
        TenantAuthorizationDecision(
            False,
            TenantAuthorizationReason.ROLE_ASSIGNMENT_INACTIVE,
        ),
    )
    app = _app()

    def request_once(index: int) -> int:
        with TestClient(app) as client:
            return client.get(
                "/cert",
                headers={
                    "X-Tenant-ID": _TENANT,
                    "X-Correlation-ID": f"injected-{index}",
                },
            ).status_code

    with ThreadPoolExecutor(max_workers=4) as executor:
        statuses = list(executor.map(request_once, range(4)))

    assert statuses == [403, 403, 403, 403]
    events = _events(caplog)
    assert len(events) == 4
    correlations = {event["correlation_ref"] for event in events}
    assert len(correlations) == 4
    assert not any("injected-" in repr(event) for event in events)


def test_pre_authentication_failures_remain_401_and_are_not_misclassified(
    caplog: Any,
) -> None:
    caplog.set_level(logging.INFO)
    app = FastAPI()
    register_error_handlers(app, debug=False)

    @app.get("/cert")
    async def cert(
        _context: boundary.TenantAuthorizationContext = Depends(
            boundary.RequireTenantAuthorization(_PERMISSION, _OPERATION)
        ),
    ) -> dict[str, bool]:
        return {"authorized": True}

    with TestClient(app) as client:
        missing = client.get("/cert", headers={"X-Tenant-ID": _TENANT})
        invalid = client.get(
            "/cert",
            headers={
                "X-Tenant-ID": _TENANT,
                "Authorization": "Bearer invalid-token-secret",
            },
        )

    assert missing.status_code == 401
    assert invalid.status_code == 401
    assert _events(caplog) == []


def test_observation_adds_no_authority_or_persistence() -> None:
    source = inspect.getsource(boundary)
    dependency = boundary.RequireTenantAuthorization(_PERMISSION, _OPERATION)
    assert dependency.permission_id == _PERMISSION
    assert dependency.operation == _OPERATION
    for forbidden in (
        "insert_one(",
        "update_one(",
        "delete_one(",
        "replace_one(",
        "create_index(",
        "MongoClient(",
    ):
        assert forbidden not in source




def test_observation_pseudonym_failure_is_isolated(monkeypatch):
    """Synthetic pseudonym failure must not replace an IAM verdict."""
    from tools.eos.api import tenant_authorization_http as boundary

    def fail_pseudonym(value):
        raise RuntimeError("SYNTHETIC_PSEUDONYM_FAILURE")

    monkeypatch.setattr(boundary, "_observation_ref", fail_pseudonym)

    for outcome, http_status in (
        ("AUTHORIZATION_DENIED", 403),
        ("DEPENDENCY_UNAVAILABLE", 503),
    ):
        boundary._observe_terminal(
            outcome=outcome,
            reason=None,
            tenant_id="synthetic-tenant",
            principal_id="synthetic-principal",
            correlation_id="server-generated-test",
            http_status=http_status,
        )


def test_default_message_formatter_preserves_only_existing_closed_observation(caplog, monkeypatch):
    """Terminal formatters render the same non-secret references as structured sinks."""
    caplog.set_level(logging.INFO)
    _set_decision(monkeypatch, TenantAuthorizationDecision(False, TenantAuthorizationReason.PERMISSION_NOT_GRANTED))
    with TestClient(_app()) as client:
        assert client.get("/cert", headers={"X-Tenant-ID": _TENANT,
            "Authorization": "Bearer synthetic-secret"}).status_code == 403
    records = [record for record in caplog.records if hasattr(record, "wilsy_authorization_observation")]
    assert len(records) == 1
    rendered = logging.Formatter("%(message)s").format(records[0])
    prefix = "TENANT_AUTHORIZATION_HTTP_TERMINAL "
    assert rendered.startswith(prefix)
    assert json.loads(rendered[len(prefix):]) == records[0].wilsy_authorization_observation
    for forbidden in (_TENANT, _PRINCIPAL, "synthetic-secret", "private@example.test", _PERMISSION, _OPERATION):
        assert forbidden not in rendered

# ARTIFACT: test_tenant_authorization_denial_observability.py
# VERSION: v1.2.0-SCOPED-REQUEST-TIMING-CERT
# AUTHORITY BOUNDARY: direct observation verification only; existing IAM decides
# TENANT POSTURE: raw tenant and principal identities are forbidden from events
# FAIL-CLOSED POSTURE: telemetry failure never alters authorization verdicts
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
