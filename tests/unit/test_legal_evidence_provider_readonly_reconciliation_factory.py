"""Adversarial tests for the read-only reconciliation dependency factory.

TITLE: Legal Evidence Read-Only Reconciliation Factory Tests
VERSION: v1.0.0-L10A2R-C4D7B-DEPENDENCY-SEAM-TESTS
AUTHORITY: WILSY OS Core Governance / Python EOS Legal Operations
PURPOSE: Prove fail-closed construction, exact provider identity and no
         construction-time I/O or transaction lifecycle.
AUTHORITY BOUNDARY: Test-only; no provider mutation or cleanup authority.
"""

from __future__ import annotations

import pytest

from tools.eos.legal_operations.registry.legal_evidence_binary_write_intent_registry import (
    COLLECTION as WRITE_INTENT_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_evidence_commit_uncertainty_registry import (
    COLLECTION as UNCERTAINTY_COLLECTION,
)
from tools.eos.legal_operations.registry.legal_evidence_object_metadata_registry import (
    COLLECTION as METADATA_COLLECTION,
)
from tools.eos.legal_operations.service.legal_evidence_provider_readonly_reconciliation_factory import (
    LegalEvidenceProviderReadOnlyReconciliationFactoryError,
    build_legal_evidence_provider_readonly_reconciliation_dependencies,
)


class _Provider:
    """Explicit provider double implementing both required provider seams."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def list_incomplete_write_session_page(self, *args, **kwargs):
        self.calls.append("coverage-incomplete")
        raise AssertionError("provider I/O must not occur during construction")

    def list_completed_object_version_page(self, *args, **kwargs):
        self.calls.append("coverage-completed")
        raise AssertionError("provider I/O must not occur during construction")

    def list_incomplete_write_sessions(self, *args, **kwargs):
        self.calls.append("discovery-incomplete")
        raise AssertionError("provider I/O must not occur during construction")

    def list_completed_object_versions(self, *args, **kwargs):
        self.calls.append("discovery-completed")
        raise AssertionError("provider I/O must not occur during construction")


class _CoverageOnlyProvider:
    """Valid coverage port that deliberately lacks discovery operations."""

    def list_incomplete_write_session_page(self, *args, **kwargs):
        raise AssertionError("provider I/O must not occur during construction")

    def list_completed_object_version_page(self, *args, **kwargs):
        raise AssertionError("provider I/O must not occur during construction")


class _Database:
    def __init__(self, *, missing: str | None = None) -> None:
        self.missing = missing
        self.lookups: list[str] = []
        self.collections = {
            METADATA_COLLECTION: object(),
            UNCERTAINTY_COLLECTION: object(),
            WRITE_INTENT_COLLECTION: object(),
        }

    def __getitem__(self, name: str):
        self.lookups.append(name)
        if name == self.missing:
            raise KeyError(name)
        return self.collections[name]


def test_missing_provider_fails_closed_before_database_access() -> None:
    database = _Database()
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationFactoryError,
        match="PROVIDER_REQUIRED",
    ):
        build_legal_evidence_provider_readonly_reconciliation_dependencies(
            provider=None, mongo_database=database
        )
    assert database.lookups == []


@pytest.mark.parametrize("database", [None, object(), []])
def test_missing_or_invalid_database_fails_closed(database: object) -> None:
    with pytest.raises(LegalEvidenceProviderReadOnlyReconciliationFactoryError):
        build_legal_evidence_provider_readonly_reconciliation_dependencies(
            provider=_Provider(), mongo_database=database
        )


def test_invalid_provider_interface_fails_closed() -> None:
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationFactoryError,
        match="COVERAGE_PROVIDER_INVALID",
    ):
        build_legal_evidence_provider_readonly_reconciliation_dependencies(
            provider=object(), mongo_database=_Database()
        )


def test_coverage_provider_without_discovery_interface_fails_closed() -> None:
    provider = _CoverageOnlyProvider()
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationFactoryError,
        match="DISCOVERY_PROVIDER_INVALID",
    ):
        build_legal_evidence_provider_readonly_reconciliation_dependencies(
            provider=provider, mongo_database=_Database()
        )


@pytest.mark.parametrize(
    "missing",
    [METADATA_COLLECTION, UNCERTAINTY_COLLECTION, WRITE_INTENT_COLLECTION],
)
def test_each_required_mongo_collection_fails_closed_when_missing(missing: str) -> None:
    database = _Database(missing=missing)
    with pytest.raises(
        LegalEvidenceProviderReadOnlyReconciliationFactoryError,
        match="MONGO_COLLECTION_UNAVAILABLE",
    ):
        build_legal_evidence_provider_readonly_reconciliation_dependencies(
            provider=_Provider(), mongo_database=database
        )
    assert missing in database.lookups


def test_factory_wires_exact_same_provider_into_all_services() -> None:
    provider = _Provider()
    database = _Database()
    dependencies = build_legal_evidence_provider_readonly_reconciliation_dependencies(
        provider=provider, mongo_database=database
    )

    assert dependencies.discovery is provider
    assert dependencies.coverage_service._provider is provider
    assert dependencies.classification_service._discovery is provider
    assert dependencies.coordinator._discovery is provider
    assert dependencies.coordinator._coverage is dependencies.coverage_service
    assert dependencies.coordinator._classification is dependencies.classification_service
    assert set(database.lookups) == {
        METADATA_COLLECTION, UNCERTAINTY_COLLECTION, WRITE_INTENT_COLLECTION
    }


def test_construction_has_no_provider_calls_index_creation_or_transaction_lifecycle() -> None:
    provider = _Provider()
    database = _Database()
    dependencies = build_legal_evidence_provider_readonly_reconciliation_dependencies(
        provider=provider, mongo_database=database
    )

    assert provider.calls == []
    # Collection doubles intentionally expose no create_index/session methods;
    # successful construction proves the factory does not invoke either.
    assert all(
        not hasattr(collection, "create_index") and not hasattr(collection, "start_session")
        for collection in database.collections.values()
    )
    assert dependencies.coordinator is not None


# ARTIFACT: test_legal_evidence_provider_readonly_reconciliation_factory.py
# VERSION: v1.0.0-L10A2R-C4D7B-DEPENDENCY-SEAM-TESTS
# AUTHORITY BOUNDARY: test evidence only; no runtime or cleanup authority
# FAIL-CLOSED POSTURE: missing dependencies and interface drift must reject
# END OF WILSY OS SOVEREIGN ARTIFACT
