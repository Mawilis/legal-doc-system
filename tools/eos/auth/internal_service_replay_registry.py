"""WILSY OS Internal Service Replay Registry

TITLE: WILSY OS Internal Service Replay Registry
VERSION: v1.0.0-WILSY-INTERNAL-SERVICE-REPLAY
AUTHORITY: Internal service replay persistence only.
EPITOME: Atomically reserves signed service nonces using Mongo uniqueness.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/internal_service_replay_registry.py
COLLABORATION / OWNERSHIP: EOS trust verifier consumes ReplayStore semantics.
CERTIFICATION/UPDATE DATE: 2026-08-30
CHANGELOG: v1.0.0-WILSY-INTERNAL-SERVICE-REPLAY - atomic nonce registry.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No user, tenant, credential, or secret fields persist.
TENANT BOUNDARY: None.
AUTHORITY BOUNDARY: Replay persistence only.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Optional
from pymongo import ASCENDING
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

VERSION = "v1.0.0-WILSY-INTERNAL-SERVICE-REPLAY"
COLLECTION = "internal_service_replay_nonces"

class ReplayRegistryError(RuntimeError): """Bounded persistence failure."""
class ReplayRegistryConfigurationError(ReplayRegistryError): """Invalid provider or input."""

def _target(collection: Optional[Collection]) -> Collection:
    if collection is not None: return collection
    try:
        from tools.eos.kernel.db import get_database
        db = get_database()
    except Exception as error:
        raise ReplayRegistryConfigurationError("REPLAY_REGISTRY_PROVIDER_UNAVAILABLE") from error
    if db is None: raise ReplayRegistryConfigurationError("REPLAY_REGISTRY_PROVIDER_UNAVAILABLE")
    return db[COLLECTION]

class InternalServiceReplayRegistry:
    """Mongo-backed atomic ReplayStore implementation."""
    def __init__(self, collection: Optional[Collection] = None, *, now: Optional[datetime] = None) -> None:
        self._collection = collection
        self._now = now

    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        target = _target(collection)
        try:
            target.create_index([('service_id', ASCENDING), ('key_id', ASCENDING), ('nonce', ASCENDING)], unique=True, name='internal_service_replay_identity_unique')
            target.create_index([('expires_at', ASCENDING)], expireAfterSeconds=0, name='internal_service_replay_expiry_ttl')
        except PyMongoError as error: raise ReplayRegistryError("REPLAY_REGISTRY_INDEX_FAILED") from error

    def consume_once(self, *, service_id: str, key_id: str, nonce: str, expires_at: int) -> bool:
        if not all(isinstance(value, str) and value for value in (service_id, key_id, nonce)) or not isinstance(expires_at, int) or isinstance(expires_at, bool) or expires_at <= 0:
            raise ReplayRegistryConfigurationError("REPLAY_REGISTRY_INPUT_INVALID")
        document = {'service_id': service_id, 'key_id': key_id, 'nonce': nonce, 'expires_at': datetime.fromtimestamp(expires_at, timezone.utc), 'created_at': self._now or datetime.now(timezone.utc)}
        try:
            _target(self._collection).insert_one(document)
            return True
        except DuplicateKeyError:
            return False
        except PyMongoError as error:
            raise ReplayRegistryError("REPLAY_REGISTRY_PERSISTENCE_FAILED") from error

# ARTIFACT: internal_service_replay_registry.py
# VERSION: v1.0.0-WILSY-INTERNAL-SERVICE-REPLAY
# AUTHORITY BOUNDARY: Internal service replay persistence only.
# TENANT POSTURE: No tenant authority.
# FAIL-CLOSED POSTURE: Duplicate claims deny; persistence/configuration failures raise.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
