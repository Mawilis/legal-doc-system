"""Focused adversarial tests for the read-only provider reconciliation coordinator.

TITLE: Legal Evidence Provider Read-Only Reconciliation Coordinator Tests
VERSION: v1.1.0-L10A2R-C4D7A-READONLY-RECONCILIATION-TESTS
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
PURPOSE: Certify coordinator rejection boundaries and one successful, real
         coverage-verifier path without introducing runtime integration.
AUTHORITY BOUNDARY: Tests only; no provider or persistence mutation authority.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_classification import (
    LegalEvidenceProviderCleanupClassification,
    LegalEvidenceProviderCleanupClassificationEvidence,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_write_intent_correlation import (
    LegalEvidenceProviderWriteIntentCorrelationEvidence,
    LegalEvidenceProviderWriteIntentCorrelationState,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectIntentMetadataState,
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceProviderDiscoveryScope,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_enumeration_port import (
    LegalEvidenceProviderCoverageEnumerationPort,
    LegalEvidenceProviderEnumerationKind,
    LegalEvidenceProviderEnumerationPage,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_verification_service import (
    LegalEvidenceProviderCoverageVerificationService,
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
PROVIDER = "s3-certified"


def _completed(
    *,
    tenant_id: str = SCOPE.tenant_id,
    provider_name: str = PROVIDER,
    observed_at: datetime = AT,
) -> LegalEvidenceCompletedObjectObservation:
    return LegalEvidenceCompletedObjectObservation(
        tenant_id=tenant_id,
        provider_name=provider_name,
        storage_reference="opaque/storage/evidence",
        object_version_reference="version-7",
        provider_integrity_reference='"etag-7"',
        content_length=7,
        last_modified_at=AT,
        observed_at=observed_at,
        write_intent_metadata_state=LegalEvidenceCompletedObjectIntentMetadataState.ABSENT,
        write_intent_fingerprint=None,
    )


def _page(
    *,
    kind: LegalEvidenceProviderEnumerationKind,
    observations: tuple[object, ...],
) -> LegalEvidenceProviderEnumerationPage:
    return LegalEvidenceProviderEnumerationPage(
        tenant_id=SCOPE.tenant_id,
        tenant_scope_fingerprint=SCOPE.tenant_scope_fingerprint,
        provider_name=PROVIDER,
        enumeration_kind=kind,
        observed_at=AT,
        observations=observations,
        next_page_reference=None,
    )


class _Provider:
    """Test provider seam implementing coverage enumeration and discovery."""

    def __init__(self, observation: LegalEvidenceCompletedObjectObservation) -> None:
        self.observation = observation
        # Coverage pages must themselves be valid for the requested scope/time;
        # discovery can deliberately drift independently in adversarial tests.
        self.coverage_observation = _completed()
        self.calls: list[tuple[str, str | None, datetime]] = []

    def list_incomplete_write_session_page(
        self, scope: LegalEvidenceProviderDiscoveryScope, *,
        observed_at: datetime, page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        self.calls.append(("coverage-incomplete", page_reference, observed_at))
        return _page(
            kind=LegalEvidenceProviderEnumerationKind.INCOMPLETE_WRITE_SESSIONS,
            observations=(),
        )

    def list_completed_object_version_page(
        self, scope: LegalEvidenceProviderDiscoveryScope, *,
        observed_at: datetime, page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        self.calls.append(("coverage-completed", page_reference, observed_at))
        return _page(
            kind=LegalEvidenceProviderEnumerationKind.COMPLETED_OBJECT_VERSIONS,
            observations=(self.coverage_observation,),
        )

    def list_incomplete_write_sessions(
        self, scope: LegalEvidenceProviderDiscoveryScope, *,
        observed_at: datetime,
    ) -> tuple[()]:
        self.calls.append(("discovery-incomplete", None, observed_at))
        return ()

    def list_completed_object_versions(
        self, scope: LegalEvidenceProviderDiscoveryScope, *,
        observed_at: datetime,
    ) -> tuple[LegalEvidenceCompletedObjectObservation, ...]:
        self.calls.append(("discovery-completed", None, observed_at))
        return (self.observation,)


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


def _successful_coordinator(
    *,
    observation: LegalEvidenceCompletedObjectObservation | None = None,
):
    observed = observation or _completed()
    provider = _Provider(observed)
    assert isinstance(provider, LegalEvidenceProviderCoverageEnumerationPort)
    coverage = LegalEvidenceProviderCoverageVerificationService(provider=provider)
    classification = Mock()
    classification._discovery = provider
    classification.classify_tenant_observations.return_value = (
        LegalEvidenceProviderCleanupClassificationEvidence(
            tenant_id=observed.tenant_id,
            provider_name=observed.provider_name,
            storage_reference=observed.storage_reference,
            observed_at=observed.observed_at,
            classification=LegalEvidenceProviderCleanupClassification.PROVIDER_OBJECT_UNRESOLVED,
            object_version_reference=observed.object_version_reference,
            provider_integrity_reference=observed.provider_integrity_reference,
            content_length=observed.content_length,
            last_modified_at=observed.last_modified_at,
        ),
    )
    classification.correlate_tenant_completed_write_intents.return_value = (
        LegalEvidenceProviderWriteIntentCorrelationEvidence(
            tenant_id=observed.tenant_id,
            provider_name=observed.provider_name,
            storage_reference=observed.storage_reference,
            object_version_reference=observed.object_version_reference,
            observed_at=observed.observed_at,
            metadata_state=LegalEvidenceCompletedObjectIntentMetadataState.ABSENT,
            correlation_state=LegalEvidenceProviderWriteIntentCorrelationState.METADATA_ABSENT,
        ),
    )
    coordinator = LegalEvidenceProviderReadOnlyReconciliationCoordinator(
        discovery=provider,
        coverage_service=coverage,
        classification_service=classification,
    )
    return coordinator, provider, coverage, classification


def test_requires_active_caller_owned_transaction_before_any_discovery() -> None:
    coordinator, discovery, coverage, classification = _coordinator()
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationTransactionRequiredError):
        coordinator.reconcile(
            scope=SCOPE, provider_name=PROVIDER, observed_at=AT, session=None
        )
    discovery.list_incomplete_write_sessions.assert_not_called()
    coverage.verify_coverage.assert_not_called()
    classification.classify_tenant_observations.assert_not_called()


@pytest.mark.parametrize("session", [object(), SimpleNamespace(in_transaction=False)])
def test_rejects_inactive_or_unverifiable_transaction(session: object) -> None:
    coordinator, discovery, coverage, _ = _coordinator()
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationTransactionRequiredError):
        coordinator.reconcile(
            scope=SCOPE, provider_name=PROVIDER, observed_at=AT, session=session
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
        "provider_name": PROVIDER,
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
            scope=SCOPE, provider_name=PROVIDER,
            observed_at=datetime(2026, 10, 25, 6, 0), session=session,
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
            scope=SCOPE, provider_name=PROVIDER, observed_at=AT,
            session=SimpleNamespace(in_transaction=True),
        )
    discovery.list_incomplete_write_sessions.assert_not_called()
    classification.classify_tenant_observations.assert_not_called()


def test_coverage_verifier_failure_propagates_without_classification() -> None:
    coordinator, discovery, coverage, classification = _coordinator()
    coverage.verify_coverage.side_effect = RuntimeError("provider pagination failed")
    with pytest.raises(RuntimeError, match="provider pagination failed"):
        coordinator.reconcile(
            scope=SCOPE, provider_name=PROVIDER, observed_at=AT,
            session=SimpleNamespace(in_transaction=True),
        )
    discovery.list_incomplete_write_sessions.assert_not_called()
    classification.classify_tenant_observations.assert_not_called()


def test_coordinator_exposes_no_provider_or_persistence_mutation_methods() -> None:
    coordinator, _discovery, _coverage, _classification = _coordinator()
    forbidden = ("delete_object", "abort_write_session", "insert_one", "update_one", "delete_one")
    assert all(not hasattr(coordinator, name) for name in forbidden)


def test_successful_completed_only_reconciliation_uses_real_coverage_proof() -> None:
    coordinator, provider, coverage, classification = _successful_coordinator()
    session = SimpleNamespace(in_transaction=True)

    result = coordinator.reconcile(
        scope=SCOPE, provider_name=PROVIDER, observed_at=AT, session=session
    )

    assert result.tenant_id == SCOPE.tenant_id
    assert result.tenant_scope_fingerprint == SCOPE.tenant_scope_fingerprint
    assert result.provider_name == PROVIDER
    assert result.observed_at == AT
    assert len(result.coverage_verification_fingerprint) == 128
    assert result.incomplete_observation_count == 0
    assert result.completed_observation_count == 1
    assert result.coverage_complete is True
    assert result.orphan_proven is False
    assert result.provider_delete_authorized is False
    assert result.cleanup_authorized is False
    assert result.classifications[0].classification is LegalEvidenceProviderCleanupClassification.PROVIDER_OBJECT_UNRESOLVED
    assert result.write_intent_correlations[0].correlation_state is LegalEvidenceProviderWriteIntentCorrelationState.METADATA_ABSENT
    classification.classify_tenant_observations.assert_called_once_with(
        scope=SCOPE, observed_at=AT, session=session
    )
    classification.correlate_tenant_completed_write_intents.assert_called_once_with(
        scope=SCOPE, observed_at=AT, session=session
    )
    assert [call[0] for call in provider.calls] == [
        "coverage-incomplete", "coverage-completed",
        "discovery-incomplete", "discovery-completed",
    ]


@pytest.mark.parametrize(
    ("observation", "error"),
    [
        (_completed(tenant_id="tenant-other"), "OBSERVATION_SCOPE_MISMATCH"),
        (_completed(provider_name="different-provider"), "OBSERVATION_SCOPE_MISMATCH"),
        (_completed(observed_at=datetime(2026, 10, 25, 6, 1, tzinfo=timezone.utc)), "OBSERVATION_TIME_MISMATCH"),
    ],
)
def test_discovery_tenant_provider_or_time_drift_fails_before_classification(
    observation: LegalEvidenceCompletedObjectObservation, error: str,
) -> None:
    coordinator, _provider, _coverage, classification = _successful_coordinator(
        observation=observation
    )
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationError, match=error):
        coordinator.reconcile(
            scope=SCOPE, provider_name=PROVIDER, observed_at=AT,
            session=SimpleNamespace(in_transaction=True),
        )
    classification.classify_tenant_observations.assert_not_called()
    classification.correlate_tenant_completed_write_intents.assert_not_called()


def test_classification_source_drift_fails_closed() -> None:
    coordinator, _provider, _coverage, classification = _successful_coordinator()
    classification.classify_tenant_observations.return_value = ()
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationError, match="CLASSIFICATION_SOURCE_DRIFT"):
        coordinator.reconcile(
            scope=SCOPE, provider_name=PROVIDER, observed_at=AT,
            session=SimpleNamespace(in_transaction=True),
        )
    classification.correlate_tenant_completed_write_intents.assert_not_called()


def test_correlation_source_drift_fails_closed() -> None:
    coordinator, _provider, _coverage, classification = _successful_coordinator()
    classification.correlate_tenant_completed_write_intents.return_value = ()
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationError, match="CORRELATION_SOURCE_DRIFT"):
        coordinator.reconcile(
            scope=SCOPE, provider_name=PROVIDER, observed_at=AT,
            session=SimpleNamespace(in_transaction=True),
        )


def test_incomplete_session_membership_remains_fail_closed() -> None:
    from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
        LegalEvidenceIncompleteWriteSessionObservation,
    )

    incomplete = LegalEvidenceIncompleteWriteSessionObservation(
        tenant_id=SCOPE.tenant_id,
        provider_name=PROVIDER,
        storage_reference="opaque/storage/incomplete",
        write_session_reference="session-1",
        initiated_at=AT,
        observed_at=AT,
    )
    provider = _Provider(_completed())
    provider.list_incomplete_write_sessions = Mock(return_value=(incomplete,))
    classification = Mock()
    classification._discovery = provider
    coverage = Mock()
    coverage.verify_coverage.return_value = object()
    coverage.accepts_verification.return_value = True
    verification = SimpleNamespace(
        tenant_id=SCOPE.tenant_id,
        tenant_scope_fingerprint=SCOPE.tenant_scope_fingerprint,
        provider_name=PROVIDER,
        observed_at=AT,
        incomplete_observation_count=1,
        completed_observation_count=1,
        fingerprint="b" * 128,
    )
    coverage.verify_coverage.return_value = verification
    coverage.contains_completed_observation.return_value = True
    coordinator = LegalEvidenceProviderReadOnlyReconciliationCoordinator(
        discovery=provider, coverage_service=coverage,
        classification_service=classification,
    )
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationError, match="INCOMPLETE_MEMBERSHIP_UNPROVEN"):
        coordinator.reconcile(
            scope=SCOPE, provider_name=PROVIDER, observed_at=AT,
            session=SimpleNamespace(in_transaction=True),
        )
    classification.classify_tenant_observations.assert_not_called()


# ARTIFACT: test_legal_evidence_provider_readonly_reconciliation_coordinator.py
# VERSION: v1.1.0-L10A2R-C4D7A-READONLY-RECONCILIATION-TESTS
# AUTHORITY BOUNDARY: unit certification only; no production mutation authority
# FAIL-CLOSED POSTURE: test evidence cannot elevate runtime or deletion authority
# END OF WILSY OS SOVEREIGN ARTIFACT
