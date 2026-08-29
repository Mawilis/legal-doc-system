"""TITLE: WILSY OS Role Assignment Repository.
VERSION: v1.0.1-WILSY-ROLE-ASSIGNMENT-REPOSITORY
AUTHORITY: Durable persistence, current resolution, and revision CAS for tenant-scoped role assignments only.
EPITOME: Mongo-backed repository for the current principal/tenant/role assignment snapshot keyed by the explicit governed natural authority key.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/role_assignment_repository.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-08-29.
CHANGELOG:
  v1.0.1-WILSY-ROLE-ASSIGNMENT-REPOSITORY: Sovereign structure hardening and repository contract certification preparation; no expansion into role, permission, principal, membership, authentication, authorization, or financial authority.
  v1.0.0-WILSY-ROLE-ASSIGNMENT-REPOSITORY: Established strict three-part natural-key persistence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Fail closed on unavailable persistence, malformed records, duplicate authority, invalid input, and revision conflict. Persist only authority identifiers, status, and revision required by the role-assignment contract.
TENANT BOUNDARY: Every role assignment is explicitly scoped to principal_id + tenant_id + role_id. No tenant inference, default tenant, global-root fallback, or cross-tenant lookup is permitted.
AUTHORITY BOUNDARY: Owns persistence, resolution, hydration, and revision CAS only. Does not own principal lifecycle, tenant membership, role definitions, permissions, credential truth, authentication, authorization policy, or financial execution.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

from typing import Mapping, Optional, cast

from pymongo import ASCENDING
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.role_assignment import RoleAssignmentAuthority, RoleAssignmentStatus

VERSION = "v1.0.1-WILSY-ROLE-ASSIGNMENT-REPOSITORY"
COLLECTION = "role_assignments"


class RoleAssignmentRepositoryError(RuntimeError):
    """Base failure for role-assignment persistence and resolution boundaries."""


class RoleAssignmentNotFoundError(RoleAssignmentRepositoryError):
    """Raised when no assignment exists for the requested natural key."""


class RoleAssignmentAlreadyExistsError(RoleAssignmentRepositoryError):
    """Raised when insertion conflicts with an existing natural-key authority."""


class RoleAssignmentRevisionConflictError(RoleAssignmentRepositoryError):
    """Raised when compare-and-swap cannot apply the expected revision."""


class RoleAssignmentPersistedRecordInvalidError(RoleAssignmentRepositoryError):
    """Raised when a persisted assignment cannot be safely hydrated."""


def _target(collection: Optional[Collection]) -> Collection:
    """Resolve an explicit collection or the configured database collection."""
    if collection is not None:
        return collection
    from tools.eos.kernel.db import get_database
    database = get_database()
    if database is None:
        raise RoleAssignmentRepositoryError("ROLE_ASSIGNMENT_PERSISTENCE_UNAVAILABLE")
    return database[COLLECTION]


def _document(value: RoleAssignmentAuthority) -> dict[str, object]:
    """Serialize one role assignment using its governed persisted shape."""
    return {
        "principal_id": value.principal_id,
        "tenant_id": value.tenant_id,
        "role_id": value.role_id,
        "status": value.status.value,
        "revision": value.revision,
    }


def _hydrate(document: Mapping[str, object]) -> RoleAssignmentAuthority:
    """Hydrate a persisted record and reject malformed authority state."""
    try:
        principal_id, tenant_id, role_id, status, revision = (
            document["principal_id"], document["tenant_id"], document["role_id"],
            document["status"], document["revision"],
        )
        if (
            not all(isinstance(item, str) for item in (principal_id, tenant_id, role_id, status))
            or not isinstance(revision, int)
            or isinstance(revision, bool)
        ):
            raise TypeError
        return RoleAssignmentAuthority(
            cast(str, principal_id), cast(str, tenant_id), cast(str, role_id),
            RoleAssignmentStatus(cast(str, status)), revision,
        )
    except (KeyError, TypeError, ValueError) as error:
        raise RoleAssignmentPersistedRecordInvalidError(
            "ROLE_ASSIGNMENT_PERSISTED_RECORD_INVALID"
        ) from error


class RoleAssignmentRepository:
    """Persist and resolve current role-assignment authority without owning transactions."""

    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        """Ensure the deterministic unique three-part natural-key index."""
        _target(collection).create_index(
            [("principal_id", ASCENDING), ("tenant_id", ASCENDING), ("role_id", ASCENDING)],
            unique=True,
            name="principal_tenant_role_assignment_unique",
        )

    @staticmethod
    def insert(
        value: RoleAssignmentAuthority,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> RoleAssignmentAuthority:
        """Insert revision-zero authority exactly once, preserving caller session ownership."""
        if not isinstance(value, RoleAssignmentAuthority) or value.revision != 0:
            raise RoleAssignmentRepositoryError("ROLE_ASSIGNMENT_INSERT_INVALID")
        try:
            _target(collection).insert_one(_document(value), session=session)
            return value
        except DuplicateKeyError as error:
            raise RoleAssignmentAlreadyExistsError("ROLE_ASSIGNMENT_ALREADY_EXISTS") from error
        except PyMongoError as error:
            raise RoleAssignmentRepositoryError("ROLE_ASSIGNMENT_INSERT_FAILED") from error

    @staticmethod
    def resolve(
        principal_id: str,
        tenant_id: str,
        role_id: str,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> RoleAssignmentAuthority:
        """Resolve the current assignment for an explicit principal/tenant/role key."""
        if not all(isinstance(item, str) and item for item in (principal_id, tenant_id, role_id)):
            raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")
        try:
            row = _target(collection).find_one(
                {"principal_id": principal_id, "tenant_id": tenant_id, "role_id": role_id},
                session=session,
            )
        except PyMongoError as error:
            raise RoleAssignmentRepositoryError("ROLE_ASSIGNMENT_READ_FAILED") from error
        if row is None:
            raise RoleAssignmentNotFoundError("ROLE_ASSIGNMENT_NOT_FOUND")
        return _hydrate(row)

    @staticmethod
    def compare_and_swap(
        value: RoleAssignmentAuthority,
        expected_revision: int,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> RoleAssignmentAuthority:
        """Advance exactly one revision using compare-and-swap on the natural key."""
        if (
            not isinstance(expected_revision, int)
            or isinstance(expected_revision, bool)
            or expected_revision < 0
            or value.revision != expected_revision + 1
        ):
            raise RoleAssignmentRevisionConflictError("ROLE_ASSIGNMENT_REVISION_CONFLICT")
        try:
            result = _target(collection).replace_one(
                {
                    "principal_id": value.principal_id,
                    "tenant_id": value.tenant_id,
                    "role_id": value.role_id,
                    "revision": expected_revision,
                },
                _document(value),
                upsert=False,
                session=session,
            )
        except PyMongoError as error:
            raise RoleAssignmentRepositoryError("ROLE_ASSIGNMENT_UPDATE_FAILED") from error
        if result.matched_count != 1:
            raise RoleAssignmentRevisionConflictError("ROLE_ASSIGNMENT_REVISION_CONFLICT")
        return value


__all__ = [
    "COLLECTION",
    "RoleAssignmentAlreadyExistsError",
    "RoleAssignmentNotFoundError",
    "RoleAssignmentPersistedRecordInvalidError",
    "RoleAssignmentRepository",
    "RoleAssignmentRepositoryError",
    "RoleAssignmentRevisionConflictError",
]

# ARTIFACT: role_assignment_repository.py
# VERSION: v1.0.1-WILSY-ROLE-ASSIGNMENT-REPOSITORY
# AUTHORITY BOUNDARY: role-assignment persistence, current resolution, hydration, and revision CAS only
# TENANT POSTURE: every authority record is explicitly scoped by principal_id, tenant_id, and role_id; no tenant inference
# FAIL-CLOSED POSTURE: absent, duplicate, malformed, unavailable, invalid, and stale-revision authority states never become successful authority
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
