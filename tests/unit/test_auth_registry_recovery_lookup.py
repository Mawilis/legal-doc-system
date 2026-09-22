"""WILSY OS tenant-scoped recovery principal lookup direct certificate.

TITLE: AuthRegistry Recovery Principal Lookup Direct Unit Certificate
VERSION: v1.0.0-R10E1-AUTH-REGISTRY-RECOVERY-LOOKUP-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies exact canonical-tenant + normalized-email resolution for
         password-recovery initiation without credential or tenant authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_auth_registry_recovery_lookup.py
COLLABORATION / OWNERSHIP: Test-only evidence for AuthRegistry; recovery
                           issuance, delivery, HTTP, and reset consumption are
                           outside this certificate.
CERTIFICATION / UPDATE DATE: 2026-09-22
CHANGELOG:
  v1.0.0-R10E1-AUTH-REGISTRY-RECOVERY-LOOKUP-CERT — Adds deterministic coverage for canonical tenant scoping,
    login-email normalization, scoped absence, cross-tenant isolation,
    ambiguous duplicate rejection, caller-session propagation, strict user
    hydration, principal-id-only output, and non-ownership of mutations,
    transactions, recovery capability issuance, or delivery.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Synthetic identity data only; password hashes are
                            sentinel values and are never returned by the API.
TENANT BOUNDARY: Every successful lookup requires one canonical tenant_id and
                 exact durable tenantId + normalized email predicate.
AUTHORITY BOUNDARY: Read-only recovery candidate resolution only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusively financial.
"""

from __future__ import annotations

import ast
import inspect
from datetime import datetime
from types import SimpleNamespace
from typing import Any, cast

import pytest
from bson import ObjectId

from tools.eos.saas.auth import auth_registry as auth_registry_module
from tools.eos.saas.auth.auth_registry import AuthRegistry, AuthRegistryTenantError


class _Cursor:
    def __init__(self, documents: list[dict[str, Any]]) -> None:
        self.documents = [dict(document) for document in documents]
        self.limit_value: int | None = None

    def limit(self, value: int) -> "_Cursor":
        self.limit_value = value
        return self

    def __iter__(self):
        documents = self.documents if self.limit_value is None else self.documents[: self.limit_value]
        return iter([dict(document) for document in documents])


