"""Durable repository for tenant-neutral global principal credentials.

This repository owns persistence only. It does not authenticate passwords,
manage MFA factors, create principals, create memberships, assign capacities,
issue sessions, or own Mongo transaction lifecycle.
"""
from __future__ import annotations

from typing import Any, Mapping, Optional

from pymongo import ASCENDING
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.principal_credential import (
    MAX_CREDENTIAL_REVISION,
    PrincipalCredential,
    normalize_principal_email,
    validate_password_hash,
)

VERSION = "v1.0.0-GLOBAL-PRINCIPAL-CREDENTIAL-REPOSITORY"
COLLECTION = "principal_credentials"


class PrincipalCredentialRepositoryError(RuntimeError):
    """Base fail-closed repository error."""


class PrincipalCredentialNotFoundError(PrincipalCredentialRepositoryError):
    """No credential exists for the exact principal/email key."""


class PrincipalCredentialAlreadyExistsError(PrincipalCredentialRepositoryError):
    """A global principal or normalized email already has a credential."""


class PrincipalCredentialRevisionConflictError(PrincipalCredentialRepositoryError):
    """A password verifier update lost its expected revision race."""


class PrincipalCredentialPersistedRecordInvalidError(PrincipalCredentialRepositoryError):
    """Persisted global credential material failed strict hydration."""


class PrincipalCredentialMfaStateConflictError(PrincipalCredentialRepositoryError):
    """MFA enrollment state is already enabled or changed concurrently."""



def _target(collection: Optional[Collection]) -> Collection:
    if collection is not None:
        return collection
    from tools.eos.kernel.db import get_database
    database = get_database()
    if database is None:
        raise PrincipalCredentialRepositoryError("PRINCIPAL_CREDENTIAL_PERSISTENCE_UNAVAILABLE")
    return database[COLLECTION]


def _document(value: PrincipalCredential) -> dict[str, object]:
    return {
        "principal_id": value.principal_id,
        "normalized_email": value.normalized_email,
        "password_hash": value.password_hash,
        "credential_revision": value.credential_revision,
        "mfa_enabled": value.mfa_enabled,
    }


def _find_unique(
    target: Collection,
    query: dict[str, object],
    *,
    session: Optional[ClientSession] = None,
) -> Mapping[str, object] | None:
    """Read at most two exact matches so missing indexes cannot hide ambiguity."""
    rows = list(target.find(query, session=session).limit(2))
    if len(rows) > 1:
        raise PrincipalCredentialPersistedRecordInvalidError(
            "PRINCIPAL_CREDENTIAL_DUPLICATE_KEY"
        )
    return rows[0] if rows else None


def _hydrate(document: Mapping[str, object]) -> PrincipalCredential:
    try:
        return PrincipalCredential(
            principal_id=document["principal_id"],  # type: ignore[arg-type]
            normalized_email=document["normalized_email"],  # type: ignore[arg-type]
            password_hash=document["password_hash"],  # type: ignore[arg-type]
            credential_revision=document["credential_revision"],  # type: ignore[arg-type]
            mfa_enabled=document["mfa_enabled"],  # type: ignore[arg-type]
        )
    except (KeyError, TypeError, ValueError) as error:
        raise PrincipalCredentialPersistedRecordInvalidError(
            "PRINCIPAL_CREDENTIAL_PERSISTED_RECORD_INVALID"
        ) from error


