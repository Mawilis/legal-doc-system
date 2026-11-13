"""Wilsy OS canonical authentication registry.

TITLE: WILSY OS Authentication Registry
VERSION: v1.13.0-CONSOLIDATION-STRICT-IDENTITY-HYDRATION
AUTHORITY: Wilsy OS Core Governance
EPITOME: Owns password, JWT, OTP, session, and refresh-token business semantics
         while consuming the caller-established canonical Kernel database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/auth_registry.py
COLLABORATION / OWNERSHIP: Auth router delegates here; tools.eos.kernel.db owns
                           the sole Mongo lifecycle and connection recovery.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG:
  v1.13.0-CONSOLIDATION-STRICT-IDENTITY-HYDRATION — Rejects malformed canonical identities and non-BSON legacy IDs; preserves established absent/null user_id ObjectId compatibility without writes; denies canonical/legacy collisions; sanitizes opt-in legacy diagnostics; validates hydration before tenant-bound auth updates.
  v1.12.0-P3-R3G-C6-SESSION-BSON-UTC-HYDRATION — Normalizes only valid Mongo-hydrated session expiry datetimes and observation datetimes to aware UTC before currentness comparison, preserving exact tenant/principal/reference binding, caller-owned session propagation, and fail-closed non-datetime handling.
  v1.11.0-D15G-DEV-TRANSACTIONAL-TENANT-RESOLUTION — Extends the D15G developer-persona transaction seam so canonical
    tenant validation for register_user participates in the exact caller-owned
    ClientSession before the credential insert. No-session behavior remains
    unchanged; AuthRegistry still starts, commits, aborts, and retries no
    transaction and gains no membership, role, authorization, or financial
    authority.
  v1.10.0-D15G-DEV-TRANSACTIONAL-USER-REGISTRATION — Extends canonical user registration with an optional caller-owned
    Mongo ClientSession so higher-level admission/provisioning orchestration can
    compose the credential row atomically with independently governed principal,
    membership, business-role, and authorization-role authorities. The registry
    still owns no transaction, performs no role grant, creates no final session,
    and preserves the existing no-session registration behavior exactly.
  v1.4.0-R1D-B0F-B3B-CANONICAL-TENANT-SOURCE — Added one authoritative
    TenantRegistry resolver before user hydration, user creation, JWT issuance,
    session persistence, and refresh-token validation; removed tenant fallback
    projection and reordered refresh persistence after session persistence.
  v1.5.0-R1D-B0F-B4-R2-CANONICAL-TOKEN-CONTRACT — Delegates access-token
    encoding to jwt_provider, removes the JWT_SECRET fallback, and emits the
    canonical identity_id/tenant_id/roles/permissions claim contract.
  v1.6.0-R1D-B0F-B4-R6-PRINCIPAL-AUTHORITY-GATE — Final session issuance now
    consumes a durable ACTIVE PrincipalAuthority; login never creates one.
  v1.7.0-R10C2B-TENANT-BEARING-REFRESH-AUTHORITY — Canonical Python refresh
    creation now persists validated tenant_id, validation distinguishes
    temporary missing-field legacy compatibility from corrupt-present state,
    and tenant-scoped revocation accepts caller sessions without owning a
    transaction. No migration, legacy rejection, credential revision, or JWT
    cutover is performed by this version.
  v1.8.0-R10C2F1-CREDENTIAL-REVISION-AUTHORITY — Adds the durable
    credential_revision baseline and fail-closed hydration, exact
    tenant/principal revision reads, caller-session password/revision CAS,
    and tenant-scoped session revocation. Missing legacy revision reads as
    zero without write-on-read; malformed values fail closed. This version
    does not change JWT issuance/verification, reset orchestration, refresh
    compatibility, Node authority, or transaction ownership.
  v1.9.0-R10C2F6-ACCESS-PREAUTH-ISSUER-BINDING — Adds explicit ACCESS and
    PRE_AUTH issuer seams, binds create_session ACCESS tokens to a fresh exact
    durable credential revision read, propagates caller sessions through that
    read and existing persistence path, and preserves generic generate_jwt as
    a transitional unspecified-purpose compatibility path. Verification
    enforcement, router migration, reset orchestration, and Node authority
    remain outside this version.
  v1.3.0-LEGACY-ID-SYMMETRY — Unified canonical and legacy user identity
    resolution for reads and updates using a validated exact Mongo _id fallback;
    existing OTP identity and enrollment semantics remain unchanged.
  v1.2.0-CANONICAL-DB-BINDING — Removed private Mongo lifecycle and resolved
    every collection lazily from the canonical Kernel database accessor; database
    absence now raises a PyMongoError-compatible failure.
  v1.1.2-FALLBACK-ID — Missing durable user_id falls back to Mongo _id.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Credential material is never logged or returned;
                            unavailable persistence fails closed.
TENANT BOUNDARY: Tenant, role, and permission facts remain durable user fields;
                 this registry does not infer or broaden tenant authority.
AUTHORITY BOUNDARY: Authentication business semantics only; Kernel DB owns
                    connection lifecycle, while auth_router owns HTTP semantics.
FINANCIAL AUTHORITY BOUNDARY: None; Kennel EOS exclusively owns financial execution.
"""

import bcrypt
import pyotp
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, List, Any
import uuid
import logging
import os

from bson import ObjectId
from pymongo.errors import ConnectionFailure, DuplicateKeyError, PyMongoError

from ..domain.auth import User, Session, AuthRequest, VerifyOTPRequest
from ..tenancy.tenant_registry import TenantRegistry
from tools.eos.kernel import db as kernel_db
from tools.eos.auth.jwt_provider import TokenPurpose, create_access_token
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus

