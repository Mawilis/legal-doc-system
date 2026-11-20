"""
TITLE: WILSY OS Kernel Mongo Transport Observability Certificate
VERSION: v1.1.0-DEV-POOL-AWAITED-HELLO-CERT
AUTHORITY: Wilsy OS Core Governance
EPITOME: Proves opt-in trace timing, private heartbeat observations and
         fail-closed primary-selection recovery without live Mongo access.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_kernel_mongo_transport_observability.py
COLLABORATION / OWNERSHIP: Kernel Mongo lifecycle and authenticated timing
                           scope own the production implementation.
CERTIFICATION / UPDATE DATE: 2026-11-19
CHANGELOG: v1.1.0-DEV-POOL-AWAITED-HELLO-CERT certifies awaited
           streaming heartbeat exclusion and development-only zero-minimum
           connection pool alongside production minimum preservation.
CHANGELOG: v1.0.0-TRANSPORT-RECOVERY-CERT certifies trace accounting,
           endpoint-free transport telemetry and failure-then-reconnect state.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic events, no user, URI or live database access.
TENANT BOUNDARY: No persistence queries or real tenant identifiers.
AUTHORITY BOUNDARY: Deterministic mocked client, no login or grant authority.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes financial commands.
"""
from __future__ import annotations

from types import SimpleNamespace

from pymongo import errors

from tools.eos.kernel import db


def test_authenticated_precommand_and_residual_are_separately_accounted(monkeypatch):
    """Certify per-trace timing is additive without reading command payloads."""
    monkeypatch.setenv("WILSY_MY_WORK_TIMING", "1")
    clock = iter((0, 10_000_000, 60_000_000))
    monkeypatch.setattr(db.time, "perf_counter_ns", lambda: next(clock))
    records: list[dict] = []
    monkeypatch.setattr(db, "_emit_mongo_timing", lambda **value: records.append(value))
    listener = db._RequestMongoTimingListener()
    event = SimpleNamespace(
        request_id=7,
        connection_id=("DO_NOT_LOG_SERVER", 27017),
        server_connection_id=21,
        service_id=None,
        operation_id=10,
        duration_micros=20_000,
    )

    with db.mongo_timing_scope(
        stage="AUTH_CREDENTIAL_LEGACY_IDENTITY_LOOKUP",
        correlation="TRC-ABCDEFGH-ABC123",
    ):
        listener.started(event)
        listener.succeeded(event)

    by_event = {record["event"]: record for record in records}
    assert by_event["AUTH_MONGO_PRE_COMMAND_DRIVER_WAIT"]["duration_ms"] == 10.0
    assert by_event["AUTH_MONGO_COMMAND_ROUND_TRIP"]["duration_ms"] == 20.0
    assert by_event["AUTH_MONGO_CLIENT_RESIDUAL"]["duration_ms"] == 30.0
    assert all(record["trace_id"] == "TRC-ABCDEFGH-ABC123" for record in records)
    assert "DO_NOT_LOG_SERVER" not in str(records)


def test_connection_and_heartbeat_telemetry_is_bounded_and_private(monkeypatch, caplog):
    """Monitor connection and replica recovery without hostname or exception data."""
    monkeypatch.setenv("WILSY_MY_WORK_TIMING", "1")
    listener = db._RequestMongoTimingListener()
    heartbeats = db._RequestMongoHeartbeatListener()
    secret = "DO_NOT_LOG_ENDPOINT_OR_REPLY"
    with caplog.at_level("INFO", logger=db.__name__):
        listener.connection_ready(
            SimpleNamespace(duration=0.42, address=secret, connection_id=secret)
        )
        listener.pool_cleared(SimpleNamespace(address=secret))
        heartbeats.succeeded(
            SimpleNamespace(duration=0.25, connection_id=secret, reply=secret)
        )
        heartbeats.failed(
            SimpleNamespace(duration=0.6, connection_id=secret, reply=secret)
        )

    lines = [
        record.message for record in caplog.records
        if "WILSY_MONGO_TRANSPORT" in record.message
    ]
    assert len(lines) == 4
    assert any("event=CONNECTION_ESTABLISHMENT outcome=OK duration_ms=420.000" in line for line in lines)
    assert any("event=POOL_CLEARED outcome=OBSERVED" in line for line in lines)
    assert any("event=HEARTBEAT outcome=OK duration_ms=250.000" in line for line in lines)
    assert any("event=HEARTBEAT outcome=FAILED duration_ms=600.000" in line for line in lines)
    assert all(secret not in line for line in lines)

    caplog.clear()
    with caplog.at_level("INFO", logger=db.__name__):
        heartbeats.succeeded(
            SimpleNamespace(duration=10.0, awaited=True, connection_id=secret, reply=secret)
        )
        heartbeats.succeeded(
            SimpleNamespace(duration=0.35, awaited=False, connection_id=secret, reply=secret)
        )
    emitted = [
        record.message for record in caplog.records
        if "WILSY_MONGO_TRANSPORT" in record.message
    ]
    assert len(emitted) == 1
    assert "event=HEARTBEAT outcome=OK duration_ms=350.000" in emitted[0]


