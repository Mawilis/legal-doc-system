"""WILSY OS — durable platform billing release-authorization registry.

TITLE: Platform Billing Release Authorization Registry
VERSION: v1.1.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-REGISTRY
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Persist immutable tenant-scoped release evidence with strict replay and corruption handling.
EPITOME: Durable evidence only; no approval, payment, execution, or settlement authority.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/billing/platform_billing_release_authorization_registry.py
COLLABORATION / OWNERSHIP: Python EOS / Wilsy OS Core Engineering
CERTIFICATION / UPDATE DATE: 2026-09-04
CHANGELOG: v1.1.0 defers kernel database import until explicit-collection fallback is required.
COMPLIANCE: POPIA §19 | GDPR Article 32 | SOC2 CC7.2
SECURITY / PRIVACY: No raw payment instruments, credentials, provider or execution data.
TENANT BOUNDARY: Every identity and idempotency lookup includes tenant_id.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution and settlement.
TRANSACTION BOUNDARY: Caller-owned sessions are propagated and never committed or aborted here.
"""
from __future__ import annotations
import hashlib, hmac, json, re
from dataclasses import dataclass
from typing import Any, Optional
from pymongo import ASCENDING, WriteConcern
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from ..domain.platform_billing_release_authorization import PlatformBillingReleaseAuthorization, PlatformBillingReleaseAuthorizationDomainError

VERSION = "v1.1.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-REGISTRY"
SCHEMA = "WILSY-PLATFORM-BILLING-RELEASE-AUTHORIZATION/V2"
COLLECTION = "platform_billing_release_authorizations"
_WC = WriteConcern(w="majority", j=True, wtimeout=10000)
_RC = ReadConcern("majority")

class PlatformBillingReleaseAuthorizationRegistryError(RuntimeError): pass
class PlatformBillingReleaseAuthorizationNotFoundError(PlatformBillingReleaseAuthorizationRegistryError): pass
class PlatformBillingReleaseAuthorizationPersistedRecordInvalidError(PlatformBillingReleaseAuthorizationRegistryError): pass
class PlatformBillingReleaseAuthorizationIdempotencyConflictError(PlatformBillingReleaseAuthorizationRegistryError): pass
class PlatformBillingReleaseAuthorizationIdentityConflictError(PlatformBillingReleaseAuthorizationRegistryError): pass

@dataclass(frozen=True)
class CreateResult:
    authorization: PlatformBillingReleaseAuthorization
    replayed: bool

def _collection(collection: Optional[Collection] = None) -> Collection:
    if collection is not None: return collection.with_options(write_concern=_WC, read_concern=_RC)
    from ...kernel.db import get_database
    database = get_database()
    if database is None: raise PlatformBillingReleaseAuthorizationRegistryError("PLATFORM_RELEASE_AUTHORIZATION_PERSISTENCE_UNAVAILABLE")
    return database[COLLECTION].with_options(write_concern=_WC, read_concern=_RC)

