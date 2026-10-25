"""WILSY OS Legal Evidence read-only reconciliation dependency factory.

TITLE: Legal Evidence Read-Only Reconciliation Dependency Factory
VERSION: v1.1.0-L10A2R-C4D7B-READONLY-FACADE-REQUIRED
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Construct the existing certified read-only reconciliation services
         from an explicitly configured provider and caller-owned Mongo database.
ABSOLUTE CANONICAL PATH:
    tools/eos/legal_operations/service/legal_evidence_provider_readonly_reconciliation_factory.py
COLLABORATION / OWNERSHIP:
    Composes existing C2, C4B, C4D5C, C4D6B and C4D7A components. Does not
    own provider configuration, authentication, tenant authorization, indexes,
    transaction lifecycle, cleanup authorization, or provider mutation.
CERTIFICATION / UPDATE DATE: 2026-10-25
CHANGELOG:
    v1.1.0-L10A2R-C4D7B-READONLY-FACADE-REQUIRED requires the explicit read-only provider facade so a broader
    upload adapter's mutation methods are not exposed through reconciliation.
    Construction still performs no provider I/O, index creation, persistence
    writes, or transaction lifecycle.
COMPLIANCE:
    Implements engineering boundaries only; makes no independent compliance claim.
SECURITY / PRIVACY POSTURE:
    Requires an explicitly configured provider and Mongo database. Rejects
    missing dependencies before constructing any service.
TENANT BOUNDARY:
    Tenant scope is supplied later to the coordinator and never inferred here.
AUTHORITY BOUNDARY:
    Construction only. The returned coordinator is read-only and does not
    authorize cleanup, orphan proof, retention/hold release, or deletion.
FINANCIAL AUTHORITY BOUNDARY:
    None. Kennel EOS exclusively owns financial execution and settlement.
TRANSACTION BOUNDARY:
    Accepts an existing database handle but never opens a session or starts,
    commits, aborts, or retries a transaction. Callers pass an active session
    to coordinator.reconcile().
FAIL-CLOSED POSTURE:
    Missing/invalid provider or database collection access rejects; no fallback
    configuration, default tenant, or synthetic provider is created.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from tools.eos.legal_operations.registry.legal_evidence_binary_write_intent_registry import (
    COLLECTION as WRITE_INTENT_COLLECTION,
    LegalEvidenceBinaryWriteIntentRegistry,
)
from tools.eos.legal_operations.registry.legal_evidence_commit_uncertainty_registry import (
    COLLECTION as UNCERTAINTY_COLLECTION,
    LegalEvidenceCommitUncertaintyRegistry,
)
from tools.eos.legal_operations.registry.legal_evidence_object_metadata_registry import (
    COLLECTION as METADATA_COLLECTION,
    LegalEvidenceObjectMetadataRegistry,
)
from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_classification_service import (
    LegalEvidenceProviderCleanupClassificationService,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_enumeration_port import (
    LegalEvidenceProviderCoverageEnumerationPort,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_verification_service import (
    LegalEvidenceProviderCoverageVerificationService,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_provider import (
    LegalEvidenceProviderReadOnlyReconciliationProvider,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_coordinator import (
    LegalEvidenceProviderReadOnlyReconciliationCoordinator,
)


VERSION: Final[str] = "v1.1.0-L10A2R-C4D7B-READONLY-FACADE-REQUIRED"


class LegalEvidenceProviderReadOnlyReconciliationFactoryError(RuntimeError):
    """Stable, non-sensitive dependency-construction failure."""


@dataclass(frozen=True, slots=True)
class LegalEvidenceProviderReadOnlyReconciliationDependencies:
    """Explicitly assembled services; no lifecycle or mutation methods."""

    coordinator: LegalEvidenceProviderReadOnlyReconciliationCoordinator
    discovery: LegalEvidenceProviderReadOnlyReconciliationProvider
    coverage_service: LegalEvidenceProviderCoverageVerificationService
    classification_service: LegalEvidenceProviderCleanupClassificationService


def _required_collection(database: Any, name: str) -> Any:
    """Resolve one existing Mongo collection without creating indexes or data."""
    try:
        collection = database[name]
    except (KeyError, TypeError, AttributeError) as error:
        raise LegalEvidenceProviderReadOnlyReconciliationFactoryError(
            "L10A2R_C4D7B_MONGO_COLLECTION_UNAVAILABLE"
        ) from error
    if collection is None:
        raise LegalEvidenceProviderReadOnlyReconciliationFactoryError(
            "L10A2R_C4D7B_MONGO_COLLECTION_UNAVAILABLE"
        )
    return collection


def build_legal_evidence_provider_readonly_reconciliation_dependencies(
    *,
    provider: object,
    mongo_database: Any,
) -> LegalEvidenceProviderReadOnlyReconciliationDependencies:
    """Build the certified read-only service graph from explicit dependencies.

    The caller must supply a `LegalEvidenceProviderReadOnlyReconciliationProvider`
    facade around the already configured adapter, plus the intended Mongo
    database handle. The facade exposes only discovery and coverage-page
    enumeration; arbitrary adapter attributes and upload/mutation methods are
    not forwarded. This function does not create clients, read environment
    variables, start transactions, create indexes, perform provider calls, or
    write persistence. The exact same facade instance is passed to all services.
    """
    if provider is None:
        raise LegalEvidenceProviderReadOnlyReconciliationFactoryError(
            "L10A2R_C4D7B_PROVIDER_REQUIRED"
        )
    if type(provider) is not LegalEvidenceProviderReadOnlyReconciliationProvider:
        raise LegalEvidenceProviderReadOnlyReconciliationFactoryError(
            "L10A2R_C4D7B_READ_ONLY_PROVIDER_FACADE_REQUIRED"
        )
    if not isinstance(provider, LegalEvidenceProviderCoverageEnumerationPort):
        raise LegalEvidenceProviderReadOnlyReconciliationFactoryError(
            "L10A2R_C4D7B_COVERAGE_PROVIDER_INVALID"
        )
    for method in ("list_incomplete_write_sessions", "list_completed_object_versions"):
        if not callable(getattr(provider, method, None)):
            raise LegalEvidenceProviderReadOnlyReconciliationFactoryError(
                "L10A2R_C4D7B_DISCOVERY_PROVIDER_INVALID"
            )
    if mongo_database is None or not callable(getattr(mongo_database, "__getitem__", None)):
        raise LegalEvidenceProviderReadOnlyReconciliationFactoryError(
            "L10A2R_C4D7B_MONGO_DATABASE_REQUIRED"
        )

    metadata_collection = _required_collection(mongo_database, METADATA_COLLECTION)
    uncertainty_collection = _required_collection(mongo_database, UNCERTAINTY_COLLECTION)
    write_intent_collection = _required_collection(mongo_database, WRITE_INTENT_COLLECTION)

    metadata_registry = LegalEvidenceObjectMetadataRegistry(metadata_collection)
    uncertainty_registry = LegalEvidenceCommitUncertaintyRegistry(uncertainty_collection)
    write_intent_registry = LegalEvidenceBinaryWriteIntentRegistry(write_intent_collection)

    coverage_service = LegalEvidenceProviderCoverageVerificationService(
        provider=provider,
    )
    classification_service = LegalEvidenceProviderCleanupClassificationService(
        discovery=provider,
        metadata_registry=metadata_registry,
        uncertainty_registry=uncertainty_registry,
        write_intent_registry=write_intent_registry,
    )
    coordinator = LegalEvidenceProviderReadOnlyReconciliationCoordinator(
        discovery=provider,
        coverage_service=coverage_service,
        classification_service=classification_service,
    )
    return LegalEvidenceProviderReadOnlyReconciliationDependencies(
        coordinator=coordinator,
        discovery=provider,
        coverage_service=coverage_service,
        classification_service=classification_service,
    )


__all__ = [
    "VERSION",
    "LegalEvidenceProviderReadOnlyReconciliationFactoryError",
    "LegalEvidenceProviderReadOnlyReconciliationDependencies",
    "build_legal_evidence_provider_readonly_reconciliation_dependencies",
]


# ARTIFACT: legal_evidence_provider_readonly_reconciliation_factory.py
# VERSION: v1.1.0-L10A2R-C4D7B-READONLY-FACADE-REQUIRED
# AUTHORITY BOUNDARY: explicit dependency construction only; read-only coordinator
# TENANT POSTURE: scope remains caller-supplied and server-authorized
# FAIL-CLOSED POSTURE: missing dependencies reject; no defaults or side effects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
