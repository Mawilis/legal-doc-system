# -*- coding: utf-8 -*-
"""
===============================================================================
WILSY OS — SOVEREIGN CERTIFICATION ARTIFACT
TENANT REGISTRY — MAPPING FAILURE SEMANTICS — UNIT CERTIFICATE
===============================================================================

TITLE:
    WILSY OS Tenant Registry Mapping Failure Semantics Unit Certification

FILE:
    tests/unit/test_tenant_registry_mapping_failure_semantics.py

VERSION:
    v1.0.0-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS-CERT

AUTHORITY:
    Wilsy OS Core Governance.
    Deterministic unit certification of the TenantRegistry GET persistence and
    read-integrity contract.

EPITOME:
    Certifies that healthy persisted tenant truth maps successfully, genuine
    absence alone returns None, malformed persisted tenant truth raises the exact
    GET-invalid-document error, MongoDB outage remains a distinct failure class,
    ObjectId compatibility stays bounded, list tolerance remains unchanged, and
    transport projections never become registry authority.

ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_registry_mapping_failure_semantics.py

COLLABORATION / OWNERSHIP:
    Wilson Khanyezi / Wilsy Core Engineering.

CERTIFICATION / UPDATE DATE:
    2026-08-30

CHANGELOG:
    v1.0.0-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS-CERT
        - Establishes deterministic B1.1 mapping-failure certification.
        - Proves invalid persisted GET truth cannot masquerade as absence.
        - Locks GET-invalid-document versus GET-unavailable semantics.
        - Preserves ObjectId compatibility, list behavior, archive behavior,
          and compatibility-header non-authority.

COMPLIANCE:
    POPIA section 19.
    GDPR Article 32.
    SOC 2 CC7.2.
    ISO 27001.

SECURITY / PRIVACY POSTURE:
    In-memory deterministic collection doubles only.
    No production tenant data, credentials, network access, or persistent
    mutation outside bounded test substitution.

TENANT BOUNDARY:
    Exact tenant identifiers are asserted.
    tenant_id_header is compatibility-only and cannot redirect tenant lookup.

AUTHORITY BOUNDARY:
    Evidence only.
    No authentication, authorization, membership, role, permission, JWT, HTTP,
    or financial authority is created by this certificate.

FINANCIAL AUTHORITY BOUNDARY:
    No financial state or execution is touched.
    Kennel EOS remains the exclusive financial execution authority.

CERTIFICATION CLASS:
    UNIT / DETERMINISTIC / FAIL-CLOSED

STRUCTURAL GOVERNANCE:
    AGENTS.md v1.2.0-SOVEREIGN-LEGAL-OPERATIONS-CONSTITUTION.
===============================================================================
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Iterator

import pytest
from bson import ObjectId
from pymongo.errors import PyMongoError

import tools.eos.saas.tenancy.tenant_registry as registry_module
from tools.eos.saas.tenancy.tenant_registry import (
    TenantRegistry,
    TenantRegistryError,
)


# =============================================================================
# CERTIFICATION CONSTANTS
# =============================================================================

VERSION = "v1.0.0-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS-CERT"
EXPECTED_PRIMARY_VERSION = "v1.3.1-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS"
INVALID_DOCUMENT = "TENANT_REGISTRY_GET_INVALID_DOCUMENT"
GET_UNAVAILABLE = "TENANT_REGISTRY_GET_UNAVAILABLE"


# =============================================================================
# DETERMINISTIC COLLECTION EVIDENCE DOUBLES
# =============================================================================


@dataclass(frozen=True, slots=True)
class _UpdateResult:
    """Represent the exact modified_count contract consumed by archive()."""

    modified_count: int


class _CursorFake:
    """Represent the bounded cursor protocol consumed by TenantRegistry.list()."""

    def __init__(self, docs: list[dict[str, Any]]) -> None:
        self._docs = docs

    def skip(self, _value: int) -> "_CursorFake":
        """Preserve the cursor while recording no additional authority."""
        return self

    def limit(self, _value: int) -> "_CursorFake":
        """Preserve the cursor while recording no additional authority."""
        return self

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Yield the deterministic persisted documents."""
        return iter(self._docs)