def _fingerprint(authorization: PlatformBillingReleaseAuthorization) -> str:
    raw = json.dumps(authorization.to_persistence_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return hashlib.sha3_512(raw).hexdigest()

def _hydrate(document: dict[str, Any]) -> PlatformBillingReleaseAuthorization:
    try:
        body = dict(document)
        body.pop("_id", None)
        stored = body.get("release_authorization_fingerprint")
        if not isinstance(stored, str) or re.fullmatch(r"[0-9a-f]{128}", stored) is None: raise ValueError("fingerprint")
        value = PlatformBillingReleaseAuthorization.from_persistence_dict(body)
        if not hmac.compare_digest(stored, value.release_authorization_fingerprint): raise ValueError("integrity")
        if value.release_authorization_fingerprint != stored: raise ValueError("domain fingerprint")
        return value
    except (KeyError, TypeError, ValueError, PlatformBillingReleaseAuthorizationDomainError) as error:
        raise PlatformBillingReleaseAuthorizationPersistedRecordInvalidError("PLATFORM_RELEASE_AUTHORIZATION_PERSISTED_RECORD_INVALID") from error

class PlatformBillingReleaseAuthorizationRegistry:
    """Tenant-scoped durable immutable evidence boundary."""
    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        target = _collection(collection)
        target.create_index([("tenant_id", ASCENDING), ("release_authorization_id", ASCENDING)], unique=True, name="tenant_release_authorization_unique")
        target.create_index([("tenant_id", ASCENDING), ("idempotency_key", ASCENDING)], unique=True, name="tenant_release_authorization_idempotency_unique")

    @staticmethod
    def create(authorization: PlatformBillingReleaseAuthorization, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> CreateResult:
        if not isinstance(authorization, PlatformBillingReleaseAuthorization): raise PlatformBillingReleaseAuthorizationRegistryError("authorization is invalid")
        target = _collection(collection); PlatformBillingReleaseAuthorizationRegistry.ensure_indexes(target)
        document = authorization.to_persistence_dict()
        existing = target.find_one({"tenant_id": authorization.tenant_id, "idempotency_key": authorization.idempotency_key}, session=session) if session is not None else None
        if existing is not None:
            persisted = _hydrate(existing)
            if hmac.compare_digest(persisted.release_authorization_fingerprint, authorization.release_authorization_fingerprint):
                return CreateResult(persisted, True)
            raise PlatformBillingReleaseAuthorizationIdempotencyConflictError("PLATFORM_RELEASE_AUTHORIZATION_IDEMPOTENCY_CONFLICT")
        try:
            target.insert_one(document, session=session)
            return CreateResult(authorization, False)
        except DuplicateKeyError as error:
            existing = target.find_one({"tenant_id": authorization.tenant_id, "idempotency_key": authorization.idempotency_key}, session=session)
            if existing is not None:
                persisted = _hydrate(existing)
                if hmac.compare_digest(persisted.release_authorization_fingerprint, authorization.release_authorization_fingerprint): return CreateResult(persisted, True)
                raise PlatformBillingReleaseAuthorizationIdempotencyConflictError("PLATFORM_RELEASE_AUTHORIZATION_IDEMPOTENCY_CONFLICT") from error
            existing = target.find_one({"tenant_id": authorization.tenant_id, "release_authorization_id": authorization.release_authorization_id}, session=session)
            if existing is not None:
                _hydrate(existing)
                raise PlatformBillingReleaseAuthorizationIdentityConflictError("PLATFORM_RELEASE_AUTHORIZATION_IDENTITY_CONFLICT") from error
            raise PlatformBillingReleaseAuthorizationRegistryError("PLATFORM_RELEASE_AUTHORIZATION_UNCLASSIFIED_DUPLICATE") from error
        except PyMongoError as error: raise PlatformBillingReleaseAuthorizationRegistryError("PLATFORM_RELEASE_AUTHORIZATION_PERSISTENCE_UNAVAILABLE") from error

    @staticmethod
    def get(tenant_id: str, release_authorization_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> PlatformBillingReleaseAuthorization:
        target = _collection(collection)
        try: document = target.find_one({"tenant_id": tenant_id, "release_authorization_id": release_authorization_id}, session=session)
        except PyMongoError as error: raise PlatformBillingReleaseAuthorizationRegistryError("PLATFORM_RELEASE_AUTHORIZATION_PERSISTENCE_UNAVAILABLE") from error
        if document is None: raise PlatformBillingReleaseAuthorizationNotFoundError("PLATFORM_RELEASE_AUTHORIZATION_NOT_FOUND")
        return _hydrate(document)

__all__ = ["PlatformBillingReleaseAuthorizationRegistry", "PlatformBillingReleaseAuthorizationRegistryError", "PlatformBillingReleaseAuthorizationNotFoundError", "PlatformBillingReleaseAuthorizationPersistedRecordInvalidError", "PlatformBillingReleaseAuthorizationIdempotencyConflictError", "PlatformBillingReleaseAuthorizationIdentityConflictError", "CreateResult", "VERSION"]
# ARTIFACT: platform_billing_release_authorization_registry.py
# VERSION: v1.1.0-PLATFORM-BILLING-RELEASE-AUTHORIZATION-REGISTRY
# AUTHORITY BOUNDARY: durable release evidence only; no execution or settlement
# TENANT POSTURE: tenant-scoped identities and idempotency
# SECURITY / PRIVACY POSTURE: no raw payment instruments, credentials, or provider secrets
# FAIL-CLOSED DECLARATION: invalid records, persistence failures, and replay conflicts fail closed
# FAIL-CLOSED POSTURE: corruption, conflict, absence, and outage are explicit
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