class _RecordingCollection:
    def __init__(self, documents: list[dict[str, Any]] | None = None) -> None:
        self.documents = [dict(document) for document in (documents or [])]
        self.calls: list[dict[str, Any]] = []

    @staticmethod
    def _matches(document: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(document.get(key) == expected for key, expected in query.items())

    def find(self, query: dict[str, Any], **kwargs: Any) -> _Cursor:
        self.calls.append({"operation": "find", "query": dict(query), "kwargs": dict(kwargs)})
        return _Cursor([document for document in self.documents if self._matches(document, query)])

    def insert_one(self, *_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("recovery lookup must not write")

    def update_one(self, *_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("recovery lookup must not write")

    def delete_many(self, *_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("recovery lookup must not write")


class _RecordingDatabase:
    def __init__(self, users: list[dict[str, Any]]) -> None:
        self.collections = {"users": _RecordingCollection(users)}

    def __getitem__(self, name: str) -> _RecordingCollection:
        if name not in self.collections:
            self.collections[name] = _RecordingCollection()
        return self.collections[name]


class _TenantRegistry:
    calls: list[tuple[object, bool]] = []

    @classmethod
    def resolve_canonical_tenant(cls, value: object, allow_alias: bool = False) -> SimpleNamespace:
        cls.calls.append((value, allow_alias))
        if value not in {"TENANT-ONE", "TENANT-TWO"}:
            raise ValueError("tenant is not canonical")
        return SimpleNamespace(tenant_id=value)


class _Session:
    def __init__(self) -> None:
        self.start_calls = 0
        self.commit_calls = 0
        self.abort_calls = 0


def _user_document(**overrides: Any) -> dict[str, Any]:
    document: dict[str, Any] = {
        "_id": ObjectId("507f1f77bcf86cd799439011"),
        "user_id": "principal-1",
        "email": "person@example.com",
        "firstName": "Synthetic",
        "lastName": "Principal",
        "role": "USER",
        "permissions": ["legal:read"],
        "tenantId": "TENANT-ONE",
        "passwordHash": "bcrypt-secret-sentinel",
        "credential_revision": 4,
        "mfaRegistered": True,
        "hasSignedCovenant": False,
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
    }
    document.update(overrides)
    return document


def _registry(monkeypatch: pytest.MonkeyPatch, users: list[dict[str, Any]]) -> tuple[AuthRegistry, _RecordingDatabase]:
    database = _RecordingDatabase(users)
    monkeypatch.setattr(auth_registry_module.kernel_db, "get_database", lambda: database)
    _TenantRegistry.calls = []
    return AuthRegistry(cast(Any, _TenantRegistry)), database


def test_public_signature_and_production_version() -> None:
    assert auth_registry_module.VERSION == "v1.10.0-R10E1-TENANT-EMAIL-RECOVERY-LOOKUP"
    signature = inspect.signature(AuthRegistry.resolve_principal_id_by_email_for_tenant)
    assert list(signature.parameters) == ["self", "tenant_id", "email", "session"]
    assert signature.parameters["session"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["session"].default is None


def test_exact_tenant_email_lookup_normalizes_email_and_forwards_session(monkeypatch: pytest.MonkeyPatch) -> None:
    registry, database = _registry(monkeypatch, [_user_document()])
    session = _Session()
    principal_id = registry.resolve_principal_id_by_email_for_tenant(
        "TENANT-ONE", "  PERSON@EXAMPLE.COM  ", session=session
    )
    assert principal_id == "principal-1"
    assert _TenantRegistry.calls == [("TENANT-ONE", False), ("TENANT-ONE", False)]
    calls = database.collections["users"].calls
    assert calls == [{
        "operation": "find",
        "query": {"tenantId": "TENANT-ONE", "email": "person@example.com"},
        "kwargs": {"session": session},
    }]
    assert session.start_calls == session.commit_calls == session.abort_calls == 0


def test_scoped_absence_and_cross_tenant_identity_return_no_principal(monkeypatch: pytest.MonkeyPatch) -> None:
    registry, _database = _registry(monkeypatch, [_user_document(tenantId="TENANT-TWO")])
    assert registry.resolve_principal_id_by_email_for_tenant("TENANT-ONE", "person@example.com") is None


def test_ambiguous_duplicate_rows_fail_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    registry, _database = _registry(monkeypatch, [
        _user_document(),
        _user_document(_id=ObjectId("507f1f77bcf86cd799439012"), user_id="principal-2"),
    ])
    with pytest.raises(AuthRegistryTenantError) as error:
        registry.resolve_principal_id_by_email_for_tenant("TENANT-ONE", "person@example.com")
    assert str(error.value) == "AUTH_RECOVERY_PRINCIPAL_AMBIGUOUS"


@pytest.mark.parametrize("email", ["", "   ", "x" * 321, None, 7])
def test_invalid_email_shape_fails_before_user_read(monkeypatch: pytest.MonkeyPatch, email: object) -> None:
    registry, database = _registry(monkeypatch, [_user_document()])
    with pytest.raises(AuthRegistryTenantError):
        registry.resolve_principal_id_by_email_for_tenant("TENANT-ONE", cast(Any, email))
    assert database.collections["users"].calls == []


def test_noncanonical_tenant_fails_before_user_read(monkeypatch: pytest.MonkeyPatch) -> None:
    registry, database = _registry(monkeypatch, [_user_document()])
    with pytest.raises(AuthRegistryTenantError):
        registry.resolve_principal_id_by_email_for_tenant("wilsy-alias", "person@example.com")
    assert database.collections["users"].calls == []


def test_corrupt_matching_user_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    document = _user_document()
    document["credential_revision"] = "corrupt"
    registry, _database = _registry(monkeypatch, [document])
    with pytest.raises(AuthRegistryTenantError) as error:
        registry.resolve_principal_id_by_email_for_tenant("TENANT-ONE", "person@example.com")
    assert str(error.value) == "AUTH_RECOVERY_PRINCIPAL_INVALID"


def test_lookup_returns_only_principal_identifier_not_credential_material(monkeypatch: pytest.MonkeyPatch) -> None:
    registry, _database = _registry(monkeypatch, [_user_document()])
    result = registry.resolve_principal_id_by_email_for_tenant("TENANT-ONE", "person@example.com")
    assert result == "principal-1"
    assert isinstance(result, str)
    assert "bcrypt" not in result
    assert "legal:read" not in result


def test_lookup_source_owns_no_mutation_transaction_or_recovery_issuance() -> None:
    source = inspect.getsource(AuthRegistry.resolve_principal_id_by_email_for_tenant)
    tree = ast.parse(source)
    called = {
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
    }
    assert not called.intersection({
        "insert_one", "update_one", "delete_one", "delete_many",
        "start_session", "start_transaction", "commit_transaction", "abort_transaction",
        "issue", "create_session", "generate_jwt", "generate_access_jwt",
    })
    assert "passwordHash" not in source
    assert "PasswordRecoveryCapability" not in source


# ARTIFACT: tests/unit/test_auth_registry_recovery_lookup.py
# VERSION: v1.0.0-R10E1-AUTH-REGISTRY-RECOVERY-LOOKUP-CERT
# AUTHORITY BOUNDARY: exact tenant/email recovery candidate lookup evidence only
# TENANT POSTURE: canonical tenant + normalized email; scoped absence does not disclose other tenants
# FAIL-CLOSED POSTURE: invalid, ambiguous, corrupt, or unavailable identity cannot become a recovery principal
# FINANCIAL EXECUTION AUTHORITY: None; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
