"""WILSY OS global-principal membership selection and revision-bound MFA challenges.

TITLE: WILSY OS Membership Selection Challenge Authority
VERSION: v1.0.0-GLOBAL-MEMBERSHIP-SELECTION-CHALLENGE
AUTHORITY: One-time challenge lifecycle and selected-membership snapshot composition only.
EPITOME: Converts a password-verified global principal into one explicit, current
         tenant/business-capacity selection and a one-time MFA challenge.
ABSOLUTE CANONICAL PATH:
    /Users/wilsonkhanyezi/legal-doc-system/tools/eos/auth/membership_selection_challenge.py
COLLABORATION / OWNERSHIP:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd).
    Engineering collaborator: WILSY OS Core Systems Engineering.
CERTIFICATION / UPDATE DATE: 2026-11-03.
CHANGELOG:
    v1.0.0-GLOBAL-MEMBERSHIP-SELECTION-CHALLENGE introduces hashed,
    one-time, expiring membership-selection and MFA challenge records.
    Both transitions re-read global principal, credential revision, exact
    tenant membership, canonical tenant and selected business capacity inside
    a caller-owned Mongo transaction. MFA challenge evidence binds the
    credential, membership and capacity revisions and the EOS workspace.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE:
    Raw challenge secrets are returned once and never persisted or logged.
    Persisted challenge records contain only SHA3-512 token digests and the
    minimum authority snapshot needed for exact revalidation. Challenges expire,
    are purpose-bound and are consumed atomically. No credential or MFA secret
    is copied into a challenge record.
TENANT BOUNDARY:
    The selection challenge is tenant-neutral. A selected challenge is bound
    to one exact canonical tenant, principal, membership revision, business
    role, capacity revision and workspace. No browser-supplied revision is
    trusted and no tenant directory scan is performed.
AUTHORITY BOUNDARY:
    This module owns challenge lifecycle and read-only composition only. It
    creates no principal, membership, business role, permission, legal practice
    authority, entitlement, session, refresh token or access token. The caller
    owns factor verification and final session issuance.
TRANSACTION BOUNDARY:
    All state transitions require an already-active caller-owned Mongo session.
    The caller must abort the transaction on every raised exception and commit
    only after the complete transition succeeds. This module never starts,
    commits, aborts or retries a transaction.
FINANCIAL AUTHORITY BOUNDARY:
    No financial authority. Kennel EOS remains the exclusive financial execution
    authority.
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any, Mapping

from pymongo import ASCENDING, ReturnDocument
from pymongo.client_session import ClientSession
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError

from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_credential_repository import (
    PrincipalCredentialNotFoundError,
    PrincipalCredentialRepository,
    PrincipalCredentialRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus
from tools.eos.auth.tenant_business_role import TenantBusinessRoleStatus
from tools.eos.auth.tenant_business_role_repository import (
    TenantBusinessRoleNotFoundError,
    TenantBusinessRoleRepository,
    TenantBusinessRoleRepositoryError,
)
from tools.eos.auth.tenant_membership import TenantMembershipStatus
from tools.eos.auth.tenant_membership_repository import (
    TenantMembershipNotFoundError,
    TenantMembershipRepository,
    TenantMembershipRepositoryError,
)
from tools.eos.auth.workspace_bootstrap_projection import (
    WorkspaceBootstrapProjectionError,
    resolve_workspace_id,
)
from tools.eos.saas.tenancy.tenant_registry import TenantRegistry, TenantRegistryError


VERSION = "v1.0.0-GLOBAL-MEMBERSHIP-SELECTION-CHALLENGE"
COLLECTION = "eos_authentication_challenges"
DEFAULT_CHALLENGE_TTL_SECONDS = 300
MIN_CHALLENGE_TTL_SECONDS = 30
MAX_CHALLENGE_TTL_SECONDS = 600
SELECTION_PURPOSE = "MEMBERSHIP_SELECTION"
MFA_PURPOSE = "SELECTED_MEMBERSHIP_MFA"


class MembershipSelectionChallengeError(RuntimeError):
    """Base fail-closed error for membership-selection and MFA challenge transitions."""


class MembershipSelectionChallengeRejected(MembershipSelectionChallengeError):
    """A challenge or selected authority is absent, stale, inactive, or inconsistent."""


class MembershipSelectionChallengeUnavailable(MembershipSelectionChallengeError):
    """A required persistence or current-authority source is unavailable."""


@dataclass(frozen=True, slots=True)
class MembershipSelectionChallengeReceipt:
    """One-time global-principal selection capability; secret is never represented."""

    principal_id: str
    credential_revision: int
    expires_at: datetime
    challenge_token: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class SelectedMembershipMfaChallenge:
    """One-time MFA capability bound to exact current membership and capacity revisions."""

    principal_id: str
    tenant_id: str
    business_role: str
    workspace_id: str
    credential_revision: int
    membership_revision: int
    capacity_revision: int
    expires_at: datetime
    challenge_token: str = field(repr=False)


@dataclass(frozen=True, slots=True)
class SelectedMembershipContext:
    """Current server-revalidated authority snapshot after one-time MFA challenge consumption."""

    principal_id: str
    tenant_id: str
    business_role: str
    workspace_id: str
    credential_revision: int
    membership_revision: int
    capacity_revision: int

@dataclass(frozen=True, slots=True)
class MfaChallengeFactorContext:
    """Minimal principal/credential binding read from an unconsumed MFA challenge."""

    principal_id: str
    credential_revision: int

@dataclass(frozen=True, slots=True)
class SelectionChallengeContext:
    """Minimal principal/credential binding read from an unconsumed selection challenge."""

    principal_id: str
    credential_revision: int


def _require_exact_text(value: object, code: str) -> str:
    """Require one non-empty, already-trimmed identifier without normalization."""
    if not isinstance(value, str) or not value or value != value.strip():
        raise MembershipSelectionChallengeRejected(code)
    return value


def _require_revision(value: object, code: str) -> int:
    """Require a bounded, non-negative integer authority revision."""
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or value < 0
        or value > (1 << 63) - 1
    ):
        raise MembershipSelectionChallengeRejected(code)
    return value


def _utc_now(value: datetime | None) -> datetime:
    """Resolve a timezone-aware UTC instant for deterministic challenge expiry."""
    instant = value if value is not None else datetime.now(timezone.utc)
    if not isinstance(instant, datetime) or instant.tzinfo is None or instant.utcoffset() is None:
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_TIME_INVALID")
    return instant.astimezone(timezone.utc)


def _require_transaction(session: ClientSession | Any) -> None:
    """Require an active caller-owned transaction without taking lifecycle ownership."""
    marker = getattr(session, "in_transaction", None) if session is not None else None
    active = marker() if callable(marker) else marker
    if active is not True:
        raise MembershipSelectionChallengeError("AUTH_CHALLENGE_TRANSACTION_REQUIRED")


def _digest(token: str) -> str:
    """Return the SHA3-512 digest of one opaque challenge bearer value."""
    return hashlib.sha3_512(token.encode("utf-8")).hexdigest()


def _validate_ttl(ttl_seconds: int) -> int:
    """Validate a bounded challenge lifetime in seconds."""
    if (
        not isinstance(ttl_seconds, int)
        or isinstance(ttl_seconds, bool)
        or not MIN_CHALLENGE_TTL_SECONDS <= ttl_seconds <= MAX_CHALLENGE_TTL_SECONDS
    ):
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_TTL_INVALID")
    return ttl_seconds


def _target(collection: Collection | None) -> Collection:
    """Resolve the injected or canonical EOS challenge collection without creating indexes."""
    if collection is not None:
        return collection
    from tools.eos.kernel.db import get_database

    database = get_database()
    if database is None:
        raise MembershipSelectionChallengeUnavailable("AUTH_CHALLENGE_PERSISTENCE_UNAVAILABLE")
    return database[COLLECTION]


def _insert_challenge(
    *,
    collection: Collection,
    document: dict[str, object],
    session: ClientSession | Any,
) -> None:
    """Insert one challenge record without upsert or transaction ownership."""
    try:
        collection.insert_one(document, session=session)
    except DuplicateKeyError as error:
        raise MembershipSelectionChallengeUnavailable("AUTH_CHALLENGE_DIGEST_COLLISION") from error
    except PyMongoError as error:
        raise MembershipSelectionChallengeUnavailable("AUTH_CHALLENGE_PERSISTENCE_FAILED") from error


def _consume_challenge(
    *,
    collection: Collection,
    token: str,
    purpose: str,
    now: datetime,
    session: ClientSession | Any,
) -> Mapping[str, object]:
    """Atomically consume one unexpired, purpose-bound opaque challenge digest."""
    if not isinstance(token, str) or not 40 <= len(token) <= 128:
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_INVALID_EXPIRED_OR_CONSUMED")
    try:
        document = collection.find_one_and_update(
            {
                "challenge_digest": _digest(token),
                "purpose": purpose,
                "consumed_at": None,
                "expires_at": {"$gt": now},
            },
            {"$set": {"consumed_at": now}},
            return_document=ReturnDocument.AFTER,
            session=session,
        )
    except PyMongoError as error:
        raise MembershipSelectionChallengeUnavailable("AUTH_CHALLENGE_CONSUMPTION_FAILED") from error
    if not isinstance(document, Mapping):
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_INVALID_EXPIRED_OR_CONSUMED")
    return document


def _require_active_principal(
    principal_id: str,
    principal_repository: Any,
    session: ClientSession | Any,
) -> None:
    """Re-read exact global principal lifecycle state in the caller transaction."""
    try:
        principal = principal_repository.get(principal_id, session=session)
    except PrincipalAuthorityNotFoundError as error:
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_PRINCIPAL_NOT_ACTIVE") from error
    except PrincipalAuthorityRepositoryError as error:
        raise MembershipSelectionChallengeUnavailable("AUTH_CHALLENGE_PRINCIPAL_UNAVAILABLE") from error
    if (
        getattr(principal, "principal_id", None) != principal_id
        or getattr(principal, "status", None) is not PrincipalStatus.ACTIVE
    ):
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_PRINCIPAL_NOT_ACTIVE")


def _require_current_credential(
    principal_id: str,
    expected_revision: int,
    credential_repository: Any,
    session: ClientSession | Any,
) -> None:
    """Re-read global credential state and reject a changed credential epoch."""
    try:
        credential = credential_repository.get_by_principal(principal_id, session=session)
    except PrincipalCredentialNotFoundError as error:
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_CREDENTIAL_REQUIRED") from error
    except PrincipalCredentialRepositoryError as error:
        raise MembershipSelectionChallengeUnavailable("AUTH_CHALLENGE_CREDENTIAL_UNAVAILABLE") from error
    observed_revision = _require_revision(
        getattr(credential, "credential_revision", None),
        "AUTH_CHALLENGE_CREDENTIAL_REVISION_INVALID",
    )
    if credential.principal_id != principal_id or observed_revision != expected_revision:
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_CREDENTIAL_REVISION_STALE")
    if getattr(credential, "mfa_enabled", None) is not True:
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_MFA_ENROLLMENT_REQUIRED")


def _resolve_selected_authority(
    *,
    principal_id: str,
    tenant_id: str,
    business_role: str,
    principal_repository: Any,
    credential_repository: Any,
    membership_repository: Any,
    business_role_repository: Any,
    tenant_resolver: Any,
    credential_revision: int,
    session: ClientSession | Any,
) -> SelectedMembershipContext:
    """Revalidate exact principal, credential, membership, tenant and capacity authorities."""
    _require_active_principal(principal_id, principal_repository, session)
    _require_current_credential(principal_id, credential_revision, credential_repository, session)

    try:
        membership = membership_repository.resolve(principal_id, tenant_id, session=session)
    except TenantMembershipNotFoundError as error:
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_MEMBERSHIP_REQUIRED") from error
    except TenantMembershipRepositoryError as error:
        raise MembershipSelectionChallengeUnavailable("AUTH_CHALLENGE_MEMBERSHIP_UNAVAILABLE") from error
    if (
        getattr(membership, "principal_id", None) != principal_id
        or getattr(membership, "tenant_id", None) != tenant_id
        or getattr(membership, "status", None) is not TenantMembershipStatus.ACTIVE
    ):
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_MEMBERSHIP_INACTIVE_OR_MISMATCHED")
    membership_revision = _require_revision(
        getattr(membership, "revision", None),
        "AUTH_CHALLENGE_MEMBERSHIP_REVISION_INVALID",
    )

    try:
        tenant = tenant_resolver(tenant_id, session=session)
    except TenantRegistryError as error:
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_TENANT_NOT_ACTIVE") from error
    if getattr(tenant, "tenant_id", None) != tenant_id:
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_TENANT_MISMATCH")

    try:
        capacity = business_role_repository.resolve_business_role(
            principal_id,
            tenant_id,
            business_role,
            session=session,
        )
    except TenantBusinessRoleNotFoundError as error:
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_CAPACITY_REQUIRED") from error
    except TenantBusinessRoleRepositoryError as error:
        raise MembershipSelectionChallengeUnavailable("AUTH_CHALLENGE_CAPACITY_UNAVAILABLE") from error
    if (
        getattr(capacity, "principal_id", None) != principal_id
        or getattr(capacity, "tenant_id", None) != tenant_id
        or getattr(capacity, "business_role", None) != business_role
        or getattr(capacity, "status", None) is not TenantBusinessRoleStatus.ACTIVE
    ):
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_CAPACITY_INACTIVE_OR_MISMATCHED")
    capacity_revision = _require_revision(
        getattr(capacity, "revision", None),
        "AUTH_CHALLENGE_CAPACITY_REVISION_INVALID",
    )

    try:
        workspace_id = resolve_workspace_id(business_role)
    except WorkspaceBootstrapProjectionError as error:
        raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_WORKSPACE_UNMAPPED") from error

    return SelectedMembershipContext(
        principal_id=principal_id,
        tenant_id=tenant_id,
        business_role=business_role,
        workspace_id=workspace_id,
        credential_revision=credential_revision,
        membership_revision=membership_revision,
        capacity_revision=capacity_revision,
    )


class MembershipSelectionChallengeService:
    """Issue and consume one-time membership-selection and selected-capacity MFA challenges.

    Authority is limited to challenge lifecycle and current authority revalidation.
    Every transition requires a caller-owned active Mongo transaction. This service
    never creates principals, memberships, business capacities, permissions,
    sessions, refresh tokens or access tokens. It does not verify TOTP factors.
    """

    def __init__(
        self,
        *,
        collection: Collection | None = None,
        principal_repository: Any = None,
        credential_repository: Any = None,
        membership_repository: Any = None,
        business_role_repository: Any = None,
        tenant_resolver: Any = None,
    ) -> None:
        """Bind existing EOS authorities and an optional challenge collection.

        Injected repositories and resolver are read-only dependencies. No index,
        collection, tenant, membership or business-capacity creation occurs here.
        """
        self._collection = collection
        self._principals = principal_repository or PrincipalAuthorityRepository()
        self._credentials = credential_repository or PrincipalCredentialRepository()
        self._memberships = membership_repository or TenantMembershipRepository()
        self._business_roles = business_role_repository or TenantBusinessRoleRepository()
        self._tenant_resolver = tenant_resolver or TenantRegistry.resolve_canonical_tenant

    @staticmethod
    def ensure_indexes(collection: Collection) -> None:
        """Create challenge digest uniqueness and expiry TTL indexes at governed startup only."""
        collection.create_index(
            [("challenge_digest", ASCENDING)],
            unique=True,
            name="eos_authentication_challenge_digest_unique",
        )
        collection.create_index(
            [("expires_at", ASCENDING)],
            expireAfterSeconds=0,
            name="eos_authentication_challenge_expiry_ttl",
        )

    def issue_membership_selection_challenge(
        self,
        *,
        principal_id: str,
        credential_revision: int,
        session: ClientSession | Any,
        now: datetime | None = None,
        ttl_seconds: int = DEFAULT_CHALLENGE_TTL_SECONDS,
    ) -> MembershipSelectionChallengeReceipt:
        """Issue one tenant-neutral selection capability after global credential verification.

        The exact ACTIVE principal and current global credential revision are
        re-read in the caller transaction. The supplied revision is only a
        comparison value from the successful credential-verification result;
        it cannot override the durable revision. A raw random capability is
        returned once while only its SHA3-512 digest is persisted.
        """
        _require_transaction(session)
        principal = _require_exact_text(principal_id, "AUTH_CHALLENGE_PRINCIPAL_INVALID")
        revision = _require_revision(credential_revision, "AUTH_CHALLENGE_CREDENTIAL_REVISION_INVALID")
        instant = _utc_now(now)
        ttl = _validate_ttl(ttl_seconds)
        _require_active_principal(principal, self._principals, session)
        _require_current_credential(principal, revision, self._credentials, session)

        token = secrets.token_urlsafe(48)
        expires_at = instant + timedelta(seconds=ttl)
        _insert_challenge(
            collection=_target(self._collection),
            document={
                "challenge_digest": _digest(token),
                "purpose": SELECTION_PURPOSE,
                "principal_id": principal,
                "credential_revision": revision,
                "issued_at": instant,
                "expires_at": expires_at,
                "consumed_at": None,
                "schema_version": 1,
            },
            session=session,
        )
        return MembershipSelectionChallengeReceipt(
            principal_id=principal,
            credential_revision=revision,
            expires_at=expires_at,
            challenge_token=token,
        )

    def select_membership_and_issue_mfa_challenge(
        self,
        *,
        selection_challenge_token: str,
        tenant_id: str,
        business_role: str,
        session: ClientSession | Any,
        now: datetime | None = None,
        ttl_seconds: int = DEFAULT_CHALLENGE_TTL_SECONDS,
    ) -> SelectedMembershipMfaChallenge:
        """Consume a selection capability and issue MFA bound to one exact capacity.

        Browser input is limited to the opaque selection capability, canonical
        tenant ID and explicit business-role choice. Membership, capacity,
        workspace and all revisions are re-read from EOS inside the same caller
        transaction. An exception requires the caller to abort that transaction,
        restoring the selection challenge's unconsumed state.
        """
        _require_transaction(session)
        tenant = _require_exact_text(tenant_id, "AUTH_CHALLENGE_TENANT_INVALID")
        role = _require_exact_text(business_role, "AUTH_CHALLENGE_CAPACITY_INVALID")
        instant = _utc_now(now)
        ttl = _validate_ttl(ttl_seconds)
        consumed = _consume_challenge(
            collection=_target(self._collection),
            token=selection_challenge_token,
            purpose=SELECTION_PURPOSE,
            now=instant,
            session=session,
        )
        principal = _require_exact_text(
            consumed.get("principal_id"),
            "AUTH_CHALLENGE_PRINCIPAL_INVALID",
        )
        credential_revision = _require_revision(
            consumed.get("credential_revision"),
            "AUTH_CHALLENGE_CREDENTIAL_REVISION_INVALID",
        )
        selected = _resolve_selected_authority(
            principal_id=principal,
            tenant_id=tenant,
            business_role=role,
            principal_repository=self._principals,
            credential_repository=self._credentials,
            membership_repository=self._memberships,
            business_role_repository=self._business_roles,
            tenant_resolver=self._tenant_resolver,
            credential_revision=credential_revision,
            session=session,
        )

        token = secrets.token_urlsafe(48)
        expires_at = instant + timedelta(seconds=ttl)
        _insert_challenge(
            collection=_target(self._collection),
            document={
                "challenge_digest": _digest(token),
                "purpose": MFA_PURPOSE,
                "principal_id": selected.principal_id,
                "credential_revision": selected.credential_revision,
                "tenant_id": selected.tenant_id,
                "membership_revision": selected.membership_revision,
                "business_role": selected.business_role,
                "capacity_revision": selected.capacity_revision,
                "workspace_id": selected.workspace_id,
                "issued_at": instant,
                "expires_at": expires_at,
                "consumed_at": None,
                "schema_version": 1,
            },
            session=session,
        )
        return SelectedMembershipMfaChallenge(
            principal_id=selected.principal_id,
            tenant_id=selected.tenant_id,
            business_role=selected.business_role,
            workspace_id=selected.workspace_id,
            credential_revision=selected.credential_revision,
            membership_revision=selected.membership_revision,
            capacity_revision=selected.capacity_revision,
            expires_at=expires_at,
            challenge_token=token,
        )

    def get_selection_challenge_context(
        self,
        *,
        selection_challenge_token: str,
        session: ClientSession | Any,
        now: datetime | None = None,
    ) -> SelectionChallengeContext:
        """Read an unconsumed selection challenge for bounded membership pagination."""
        _require_transaction(session)
        instant = _utc_now(now)
        if not isinstance(selection_challenge_token, str) or not 40 <= len(selection_challenge_token) <= 128:
            raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_INVALID_EXPIRED_OR_CONSUMED")
        try:
            document = _target(self._collection).find_one(
                {
                    "challenge_digest": _digest(selection_challenge_token),
                    "purpose": SELECTION_PURPOSE,
                    "consumed_at": None,
                    "expires_at": {"$gt": instant},
                },
                session=session,
            )
        except PyMongoError as error:
            raise MembershipSelectionChallengeUnavailable("AUTH_CHALLENGE_READ_FAILED") from error
        if not isinstance(document, Mapping):
            raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_INVALID_EXPIRED_OR_CONSUMED")
        principal = _require_exact_text(
            document.get("principal_id"),
            "AUTH_CHALLENGE_PRINCIPAL_INVALID",
        )
        revision = _require_revision(
            document.get("credential_revision"),
            "AUTH_CHALLENGE_CREDENTIAL_REVISION_INVALID",
        )
        _require_active_principal(principal, self._principals, session)
        _require_current_credential(principal, revision, self._credentials, session)
        return SelectionChallengeContext(principal_id=principal, credential_revision=revision)

    def get_mfa_challenge_factor_context(
        self,
        *,
        mfa_challenge_token: str,
        session: ClientSession | Any,
        now: datetime | None = None,
    ) -> MfaChallengeFactorContext:
        """Read the exact unconsumed MFA challenge binding inside the caller transaction.

        This read does not consume the challenge. It lets the caller verify the
        enrolled principal factor in the same transaction before the subsequent
        consume-and-session transition. A failed factor must abort the transaction.
        """
        _require_transaction(session)
        instant = _utc_now(now)
        if not isinstance(mfa_challenge_token, str) or not 40 <= len(mfa_challenge_token) <= 128:
            raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_INVALID_EXPIRED_OR_CONSUMED")
        try:
            document = _target(self._collection).find_one(
                {
                    "challenge_digest": _digest(mfa_challenge_token),
                    "purpose": MFA_PURPOSE,
                    "consumed_at": None,
                    "expires_at": {"$gt": instant},
                },
                session=session,
            )
        except PyMongoError as error:
            raise MembershipSelectionChallengeUnavailable("AUTH_CHALLENGE_READ_FAILED") from error
        if not isinstance(document, Mapping):
            raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_INVALID_EXPIRED_OR_CONSUMED")
        principal = _require_exact_text(
            document.get("principal_id"),
            "AUTH_CHALLENGE_PRINCIPAL_INVALID",
        )
        revision = _require_revision(
            document.get("credential_revision"),
            "AUTH_CHALLENGE_CREDENTIAL_REVISION_INVALID",
        )
        return MfaChallengeFactorContext(principal_id=principal, credential_revision=revision)

    def consume_mfa_challenge_after_factor_verification(
        self,
        *,
        mfa_challenge_token: str,
        session: ClientSession | Any,
        now: datetime | None = None,
    ) -> SelectedMembershipContext:
        """Consume MFA challenge after caller-verified factor and revalidate all revisions.

        The caller must verify the enrolled factor for the challenge principal
        before invoking this method. This method consumes the opaque challenge
        once, then re-reads principal, credential, membership, canonical tenant
        and the exact selected business capacity in the caller transaction.
        It returns only a current immutable selection snapshot; it issues no
        session or access token. Any exception requires transaction abort.
        """
        _require_transaction(session)
        instant = _utc_now(now)
        consumed = _consume_challenge(
            collection=_target(self._collection),
            token=mfa_challenge_token,
            purpose=MFA_PURPOSE,
            now=instant,
            session=session,
        )
        principal = _require_exact_text(
            consumed.get("principal_id"),
            "AUTH_CHALLENGE_PRINCIPAL_INVALID",
        )
        tenant = _require_exact_text(
            consumed.get("tenant_id"),
            "AUTH_CHALLENGE_TENANT_INVALID",
        )
        role = _require_exact_text(
            consumed.get("business_role"),
            "AUTH_CHALLENGE_CAPACITY_INVALID",
        )
        credential_revision = _require_revision(
            consumed.get("credential_revision"),
            "AUTH_CHALLENGE_CREDENTIAL_REVISION_INVALID",
        )
        expected_membership_revision = _require_revision(
            consumed.get("membership_revision"),
            "AUTH_CHALLENGE_MEMBERSHIP_REVISION_INVALID",
        )
        expected_capacity_revision = _require_revision(
            consumed.get("capacity_revision"),
            "AUTH_CHALLENGE_CAPACITY_REVISION_INVALID",
        )
        expected_workspace = _require_exact_text(
            consumed.get("workspace_id"),
            "AUTH_CHALLENGE_WORKSPACE_INVALID",
        )
        selected = _resolve_selected_authority(
            principal_id=principal,
            tenant_id=tenant,
            business_role=role,
            principal_repository=self._principals,
            credential_repository=self._credentials,
            membership_repository=self._memberships,
            business_role_repository=self._business_roles,
            tenant_resolver=self._tenant_resolver,
            credential_revision=credential_revision,
            session=session,
        )
        if (
            selected.membership_revision != expected_membership_revision
            or selected.capacity_revision != expected_capacity_revision
            or selected.workspace_id != expected_workspace
        ):
            raise MembershipSelectionChallengeRejected("AUTH_CHALLENGE_SELECTED_AUTHORITY_STALE")
        return selected


__all__ = [
    "VERSION",
    "COLLECTION",
    "DEFAULT_CHALLENGE_TTL_SECONDS",
    "MembershipSelectionChallengeError",
    "MembershipSelectionChallengeRejected",
    "MembershipSelectionChallengeUnavailable",
    "MembershipSelectionChallengeReceipt",
    "SelectedMembershipMfaChallenge",
    "SelectedMembershipContext",
    "MfaChallengeFactorContext",
    "SelectionChallengeContext",
    "MembershipSelectionChallengeService",
]

# ARTIFACT: membership_selection_challenge.py
# VERSION: v1.0.0-GLOBAL-MEMBERSHIP-SELECTION-CHALLENGE
# AUTHORITY BOUNDARY: one-time challenge lifecycle and revision-bound selection only
# TENANT POSTURE: tenant-neutral selection token; selected MFA challenge binds exact principal/tenant/capacity
# FAIL-CLOSED POSTURE: expired, reused, stale, malformed, inactive, ambiguous, and unavailable authority rejects
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