class PrincipalCredentialRepository:
    """Persist one tenant-neutral credential record per global principal."""

    @staticmethod
    def ensure_indexes(collection: Optional[Collection] = None) -> None:
        target = _target(collection)
        target.create_index(
            [("principal_id", ASCENDING)],
            unique=True,
            name="principal_credential_principal_unique",
        )
        target.create_index(
            [("normalized_email", ASCENDING)],
            unique=True,
            name="principal_credential_email_unique",
        )

    @staticmethod
    def insert(
        value: PrincipalCredential,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> PrincipalCredential:
        if not isinstance(value, PrincipalCredential):
            raise PrincipalCredentialRepositoryError("PRINCIPAL_CREDENTIAL_INSERT_INVALID")
        try:
            _target(collection).insert_one(_document(value), session=session)
        except DuplicateKeyError as error:
            raise PrincipalCredentialAlreadyExistsError(
                "PRINCIPAL_CREDENTIAL_ALREADY_EXISTS"
            ) from error
        except PyMongoError as error:
            raise PrincipalCredentialRepositoryError(
                "PRINCIPAL_CREDENTIAL_INSERT_FAILED"
            ) from error
        return value

    @staticmethod
    def get_by_principal(
        principal_id: str,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> PrincipalCredential:
        if not isinstance(principal_id, str) or not principal_id or principal_id != principal_id.strip():
            raise PrincipalCredentialNotFoundError("PRINCIPAL_CREDENTIAL_NOT_FOUND")
        try:
            row = _find_unique(_target(collection), {"principal_id": principal_id}, session=session)
        except PyMongoError as error:
            raise PrincipalCredentialRepositoryError("PRINCIPAL_CREDENTIAL_READ_FAILED") from error
        if row is None:
            raise PrincipalCredentialNotFoundError("PRINCIPAL_CREDENTIAL_NOT_FOUND")
        value = _hydrate(row)
        if value.principal_id != principal_id:
            raise PrincipalCredentialPersistedRecordInvalidError(
                "PRINCIPAL_CREDENTIAL_PRINCIPAL_MISMATCH"
            )
        return value

    @staticmethod
    def get_by_email(
        email: str,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> PrincipalCredential:
        try:
            normalized_email = normalize_principal_email(email)
        except ValueError as error:
            raise PrincipalCredentialNotFoundError("PRINCIPAL_CREDENTIAL_NOT_FOUND") from error
        try:
            row = _find_unique(
                _target(collection),
                {"normalized_email": normalized_email},
                session=session,
            )
        except PyMongoError as error:
            raise PrincipalCredentialRepositoryError("PRINCIPAL_CREDENTIAL_READ_FAILED") from error
        if row is None:
            raise PrincipalCredentialNotFoundError("PRINCIPAL_CREDENTIAL_NOT_FOUND")
        value = _hydrate(row)
        if value.normalized_email != normalized_email:
            raise PrincipalCredentialPersistedRecordInvalidError(
                "PRINCIPAL_CREDENTIAL_EMAIL_MISMATCH"
            )
        return value

    @staticmethod
    def enable_mfa(
        principal_id: str,
        expected_revision: int,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> PrincipalCredential:
        """Enable MFA once and advance the global credential epoch atomically."""
        if (
            not isinstance(expected_revision, int)
            or isinstance(expected_revision, bool)
            or not 0 <= expected_revision < MAX_CREDENTIAL_REVISION
        ):
            raise PrincipalCredentialRevisionConflictError(
                "PRINCIPAL_CREDENTIAL_REVISION_CONFLICT"
            )
        current = PrincipalCredentialRepository.get_by_principal(
            principal_id,
            collection,
            session=session,
        )
        if current.credential_revision != expected_revision:
            raise PrincipalCredentialRevisionConflictError(
                "PRINCIPAL_CREDENTIAL_REVISION_CONFLICT"
            )
        if current.mfa_enabled is True:
            raise PrincipalCredentialMfaStateConflictError(
                "PRINCIPAL_CREDENTIAL_MFA_ALREADY_ENABLED"
            )
        try:
            result = _target(collection).update_one(
                {
                    "principal_id": principal_id,
                    "credential_revision": expected_revision,
                    "mfa_enabled": False,
                },
                {
                    "$set": {"mfa_enabled": True},
                    "$inc": {"credential_revision": 1},
                },
                upsert=False,
                session=session,
            )
        except PyMongoError as error:
            raise PrincipalCredentialRepositoryError(
                "PRINCIPAL_CREDENTIAL_MFA_ENABLE_FAILED"
            ) from error
        if getattr(result, "matched_count", 0) != 1:
            raise PrincipalCredentialMfaStateConflictError(
                "PRINCIPAL_CREDENTIAL_MFA_STATE_CONFLICT"
            )
        return PrincipalCredential(
            principal_id=current.principal_id,
            normalized_email=current.normalized_email,
            password_hash=current.password_hash,
            credential_revision=expected_revision + 1,
            mfa_enabled=True,
        )

    @staticmethod
    def compare_and_swap_password_hash(
        principal_id: str,
        expected_revision: int,
        new_password_hash: str,
        collection: Optional[Collection] = None,
        *,
        session: Optional[ClientSession] = None,
    ) -> PrincipalCredential:
        if (
            not isinstance(expected_revision, int)
            or isinstance(expected_revision, bool)
            or not 0 <= expected_revision < MAX_CREDENTIAL_REVISION
        ):
            raise PrincipalCredentialRevisionConflictError(
                "PRINCIPAL_CREDENTIAL_REVISION_CONFLICT"
            )
        try:
            validate_password_hash(new_password_hash)
        except ValueError as error:
            raise PrincipalCredentialRepositoryError(
                "PRINCIPAL_CREDENTIAL_PASSWORD_VERIFIER_INVALID"
            ) from error
        current = PrincipalCredentialRepository.get_by_principal(
            principal_id,
            collection,
            session=session,
        )
        if current.credential_revision != expected_revision:
            raise PrincipalCredentialRevisionConflictError(
                "PRINCIPAL_CREDENTIAL_REVISION_CONFLICT"
            )
        try:
            result = _target(collection).update_one(
                {
                    "principal_id": principal_id,
                    "credential_revision": expected_revision,
                },
                {
                    "$set": {"password_hash": new_password_hash},
                    "$inc": {"credential_revision": 1},
                },
                upsert=False,
                session=session,
            )
        except PyMongoError as error:
            raise PrincipalCredentialRepositoryError(
                "PRINCIPAL_CREDENTIAL_UPDATE_FAILED"
            ) from error
        if getattr(result, "matched_count", 0) != 1:
            raise PrincipalCredentialRevisionConflictError(
                "PRINCIPAL_CREDENTIAL_REVISION_CONFLICT"
            )
        return PrincipalCredential(
            principal_id=current.principal_id,
            normalized_email=current.normalized_email,
            password_hash=new_password_hash,
            credential_revision=expected_revision + 1,
            mfa_enabled=current.mfa_enabled,
        )


__all__ = [
    "VERSION",
    "COLLECTION",
    "PrincipalCredentialRepository",
    "PrincipalCredentialRepositoryError",
    "PrincipalCredentialNotFoundError",
    "PrincipalCredentialAlreadyExistsError",
    "PrincipalCredentialRevisionConflictError",
    "PrincipalCredentialPersistedRecordInvalidError",
    "PrincipalCredentialMfaStateConflictError",
]
