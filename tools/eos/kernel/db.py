# -*- coding: utf-8 -*-
"""
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
Wilsy OS canonical Kennel database lifecycle and opt-in timing boundary.

TITLE: WILSY OS Sovereign Kennel Database Anchor
VERSION: v2.7.1-POOL-OPTION-RESTORATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Owns the sole EOS MongoClient lifecycle and canonical database binding;
         optionally observes request-scoped pool and command timings.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kernel/db.py
COLLABORATION / OWNERSHIP: EOS runtime owns connection startup and shutdown;
                           AuthRegistry supplies validated timing context only.
CERTIFICATION / UPDATE DATE: 2026-11-19
CHANGELOG:
  v2.7.1-POOL-OPTION-RESTORATION — Restores actual source line breaks so
    minPoolSize is passed to MongoClient: zero outside production and ten in
    production. This is a configuration delivery fix only; no changes to TLS,
    tenant authority, retries, timeouts or the heartbeat filter.
  v2.7.0-DEV-POOL-STREAMING-HEARTBEAT — Avoids forced minimum connection
    replenishment only outside production, while retaining production pool
    settings. Filters successful awaited streaming heartbeat durations from
    slow-heartbeat telemetry because the server deliberately holds awaitable
    hello for its long-poll window; retains non-awaited and failed events.
    Preserves TLS, timeout, retry, tenant and authorization semantics.
  v2.6.0-OPT-IN-TRANSPORT-PHASE-TELEMETRY — Adds opt-in pre-command
    driver timing, connection establishment and heartbeat observations.
    Preserves exact-tenant authority, security settings and driver retries.
  v2.5.0-STRICT-REMOTE-MONGO-TLS — Requires TLS for every non-loopback
    MongoDB target, rejects explicit insecure remote overrides, and always
    validates certificates and hostnames for TLS connections.
  v2.4.0-OPT-IN-MONGO-REQUEST-DIAGNOSTICS — Adds fail-isolated, trace-bound
    Mongo pool checkout and command round-trip telemetry at the canonical
    MongoClient construction boundary. It records no query, document, database,
    endpoint, credential, principal, tenant, or exception values.
  v2.3.0-EOS-PRODUCTION-ENV-ALIAS-ALIGNMENT — Treats either WILSY_ENV or ENV
    production marker as authoritative and blocks repository dotenv rescue.
  v2.2.0-R1D-B0F-B3B-R0-CANONICAL-URI — Makes MONGODB_URI the sole database
    authority and blocks repository dotenv rescue in production.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Remote MongoDB transport requires certificate- and
    hostname-verified TLS. Mongo monitoring is disabled unless
    WILSY_MY_WORK_TIMING=1; telemetry is allowlisted and fail-isolated.
TENANT BOUNDARY: Database selection is configuration-owned; query tenant scope
    remains the calling registry's responsibility.
AUTHORITY BOUNDARY: Connection lifecycle and safe diagnostics only; no business
    or authorization authority is created.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns execution.
"""
import logging
import ipaddress
import os
import re
import threading
import time
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlsplit

from dotenv import load_dotenv
from pymongo import MongoClient, errors, monitoring

logger = logging.getLogger(__name__)

# The kernel is launched directly by the root development command, so it does
# not inherit Node's dotenv bootstrap. Repository dotenv is a development/test
# convenience only; production must receive MONGODB_URI from deployment.
_REPOSITORY_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


def _mongo_hosts(uri: str) -> tuple[str, ...]:
    """Extract MongoDB seed hosts without exposing URI credentials.

    This parser is used only to distinguish loopback development targets from
    remote databases. PyMongo remains responsible for full URI validation and
    connection semantics.
    """
    try:
        parsed = urlsplit(uri)
        authority = parsed.netloc.rsplit("@", 1)[-1]
        hosts: list[str] = []
        for endpoint in authority.split(","):
            value = endpoint.strip()
            if value.startswith("[") and "]" in value:
                host = value[1:value.index("]")]
            else:
                host = value.rsplit(":", 1)[0] if ":" in value else value
            if host:
                hosts.append(host.rstrip(".").lower())
        if parsed.scheme == "mongodb+srv" and parsed.hostname:
            return (parsed.hostname.rstrip(".").lower(),)
        return tuple(hosts)
    except (TypeError, ValueError):
        return ()


