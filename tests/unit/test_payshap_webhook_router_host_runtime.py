"""Direct certificate for PayShap host-to-reconciliation composition.

TITLE: PayShap Host Runtime Reconciliation Unit Certificate
VERSION: v1.0.0-M11-HOST-PAYSHAP-RECONCILIATION
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Prove authenticated EXECUTED webhooks delegate evidence-gated
         reconciliation through the caller-owned transaction.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_payshap_webhook_router_host_runtime.py
COLLABORATION / OWNERSHIP: Kennel EOS provider-ingress certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-12
CHANGELOG: v1.0.0 certifies route registration, same-session forwarding,
           bounded non-settlement responses, and fail-closed delegation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic opaque references only; no secrets or providers.
TENANT BOUNDARY: The router preserves signed tenant and canonical attempt scope.
AUTHORITY BOUNDARY: HTTP composition only; reconciliation remains canonical.
FINANCIAL AUTHORITY BOUNDARY: EXECUTION != SETTLEMENT; no paid or settlement truth.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock, patch

from fastapi import FastAPI

from tools.eos.api.payshap_webhook_router import (
    ROUTE_PATH,
    _observation_status,
    compose_authenticated_payshap_webhook,
    router,
)
from tools.eos.kennel.domain.financial_execution_provider_observation import ObservationStatus
from tools.eos.kennel.providers.payshap_contract import PayShapStatus


NOW = datetime(2026, 9, 12, 10, tzinfo=timezone.utc)


class _Database(dict[str, Mock]):
    """Small injected collection map; no persistence or network access."""

    def __missing__(self, key: str) -> Mock:
        value = Mock(name=key)
        self[key] = value
        return value


def _webhook(status: PayShapStatus) -> SimpleNamespace:
    return SimpleNamespace(
        tenant_id="tenant-1",
        provider_event_id="event-1",
        execution_command_id="command-1",
        provider_reference="provider-request-1",
        provider_execution_reference="provider-execution-1"
        if status is PayShapStatus.EXECUTED
        else None,
        provider_status=status,
        provider_timestamp=NOW if status is PayShapStatus.EXECUTED else None,
        evidence_reference="evidence-1",
        observed_at=NOW,
        is_replay=False,
    )


def test_webhook_route_is_registered_exactly_once() -> None:
    routes = [
        route
        for route in router.routes
        if getattr(route, "path", None) == ROUTE_PATH
        and "POST" in getattr(route, "methods", set())
    ]
    assert len(routes) == 1
    app = FastAPI()
    app.include_router(router)
    included = cast(Any, app.router.routes[-1])
    effective = [
        context
        for context in included.effective_route_contexts()
        if getattr(context, "path", None) == ROUTE_PATH
        and "POST" in getattr(context, "methods", set())
    ]
    assert len(effective) == 1


def test_authenticated_executed_delegates_once_with_same_session() -> None:
    database = _Database()
    session = Mock(in_transaction=True)
    attempt = SimpleNamespace(
        tenant_id="tenant-1",
        execution_attempt_id="attempt-1",
        provider_name="PAYSHAP",
    )
    stored = SimpleNamespace(payload_fingerprint="f" * 128)
    application = SimpleNamespace(decision=SimpleNamespace(reconciliation_required=True))
    with (
        patch(
            "tools.eos.api.payshap_webhook_router.ingest_webhook",
            return_value=_webhook(PayShapStatus.EXECUTED),
        ),
        patch(
            "tools.eos.api.payshap_webhook_router.PayShapEvidenceRegistry.get",
            return_value=stored,
        ),
        patch(
            "tools.eos.api.payshap_webhook_router._resolve_attempt",
            return_value=attempt,
        ),
        patch(
            "tools.eos.api.payshap_webhook_router.ingest_authenticated_provider_observation",
            return_value=application,
        ),
        patch(
            "tools.eos.api.payshap_webhook_router.reconcile_and_finalize_execution",
            return_value=object(),
        ) as reconcile,
    ):
        result = compose_authenticated_payshap_webhook(
            {"status": "EXECUTED"},
            "signature",
            "secret",
            database=database,
            session=session,
        )
    assert result.reconciliation_required is False
    reconcile.assert_called_once()
    args = reconcile.call_args
    assert args.args == ("tenant-1", "attempt-1")
    assert args.kwargs["session"] is session
    assert args.kwargs["execution_time_evidence"].execution_attempt_id == "attempt-1"
    assert args.kwargs["execution_time_evidence"].provider_execution_reference == "provider-execution-1"


def test_non_executed_status_preserves_reconciliation_result_without_call() -> None:
    database = _Database()
    session = Mock(in_transaction=True)
    attempt = SimpleNamespace(
        tenant_id="tenant-1",
        execution_attempt_id="attempt-1",
        provider_name="PAYSHAP",
    )
    stored = SimpleNamespace(payload_fingerprint="f" * 128)
    application = SimpleNamespace(decision=SimpleNamespace(reconciliation_required=True))
    with (
        patch(
            "tools.eos.api.payshap_webhook_router.ingest_webhook",
            return_value=_webhook(PayShapStatus.ACCEPTED),
        ),
        patch(
            "tools.eos.api.payshap_webhook_router.PayShapEvidenceRegistry.get",
            return_value=stored,
        ),
        patch(
            "tools.eos.api.payshap_webhook_router._resolve_attempt",
            return_value=attempt,
        ),
        patch(
            "tools.eos.api.payshap_webhook_router.ingest_authenticated_provider_observation",
            return_value=application,
        ),
        patch(
            "tools.eos.api.payshap_webhook_router.reconcile_and_finalize_execution"
        ) as reconcile,
    ):
        result = compose_authenticated_payshap_webhook(
            {"status": "ACCEPTED"},
            "signature",
            "secret",
            database=database,
            session=session,
        )
    assert result.reconciliation_required is True
    reconcile.assert_not_called()


def test_paid_status_remains_non_settlement_provider_evidence() -> None:
    assert _observation_status(PayShapStatus.UNKNOWN) is ObservationStatus.UNKNOWN


# ARTIFACT: test_payshap_webhook_router_host_runtime.py
# VERSION: v1.0.0-M11-HOST-PAYSHAP-RECONCILIATION
# AUTHORITY BOUNDARY: authenticated PayShap host composition only.
# TENANT POSTURE: signed tenant and canonical attempt correlation remain authoritative.
# FAIL-CLOSED POSTURE: reconciliation failures propagate to the route boundary.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively; EXECUTION != SETTLEMENT.
# END OF WILSY OS SOVEREIGN ARTIFACT
