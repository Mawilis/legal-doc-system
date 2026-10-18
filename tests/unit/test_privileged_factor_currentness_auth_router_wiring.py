"""TITLE: Privileged Factor Currentness Authentication Router Wiring Tests.
VERSION: v1.0.0-P3-R3G-S5-A1-R7-AUTH-ROUTE-BINDING
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Certifies atomic factor-currentness persistence and exact production
FastAPI endpoint identity without creating authentication or role authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_privileged_factor_currentness_auth_router_wiring.py
COLLABORATION / OWNERSHIP: Authentication router and canonical API composition tests.
CERTIFICATION/UPDATE DATE: 2026-10-14.
CHANGELOG:
  v1.0.0-P3-R3G-S5-A1-R7-AUTH-ROUTE-BINDING: Adds production-derived route-object
  identity and effective path/method collision certification for validate-MFA,
  verify-OTP, verify-3FA, and the non-HTTP factor-currentness helper.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY/PRIVACY POSTURE: Uses synthetic identities and exposes no bearer secret.
TENANT BOUNDARY: Atomicity assertions remain exact-tenant and synthetic.
AUTHORITY BOUNDARY: Tests observe routing and persistence; they grant no authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
from fastapi.routing import APIRoute

from tools.eos.api import auth_router
from tools.eos.api.server import WilsyAPIServer
from tools.eos.auth.privileged_factor_verification_currentness_registry import (
    COLLECTION,
)
from tools.eos.kernel import db as kernel_db


class Result:
    inserted_id = "factor"


class Collection:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def create_index(
        self,
        _keys: object,
        **_kwargs: object,
    ) -> str:
        return "index"

    def find_one(
        self,
        query: dict[str, object],
        *,
        session: object = None,
    ) -> dict[str, object] | None:
        del session

        for row in self.rows:
            if all(
                row.get(k) == v
                for k, v
                in query.items()
            ):
                return dict(row)

        return None

    def insert_one(
        self,
        row: dict[str, object],
        *,
        session: object = None,
    ) -> Result:
        assert session is not None
        self.rows.append(
            dict(row)
        )
        return Result()


class Database:
    def __init__(self) -> None:
        self.collections: dict[
            str,
            Collection,
        ] = {}

    def __getitem__(
        self,
        name: str,
    ) -> Collection:
        return self.collections.setdefault(
            name,
            Collection(),
        )


class Session:
    def __init__(self) -> None:
        self.in_transaction = False
        self.events: list[str] = []

    def start_transaction(self) -> None:
        self.events.append("start")
        self.in_transaction = True

    def commit_transaction(self) -> None:
        self.events.append("commit")
        self.in_transaction = False

    def abort_transaction(self) -> None:
        self.events.append("abort")
        self.in_transaction = False

    def end_session(self) -> None:
        self.events.append("end")


class Client:
    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def start_session(self) -> Session:
        return self.session


class Registry:
    def __init__(
        self,
        *,
        fail_session: bool = False,
        fail_revision: bool = False,
    ) -> None:
        self.fail_session = fail_session
        self.fail_revision = fail_revision

    def create_session(
        self,
        _user: Any,
        *,
        session: object = None,
    ) -> Any:
        assert session is not None

        if self.fail_session:
            raise RuntimeError(
                "session-failure"
            )

        return SimpleNamespace(
            token="opaque-bearer",
            sessionReference="WILSYSESSION-test",
        )

    def get_credential_revision(
        self,
        tenant_id: str,
        principal_id: str,
        *,
        session: object = None,
    ) -> int:
        assert tenant_id == "tenant-a"
        assert principal_id == "principal-a"
        assert session is not None

        if self.fail_revision:
            raise RuntimeError(
                "revision-failure"
            )

        return 7


USER = SimpleNamespace(
    id="principal-a",
    tenantId="tenant-a",
)


def install(
    monkeypatch: pytest.MonkeyPatch,
    registry: Registry | None = None,
) -> tuple[
    Registry,
    Database,
    Session,
]:
    database = Database()
    session = Session()
    client = Client(session)
    active = registry or Registry()

    monkeypatch.setattr(
        kernel_db,
        "get_database",
        lambda: database,
    )

    monkeypatch.setattr(
        kernel_db,
        "get_client",
        lambda: client,
    )

    return active, database, session


def test_success_is_atomic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry, database, session = install(
        monkeypatch
    )

    result = (
        auth_router
        ._create_factor_current_session(
            registry,
            USER,
        )
    )

    assert result.token == "opaque-bearer"

    assert session.events == [
        "start",
        "commit",
        "end",
    ]

    rows = database[
        COLLECTION
    ].rows

    assert len(rows) == 1

    row = rows[0]

    assert row["principal_id"] == "principal-a"
    assert row["session_reference"] == "WILSYSESSION-test"
    assert row["credential_revision"] == 7
    assert row["status"] == "VERIFIED"

    assert isinstance(
        row["authenticated_at"],
        datetime,
    )

    assert str(
        row[
            "factor_verification_reference"
        ]
    ).startswith(
        "WILSYFACTOR-"
    )

    assert (
        row[
            "factor_verification_reference"
        ]
        != result.token
    )


@pytest.mark.parametrize(
    "failure",
    [
        "session",
        "revision",
    ],
)
def test_failure_aborts(
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    registry = Registry(
        fail_session=(
            failure == "session"
        ),
        fail_revision=(
            failure == "revision"
        ),
    )

    (
        _registry,
        database,
        session,
    ) = install(
        monkeypatch,
        registry,
    )

    with pytest.raises(RuntimeError):
        (
            auth_router
            ._create_factor_current_session(
                registry,
                USER,
            )
        )

    assert session.events == [
        "start",
        "abort",
        "end",
    ]

    assert database[
        COLLECTION
    ].rows == []


def test_source_has_no_forbidden_authority() -> None:
    path = auth_router.__file__
    assert path is not None

    source = Path(path).read_text(
        encoding="utf-8"
    )

    helper = source[
        source.index(
            "def _create_factor_current_session"
        ):
        source.index(
            "async def validate_mfa_setup"
        )
    ]

    for forbidden in (
        "MongoClient(",
        "create_otp_secret",
        "SUPER_ADMIN",
        "privileged_activation",
        "financial_execution",
    ):
        assert forbidden not in helper


def test_factor_helper_is_not_an_http_endpoint() -> None:
    """Certify production-derived effective paths and exact endpoint identities."""
    server = WilsyAPIServer(
        reasoning_provider_binding=object(),
    )

    auth_mounts = [
        route
        for route in server.app.routes
        if (
            type(route).__name__ == "_IncludedRouter"
            and getattr(route, "original_router", None)
            is auth_router.router
        )
    ]
    assert len(auth_mounts) == 1

    mount = cast(Any, auth_mounts[0])
    mount_prefix = mount.include_context.prefix
    assert mount_prefix == "/api"

    effective_routes = [
        (
            f"{mount_prefix}{route.path}",
            method,
            route.endpoint,
        )
        for route in auth_router.router.routes
        if isinstance(route, APIRoute)
        for method in (route.methods or set())
    ]

    assert not any(
        endpoint
        is auth_router._create_factor_current_session
        for _path, _method, endpoint in effective_routes
    )

    expected = {
        (
            "/api/auth/validate-mfa-setup",
            "POST",
        ): auth_router.validate_mfa_setup,
        (
            "/api/auth/verify-otp",
            "POST",
        ): auth_router.verify_otp,
        (
            "/api/auth/verify-3fa",
            "POST",
        ): auth_router.verify_otp,
    }
    route_bindings = {
        (path, method): endpoint
        for path, method, endpoint in effective_routes
        if (path, method) in expected
    }
    assert route_bindings == expected

    path_method_counts = Counter(
        (path, method)
        for path, method, _endpoint in effective_routes
    )
    assert all(
        count == 1
        for count in path_method_counts.values()
    )


# ARTIFACT: test_privileged_factor_currentness_auth_router_wiring.py
# VERSION: v1.0.0-P3-R3G-S5-A1-R7-AUTH-ROUTE-BINDING
# AUTHORITY BOUNDARY: Test observation only; no authentication, role, Legal, billing, or financial authority.
# TENANT POSTURE: Synthetic exact-tenant evidence only; no cross-tenant disclosure.
# FAIL-CLOSED POSTURE: Missing, duplicate, or identity-mismatched routes fail certification.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
