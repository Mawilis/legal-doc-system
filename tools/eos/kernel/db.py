# -*- coding: utf-8 -*-
"""
===============================================================================
EPITOME: WILSY OS - SOVEREIGN KENNEL DATABASE ANCHOR (ATLAS-RESILIENT)
STANDARD: BIBLICAL WORTH BILLIONS NO CHILD'S PLACE
===============================================================================
File:           tools/eos/kernel/db.py
Version:        v2.0.0-TLS-FIX
Authority:      Wilsy OS Core Governance
Classification: Production Artifact (Zero-Downtime Architecture)

COLLABORATION COMMENTS:
- @Wilson: Added conditional TLS options for development to bypass SSL
  handshake errors without compromising production security.
- @WilsyOS: TLS options are enabled only when ENV != 'production'.

Forensic Relationships:
  Upstream:   kennel.py, billing_registry.py, all SaaS modules
  Downstream: All Mongoose/PyMongo models and collections
===============================================================================
"""

import os
import logging
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, errors

logger = logging.getLogger(__name__)

# The kernel is launched directly by the root development command, so it does
# not inherit Node's dotenv bootstrap.  Load the repository environment before
# resolving persistence configuration; never overwrite deployment-provided
# values.
load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=False)

# --- Configuration ---
MAX_RETRY_ATTEMPTS = int(os.getenv('WILSY_KENNEL_DB_MAX_RETRIES', 5))
RETRY_DELAY_MS = int(os.getenv('WILSY_KENNEL_DB_RETRY_MS', 5000))

# --- State ---
_client = None
_db = None
_ready = False
_last_error = None


def resolve_mongo_uri():
    """Resolve MongoDB URI from environment variables."""
    uri = (
        os.getenv('MONGODB_URI') or
        os.getenv('MONGO_URI') or
        os.getenv('DATABASE_URL') or
        os.getenv('WILSY_MONGO_URI') or
        ''
    )
    return str(uri).strip()


def get_db_status():
    """Return diagnostic snapshot."""
    return {
        'ready': _ready,
        'client_created': _client is not None,
        'database_name': _db.name if _db is not None else None,
        'last_error': str(_last_error) if _last_error else None,
    }


def is_db_ready():
    """Return True if the database is connected and ready."""
    return _ready and _client is not None


def get_database():
    """Return the MongoDB database instance."""
    return _db


def get_client():
    """Return the MongoDB client instance."""
    return _client


def connect_db(force_reconnect=False):
    """
    Sovereign Atlas connector for the Kennel. Resolves even if offline;
    the Kennel will start in DEGRADED mode and retry in the background.
    Returns (success: bool, message: str).
    """
    global _client, _db, _ready, _last_error

    if _ready and not force_reconnect:
        logger.info("[KENNEL_DB] Already connected and ready.")
        return True, "Already connected"

    uri = resolve_mongo_uri()
    if not uri:
        _last_error = "MONGODB_URI environment variable missing"
        logger.error("[KENNEL_DB] 💥 CRITICAL: No MONGODB_URI in environment.")
        return False, "MONGODB_URI missing"

    # Determine environment
    is_dev = os.getenv('ENV') != 'production'

    # PyMongo connection options – conditional TLS relaxation for development
    options = {
        'tls': True,
        'tlsAllowInvalidCertificates': is_dev,
        'tlsAllowInvalidHostnames': is_dev,
        'connectTimeoutMS': int(os.getenv('WILSY_KENNEL_DB_CONNECT_TIMEOUT_MS', 30000)),
        'socketTimeoutMS': int(os.getenv('WILSY_KENNEL_DB_SOCKET_TIMEOUT_MS', 45000)),
        'serverSelectionTimeoutMS': int(os.getenv('WILSY_KENNEL_DB_SERVER_SELECTION_MS', 5000)),
        'maxPoolSize': 50,
        'minPoolSize': 10,
        'maxIdleTimeMS': 60000,
        'retryWrites': True,
        'retryReads': True,
    }

    try:
        logger.info("[KENNEL_DB] 📡 Initiating Atlas replica set link...")
        _client = MongoClient(uri, **options)
        # Force a ping to verify connectivity
        _client.admin.command('ping')
        _db = _client.get_database()  # Uses the database from the URI
        _ready = True
        _last_error = None
        logger.info("[KENNEL_DB] ✅ Replica set linked. Persistence ONLINE.")
        return True, "Connected successfully"
    except errors.ServerSelectionTimeoutError as e:
        _last_error = e
        _ready = False
        logger.error(f"[KENNEL_DB] ⚠️ REPLICA LINK SEVERED — Kennel will run DEGRADED.")
        logger.error(f"[KENNEL_DB] Atlas checklist: Network Access → Verify IP whitelist.")
        logger.error(f"[KENNEL_DB] Detail: {str(e)[:240]}")
        return False, f"ServerSelectionTimeoutError: {str(e)[:200]}"
    except Exception as e:
        _last_error = e
        _ready = False
        logger.error(f"[KENNEL_DB] ⚠️ Connection error: {str(e)[:240]}")
        return False, f"Connection error: {str(e)[:200]}"


# ─── Self-Healing Background Retry ──────────────────────────────────────
import threading
import time

def _background_reanchor():
    """Background thread to retry connection indefinitely if not ready."""
    while not _ready:
        logger.warning("[KENNEL_DB] 📡 Background re-anchor attempt...")
        success, _ = connect_db(force_reconnect=True)
        if success:
            logger.info("[KENNEL_DB] ✅ Replica link restored automatically.")
            break
        time.sleep(RETRY_DELAY_MS / 1000.0)

# Start the background thread if connection fails initially
def start_background_reanchor():
    if not _ready:
        thread = threading.Thread(target=_background_reanchor, daemon=True)
        thread.start()
        logger.info("[KENNEL_DB] 🔄 Background re-anchor thread started.")


# ─── Initial connection attempt (non-blocking) ──────────────────────────
connect_db()
# If not ready, start background retry
if not _ready:
    start_background_reanchor()

# ─── Convenience exports ────────────────────────────────────────────────
def disconnect_db():
    """Gracefully close the connection."""
    global _client, _ready
    if _client:
        try:
            _client.close()
            logger.info("[KENNEL_DB] Sovereign Database link gracefully severed.")
        except Exception as e:
            logger.error(f"[KENNEL_DB] Disconnect error: {e}")
    _client = None
    _ready = False

# ─── Default export (for simplicity) ────────────────────────────────────
__all__ = [
    'connect_db', 'disconnect_db', 'get_database', 'get_client',
    'is_db_ready', 'get_db_status',
]
