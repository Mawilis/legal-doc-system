"""TITLE: WILSY OS Tenant Business-Role Repository.
VERSION: v1.0.0-TENANT-BUSINESS-ROLE-REPOSITORY
AUTHORITY: Durable persistence and CAS for tenant business-role facts only.
EPITOME: Stores one explicit principal/tenant business-role snapshot.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_business_role_repository.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-05.
CHANGELOG: v1.0.0 establishes isolated Mongo persistence for F1A values.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Queries always require exact principal_id and tenant_id.
AUTHORITY BOUNDARY: Persistence only; no authorization or policy decisions.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
TRANSACTION BOUNDARY: Caller owns optional ClientSession and transactions.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Mapping, Optional, cast
from pymongo import ASCENDING
from bson.codec_options import CodecOptions
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError
from tools.eos.auth.tenant_business_role import TenantBusinessRoleAuthority, TenantBusinessRoleStatus

VERSION = "v1.0.0-TENANT-BUSINESS-ROLE-REPOSITORY"
COLLECTION = "tenant_business_roles"

class TenantBusinessRoleRepositoryError(RuntimeError): pass
class TenantBusinessRoleAlreadyExistsError(TenantBusinessRoleRepositoryError): pass
class TenantBusinessRoleNotFoundError(TenantBusinessRoleRepositoryError): pass
class TenantBusinessRoleRevisionConflictError(TenantBusinessRoleRepositoryError): pass
class TenantBusinessRolePersistedRecordInvalidError(TenantBusinessRoleRepositoryError): pass

def _target(collection: Optional[Collection]) -> Collection:
    if collection is not None:
        if isinstance(collection, Collection):
            return collection.with_options(codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc))
        return collection
    from tools.eos.kernel.db import get_database
    database = get_database()
    if database is None: raise TenantBusinessRoleRepositoryError("TENANT_BUSINESS_ROLE_PERSISTENCE_UNAVAILABLE")
    return database.get_collection(COLLECTION, codec_options=CodecOptions(tz_aware=True, tzinfo=timezone.utc))

def _document(value: TenantBusinessRoleAuthority) -> dict[str, object]:
    return {"principal_id": value.principal_id, "tenant_id": value.tenant_id, "business_role": value.business_role, "status": value.status.value, "revision": value.revision, "effective_at": value.effective_at, "revoked_at": value.revoked_at}

def _aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("persisted timestamp must be timezone-aware")
    return value

def _hydrate(document: Mapping[str, object]) -> TenantBusinessRoleAuthority:
    try:
        value = TenantBusinessRoleAuthority(cast(str, document["principal_id"]), cast(str, document["tenant_id"]), cast(str, document["business_role"]), TenantBusinessRoleStatus(cast(str, document["status"])), cast(int, document["revision"]), _aware(cast(datetime, document["effective_at"])), None if document.get("revoked_at") is None else _aware(cast(datetime, document["revoked_at"])))
        return value
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        raise TenantBusinessRolePersistedRecordInvalidError("TENANT_BUSINESS_ROLE_PERSISTED_RECORD_INVALID") from error

class TenantBusinessRoleRepository:
    """Persist and resolve current business-role facts without owning transactions."""
    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        _target(collection).create_index([('principal_id', ASCENDING), ('tenant_id', ASCENDING)], unique=True, name='principal_tenant_business_role_unique')
    @staticmethod
    def insert(value: TenantBusinessRoleAuthority, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> TenantBusinessRoleAuthority:
        if not isinstance(value, TenantBusinessRoleAuthority): raise TenantBusinessRoleRepositoryError("TENANT_BUSINESS_ROLE_INSERT_INVALID")
        try: _target(collection).insert_one(_document(value), session=session); return value
        except DuplicateKeyError as error: raise TenantBusinessRoleAlreadyExistsError("TENANT_BUSINESS_ROLE_ALREADY_EXISTS") from error
        except PyMongoError as error: raise TenantBusinessRoleRepositoryError("TENANT_BUSINESS_ROLE_INSERT_FAILED") from error
    @staticmethod
    def resolve(principal_id: str, tenant_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> TenantBusinessRoleAuthority:
        if not all(isinstance(v, str) and v == v.strip() and v for v in (principal_id, tenant_id)): raise TenantBusinessRoleNotFoundError("TENANT_BUSINESS_ROLE_NOT_FOUND")
        try: row = _target(collection).find_one({'principal_id': principal_id, 'tenant_id': tenant_id}, session=session)
        except PyMongoError as error: raise TenantBusinessRoleRepositoryError("TENANT_BUSINESS_ROLE_READ_FAILED") from error
        if row is None: raise TenantBusinessRoleNotFoundError("TENANT_BUSINESS_ROLE_NOT_FOUND")
        return _hydrate(row)
    @staticmethod
    def compare_and_swap(value: TenantBusinessRoleAuthority, expected_revision: int, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> TenantBusinessRoleAuthority:
        if not isinstance(expected_revision, int) or isinstance(expected_revision, bool) or expected_revision < 0 or value.revision != expected_revision + 1: raise TenantBusinessRoleRevisionConflictError("TENANT_BUSINESS_ROLE_REVISION_CONFLICT")
        try: result = _target(collection).replace_one({'principal_id': value.principal_id, 'tenant_id': value.tenant_id, 'revision': expected_revision}, _document(value), upsert=False, session=session)
        except PyMongoError as error: raise TenantBusinessRoleRepositoryError("TENANT_BUSINESS_ROLE_UPDATE_FAILED") from error
        if result.matched_count != 1: raise TenantBusinessRoleRevisionConflictError("TENANT_BUSINESS_ROLE_REVISION_CONFLICT")
        return value

__all__ = ['COLLECTION','VERSION','TenantBusinessRoleRepository','TenantBusinessRoleRepositoryError','TenantBusinessRoleAlreadyExistsError','TenantBusinessRoleNotFoundError','TenantBusinessRoleRevisionConflictError','TenantBusinessRolePersistedRecordInvalidError']
# ARTIFACT: tenant_business_role_repository.py
# VERSION: v1.0.0-TENANT-BUSINESS-ROLE-REPOSITORY
# AUTHORITY BOUNDARY: business-role persistence and CAS only
# TENANT POSTURE: exact principal/tenant scope
# FAIL-CLOSED POSTURE: malformed, duplicate, unavailable, and stale states reject
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
