"""Durable Mongo repository for current tenant membership authority snapshots.

TITLE: WILSY OS Tenant Membership Repository
VERSION: v1.0.0-WILSY-TENANT-MEMBERSHIP-REPOSITORY
AUTHORITY: Persistence, resolution, and revision CAS for tenant membership only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/tenant_membership_repository.py
CERTIFICATION/UPDATE DATE: 2026-08-29
CHANGELOG: v1.0.0 establishes compound-key membership persistence with caller-owned sessions.
COMPLIANCE: Deterministic serialization, unique identity, strict hydration, and no transition policy.
SECURITY/PRIVACY POSTURE: Stores only principal_id, tenant_id, status, and revision.
TENANT BOUNDARY: Every operation resolves the explicit principal/tenant pair.
AUTHORITY BOUNDARY: Does not own lifecycle policy, principal authority, roles, credentials, or membership administration.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial execution authority.

Epitome:
    A narrow persistence seam for the natural membership key
    (principal_id, tenant_id). Callers own sessions and transactions.

Biblical Anchor:
    "And he shall be like a tree planted by the rivers of water..." — Psalm 1:3

Collaboration & Ownership:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    AI Collaborator: Core Systems Engineering Agent
    File Path: tools/eos/auth/tenant_membership_repository.py
"""
from __future__ import annotations
from typing import Mapping, Optional
from pymongo import ASCENDING
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError
from tools.eos.auth.tenant_membership import TenantMembershipAuthority, TenantMembershipStatus

COLLECTION = "tenant_memberships"

class TenantMembershipRepositoryError(RuntimeError):
    """Base fail-closed repository error."""
class TenantMembershipNotFoundError(TenantMembershipRepositoryError):
    """No membership exists for the requested pair."""
class TenantMembershipAlreadyExistsError(TenantMembershipRepositoryError):
    """The natural membership pair already exists."""
class TenantMembershipRevisionConflictError(TenantMembershipRepositoryError):
    """The expected revision was stale or the next snapshot was invalid."""
class TenantMembershipPersistedRecordInvalidError(TenantMembershipRepositoryError):
    """Persisted membership data failed strict hydration validation."""

def _target(collection: Optional[Collection]) -> Collection:
    """Resolve an injected collection without owning persistence lifecycle."""
    if collection is not None: return collection
    from tools.eos.kernel.db import get_database
    database = get_database()
    if database is None: raise TenantMembershipRepositoryError("TENANT_MEMBERSHIP_PERSISTENCE_UNAVAILABLE")
    return database[COLLECTION]

def _document(value: TenantMembershipAuthority) -> dict[str, object]:
    """Serialize exactly the four canonical membership fields."""
    return {"principal_id": value.principal_id, "tenant_id": value.tenant_id, "status": value.status.value, "revision": value.revision}

def _hydrate(document: Mapping[str, object]) -> TenantMembershipAuthority:
    """Hydrate persisted state and reject malformed authority."""
    try:
        principal_id, tenant_id, status, revision = (document["principal_id"], document["tenant_id"], document["status"], document["revision"])
        if not isinstance(principal_id, str) or not isinstance(tenant_id, str) or not isinstance(status, str) or not isinstance(revision, int) or isinstance(revision, bool): raise TypeError("invalid persisted membership")
        return TenantMembershipAuthority(principal_id, tenant_id, TenantMembershipStatus(status), revision)
    except (KeyError, TypeError, ValueError) as error:
        raise TenantMembershipPersistedRecordInvalidError("TENANT_MEMBERSHIP_PERSISTED_RECORD_INVALID") from error

class TenantMembershipRepository:
    """Persist and resolve membership snapshots without transition authority."""
    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        """Create the deterministic unique compound natural-key index."""
        _target(collection).create_index([ ("principal_id", ASCENDING), ("tenant_id", ASCENDING) ], unique=True, name="principal_tenant_membership_unique")

    @staticmethod
    def insert(value: TenantMembershipAuthority, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> TenantMembershipAuthority:
        """Insert one snapshot without implicit overwrite or upsert."""
        if not isinstance(value, TenantMembershipAuthority): raise TenantMembershipRepositoryError("TENANT_MEMBERSHIP_INSERT_INVALID")
        try: _target(collection).insert_one(_document(value), session=session); return value
        except DuplicateKeyError as error: raise TenantMembershipAlreadyExistsError("TENANT_MEMBERSHIP_ALREADY_EXISTS") from error
        except PyMongoError as error: raise TenantMembershipRepositoryError("TENANT_MEMBERSHIP_INSERT_FAILED") from error

    @staticmethod
    def resolve(principal_id: str, tenant_id: str, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> TenantMembershipAuthority:
        """Resolve exact natural-key membership or raise explicit absence."""
        if not isinstance(principal_id, str) or not isinstance(tenant_id, str) or not principal_id or not tenant_id: raise TenantMembershipNotFoundError("TENANT_MEMBERSHIP_NOT_FOUND")
        try: row = _target(collection).find_one({"principal_id": principal_id, "tenant_id": tenant_id}, session=session)
        except PyMongoError as error: raise TenantMembershipRepositoryError("TENANT_MEMBERSHIP_READ_FAILED") from error
        if row is None: raise TenantMembershipNotFoundError("TENANT_MEMBERSHIP_NOT_FOUND")
        return _hydrate(row)

    @staticmethod
    def compare_and_swap(value: TenantMembershipAuthority, expected_revision: int, collection: Optional[Collection] = None, *, session: Optional[ClientSession] = None) -> TenantMembershipAuthority:
        """Replace only matching natural key/revision with exactly revision+1."""
        if not isinstance(expected_revision, int) or isinstance(expected_revision, bool) or expected_revision < 0 or value.revision != expected_revision + 1: raise TenantMembershipRevisionConflictError("TENANT_MEMBERSHIP_REVISION_CONFLICT")
        try: result = _target(collection).replace_one({"principal_id": value.principal_id, "tenant_id": value.tenant_id, "revision": expected_revision}, _document(value), upsert=False, session=session)
        except PyMongoError as error: raise TenantMembershipRepositoryError("TENANT_MEMBERSHIP_UPDATE_FAILED") from error
        if result.matched_count != 1: raise TenantMembershipRevisionConflictError("TENANT_MEMBERSHIP_REVISION_CONFLICT")
        return value

__all__ = ["COLLECTION", "TenantMembershipAlreadyExistsError", "TenantMembershipNotFoundError", "TenantMembershipPersistedRecordInvalidError", "TenantMembershipRepository", "TenantMembershipRepositoryError", "TenantMembershipRevisionConflictError"]

# ARTIFACT: tenant_membership_repository.py
# VERSION: v1.0.0-WILSY-TENANT-MEMBERSHIP-REPOSITORY
# AUTHORITY BOUNDARY: durable membership persistence and revision CAS only
# TENANT POSTURE: explicit compound principal/tenant key
# FAIL-CLOSED POSTURE: duplicates, absence, corruption, database failures, and stale writes are explicit
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
