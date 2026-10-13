
"""W3D-R8C direct conditional HTTP workforce authorization certificate."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pytest

from tools.eos.api import tenant_authorization_http as subject
from tools.eos.api.exceptions import (
    ForbiddenOperationException,
    WilsyAPIException,
)
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationDecision,
    TenantAuthorizationReason,
)


class _Repositories:
    pass


class _Transaction:
    def __init__(
        self,
        counters: dict[str, int],
    ) -> None:
        self.counters = counters

    def __enter__(self) -> "_Transaction":
        self.counters["transaction_enter"] += 1
        return self

    def __exit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> None:
        del exc_type, exc, traceback
        self.counters["transaction_exit"] += 1


class _Session:
    def __init__(
        self,
        counters: dict[str, int],
    ) -> None:
        self.counters = counters

    def __enter__(self) -> "_Session":
        self.counters["session_enter"] += 1
        return self

    def __exit__(
        self,
        exc_type: object,
        exc: object,
        traceback: object,
    ) -> None:
        del exc_type, exc, traceback
        self.counters["session_exit"] += 1

    def start_transaction(self) -> _Transaction:
        self.counters["start_transaction"] += 1
        return _Transaction(self.counters)


class _Client:
    def __init__(
        self,
        counters: dict[str, int],
    ) -> None:
        self.counters = counters

    def start_session(self) -> _Session:
        self.counters["start_session"] += 1
        return _Session(self.counters)


class _Database:
    def __init__(
        self,
        counters: dict[str, int],
        collection: object,
    ) -> None:
        self.counters = counters
        self.collection = collection

    def __getitem__(
        self,
        name: str,
    ) -> object:
        self.counters["collection_lookup"] += 1
        assert name == "workforce_relationship_history"
        return self.collection


def _identity() -> SovereignIdentity:
    return cast(
        SovereignIdentity,
        SimpleNamespace(
            identity_id="principal-r8c",
        ),
    )


def _repositories() -> tuple[
    object,
    object,
    object,
]:
    return (
        _Repositories(),
        _Repositories(),
        _Repositories(),
    )


@pytest.mark.anyio
async def test_non_workforce_permission_opens_no_database_or_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = {
        "client": 0,
        "database": 0,
        "composer": 0,
    }

    def forbidden_client() -> object:
        calls["client"] += 1
        raise AssertionError(
            "non-workforce authorization must not request Mongo client"
        )

    def forbidden_database() -> object:
        calls["database"] += 1
        raise AssertionError(
            "non-workforce authorization must not request database"
        )

    def compose(**kwargs: Any) -> TenantAuthorizationDecision:
        calls["composer"] += 1
        assert "session" not in kwargs
        assert "workforce_relationship_collection" not in kwargs

        return TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
            "tenant_auditor",
        )

    monkeypatch.setattr(
        subject,
        "get_client",
        forbidden_client,
    )
    monkeypatch.setattr(
        subject,
        "get_database",
        forbidden_database,
    )
    monkeypatch.setattr(
        subject,
        "authorize_tenant_operation",
        compose,
    )

    principal, membership, roles = _repositories()

    dependency = subject.RequireTenantAuthorization(
        "audit:read",
        "audit_read",
    )

    result = await dependency(
        identity=_identity(),
        tenant_id="tenant-r8c",
        principal_repository=principal,
        membership_repository=membership,
        role_assignment_repository=roles,
    )

    assert result.decision.authorized is True
    assert calls == {
        "client": 0,
        "database": 0,
        "composer": 1,
    }


@pytest.mark.anyio
async def test_workforce_permission_uses_one_session_one_transaction_and_same_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    counters = {
        "get_client": 0,
        "get_database": 0,
        "start_session": 0,
        "session_enter": 0,
        "session_exit": 0,
        "start_transaction": 0,
        "transaction_enter": 0,
        "transaction_exit": 0,
        "collection_lookup": 0,
        "composer": 0,
    }

    collection = object()
    client = _Client(counters)
    database = _Database(
        counters,
        collection,
    )

    def get_client() -> _Client:
        counters["get_client"] += 1
        return client

    def get_database() -> _Database:
        counters["get_database"] += 1
        return database

    captured_session: list[object] = []

    def compose(**kwargs: Any) -> TenantAuthorizationDecision:
        counters["composer"] += 1

        session = kwargs.get("session")

        assert isinstance(
            session,
            _Session,
        )
        assert (
            kwargs.get(
                "workforce_relationship_collection"
            )
            is collection
        )

        captured_session.append(session)

        return TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
            "tenant_hr_director",
        )

    monkeypatch.setattr(
        subject,
        "get_client",
        get_client,
    )
    monkeypatch.setattr(
        subject,
        "get_database",
        get_database,
    )
    monkeypatch.setattr(
        subject,
        "authorize_tenant_operation",
        compose,
    )

    principal, membership, roles = _repositories()

    dependency = subject.RequireTenantAuthorization(
        "hr:employee_relation:write",
        "hr_employee_relation_write",
    )

    result = await dependency(
        identity=_identity(),
        tenant_id="tenant-r8c",
        principal_repository=principal,
        membership_repository=membership,
        role_assignment_repository=roles,
    )

    assert result.decision.authorized is True
    assert len(captured_session) == 1

    assert counters == {
        "get_client": 1,
        "get_database": 1,
        "start_session": 1,
        "session_enter": 1,
        "session_exit": 1,
        "start_transaction": 1,
        "transaction_enter": 1,
        "transaction_exit": 1,
        "collection_lookup": 1,
        "composer": 1,
    }


@pytest.mark.anyio
async def test_workforce_not_current_maps_to_forbidden(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    counters: dict[str, int] = {
        "start_session": 0,
        "session_enter": 0,
        "session_exit": 0,
        "start_transaction": 0,
        "transaction_enter": 0,
        "transaction_exit": 0,
        "collection_lookup": 0,
    }

    monkeypatch.setattr(
        subject,
        "get_client",
        lambda: _Client(counters),
    )
    monkeypatch.setattr(
        subject,
        "get_database",
        lambda: _Database(
            counters,
            object(),
        ),
    )
    monkeypatch.setattr(
        subject,
        "authorize_tenant_operation",
        lambda **kwargs: TenantAuthorizationDecision(
            False,
            TenantAuthorizationReason.WORKFORCE_NOT_CURRENT,
            "tenant_hr_director",
        ),
    )

    principal, membership, roles = _repositories()

    dependency = subject.RequireTenantAuthorization(
        "hr:employee_relation:write",
        "hr_employee_relation_write",
    )

    with pytest.raises(
        ForbiddenOperationException
    ):
        await dependency(
            identity=_identity(),
            tenant_id="tenant-r8c",
            principal_repository=principal,
            membership_repository=membership,
            role_assignment_repository=roles,
        )


@pytest.mark.anyio
async def test_workforce_authority_unavailable_maps_to_503(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    counters: dict[str, int] = {
        "start_session": 0,
        "session_enter": 0,
        "session_exit": 0,
        "start_transaction": 0,
        "transaction_enter": 0,
        "transaction_exit": 0,
        "collection_lookup": 0,
    }

    monkeypatch.setattr(
        subject,
        "get_client",
        lambda: _Client(counters),
    )
    monkeypatch.setattr(
        subject,
        "get_database",
        lambda: _Database(
            counters,
            object(),
        ),
    )
    monkeypatch.setattr(
        subject,
        "authorize_tenant_operation",
        lambda **kwargs: TenantAuthorizationDecision(
            False,
            TenantAuthorizationReason.WORKFORCE_AUTHORITY_UNAVAILABLE,
            "tenant_hr_director",
        ),
    )

    principal, membership, roles = _repositories()

    dependency = subject.RequireTenantAuthorization(
        "hr:employee_relation:write",
        "hr_employee_relation_write",
    )

    with pytest.raises(
        WilsyAPIException
    ) as captured:
        await dependency(
            identity=_identity(),
            tenant_id="tenant-r8c",
            principal_repository=principal,
            membership_repository=membership,
            role_assignment_repository=roles,
        )

    assert captured.value.status_code == 503


@pytest.mark.anyio
async def test_missing_kernel_database_fails_workforce_path_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    composer_calls = 0

    def compose(**kwargs: Any) -> TenantAuthorizationDecision:
        nonlocal composer_calls
        composer_calls += 1
        raise AssertionError(
            "composer must not run without kernel database"
        )

    monkeypatch.setattr(
        subject,
        "get_client",
        lambda: object(),
    )
    monkeypatch.setattr(
        subject,
        "get_database",
        lambda: None,
    )
    monkeypatch.setattr(
        subject,
        "authorize_tenant_operation",
        compose,
    )

    principal, membership, roles = _repositories()

    dependency = subject.RequireTenantAuthorization(
        "hr:employee_relation:write",
        "hr_employee_relation_write",
    )

    with pytest.raises(
        WilsyAPIException
    ) as captured:
        await dependency(
            identity=_identity(),
            tenant_id="tenant-r8c",
            principal_repository=principal,
            membership_repository=membership,
            role_assignment_repository=roles,
        )

    assert captured.value.status_code == 503
    assert composer_calls == 0


@pytest.mark.anyio
async def test_unknown_permission_preserves_existing_composer_semantics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def forbidden_client() -> object:
        raise AssertionError(
            "unknown permission must not manufacture workforce classification"
        )

    def forbidden_database() -> object:
        raise AssertionError(
            "unknown permission must not open workforce persistence"
        )

    monkeypatch.setattr(
        subject,
        "get_client",
        forbidden_client,
    )
    monkeypatch.setattr(
        subject,
        "get_database",
        forbidden_database,
    )
    monkeypatch.setattr(
        subject,
        "authorize_tenant_operation",
        lambda **kwargs: TenantAuthorizationDecision(
            False,
            TenantAuthorizationReason.PERMISSION_UNKNOWN,
            None,
        ),
    )

    principal, membership, roles = _repositories()

    dependency = subject.RequireTenantAuthorization(
        "unknown:permission",
        "unknown_operation",
    )

    with pytest.raises(
        ForbiddenOperationException
    ):
        await dependency(
            identity=_identity(),
            tenant_id="tenant-r8c",
            principal_repository=principal,
            membership_repository=membership,
            role_assignment_repository=roles,
        )
