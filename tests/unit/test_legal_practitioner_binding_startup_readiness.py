"""WILSY OS P12C-R4L fail-closed practitioner-binding startup certificate.

VERSION: v1.4.1-P12C-R4N-STARTUP-INDEX-DOUBLE-CERT
AUTHORITY: Canonical EOS startup lifecycle and P12C binding readiness.
TEST POSTURE: No live database, service startup, index DDL or IAM grant.
BOUNDARY: A failed database bootstrap cannot complete startup normally.
PRIVACY: No tenant, matter, credential or protected system data.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_legal_practitioner_binding_startup_readiness.py
COLLABORATION / OWNERSHIP: Exercises the canonical EOS startup lifecycle and
                           practitioner-binding readiness gate.
CERTIFICATION / UPDATE DATE: 2026-11-11
CHANGELOG: v1.4.1-P12C-R4N-STARTUP-INDEX-DOUBLE-CERT records the verified sovereign metadata correction; test and production behavior are unchanged.
           v1.4.0-P12C-R4N-STARTUP-INDEX-DOUBLE-CERT gives the startup test
           database doubles the collection index and database relationships
           consumed by the actual EOS startup path.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic Mongo interface doubles only.
TENANT POSTURE: No tenant records are read or written.
AUTHORITY BOUNDARY: Startup readiness does not create IAM roles or permissions.
FINANCIAL AUTHORITY: Kennel EOS exclusively.
TITLE: WILSY OS Practitioner Binding Startup Readiness Certificate
EPITOME: Certify the canonical EOS startup readiness gate without creating identity, tenant, database, or IAM authority.
"""

from __future__ import annotations

import asyncio

import pytest

from tools.eos.api import server


def test_binding_index_readiness_initially_false():
    """Binding commands must not inherit ready state at composition."""
    assert (
        getattr(server.app.state, "p12c_binding_indexes_ready", None)
        is False
    )


def test_failed_database_bootstrap_aborts_startup(monkeypatch):
    """No normal startup completion after a failed database connection."""
    calls = []

    def disconnected():
        calls.append("connect_db")
        return False, "P12C_TEST_DISCONNECTED"

    monkeypatch.setattr(server, "connect_db", disconnected)

    handlers = [
        handler
        for handler in server.app.router.on_startup
        if handler.__name__ == "start_database"
    ]
    assert len(handlers) == 1

    asyncio.run(handlers[0]())

    assert calls == ["connect_db"]
    assert (
        getattr(server.app.state, "p12c_binding_indexes_ready", None)
        is False
    )



@pytest.mark.parametrize(
    "endpoint,payload",
    [
        (
            "/api/legal-operations/practitioner-bindings",
            {
                "case_matter_id": "matter-A",
                "practitioner_principal_id": "lawyer-A",
                "binding_id": "binding-A",
                "access_evidence_id": "evidence-A",
                "expected_access_evidence_fingerprint": "a" * 128,
            },
        ),
        (
            "/api/legal-operations/practitioner-bindings/revocations",
            {
                "binding_id": "binding-A",
                "evidence_reference": "revocation-A",
            },
        ),
    ],
)
def test_binding_command_requires_completed_index_startup(
    monkeypatch, endpoint, payload
):
    """An admitted request cannot enter a transaction before index readiness."""
    from types import SimpleNamespace
    from fastapi.testclient import TestClient
    from tools.eos.api import (
        legal_practitioner_matter_binding_router as binding_api,
    )

    def forbidden_transaction(callback):
        raise AssertionError("TRANSACTION_STARTED_BEFORE_INDEX_READINESS")

    monkeypatch.setattr(
        binding_api, "_transaction", forbidden_transaction
    )

    server.app.state.p12c_binding_indexes_ready = False

    server.app.dependency_overrides[binding_api._PROVISION] = (
        lambda: SimpleNamespace(
            tenant_id="tenant-A",
            identity=SimpleNamespace(identity_id="partner-A"),
        )
    )

    repository_factories = (
        binding_api.get_principal_authority_repository,
        binding_api.get_tenant_membership_repository,
        binding_api.get_role_assignment_repository,
        binding_api.get_authorization_role_repository,
    )

    for factory in repository_factories:
        server.app.dependency_overrides[factory] = lambda: object()

    try:
        client = TestClient(
            server.app, raise_server_exceptions=False
        )
        response = client.post(endpoint, json=payload)
        assert response.status_code == 503, (
            endpoint, response.status_code, response.text
        )
        assert response.json()["detail"] == (
            "P9_BINDING_INDEXES_NOT_READY"
        )
    finally:
        server.app.dependency_overrides.clear()
        server.app.state.p12c_binding_indexes_ready = False



