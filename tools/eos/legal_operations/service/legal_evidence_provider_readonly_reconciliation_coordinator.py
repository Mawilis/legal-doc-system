"""WILSY OS read-only Legal Evidence provider reconciliation coordinator.

TITLE: Legal Evidence Provider Read-Only Reconciliation Coordinator
VERSION: v1.0.0-L10A2R-C4D7A-READONLY-RECONCILIATION-COORDINATOR
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Bind trusted exhaustive provider coverage to exact tenant-scoped
         observations, existing read-only classification and write-intent
         correlation without granting cleanup or mutation authority.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_coordinator.py
COLLABORATION / OWNERSHIP:
    Composes C4D1 discovery, C4D6C-B trusted coverage, C4D3B classification
    and C4D5D3 exact write-intent correlation. Does not replace their authority.
CERTIFICATION / UPDATE DATE: 2026-10-25
CHANGELOG:
    v1.0.0 introduces explicit read-only coordination, exact coverage binding,
    scope/time checks, deterministic snapshot comparison and caller-owned
    transaction propagation. Runtime scheduling is deliberately not wired.
COMPLIANCE:
    Tenant-isolation and evidence-provenance controls; no independent legal
    compliance claim.
SECURITY / PRIVACY POSTURE:
    Accepts only validated immutable contracts and trusted service-issued
    coverage proof. Divergent or incomplete evidence fails closed.
TENANT BOUNDARY:
    Requires one exact LegalEvidenceProviderDiscoveryScope. Every observed,
    classified and correlated item must remain in that tenant and provider.
AUTHORITY BOUNDARY:
    Read-only reconciliation summary only. No provider mutation, persistence
    writes, cleanup authorization, orphan proof, commit recovery, retention,
    legal hold, IAM or availability authority.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS remains the exclusive financial execution authority.
TRANSACTION BOUNDARY:
    Caller supplies and owns one already-active transaction for classification
    and exact write-intent correlation. This coordinator never starts, commits,
    aborts or retries a transaction.
FAIL-CLOSED POSTURE:
    Missing coverage, scope/time/provider divergence, observation-set drift,
    invalid result types, and transaction absence reject with stable errors.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Final

from tools.eos.legal_operations.domain.legal_evidence_provider_cleanup_classification import (
    LegalEvidenceProviderCleanupClassificationEvidence,
)
from tools.eos.legal_operations.domain.legal_evidence_provider_write_intent_correlation import (
    LegalEvidenceProviderWriteIntentCorrelationEvidence,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceIncompleteWriteSessionObservation,
    LegalEvidenceProviderCleanupDiscoveryPort,
    LegalEvidenceProviderDiscoveryScope,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_verification_service import (
    LegalEvidenceProviderCoverageVerification,
    LegalEvidenceProviderCoverageVerificationService,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_classification_service import (
    LegalEvidenceProviderCleanupClassificationService,
)


VERSION: Final[str] = (
    "v1.0.0-L10A2R-C4D7A-READONLY-RECONCILIATION-COORDINATOR"
)


class LegalEvidenceProviderReadOnlyReconciliationError(RuntimeError):
    """Fail-closed coordinator contract error.

    This error represents rejected reconciliation evidence only. It does not
    authorize provider mutation, cleanup, persistence changes or financial work.
    """


class LegalEvidenceProviderReadOnlyReconciliationTransactionRequiredError(
    LegalEvidenceProviderReadOnlyReconciliationError
):
    """Raised unless the caller supplies one already-active transaction."""


def _utc(value: datetime) -> datetime:
    """Validate and normalize the caller's explicit observation time."""
    if (
        not isinstance(value, datetime)
        or value.tzinfo is None
        or value.utcoffset() is None
    ):
        raise LegalEvidenceProviderReadOnlyReconciliationError(
            "L10A2R_C4D7A_OBSERVATION_TIME_INVALID"
        )
    return value.astimezone(timezone.utc)


