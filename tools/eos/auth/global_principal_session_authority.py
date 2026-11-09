"""TITLE: WILSY OS Global Principal Session and Refresh Authority.
VERSION: v1.1.0-GLOBAL-PRINCIPAL-HEADQUARTERS-SESSION
AUTHORITY: Server-owned selected-membership session issuance, refresh and revocation.
EPITOME: Revalidates principal, credential, exact tenant membership, selected
         business capacity, canonical tenant and tenant-aware workspace binding.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/global_principal_session_authority.py
COLLABORATION / OWNERSHIP: WILSY OS Core Engineering.
CERTIFICATION / UPDATE DATE: 2026-11-08.
CHANGELOG:
    2026-11-08 v1.1.0-GLOBAL-PRINCIPAL-HEADQUARTERS-SESSION revalidates the selected workspace against the exact
    tenant identifier. Only the canonical WILSY company tenant's tenant_owner
    capacity selects WILSY_HEADQUARTERS; customer tenant owners retain the
    Executive Command Centre. Existing transaction ownership and session
    revision checks remain unchanged.
    v1.0.0-GLOBAL-PRINCIPAL-SESSION-AUTHORITY introduced revision-bound selected-membership session and refresh authority.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Opaque session and refresh credentials; exact
    principal, credential, membership and capacity revision revalidation.
TENANT BOUNDARY: Every session is bound to one exact principal and canonical
    tenant; browser and JWT projections do not establish workspace authority.
AUTHORITY BOUNDARY: Owns global session and refresh lifecycle only; it does
    not create memberships, business capacities, permissions or HR authority.
TRANSACTION BOUNDARY: Mutations require an active caller-owned Mongo transaction;
    this module never starts, commits, aborts or retries transactions.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS remains exclusive.
"""
from __future__ import annotations

