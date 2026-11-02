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


class _OperationIdempotencyRegistry:
    def __init__(self) -> None:
        self.calls = []
        self.cached = None

    def lookup(self, **kwargs):
        self.calls.append(("lookup", kwargs))
        if self.cached is None:
            return None
        if self.cached[0] != kwargs["request_fingerprint"]:
            raise RuntimeError("idempotency conflict")
        return dict(self.cached[1])

    def record(self, **kwargs):
        self.calls.append(("record", kwargs))
        self.cached = (kwargs["request_fingerprint"], dict(kwargs["response"]))


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


def test_idempotent_invocation_replays_exact_result_after_reauthorization():
    registry = _Registry()
    gate = _Gate()
    gate.authorize = lambda **kwargs: SimpleNamespace(
        scope=SimpleNamespace(
            tenant_id="tenant-1",
            tenant_scope_fingerprint="scope-fingerprint-1",
        ),
        provider_name="aws_s3",
    )
    coordinator = _Coordinator()
    coordinator.reconcile = lambda **kwargs: SimpleNamespace(
        tenant_id="tenant-1",
        tenant_scope_fingerprint="scope-fingerprint-1",
        provider_name="aws_s3",
        observed_at=kwargs["observed_at"],
        coverage_verification_fingerprint="coverage-fingerprint-1",
        incomplete_observation_count=0,
        completed_observation_count=2,
        classifications=(object(),),
        write_intent_correlations=(),
        coverage_complete=True,
        orphan_proven=False,
        provider_delete_authorized=False,
        cleanup_authorized=False,
    )
    operation_registry = _OperationIdempotencyRegistry()
    composition = LegalEvidenceProviderReadOnlyReconciliationProductionComposition(
        target=object(),
        business_client=SimpleNamespace(start_session=lambda: None),
        registry=registry,
        gate=gate,
        dependencies=SimpleNamespace(coordinator=coordinator),
        idempotency_registry=operation_registry,
    )
    base_fields = {
        "service_id": "trusted-service",
        "key_id": "key-1",
        "audience": "legal-evidence-reconciliation",
        "method": "POST",
        "path": "/api/legal-operations/evidence-provider/reconciliation",
        "body_sha3_512": "body-fingerprint",
        "nonce": "nonce-1",
    }
    first = composition.authorize_and_reconcile_idempotently(
        signed_workload_fields=base_fields,
        body=b'{"idempotency_key":"operation-1"}',
        idempotency_key="operation-1",
        at=datetime(2026, 10, 25, tzinfo=timezone.utc),
        session=object(),
    )
    second_fields = {**base_fields, "nonce": "nonce-2"}
    second = composition.authorize_and_reconcile_idempotently(
        signed_workload_fields=second_fields,
        body=b'{"idempotency_key":"operation-1"}',
        idempotency_key="operation-1",
        at=datetime(2026, 10, 25, 1, tzinfo=timezone.utc),
        session=object(),
    )
    assert first == second
    assert first["classification_count"] == 1
    assert first["coverage_verification_fingerprint"] == "coverage-fingerprint-1"
    assert len(operation_registry.calls) == 3
    assert [call[0] for call in operation_registry.calls] == ["lookup", "record", "lookup"]


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