def _require_active_transaction(session: Any) -> Any:
    """Require an active caller-owned transaction without taking its lifecycle."""
    if session is None:
        raise LegalEvidenceProviderReadOnlyReconciliationTransactionRequiredError(
            "L10A2R_C4D7A_TRANSACTION_REQUIRED"
        )
    marker = getattr(session, "in_transaction", False)
    try:
        active = marker() if callable(marker) else marker
    except (AttributeError, TypeError):
        active = False
    if active is not True:
        raise LegalEvidenceProviderReadOnlyReconciliationTransactionRequiredError(
            "L10A2R_C4D7A_TRANSACTION_REQUIRED"
        )
    return session


def _observation_key(
    observation: (
        LegalEvidenceIncompleteWriteSessionObservation
        | LegalEvidenceCompletedObjectObservation
    ),
) -> tuple[str, ...]:
    """Build a deterministic semantic key for one immutable provider observation."""
    if type(observation) is LegalEvidenceIncompleteWriteSessionObservation:
        return (
            "INCOMPLETE",
            observation.tenant_id,
            observation.provider_name,
            observation.storage_reference,
            observation.write_session_reference,
            observation.initiated_at.isoformat(),
            observation.observed_at.isoformat(),
        )
    if type(observation) is LegalEvidenceCompletedObjectObservation:
        return (
            "COMPLETED",
            observation.tenant_id,
            observation.provider_name,
            observation.storage_reference,
            observation.object_version_reference,
            observation.provider_integrity_reference,
            str(observation.content_length),
            observation.last_modified_at.isoformat(),
            observation.observed_at.isoformat(),
            observation.write_intent_metadata_state.value,
            observation.write_intent_fingerprint or "",
        )
    raise LegalEvidenceProviderReadOnlyReconciliationError(
        "L10A2R_C4D7A_OBSERVATION_TYPE_INVALID"
    )


def _classification_key(
    item: LegalEvidenceProviderCleanupClassificationEvidence,
) -> tuple[str, ...]:
    """Project classification evidence onto its source observation identity."""
    if type(item) is not LegalEvidenceProviderCleanupClassificationEvidence:
        raise LegalEvidenceProviderReadOnlyReconciliationError(
            "L10A2R_C4D7A_CLASSIFICATION_TYPE_INVALID"
        )
    return (
        "INCOMPLETE" if item.write_session_reference is not None else "COMPLETED",
        item.tenant_id,
        item.provider_name,
        item.storage_reference,
        item.object_version_reference or item.write_session_reference or "",
        item.provider_integrity_reference or "",
        str(item.content_length or ""),
        item.last_modified_at.isoformat() if item.last_modified_at else "",
        item.observed_at.isoformat(),
        item.initiated_at.isoformat() if item.initiated_at else "",
    )


def _correlation_key(
    item: LegalEvidenceProviderWriteIntentCorrelationEvidence,
) -> tuple[str, ...]:
    """Project correlation evidence onto its completed provider object identity."""
    if type(item) is not LegalEvidenceProviderWriteIntentCorrelationEvidence:
        raise LegalEvidenceProviderReadOnlyReconciliationError(
            "L10A2R_C4D7A_CORRELATION_TYPE_INVALID"
        )
    return (
        item.tenant_id,
        item.provider_name,
        item.storage_reference,
        item.object_version_reference,
        item.observed_at.isoformat(),
    )


@dataclass(frozen=True, slots=True)
class LegalEvidenceProviderReadOnlyReconciliationResult:
    """Immutable read-only reconciliation output for one provider and tenant.

    The result records coverage and source-evidence classifications only. It
    contains no deletion or cleanup command and does not assert that any
    observation is an orphan.
    """

    tenant_id: str
    tenant_scope_fingerprint: str
    provider_name: str
    observed_at: datetime
    coverage_verification_fingerprint: str
    incomplete_observation_count: int
    completed_observation_count: int
    classifications: tuple[LegalEvidenceProviderCleanupClassificationEvidence, ...]
    write_intent_correlations: tuple[LegalEvidenceProviderWriteIntentCorrelationEvidence, ...]
    coverage_complete: bool = True
    orphan_proven: bool = False
    provider_delete_authorized: bool = False
    cleanup_authorized: bool = False

    def __post_init__(self) -> None:
        """Reject any result that claims more than exhaustive read-only evidence."""
        if self.coverage_complete is not True:
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_COVERAGE_COMPLETENESS_REQUIRED"
            )
        if (
            self.orphan_proven is not False
            or self.provider_delete_authorized is not False
            or self.cleanup_authorized is not False
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_LATER_AUTHORITY_FORBIDDEN"
            )
        if type(self.classifications) is not tuple or type(self.write_intent_correlations) is not tuple:
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_RESULT_COLLECTION_INVALID"
            )


