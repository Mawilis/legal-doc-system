from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest

from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_production_composition import (
    LegalEvidenceProviderReadOnlyReconciliationCompositionError,
    LegalEvidenceProviderReadOnlyReconciliationProductionComposition,
    build_legal_evidence_provider_readonly_reconciliation_production_composition,
)


class _Registry:
    def __init__(self, error: Exception | None = None, *, ready: bool = True) -> None:
        self.error = error
        self.ready = ready
        self.calls = 0

    def ensure_indexes(self) -> None:
        self.calls += 1
        if self.error:
            raise self.error

    def verify_indexes(self) -> bool:
        self.calls += 1
        if self.error:
            raise self.error
        return self.ready


class _Gate:
    def __init__(self) -> None:
        self.calls = []
        self.scope = object()

    def authorize(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            scope=self.scope,
            provider_name="aws_s3",
        )


class _Coordinator:
    def __init__(self) -> None:
        self.calls = []

    def reconcile(self, **kwargs):
        self.calls.append(kwargs)
        return "reconciled"


def _composition(registry=None, gate=None, coordinator=None):
    registry = registry or _Registry()
    gate = gate or _Gate()
    coordinator = coordinator or _Coordinator()
    return (
        LegalEvidenceProviderReadOnlyReconciliationProductionComposition(
            target=object(),
            business_client=SimpleNamespace(start_session=lambda: None),
            registry=registry,
            gate=gate,
            dependencies=SimpleNamespace(coordinator=coordinator),
        ),
        registry,
        gate,
        coordinator,
    )


def test_composition_fails_closed_when_deployment_has_not_provisioned_audit_indexes():
    registry = _Registry(ready=False)
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationCompositionError,
        match="PLATFORM_DECISION_AUDIT_INDEXES_NOT_PROVISIONED",
    ):
        _composition(registry=registry)
    assert registry.calls == 1


def test_composition_fails_closed_when_read_only_index_verification_fails():
    registry = _Registry(RuntimeError("index verification unavailable"))
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationCompositionError,
        match="PLATFORM_DECISION_AUDIT_INDEX_VERIFICATION_FAILED",
    ):
        _composition(registry=registry)
    assert registry.calls == 1


def test_authorized_composition_passes_only_gate_derived_scope_to_coordinator():
    composition, registry, gate, coordinator = _composition()
    at = datetime.now(timezone.utc)
    session = object()
    fields = {"service_id": "signed-service"}

    result = composition.authorize_and_reconcile(
        signed_workload_fields=fields,
        body=b"signed body",
        idempotency_key="reconcile-2",
        at=at,
        session=session,
    )

    assert result == "reconciled"
    assert registry.calls == 1
    assert callable(composition.business_client.start_session)
    assert gate.calls == [
        {
            "request": fields,
            "body": b"signed body",
            "idempotency_key": "reconcile-2",
            "at": at,
            "session": session,
        }
    ]
    assert coordinator.calls == [
        {
            "scope": gate.scope,
            "provider_name": "aws_s3",
            "observed_at": at,
            "session": session,
        }
    ]
    assert coordinator.calls[0]["scope"] is gate.scope


def test_production_builder_rejects_shared_business_and_audit_mongo_client():
    shared_client = object()
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationCompositionError,
        match="DISTINCT_SERVER_OWNED_AUDIT_CLIENT_REQUIRED",
    ):
        build_legal_evidence_provider_readonly_reconciliation_production_composition(
            mongo_database=SimpleNamespace(client=shared_client),
            audit_database=SimpleNamespace(client=shared_client),
            audit_client=shared_client,
            use_authority=object(),
            permission_possession_resolver=object(),
            workload_keys={},
            expected_audience="internal-reconciliation",
            env={},
        )
