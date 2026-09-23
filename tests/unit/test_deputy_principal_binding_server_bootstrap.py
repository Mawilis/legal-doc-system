"""Direct certificate for L8-6B binding-index server bootstrap.

TITLE: WILSY OS Deputy Principal Binding Index Bootstrap Certificate
VERSION: v1.0.0-L8-6B-DEPUTY-BINDING-INDEX-BOOTSTRAP-CERT
AUTHORITY: Direct ASGI-startup certification for binding schema readiness only.
EPITOME: Prove successful database startup ensures the immutable L8-6B binding
         indexes on the exact canonical collection, failed database bootstrap
         performs no index work, and startup never creates identity bindings.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_deputy_principal_binding_server_bootstrap.py
COLLABORATION / OWNERSHIP: Certificate for server startup composition only;
                            binding registry owns indexes/persistence and L8-6B
                            orchestration owns identity composition.
CERTIFICATION / UPDATE DATE: 2026-09-23
CHANGELOG: 2026-09-23 v1.0.0-L8-6B-DEPUTY-BINDING-INDEX-BOOTSTRAP-CERT
           establishes successful-connect index invocation, failed-connect
           no-op, exact collection ownership, no binding creation, and server
           production-version binding.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No user data or binding payload is created.
TENANT BOUNDARY: Startup creates only collection indexes, never tenant records.
AUTHORITY BOUNDARY: Schema readiness only; no IAM or identity truth creation.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS remains exclusive.
FAIL-CLOSED DECLARATION: Index-bootstrap failure propagates from startup rather
                         than representing binding persistence as ready.
"""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

import pytest

import tools.eos.api.server as server


VERSION = "v1.0.0-L8-6B-DEPUTY-BINDING-INDEX-BOOTSTRAP-CERT"


class FakeDatabase:
    """Return stable named collection markers through mapping access."""

    def __init__(self) -> None:
        self.requests: list[str] = []

    def __getitem__(self, name: str) -> object:
        self.requests.append(name)
        return SimpleNamespace(name=name)


def _start_database_handler() -> Any:
    """Resolve only the canonical DB startup callback from the mounted app."""
    matches = [
        handler
        for handler in server.app.router.on_startup
        if getattr(handler, "__name__", "") == "start_database"
    ]
    assert len(matches) == 1
    return matches[0]


def test_successful_database_bootstrap_ensures_exact_binding_indexes_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Connected startup ensures indexes on the canonical binding collection."""
    database = FakeDatabase()
    observed: list[object] = []
    creates: list[object] = []

    monkeypatch.setattr(server, "connect_db", lambda: (True, "connected"))
    monkeypatch.setattr(server, "get_database", lambda: database)
    monkeypatch.setattr(server, "get_client", lambda: None)
    monkeypatch.setattr(
        server.DeputyPrincipalBindingRegistry,
        "ensure_indexes",
        staticmethod(lambda collection: observed.append(collection)),
    )
    monkeypatch.setattr(
        server.DeputyPrincipalBindingRegistry,
        "create",
        staticmethod(lambda *args, **kwargs: creates.append((args, kwargs))),
    )

    asyncio.run(_start_database_handler()())

    assert database.requests == [server.DEPUTY_PRINCIPAL_BINDING_COLLECTION]
    assert len(observed) == 1
    assert getattr(observed[0], "name", None) == (
        server.DEPUTY_PRINCIPAL_BINDING_COLLECTION
    )
    assert creates == []


def test_failed_database_bootstrap_does_not_touch_binding_indexes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Unavailable DB bootstrap returns without claiming schema readiness."""
    database_reads: list[str] = []
    index_calls: list[object] = []

    monkeypatch.setattr(server, "connect_db", lambda: (False, "unavailable"))
    monkeypatch.setattr(
        server,
        "get_database",
        lambda: database_reads.append("database") or FakeDatabase(),
    )
    monkeypatch.setattr(
        server.DeputyPrincipalBindingRegistry,
        "ensure_indexes",
        staticmethod(lambda collection: index_calls.append(collection)),
    )

    asyncio.run(_start_database_handler()())

    assert database_reads == []
    assert index_calls == []


def test_index_bootstrap_failure_propagates_fail_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Index failure is not swallowed as a successfully ready server authority."""
    database = FakeDatabase()

    monkeypatch.setattr(server, "connect_db", lambda: (True, "connected"))
    monkeypatch.setattr(server, "get_database", lambda: database)
    monkeypatch.setattr(server, "get_client", lambda: None)

    def reject(_collection: object) -> None:
        raise RuntimeError("synthetic index failure")

    monkeypatch.setattr(
        server.DeputyPrincipalBindingRegistry,
        "ensure_indexes",
        staticmethod(reject),
    )

    with pytest.raises(RuntimeError, match="synthetic index failure"):
        asyncio.run(_start_database_handler()())


def test_server_version_is_exact_l8_6b_bootstrap_release() -> None:
    """Certificate remains bound to the intended production startup release."""
    assert server.VERSION == "v1.18.0-L8-6B-DEPUTY-BINDING-INDEX-BOOTSTRAP"
    assert VERSION == "v1.0.0-L8-6B-DEPUTY-BINDING-INDEX-BOOTSTRAP-CERT"


# ARTIFACT: test_deputy_principal_binding_server_bootstrap.py
# VERSION: v1.0.0-L8-6B-DEPUTY-BINDING-INDEX-BOOTSTRAP-CERT
# AUTHORITY BOUNDARY: direct server startup binding-index readiness certificate only
# TENANT POSTURE: startup creates indexes only and no tenant binding records
# FAIL-CLOSED POSTURE: DB/index bootstrap failure never masquerades as ready
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