def _is_loopback_mongo_uri(uri: str) -> bool:
    """Return true only when every canonical MongoDB seed is loopback."""
    hosts = _mongo_hosts(uri)
    if not hosts:
        return False
    for host in hosts:
        if host == "localhost":
            continue
        try:
            if not ipaddress.ip_address(host).is_loopback:
                return False
        except ValueError:
            return False
    return True


def _is_production_environment() -> bool:
    """Fail safe when either supported deployment marker declares production.

    The canonical EOS Kubernetes manifest sets WILSY_ENV=production. Older
    deployments may set ENV=production. Treat either marker as authoritative
    so an unset ENV cannot silently downgrade a production EOS process.
    """
    production_values = {"production", "prod"}
    return any(
        os.getenv(name, "").strip().lower() in production_values
        for name in ("WILSY_ENV", "ENV")
    )


def _load_nonproduction_dotenv() -> None:
    """Load repository dotenv only outside production and never override env."""
    if not _is_production_environment():
        load_dotenv(_REPOSITORY_ENV_PATH, override=False)

# --- Configuration ---
MAX_RETRY_ATTEMPTS = int(os.getenv('WILSY_KENNEL_DB_MAX_RETRIES', 5))
RETRY_DELAY_MS = int(os.getenv('WILSY_KENNEL_DB_RETRY_MS', 5000))

# --- State ---
_client = None
_db = None
_ready = False
_last_error = None
_state_lock = threading.RLock()
_retry_thread = None

_MONGO_TIMING_ENVIRONMENT_VARIABLE = "WILSY_MY_WORK_TIMING"
_MONGO_TIMING_STAGES = frozenset(
    {
        "AUTH_CREDENTIAL_TENANT_RESOLUTION",
        "AUTH_CREDENTIAL_EXACT_IDENTITY_LOOKUP",
        "AUTH_CREDENTIAL_LEGACY_IDENTITY_LOOKUP",
        "AUTH_CREDENTIAL_COLLISION_VERIFICATION",
        "AUTH_CREDENTIAL_RECORD_HYDRATION_VALIDATION",
    }
)
_MONGO_TRACE_PATTERN = re.compile(
    r"TRC-(?:[A-Z0-9]{8}-[A-Z0-9]{6}|SERVER-[A-F0-9]{12})\Z"
)
_MONGO_TIMING_CONTEXT: ContextVar[dict[str, Any] | None] = ContextVar(
    "wilsy_kernel_mongo_timing_context", default=None
)


def _mongo_timing_is_enabled() -> bool:
    """Return whether request-scoped Mongo timing was enabled at process runtime."""
    return os.getenv(_MONGO_TIMING_ENVIRONMENT_VARIABLE, "").strip() == "1"


def _emit_mongo_timing(
    *,
    trace_id: str,
    operation_stage: str,
    event: str,
    outcome: str,
    duration_ms: float,
    checked_out: int | None = None,
    pool_capacity: int | None = None,
) -> None:
    """Write only allowlisted stage labels and bounded numeric diagnostics."""
    if (
        not _mongo_timing_is_enabled()
        or _MONGO_TRACE_PATTERN.fullmatch(trace_id) is None
        or operation_stage not in _MONGO_TIMING_STAGES
        or event not in {
            "AUTH_MONGO_POOL_CHECKOUT",
            "AUTH_MONGO_POOL_CHECKOUT_FAILURE",
            "AUTH_MONGO_POOL_PRESSURE",
            "AUTH_MONGO_COMMAND_ROUND_TRIP",
            "AUTH_MONGO_CLIENT_RESIDUAL",
            "AUTH_MONGO_PRE_COMMAND_DRIVER_WAIT",
        }
        or outcome not in {"OK", "FAILED", "OBSERVED"}
    ):
        return
    try:
        if event == "AUTH_MONGO_POOL_PRESSURE":
            if checked_out is None or pool_capacity is None:
                return
            logger.info(
                "WILSY_MONGO_TIMING trace_id=%s operation_stage=%s event=%s outcome=%s checked_out=%d pool_capacity=%d",
                trace_id,
                operation_stage,
                event,
                outcome,
                max(0, checked_out),
                max(0, pool_capacity),
            )
            return
        safe_duration = max(0.0, float(duration_ms))
        logger.info(
            "WILSY_MONGO_TIMING trace_id=%s operation_stage=%s event=%s outcome=%s duration_ms=%.3f",
            trace_id,
            operation_stage,
            event,
            outcome,
            safe_duration,
        )
    except Exception:
        # Optional diagnostics must never alter database or authorization behavior.
        return