@pytest.mark.parametrize(
    "endpoint,payload",
    [
        (
            "/api/legal-operations/practitioner-bindings",
            {
                "case_matter_id": "matter-A",
                "practitioner_principal_id": "lawyer-A",
                "binding_id": "binding-A",
                "access_evidence_id": "evidence-A",
                "expected_access_evidence_fingerprint": "a" * 128,
            },
        ),
        (
            "/api/legal-operations/practitioner-bindings/revocations",
            {
                "binding_id": "binding-A",
                "evidence_reference": "revocation-A",
            },
        ),
    ],
)
def test_ready_binding_command_reaches_transaction_boundary(
    monkeypatch, endpoint, payload
):
    """Certified-ready requests may reach the existing command boundary."""
    from types import SimpleNamespace
    from fastapi.testclient import TestClient
    from tools.eos.api import (
        legal_practitioner_matter_binding_router as binding_api,
    )

    transaction_calls = []

    def observed_transaction(callback):
        transaction_calls.append(callback)
        return {"readiness_certificate": "REACHED_TRANSACTION_BOUNDARY"}

    monkeypatch.setattr(
        binding_api, "_transaction", observed_transaction
    )

    server.app.state.p12c_binding_indexes_ready = True

    server.app.dependency_overrides[binding_api._PROVISION] = (
        lambda: SimpleNamespace(
            tenant_id="tenant-A",
            identity=SimpleNamespace(identity_id="partner-A"),
        )
    )

    factories = (
        binding_api.get_principal_authority_repository,
        binding_api.get_tenant_membership_repository,
        binding_api.get_role_assignment_repository,
        binding_api.get_authorization_role_repository,
    )
    for factory in factories:
        server.app.dependency_overrides[factory] = lambda: object()

    try:
        response = TestClient(
            server.app, raise_server_exceptions=False
        ).post(endpoint, json=payload)

        assert response.status_code == 201, (
            endpoint, response.status_code, response.text
        )
        assert response.json() == {
            "readiness_certificate": "REACHED_TRANSACTION_BOUNDARY"
        }
        assert len(transaction_calls) == 1
    finally:
        server.app.dependency_overrides.clear()
        server.app.state.p12c_binding_indexes_ready = False



