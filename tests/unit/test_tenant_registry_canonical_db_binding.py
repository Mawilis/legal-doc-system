"""WILSY OS tenant registry canonical database binding certificate.

TITLE: Tenant Registry Canonical Kernel Database Binding
VERSION: v1.0.1-PYRIGHT-CLOSURE-CERT
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Proves tenant persistence is import-inert and resolves lazily from the
         sole kernel database owner without changing tenant authority semantics.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_registry_canonical_db_binding.py
COLLABORATION / OWNERSHIP: TenantRegistry, tools.eos.kernel.db, and auth_router.
CERTIFICATION / UPDATE DATE: 2026-09-17.
CHANGELOG: v1.0.1-PYRIGHT-CLOSURE-CERT — Types the deterministic session
           sentinel without weakening the production ClientSession contract.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic documents only; no network or production data.
TENANT BOUNDARY: Alias lookup is exact and server-side against the canonical collection.
AUTHORITY BOUNDARY: Persistence binding evidence only; no tenant/role/permission grant.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import pytest
from pymongo.errors import PyMongoError

import tools.eos.saas.tenancy.tenant_registry as registry_module
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry, TenantRegistryError


def _tenant_doc(tenant_id: str = "WILSYTENANT-test") -> dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "alias": "wilsy",
        "name": "Wilsy (Pty) Ltd",
        "industry": "Legal",
        "plan": "ENTERPRISE",
        "status": "ACTIVE",
        "regions": ["Africa"],
        "created_at": "2026-09-17T00:00:00+00:00",
        "verified": True,
    }


class _Collection:
    def __init__(self, result: dict[str, Any] | None = None, error: Exception | None = None) -> None:
        self.result = result
        self.error = error
        self.queries: list[dict[str, Any]] = []

    def find_one(self, query: dict[str, Any], **_kwargs: Any) -> dict[str, Any] | None:
        self.queries.append(query)
        if self.error:
            raise self.error
        return self.result


class _Database:
    def __init__(self, collection: _Collection) -> None:
        self.collection = collection
        self.requests = 0

    def __getitem__(self, name: str) -> _Collection:
        assert name == "tenants"
        self.requests += 1
        return self.collection


def test_registry_source_has_no_private_driver_or_uri_lifecycle() -> None:
    source = Path(registry_module.__file__).read_text(encoding="utf-8")
    assert "MongoClient" not in source
    assert "MONGO_URI" not in source
    assert "MONGODB_URI" not in source
    assert "os.getenv" not in source
    assert registry_module.tenants_collection is None


def test_import_is_inert_and_database_is_resolved_lazily(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    collection = _Collection(_tenant_doc())
    database = _Database(collection)
    calls: list[str] = []

    def get_database() -> _Database:
        calls.append("get_database")
        return database

    monkeypatch.setattr(registry_module.kernel_db, "get_database", get_database)
    assert calls == []

    tenant = TenantRegistry.get_tenant_by_alias("wilsy")

    assert calls == ["get_database"]
    assert database.requests == 1
    assert tenant is not None
    assert tenant.tenant_id == "WILSYTENANT-test"
    assert collection.queries == [
        {
            "$or": [
                {"alias": {"$regex": "^wilsy$", "$options": "i"}},
                {"tenant_id": {"$regex": "^wilsy$", "$options": "i"}},
                {"name": {"$regex": "^wilsy$", "$options": "i"}},
            ]
        }
    ]


def test_canonical_database_unavailability_is_not_tenant_absence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(registry_module.kernel_db, "get_database", lambda: None)

    with pytest.raises(TenantRegistryError, match="TENANT_REGISTRY_GET_UNAVAILABLE"):
        TenantRegistry.get("WILSYTENANT-missing")

    with pytest.raises(TenantRegistryError, match="TENANT_REGISTRY_ALIAS_LOOKUP_UNAVAILABLE"):
        TenantRegistry.get_tenant_by_alias("wilsy")


def test_explicit_collection_remains_authoritative_and_bypasses_kernel(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    explicit = _Collection(_tenant_doc("WILSYTENANT-explicit"))
    monkeypatch.setattr(
        registry_module.kernel_db,
        "get_database",
        lambda: (_ for _ in ()).throw(AssertionError("kernel database should not be used")),
    )

    tenant = TenantRegistry.get(
        "WILSYTENANT-explicit",
        collection=explicit,  # type: ignore[arg-type]
        session=cast(Any, object()),
    )

    assert tenant is not None
    assert tenant.tenant_id == "WILSYTENANT-explicit"


def test_mongo_failure_remains_distinct_from_alias_absence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    collection = _Collection(error=PyMongoError("unauthorized"))
    monkeypatch.setattr(
        registry_module.kernel_db,
        "get_database",
        lambda: _Database(collection),
    )

    with pytest.raises(
        TenantRegistryError,
        match="TENANT_REGISTRY_ALIAS_LOOKUP_UNAVAILABLE",
    ):
        TenantRegistry.get_tenant_by_alias("wilsy")


# ARTIFACT: test_tenant_registry_canonical_db_binding.py
# VERSION: v1.0.1-PYRIGHT-CLOSURE-CERT
# AUTHORITY BOUNDARY: canonical persistence binding evidence only
# TENANT POSTURE: exact server-side alias lookup; no directory or fallback authority
# FAIL-CLOSED POSTURE: unavailable canonical DB never becomes tenant absence
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