@contextmanager
def mongo_timing_scope(*, stage: str, correlation: str | None) -> Iterator[None]:
    """Bind one safe credential-read stage to Mongo monitoring callbacks.

    @description Correlates pool and command timing for the exact synchronous
    Mongo operation performed inside this scope.
    @collaboration AuthRegistry credential-currentness diagnostics only.
    @institutional Observation has no connection, query, transaction, tenant,
    credential, or authorization authority. Invalid context remains unobserved.
    """
    if (
        not _mongo_timing_is_enabled()
        or stage not in _MONGO_TIMING_STAGES
        or not isinstance(correlation, str)
        or _MONGO_TRACE_PATTERN.fullmatch(correlation) is None
    ):
        yield
        return
    scope: dict[str, Any] = {
        "trace_id": correlation,
        "operation_stage": stage,
        "started_ns": time.perf_counter_ns(),
        "pool_wait_ms": 0.0,
        "command_round_trip_ms": 0.0,
        "first_command_observed": False,
        "pre_command_ms": 0.0,
    }
    token = _MONGO_TIMING_CONTEXT.set(scope)
    outcome = "OBSERVED"
    try:
        yield
    except BaseException:
        outcome = "FAILED"
        raise
    finally:
        _MONGO_TIMING_CONTEXT.reset(token)
        elapsed_ms = max(0.0, (time.perf_counter_ns() - scope["started_ns"]) / 1_000_000)
        residual_ms = max(
            0.0,
            elapsed_ms - scope["pool_wait_ms"] - scope["command_round_trip_ms"]
            - scope["pre_command_ms"],
        )
        _emit_mongo_timing(
            trace_id=scope["trace_id"],
            operation_stage=scope["operation_stage"],
            event="AUTH_MONGO_CLIENT_RESIDUAL",
            outcome=outcome,
            duration_ms=residual_ms,
        )


