# -*- coding: utf-8 -*-
"""
===============================================================================
EPITOME: WILSY OS - SOVEREIGN KENNEL DATABASE ANCHOR (ATLAS-RESILIENT)
STANDARD: BIBLICAL WORTH BILLIONS NO CHILD'S PLACE
===============================================================================
File:           tools/eos/kernel/db.py
Version:        v2.2.0-R1D-B0F-B3B-R0-CANONICAL-URI
Authority:      Wilsy OS Core Governance
Classification: Production Artifact (Zero-Downtime Architecture)
CHANGELOG: v2.2.0-R1D-B0F-B3B-R0-CANONICAL-URI makes MONGODB_URI the sole
            database authority, blocks repository dotenv rescue in production,
            and preserves explicit caller-owned lifecycle semantics.

COLLABORATION COMMENTS:
- @Wilson: Added conditional TLS options for development to bypass SSL
  handshake errors without compromising production security.
- @WilsyOS: TLS options are enabled only when ENV != 'production'.
- @WilsyOS: Connection and retry lifecycle is now explicit and import-inert;
  API startup owns connect/disconnect and no thread is created implicitly.

Forensic Relationships:
  Upstream:   kennel.py, billing_registry.py, all SaaS modules
  Downstream: All Mongoose/PyMongo models and collections
===============================================================================
"""

import logging
import os
import threading
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, errors

logger = logging.getLogger(__name__)

# The kernel is launched directly by the root development command, so it does
# not inherit Node's dotenv bootstrap. Repository dotenv is a development/test
# convenience only; production must receive MONGODB_URI from deployment.
_REPOSITORY_ENV_PATH = Path(__file__).resolve().parents[3] / ".env"


def _is_production_environment() -> bool:
    """Return whether deployment configuration is explicitly production."""
    return os.getenv("ENV", "").strip().lower() in {"production", "prod"}


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

    # Determine environment
    is_dev = not _is_production_environment()

    # PyMongo connection options.  Local certification Mongo is deliberately
    # non-TLS; Atlas and production remain TLS-first unless explicitly opted
    # out by a controlled environment setting.
    options = {
        'tls': (
            os.getenv('WILSY_KENNEL_DB_TLS', '').strip().lower() in {'1', 'true', 'yes', 'on'}
            if os.getenv('WILSY_KENNEL_DB_TLS') is not None
            else (uri.startswith('mongodb+srv://') or not is_dev)
        ),
        'connectTimeoutMS': int(os.getenv('WILSY_KENNEL_DB_CONNECT_TIMEOUT_MS', 30000)),
        'socketTimeoutMS': int(os.getenv('WILSY_KENNEL_DB_SOCKET_TIMEOUT_MS', 45000)),
        'serverSelectionTimeoutMS': int(os.getenv('WILSY_KENNEL_DB_SERVER_SELECTION_MS', 5000)),
        'maxPoolSize': 50,
        'minPoolSize': 10,
        'maxIdleTimeMS': 60000,
        'retryWrites': True,
        'retryReads': True,
    }
    if options['tls']:
        options['tlsAllowInvalidCertificates'] = is_dev
        options['tlsAllowInvalidHostnames'] = is_dev

    local_client = None
    try:
        logger.info("[KENNEL_DB] 📡 Initiating explicit replica set link...")
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
# VERSION: v2.2.0-R1D-B0F-B3B-R0-CANONICAL-URI
# AUTHORITY BOUNDARY: Explicit database lifecycle only; no business authority.
# TENANT POSTURE: Database accessors do not bypass caller tenant predicates.
# FAIL-CLOSED POSTURE: Unavailable persistence is reported explicitly.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
