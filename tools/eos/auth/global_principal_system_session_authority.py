"""Tenant-neutral SYSTEM MFA challenge and session authority.

SYSTEM sessions are separately scoped from tenant memberships and capacities.
Every issuance and currentness check re-proves the canonical SYSTEM queue-read
permission and active PLATFORM workforce relationship in the caller transaction.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import secrets
from typing import Any

from pymongo import ASCENDING, ReturnDocument
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from pymongo.errors import PyMongoError

from tools.eos.auth.jwt_provider import TokenPurpose, create_access_token
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_credential_repository import (
    PrincipalCredentialRepository,
    PrincipalCredentialRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.system_services.eos_authorizer import (
    SystemServicesAuthorizationError,
    SystemServicesAuthorizationUnavailable,
)

CHALLENGE_COLLECTION = "global_principal_system_mfa_challenges"
SESSION_COLLECTION = "global_principal_system_sessions"
REFRESH_COLLECTION = "global_principal_system_refresh_tokens"
CHALLENGE_TTL_SECONDS = 300
ACCESS_TTL_SECONDS = 900
REFRESH_TTL_SECONDS = 60 * 60 * 8
SYSTEM_SCOPE_MARKER = "SYSTEM"
SYSTEM_WORKSPACE_ID = "SYSTEM_SERVICES"
SYSTEM_ROLE = "SYSTEM_SERVICES"
QUEUE_READ_PERMISSION = "system_services:queue:read"


class GlobalPrincipalSystemSessionError(RuntimeError):
    """Base fail-closed SYSTEM session boundary error."""


class GlobalPrincipalSystemSessionRejected(GlobalPrincipalSystemSessionError):
    """A SYSTEM challenge or session is invalid, stale, or unauthorized."""


class GlobalPrincipalSystemSessionUnavailable(GlobalPrincipalSystemSessionError):
    """Canonical SYSTEM authority or persistence is unavailable."""


@dataclass(frozen=True, slots=True)
class SystemMfaFactorContext:
    principal_id: str
    credential_revision: int


@dataclass(frozen=True, slots=True)
class GlobalPrincipalSystemSessionReceipt:
    principal_id: str
    session_reference: str
    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    access_expires_at: datetime
    refresh_expires_at: datetime


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _require_transaction(session: Any) -> None:
    marker = getattr(session, "in_transaction", False)
    active = marker() if callable(marker) else marker
    if active is not True:
        raise GlobalPrincipalSystemSessionUnavailable("SYSTEM_SESSION_ACTIVE_TRANSACTION_REQUIRED")


class GlobalPrincipalSystemMfaChallengeService:
    """Issue and consume one-time, principal-scoped SYSTEM MFA challenges."""

    def __init__(self, *, collection: Collection | None = None) -> None:
        self._collection = collection

    def _store(self) -> Collection:
        if self._collection is None:
            raise GlobalPrincipalSystemSessionUnavailable("SYSTEM_MFA_CHALLENGE_STORE_UNAVAILABLE")
        return self._collection

    @staticmethod
    def ensure_indexes(collection: Collection) -> None:
        collection.create_index(
            [("challenge_digest", ASCENDING)],
            unique=True,
            name="global_principal_system_mfa_challenge_digest_unique",
        )
        collection.create_index(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=0,
            name="global_principal_system_mfa_challenge_expiry_ttl",
        )

    def issue(
        self,
        *,
        principal_id: str,
        credential_revision: int,
        session: ClientSession,
        now: datetime | None = None,
    ) -> tuple[str, datetime]:
        _require_transaction(session)
        if not isinstance(principal_id, str) or not principal_id or principal_id != principal_id.strip():
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_MFA_PRINCIPAL_INVALID")
        if not isinstance(credential_revision, int) or isinstance(credential_revision, bool) or credential_revision < 0:
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_MFA_CREDENTIAL_REVISION_INVALID")
        instant = now or datetime.now(timezone.utc)
        if instant.tzinfo is None or instant.utcoffset() is None:
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_MFA_TIME_INVALID")
        token = "sysmfa_" + secrets.token_urlsafe(32)
        expires_at = instant + timedelta(seconds=CHALLENGE_TTL_SECONDS)
        self._store().insert_one(
            {
                "challenge_digest": _digest(token),
                "principal_id": principal_id,
                "credential_revision": credential_revision,
                "created_at": instant,
                "expires_at": expires_at,
                "consumed_at": None,
                "schema_version": 1,
            },
            session=session,
        )
        return token, expires_at

    def get_factor_context(
        self,
        token: str,
        *,
        session: ClientSession,
        now: datetime | None = None,
    ) -> SystemMfaFactorContext:
        _require_transaction(session)
        if not isinstance(token, str) or not token.startswith("sysmfa_"):
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_MFA_CHALLENGE_INVALID")
        instant = now or datetime.now(timezone.utc)
        record = self._store().find_one(
            {
                "challenge_digest": _digest(token),
                "consumed_at": None,
                "expires_at": {"$gt": instant},
            },
            session=session,
        )
        if not isinstance(record, dict):
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_MFA_CHALLENGE_INVALID_OR_EXPIRED")
        principal_id = record.get("principal_id")
        revision = record.get("credential_revision")
        if (
            not isinstance(principal_id, str)
            or not principal_id
            or not isinstance(revision, int)
            or isinstance(revision, bool)
            or revision < 0
        ):
            raise GlobalPrincipalSystemSessionUnavailable("SYSTEM_MFA_CHALLENGE_CORRUPT")
        return SystemMfaFactorContext(principal_id, revision)

    def consume(
        self,
        token: str,
        *,
        principal_id: str,
        credential_revision: int,
        session: ClientSession,
        now: datetime | None = None,
    ) -> None:
        _require_transaction(session)
        instant = now or datetime.now(timezone.utc)
        result = self._store().update_one(
            {
                "challenge_digest": _digest(token),
                "principal_id": principal_id,
                "credential_revision": credential_revision,
                "consumed_at": None,
                "expires_at": {"$gt": instant},
            },
            {"$set": {"consumed_at": instant}},
            session=session,
        )
        if result.modified_count != 1:
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_MFA_CHALLENGE_ALREADY_CONSUMED")


class GlobalPrincipalSystemSessionAuthority:
    """Issue and revalidate SYSTEM sessions without manufacturing tenant membership."""

    def __init__(
        self,
        *,
        sessions: Collection | None = None,
        refresh_tokens: Collection | None = None,
        principal_repository: Any = None,
        credential_repository: Any = None,
        principal_collection: Collection | None = None,
        credential_collection: Collection | None = None,
        authorizer: Any = None,
    ) -> None:
        self._sessions = sessions
        self._refresh_tokens = refresh_tokens
        self._principals = principal_repository or PrincipalAuthorityRepository()
        self._credentials = credential_repository or PrincipalCredentialRepository()
        self._principal_collection = principal_collection
        self._credential_collection = credential_collection
        self._authorizer = authorizer

    def _store(self) -> Collection:
        if self._sessions is None:
            raise GlobalPrincipalSystemSessionUnavailable("SYSTEM_SESSION_STORE_UNAVAILABLE")
        return self._sessions

    @staticmethod
    def ensure_indexes(sessions: Collection, refresh_tokens: Collection) -> None:
        sessions.create_index(
            [("session_reference", ASCENDING)],
            unique=True,
            name="global_principal_system_session_reference_unique",
        )
        sessions.create_index(
            [("principal_id", ASCENDING), ("revoked_at", ASCENDING)],
            name="global_principal_system_session_current_lookup",
        )
        sessions.create_index(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=0,
            name="global_principal_system_session_expiry_ttl",
        )
        refresh_tokens.create_index(
            [("token_digest", ASCENDING)],
            unique=True,
            name="global_principal_system_refresh_digest_unique",
        )
        refresh_tokens.create_index(
            [("session_reference", ASCENDING), ("revoked_at", ASCENDING)],
            name="global_principal_system_refresh_session_lookup",
        )
        refresh_tokens.create_index(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=0,
            name="global_principal_system_refresh_expiry_ttl",
        )

    def _refresh_store(self) -> Collection:
        if self._refresh_tokens is None:
            raise GlobalPrincipalSystemSessionUnavailable("SYSTEM_REFRESH_STORE_UNAVAILABLE")
        return self._refresh_tokens

    def _revalidate_principal(
        self,
        principal_id: str,
        credential_revision: int,
        *,
        session: ClientSession,
    ) -> None:
        try:
            principal = self._principals.get(principal_id, self._principal_collection, session=session)
            credential = self._credentials.get_by_principal(principal_id, self._credential_collection, session=session)
        except (PrincipalAuthorityRepositoryError, PrincipalCredentialRepositoryError) as error:
            raise GlobalPrincipalSystemSessionUnavailable("SYSTEM_PRINCIPAL_AUTHORITY_UNAVAILABLE") from error
        if principal.status is not PrincipalStatus.ACTIVE:
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_PRINCIPAL_INACTIVE")
        if credential.credential_revision != credential_revision or credential.mfa_enabled is not True:
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_CREDENTIAL_STALE")
        if self._authorizer is None:
            raise GlobalPrincipalSystemSessionUnavailable("SYSTEM_AUTHORIZER_UNAVAILABLE")
        try:
            self._authorizer.require(
                principal_id=principal_id,
                permission_id=QUEUE_READ_PERMISSION,
                session=session,
            )
        except SystemServicesAuthorizationError as error:
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_WORKSPACE_AUTHORITY_REQUIRED") from error
        except SystemServicesAuthorizationUnavailable as error:
            raise GlobalPrincipalSystemSessionUnavailable("SYSTEM_WORKSPACE_AUTHORITY_UNAVAILABLE") from error

    def issue_after_mfa(
        self,
        principal_id: str,
        credential_revision: int,
        *,
        session: ClientSession,
        now: datetime | None = None,
    ) -> GlobalPrincipalSystemSessionReceipt:
        _require_transaction(session)
        instant = now or datetime.now(timezone.utc)
        self._revalidate_principal(principal_id, credential_revision, session=session)
        reference = "WILSYS-SYSTEM-SESSION-" + secrets.token_urlsafe(24)
        refresh_token = "sysrefresh_" + secrets.token_urlsafe(32)
        access_expires_at = instant + timedelta(seconds=ACCESS_TTL_SECONDS)
        refresh_expires_at = instant + timedelta(seconds=REFRESH_TTL_SECONDS)
        token = create_access_token(
            {
                "identity_id": principal_id,
                "tenant_id": SYSTEM_SCOPE_MARKER,
                "roles": [SYSTEM_ROLE],
                "permissions": [],
                "session_reference": reference,
                "workspace_id": SYSTEM_WORKSPACE_ID,
                "principal_scope": "SYSTEM",
            },
            expires_in_seconds=ACCESS_TTL_SECONDS,
            token_purpose=TokenPurpose.ACCESS,
            credential_revision=credential_revision,
        )
        self._store().insert_one(
            {
                "session_reference": reference,
                "principal_id": principal_id,
                "credential_revision": credential_revision,
                "created_at": instant,
                "expires_at": refresh_expires_at,
                "revoked_at": None,
                "schema_version": 1,
            },
            session=session,
        )
        self._refresh_store().insert_one(
            {
                "token_digest": _digest(refresh_token),
                "session_reference": reference,
                "principal_id": principal_id,
                "credential_revision": credential_revision,
                "issued_at": instant,
                "expires_at": refresh_expires_at,
                "consumed_at": None,
                "revoked_at": None,
                "schema_version": 1,
            },
            session=session,
        )
        return GlobalPrincipalSystemSessionReceipt(
            principal_id=principal_id,
            session_reference=reference,
            access_token=token,
            refresh_token=refresh_token,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
        )

    def rotate_refresh_token(
        self,
        refresh_token: str,
        *,
        session: ClientSession,
        now: datetime | None = None,
    ) -> GlobalPrincipalSystemSessionReceipt:
        """Rotate a SYSTEM refresh bearer in the caller-owned transaction."""
        _require_transaction(session)
        instant = now or datetime.now(timezone.utc)
        if not isinstance(refresh_token, str) or not refresh_token.startswith("sysrefresh_"):
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_REFRESH_INVALID")
        try:
            row = self._refresh_store().find_one_and_update(
                {
                    "token_digest": _digest(refresh_token),
                    "consumed_at": None,
                    "revoked_at": None,
                    "expires_at": {"$gt": instant},
                },
                {"$set": {"consumed_at": instant}},
                return_document=ReturnDocument.AFTER,
                session=session,
            )
        except PyMongoError as error:
            raise GlobalPrincipalSystemSessionUnavailable("SYSTEM_REFRESH_READ_FAILED") from error
        if not isinstance(row, dict):
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_REFRESH_INVALID")
        principal_id = row.get("principal_id")
        credential_revision = row.get("credential_revision")
        reference = row.get("session_reference")
        if (
            not isinstance(principal_id, str)
            or not isinstance(credential_revision, int)
            or isinstance(credential_revision, bool)
            or not isinstance(reference, str)
        ):
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_REFRESH_SESSION_INVALID")
        session_row = self._store().find_one(
            {
                "principal_id": principal_id,
                "session_reference": reference,
                "credential_revision": credential_revision,
                "revoked_at": None,
                "expires_at": {"$gt": instant},
            },
            session=session,
        )
        if not isinstance(session_row, dict):
            raise GlobalPrincipalSystemSessionRejected("SYSTEM_REFRESH_SESSION_REVOKED")
        self._revalidate_principal(principal_id, credential_revision, session=session)
        new_refresh = "sysrefresh_" + secrets.token_urlsafe(32)
        refresh_expires_at = min(session_row["expires_at"], instant + timedelta(seconds=REFRESH_TTL_SECONDS))
        access_expires_at = instant + timedelta(seconds=ACCESS_TTL_SECONDS)
        access = create_access_token(
            {
                "identity_id": principal_id,
                "tenant_id": SYSTEM_SCOPE_MARKER,
                "roles": [SYSTEM_ROLE],
                "permissions": [],
                "session_reference": reference,
                "workspace_id": SYSTEM_WORKSPACE_ID,
                "principal_scope": "SYSTEM",
            },
            expires_in_seconds=ACCESS_TTL_SECONDS,
            token_purpose=TokenPurpose.ACCESS,
            credential_revision=credential_revision,
        )
        try:
            self._refresh_store().insert_one(
                {
                    "token_digest": _digest(new_refresh),
                    "session_reference": reference,
                    "principal_id": principal_id,
                    "credential_revision": credential_revision,
                    "issued_at": instant,
                    "expires_at": refresh_expires_at,
                    "consumed_at": None,
                    "revoked_at": None,
                    "schema_version": 1,
                },
                session=session,
            )
        except PyMongoError as error:
            raise GlobalPrincipalSystemSessionUnavailable("SYSTEM_REFRESH_ROTATION_FAILED") from error
        return GlobalPrincipalSystemSessionReceipt(
            principal_id=principal_id,
            session_reference=reference,
            access_token=access,
            refresh_token=new_refresh,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
        )

    def is_session_current(
        self,
        *,
        principal_id: str,
        session_reference: str,
        expected_credential_revision: int,
        session: ClientSession,
        now: datetime | None = None,
    ) -> bool:
        _require_transaction(session)
        instant = now or datetime.now(timezone.utc)
        record = self._store().find_one(
            {
                "principal_id": principal_id,
                "session_reference": session_reference,
                "credential_revision": expected_credential_revision,
                "revoked_at": None,
                "expires_at": {"$gt": instant},
            },
            session=session,
        )
        if not isinstance(record, dict):
            return False
        self._revalidate_principal(principal_id, expected_credential_revision, session=session)
        return True

    def revoke(
        self,
        *,
        principal_id: str,
        session_reference: str,
        session: ClientSession,
        now: datetime | None = None,
    ) -> bool:
        _require_transaction(session)
        instant = now or datetime.now(timezone.utc)
        result = self._store().update_one(
            {
                "principal_id": principal_id,
                "session_reference": session_reference,
                "revoked_at": None,
            },
            {"$set": {"revoked_at": instant}},
            session=session,
        )
        self._refresh_store().update_many(
            {
                "principal_id": principal_id,
                "session_reference": session_reference,
                "revoked_at": None,
            },
            {"$set": {"revoked_at": instant}},
            session=session,
        )
        return result.modified_count == 1
