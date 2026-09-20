"""WILSY OS canonical tenant source-of-truth hardening certificate.

TITLE: R1D-B0F-B3B Canonical Tenant Source-of-Truth Certificate
VERSION: v1.0.1-R1D-B0F-B3B-SIGNING-CONFIG-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves users, hydrated principals, JWTs, sessions, and refresh-token
         validation cannot rely on absent, duplicate, inactive, or pseudo tenants.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_canonical_tenant_source_of_truth.py
COLLABORATION / OWNERSHIP: AuthRegistry, TenantRegistry, auth_router, and
                           browser tenant projection boundaries.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG: v1.0.1-R1D-B0F-B3B-SIGNING-CONFIG-CERT — Supplies an explicit
           synthetic signing secret for session/refresh interoperability while
           preserving fail-closed production configuration.
           v1.0.0-R1D-B0F-B3B-CERT — Initial deterministic source-of-truth
           certificate for canonical tenant identity hardening.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic credentials and in-memory persistence only.
TENANT BOUNDARY: Every identity operation resolves exactly one ACTIVE tenant_id.
AUTHORITY BOUNDARY: Certificate evidence only; no membership or role grants.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""

from __future__ import annotations

import inspect
from datetime import datetime, timedelta
from typing import Any

import pytest

from tools.eos.saas.auth.auth_registry import (
    AuthRegistry,
    AuthRegistryTenantError,
)
from tools.eos.saas.domain.auth import User
from tools.eos.saas.tenancy.tenant_registry import (
    TenantRegistry,
    TenantRegistryError,
)


def _matches(document: dict[str, Any], query: dict[str, Any]) -> bool:
    for field, expected in query.items():
        if isinstance(expected, dict) and "$regex" in expected:
            import re

            if re.search(expected["$regex"], str(document.get(field, "")), re.I if expected.get("$options") == "i" else 0) is None:
                return False
        elif document.get(field) != expected:
            return False
    return True


class _Result:
    def __init__(self, modified_count: int = 1) -> None:
        self.modified_count = modified_count


class _Collection:
    def __init__(self, documents: list[dict[str, Any]] | None = None) -> None:
        self.documents = list(documents or [])
        self.inserted: list[dict[str, Any]] = []

    def count_documents(self, query: dict[str, Any], **_kwargs: Any) -> int:
        return sum(_matches(document, query) for document in self.documents)

    def find_one(self, query: dict[str, Any], **_kwargs: Any) -> dict[str, Any] | None:
        return next((document for document in self.documents if _matches(document, query)), None)

    def insert_one(self, document: dict[str, Any], **_kwargs: Any) -> _Result:
        self.documents.append(dict(document))
        self.inserted.append(dict(document))
        return _Result()

    def update_one(self, query: dict[str, Any], update: dict[str, Any], **_kwargs: Any) -> _Result:
        document = self.find_one(query)
        if document is None:
            return _Result(0)
        document.update(update.get("$set", {}))
        return _Result()


class _Database:
    def __init__(self, tenant_documents: list[dict[str, Any]]) -> None:
        self.collections = {
            "tenants": _Collection(tenant_documents),
            "users": _Collection(),
            "sessions": _Collection(),
            "refresh_tokens": _Collection(),
            "otp_secrets": _Collection(),
            "principal_authorities": _Collection(),
        }

    def __getitem__(self, name: str) -> _Collection:
        return self.collections[name]


def _tenant(tenant_id: str = "TENANT-CANONICAL", *, status: str = "ACTIVE", alias: str = "wilsy") -> dict[str, Any]:
    return {
        "tenant_id": tenant_id,
        "alias": alias,
        "name": "Wilsy (Pty) Ltd",
        "industry": "Legal",
        "plan": "ENTERPRISE",
        "status": status,
        "regions": ["Africa"],
        "created_at": "2026-09-17T00:00:00+00:00",
        "verified": True,
    }


def _registry(monkeypatch: pytest.MonkeyPatch, tenants: list[dict[str, Any]] | None = None) -> tuple[AuthRegistry, _Database]:
    database = _Database(tenants or [_tenant()])
    import tools.eos.saas.auth.auth_registry as auth_module

    monkeypatch.setattr(auth_module.kernel_db, "get_database", lambda: database)
    return AuthRegistry(), database


def test_source_uses_one_kernel_resolver_and_no_auth_tenant_fallbacks() -> None:
    import tools.eos.saas.auth.auth_registry as auth_module
    import tools.eos.saas.tenancy.tenant_registry as tenant_module

    auth_source = inspect.getsource(auth_module)
    tenant_source = inspect.getsource(tenant_module)
    assert "MongoClient(" not in auth_source
    assert "MongoClient(" not in tenant_source
    assert 'doc.get("tenantId", "GLOBAL_ROOT")' not in auth_source
    assert "resolve_canonical_tenant" in auth_source
    assert "resolve_canonical_tenant" in tenant_source


def test_alias_resolves_to_canonical_id_before_user_persistence(monkeypatch: pytest.MonkeyPatch) -> None:
    registry, database = _registry(monkeypatch)
    user = registry.register_user("alias@example.com", "ValidPassword!123", "Alias", "User", "USER", "wilsy")
    assert user.tenantId == "TENANT-CANONICAL"
    assert database["users"].documents[0]["tenantId"] == "TENANT-CANONICAL"


@pytest.mark.parametrize("reference", ["missing", "wilsy-sovereign-root", "MASTER", "GLOBAL_ROOT"])
def test_missing_and_pseudo_tenants_reject_user_without_persistence(monkeypatch: pytest.MonkeyPatch, reference: str) -> None:
    registry, database = _registry(monkeypatch)
    with pytest.raises(AuthRegistryTenantError):
        registry.register_user("blocked@example.test", "ValidPassword!123", "Blocked", "User", "USER", reference)
    assert database["users"].documents == []


def test_duplicate_tenant_id_fails_closed_before_user_persistence(monkeypatch: pytest.MonkeyPatch) -> None:
    registry, database = _registry(monkeypatch, [_tenant(), _tenant()])
    with pytest.raises(AuthRegistryTenantError):
        registry.register_user("duplicate@example.test", "ValidPassword!123", "Duplicate", "User", "USER", "TENANT-CANONICAL")
    assert database["users"].documents == []


def test_inactive_canonical_tenant_fails_closed_before_user_persistence(monkeypatch: pytest.MonkeyPatch) -> None:
    registry, database = _registry(monkeypatch, [_tenant(status="SUSPENDED")])
    with pytest.raises(AuthRegistryTenantError):
        registry.register_user("inactive@example.com", "ValidPassword!123", "Inactive", "User", "USER", "TENANT-CANONICAL")
    assert database["users"].documents == []


def test_bad_hydrated_user_fails_closed_without_pseudo_injection(monkeypatch: pytest.MonkeyPatch) -> None:
    registry, database = _registry(monkeypatch)
    database["users"].documents.append({"user_id": "bad-user", "email": "bad@example.com", "tenantId": "MASTER"})
    with pytest.raises(AuthRegistryTenantError):
        registry.get_user_by_email("bad@example.com")


def test_session_validates_tenant_before_jwt_session_or_refresh(monkeypatch: pytest.MonkeyPatch) -> None:
    registry, database = _registry(monkeypatch)
    invalid_user = User(
        id="invalid-user", email="invalid@example.com", firstName="Invalid", lastName="User",
        role="USER", permissions=[], tenantId="GLOBAL_ROOT", passwordHash="hash",
    )
    with pytest.raises(AuthRegistryTenantError):
        registry.create_session(invalid_user)
    assert database["sessions"].documents == []
    assert database["refresh_tokens"].documents == []


def test_valid_session_claim_is_canonical_and_refresh_rechecks_tenant(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_JWT_SECRET", "unit-canonical-signing-secret")
    registry, database = _registry(monkeypatch)
    user = registry.register_user("session@example.com", "ValidPassword!123", "Session", "User", "USER", "TENANT-CANONICAL")
    database["principal_authorities"].documents.append({"principal_id": user.id, "status": "ACTIVE", "revision": 0})
    session = registry.create_session(user)
    assert session.tenantId == "TENANT-CANONICAL"
    assert database["sessions"].documents[0]["tenant_id"] == "TENANT-CANONICAL"
    refresh = database["refresh_tokens"].documents[0]["token"]
    assert registry.validate_refresh_token(refresh) == user.id
    database["tenants"].documents.clear()
    assert registry.validate_refresh_token(refresh) is None


def test_tenant_create_rejects_reserved_pseudo_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    _, database = _registry(monkeypatch)
    result: dict[str, Any]
    # The production create seam has no alternate authority; exercise it through
    # the canonical test substitution slot without touching a real database.
    import tools.eos.saas.tenancy.tenant_registry as tenant_module

    tenant_module.tenants_collection = database["tenants"]
    try:
        result = TenantRegistry.create({"tenant_id": "MASTER", "name": "Invalid"})
    finally:
        tenant_module.tenants_collection = None
    assert result["success"] is False
    assert database["tenants"].documents == [_tenant()]


"""
ARTIFACT: tests/unit/test_canonical_tenant_source_of_truth.py
VERSION: v1.0.1-R1D-B0F-B3B-SIGNING-CONFIG-CERT
AUTHORITY BOUNDARY: deterministic canonical tenant identity evidence only
TENANT POSTURE: exact ACTIVE tenant_id required; aliases are resolved once before persistence
FAIL-CLOSED POSTURE: missing, duplicate, inactive, corrupt, or pseudo references issue no auth material
FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
END OF WILSY OS SOVEREIGN ARTIFACT
"""
