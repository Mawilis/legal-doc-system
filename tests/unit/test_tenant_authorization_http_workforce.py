
"""TITLE: WILSY OS Tenant Authorization HTTP Workforce Certificate
VERSION: v1.3.0-PLATFORM-ADMISSION-CURRENTNESS-HTTP-CERT
AUTHORITY: WILSY EOS unit-test authority; never grants tenant permissions.
EPITOME: Verify existing IAM decisions, exact-WILSY platform-employer pair
         selection, customer HR entitlement gates, and nonblocking persistence.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_tenant_authorization_http_workforce.py
COLLABORATION / OWNERSHIP: EOS tenant_authorization_http; frozen IAM composer.
CERTIFICATION / UPDATE DATE: 2026-11-11
CHANGELOG: 2026-11-13 v1.3.0-PLATFORM-ADMISSION-CURRENTNESS-HTTP-CERT verifies the
           admission capability selects the existing workforce transaction
           without customer HR entitlement, while preserving exact WILSY scope.
           v1.2.0-HR-ENTITLEMENT-PFE-SCOPE-CERT verifies the prior employer and customer HR pairs.
           2026-11-11 v1.1.0-EVENT-LOOP-RESPONSIVENESS-CERT retained workforce
           transaction and fail-closed denial/outage certification.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identities, no external credentials.
TENANT BOUNDARY: Assertions use synthetic customer scope or the exact canonical
                 WILSY employer identifier; no tenant records are mutated.
AUTHORITY BOUNDARY: Unit mocks verify existing IAM and D22B2 gates; no role,
                    membership, entitlement, or employee authority is created.
TRANSACTION / IDEMPOTENCY BOUNDARY: Fake sessions only; no durable writes.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
FAIL-CLOSED POSTURE: Errors remain rejected, not turned into granted work.
"""

from __future__ import annotations

from threading import get_ident
from types import SimpleNamespace
from typing import Any, cast

import pytest
from starlette.requests import Request

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

    def start_transaction(self, **options: object) -> _Transaction:
        del options
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
        named_collections: dict[str, object] | None = None,
    ) -> None:
        self.counters = counters
        self.collection = collection
        self.named_collections = dict(named_collections or {})
        self.collection_names: list[str] = []

    def __getitem__(
        self,
        name: str,
    ) -> object:
        self.counters["collection_lookup"] += 1
        assert name == "workforce_relationship_history"
        return self.collection

    def get_collection(self, name: str) -> object:
        self.collection_names.append(name)
        return self.named_collections.get(name, self.collection)


