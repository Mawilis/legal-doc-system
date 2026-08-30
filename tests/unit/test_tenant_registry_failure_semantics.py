"""TITLE: WILSY OS Tenant Registry Failure Semantics Unit Certification.
VERSION: v1.0.0-TENANT-REGISTRY-FAILURE-SEMANTICS-CERT
AUTHORITY: Deterministic unit certification of TenantRegistry get/archive absence-vs-outage behavior.
EPITOME: Proves successful lookup/archive, genuine absence/no-change, explicit PyMongo outage signaling, cause preservation, and transport non-authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_registry_failure_semantics.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-30.
CHANGELOG: v1.0.0 establishes bounded get/archive failure-semantics certification for 3K2.8B1.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Controlled in-memory fakes only; no credentials, production tenant data, or network access.
TENANT BOUNDARY: Exact tenant identifiers are asserted; compatibility header values never alter lookup/archive scope.
AUTHORITY BOUNDARY: Persistence-boundary certification only; no authentication, authorization, role, membership, or HTTP authority.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains exclusive.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any

import pytest
from pymongo.errors import PyMongoError

import tools.eos.saas.tenancy.tenant_registry as registry_module
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry, TenantRegistryError

VERSION = "v1.0.0-TENANT-REGISTRY-FAILURE-SEMANTICS-CERT"


@dataclass(frozen=True, slots=True)
class _UpdateResult:
    modified_count: int


class _CollectionFake:
    """Minimal deterministic collection double for get/archive certification."""

    def __init__(
        self,
        *,
        find_result: dict[str, Any] | None = None,
        find_error: PyMongoError | None = None,
        modified_count: int = 0,
        update_error: PyMongoError | None = None,
    ) -> None:
        self.find_result = find_result
        self.find_error = find_error
        self.modified_count = modified_count
        self.update_error = update_error
        self.find_calls: list[dict[str, Any]] = []
        self.update_calls: list[tuple[dict[str, Any], dict[str, Any]]] = []

    def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        self.find_calls.append(query)
        if self.find_error is not None:
            raise self.find_error
        return self.find_result

    def update_one(
        self,
        query: dict[str, Any],
        update: dict[str, Any],
    ) -> _UpdateResult:
        self.update_calls.append((query, update))
        if self.update_error is not None:
            raise self.update_error
        return _UpdateResult(self.modified_count)


def _tenant_doc(tenant_id: str = "tenant-a") -> dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "name": "Tenant A",
        "industry": "General",
        "plan": "ENTERPRISE",
        "status": "ACTIVE",
        "regions": ["Africa"],
        "created_at": "2026-08-30T00:00:00+00:00",
        "alias": "tenant-a",
        "region": "ZA",
        "verified": False,
    }


def test_registry_error_is_bounded_runtime_error() -> None:
    """The persistence outage type is explicit and not an HTTP/authority decision."""
    assert issubclass(TenantRegistryError, RuntimeError)
    assert TenantRegistryError.__module__ == registry_module.__name__


def test_get_success_returns_mapped_tenant(monkeypatch: pytest.MonkeyPatch) -> None:
    """A successful lookup returns the mapped tenant entity."""
    fake = _CollectionFake(find_result=_tenant_doc())
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    tenant = TenantRegistry.get("tenant-a")

    assert tenant is not None
    assert tenant.tenant_id == "tenant-a"
    assert tenant.organization.organization_name == "Tenant A"
    assert fake.find_calls == [{"tenant_id": "tenant-a"}]


def test_get_missing_returns_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Genuine persistence absence remains None."""
    fake = _CollectionFake(find_result=None)
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    assert TenantRegistry.get("missing") is None
    assert fake.find_calls == [{"tenant_id": "missing"}]


