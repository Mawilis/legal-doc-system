"""Direct certificate for the canonical Kernel database configuration authority.

TITLE: WILSY OS Kernel Database Configuration Authority Certificate
VERSION: v1.3.0-STRICT-REMOTE-MONGO-TLS-CERTIFICATE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves that MONGODB_URI remains canonical, remote MongoDB targets use
         verified TLS in every environment, local authenticated replica-set
         behavior remains intact, and diagnostics do not expose credentials.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_kernel_db_configuration_authority.py
COLLABORATION / OWNERSHIP: Certificate for tools.eos.kernel.db.
CERTIFICATION / UPDATE DATE: 2026-11-16
CHANGELOG:
  v1.3.0-STRICT-REMOTE-MONGO-TLS-CERTIFICATE proves Atlas and all remote
    targets require TLS, reject insecure overrides, and verify certificates
    and hostnames, while loopback Mongo retains its existing non-TLS default.
  v1.2.0-OPT-IN-MONGO-TIMING-CERTIFICATE covers opt-in listener attachment,
    validated opaque trace scope, fixed labels, privacy, checkout failures, and
    telemetry fault isolation at the canonical Mongo client boundary.
  v1.1.0-EOS-PRODUCTION-ENV-ALIAS-ALIGNMENT covers production markers and TLS.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Tests database configuration authority without exposing credentials or granting access to production data.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement or financial execution authority; Kennel EOS remains exclusive.
TENANT BOUNDARY: Database selection is configuration-owned, never request-owned.
AUTHORITY BOUNDARY: Kernel connection lifecycle only; no tenant or auth grant.
"""
from __future__ import annotations

import inspect
import io
import logging
import os
from datetime import timedelta
from types import SimpleNamespace
from typing import Any

import pytest

import tools.eos.kernel.db as kernel_db