class _RequestMongoTimingListener(monitoring.CommandListener, monitoring.ConnectionPoolListener):
    """Observe scoped Mongo checkout and round-trip timings without query data."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._command_scopes: dict[tuple[Any, ...], dict[str, Any]] = {}
        self._checked_out: dict[Any, int] = {}
        self._pool_capacities: dict[Any, int] = {}
        self._configured_pool_capacity: int | None = None

    def started(self, event: Any) -> None:
        try:
            scope = _MONGO_TIMING_CONTEXT.get()
            if scope is None or not _mongo_timing_is_enabled():
                return
            if not scope["first_command_observed"]:
                scope["first_command_observed"] = True
                precommand_ms = max(
                    0.0,
                    (time.perf_counter_ns() - scope["started_ns"]) / 1_000_000
                    - scope["pool_wait_ms"],
                )
                scope["pre_command_ms"] = precommand_ms
                # Includes server selection plus driver setup/scheduling;
                # this is not falsely described as pure server selection.
                _emit_mongo_timing(
                    trace_id=scope["trace_id"],
                    operation_stage=scope["operation_stage"],
                    event="AUTH_MONGO_PRE_COMMAND_DRIVER_WAIT",
                    outcome="OBSERVED",
                    duration_ms=precommand_ms,
                )
            key = self._command_key(event)
            with self._lock:
                self._command_scopes[key] = scope
        except Exception:
            return

    @staticmethod
    def _command_key(event: Any) -> tuple[Any, ...]:
        """Use internal driver correlation fields without logging them."""
        return (
            getattr(event, "connection_id", None),
            getattr(event, "server_connection_id", None),
            getattr(event, "service_id", None),
            getattr(event, "operation_id", None),
            int(event.request_id),
        )

    def succeeded(self, event: Any) -> None:
        self._finish_command(event, outcome="OK")

    def failed(self, event: Any) -> None:
        self._finish_command(event, outcome="FAILED")

    def _finish_command(self, event: Any, *, outcome: str) -> None:
        try:
            with self._lock:
                scope = self._command_scopes.pop(self._command_key(event), None)
            if scope is None:
                return
            duration_micros = getattr(event, "duration_micros", None)
            if isinstance(duration_micros, (int, float)) and not isinstance(duration_micros, bool):
                duration = max(0.0, float(duration_micros) / 1000.0)
            else:
                duration = max(0.0, float(event.duration.total_seconds()) * 1000.0)
            scope["command_round_trip_ms"] += duration
            _emit_mongo_timing(
                trace_id=scope["trace_id"],
                operation_stage=scope["operation_stage"],
                event="AUTH_MONGO_COMMAND_ROUND_TRIP",
                outcome=outcome,
                duration_ms=duration,
            )
        except Exception:
            return

    def configure_pool_capacity(self, value: int) -> None:
        """Record the canonical client setting for per-server saturation context."""
        if isinstance(value, int) and value > 0:
            self._configured_pool_capacity = value

    def pool_created(self, event: Any) -> None:
        try:
            options = getattr(event, "options", {})
            maximum = (
                options.get("maxPoolSize", self._configured_pool_capacity)
                if isinstance(options, dict)
                else self._configured_pool_capacity
            )
            if isinstance(maximum, int) and maximum > 0:
                with self._lock:
                    self._pool_capacities[event.address] = maximum
                    self._checked_out.setdefault(event.address, 0)
        except Exception:
            return

    def pool_ready(self, event: Any) -> None:
        return

    def pool_cleared(self, event: Any) -> None:
        _emit_transport_phase("POOL_CLEARED", "OBSERVED", 0.0)

    def pool_closed(self, event: Any) -> None:
        try:
            with self._lock:
                self._checked_out.pop(event.address, None)
                self._pool_capacities.pop(event.address, None)
        except Exception:
            return

    def connection_created(self, event: Any) -> None:
        return

    def connection_ready(self, event: Any) -> None:
        try:
            seconds = getattr(event, "duration", None)
            if isinstance(seconds, (int, float)) and not isinstance(seconds, bool):
                _emit_transport_phase(
                    "CONNECTION_ESTABLISHMENT", "OK",
                    max(0.0, float(seconds) * 1000.0),
                )
        except Exception:
            return

    def connection_closed(self, event: Any) -> None:
        return

    def connection_check_out_started(self, event: Any) -> None:
        return

    def connection_checked_out(self, event: Any) -> None:
        try:
            with self._lock:
                active = self._checked_out.get(event.address, 0) + 1
                self._checked_out[event.address] = active
                capacity = self._pool_capacities.get(event.address)
            scope = _MONGO_TIMING_CONTEXT.get()
            if scope is None:
                return
            duration_seconds = getattr(event, "duration", None)
            wait_ms = max(0.0, float(duration_seconds or 0.0) * 1000.0)
            scope["pool_wait_ms"] += wait_ms
            _emit_mongo_timing(
                trace_id=scope["trace_id"],
                operation_stage=scope["operation_stage"],
                event="AUTH_MONGO_POOL_CHECKOUT",
                outcome="OK",
                duration_ms=wait_ms,
            )
            if capacity is not None:
                _emit_mongo_timing(
                    trace_id=scope["trace_id"],
                    operation_stage=scope["operation_stage"],
                    event="AUTH_MONGO_POOL_PRESSURE",
                    outcome="OBSERVED",
                    duration_ms=0.0,
                    checked_out=active,
                    pool_capacity=capacity,
                )
        except Exception:
            return

    def connection_checked_in(self, event: Any) -> None:
        try:
            with self._lock:
                active = max(0, self._checked_out.get(event.address, 0) - 1)
                self._checked_out[event.address] = active
        except Exception:
            return

    def connection_check_out_failed(self, event: Any) -> None:
        try:
            scope = _MONGO_TIMING_CONTEXT.get()
            if scope is None:
                return
            duration_seconds = getattr(event, "duration", None)
            wait_ms = max(0.0, float(duration_seconds or 0.0) * 1000.0)
            with self._lock:
                active = self._checked_out.get(event.address, 0)
                capacity = self._pool_capacities.get(event.address)
            _emit_mongo_timing(
                trace_id=scope["trace_id"],
                operation_stage=scope["operation_stage"],
                event="AUTH_MONGO_POOL_CHECKOUT_FAILURE",
                outcome="FAILED",
                duration_ms=wait_ms,
                checked_out=active if capacity is not None else None,
                pool_capacity=capacity,
            )
        except Exception:
            return


def _emit_transport_phase(event: str, outcome: str, duration_ms: float) -> None:
    """Emit opt-in driver telemetry; no endpoint, user, tenant or error data.

    @authority Observability only, without database or financial authority.
    @privacy Only fixed labels and nonnegative durations are emitted.
    """
    if (
        not _mongo_timing_is_enabled()
        or event not in {"CONNECTION_ESTABLISHMENT", "HEARTBEAT", "POOL_CLEARED"}
        or outcome not in {"OK", "FAILED", "OBSERVED"}
    ):
        return
    try:
        logger.info(
            "WILSY_MONGO_TRANSPORT event=%s outcome=%s duration_ms=%.3f",
            event, outcome, max(0.0, float(duration_ms)),
        )
    except Exception:
        return


class _RequestMongoHeartbeatListener(monitoring.ServerHeartbeatListener):
    """Observe slow/failed heartbeats without affecting topology selection.

    @authority Monitoring only; no tenant or financial execution.
    @privacy Replies and network endpoints are never inspected or logged.
    """

    def started(self, event: Any) -> None:
        return

    def succeeded(self, event: Any) -> None:
        try:
            # Awaited streaming hello is intentionally long-polled by MongoDB,
            # often for approximately ten seconds. It is not a network RTT.
            if getattr(event, "awaited", False) is True:
                return
            seconds = getattr(event, "duration", None)
            if isinstance(seconds, (int, float)) and not isinstance(seconds, bool):
                if float(seconds) >= 0.1:
                    _emit_transport_phase("HEARTBEAT", "OK", float(seconds) * 1000.0)
        except Exception:
            return

    def failed(self, event: Any) -> None:
        try:
            seconds = getattr(event, "duration", None)
            value = (
                max(0.0, float(seconds) * 1000.0)
                if isinstance(seconds, (int, float)) and not isinstance(seconds, bool)
                else 0.0
            )
            _emit_transport_phase("HEARTBEAT", "FAILED", value)
        except Exception:
            return


_MONGO_TIMING_LISTENER = _RequestMongoTimingListener()
_MONGO_HEARTBEAT_LISTENER = _RequestMongoHeartbeatListener()
_retry_stop = None


def resolve_mongo_uri():
    """Resolve the sole canonical URI, failing closed when it is absent.

    ``MONGODB_URI`` is deployment authority. In non-production, the repository
    ``.env`` may populate it when the process did not already provide it. No
    alternate authority participates.
    """
    _load_nonproduction_dotenv()
    return str(os.getenv("MONGODB_URI") or "").strip()


def get_db_status():
    """Return diagnostic snapshot."""
    with _state_lock:
        return {
            'ready': _ready,
            'client_created': _client is not None,
            'database_name': _db.name if _db is not None else None,
            'last_error': str(_last_error) if _last_error else None,
            'retry_thread_alive': bool(_retry_thread and _retry_thread.is_alive()),
        }


def is_db_ready():
    """Return True if the database is connected and ready."""
    with _state_lock:
        return _ready and _client is not None


def get_database():
    """Return the MongoDB database instance."""
    with _state_lock:
        return _db


def get_client():
    """Return the MongoDB client instance."""
    with _state_lock:
        return _client


def connect_db(force_reconnect=False):
    """
    Sovereign Atlas connector for the Kennel. Resolves connectivity only when
    explicitly invoked by the runtime owner; callers may separately request
    bounded background re-anchor retries after a failed connection.
    Returns (success: bool, message: str).
    """
    global _client, _db, _ready, _last_error

    with _state_lock:
        if _ready and _client is not None and not force_reconnect:
            return True, "Already connected"

    uri = resolve_mongo_uri()
    if not uri:
        _last_error = "MONGODB_URI environment variable missing"
        logger.error("[KENNEL_DB] 💥 CRITICAL: No MONGODB_URI in environment.")
        return False, "MONGODB_URI missing"

    # Remote MongoDB transport is always encrypted. Only all-loopback
    # development replica sets retain the established non-TLS default.
    # Atlas SRV hosts are remote by definition. Explicit TLS configuration may
    # enable TLS locally, but cannot downgrade any remote or production target.
    is_loopback_target = _is_loopback_mongo_uri(uri)
    tls_required = _is_production_environment() or not is_loopback_target
    configured_tls = os.getenv('WILSY_KENNEL_DB_TLS')
    if configured_tls is not None:
        normalized_tls = configured_tls.strip().lower()
        if normalized_tls not in {'1', 'true', 'yes', 'on', '0', 'false', 'no', 'off'}:
            _last_error = 'WILSY_KENNEL_DB_TLS configuration invalid'
            logger.error('[KENNEL_DB] TLS configuration is invalid; connection refused.')
            return False, 'TLS configuration invalid'
        requested_tls = normalized_tls in {'1', 'true', 'yes', 'on'}
        if tls_required and not requested_tls:
            _last_error = 'TLS required for remote MongoDB target'
            logger.error('[KENNEL_DB] TLS downgrade refused for remote database target.')
            return False, 'TLS required for remote database target'
        tls_enabled = requested_tls or tls_required
    else:
        tls_enabled = tls_required

    # PyMongo uses the platform trust store and verifies hostnames by default.
    # Set both flags explicitly so development configuration cannot silently
    # accept an invalid Atlas certificate or endpoint identity.
    options = {
        'tls': tls_enabled,
        'connectTimeoutMS': int(os.getenv('WILSY_KENNEL_DB_CONNECT_TIMEOUT_MS', 30000)),
        'socketTimeoutMS': int(os.getenv('WILSY_KENNEL_DB_SOCKET_TIMEOUT_MS', 45000)),
        'serverSelectionTimeoutMS': int(os.getenv('WILSY_KENNEL_DB_SERVER_SELECTION_MS', 5000)),
        'maxPoolSize': 50,
        # Hotspot development: do not continuously replenish ten sockets per
        # server when connectivity is unstable; production retains its baseline.
        'minPoolSize': 10 if _is_production_environment() else 0,
        'maxIdleTimeMS': 60000,
        'retryWrites': True,
        'retryReads': True,
    }
    if options['tls']:
        options['tlsAllowInvalidCertificates'] = False
        options['tlsAllowInvalidHostnames'] = False

    local_client = None
    try:
        logger.info("[KENNEL_DB] 📡 Initiating explicit replica set link...")
        if _mongo_timing_is_enabled():
            _MONGO_TIMING_LISTENER.configure_pool_capacity(options["maxPoolSize"])
            options["event_listeners"] = [_MONGO_TIMING_LISTENER, _MONGO_HEARTBEAT_LISTENER]
        local_client = MongoClient(uri, **options)
        # Force a ping to verify connectivity
        local_client.admin.command('ping')
        database = local_client.get_database()  # Uses the database from the URI
        with _state_lock:
            previous_client = _client
            _client = local_client
            _db = database
            _ready = True
            _last_error = None
        if previous_client is not None and previous_client is not local_client:
            previous_client.close()
        logger.info("[KENNEL_DB] ✅ Replica set linked. Persistence ONLINE.")
        return True, "Connected successfully"
    except errors.ServerSelectionTimeoutError as e:
        if local_client is not None:
            local_client.close()
        with _state_lock:
            _last_error = e
            _ready = False
        logger.error(f"[KENNEL_DB] ⚠️ REPLICA LINK SEVERED — Kennel will run DEGRADED.")
        logger.error(f"[KENNEL_DB] Atlas checklist: Network Access → Verify IP whitelist.")
        logger.error(f"[KENNEL_DB] Detail: {str(e)[:240]}")
        return False, f"ServerSelectionTimeoutError: {str(e)[:200]}"
    except Exception as e:
        if local_client is not None:
            local_client.close()
        with _state_lock:
            _last_error = e
            _ready = False
        logger.error(f"[KENNEL_DB] ⚠️ Connection error: {str(e)[:240]}")
        return False, f"Connection error: {str(e)[:200]}"


# ─── Self-Healing Background Retry ──────────────────────────────────────
def _background_reanchor():
    """Retry explicitly requested by a runtime owner until stopped."""
    global _retry_thread, _retry_stop
    stop_event = _retry_stop
    if stop_event is None:
        return
    while not stop_event.is_set() and not is_db_ready():
        logger.warning("[KENNEL_DB] 📡 Explicit background re-anchor attempt...")
        success, _ = connect_db(force_reconnect=True)
        if success:
            break
        stop_event.wait(RETRY_DELAY_MS / 1000.0)
    with _state_lock:
        _retry_thread = None
        _retry_stop = None

# Background retry is opt-in and owned by the caller; imports never start it.
def start_background_reanchor():
    """Start one explicitly owned retry worker; import never invokes this."""
    global _retry_thread, _retry_stop
    with _state_lock:
        if _ready or (_retry_thread is not None and _retry_thread.is_alive()):
            return False
        _retry_stop = threading.Event()
        _retry_thread = threading.Thread(
            target=_background_reanchor,
            name="wilsy-kernel-db-reanchor",
            daemon=True,
        )
        _retry_thread.start()
        return True


def stop_background_reanchor(timeout=2.0):
    """Stop an explicitly owned retry worker within a bounded timeout."""
    global _retry_thread, _retry_stop
    with _state_lock:
        thread = _retry_thread
        stop_event = _retry_stop
        if stop_event is not None:
            stop_event.set()
    if thread is not None:
        thread.join(timeout=max(0.0, float(timeout)))
    with _state_lock:
        stopped = _retry_thread is None or not _retry_thread.is_alive()
        if stopped:
            _retry_thread = None
            _retry_stop = None
        return stopped

# ─── Convenience exports ────────────────────────────────────────────────
def disconnect_db():
    """Gracefully close the connection."""
    global _client, _db, _ready, _last_error
    stop_background_reanchor()
    with _state_lock:
        client = _client
        _client = None
        _db = None
        _ready = False
        _last_error = None
    if client:
        try:
            client.close()
            logger.info("[KENNEL_DB] Sovereign Database link gracefully severed.")
        except Exception as e:
            logger.error(f"[KENNEL_DB] Disconnect error: {e}")

# ─── Default export (for simplicity) ────────────────────────────────────
__all__ = [
    'connect_db', 'disconnect_db', 'get_database', 'get_client',
    'is_db_ready', 'get_db_status', 'start_background_reanchor',
    'stop_background_reanchor', 'resolve_mongo_uri',
]

# ARTIFACT: tools/eos/kernel/db.py
# VERSION: v2.7.1-POOL-OPTION-RESTORATION
# AUTHORITY BOUNDARY: Explicit database lifecycle only; no business authority.
# TENANT POSTURE: Database accessors do not bypass caller tenant predicates.
# FAIL-CLOSED POSTURE: Unavailable persistence is reported explicitly.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