class _CollectionFake:
    """Provide the minimal deterministic Mongo collection contract under test."""

    def __init__(
        self,
        *,
        find_results: list[dict[str, Any] | None] | None = None,
        list_docs: list[dict[str, Any]] | None = None,
        find_error: PyMongoError | None = None,
        modified_count: int = 0,
    ) -> None:
        self.find_results = list(find_results or [])
        self.list_docs = list(list_docs or [])
        self.find_error = find_error
        self.modified_count = modified_count
        self.find_calls: list[dict[str, Any]] = []
        self.update_calls: list[tuple[dict[str, Any], dict[str, Any]]] = []

    def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        """Resolve one deterministic result or raise the configured Mongo failure."""
        self.find_calls.append(query)
        if self.find_error is not None:
            raise self.find_error
        if self.find_results:
            return self.find_results.pop(0)
        return None

    def count_documents(self, query: dict[str, Any]) -> int:
        """Return the deterministic total used by legacy list behavior."""
        assert query == {}
        return len(self.list_docs)

    def find(
        self,
        query: dict[str, Any],
        projection: dict[str, Any],
    ) -> _CursorFake:
        """Return the deterministic list cursor."""
        assert query == {}
        assert projection == {"_id": 0}
        return _CursorFake(self.list_docs)

    def update_one(
        self,
        query: dict[str, Any],
        update: dict[str, Any],
    ) -> _UpdateResult:
        """Record the exact archive mutation and return modified_count evidence."""
        self.update_calls.append((query, update))
        return _UpdateResult(self.modified_count)


# =============================================================================
# CANONICAL TEST DOCUMENT BUILDERS
# =============================================================================


def _tenant_doc(tenant_id: str = "tenant-a") -> dict[str, Any]:
    """Build one healthy deterministic tenant persistence document."""
    return {
        "tenant_id": tenant_id,
        "name": "Tenant A",
        "industry": "General",
        "plan": "ENTERPRISE",
        "status": "ACTIVE",
        "regions": ["Africa"],
        "created_at": "2026-08-30T00:00:00+00:00",
        "alias": tenant_id,
        "region": "ZA",
        "verified": False,
    }


def _invalid_doc(tenant_id: str = "tenant-corrupt") -> dict[str, Any]:
    """Build an existing document that enters and fails the real mapper."""
    doc = _tenant_doc(tenant_id)
    doc["subscription"] = "corrupt"
    return doc


# =============================================================================
# VERSION AND ERROR-SURFACE CERTIFICATION
# =============================================================================


def test_primary_version_and_error_type_are_exact() -> None:
    """Lock the B1.1 production version and bounded error type."""
    assert registry_module.VERSION == EXPECTED_PRIMARY_VERSION
    assert issubclass(TenantRegistryError, RuntimeError)


# =============================================================================
# HEALTHY GET / GENUINE ABSENCE CERTIFICATION
# =============================================================================


def test_healthy_matching_document_maps_to_entity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A healthy matching persisted document returns the correct tenant entity."""
    fake = _CollectionFake(find_results=[_tenant_doc()])
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    tenant = TenantRegistry.get("tenant-a")

    assert tenant is not None
    assert tenant.tenant_id == "tenant-a"
    assert tenant.organization.organization_name == "Tenant A"
    assert fake.find_calls == [{"tenant_id": "tenant-a"}]


def test_genuine_absence_is_still_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """A genuinely absent tenant remains the sole ordinary None GET result."""
    fake = _CollectionFake(find_results=[None])
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    assert TenantRegistry.get("missing") is None
    assert fake.find_calls == [{"tenant_id": "missing"}]


# =============================================================================
# INVALID PERSISTED TRUTH CERTIFICATION
# =============================================================================


def test_existing_invalid_document_raises_exact_get_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An existing unmappable document raises the exact GET-invalid error."""
    fake = _CollectionFake(find_results=[_invalid_doc()])
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    with pytest.raises(TenantRegistryError) as raised:
        TenantRegistry.get("tenant-corrupt")

    assert str(raised.value) == INVALID_DOCUMENT
    assert raised.value.__cause__ is None
    assert fake.find_calls == [{"tenant_id": "tenant-corrupt"}]


def test_existing_invalid_document_can_never_return_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Persisted corruption is structurally distinct from genuine absence."""
    fake = _CollectionFake(find_results=[_invalid_doc()])
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    with pytest.raises(TenantRegistryError, match=f"^{INVALID_DOCUMENT}$"):
        TenantRegistry.get("tenant-corrupt")


# =============================================================================
# INFRASTRUCTURE OUTAGE CERTIFICATION
# =============================================================================


def test_mongo_outage_remains_distinct_and_preserves_cause(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mongo outage keeps the exact unavailable token and original cause."""
    failure = PyMongoError("offline")
    fake = _CollectionFake(find_error=failure)
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    with pytest.raises(TenantRegistryError) as raised:
        TenantRegistry.get("tenant-a")

    assert str(raised.value) == GET_UNAVAILABLE
    assert raised.value.__cause__ is failure


# =============================================================================
# LEGACY LIST BEHAVIOR PRESERVATION
# =============================================================================