@pytest.mark.parametrize(
    "failed_installer",
    ["access", "binding", "disposition", None, "missing_client"],
)
def test_p12c_index_startup_atomic_readiness(
    monkeypatch, failed_installer
):
    """Readiness becomes true only after every required installer succeeds."""
    from types import SimpleNamespace
    class Database:
        def __init__(self):
            self.collections = {}

        def __getitem__(self, name):
            if name not in self.collections:
                self.collections[name] = Collection(name, self)
            return self.collections[name]

        def get_collection(self, name):
            return self[name]

    class Collection:
        def __init__(self, name, database):
            self.name = name
            self.database = database

        def create_index(self, _keys, **_kwargs):
            return "startup-test-index"

    class NoopRegistry:
        def __init__(self, *args, **kwargs):
            pass

        def ensure_indexes(self, *args, **kwargs):
            return None

    class NoopSecurityRegistry:
        @staticmethod
        def ensure_indexes(*args, **kwargs):
            return None

    for symbol in (
        "TenantAuthorizationDecisionEvidenceRegistry",
        "AuthorizationRoleRevocationEvidenceRegistry",
        "PrivilegedFactorVerificationCurrentnessRegistry",
        "InternalServiceWorkloadCredentialRegistry",
        "PrivilegedWorkloadTrustCurrentnessRegistry",
        "PrivilegedNoninteractiveSecurityProofRegistry",
        "PrivilegedSecurityAssuranceEvidenceRegistry",
    ):
        monkeypatch.setattr(server, symbol, NoopRegistry)

    for symbol in (
        "InternalServiceReplayRegistry",
        "DeputyPrincipalBindingRegistry",
        "LegalStorefrontPublicIntentRegistry",
        "LegalStorefrontPublicIntentRateLimit",
    ):
        monkeypatch.setattr(server, symbol, NoopSecurityRegistry)

    monkeypatch.setattr(
        server, "connect_db", lambda: (True, "ISOLATED_TEST")
    )
    monkeypatch.setattr(server, "get_database", lambda: Database())
    monkeypatch.setattr(
        server,
        "get_client",
        lambda: None if failed_installer == "missing_client" else object(),
    )
    monkeypatch.setattr(
        server,
        "get_principal_authority_repository",
        lambda: object(),
    )

    calls = []

    def installer(name):
        def run(collection):
            calls.append((name, collection.name))
            if name == failed_installer:
                raise RuntimeError("P12C_INDEX_INSTALLATION_FAILED")
        return run

    monkeypatch.setattr(
        server.p12c_access_registry,
        "ensure_indexes",
        installer("access"),
    )
    monkeypatch.setattr(
        server.p12c_binding_registry,
        "ensure_indexes",
        installer("binding"),
    )
    monkeypatch.setattr(
        server.p12c_disposition_registry,
        "ensure_indexes",
        installer("disposition"),
    )

    handlers = [
        handler for handler in server.app.router.on_startup
        if handler.__name__ == "start_database"
    ]
    assert len(handlers) == 1

    server.app.state.p12c_binding_indexes_ready = False

    try:
        if failed_installer == "missing_client":
            asyncio.run(handlers[0]())
            assert [name for name, _ in calls] == [
                "access", "binding", "disposition"
            ]
            assert server.app.state.p12c_binding_indexes_ready is False
        elif failed_installer is None:
            asyncio.run(handlers[0]())
            assert server.app.state.p12c_binding_indexes_ready is True
            assert [name for name, _ in calls] == [
                "access", "binding", "disposition"
            ]
        else:
            with pytest.raises(
                RuntimeError,
                match="P12C_INDEX_INSTALLATION_FAILED",
            ):
                asyncio.run(handlers[0]())

            assert server.app.state.p12c_binding_indexes_ready is False
            assert failed_installer in [name for name, _ in calls]
            assert len(calls) == (
                ["access", "binding", "disposition"].index(
                    failed_installer
                ) + 1
            )
    finally:
        server.app.state.p12c_binding_indexes_ready = False



def test_p12c_shutdown_clears_readiness(monkeypatch):
    """Shutdown disables binding commands before disconnecting storage."""
    calls = []

    def isolated_disconnect():
        assert server.app.state.p12c_binding_indexes_ready is False
        calls.append("disconnect_db")

    monkeypatch.setattr(server, "disconnect_db", isolated_disconnect)

    handlers = [
        handler for handler in server.app.router.on_shutdown
        if handler.__name__ == "stop_database"
    ]
    assert len(handlers) == 1

    server.app.state.p12c_binding_indexes_ready = True
    try:
        asyncio.run(handlers[0]())
        assert calls == ["disconnect_db"]
        assert server.app.state.p12c_binding_indexes_ready is False
    finally:
        server.app.state.p12c_binding_indexes_ready = False


# ARTIFACT: test_legal_practitioner_binding_startup_readiness.py
# VERSION: v1.4.1-P12C-R4N-STARTUP-INDEX-DOUBLE-CERT
# AUTHORITY: EOS startup certificate only
# PHYSICAL DATABASE CONTACT: prohibited
# FINANCIAL EXECUTION AUTHORITY: none
# AUTHORITY BOUNDARY: Startup readiness certificate only; no identity or IAM grant
# TENANT POSTURE: No tenant records are read or written
# FAIL-CLOSED POSTURE: Failed database bootstrap or index readiness prevents normal startup
# END OF WILSY OS SOVEREIGN ARTIFACT