def test_primary_selection_failure_recovers_only_on_explicit_retry(monkeypatch):
    """Loss of primary must fail closed, never downgrade TLS, and reconnect cleanly."""
    monkeypatch.setattr(db, "_client", None)
    monkeypatch.setattr(db, "_db", None)
    monkeypatch.setattr(db, "_ready", False)
    monkeypatch.setattr(db, "_last_error", None)
    monkeypatch.setattr(db, "_retry_thread", None)
    monkeypatch.setattr(db, "_retry_stop", None)
    monkeypatch.setattr(db, "resolve_mongo_uri", lambda: "mongodb+srv://example.invalid/wilsy")
    monkeypatch.setattr(db, "_is_loopback_mongo_uri", lambda _: False)
    monkeypatch.delenv("WILSY_KENNEL_DB_TLS", raising=False)
    monkeypatch.delenv("WILSY_MY_WORK_TIMING", raising=False)

    clients = []

    class SyntheticClient:
        """Driver stand-in; never opens network sockets or reads identities."""

        def __init__(self, _uri, **kwargs):
            self.options = kwargs
            self.closed = False
            self.admin = self
            self.first = len(clients) == 0
            clients.append(self)

        def command(self, _name):
            if self.first:
                raise errors.ServerSelectionTimeoutError("SYNTHETIC_NO_PRIMARY")
            return {"ok": 1}

        def get_database(self):
            return SimpleNamespace(name="wilsy")

        def close(self):
            self.closed = True

    monkeypatch.setattr(db, "MongoClient", SyntheticClient)

    failure, _reason = db.connect_db()
    assert failure is False
    assert db.is_db_ready() is False
    assert clients[0].closed is True
    assert len(clients) == 1

    success, _reason = db.connect_db()
    assert success is True
    assert db.is_db_ready() is True
    assert len(clients) == 2
    assert clients[1].options["minPoolSize"] == 0
    assert clients[1].options["tls"] is True
    assert clients[1].options["tlsAllowInvalidCertificates"] is False
    assert clients[1].options["tlsAllowInvalidHostnames"] is False
    assert clients[1].options["serverSelectionTimeoutMS"] == 5000
    db.disconnect_db()
    assert clients[1].closed is True
    assert db.is_db_ready() is False


def test_production_connection_retains_ten_minimum_pooled_sockets(monkeypatch):
    """Preserve original production pool settings and mandatory TLS.

    @authority Synthetic connection options only; no remote or business access.
    @tenant No tenant record queried or disclosed.
    @failure Failure raises immediately on changed production connection policy.
    """
    monkeypatch.setenv("WILSY_ENV", "production")
    monkeypatch.setenv("MONGODB_URI", "mongodb+srv://example.invalid/wilsy")
    monkeypatch.delenv("WILSY_KENNEL_DB_TLS", raising=False)
    monkeypatch.delenv("WILSY_MY_WORK_TIMING", raising=False)
    monkeypatch.setattr(db, "_client", None)
    monkeypatch.setattr(db, "_db", None)
    monkeypatch.setattr(db, "_ready", False)
    monkeypatch.setattr(db, "_last_error", None)
    monkeypatch.setattr(db, "_retry_thread", None)
    monkeypatch.setattr(db, "_retry_stop", None)

    calls = []

    class SyntheticClient:
        """Capture production options without opening a real connection."""

        def __init__(self, _uri, **kwargs):
            self.options = kwargs
            self.admin = self
            calls.append(self)

        def command(self, _command):
            return {"ok": 1}

        def get_database(self):
            return SimpleNamespace(name="wilsy")

        def close(self):
            return

    monkeypatch.setattr(db, "MongoClient", SyntheticClient)
    result, _message = db.connect_db()
    assert result is True
    assert len(calls) == 1
    assert calls[0].options["minPoolSize"] == 10
    assert calls[0].options["maxPoolSize"] == 50
    assert calls[0].options["tls"] is True
    assert calls[0].options["tlsAllowInvalidCertificates"] is False
    assert calls[0].options["tlsAllowInvalidHostnames"] is False
    db.disconnect_db()


# ARTIFACT: tests/unit/test_kernel_mongo_transport_observability.py
# VERSION: v1.1.0-DEV-POOL-AWAITED-HELLO-CERT
# AUTHORITY BOUNDARY: Read-only synthetic Kernel transport verification.
# TENANT POSTURE: No tenant records or user identities.
# FAIL-CLOSED POSTURE: Primary unavailable cannot produce a ready connection.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