def test_get_outage_raises_bounded_error_with_cause(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PyMongo failure cannot masquerade as tenant absence."""
    failure = PyMongoError("get outage")
    fake = _CollectionFake(find_error=failure)
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    with pytest.raises(TenantRegistryError, match="TENANT_REGISTRY_GET_UNAVAILABLE") as raised:
        TenantRegistry.get("tenant-a")

    assert raised.value.__cause__ is failure
    assert fake.find_calls == [{"tenant_id": "tenant-a"}]


def test_get_outage_is_never_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """The outage branch is structurally distinct from the absence branch."""
    fake = _CollectionFake(find_error=PyMongoError("offline"))
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    with pytest.raises(TenantRegistryError):
        TenantRegistry.get("tenant-a")


def test_archive_success_updates_exact_tenant(monkeypatch: pytest.MonkeyPatch) -> None:
    """Successful archive preserves archive-only status mutation semantics."""
    fake = _CollectionFake(modified_count=1)
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    assert TenantRegistry.archive("tenant-a") is True
    assert fake.update_calls == [
        ({"tenant_id": "tenant-a"}, {"$set": {"status": "ARCHIVED"}})
    ]


def test_archive_zero_modification_returns_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A genuine zero-modification result remains ordinary False."""
    fake = _CollectionFake(modified_count=0)
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    assert TenantRegistry.archive("missing") is False
    assert fake.update_calls == [
        ({"tenant_id": "missing"}, {"$set": {"status": "ARCHIVED"}})
    ]


def test_archive_outage_raises_bounded_error_with_cause(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PyMongo failure cannot masquerade as an ordinary archive no-change."""
    failure = PyMongoError("archive outage")
    fake = _CollectionFake(update_error=failure)
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    with pytest.raises(
        TenantRegistryError,
        match="TENANT_REGISTRY_ARCHIVE_UNAVAILABLE",
    ) as raised:
        TenantRegistry.archive("tenant-a")

    assert raised.value.__cause__ is failure


def test_archive_outage_is_never_false(monkeypatch: pytest.MonkeyPatch) -> None:
    """The outage branch is structurally distinct from modified_count == 0."""
    fake = _CollectionFake(update_error=PyMongoError("offline"))
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    with pytest.raises(TenantRegistryError):
        TenantRegistry.archive("tenant-a")


def test_compatibility_header_is_never_lookup_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Different compatibility header projections produce the same tenant-id lookup."""
    fake = _CollectionFake(find_result=_tenant_doc())
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    first = TenantRegistry.get("tenant-a", tenant_id_header="GLOBAL_ROOT")
    second = TenantRegistry.get("tenant-a", tenant_id_header="tenant-b")

    assert first is not None and second is not None
    assert first.tenant_id == second.tenant_id == "tenant-a"
    assert fake.find_calls == [
        {"tenant_id": "tenant-a"},
        {"tenant_id": "tenant-a"},
    ]


def test_compatibility_header_is_never_archive_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Different compatibility header projections cannot widen archive target scope."""
    fake = _CollectionFake(modified_count=1)
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    assert TenantRegistry.archive("tenant-a", tenant_id_header="GLOBAL_ROOT") is True
    assert TenantRegistry.archive("tenant-a", tenant_id_header="tenant-b") is True
    assert fake.update_calls == [
        ({"tenant_id": "tenant-a"}, {"$set": {"status": "ARCHIVED"}}),
        ({"tenant_id": "tenant-a"}, {"$set": {"status": "ARCHIVED"}}),
    ]


def test_registry_signatures_expose_no_role_jwt_permission_or_financial_authority() -> None:
    """Public get/archive inputs contain no grant-bearing caller projections."""
    forbidden = {
        "role",
        "roles",
        "jwt_role",
        "jwt_roles",
        "permission",
        "permissions",
        "caller_role",
        "authorization",
        "financial_execution",
    }
    for method in (TenantRegistry.get, TenantRegistry.archive):
        assert not forbidden.intersection(inspect.signature(method).parameters)


def test_get_archive_cert_does_not_mutate_other_registry_methods(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Certification substitutes only persistence state; other public methods remain intact."""
    original_methods = {
        name: TenantRegistry.__dict__[name]
        for name in ("list", "get_tenant_by_alias", "create", "update")
    }
    fake = _CollectionFake(find_result=None, modified_count=0)
    monkeypatch.setattr(registry_module, "tenants_collection", fake)

    assert TenantRegistry.get("missing") is None
    assert TenantRegistry.archive("missing") is False

    assert {
        name: TenantRegistry.__dict__[name]
        for name in original_methods
    } == original_methods


def test_collection_substitution_restores_after_bounded_context(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A bounded monkeypatch context restores the real module collection reference."""
    original = registry_module.tenants_collection
    fake = _CollectionFake(find_result=None)

    with monkeypatch.context() as scoped:
        scoped.setattr(registry_module, "tenants_collection", fake)
        assert registry_module.tenants_collection is fake
        assert TenantRegistry.get("missing") is None

    assert registry_module.tenants_collection is original


# ARTIFACT: test_tenant_registry_failure_semantics.py
# VERSION: v1.0.0-TENANT-REGISTRY-FAILURE-SEMANTICS-CERT
# AUTHORITY BOUNDARY: deterministic persistence-boundary certification only; no authentication, authorization, role, or membership authority
# TENANT POSTURE: exact tenant-id filters are certified; compatibility headers never alter target scope
# FAIL-CLOSED POSTURE: Mongo outages raise bounded TenantRegistryError and cannot collapse into tenant absence or archive no-change
# FINANCIAL EXECUTION AUTHORITY: None. Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
