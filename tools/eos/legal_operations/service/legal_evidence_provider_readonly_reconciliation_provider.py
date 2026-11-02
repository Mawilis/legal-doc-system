"""Read-only facade for a provider adapter used by reconciliation.

TITLE: Legal Evidence Provider Read-Only Reconciliation Facade
VERSION: v1.0.0-L10A2R-C4D7-READONLY-PROVIDER-FACADE
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
EPITOME: Expose only discovery and exhaustive coverage-enumeration operations
         from a broader provider adapter; do not surface its write methods.
AUTHORITY BOUNDARY: Read-only provider observations only.
TRANSACTION BOUNDARY: Delegates read-only calls; never owns Mongo transactions.
CHANGELOG: v1.0.0 adds a strict facade with no dynamic attribute forwarding.
"""

from __future__ import annotations

from typing import Any, Final

from tools.eos.legal_operations.service.legal_evidence_provider_cleanup_discovery_port import (
    LegalEvidenceCompletedObjectObservation,
    LegalEvidenceIncompleteWriteSessionObservation,
    LegalEvidenceProviderCleanupDiscoveryPort,
    LegalEvidenceProviderDiscoveryScope,
)
from tools.eos.legal_operations.service.legal_evidence_provider_coverage_enumeration_port import (
    LegalEvidenceProviderCoverageEnumerationPort,
    LegalEvidenceProviderEnumerationPage,
)


VERSION: Final[str] = "v1.0.0-L10A2R-C4D7-READONLY-PROVIDER-FACADE"


class LegalEvidenceProviderReadOnlyReconciliationProviderError(RuntimeError):
    """Stable, non-sensitive failure while constructing the read-only facade."""


class LegalEvidenceProviderReadOnlyReconciliationProvider:
    """Expose only the four read-only provider operations reconciliation needs.

    The wrapped adapter may support binary writes for a separate authorized
    upload workflow. This facade deliberately does not forward arbitrary
    attributes and has no public adapter accessor.
    """

    __slots__ = ("__adapter",)

    def __init__(self, adapter: object) -> None:
        if adapter is None:
            raise LegalEvidenceProviderReadOnlyReconciliationProviderError(
                "READ_ONLY_PROVIDER_ADAPTER_REQUIRED"
            )
        if not isinstance(adapter, LegalEvidenceProviderCoverageEnumerationPort):
            raise LegalEvidenceProviderReadOnlyReconciliationProviderError(
                "COVERAGE_ENUMERATION_PORT_REQUIRED"
            )
        for method in (
            "list_incomplete_write_sessions",
            "list_completed_object_versions",
        ):
            if not callable(getattr(adapter, method, None)):
                raise LegalEvidenceProviderReadOnlyReconciliationProviderError(
                    "DISCOVERY_PORT_REQUIRED"
                )
        self.__adapter = adapter

    def list_incomplete_write_session_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: Any,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        """Enumerate one page of incomplete-write-session coverage."""
        return self.__adapter.list_incomplete_write_session_page(
            scope,
            observed_at=observed_at,
            page_reference=page_reference,
        )

    def list_completed_object_version_page(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: Any,
        page_reference: str | None,
    ) -> LegalEvidenceProviderEnumerationPage:
        """Enumerate one page of completed-object-version coverage."""
        return self.__adapter.list_completed_object_version_page(
            scope,
            observed_at=observed_at,
            page_reference=page_reference,
        )

    def list_incomplete_write_sessions(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: Any,
    ) -> tuple[LegalEvidenceIncompleteWriteSessionObservation, ...]:
        """Return incomplete-write observations without exposing write methods."""
        return self.__adapter.list_incomplete_write_sessions(
            scope,
            observed_at=observed_at,
        )

    def list_completed_object_versions(
        self,
        scope: LegalEvidenceProviderDiscoveryScope,
        *,
        observed_at: Any,
    ) -> tuple[LegalEvidenceCompletedObjectObservation, ...]:
        """Return completed-object observations without exposing write methods."""
        return self.__adapter.list_completed_object_versions(
            scope,
            observed_at=observed_at,
        )


__all__ = [
    "VERSION",
    "LegalEvidenceProviderReadOnlyReconciliationProviderError",
    "LegalEvidenceProviderReadOnlyReconciliationProvider",
]


# ARTIFACT: legal_evidence_provider_readonly_reconciliation_provider.py
# VERSION: v1.0.0-L10A2R-C4D7-READONLY-PROVIDER-FACADE
# AUTHORITY BOUNDARY: discovery and coverage enumeration only
# MUTATION POSTURE: no dynamic attribute forwarding or public adapter accessor
# END OF WILSY OS SOVEREIGN ARTIFACT
