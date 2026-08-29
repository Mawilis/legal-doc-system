# -*- coding: utf-8 -*-
"""Durable Mongo repository for current PrincipalAuthority snapshots.

TITLE: WILSY OS Principal Authority Repository
VERSION: v1.0.0-WILSY-PRINCIPAL-AUTHORITY-REPOSITORY
AUTHORITY: Current PrincipalAuthority persistence, resolution, and revision CAS only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/principal_authority_repository.py
CERTIFICATION/UPDATE DATE: 2026-08-29
CHANGELOG: v1.0.0 establishes tenant-neutral Mongo persistence with duplicate and stale-write protection.
COMPLIANCE: Caller-owned sessions; deterministic unique identity; no hidden transaction or retry ownership.
SECURITY/PRIVACY POSTURE: Stores only opaque principal_id, PrincipalStatus value, and revision.
TENANT BOUNDARY: PrincipalAuthority is tenant-neutral; no tenant field or cross-tenant lookup exists here.
AUTHORITY BOUNDARY: No lifecycle transition policy, authentication, authorization, credentials, roles, or membership.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial execution authority.

Epitome:
    A narrow persistence seam for current immutable authority snapshots. The
    caller owns sessions, transaction boundaries, retries, and lifecycle policy.

Biblical Anchor:
    "And he shall be like a tree planted by the rivers of water..." — Psalm 1:3

Collaboration & Ownership:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    AI Collaborator: Core Systems Engineering Agent
    File Path: tools/eos/auth/principal_authority_repository.py
"""
from __future__ import annotations

from typing import Mapping, Optional

from pymongo import ASCENDING
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_status import PrincipalStatus

VERSION = "v1.0.0-WILSY-PRINCIPAL-AUTHORITY-REPOSITORY"
COLLECTION = "principal_authorities"


class PrincipalAuthorityRepositoryError(RuntimeError):
    """Base fail-closed repository error."""


class PrincipalAuthorityNotFoundError(PrincipalAuthorityRepositoryError):
    """No current authority exists for the requested principal identifier."""


class PrincipalAuthorityAlreadyExistsError(PrincipalAuthorityRepositoryError):
    """An initial authority already exists for the principal identifier."""


class PrincipalAuthorityRevisionConflictError(PrincipalAuthorityRepositoryError):
    """The expected revision was stale or the target snapshot was invalid."""


class PrincipalAuthorityPersistedRecordInvalidError(PrincipalAuthorityRepositoryError):
    """Persisted authority data failed strict hydration validation."""


def _target(collection: Optional[Collection]) -> Collection:
    """Resolve an injected collection without taking transaction ownership."""
    if collection is not None:
        return collection
    from tools.eos.kernel.db import get_database

    database = get_database()
    if database is None:
        raise PrincipalAuthorityRepositoryError("PRINCIPAL_AUTHORITY_PERSISTENCE_UNAVAILABLE")
    return database[COLLECTION]


def _document(authority: PrincipalAuthority) -> dict[str, object]:
    """Serialize exactly the three canonical authority fields."""
    return {
        "principal_id": authority.principal_id,
        "status": authority.status.value,
        "revision": authority.revision,
    }


def _hydrate(document: Mapping[str, object]) -> PrincipalAuthority:
    """Hydrate persisted state and reject corruption before returning it."""
    try:
        principal_id = document["principal_id"]
        status = document["status"]
        revision = document["revision"]
        if not isinstance(principal_id, str) or not isinstance(status, str):
            raise TypeError("identity or status type invalid")
        if not isinstance(revision, int) or isinstance(revision, bool):
            raise TypeError("revision type invalid")
        return PrincipalAuthority(principal_id, PrincipalStatus(status), revision)
    except (KeyError, TypeError, ValueError) as error:
        raise PrincipalAuthorityPersistedRecordInvalidError(
            "PRINCIPAL_AUTHORITY_PERSISTED_RECORD_INVALID"
        ) from error


class PrincipalAuthorityRepository:
    """Persist and resolve current PrincipalAuthority without owning transactions."""

    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        """Create the deterministic unique principal identity index."""
        _target(collection).create_index(
            [("principal_id", ASCENDING)], unique=True, name="principal_identity_unique"
        )

    @staticmethod
    def create(
        authority: PrincipalAuthority,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> PrincipalAuthority:
        """Insert one initial snapshot; never implicitly upsert or overwrite."""
        if not isinstance(authority, PrincipalAuthority):
            raise PrincipalAuthorityRepositoryError("PRINCIPAL_AUTHORITY_CREATE_INVALID")
        try:
            _target(collection).insert_one(_document(authority), session=session)
            return authority
        except DuplicateKeyError as error:
            raise PrincipalAuthorityAlreadyExistsError(
                "PRINCIPAL_AUTHORITY_ALREADY_EXISTS"
            ) from error
        except PyMongoError as error:
            raise PrincipalAuthorityRepositoryError(
                "PRINCIPAL_AUTHORITY_CREATE_FAILED"
            ) from error

    @staticmethod
    def get(
        principal_id: str,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> PrincipalAuthority:
        """Resolve exact current authority or raise explicit absence."""
        if not isinstance(principal_id, str) or not principal_id:
            raise PrincipalAuthorityNotFoundError("PRINCIPAL_AUTHORITY_NOT_FOUND")
        try:
            row = _target(collection).find_one({"principal_id": principal_id}, session=session)
        except PyMongoError as error:
            raise PrincipalAuthorityRepositoryError("PRINCIPAL_AUTHORITY_READ_FAILED") from error
        if row is None:
            raise PrincipalAuthorityNotFoundError("PRINCIPAL_AUTHORITY_NOT_FOUND")
        return _hydrate(row)

    @staticmethod
    def compare_and_swap(
        authority: PrincipalAuthority,
        expected_revision: int,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> PrincipalAuthority:
        """Persist a revision+1 snapshot only when the expected revision matches."""
        if not isinstance(expected_revision, int) or isinstance(expected_revision, bool):
            raise PrincipalAuthorityRevisionConflictError("PRINCIPAL_AUTHORITY_REVISION_CONFLICT")
        if authority.revision != expected_revision + 1:
            raise PrincipalAuthorityRevisionConflictError("PRINCIPAL_AUTHORITY_REVISION_CONFLICT")
        try:
            result = _target(collection).replace_one(
                {"principal_id": authority.principal_id, "revision": expected_revision},
                _document(authority),
                upsert=False,
                session=session,
            )
        except PyMongoError as error:
            raise PrincipalAuthorityRepositoryError("PRINCIPAL_AUTHORITY_UPDATE_FAILED") from error
        if result.matched_count != 1:
            raise PrincipalAuthorityRevisionConflictError("PRINCIPAL_AUTHORITY_REVISION_CONFLICT")
        return authority


__all__ = [
    "COLLECTION",
    "VERSION",
    "PrincipalAuthorityAlreadyExistsError",
    "PrincipalAuthorityNotFoundError",
    "PrincipalAuthorityPersistedRecordInvalidError",
    "PrincipalAuthorityRepository",
    "PrincipalAuthorityRepositoryError",
    "PrincipalAuthorityRevisionConflictError",
]

# ARTIFACT: principal_authority_repository.py
# VERSION: v1.0.0-WILSY-PRINCIPAL-AUTHORITY-REPOSITORY
# AUTHORITY BOUNDARY: current snapshot persistence and revision CAS only
# TENANT POSTURE: tenant-neutral; no membership authority
# FAIL-CLOSED POSTURE: absence, duplicates, corruption, and stale writes are explicit errors
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