def _disable_dotenv(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(kernel_db, "load_dotenv", lambda *_args, **_kwargs: False)


def test_process_mongodb_uri_is_canonical_even_when_legacy_aliases_differ(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv(monkeypatch)
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("MONGODB_URI", "mongodb://canonical/wilsy")
    monkeypatch.setenv("MONGO_URI", "mongodb://legacy/other")
    monkeypatch.setenv("DATABASE_URL", "mongodb://database-url/other")
    monkeypatch.setenv("WILSY_MONGO_URI", "mongodb://wilsy-alias/other")
    assert kernel_db.resolve_mongo_uri() == "mongodb://canonical/wilsy"


@pytest.mark.parametrize("legacy_name", ["MONGO_URI", "DATABASE_URL", "WILSY_MONGO_URI"])
def test_missing_canonical_uri_never_falls_back_to_legacy_alias(monkeypatch: pytest.MonkeyPatch, legacy_name: str) -> None:
    _disable_dotenv(monkeypatch)
    monkeypatch.setenv("ENV", "test")
    monkeypatch.delenv("MONGODB_URI", raising=False)
    monkeypatch.setenv(legacy_name, "mongodb://legacy/other")
    assert kernel_db.resolve_mongo_uri() == ""


def test_production_missing_authority_fails_before_mongo_client_creation(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv(monkeypatch)
    monkeypatch.setenv("ENV", "production")
    monkeypatch.delenv("MONGODB_URI", raising=False)
    monkeypatch.setenv("MONGO_URI", "mongodb://legacy/other")
    created: list[bool] = []

    class ForbiddenClient:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            created.append(True)

    monkeypatch.setattr(kernel_db, "MongoClient", ForbiddenClient)
    kernel_db.disconnect_db()
    connected, detail = kernel_db.connect_db()
    assert connected is False
    assert "missing" in detail.lower()
    assert created == []


def test_production_deployment_uri_is_not_overridden_or_dotenv_loaded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "production")
    monkeypatch.setenv("MONGODB_URI", "mongodb://deployment/wilsy")
    monkeypatch.setenv("MONGO_URI", "mongodb://legacy/other")

    def forbidden_dotenv(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("repository dotenv is forbidden in production")

    monkeypatch.setattr(kernel_db, "load_dotenv", forbidden_dotenv)
    assert kernel_db.resolve_mongo_uri() == "mongodb://deployment/wilsy"


def test_nonproduction_dotenv_can_supply_only_missing_canonical_uri(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "development")
    monkeypatch.delenv("MONGODB_URI", raising=False)

    def controlled_dotenv(*_args: Any, **_kwargs: Any) -> None:
        os.environ.setdefault("MONGODB_URI", "mongodb://dotenv/wilsy")

    monkeypatch.setattr(kernel_db, "load_dotenv", controlled_dotenv)
    assert kernel_db.resolve_mongo_uri() == "mongodb://dotenv/wilsy"


def test_safe_status_contains_database_name_but_no_uri_or_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(kernel_db, "_db", SimpleNamespace(name="wilsy-os-dev"))
    monkeypatch.setattr(kernel_db, "_client", object())
    monkeypatch.setattr(kernel_db, "_last_error", None)
    status = kernel_db.get_db_status()
    assert status == {
        "ready": False,
        "client_created": True,
        "database_name": "wilsy-os-dev",
        "last_error": None,
        "retry_thread_alive": False,
    }
    rendered = repr(status)
    assert "mongodb://" not in rendered
    assert "password" not in rendered.lower()


def test_resolver_source_has_no_legacy_fallback_authorities() -> None:
    source = inspect.getsource(kernel_db.resolve_mongo_uri)
    assert "MONGO_URI" not in source
    assert "DATABASE_URL" not in source
    assert "WILSY_MONGO_URI" not in source
    assert "localhost" not in source



def test_wilsy_env_production_disables_repository_dotenv_without_legacy_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WILSY_ENV", "production")
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.setenv("MONGODB_URI", "mongodb+srv://deployment.example/wilsy")

    def forbidden_dotenv(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("WILSY_ENV=production must disable repository dotenv")

    monkeypatch.setattr(kernel_db, "load_dotenv", forbidden_dotenv)
    assert kernel_db._is_production_environment() is True
    assert kernel_db.resolve_mongo_uri() == "mongodb+srv://deployment.example/wilsy"


def test_wilsy_env_production_missing_uri_fails_before_client_creation(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv(monkeypatch)
    monkeypatch.setenv("WILSY_ENV", "production")
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.delenv("MONGODB_URI", raising=False)
    created: list[bool] = []

    class ForbiddenClient:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            created.append(True)

    monkeypatch.setattr(kernel_db, "MongoClient", ForbiddenClient)
    kernel_db.disconnect_db()
    connected, detail = kernel_db.connect_db()
    assert connected is False
    assert "missing" in detail.lower()
    assert created == []


def test_wilsy_env_production_enforces_verified_tls(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv(monkeypatch)
    monkeypatch.setenv("WILSY_ENV", "production")
    monkeypatch.delenv("ENV", raising=False)
    monkeypatch.setenv("MONGODB_URI", "mongodb+srv://deployment.example/wilsy")
    captured: dict[str, Any] = {}

    class FakeAdmin:
        def command(self, command: str) -> dict[str, int]:
            assert command == "ping"
            return {"ok": 1}

    class FakeDatabase:
        name = "wilsy"

    class FakeClient:
        def __init__(self, _uri: str, **options: Any) -> None:
            captured.update(options)
            self.admin = FakeAdmin()

        def get_database(self) -> FakeDatabase:
            return FakeDatabase()

        def close(self) -> None:
            return None

    monkeypatch.setattr(kernel_db, "MongoClient", FakeClient)
    kernel_db.disconnect_db()
    connected, detail = kernel_db.connect_db()
    try:
        assert connected is True, detail
        assert captured["tls"] is True
        assert captured["tlsAllowInvalidCertificates"] is False
        assert captured["tlsAllowInvalidHostnames"] is False
    finally:
        kernel_db.disconnect_db()


def test_nonproduction_atlas_enforces_verified_tls(monkeypatch: pytest.MonkeyPatch) -> None:
    _disable_dotenv(monkeypatch)
    monkeypatch.setenv("ENV", "development")
    monkeypatch.delenv("WILSY_ENV", raising=False)
    monkeypatch.delenv("WILSY_KENNEL_DB_TLS", raising=False)
    uri = "mongodb+srv://operator:synthetic-secret@cluster.example.mongodb.net/wilsy"
    monkeypatch.setenv("MONGODB_URI", uri)
    captured: dict[str, Any] = {}

    class FakeAdmin:
        def command(self, command: str) -> dict[str, int]:
            assert command == "ping"
            return {"ok": 1}

    class FakeDatabase:
        name = "wilsy"

    class FakeClient:
        def __init__(self, selected_uri: str, **options: Any) -> None:
            captured["uri"] = selected_uri
            captured.update(options)
            self.admin = FakeAdmin()

        def get_database(self) -> FakeDatabase:
            return FakeDatabase()

        def close(self) -> None:
            return None

    monkeypatch.setattr(kernel_db, "MongoClient", FakeClient)
    kernel_db.disconnect_db()
    connected, detail = kernel_db.connect_db()
    try:
        assert connected is True, detail
        assert captured["uri"] == uri
        assert captured["tls"] is True
        assert captured["tlsAllowInvalidCertificates"] is False
        assert captured["tlsAllowInvalidHostnames"] is False
    finally:
        kernel_db.disconnect_db()


@pytest.mark.parametrize("override", ["0", "false", "no", "off"])
def test_atlas_rejects_insecure_tls_override_before_client_creation(
    monkeypatch: pytest.MonkeyPatch,
    override: str,
) -> None:
    _disable_dotenv(monkeypatch)
    monkeypatch.setenv("ENV", "development")
    monkeypatch.delenv("WILSY_ENV", raising=False)
    monkeypatch.setenv("WILSY_KENNEL_DB_TLS", override)
    monkeypatch.setenv(
        "MONGODB_URI",
        "mongodb+srv://operator:synthetic-secret@cluster.example.mongodb.net/wilsy",
    )
    created: list[bool] = []

    class ForbiddenClient:
        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            created.append(True)

    monkeypatch.setattr(kernel_db, "MongoClient", ForbiddenClient)
    kernel_db.disconnect_db()
    connected, detail = kernel_db.connect_db()
    assert connected is False
    assert "TLS required" in detail
    assert created == []


def test_local_authenticated_replica_set_keeps_non_tls_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_dotenv(monkeypatch)
    monkeypatch.setenv("ENV", "development")
    monkeypatch.delenv("WILSY_ENV", raising=False)
    monkeypatch.delenv("WILSY_KENNEL_DB_TLS", raising=False)
    uri = "mongodb://operator:synthetic-secret@127.0.0.1:27017/wilsy?replicaSet=rs0&authSource=admin"
    monkeypatch.setenv("MONGODB_URI", uri)
    captured: dict[str, Any] = {}

    class FakeAdmin:
        def command(self, command: str) -> dict[str, int]:
            assert command == "ping"
            return {"ok": 1}

    class FakeDatabase:
        name = "wilsy"

    class FakeClient:
        def __init__(self, selected_uri: str, **options: Any) -> None:
            captured["uri"] = selected_uri
            captured.update(options)
            self.admin = FakeAdmin()

        def get_database(self) -> FakeDatabase:
            return FakeDatabase()

        def close(self) -> None:
            return None

    monkeypatch.setattr(kernel_db, "MongoClient", FakeClient)
    kernel_db.disconnect_db()
    connected, detail = kernel_db.connect_db()
    try:
        assert connected is True, detail
        assert captured["uri"] == uri
        assert captured["tls"] is False
        assert "tlsAllowInvalidCertificates" not in captured
        assert "tlsAllowInvalidHostnames" not in captured
    finally:
        kernel_db.disconnect_db()


def test_mongo_timing_scope_correlates_only_safe_pool_and_command_metrics(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WILSY_MY_WORK_TIMING", "1")
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger = logging.getLogger(kernel_db.__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    listener = kernel_db._RequestMongoTimingListener()
    listener.configure_pool_capacity(50)
    address = ("diagnostic-host-never-logged", 27017)
    listener.pool_created(SimpleNamespace(address=address, options={"maxPoolSize": 50}))
    trace = "TRC-ABCDEFGH-123456"
    try:
        with kernel_db.mongo_timing_scope(
            stage="AUTH_CREDENTIAL_LEGACY_IDENTITY_LOOKUP",
            correlation=trace,
        ):
            listener.connection_checked_out(
                SimpleNamespace(address=address, connection_id=1, duration=0.002)
            )
            listener.started(
                SimpleNamespace(
                    request_id=71,
                    command_name="find",
                    command={"filter": {"principal": "private-principal"}},
                )
            )
            listener.succeeded(
                SimpleNamespace(request_id=71, duration=timedelta(milliseconds=7))
            )
            listener.connection_check_out_failed(
                SimpleNamespace(
                    address=address,
                    reason="private driver failure details",
                    duration=0.003,
                )
            )
    finally:
        logger.removeHandler(handler)
    rendered = stream.getvalue()
    assert trace in rendered
    assert "AUTH_MONGO_POOL_CHECKOUT" in rendered
    assert "AUTH_MONGO_POOL_PRESSURE" in rendered
    assert "AUTH_MONGO_COMMAND_ROUND_TRIP" in rendered
    assert "AUTH_MONGO_POOL_CHECKOUT_FAILURE" in rendered
    assert "AUTH_MONGO_CLIENT_RESIDUAL" in rendered
    assert "private-principal" not in rendered
    assert "diagnostic-host-never-logged" not in rendered
    assert "private driver failure details" not in rendered


def test_mongo_timing_scope_rejects_invalid_trace_and_stage(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setenv("WILSY_MY_WORK_TIMING", "1")
    with caplog.at_level(logging.INFO, logger=kernel_db.__name__):
        with kernel_db.mongo_timing_scope(
            stage="AUTH_CREDENTIAL_LEGACY_IDENTITY_LOOKUP", correlation="bad-trace"
        ):
            pass
        with kernel_db.mongo_timing_scope(
            stage="AUTH_UNLISTED_STAGE", correlation="TRC-ABCDEFGH-123456"
        ):
            pass
    assert "WILSY_MONGO_TIMING" not in caplog.text


def test_mongo_timing_fault_isolation_preserves_operation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("WILSY_MY_WORK_TIMING", "1")
    executed: list[bool] = []

    def fail_telemetry(*_args: Any, **_kwargs: Any) -> None:
        raise RuntimeError("diagnostic sink failure")

    monkeypatch.setattr(kernel_db.logger, "info", fail_telemetry)
    with kernel_db.mongo_timing_scope(
        stage="AUTH_CREDENTIAL_LEGACY_IDENTITY_LOOKUP",
        correlation="TRC-ABCDEFGH-123456",
    ):
        executed.append(True)
    assert executed == [True]


def test_mongo_timing_listener_is_attached_only_when_opted_in(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _disable_dotenv(monkeypatch)
    monkeypatch.setenv("ENV", "development")
    monkeypatch.setenv("WILSY_MY_WORK_TIMING", "1")
    monkeypatch.setenv("MONGODB_URI", "mongodb://diagnostic.invalid/wilsy")
    captured: dict[str, Any] = {}

    class FakeAdmin:
        def command(self, command: str) -> dict[str, int]:
            assert command == "ping"
            return {"ok": 1}

    class FakeDatabase:
        name = "wilsy"

    class FakeClient:
        def __init__(self, _uri: str, **options: Any) -> None:
            captured.update(options)
            self.admin = FakeAdmin()

        def get_database(self) -> FakeDatabase:
            return FakeDatabase()

        def close(self) -> None:
            return None

    monkeypatch.setattr(kernel_db, "MongoClient", FakeClient)
    kernel_db.disconnect_db()
    connected, detail = kernel_db.connect_db()
    try:
        assert connected is True, detail
        assert captured["event_listeners"] == [kernel_db._MONGO_TIMING_LISTENER]
        assert captured["maxPoolSize"] == 50
    finally:
        kernel_db.disconnect_db()


# ARTIFACT: test_kernel_db_configuration_authority.py
# VERSION: v1.3.0-STRICT-REMOTE-MONGO-TLS-CERTIFICATE
# AUTHORITY BOUNDARY: Kernel configuration certificate only.
# TENANT POSTURE: Database identity is not selected by tenant aliases or requests.
# FAIL-CLOSED POSTURE: Missing production MONGODB_URI prevents MongoClient creation.
# ENVIRONMENT POSTURE: WILSY_ENV=production is authoritative for EOS deployments.
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