VERSION = "v1.13.0-CONSOLIDATION-STRICT-IDENTITY-HYDRATION"

# Configuration
JWT_EXPIRY_HOURS = 24
BCRYPT_ROUNDS = 12
CREDENTIAL_REVISION_FIELD = "credential_revision"
CREDENTIAL_REVISION_MAX = (1 << 63) - 1

logger = logging.getLogger(__name__)


class AuthRegistryTenantError(RuntimeError):
    """Expose a stable authentication integrity code without persisted identity.

    Invalid tenant, identity, revision or authority state must not hydrate a user,
    mutate auth state or issue final credentials. The generic message discloses
    no tenant, principal, credential or financial facts. HTTP translation remains
    caller-owned; this exception performs no repair or transaction lifecycle.
    """

    def __init__(self, code: str) -> None:
        """Retain only a registry-owned code and non-identifying human message."""
        super().__init__(code)
        self.error = code
        self.message = "Authentication identity, tenant or authority could not be verified."


def _validated_credential_revision(value: Any, *, present: bool = True) -> int:
    """Validate one durable credential revision without coercion or leakage.

    A missing field is represented by ``present=False`` and is the explicitly
    supported legacy baseline.  Every present value must be a non-boolean,
    non-negative Python integer within MongoDB's signed int64 range.  The
    returned code-only exception is safe for authentication callers and does
    not retain a user document, password, or hash.
    """
    if not present:
        return 0
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
        or value > CREDENTIAL_REVISION_MAX
    ):
        raise AuthRegistryTenantError("AUTH_CREDENTIAL_REVISION_INVALID")
    return value