class LegalEvidenceProviderReadOnlyReconciliationCoordinator:
    """Coordinate exhaustive coverage and existing read-only Legal Evidence services.

    Construction binds existing discovery, trusted coverage-verification and
    classification service instances. The same discovery instance must be used
    by the classification service. Execution performs no writes and leaves
    transaction lifecycle to the caller.
    """

    __slots__ = ("_discovery", "_coverage", "_classification")

    def __init__(
        self,
        *,
        discovery: LegalEvidenceProviderCleanupDiscoveryPort,
        coverage_service: LegalEvidenceProviderCoverageVerificationService,
        classification_service: LegalEvidenceProviderCleanupClassificationService,
    ) -> None:
        if discovery is None or coverage_service is None or classification_service is None:
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_DEPENDENCY_REQUIRED"
            )
        if getattr(classification_service, "_discovery", None) is not discovery:
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_DISCOVERY_INSTANCE_MISMATCH"
            )
        self._discovery = discovery
        self._coverage = coverage_service
        self._classification = classification_service

    def reconcile(
        self,
        *,
        scope: LegalEvidenceProviderDiscoveryScope,
        provider_name: str,
        observed_at: datetime,
        session: Any,
    ) -> LegalEvidenceProviderReadOnlyReconciliationResult:
        """Produce one exhaustive, tenant/provider/time-bound read-only result.

        The coverage service traverses its certified provider enumeration seam
        before discovery is consumed. Each discovered completed object must be
        present in the exact issuing service's sealed coverage membership.
        The existing classifier and correlation service then run with the exact
        caller-owned active transaction. Their results must match the observed
        source snapshot semantically; source drift rejects instead of returning
        a misleading complete result.
        """
        tx = _require_active_transaction(session)
        if type(scope) is not LegalEvidenceProviderDiscoveryScope:
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_SCOPE_REQUIRED"
            )
        if not isinstance(provider_name, str) or not provider_name.strip():
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_PROVIDER_REQUIRED"
            )
        provider = provider_name.strip()
        at = _utc(observed_at)

        verification = self._coverage.verify_coverage(
            scope=scope,
            provider_name=provider,
            observed_at=at,
        )
        if (
            not self._coverage.accepts_verification(verification)
            or type(verification) is not LegalEvidenceProviderCoverageVerification
            or verification.tenant_id != scope.tenant_id
            or verification.tenant_scope_fingerprint != scope.tenant_scope_fingerprint
            or verification.provider_name != provider
            or verification.observed_at != at
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_COVERAGE_SCOPE_MISMATCH"
            )

        incomplete = self._discovery.list_incomplete_write_sessions(
            scope, observed_at=at
        )
        completed = self._discovery.list_completed_object_versions(
            scope, observed_at=at
        )
        if type(incomplete) is not tuple or type(completed) is not tuple:
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_DISCOVERY_RESULT_INVALID"
            )

        source = incomplete + completed
        for item in source:
            key = _observation_key(item)
            if item.tenant_id != scope.tenant_id or item.provider_name != provider:
                raise LegalEvidenceProviderReadOnlyReconciliationError(
                    "L10A2R_C4D7A_OBSERVATION_SCOPE_MISMATCH"
                )
            if item.observed_at != at:
                raise LegalEvidenceProviderReadOnlyReconciliationError(
                    "L10A2R_C4D7A_OBSERVATION_TIME_MISMATCH"
                )
            if key[0] == "COMPLETED" and not self._coverage.contains_completed_observation(
                verified=verification, observation=item
            ):
                raise LegalEvidenceProviderReadOnlyReconciliationError(
                    "L10A2R_C4D7A_COMPLETED_OBSERVATION_NOT_COVERED"
                )

        # The current trusted verifier seals exact completed-object membership,
        # but only page-level fingerprints (not individual membership digests) for
        # incomplete sessions. Count equality alone cannot prove identity. Refuse
        # to report a complete reconciliation while any incomplete session exists.
        if incomplete:
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_INCOMPLETE_MEMBERSHIP_UNPROVEN"
            )
        if (
            len(incomplete) != verification.incomplete_observation_count
            or len(completed) != verification.completed_observation_count
        ):
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_COVERAGE_COUNT_MISMATCH"
            )

        classified = self._classification.classify_tenant_observations(
            scope=scope, observed_at=at, session=tx
        )
        correlations = self._classification.correlate_tenant_completed_write_intents(
            scope=scope, observed_at=at, session=tx
        )
        if type(classified) is not tuple or type(correlations) is not tuple:
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_CLASSIFICATION_RESULT_INVALID"
            )

        expected_classification = tuple(
            sorted(
                (
                    (
                        "INCOMPLETE",
                        item.tenant_id,
                        item.provider_name,
                        item.storage_reference,
                        item.write_session_reference,
                        "",
                        "",
                        "",
                        item.observed_at.isoformat(),
                        item.initiated_at.isoformat(),
                    )
                    if type(item) is LegalEvidenceIncompleteWriteSessionObservation
                    else (
                        "COMPLETED",
                        item.tenant_id,
                        item.provider_name,
                        item.storage_reference,
                        item.object_version_reference,
                        item.provider_integrity_reference,
                        str(item.content_length),
                        item.last_modified_at.isoformat(),
                        item.observed_at.isoformat(),
                        "",
                    )
                    for item in source
                )
            )
        )
        actual_classification = tuple(sorted(_classification_key(item) for item in classified))
        if actual_classification != expected_classification:
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_CLASSIFICATION_SOURCE_DRIFT"
            )

        expected_correlations = tuple(
            sorted(
                (
                    item.tenant_id,
                    item.provider_name,
                    item.storage_reference,
                    item.object_version_reference,
                    item.observed_at.isoformat(),
                )
                for item in completed
            )
        )
        actual_correlations = tuple(sorted(_correlation_key(item) for item in correlations))
        if actual_correlations != expected_correlations:
            raise LegalEvidenceProviderReadOnlyReconciliationError(
                "L10A2R_C4D7A_CORRELATION_SOURCE_DRIFT"
            )

        return LegalEvidenceProviderReadOnlyReconciliationResult(
            tenant_id=scope.tenant_id,
            tenant_scope_fingerprint=scope.tenant_scope_fingerprint,
            provider_name=provider,
            observed_at=at,
            coverage_verification_fingerprint=verification.fingerprint,
            incomplete_observation_count=len(incomplete),
            completed_observation_count=len(completed),
            classifications=classified,
            write_intent_correlations=correlations,
        )


__all__ = [
    "VERSION",
    "LegalEvidenceProviderReadOnlyReconciliationError",
    "LegalEvidenceProviderReadOnlyReconciliationTransactionRequiredError",
    "LegalEvidenceProviderReadOnlyReconciliationResult",
    "LegalEvidenceProviderReadOnlyReconciliationCoordinator",
]


# ARTIFACT: legal_evidence_provider_readonly_reconciliation_coordinator.py
# VERSION: v1.0.0-L10A2R-C4D7A-READONLY-RECONCILIATION-COORDINATOR
# AUTHORITY BOUNDARY: exhaustive provider coverage plus read-only classification/correlation only
# TENANT POSTURE: exact tenant/provider/scope/time binding; divergence rejects
# FAIL-CLOSED POSTURE: missing, incomplete, divergent or tampered evidence rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
