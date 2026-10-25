"""Focused adversarial tests for the read-only provider reconciliation coordinator."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceProviderDiscoveryScope,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_coordinator import (
    LegalEvidenceProviderReadOnlyReconciliationCoordinator,
    LegalEvidenceProviderReadOnlyReconciliationError,
    LegalEvidenceProviderReadOnlyReconciliationResult,
    LegalEvidenceProviderReadOnlyReconciliationTransactionRequiredError,
)


AT = datetime(2026, 10, 25, 6, 0, tzinfo=timezone.utc)
SCOPE = LegalEvidenceProviderDiscoveryScope(
    tenant_id="tenant-legal-1",
    tenant_scope_fingerprint="a" * 128,
)


def _coordinator(*, discovery: object | None = None):
    discovery = discovery or Mock()
    coverage = Mock()
    classification = Mock()
    classification._discovery = discovery
    coordinator = LegalEvidenceProviderReadOnlyReconciliationCoordinator(
        discovery=discovery,
        coverage_service=coverage,
        classification_service=classification,
    )
    return coordinator, discovery, coverage, classification


def test_requires_active_caller_owned_transaction_before_any_discovery() -> None:
    coordinator, discovery, coverage, classification = _coordinator()
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationTransactionRequiredError):
        coordinator.reconcile(
            scope=SCOPE, provider_name="s3-certified", observed_at=AT, session=None
        )
    discovery.list_incomplete_write_sessions.assert_not_called()
    coverage.verify_coverage.assert_not_called()
    classification.classify_tenant_observations.assert_not_called()


@pytest.mark.parametrize("session", [object(), SimpleNamespace(in_transaction=False)])
def test_rejects_inactive_or_unverifiable_transaction(session: object) -> None:
    coordinator, discovery, coverage, _ = _coordinator()
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationTransactionRequiredError):
        coordinator.reconcile(
            scope=SCOPE, provider_name="s3-certified", observed_at=AT, session=session
        )
    coverage.verify_coverage.assert_not_called()
    discovery.list_incomplete_write_sessions.assert_not_called()


def test_rejects_missing_dependencies() -> None:
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationError):
        LegalEvidenceProviderReadOnlyReconciliationCoordinator(
            discovery=None, coverage_service=Mock(), classification_service=Mock()
        )


def test_rejects_classification_service_bound_to_different_discovery_instance() -> None:
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationError, match="DISCOVERY_INSTANCE_MISMATCH"):
        LegalEvidenceProviderReadOnlyReconciliationCoordinator(
            discovery=Mock(),
            coverage_service=Mock(),
            classification_service=SimpleNamespace(_discovery=Mock()),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("coverage_complete", False),
        ("orphan_proven", True),
        ("provider_delete_authorized", True),
        ("cleanup_authorized", True),
    ],
)
def test_result_rejects_incomplete_coverage_or_later_authority(field: str, value: bool) -> None:
    kwargs = {
        "tenant_id": SCOPE.tenant_id,
        "tenant_scope_fingerprint": SCOPE.tenant_scope_fingerprint,
        "provider_name": "s3-certified",
        "observed_at": AT,
        "coverage_verification_fingerprint": "b" * 128,
        "incomplete_observation_count": 0,
        "completed_observation_count": 0,
        "classifications": (),
        "write_intent_correlations": (),
    }
    kwargs[field] = value
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationError):
        LegalEvidenceProviderReadOnlyReconciliationResult(**kwargs)


def test_public_surface_has_no_mutating_or_later_authority_operations() -> None:
    names = set(dir(LegalEvidenceProviderReadOnlyReconciliationCoordinator))
    forbidden = {
        "delete", "abort", "authorize_cleanup", "issue_orphan_proof",
        "reconcile_commit", "release_retention", "clear_legal_hold",
        "publish_availability", "execute_payment", "settle_payment",
    }
    assert names.isdisjoint(forbidden)


def test_bad_observation_time_rejected_before_coverage_or_discovery() -> None:
    coordinator, discovery, coverage, _ = _coordinator()
    session = SimpleNamespace(in_transaction=True)
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationError, match="OBSERVATION_TIME_INVALID"):
        coordinator.reconcile(
            scope=SCOPE,
            provider_name="s3-certified",
            observed_at=datetime(2026, 10, 25, 6, 0),
            session=session,
        )
    coverage.verify_coverage.assert_not_called()
    discovery.list_incomplete_write_sessions.assert_not_called()


def test_provider_name_must_be_explicit_and_nonblank() -> None:
    coordinator, discovery, coverage, _ = _coordinator()
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationError, match="PROVIDER_REQUIRED"):
        coordinator.reconcile(
            scope=SCOPE, provider_name="  ", observed_at=AT,
            session=SimpleNamespace(in_transaction=True),
        )
    coverage.verify_coverage.assert_not_called()
    discovery.list_incomplete_write_sessions.assert_not_called()

def test_rejects_missing_or_fabricated_coverage_proof_before_classification() -> None:
    coordinator, discovery, coverage, classification = _coordinator()
    coverage.verify_coverage.return_value = object()
    coverage.accepts_verification.return_value = False
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationError, match="COVERAGE_SCOPE_MISMATCH"):
        coordinator.reconcile(
            scope=SCOPE,
            provider_name="s3-certified",
            observed_at=AT,
            session=SimpleNamespace(in_transaction=True),
        )
    discovery.list_incomplete_write_sessions.assert_not_called()
    classification.classify_tenant_observations.assert_not_called()


def test_coverage_verifier_failure_propagates_without_classification() -> None:
    coordinator, discovery, coverage, classification = _coordinator()
    coverage.verify_coverage.side_effect = RuntimeError("provider pagination failed")
    with pytest.raises(RuntimeError, match="provider pagination failed"):
        coordinator.reconcile(
            scope=SCOPE,
            provider_name="s3-certified",
            observed_at=AT,
            session=SimpleNamespace(in_transaction=True),
        )
    discovery.list_incomplete_write_sessions.assert_not_called()
    classification.classify_tenant_observations.assert_not_called()


def test_no_provider_or_persistence_mutation_methods_are_exposed() -> None:
    coordinator, discovery, coverage, classification = _coordinator()
    forbidden = ("delete_object", "abort_write_session", "insert_one", "update_one", "delete_one")
    assert all(not hasattr(coordinator, name) for name in forbidden)
    assert all(not hasattr(coverage, name) for name in forbidden)
    assert all(not hasattr(classification, name) for name in forbidden)
    assert all(not hasattr(discovery, name) for name in forbidden)