def _identity() -> SovereignIdentity:
    return cast(
        SovereignIdentity,
        SimpleNamespace(
            identity_id="principal-r8c",
            principal_scope="TENANT",
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
        request=Request({"type": "http"}),
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
async def test_blocking_iam_composer_runs_off_asgi_event_loop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Slow synchronous IAM must not execute on the async request loop."""
    request_loop_thread = get_ident()
    composer_threads: list[int] = []

    def compose(**kwargs: Any) -> TenantAuthorizationDecision:
        composer_threads.append(get_ident())
        return TenantAuthorizationDecision(
            True,
            TenantAuthorizationReason.AUTHORIZED,
            "tenant_auditor",
        )

    monkeypatch.setattr(subject, "authorize_tenant_operation", compose)
    principal, membership, roles = _repositories()
    result = await subject.RequireTenantAuthorization("audit:read", "audit_read")(
        request=Request({"type": "http"}),
        identity=_identity(),
        tenant_id="tenant-r8c",
        principal_repository=principal,
        membership_repository=membership,
        role_assignment_repository=roles,
    )
    assert result.decision.authorized is True
    assert composer_threads and composer_threads[0] != request_loop_thread


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
    # This certificate isolates the workforce transaction branch; customer HR
    # product admission is certified independently below.
    monkeypatch.setattr(
        subject,
        "_require_active_hr_product_entitlement",
        lambda tenant_id: None,
    )

    principal, membership, roles = _repositories()

    dependency = subject.RequireTenantAuthorization(
        "hr:employee_relation:write",
        "hr_employee_relation_write",
    )

    result = await dependency(
        request=Request({"type": "http"}),
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
            request=Request({"type": "http"}),
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
            request=Request({"type": "http"}),
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
            request=Request({"type": "http"}),
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
            request=Request({"type": "http"}),
            identity=_identity(),
            tenant_id="tenant-r8c",
            principal_repository=principal,
            membership_repository=membership,
            role_assignment_repository=roles,
        )


@pytest.mark.anyio
async def test_customer_hr_permission_requires_exact_active_product_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Customer hr: authorization is not sufficient without active D22B2 HR."""
    captured: dict[str, object] = {}
    entitlement_tenants: list[str] = []

    def compose(**kwargs: Any) -> TenantAuthorizationDecision:
        captured.update(kwargs)
        return TenantAuthorizationDecision(
            True, TenantAuthorizationReason.AUTHORIZED, "tenant_hr_manager"
        )

    monkeypatch.setattr(subject, "authorize_tenant_operation", compose)
    monkeypatch.setattr(
        subject,
        "_require_active_hr_product_entitlement",
        lambda tenant_id: entitlement_tenants.append(tenant_id),
    )
    principal, membership, roles = _repositories()
    dependency = subject.RequireTenantAuthorization(
        "hr:hiring_candidate:create", "hr_hiring_candidate_create"
    )

    result = await dependency(
        request=Request({"type": "http"}),
        identity=_identity(),
        tenant_id="CUSTOMER-HR-TENANT",
        principal_repository=principal,
        membership_repository=membership,
        role_assignment_repository=roles,
    )

    assert result.decision.authorized is True
    assert captured["permission_id"] == "hr:hiring_candidate:create"
    assert captured["operation"] == "hr_hiring_candidate_create"
    assert entitlement_tenants == ["CUSTOMER-HR-TENANT"]


@pytest.mark.anyio
async def test_canonical_wilsy_platform_employer_pair_bypasses_customer_hr_entitlement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Only exact canonical WILSY scope selects the separately governed pair."""
    from tools.eos.auth.workspace_bootstrap_projection import (
        WILSY_COMPANY_TENANT_ID,
    )

    captured: dict[str, object] = {}
    entitlement_calls: list[str] = []

    def compose(**kwargs: Any) -> TenantAuthorizationDecision:
        captured.update(kwargs)
        return TenantAuthorizationDecision(
            True, TenantAuthorizationReason.AUTHORIZED, "tenant_hr_manager"
        )

    monkeypatch.setattr(subject, "authorize_tenant_operation", compose)
    monkeypatch.setattr(
        subject,
        "_require_active_hr_product_entitlement",
        lambda tenant_id: entitlement_calls.append(tenant_id),
    )
    principal, membership, roles = _repositories()
    dependency = subject.RequireTenantAuthorization(
        "hr:hiring_candidate:create",
        "hr_hiring_candidate_create",
        platform_employer_permission_id=(
            "platform_employer:hiring_candidate:create"
        ),
        platform_employer_operation=(
            "platform_employer_hiring_candidate_create"
        ),
    )

    result = await dependency(
        request=Request({"type": "http"}),
        identity=_identity(),
        tenant_id=WILSY_COMPANY_TENANT_ID,
        principal_repository=principal,
        membership_repository=membership,
        role_assignment_repository=roles,
    )

    assert result.decision.authorized is True
    assert captured["tenant_id"] == WILSY_COMPANY_TENANT_ID
    assert captured["permission_id"] == "platform_employer:hiring_candidate:create"
    assert captured["operation"] == "platform_employer_hiring_candidate_create"
    assert entitlement_calls == []


@pytest.mark.anyio
async def test_platform_admission_uses_workforce_transaction_without_customer_hr_entitlement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The admission permission is currentness-gated but not product-gated."""
    from tools.eos.auth.workspace_bootstrap_projection import (
        WILSY_COMPANY_TENANT_ID,
    )

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
    database = _Database(counters, collection)
    captured: dict[str, object] = {}

    def get_client() -> _Client:
        counters["get_client"] += 1
        return client

    def get_database() -> _Database:
        counters["get_database"] += 1
        return database

    def compose(**kwargs: Any) -> TenantAuthorizationDecision:
        counters["composer"] += 1
        session = kwargs.get("session")
        assert isinstance(session, _Session)
        assert kwargs.get("workforce_relationship_collection") is collection
        captured.update(kwargs)
        return TenantAuthorizationDecision(
            True, TenantAuthorizationReason.AUTHORIZED, "tenant_hr_director"
        )

    monkeypatch.setattr(subject, "get_client", get_client)
    monkeypatch.setattr(subject, "get_database", get_database)
    monkeypatch.setattr(subject, "authorize_tenant_operation", compose)
    monkeypatch.setattr(
        subject,
        "_require_active_hr_product_entitlement",
        lambda _tenant_id: pytest.fail(
            "platform-employer admission cannot depend on customer HR subscription"
        ),
    )
    principal, membership, roles = _repositories()
    dependency = subject.RequireTenantAuthorization(
        "hr:employee_relation:write",
        "hr_employee_relation_write",
        platform_employer_permission_id=(
            "platform_employer:employee_admission:create"
        ),
        platform_employer_operation=(
            "platform_employer_employee_admission_create"
        ),
    )

    result = await dependency(
        request=Request({"type": "http"}),
        identity=_identity(),
        tenant_id=WILSY_COMPANY_TENANT_ID,
        principal_repository=principal,
        membership_repository=membership,
        role_assignment_repository=roles,
    )

    assert result.decision.authorized is True
    assert captured["tenant_id"] == WILSY_COMPANY_TENANT_ID
    assert captured["permission_id"] == "platform_employer:employee_admission:create"
    assert captured["operation"] == "platform_employer_employee_admission_create"
    assert isinstance(captured["session"], _Session)
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


def test_platform_employer_alternate_pair_must_be_complete() -> None:
    """A partial alternate pair cannot degrade to a caller-selected capability."""
    with pytest.raises(ValueError, match="supplied together"):
        subject.RequireTenantAuthorization(
            "hr:hiring_candidate:create",
            "hr_hiring_candidate_create",
            platform_employer_permission_id=(
                "platform_employer:hiring_candidate:create"
            ),
        )


def test_active_hr_product_entitlement_uses_exact_d22b2_tenant_product_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The active product check reads only the exact HR lineage in a snapshot."""
    from tools.eos.auth.workspace_bootstrap_projection import (
        WILSY_COMPANY_TENANT_ID,
    )
    from tools.eos.saas.domain.tenant_product_entitlement import (
        TenantProductEntitlementState,
    )
    from tools.eos.saas.entitlement.product_catalogue import TenantProductId
    from tools.eos.saas.entitlement.tenant_product_entitlement_composer import (
        derive_tenant_product_entitlement_id,
    )

    counters = {
        "start_session": 0,
        "session_enter": 0,
        "session_exit": 0,
        "start_transaction": 0,
        "transaction_enter": 0,
        "transaction_exit": 0,
    }
    history = object()
    current = object()
    database = _Database(
        counters,
        object(),
        {
            subject.PRODUCT_ENTITLEMENT_HISTORY_COLLECTION: history,
            subject.PRODUCT_ENTITLEMENT_CURRENT_COLLECTION: current,
        },
    )
    client = _Client(counters)
    observed: dict[str, object] = {}

    def read_current(
        tenant_id: str,
        entitlement_id: str,
        history_collection: object,
        current_collection: object,
        *,
        session: object,
    ) -> object:
        observed.update(
            tenant_id=tenant_id,
            entitlement_id=entitlement_id,
            history=history_collection,
            current=current_collection,
            session=session,
        )
        return SimpleNamespace(
            tenant_id=tenant_id,
            entitlement_id=entitlement_id,
            product_id=TenantProductId.HR,
            lifecycle_state=TenantProductEntitlementState.ACTIVE,
        )

    monkeypatch.setattr(subject, "get_client", lambda: client)
    monkeypatch.setattr(subject, "get_database", lambda: database)
    monkeypatch.setattr(
        subject, "get_current_product_entitlement", read_current
    )

    subject._require_active_hr_product_entitlement(WILSY_COMPANY_TENANT_ID)

    assert observed["tenant_id"] == WILSY_COMPANY_TENANT_ID
    assert observed["entitlement_id"] == derive_tenant_product_entitlement_id(
        WILSY_COMPANY_TENANT_ID, TenantProductId.HR
    )
    assert observed["history"] is history
    assert observed["current"] is current
    assert isinstance(observed["session"], _Session)
    assert database.collection_names == [
        subject.PRODUCT_ENTITLEMENT_HISTORY_COLLECTION,
        subject.PRODUCT_ENTITLEMENT_CURRENT_COLLECTION,
    ]
    assert counters == {
        "start_session": 1,
        "session_enter": 1,
        "session_exit": 1,
        "start_transaction": 1,
        "transaction_enter": 1,
        "transaction_exit": 1,
    }


def test_inactive_hr_entitlement_denies_and_d22b2_outage_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Terminal product state denies; corrupt or unavailable D22B2 remains 503."""
    from tools.eos.saas.domain.tenant_product_entitlement import (
        TenantProductEntitlementState,
    )
    from tools.eos.saas.entitlement.product_catalogue import TenantProductId

    class _NoopTransaction:
        def __enter__(self) -> "_NoopTransaction":
            return self

        def __exit__(
            self, exc_type: object, exc: object, traceback: object
        ) -> None:
            del exc_type, exc, traceback

    class _NoopSession:
        def __enter__(self) -> "_NoopSession":
            return self

        def __exit__(
            self, exc_type: object, exc: object, traceback: object
        ) -> None:
            del exc_type, exc, traceback

        def start_transaction(self, **kwargs: object) -> _NoopTransaction:
            del kwargs
            return _NoopTransaction()

    class _NoopClient:
        def start_session(self) -> _NoopSession:
            return _NoopSession()

    class _NoopDatabase:
        def get_collection(self, name: str) -> object:
            return name

    monkeypatch.setattr(subject, "get_client", _NoopClient)
    monkeypatch.setattr(subject, "get_database", _NoopDatabase)
    monkeypatch.setattr(
        subject,
        "derive_tenant_product_entitlement_id",
        lambda *_args: "tenant-product-id",
    )

    def inactive(*_args: object, **_kwargs: object) -> object:
        return SimpleNamespace(
            tenant_id="customer-hr-tenant",
            entitlement_id="tenant-product-id",
            product_id=TenantProductId.HR,
            lifecycle_state=TenantProductEntitlementState.SUSPENDED,
        )

    monkeypatch.setattr(subject, "get_current_product_entitlement", inactive)
    with pytest.raises(ForbiddenOperationException):
        subject._require_active_hr_product_entitlement("customer-hr-tenant")

    def unavailable(*_args: object, **_kwargs: object) -> object:
        raise subject.TenantProductEntitlementRegistryError(
            "D22B2_PERSISTENCE_UNAVAILABLE"
        )

    monkeypatch.setattr(subject, "get_current_product_entitlement", unavailable)
    with pytest.raises(WilsyAPIException) as error:
        subject._require_active_hr_product_entitlement("customer-hr-tenant")
    assert error.value.status_code == 503


# ARTIFACT: tests/unit/test_tenant_authorization_http_workforce.py
# VERSION: v1.3.0-PLATFORM-ADMISSION-CURRENTNESS-HTTP-CERT
# AUTHORITY BOUNDARY: Unit-only verification of existing IAM and D22B2 composition; no real permission grants or assignments
# TENANT POSTURE: Customer HR entitlement is exact-tenant and WILSY employer override is canonical-tenant-only
# FAIL-CLOSED POSTURE: Missing or inactive HR entitlement denies; D22B2 uncertainty remains unavailable
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
