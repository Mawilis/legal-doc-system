"""Wilsy OS canonical authentication registry.

TITLE: WILSY OS Authentication Registry
VERSION: v1.6.0-R1D-B0F-B4-R6-PRINCIPAL-AUTHORITY-GATE
AUTHORITY: Wilsy OS Core Governance
EPITOME: Owns password, JWT, OTP, session, and refresh-token business semantics
         while consuming the caller-established canonical Kernel database.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/saas/auth/auth_registry.py
COLLABORATION / OWNERSHIP: Auth router delegates here; tools.eos.kernel.db owns
                           the sole Mongo lifecycle and connection recovery.
CERTIFICATION / UPDATE DATE: 2026-09-17
CHANGELOG:
  v1.4.0-R1D-B0F-B3B-CANONICAL-TENANT-SOURCE — Added one authoritative
    TenantRegistry resolver before user hydration, user creation, JWT issuance,
    session persistence, and refresh-token validation; removed tenant fallback
    projection and reordered refresh persistence after session persistence.
  v1.5.0-R1D-B0F-B4-R2-CANONICAL-TOKEN-CONTRACT — Delegates access-token
    encoding to jwt_provider, removes the JWT_SECRET fallback, and emits the
    canonical identity_id/tenant_id/roles/permissions claim contract.
  v1.6.0-R1D-B0F-B4-R6-PRINCIPAL-AUTHORITY-GATE — Final session issuance now
    consumes a durable ACTIVE PrincipalAuthority; login never creates one.
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
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import uuid
import logging

from bson import ObjectId
from pymongo.errors import ConnectionFailure, DuplicateKeyError, PyMongoError

from ..domain.auth import User, Session, AuthRequest, VerifyOTPRequest
from ..tenancy.tenant_registry import TenantRegistry
from tools.eos.kernel import db as kernel_db
from tools.eos.auth.jwt_provider import create_access_token
from tools.eos.auth.principal_authority import PrincipalAuthority
from tools.eos.auth.principal_authority_repository import (
    PrincipalAuthorityNotFoundError,
    PrincipalAuthorityRepository,
    PrincipalAuthorityRepositoryError,
)
from tools.eos.auth.principal_status import PrincipalStatus

VERSION = "v1.6.0-R1D-B0F-B4-R6-PRINCIPAL-AUTHORITY-GATE"

# Configuration
JWT_EXPIRY_HOURS = 24
BCRYPT_ROUNDS = 12

logger = logging.getLogger(__name__)


class AuthRegistryTenantError(RuntimeError):
    """Signal that a principal tenant reference is not canonical and ACTIVE.

    This exception is deliberately fail-closed: callers receive no JWT, session,
    refresh token, or hydrated user when the canonical tenants collection cannot
    prove exactly one permitted tenant row. It grants no membership or role.
    """

class AuthRegistry:
    """
    Institutional authentication registry with MongoDB persistence.
    Handles password hashing, JWT issuance, OTP generation/validation, and session creation.
    """

    def __init__(self, tenant_registry: Optional[TenantRegistry] = None):
        """
        Initialize the auth registry.
        @param tenant_registry: Optional TenantRegistry instance. Currently not used,
               but kept for future compatibility.
        """
        self.tenant_registry = tenant_registry or TenantRegistry

    def _require_canonical_tenant(
        self,
        tenant_reference: object,
        *,
        allow_alias: bool = False,
    ) -> Any:
        """Require one ACTIVE canonical tenant before auth material is issued."""
        if not isinstance(tenant_reference, str) or not tenant_reference.strip():
            raise AuthRegistryTenantError("AUTH_TENANT_CANONICAL_INVALID")
        resolver = getattr(self.tenant_registry, "resolve_canonical_tenant", None)
        if not callable(resolver):
            resolver = TenantRegistry.resolve_canonical_tenant
        try:
            tenant = resolver(tenant_reference.strip(), allow_alias=allow_alias)
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

    def _resolve_user_identity(
        self, user_id: str
    ) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
        """Resolve one durable user and its exact mutation predicate.

        Canonical ``user_id`` identity always wins.  If absent, a validated
        ObjectId string resolves exactly one legacy Mongo document by ``_id``.
        Returning the matched document together with its predicate keeps reads,
        updates, and MFA enrollment on the same effective principal without
        broadening a query or using email as mutation identity.
        """
        users = self._collection("users")
        canonical_filter = {"user_id": user_id}
        document = users.find_one(canonical_filter)
        if document is not None:
            return document, canonical_filter

        object_id = self._validated_legacy_object_id(user_id)
        if object_id is None:
            return None, None
        legacy_filter = {"_id": object_id}
        document = users.find_one(legacy_filter)
        if document is None:
            return None, None
        return document, legacy_filter

    def hash_password(self, password: str) -> str:
        """Generate bcrypt hash."""
        salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def generate_jwt(self, user_id: str, tenant_id: str, role: str, permissions: List[str]) -> str:
        """Generate JWT only after exact canonical tenant validation."""
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
        # AuthRegistry owns durable user/tenant admission; jwt_provider owns
        # the sole cryptographic encoder and signing-secret configuration.
        return create_access_token(
            {
                "identity_id": user_id.strip(),
                "tenant_id": canonical_tenant_id,
                "roles": [role.strip()],
                "permissions": list(permissions),
            },
            expires_in_seconds=JWT_EXPIRY_HOURS * 60 * 60,
        )

    def generate_refresh_token(self, user_id: str) -> str:
        """Generate refresh material only for a hydrated canonical principal."""
        if self.get_user_by_id(user_id) is None:
            raise AuthRegistryTenantError("AUTH_PRINCIPAL_CANONICAL_INVALID")
        token = str(uuid.uuid4())
        self._collection("refresh_tokens").insert_one({
            "token": token,
            "user_id": user_id,
            "expires": datetime.utcnow() + timedelta(days=7)
        })
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

    def validate_refresh_token(self, token: str) -> Optional[str]:
        """Validate refresh token only while its principal tenant remains valid."""
        doc = self._collection("refresh_tokens").find_one({"token": token})
        if not doc or doc["expires"] < datetime.utcnow():
            return None
        user_id = doc.get("user_id")
        if not isinstance(user_id, str):
            return None
        try:
            user = self.get_user_by_id(user_id)
        except AuthRegistryTenantError:
            return None
        return user.id if user is not None else None

    def create_otp_secret(self, user_id: str) -> str:
        """Generate a new OTP secret and store it."""
        secret = pyotp.random_base32()
        self._collection("otp_secrets").update_one(
            {"user_id": user_id},
            {"$set": {"secret": secret, "created_at": datetime.utcnow()}},
            upsert=True
        )
        return secret

    def get_otp_secret(self, user_id: str) -> Optional[str]:
        """Retrieve stored OTP secret."""
        doc = self._collection("otp_secrets").find_one({"user_id": user_id})
        return doc["secret"] if doc else None

    def get_otp_uri(self, user_id: str, email: str) -> str:
        """Generate otpauth URI for QR code."""
        secret = self.get_otp_secret(user_id)
        if not secret:
            secret = self.create_otp_secret(user_id)
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=email, issuer_name="Wilsy OS")

    def verify_otp(self, user_id: str, code: str) -> bool:
        """Verify a Google Authenticator TOTP code against the enrolled secret."""
        secret = self.get_otp_secret(user_id)
        if not secret:
            return False
        totp = pyotp.TOTP(secret)
        # Allow one adjacent 30-second window for ordinary handset/server clock
        # drift without accepting an unbounded replay window.
        return totp.verify(code, valid_window=1)

    def create_session(self, user: User) -> Session:
        """Create a final session only for a durable ACTIVE principal."""
        canonical = self._require_canonical_tenant(user.tenantId)
        canonical_tenant_id = canonical.tenant_id
        self._require_active_principal_authority(user.id)
        token = self.generate_jwt(user.id, canonical_tenant_id, user.role, user.permissions)
        session = Session(
            userId=user.id,
            token=token,
            expiresAt=datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
            tenantId=canonical_tenant_id,
            role=user.role,
            permissions=user.permissions
        )
        # Store session in MongoDB (optional)
        self._collection("sessions").insert_one({
            "user_id": user.id,
            "token": token,
            "expires_at": session.expiresAt,
            "tenant_id": canonical_tenant_id,
            "role": user.role,
            "permissions": user.permissions,
            "created_at": datetime.utcnow()
        })
        # Persist refresh material only after the session write succeeds; a
        # rejected tenant can therefore never leave an orphan refresh token.
        self.generate_refresh_token(user.id)
        return session

    def register_user(self, email: str, password: str, firstName: str, lastName: str, role: str, tenantId: str) -> User:
        """Create a user only for one canonical tenant (alias input is resolved once)."""
        canonical = self._require_canonical_tenant(tenantId, allow_alias=True)
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
        # Insert into MongoDB
        doc = {
            "user_id": user.id,
            "email": user.email,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "role": user.role,
            "permissions": user.permissions,
            "tenantId": canonical_tenant_id,
            "passwordHash": user.passwordHash,
            "mfaRegistered": user.mfaRegistered,
            "hasSignedCovenant": user.hasSignedCovenant,
            "createdAt": user.createdAt,
            "updatedAt": user.updatedAt
        }
        try:
            self._collection("users").insert_one(doc)
        except DuplicateKeyError:
            raise ValueError("Email already exists")
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email from MongoDB."""
        doc = self._collection("users").find_one({"email": email})
        if not doc:
            return None
        return self._doc_to_user(doc)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve user by ID from MongoDB."""
        doc, _ = self._resolve_user_identity(user_id)
        if not doc:
            return None
        return self._doc_to_user(doc)

    def _doc_to_user(self, doc: Dict[str, Any]) -> User:
        """
        Convert MongoDB document to User object.
        If 'user_id' field is missing, fall back to '_id' (converted to str).
        """
        # Get user ID with the bounded legacy ObjectId compatibility path.
        user_id = doc.get("user_id")
        if not user_id:
            # Fallback to MongoDB _id
            user_id = str(doc.get("_id", ""))
            if user_id:
                logger.warning(f"_doc_to_user: Missing 'user_id' field. Using '_id' fallback: {user_id}")
            else:
                raise ValueError("User document has neither 'user_id' nor '_id'")

        persisted_tenant_id = doc.get("tenantId")
        canonical = self._require_canonical_tenant(persisted_tenant_id)
        if canonical.tenant_id != persisted_tenant_id:
            raise AuthRegistryTenantError("AUTH_TENANT_CANONICAL_INVALID")

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
        """Authenticate user by email and password."""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if self.verify_password(password, user.passwordHash):
            return user
        return None

    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        """Update user fields in MongoDB."""
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
        # Validate the persisted principal before mutating any auth field; a
        # malformed tenant reference must not receive an MFA/role update.
        self._require_canonical_tenant(document.get("tenantId") if document else None)
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
    Get the singleton AuthRegistry instance.
    @param tenant_registry: Optional TenantRegistry. If provided and the registry
           doesn't exist yet, it will be used; otherwise ignored.
    """
    global _registry
    if _registry is None:
        _registry = AuthRegistry(tenant_registry)
    return _registry

__all__ = ["AuthRegistry", "AuthRegistryTenantError", "get_auth_registry"]

"""
ARTIFACT: tools/eos/saas/auth/auth_registry.py
VERSION: v1.6.0-R1D-B0F-B4-R6-PRINCIPAL-AUTHORITY-GATE
AUTHORITY BOUNDARY: authentication business semantics; TenantRegistry owns canonical tenant validation
TENANT POSTURE: users, JWTs, sessions, and refresh validation require one ACTIVE canonical tenant_id
FAIL-CLOSED POSTURE: unavailable, missing, duplicate, inactive, or pseudo tenant references, and missing/inactive durable principal authority, issue no final auth material
FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
END OF WILSY OS SOVEREIGN ARTIFACT
"""