import hashlib
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from pymongo import ASCENDING, ReturnDocument
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.jwt_provider import TokenPurpose, create_access_token
from tools.eos.auth.membership_selection_challenge import SelectedMembershipContext
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityRepository, PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_credential_repository import (
    PrincipalCredentialRepository, PrincipalCredentialRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipRepository, TenantMembershipRepositoryError,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleRepository, TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.workspace_bootstrap_projection import (
    WorkspaceBootstrapProjectionError,
    resolve_workspace_id,
)
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry, TenantRegistryError

VERSION = "v1.1.0-GLOBAL-PRINCIPAL-HEADQUARTERS-SESSION"
SESSION_COLLECTION = "global_principal_sessions"
REFRESH_COLLECTION = "global_principal_refresh_tokens"
ACCESS_TTL_SECONDS = 900
REFRESH_TTL_SECONDS = 60 * 60 * 24 * 30


class GlobalPrincipalSessionError(RuntimeError):
    """Base fail-closed global session authority error."""


class GlobalPrincipalSessionRejected(GlobalPrincipalSessionError):
    """Selected authority or session is absent, stale, revoked, or inconsistent."""


class GlobalPrincipalSessionUnavailable(GlobalPrincipalSessionError):
    """A required persistence or current-authority source is unavailable."""


@dataclass(frozen=True, slots=True)
class GlobalPrincipalSessionReceipt:
    principal_id: str
    tenant_id: str
    business_role: str
    workspace_id: str
    session_reference: str
    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    access_expires_at: datetime
    refresh_expires_at: datetime


def _utc(value: datetime | None) -> datetime:
    instant = value if value is not None else datetime.now(timezone.utc)
    if not isinstance(instant, datetime) or instant.tzinfo is None or instant.utcoffset() is None:
        raise GlobalPrincipalSessionRejected("GLOBAL_SESSION_TIME_INVALID")
    return instant.astimezone(timezone.utc)

def _persisted_utc(value: Any) -> datetime:
    """Interpret BSON-naive datetimes as UTC; reject all other malformed values."""
    if not isinstance(value, datetime):
        raise GlobalPrincipalSessionRejected("GLOBAL_SESSION_TIME_INVALID")
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _require_transaction(session: ClientSession | Any) -> None:
    marker = getattr(session, "in_transaction", None) if session is not None else None
    active = marker() if callable(marker) else marker
    if active is not True:
        raise GlobalPrincipalSessionRejected("GLOBAL_SESSION_TRANSACTION_REQUIRED")


def _digest(token: str) -> str:
    return hashlib.sha3_512(token.encode("utf-8")).hexdigest()


def _target(collection: Collection | None, name: str) -> Collection:
    if collection is not None:
        return collection
    from tools.eos.kernel.db import get_database
    database = get_database()
    if database is None:
        raise GlobalPrincipalSessionUnavailable("GLOBAL_SESSION_PERSISTENCE_UNAVAILABLE")
    return database[name]


def _validate_selected_context(value: SelectedMembershipContext) -> None:
    if not isinstance(value, SelectedMembershipContext):
        raise GlobalPrincipalSessionRejected("GLOBAL_SESSION_SELECTION_INVALID")
    fields = (
        value.principal_id, value.tenant_id, value.business_role, value.workspace_id,
    )
    if any(not isinstance(item, str) or not item or item != item.strip() for item in fields):
        raise GlobalPrincipalSessionRejected("GLOBAL_SESSION_SELECTION_INVALID")
    for revision in (value.credential_revision, value.membership_revision, value.capacity_revision):
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
            raise GlobalPrincipalSessionRejected("GLOBAL_SESSION_REVISION_INVALID")


class GlobalPrincipalSessionAuthority:
    """Issue, rotate, check, and revoke exact global-principal sessions."""

    def __init__(
        self,
        *,
        sessions: Collection | None = None,
        refresh_tokens: Collection | None = None,
        principal_repository: Any = None,
        credential_repository: Any = None,
        membership_repository: Any = None,
        business_role_repository: Any = None,
        tenant_resolver: Any = None,
    ) -> None:
        self._sessions = sessions
        self._refresh = refresh_tokens
        self._principals = principal_repository or PrincipalAuthorityRepository()
        self._credentials = credential_repository or PrincipalCredentialRepository()
        self._memberships = membership_repository or TenantMembershipRepository()
        self._capacities = business_role_repository or TenantBusinessRoleRepository()
        self._tenant_resolver = tenant_resolver or TenantRegistry.resolve_canonical_tenant

    @staticmethod
    def ensure_indexes(
        sessions: Collection,
        refresh_tokens: Collection,
    ) -> None:
        """Install uniqueness/expiry indexes from canonical application startup only."""
        sessions.create_index(
            [("session_reference", ASCENDING)], unique=True,
            name="global_principal_session_reference_unique",
        )
        sessions.create_index(
            [("principal_id", ASCENDING), ("tenant_id", ASCENDING), ("revoked_at", ASCENDING)],
            name="global_principal_session_current_lookup",
        )
        refresh_tokens.create_index(
            [("token_digest", ASCENDING)], unique=True,
            name="global_principal_refresh_digest_unique",
        )
        refresh_tokens.create_index(
            [("expires_at", ASCENDING)], expireAfterSeconds=0,
            name="global_principal_refresh_expiry_ttl",
        )

    def _revalidate(self, selected: SelectedMembershipContext, session: Any) -> None:
        _validate_selected_context(selected)
        try:
            principal = self._principals.get(selected.principal_id, session=session)
            credential = self._credentials.get_by_principal(selected.principal_id, session=session)
            membership = self._memberships.resolve(
                selected.principal_id, selected.tenant_id, session=session,
            )
            capacity = self._capacities.resolve_business_role(
                selected.principal_id, selected.tenant_id, selected.business_role,
                session=session,
            )
            tenant = self._tenant_resolver(selected.tenant_id, session=session)
        except (PrincipalAuthorityRepositoryError, PrincipalCredentialRepositoryError,
                TenantMembershipRepositoryError, TenantBusinessRoleRepositoryError,
                TenantRegistryError) as error:
            raise GlobalPrincipalSessionUnavailable("GLOBAL_SESSION_AUTHORITY_READ_FAILED") from error
        if principal.status is not PrincipalStatus.ACTIVE:
            raise GlobalPrincipalSessionRejected("GLOBAL_SESSION_PRINCIPAL_INACTIVE")
        if credential.credential_revision != selected.credential_revision or credential.mfa_enabled is not True:
            raise GlobalPrincipalSessionRejected("GLOBAL_SESSION_CREDENTIAL_STALE")
        if (membership.status is not TenantMembershipStatus.ACTIVE
                or membership.revision != selected.membership_revision):
            raise GlobalPrincipalSessionRejected("GLOBAL_SESSION_MEMBERSHIP_STALE")
        if (capacity.status is not TenantBusinessRoleStatus.ACTIVE
                or capacity.revision != selected.capacity_revision):
            raise GlobalPrincipalSessionRejected("GLOBAL_SESSION_CAPACITY_STALE")
        if getattr(tenant, "tenant_id", None) != selected.tenant_id:
            raise GlobalPrincipalSessionRejected("GLOBAL_SESSION_TENANT_INVALID")
        try:
            canonical_workspace_id = resolve_workspace_id(
                selected.business_role,
                tenant_id=selected.tenant_id,
            )
        except WorkspaceBootstrapProjectionError as error:
            raise GlobalPrincipalSessionRejected("GLOBAL_SESSION_WORKSPACE_INVALID") from error
        if canonical_workspace_id != selected.workspace_id:
            raise GlobalPrincipalSessionRejected("GLOBAL_SESSION_WORKSPACE_STALE")

    def issue_after_mfa(
        self,
        selected: SelectedMembershipContext,
        *,
        session: ClientSession | Any,
        now: datetime | None = None,
    ) -> GlobalPrincipalSessionReceipt:
        """Issue ACCESS + refresh only after MFA challenge consumption, in same transaction."""
        _require_transaction(session)
        instant = _utc(now)
        self._revalidate(selected, session)
        reference = f"WILSYGLOBALSESSION-{uuid.uuid4()}"
        refresh = secrets.token_urlsafe(48)
        access_expiry = instant + timedelta(seconds=ACCESS_TTL_SECONDS)
        refresh_expiry = instant + timedelta(seconds=REFRESH_TTL_SECONDS)
        access = create_access_token(
            {
                "identity_id": selected.principal_id,
                "tenant_id": selected.tenant_id,
                "roles": [selected.business_role],
                "permissions": [],
                "session_reference": reference,
                "membership_revision": selected.membership_revision,
                "capacity_revision": selected.capacity_revision,
                "workspace_id": selected.workspace_id,
                "principal_scope": "GLOBAL",
            },
            expires_in_seconds=ACCESS_TTL_SECONDS,
            token_purpose=TokenPurpose.ACCESS,
            credential_revision=selected.credential_revision,
        )
        session_doc = {
            "session_reference": reference,
            "principal_id": selected.principal_id,
            "tenant_id": selected.tenant_id,
            "business_role": selected.business_role,
            "workspace_id": selected.workspace_id,
            "credential_revision": selected.credential_revision,
            "membership_revision": selected.membership_revision,
            "capacity_revision": selected.capacity_revision,
            "created_at": instant,
            "expires_at": refresh_expiry,
            "revoked_at": None,
            "schema_version": 1,
        }
        refresh_doc = {
            "token_digest": _digest(refresh),
            "session_reference": reference,
            "principal_id": selected.principal_id,
            "tenant_id": selected.tenant_id,
            "credential_revision": selected.credential_revision,
            "issued_at": instant,
            "expires_at": refresh_expiry,
            "consumed_at": None,
            "revoked_at": None,
            "schema_version": 1,
        }
        try:
            _target(self._sessions, SESSION_COLLECTION).insert_one(session_doc, session=session)
            _target(self._refresh, REFRESH_COLLECTION).insert_one(refresh_doc, session=session)
        except DuplicateKeyError as error:
            raise GlobalPrincipalSessionUnavailable("GLOBAL_SESSION_IDENTIFIER_COLLISION") from error
        except PyMongoError as error:
            raise GlobalPrincipalSessionUnavailable("GLOBAL_SESSION_PERSISTENCE_FAILED") from error
        return GlobalPrincipalSessionReceipt(
            principal_id=selected.principal_id,
            tenant_id=selected.tenant_id,
            business_role=selected.business_role,
            workspace_id=selected.workspace_id,
            session_reference=reference,
            access_token=access,
            refresh_token=refresh,
            access_expires_at=access_expiry,
            refresh_expires_at=refresh_expiry,
        )

    def rotate_refresh_token(
        self,
        refresh_token: str,
        *,
        session: ClientSession | Any,
        now: datetime | None = None,
    ) -> GlobalPrincipalSessionReceipt:
        """Consume one refresh bearer and rotate it; caller commits both writes atomically."""
        _require_transaction(session)
        instant = _utc(now)
        if not isinstance(refresh_token, str) or not 40 <= len(refresh_token) <= 128:
            raise GlobalPrincipalSessionRejected("GLOBAL_REFRESH_INVALID")
        target = _target(self._refresh, REFRESH_COLLECTION)
        try:
            row = target.find_one_and_update(
                {"token_digest": _digest(refresh_token), "consumed_at": None,
                 "revoked_at": None, "expires_at": {"$gt": instant}},
                {"$set": {"consumed_at": instant}},
                return_document=ReturnDocument.AFTER,
                session=session,
            )
        except PyMongoError as error:
            raise GlobalPrincipalSessionUnavailable("GLOBAL_REFRESH_READ_FAILED") from error
        if not isinstance(row, dict):
            raise GlobalPrincipalSessionRejected("GLOBAL_REFRESH_INVALID")
        reference = row.get("session_reference")
        if not isinstance(reference, str) or not reference:
            raise GlobalPrincipalSessionRejected("GLOBAL_REFRESH_SESSION_INVALID")
        session_row = _target(self._sessions, SESSION_COLLECTION).find_one(
            {"session_reference": reference, "principal_id": row.get("principal_id"),
             "tenant_id": row.get("tenant_id"), "revoked_at": None,
             "expires_at": {"$gt": instant}},
            session=session,
        )
        if not isinstance(session_row, dict):
            raise GlobalPrincipalSessionRejected("GLOBAL_REFRESH_SESSION_REVOKED")
        selected = SelectedMembershipContext(
            principal_id=row["principal_id"], tenant_id=row["tenant_id"],
            business_role=session_row["business_role"], workspace_id=session_row["workspace_id"],
            credential_revision=row["credential_revision"],
            membership_revision=session_row["membership_revision"],
            capacity_revision=session_row["capacity_revision"],
        )
        self._revalidate(selected, session)
        # Rotation retains the same session reference and authority epoch.
        new_refresh = secrets.token_urlsafe(48)
        access_expiry = instant + timedelta(seconds=ACCESS_TTL_SECONDS)
        persisted_session_expiry = _persisted_utc(session_row.get("expires_at"))
        refresh_expiry = min(
            persisted_session_expiry,
            instant + timedelta(seconds=REFRESH_TTL_SECONDS),
        )
        access = create_access_token(
            {"identity_id": selected.principal_id, "tenant_id": selected.tenant_id,
             "roles": [selected.business_role], "permissions": [],
             "session_reference": reference, "membership_revision": selected.membership_revision,
             "capacity_revision": selected.capacity_revision, "workspace_id": selected.workspace_id,
             "principal_scope": "GLOBAL"},
            expires_in_seconds=ACCESS_TTL_SECONDS, token_purpose=TokenPurpose.ACCESS,
            credential_revision=selected.credential_revision,
        )
        try:
            target.insert_one({
                "token_digest": _digest(new_refresh), "session_reference": reference,
                "principal_id": selected.principal_id, "tenant_id": selected.tenant_id,
                "credential_revision": selected.credential_revision, "issued_at": instant,
                "expires_at": refresh_expiry, "consumed_at": None, "revoked_at": None,
                "schema_version": 1,
            }, session=session)
        except (DuplicateKeyError, PyMongoError) as error:
            raise GlobalPrincipalSessionUnavailable("GLOBAL_REFRESH_ROTATION_FAILED") from error
        return GlobalPrincipalSessionReceipt(
            principal_id=selected.principal_id, tenant_id=selected.tenant_id,
            business_role=selected.business_role, workspace_id=selected.workspace_id,
            session_reference=reference, access_token=access, refresh_token=new_refresh,
            access_expires_at=access_expiry, refresh_expires_at=refresh_expiry,
        )

    def is_session_current(
        self,
        *,
        principal_id: str,
        tenant_id: str,
        session_reference: str,
        session: ClientSession | Any = None,
        now: datetime | None = None,
        expected_business_role: str | None = None,
        expected_workspace_id: str | None = None,
        expected_credential_revision: int | None = None,
        expected_membership_revision: int | None = None,
        expected_capacity_revision: int | None = None,
    ) -> bool:
        """Return currentness only after exact durable session and authority revalidation."""
        try:
            instant = _utc(now)
            row = _target(self._sessions, SESSION_COLLECTION).find_one(
                {"session_reference": session_reference, "principal_id": principal_id,
                 "tenant_id": tenant_id, "revoked_at": None, "expires_at": {"$gt": instant}},
                session=session,
            )
            if not isinstance(row, dict):
                return False
            if (
                (expected_business_role is not None and row.get("business_role") != expected_business_role)
                or (expected_workspace_id is not None and row.get("workspace_id") != expected_workspace_id)
                or (expected_credential_revision is not None and row.get("credential_revision") != expected_credential_revision)
                or (expected_membership_revision is not None and row.get("membership_revision") != expected_membership_revision)
                or (expected_capacity_revision is not None and row.get("capacity_revision") != expected_capacity_revision)
            ):
                return False
            selected = SelectedMembershipContext(
                principal_id=row["principal_id"], tenant_id=row["tenant_id"],
                business_role=row["business_role"], workspace_id=row["workspace_id"],
                credential_revision=row["credential_revision"],
                membership_revision=row["membership_revision"],
                capacity_revision=row["capacity_revision"],
            )
            self._revalidate(selected, session)
            return True
        except GlobalPrincipalSessionError:
            return False

    def revoke_session(
        self,
        *,
        principal_id: str,
        tenant_id: str,
        session_reference: str,
        session: ClientSession | Any,
        now: datetime | None = None,
    ) -> bool:
        """Revoke one exact principal/tenant/session and all its refresh credentials."""
        _require_transaction(session)
        instant = _utc(now)
        query = {"session_reference": session_reference, "principal_id": principal_id,
                 "tenant_id": tenant_id, "revoked_at": None}
        try:
            result = _target(self._sessions, SESSION_COLLECTION).update_one(
                query, {"$set": {"revoked_at": instant}}, upsert=False, session=session,
            )
            _target(self._refresh, REFRESH_COLLECTION).update_many(
                {"session_reference": session_reference, "principal_id": principal_id,
                 "tenant_id": tenant_id, "revoked_at": None},
                {"$set": {"revoked_at": instant}}, session=session,
            )
        except PyMongoError as error:
            raise GlobalPrincipalSessionUnavailable("GLOBAL_SESSION_REVOCATION_FAILED") from error
        return getattr(result, "matched_count", 0) == 1


__all__ = [
    "VERSION", "SESSION_COLLECTION", "REFRESH_COLLECTION",
    "ACCESS_TTL_SECONDS", "REFRESH_TTL_SECONDS",
    "GlobalPrincipalSessionAuthority", "GlobalPrincipalSessionError",
    "GlobalPrincipalSessionRejected", "GlobalPrincipalSessionUnavailable",
    "GlobalPrincipalSessionReceipt",
]

# ARTIFACT: global_principal_session_authority.py
# VERSION: v1.1.0-GLOBAL-PRINCIPAL-HEADQUARTERS-SESSION
# AUTHORITY BOUNDARY: global selected-membership session and refresh lifecycle only
# TENANT POSTURE: exact principal, canonical tenant, membership and capacity revisions
# FAIL-CLOSED POSTURE: stale, revoked, malformed, mismatched or unavailable authority rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