def test_list_still_skips_invalid_document_without_strict_get_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Strict invalid-document failure remains GET-specific, not list-global."""
    fake = _CollectionFake(
        list_docs=[
            _tenant_doc("tenant-good"),
            _invalid_doc("tenant-corrupt"),
        ]
    )
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    result = TenantRegistry.list()

    assert result["total"] == 2
    items = result["items"]
    assert len(items) == 1
    assert items[0].tenant_id == "tenant-good"


# =============================================================================
# OBJECTID COMPATIBILITY CERTIFICATION
# =============================================================================


def test_objectid_compatibility_fallback_remains_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A valid 24-hex identifier retains the existing exact ObjectId fallback."""
    legacy_id = "64f000000000000000000001"
    fake = _CollectionFake(
        find_results=[
            None,
            _tenant_doc(legacy_id),
        ]
    )
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    tenant = TenantRegistry.get(legacy_id)

    assert tenant is not None
    assert tenant.tenant_id == legacy_id
    assert fake.find_calls == [
        {"tenant_id": legacy_id},
        {"_id": ObjectId(legacy_id)},
    ]


def test_invalid_24_character_non_objectid_remains_genuine_absence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalid ObjectId text is bounded and cannot fabricate a second lookup."""
    value = "z" * 24
    fake = _CollectionFake(find_results=[None])
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    assert TenantRegistry.get(value) is None
    assert fake.find_calls == [{"tenant_id": value}]


# =============================================================================
# TRANSPORT NON-AUTHORITY CERTIFICATION
# =============================================================================


def test_compatibility_header_cannot_redirect_strict_mapping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Compatibility header values cannot redirect or authorize tenant lookup."""
    fake = _CollectionFake(find_results=[_invalid_doc("tenant-a")])
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    with pytest.raises(TenantRegistryError, match=f"^{INVALID_DOCUMENT}$"):
        TenantRegistry.get("tenant-a", tenant_id_header="tenant-b")

    assert fake.find_calls == [{"tenant_id": "tenant-a"}]


# =============================================================================
# ARCHIVE AND ADJACENT-BEHAVIOR PRESERVATION
# =============================================================================


def test_archive_semantics_remain_exact(monkeypatch: pytest.MonkeyPatch) -> None:
    """B1.1 preserves the already-certified soft-archive mutation exactly."""
    fake = _CollectionFake(modified_count=1)
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    assert TenantRegistry.archive("tenant-a") is True
    assert fake.update_calls == [
        (
            {"tenant_id": "tenant-a"},
            {"$set": {"status": "ARCHIVED"}},
        )
    ]


def test_other_business_methods_are_not_replaced(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """B1.1 strict GET does not replace list/create/update/alias/archive methods."""
    originals = {
        name: TenantRegistry.__dict__[name]
        for name in (
            "list",
            "get_tenant_by_alias",
            "create",
            "update",
            "archive",
        )
    }
    fake = _CollectionFake(find_results=[None])
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    assert TenantRegistry.get("missing") is None
    assert {
        name: TenantRegistry.__dict__[name]
        for name in originals
    } == originals


# =============================================================================
# AUTHORITY-SURFACE CERTIFICATION
# =============================================================================


def test_registry_surface_exposes_no_role_jwt_permission_or_financial_authority() -> None:
    """Registry public inputs expose no role/JWT/permission/financial grant path."""
    forbidden = {
        "role",
        "roles",
        "jwt_role",
        "jwt_roles",
        "caller_role",
        "permission",
        "permissions",
        "authorization",
        "financial_execution",
    }
    for method in (
        TenantRegistry.get,
        TenantRegistry.list,
        TenantRegistry.create,
        TenantRegistry.update,
        TenantRegistry.archive,
    ):
        assert not forbidden.intersection(inspect.signature(method).parameters)


# =============================================================================
# TEST ISOLATION CERTIFICATION
# =============================================================================


def test_collection_substitution_restores_cleanly(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bounded collection substitution restores the production collection object."""
    original = registry_module.tenants_collection
    fake = _CollectionFake(find_results=[None])

    with monkeypatch.context() as scoped:
        scoped.setattr(registry_module, "tenants_collection", fake)
        assert TenantRegistry.get("missing") is None

    assert registry_module.tenants_collection is original


# =============================================================================
# WILSY OS SOVEREIGN CERTIFICATION SEAL
# =============================================================================
# ARTIFACT: test_tenant_registry_mapping_failure_semantics.py
# VERSION: v1.0.0-TENANT-REGISTRY-MAPPING-FAILURE-SEMANTICS-CERT
# AUTHORITY BOUNDARY: deterministic persistence/read-integrity evidence only; no authentication, membership, role, permission, JWT, HTTP, or financial authority
# TENANT POSTURE: genuine absence alone returns None; an existing unmappable tenant fails explicitly and compatibility headers cannot redirect scope
# FAIL-CLOSED POSTURE: persisted GET corruption raises TENANT_REGISTRY_GET_INVALID_DOCUMENT while Mongo outage remains TENANT_REGISTRY_GET_UNAVAILABLE
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