class AuthRegistry:
    """
    Own legacy authentication semantics using the caller-established Kernel DB.

    TenantRegistry validates tenant truth; PrincipalAuthority admits final
    sessions. Global Principal credentials, membership, capacity and KMS MFA
    remain separate authorities. No read silently migrates identity, and caller
    sessions never transfer transaction ownership to this registry.
    """

    def __init__(self, tenant_registry: Optional[TenantRegistry] = None):
        """Bind the caller-supplied tenant resolver or canonical TenantRegistry.

        No connection, index, tenant, identity, permission, or transaction is
        created. Kernel owns persistence lifecycle; dependency absence fails
        closed when the first governed operation resolves it."""
        self.tenant_registry = tenant_registry or TenantRegistry

    def _require_canonical_tenant(
        self,
        tenant_reference: object,
        *,
        allow_alias: bool = False,
        session: Any = None,
    ) -> Any:
        """Require one ACTIVE canonical tenant while preserving caller session scope.

        When session is absent, the established resolver call remains unchanged.
        When supplied, the exact caller-owned session is forwarded to the
        canonical TenantRegistry resolver so transactional callers observe tenant
        truth and credential persistence through one Mongo transaction view.
        This helper never starts, commits, aborts, or retries a transaction and
        grants no membership, role, permission, or financial authority.
        """
        if not isinstance(tenant_reference, str) or not tenant_reference.strip():
            raise AuthRegistryTenantError("AUTH_TENANT_CANONICAL_INVALID")
        resolver = getattr(self.tenant_registry, "resolve_canonical_tenant", None)
        if not callable(resolver):
            resolver = TenantRegistry.resolve_canonical_tenant
        try:
            if session is None:
                tenant = resolver(
                    tenant_reference.strip(),
                    allow_alias=allow_alias,
                )
            else:
                tenant = resolver(
                    tenant_reference.strip(),
                    allow_alias=allow_alias,
                    session=session,
                )
        except Exception as exc:
            raise AuthRegistryTenantError(
                "AUTH_TENANT_CANONICAL_INVALID"
            ) from exc
        tenant_id = getattr(tenant, "tenant_id", None)
        if not isinstance(tenant_id, str) or not tenant_id.strip():
            raise AuthRegistryTenantError("AUTH_TENANT_CANONICAL_INVALID")
        return tenant

    def _collection(self, collection_name: str) -> Any:
        """Resolve one auth collection from the live canonical Kernel database.

        The lookup is deliberately performed for every operation.  Kernel startup
        may establish or re-anchor the database after this module is imported;
        caching a client, database, collection, or unavailable ``None`` would
        create a second lifecycle and make recovery require module re-import.
        """
        database = kernel_db.get_database()
        if database is None:
            raise ConnectionFailure("AUTH_DATABASE_UNAVAILABLE")
        return database[collection_name]

    @staticmethod
    def _call_collection(
        collection: Any,
        method_name: str,
        *args: Any,
        session: Any = None,
        **kwargs: Any,
    ) -> Any:
        """Invoke one PyMongo operation while preserving caller session ownership.

        The registry never starts, commits, aborts, or retries a transaction.
        When a caller supplies a ``ClientSession`` it is forwarded unchanged;
        absent sessions preserve compatibility with existing test doubles and
        non-transactional callers.
        """
        operation = getattr(collection, method_name)
        if session is None:
            return operation(*args, **kwargs)
        return operation(*args, session=session, **kwargs)

    @staticmethod
    def _document_credential_revision(document: Dict[str, Any]) -> int:
        """Hydrate and validate a document's credential epoch.

        The absent field is a read-only legacy baseline of zero.  This helper
        never writes a migration and never exposes the underlying document.
        """
        return _validated_credential_revision(
            document.get(CREDENTIAL_REVISION_FIELD),
            present=CREDENTIAL_REVISION_FIELD in document,
        )

    @staticmethod
    def _validated_legacy_object_id(user_id: str) -> Optional[ObjectId]:
        """Return a validated Mongo identity for legacy user documents.

        Legacy documents may have no durable ``user_id`` and are represented by
        the string form of their Mongo ``_id``.  Only a valid ObjectId string is
        accepted for that fallback; arbitrary input is never coerced into a
        mutation predicate.
        """
        if not isinstance(user_id, str) or not ObjectId.is_valid(user_id):
            return None
        try:
            return ObjectId(user_id)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _document_user_id(doc: Dict[str, Any]) -> str:
        """Validate persisted identity without coercion, mutation, or disclosure.

        Established absent/null user_id rows may retain their actual BSON
        ObjectId identity. Empty strings, false booleans, numbers, containers,
        whitespace, control characters and non-ObjectId fallbacks are corrupt
        state. In particular, None can never become the string "None".
        This compatibility identity is not a Global Principal credential or
        evidence of membership, MFA, session, or financial authority.
        """
        value = doc.get("user_id")
        if value is None:
            mongo_id = doc.get("_id")
            if isinstance(mongo_id, ObjectId):
                return str(mongo_id)
        elif (
            isinstance(value, str)
            and value
            and value == value.strip()
            and not any(ord(character) < 32 or ord(character) == 127 for character in value)
        ):
            return value
        logger.error("AUTH_PRINCIPAL_IDENTITY_INVALID")
        raise AuthRegistryTenantError("AUTH_PRINCIPAL_IDENTITY_INVALID")

    def _resolve_user_identity(
        self, user_id: str, *, session: Any = None
    ) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Resolve an exact authentication identity without canonical precedence.

        This platform credential lookup predates tenant selection. Tenant-bound
        commands use _resolve_exact_credential_identity. Both canonical and
        ObjectId paths are checked when applicable; competing rows fail closed
        without disclosing either tenant. A legacy row cannot redirect to a
        different persisted user_id. The caller owns the optional session.
        """
        if not isinstance(user_id, str) or not user_id or user_id != user_id.strip():
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_CANONICAL_INVALID")
        users = self._collection("users")
        canonical_filter = {"user_id": user_id}
        canonical_document = self._call_collection(
            users, "find_one", canonical_filter, session=session
        )
        object_id = self._validated_legacy_object_id(user_id)
        legacy_document = None
        legacy_filter = {"_id": object_id}
        if object_id is not None:
            legacy_document = self._call_collection(
                users, "find_one", legacy_filter, session=session
            )
        if canonical_document is not None and legacy_document is not None:
            if canonical_document.get("_id") != legacy_document.get("_id"):
                logger.error("AUTH_PRINCIPAL_IDENTITY_AMBIGUOUS")
                raise AuthRegistryTenantError("AUTH_PRINCIPAL_IDENTITY_AMBIGUOUS")
        if canonical_document is not None:
            return canonical_document, canonical_filter
        if legacy_document is None:
            return None, None
        if self._document_user_id(legacy_document) != user_id:
            logger.error("AUTH_PRINCIPAL_IDENTITY_AMBIGUOUS")
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_IDENTITY_AMBIGUOUS")
        return legacy_document, legacy_filter

    def _resolve_exact_credential_identity(
        self,
        tenant_id: str,
        user_id: str,
        *,
        session: Any = None,
    ) -> tuple[Dict[str, Any], Dict[str, Any], User, int]:
        """Read one exact tenant/principal credential document.

        The query is always tenant-scoped and uses only canonical ``user_id``
        or the already-governed validated Mongo ``_id`` fallback.  When an
        ObjectId-shaped input could identify both paths, both exact documents
        are checked and a collision fails closed.  No email, username, or
        tenantless fallback can authorize credential mutation.
        """
        canonical = self._require_canonical_tenant(tenant_id)
        canonical_tenant_id = canonical.tenant_id
        if not isinstance(user_id, str) or not user_id.strip():
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_CANONICAL_INVALID")
        users = self._collection("users")
        canonical_filter = {
            "user_id": user_id,
            "tenantId": canonical_tenant_id,
        }
        canonical_document = self._call_collection(
            users, "find_one", canonical_filter, session=session
        )

        object_id = self._validated_legacy_object_id(user_id)
        legacy_filter: Optional[Dict[str, Any]] = None
        legacy_document: Optional[Dict[str, Any]] = None
        if object_id is not None:
            legacy_filter = {"_id": object_id, "tenantId": canonical_tenant_id}
            legacy_document = self._call_collection(
                users, "find_one", legacy_filter, session=session
            )

        if canonical_document is not None and legacy_document is not None:
            canonical_identity = canonical_document.get("_id")
            legacy_identity = legacy_document.get("_id")
            if canonical_identity != legacy_identity:
                raise AuthRegistryTenantError("AUTH_PRINCIPAL_IDENTITY_AMBIGUOUS")

        if canonical_document is not None:
            document = canonical_document
            identity_filter = canonical_filter
        elif legacy_document is not None and legacy_filter is not None:
            persisted_user_id = legacy_document.get("user_id")
            if persisted_user_id not in (None, "", user_id):
                raise AuthRegistryTenantError("AUTH_PRINCIPAL_IDENTITY_AMBIGUOUS")
            document = legacy_document
            identity_filter = legacy_filter
        else:
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_CREDENTIAL_NOT_FOUND")

        user = self._doc_to_user(document, session=session)
        if user.tenantId != canonical_tenant_id or user.id != user_id:
            raise AuthRegistryTenantError("AUTH_CREDENTIAL_TENANT_OR_ID_MISMATCH")
        revision = self._document_credential_revision(document)
        return document, identity_filter, user, revision

    def hash_password(self, password: str) -> str:
        """Return a bcrypt verifier using the configured work factor.

        Consumes caller-supplied password material only in memory, logs nothing,
        and performs no persistence, tenant lookup, or authority grant. Encoding
        and bcrypt errors propagate to the owning authentication boundary."""
        salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Compare a password with its durable bcrypt verifier.

        The authentication router owns tenant binding and response translation.
        No state changes or authority are created; malformed verifier errors
        propagate and must never become successful authentication."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def _canonical_jwt_claims(
        self, user_id: str, tenant_id: str, role: str, permissions: List[str]
    ) -> Dict[str, Any]:
        """Validate the existing durable identity projection for JWT issuers."""
        canonical = self._require_canonical_tenant(tenant_id)
        canonical_tenant_id = canonical.tenant_id
        if not isinstance(user_id, str) or not user_id.strip():
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_CANONICAL_INVALID")
        if not isinstance(role, str) or not role.strip():
            raise AuthRegistryTenantError("AUTH_ROLE_CANONICAL_INVALID")
        if not isinstance(permissions, list) or any(
            not isinstance(permission, str) or not permission.strip()
            for permission in permissions
        ):
            raise AuthRegistryTenantError("AUTH_PERMISSIONS_CANONICAL_INVALID")
        return {
            "identity_id": user_id.strip(),
            "tenant_id": canonical_tenant_id,
            "roles": [role.strip()],
            "permissions": list(permissions),
        }

    def generate_jwt(self, user_id: str, tenant_id: str, role: str, permissions: List[str]) -> str:
        """Generate the transitional unspecified-purpose JWT.

        This compatibility seam preserves the current MFA/3FA router callers.
        It validates the established tenant and identity projection but does not
        claim ACCESS or PRE_AUTH purpose and does not read credential revision.
        Callers must migrate to the explicit issuer methods before verification
        enforcement is activated. No transaction or persistence lifecycle is
        owned beyond the canonical JWT provider.
        """
        # AuthRegistry owns durable user/tenant admission; jwt_provider owns
        # the sole cryptographic encoder and signing-secret configuration.
        return create_access_token(
            self._canonical_jwt_claims(user_id, tenant_id, role, permissions),
            expires_in_seconds=JWT_EXPIRY_HOURS * 60 * 60,
        )

    def generate_access_jwt(
        self,
        user_id: str,
        tenant_id: str,
        role: str,
        permissions: List[str],
        *,
        session: Any = None,
        session_reference: str | None = None,
    ) -> str:
        """Issue full ACCESS authority bound to fresh durable credential state.

        The exact canonical tenant and user identity are validated using the
        existing AuthRegistry authority. The credential revision is then read
        from the tenant-scoped durable user through ``get_credential_revision``;
        caller-provided user snapshots cannot assert it. A supplied Mongo
        session is forwarded unchanged and remains owned by the caller. This
        method signs only an ACCESS JWT and does not verify tokens, create a
        session, revoke authority, or own a transaction.
        """
        claims = self._canonical_jwt_claims(user_id, tenant_id, role, permissions)
        revision = self.get_credential_revision(
            claims["tenant_id"], claims["identity_id"], session=session
        )
        if session_reference is not None:
            if not isinstance(session_reference, str) or not session_reference.startswith("WILSYSESSION-") or len(session_reference) > 128:
                raise AuthRegistryTenantError("AUTH_SESSION_REFERENCE_INVALID")
            claims["session_reference"] = session_reference
        return create_access_token(
            claims,
            expires_in_seconds=JWT_EXPIRY_HOURS * 60 * 60,
            token_purpose=TokenPurpose.ACCESS,
            credential_revision=revision,
        )

    def generate_pre_auth_jwt(
        self, user_id: str, tenant_id: str, role: str, permissions: List[str]
    ) -> str:
        """Issue explicit PRE_AUTH challenge authority without a revision read.

        This seam preserves the current MFA/3FA identity projection while
        marking its purpose explicitly. It does not read users for credential
        revision, create sessions or refresh tokens, verify tokens, or own a
        transaction. The router migration is a separate gate.
        """
        return create_access_token(
            self._canonical_jwt_claims(user_id, tenant_id, role, permissions),
            expires_in_seconds=JWT_EXPIRY_HOURS * 60 * 60,
            token_purpose=TokenPurpose.PRE_AUTH,
        )

    def generate_refresh_token(
        self,
        user_id: str,
        tenant_id: Optional[str] = None,
        *,
        session: Any = None,
    ) -> str:
        """Create one tenant-bound raw refresh token for a canonical principal.

        ``user_id`` is the existing application identity (canonical ``user_id``
        or the validated legacy Mongo ``_id`` string).  ``tenant_id`` is
        validated against the durable hydrated user; omission is retained only
        for backward-compatible callers and derives the same durable tenant,
        so no new tenantless row can be written.  A supplied session is passed
        unchanged to the refresh insert; transaction lifecycle remains with the
        caller.  The raw bearer token is returned only to the existing caller,
        never logged or exposed by the registry's diagnostics.
        """
        user = self.get_user_by_id(user_id, session=session)
        if user is None:
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_CANONICAL_INVALID")
        canonical_tenant_id = user.tenantId
        if tenant_id is not None:
            canonical = self._require_canonical_tenant(tenant_id)
            if canonical.tenant_id != canonical_tenant_id:
                raise AuthRegistryTenantError("AUTH_TENANT_CANONICAL_INVALID")
            canonical_tenant_id = canonical.tenant_id
        token = str(uuid.uuid4())
        self._call_collection(
            self._collection("refresh_tokens"),
            "insert_one",
            {
                "token": token,
                "user_id": user.id,
                "tenant_id": canonical_tenant_id,
                "expires": datetime.utcnow() + timedelta(days=7),
            },
            session=session,
        )
        return token

    def _require_active_principal_authority(self, principal_id: str) -> PrincipalAuthority:
        """Require durable ACTIVE authority before final session/token issuance.

        This is a read-only consumer gate.  It deliberately does not provision
        missing authority, infer status from ``users`` or roles, or own a
        transaction.  Initial creation belongs exclusively to
        ``principal_authority_provisioning``.
        """
        try:
            authority = PrincipalAuthorityRepository.get(
                principal_id, self._collection("principal_authorities")
            )
        except PrincipalAuthorityNotFoundError as error:
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_AUTHORITY_REQUIRED") from error
        except PrincipalAuthorityRepositoryError as error:
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_AUTHORITY_UNAVAILABLE") from error
        except Exception as error:
            # A missing collection or Kernel-bound persistence fracture must
            # never escape as a successful-looking authentication response.
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_AUTHORITY_UNAVAILABLE") from error
        if authority.status is not PrincipalStatus.ACTIVE:
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_AUTHORITY_NOT_ACTIVE")
        return authority

    def validate_refresh_token(
        self, token: str, *, session: Any = None
    ) -> Optional[str]:
        """Validate a refresh token with temporary, explicit legacy compatibility.

        Tenant-bearing rows must contain a non-empty string exactly matching the
        hydrated user's canonical tenant.  A genuinely absent ``tenant_id`` is
        the pre-migration legacy state and temporarily follows the pre-existing
        identity resolver without writing or repairing the row.  Present but
        invalid or mismatched tenant data always fails closed.  This method is
        read-only and never creates a transaction, rotates a token, or performs
        migration-on-read.
        """
        doc = self._call_collection(
            self._collection("refresh_tokens"),
            "find_one",
            {"token": token},
            session=session,
        )
        expiry = doc.get("expires") if isinstance(doc, dict) else None
        if not isinstance(expiry, datetime) or expiry < datetime.utcnow():
            return None
        user_id = doc.get("user_id")
        if not isinstance(user_id, str):
            return None
        try:
            document, _ = self._resolve_user_identity(user_id, session=session)
            user = self._doc_to_user(document, session=session) if document is not None else None
        except AuthRegistryTenantError:
            return None
        if user is None:
            return None
        if "tenant_id" in doc:
            stored_tenant = doc.get("tenant_id")
            if not isinstance(stored_tenant, str) or not stored_tenant.strip():
                return None
            if stored_tenant != user.tenantId:
                return None
        # Missing tenant_id is temporary pre-migration compatibility only.  No
        # write, backfill, cleanup, or token rotation occurs on this read.
        return user.id

    def revoke_refresh_tokens(
        self,
        tenant_id: str,
        user_id: str,
        *,
        session: Any = None,
    ) -> int:
        """Revoke only migrated tenant-bound refresh authority for one user.

        The exact durable predicate is ``tenant_id`` plus the existing
        application ``user_id``.  Tenantless legacy rows are intentionally not
        matched until a separately authorized migration; this seam therefore
        cannot perform unsafe user-only deletion.  The caller owns any
        transaction and receives only the bounded deleted-row count.
        """
        document, _ = self._resolve_user_identity(user_id, session=session)
        if document is None:
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_CANONICAL_INVALID")
        user = self._doc_to_user(document, session=session)
        canonical = self._require_canonical_tenant(tenant_id)
        if canonical.tenant_id != user.tenantId:
            raise AuthRegistryTenantError("AUTH_TENANT_CANONICAL_INVALID")
        result = self._call_collection(
            self._collection("refresh_tokens"),
            "delete_many",
            {"tenant_id": canonical.tenant_id, "user_id": user.id},
            session=session,
        )
        return int(getattr(result, "deleted_count", 0))

    def create_otp_secret(self, user_id: str) -> str:
        """Persist a newly generated legacy TOTP secret for an admitted identity.

        The owning MFA flow must prove the exact principal and tenant before
        calling this identity-keyed legacy store. Returns secret material only
        to that flow; performs no Global Principal enrollment or role grant.
        Upsert errors propagate and this method owns no transaction."""
        secret = pyotp.random_base32()
        self._collection("otp_secrets").update_one(
            {"user_id": user_id},
            {"$set": {"secret": secret, "created_at": datetime.utcnow()}},
            upsert=True
        )
        return secret

    def get_otp_secret(self, user_id: str) -> Optional[str]:
        """Read legacy TOTP material for the caller-proven authentication identity.

        The owning MFA flow supplies tenant/principal admission. This global
        identity-keyed compatibility read neither repairs factors nor confers
        a Global Principal mapping, session, membership or financial authority.
        Missing material returns None; storage errors propagate."""
        doc = self._collection("otp_secrets").find_one({"user_id": user_id})
        return doc["secret"] if doc else None

    def get_otp_uri(self, user_id: str, email: str) -> str:
        """Return the provisioning URI for the existing or newly persisted factor.

        Only an admitted legacy MFA setup flow may consume the returned secret
        URI. This may create the identity-keyed factor if absent, never rotates
        an existing factor, logs no secret, and grants no session or membership.
        Factor persistence and TOTP construction failures propagate."""
        secret = self.get_otp_secret(user_id)
        if not secret:
            secret = self.create_otp_secret(user_id)
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name="Wilsy OS")

    def verify_otp(self, user_id: str, code: str) -> bool:
        """Verify a code against the existing caller-proven legacy factor.

        The owning flow proves tenant and identity; this read grants no session
        and changes no enrollment state. Missing factor returns False. One
        adjacent time window permits bounded clock drift; errors propagate."""
        secret = self.get_otp_secret(user_id)
        if not secret:
            return False
        totp = pyotp.TOTP(secret)
        # Allow one adjacent 30-second window for ordinary handset/server clock
        # drift without accepting an unbounded replay window.
        return totp.verify(code, valid_window=1)

    def create_session(self, user: User, *, session: Any = None) -> Session:
        """Create a final session only for a durable ACTIVE principal."""
        canonical = self._require_canonical_tenant(user.tenantId)
        canonical_tenant_id = canonical.tenant_id
        self._require_active_principal_authority(user.id)
        session_reference = f"WILSYSESSION-{uuid.uuid4()}"
        token = self.generate_access_jwt(
            user.id,
            canonical_tenant_id,
            user.role,
            user.permissions,
            session=session,
            session_reference=session_reference,
        )
        created_session = Session(
            userId=user.id,
            token=token,
            expiresAt=datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
            tenantId=canonical_tenant_id,
            role=user.role,
            permissions=user.permissions,
            sessionReference=session_reference,
        )
        # Session persistence is mandatory before refresh material is created.
        self._call_collection(
            self._collection("sessions"),
            "insert_one",
            {
                "user_id": user.id,
                "session_reference": session_reference,
                "token": token,
                "expires_at": created_session.expiresAt,
                "tenant_id": canonical_tenant_id,
                "role": user.role,
                "permissions": user.permissions,
                "created_at": datetime.utcnow(),
            },
            session=session,
        )
        # Persist refresh material only after the session write succeeds; a
        # rejected tenant can therefore never leave an orphan refresh token.
        self.generate_refresh_token(user.id, canonical_tenant_id, session=session)
        return created_session

    def is_session_current(
        self,
        tenant_id: str,
        user_id: str,
        session_reference: str,
        *,
        at: datetime | None = None,
        session: Any = None,
    ) -> bool:
        """Resolve currentness for one exact non-secret session reference.

        Raw bearer material is never queried or exposed. Missing, malformed,
        expired, revoked/deleted, tenant-mismatched, principal-mismatched, or
        reference-mismatched state fails closed.
        """
        if (
            not isinstance(session_reference, str)
            or not session_reference.strip()
        ):
            return False

        reference = session_reference.strip()
        canonical = self._require_canonical_tenant(tenant_id)

        (
            _document,
            _identity_filter,
            user,
            _revision,
        ) = self._resolve_exact_credential_identity(
            tenant_id,
            user_id,
            session=session,
        )

        row = self._call_collection(
            self._collection("sessions"),
            "find_one",
            {
                "tenant_id": canonical.tenant_id,
                "user_id": user.id,
                "session_reference": reference,
            },
            session=session,
        )

        if not isinstance(row, dict):
            return False

        if (
            row.get("tenant_id") != canonical.tenant_id
            or row.get("user_id") != user.id
            or row.get("session_reference") != reference
        ):
            return False

        expires_at = row.get("expires_at")

        if not isinstance(expires_at, datetime):
            return False

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at = expires_at.astimezone(timezone.utc)

        observed_at = datetime.utcnow() if at is None else at

        if not isinstance(observed_at, datetime):
            return False

        if observed_at.tzinfo is None:
            observed_at = observed_at.replace(tzinfo=timezone.utc)
        else:
            observed_at = observed_at.astimezone(timezone.utc)

        return expires_at > observed_at

    def register_user(
        self,
        email: str,
        password: str,
        firstName: str,
        lastName: str,
        role: str,
        tenantId: str,
        *,
        session: Any = None,
    ) -> User:
        """Create one canonical-tenant credential row under caller transaction ownership.

        Registration validates the supplied tenant reference through the canonical
        TenantRegistry, creates a fresh WILSYAUTH identity, hashes the password
        through this registry's bcrypt authority, and persists only the existing
        authentication user schema with credential revision zero.

        The optional session is forwarded unchanged to the single users-collection
        insert through _call_collection. This method never starts, commits, aborts,
        or retries a transaction; it never creates PrincipalAuthority,
        TenantMembership, TenantBusinessRole, RoleAssignment, JWT, session,
        refresh-token, MFA, authorization, or financial authority. Callers that
        compose those independent authorities remain responsible for the surrounding
        transaction and fail-closed rollback semantics.

        The no-session call path is behaviorally identical to the established
        registration contract. Duplicate persistence conflicts remain bounded to
        the existing ValueError("Email already exists") outcome.
        """
        canonical = self._require_canonical_tenant(
            tenantId,
            allow_alias=True,
            session=session,
        )
        canonical_tenant_id = canonical.tenant_id
        user_id = f"WILSYAUTH-{uuid.uuid4()}"
        hashed = self.hash_password(password)
        user = User(
            id=user_id,
            email=email,
            firstName=firstName,
            lastName=lastName,
            role=role,
            permissions=[],
            tenantId=canonical_tenant_id,
            passwordHash=hashed,
            mfaRegistered=False,
            hasSignedCovenant=False
        )
        doc = {
            "user_id": user.id,
            "email": user.email,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "role": user.role,
            "permissions": user.permissions,
            "tenantId": canonical_tenant_id,
            "passwordHash": user.passwordHash,
            CREDENTIAL_REVISION_FIELD: 0,
            "mfaRegistered": user.mfaRegistered,
            "hasSignedCovenant": user.hasSignedCovenant,
            "createdAt": user.createdAt,
            "updatedAt": user.updatedAt
        }
        try:
            self._call_collection(
                self._collection("users"),
                "insert_one",
                doc,
                session=session,
            )
        except DuplicateKeyError as error:
            raise ValueError("Email already exists") from error
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Read the legacy credential identified before tenant selection.

        Email is a platform authentication lookup, never a tenant mutation key
        or a Global Principal mapping. Hydration proves persisted identity and
        canonical tenant before returning credential material to auth callers.
        Missing users return None; malformed state and database errors propagate."""
        doc = self._collection("users").find_one({"email": email})
        if not doc:
            return None
        user = self._doc_to_user(doc)
        # This pre-tenant platform credential lookup must agree with the exact
        # global identity resolver. A tenant-scoped hydration alone cannot spot
        # a competing legacy/canonical identity under a different tenant.
        resolved, _identity_filter = self._resolve_user_identity(user.id)
        if (
            resolved is None
            or resolved.get("_id") != doc.get("_id")
            or resolved.get("tenantId") != user.tenantId
        ):
            logger.error("AUTH_PRINCIPAL_IDENTITY_AMBIGUOUS")
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_IDENTITY_AMBIGUOUS")
        return user

    def get_user_by_id(self, user_id: str, *, session: Any = None) -> Optional[User]:
        """Read an exact legacy authentication identity under caller session ownership.

        Canonical and BSON ObjectId paths must not compete or redirect. This
        platform lookup precedes tenant selection; tenant-bound credential
        commands use the exact scoped resolver. Missing identity returns None;
        malformed identity or tenant state fails closed. No repair is performed."""
        doc, _ = self._resolve_user_identity(user_id, session=session)
        if not doc:
            return None
        user = self._doc_to_user(doc, session=session)
        if user.id != user_id:
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_IDENTITY_AMBIGUOUS")
        return user

    def get_credential_revision(
        self,
        tenant_id: str,
        user_id: str,
        *,
        session: Any = None,
    ) -> int:
        """Read one exact tenant/principal credential revision.

        The users query is tenant-scoped and uses only the canonical ``user_id``
        or a validated legacy Mongo ``_id`` fallback.  A missing durable field
        is the compatibility baseline ``0`` and is never backfilled by this
        read.  Present malformed state, tenant mismatch, identity ambiguity,
        and absent principals fail closed with a code-only registry error.
        The caller owns the optional session and any transaction; no password,
        hash, MFA, role, membership, JWT, or financial authority is returned.
        """
        _document, _identity_filter, _user, revision = self._resolve_exact_credential_identity(
            tenant_id, user_id, session=session
        )
        return revision

    def compare_and_swap_password_hash(
        self,
        tenant_id: str,
        user_id: str,
        expected_credential_revision: int,
        new_password_hash: str,
        *,
        session: Any = None,
    ) -> int:
        """Atomically replace a password hash and advance its credential epoch.

        This is a caller-owned transaction participant.  It performs a fresh
        exact tenant/principal read, validates the expected revision, then uses
        one non-upsert Mongo ``update_one`` to set only ``passwordHash`` and
        ``credential_revision``.  A genuinely absent legacy revision at zero is
        matched with ``$exists: false`` so a concurrent writer cannot be
        overwritten.  Exact matched/modified counts and a same-session
        readback are required before returning the new revision.  The supplied
        hash is treated as already produced by canonical AuthRegistry hashing;
        it is never logged, returned, or re-hashed.  No session/refresh
        revocation, recovery consumption, JWT issuance, or transaction
        lifecycle is owned here.
        """
        expected = _validated_credential_revision(expected_credential_revision)
        if expected >= CREDENTIAL_REVISION_MAX:
            raise AuthRegistryTenantError("AUTH_CREDENTIAL_REVISION_OVERFLOW")
        if not isinstance(new_password_hash, str) or not new_password_hash:
            raise AuthRegistryTenantError("AUTH_PASSWORD_HASH_INVALID")

        document, identity_filter, user, observed = self._resolve_exact_credential_identity(
            tenant_id, user_id, session=session
        )
        if observed != expected:
            raise AuthRegistryTenantError("AUTH_CREDENTIAL_REVISION_CONFLICT")

        cas_filter = dict(identity_filter)
        if CREDENTIAL_REVISION_FIELD in document:
            cas_filter[CREDENTIAL_REVISION_FIELD] = expected
        else:
            cas_filter[CREDENTIAL_REVISION_FIELD] = {"$exists": False}
        next_revision = expected + 1
        result = self._call_collection(
            self._collection("users"),
            "update_one",
            cas_filter,
            {
                "$set": {
                    "passwordHash": new_password_hash,
                    CREDENTIAL_REVISION_FIELD: next_revision,
                }
            },
            upsert=False,
            session=session,
        )
        if (
            getattr(result, "matched_count", None) != 1
            or getattr(result, "modified_count", None) != 1
        ):
            raise AuthRegistryTenantError("AUTH_CREDENTIAL_CAS_FAILED")

        readback_document, _readback_filter, readback_user, readback_revision = (
            self._resolve_exact_credential_identity(tenant_id, user_id, session=session)
        )
        if (
            readback_revision != next_revision
            or readback_user.id != user.id
            or readback_user.tenantId != user.tenantId
            or readback_document.get("passwordHash") != new_password_hash
        ):
            raise AuthRegistryTenantError("AUTH_CREDENTIAL_CAS_READBACK_FAILED")
        return next_revision

    def revoke_sessions(
        self,
        tenant_id: str,
        user_id: str,
        *,
        session: Any = None,
    ) -> int:
        """Delete session authority for one exact tenant/principal.

        The registry resolves the principal through the same tenant-scoped
        identity contract used by credential CAS, then performs one bounded
        ``delete_many`` with exactly ``tenant_id`` and the hydrated ``user_id``.
        Only the deleted-row count is returned.  Bearer tokens are never read
        or exposed, and the caller owns session/transaction lifecycle.  This
        method does not revoke refresh rows or change password, MFA, roles,
        membership, JWTs, or financial authority.
        """
        _document, _identity_filter, user, _revision = self._resolve_exact_credential_identity(
            tenant_id, user_id, session=session
        )
        canonical = self._require_canonical_tenant(tenant_id)
        result = self._call_collection(
            self._collection("sessions"),
            "delete_many",
            {"tenant_id": canonical.tenant_id, "user_id": user.id},
            session=session,
        )
        return int(getattr(result, "deleted_count", 0))

    def _doc_to_user(self, doc: Dict[str, Any], *, session: Any = None) -> User:
        """Hydrate only a valid identity and canonical tenant, without repair.

        Legacy compatibility accepts only BSON ObjectId fallback and retains
        existing null user_id compatibility. A tenant-scoped competing identity
        rejects the hydration. No raw identifier, email, hash, factor or token
        is logged; optional legacy warnings require WILSY_MODEL_DEBUG=1.
        Authentication identity does not establish Global Principal admission.
        """
        self._document_credential_revision(doc)
        user_id = self._document_user_id(doc)
        persisted_tenant_id = doc.get("tenantId")
        canonical = self._require_canonical_tenant(persisted_tenant_id, session=session)
        if canonical.tenant_id != persisted_tenant_id:
            raise AuthRegistryTenantError("AUTH_TENANT_CANONICAL_INVALID")

        object_id = self._validated_legacy_object_id(user_id)
        if object_id is not None:
            # POPIA section 19 / GDPR Article 32: only inspect a competing
            # identity inside the already-proven tenant, never by email.
            collision_filter = (
                {"user_id": user_id, "tenantId": persisted_tenant_id}
                if doc.get("user_id") is None
                else {"_id": object_id, "tenantId": persisted_tenant_id}
            )
            competing = self._call_collection(
                self._collection("users"), "find_one", collision_filter, session=session
            )
            if competing is not None and competing.get("_id") != doc.get("_id"):
                logger.error("AUTH_PRINCIPAL_IDENTITY_AMBIGUOUS")
                raise AuthRegistryTenantError("AUTH_PRINCIPAL_IDENTITY_AMBIGUOUS")
        if doc.get("user_id") is None and os.getenv("WILSY_MODEL_DEBUG") == "1":
            logger.warning("AUTH_LEGACY_OBJECT_ID_COMPATIBILITY")

        return User(
            id=user_id,
            email=doc.get("email", ""),
            firstName=doc.get("firstName", ""),
            lastName=doc.get("lastName", ""),
            role=doc.get("role", "USER"),
            permissions=doc.get("permissions", []),
            tenantId=canonical.tenant_id,
            passwordHash=doc.get("passwordHash", ""),
            mfaRegistered=doc.get("mfaRegistered", False),
            mfaSecret=None,  # OTP secret stored separately
            hasSignedCovenant=doc.get("hasSignedCovenant", False),
            createdAt=doc.get("createdAt", datetime.utcnow()),
            updatedAt=doc.get("updatedAt", datetime.utcnow())
        )

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Return the hydrated legacy user only after bcrypt password verification.

        The router still owns discovered-tenant binding, MFA and session admission.
        Password success creates no Global Principal credential, membership,
        permission or financial authority. Missing or wrong credentials return
        None; malformed persisted identity and verification failures propagate."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if self.verify_password(password, user.passwordHash):
            return user
        return None

    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update admitted legacy MFA, covenant, role or permission fields.

        The owning auth flow must authorize the requested fields. This method
        proves identity and tenant before one tenant-bound write, guards legacy
        identity against canonical reassignment, and rehydrates durable state.
        It never updates Global Principal, membership, credential or factor
        authorities and owns no transaction. No supported fields or no durable
        change returns None; malformed identity and persistence errors propagate."""
        update_fields = {}
        for key, value in kwargs.items():
            if key in ["mfaRegistered", "hasSignedCovenant", "role", "permissions"]:
                update_fields[key] = value
        if not update_fields:
            return None
        update_fields["updatedAt"] = datetime.utcnow()
        document, identity_filter = self._resolve_user_identity(user_id)
        if identity_filter is None:
            return None
        # Hydrate before mutation: malformed identity must never receive an
        # MFA/role write and only fail later during the response readback.
        if document is None:
            return None
        user = self._doc_to_user(document)
        if user.id != user_id:
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_IDENTITY_AMBIGUOUS")
        identity_filter = dict(identity_filter)
        identity_filter["tenantId"] = user.tenantId
        if "user_id" not in identity_filter:
            # Mongo equality with None matches only missing/null legacy state;
            # a concurrently assigned canonical identity cannot be overwritten.
            identity_filter["user_id"] = None
        result = self._collection("users").update_one(
            identity_filter,
            {"$set": update_fields}
        )
        if result.modified_count == 0:
            return None
        return self.get_user_by_id(user_id)

# Singleton instance
_registry = None

def get_auth_registry(tenant_registry: Optional[TenantRegistry] = None) -> AuthRegistry:
    """
    Return the process-local authentication service without caching database state.

    The optional tenant resolver is installed only on first construction.
    Callers retain HTTP, tenant admission and transaction ownership. This
    factory creates no identity, authority, connection, index or financial state.
    """
    global _registry
    if _registry is None:
        _registry = AuthRegistry(tenant_registry)
    return _registry

__all__ = ["AuthRegistry", "AuthRegistryTenantError", "get_auth_registry"]

"""
ARTIFACT: tools/eos/saas/auth/auth_registry.py
VERSION: v1.13.0-CONSOLIDATION-STRICT-IDENTITY-HYDRATION
AUTHORITY BOUNDARY: authentication business semantics; TenantRegistry owns canonical tenant validation; registration and its tenant validation may participate in but never own a caller transaction
TENANT POSTURE: users, JWTs, sessions, credential reads/CAS, and refresh validation require one ACTIVE canonical tenant_id; revocations are tenant_id + user_id scoped
FAIL-CLOSED POSTURE: invalid identity types, malformed BSON fallbacks, competing identity rows, invalid tenant/revision/refresh state, or missing principal authority issue no final auth material; compatibility reads never migrate identities
FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
END OF WILSY OS SOVEREIGN ARTIFACT
"""
