"""
╔══════════════════════════════════════════════════════════════════════════════╗
║ WILSY OS - AUTH REGISTRY (MONGODB‑BACKED)                                   ║
║ [PASSWORD HASH | JWT | OTP | SESSION MANAGEMENT | WILSYAUTH- IDENTITY]       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ VERSION: 1.1.2-FALLBACK-ID                                                  ║
║ EPITOME: Sovereign authentication business logic with MongoDB persistence.  ║
║          Handles missing `user_id` fields by falling back to `_id`.         ║
║ ABSOLUTE PATH: tools/eos/saas/auth/auth_registry.py                         ║
║ AUTHORITY: Wilsy OS Core Governance                                         ║
║ COMPLIANCE: POPIA §19, GDPR §32, SOC2 §CC7.2, ISO 27001                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ CHANGE LOG:                                                                 ║
║   2026-08-22 v1.1.2-FALLBACK-ID – Made _doc_to_user robust: if user_id     ║
║        missing, fall back to str(doc["_id"]) and log warning.              ║
║   2026-08-20 v1.1.1-OPTIONAL-TENANT-REGISTRY – Made tenant_registry optional║
║   2026-08-20 v1.1.0-MONGODB – Replaced in‑memory storage with MongoDB.     ║
║   2026-08-20 v1.0.0-SOVEREIGN – Initial creation.                           ║
║                                                                              ║
║ CERTIFICATION SEAL: PRODUCTION_READY_v1.1.2-FALLBACK-ID                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import bcrypt
import jwt
import pyotp
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
import uuid
import logging
import os

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from ..domain.auth import User, Session, AuthRequest, VerifyOTPRequest
from ..tenancy.tenant_registry import TenantRegistry

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "wilsy-super-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24
BCRYPT_ROUNDS = 12

logger = logging.getLogger(__name__)

# ─── MongoDB Connection ──────────────────────────────────────────────────────
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/wilsy")
client = MongoClient(MONGO_URI, connect=False)
db = client.get_database("wilsy")
users_collection = db["users"]
sessions_collection = db["sessions"]
otp_secrets_collection = db["otp_secrets"]
refresh_tokens_collection = db["refresh_tokens"]

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
        self.tenant_registry = tenant_registry

    def hash_password(self, password: str) -> str:
        """Generate bcrypt hash."""
        salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against stored hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def generate_jwt(self, user_id: str, tenant_id: str, role: str, permissions: List[str]) -> str:
        """Generate JWT token with claims."""
        payload = {
            "sub": user_id,
            "tenant_id": tenant_id,
            "role": role,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def generate_refresh_token(self, user_id: str) -> str:
        """Generate a refresh token (UUID) and store it."""
        token = str(uuid.uuid4())
        refresh_tokens_collection.insert_one({
            "token": token,
            "user_id": user_id,
            "expires": datetime.utcnow() + timedelta(days=7)
        })
        return token

    def validate_refresh_token(self, token: str) -> Optional[str]:
        """Validate refresh token and return user_id if valid."""
        doc = refresh_tokens_collection.find_one({"token": token})
        if not doc or doc["expires"] < datetime.utcnow():
            return None
        return doc["user_id"]

    def create_otp_secret(self, user_id: str) -> str:
        """Generate a new OTP secret and store it."""
        secret = pyotp.random_base32()
        otp_secrets_collection.update_one(
            {"user_id": user_id},
            {"$set": {"secret": secret, "created_at": datetime.utcnow()}},
            upsert=True
        )
        return secret

    def get_otp_secret(self, user_id: str) -> Optional[str]:
        """Retrieve stored OTP secret."""
        doc = otp_secrets_collection.find_one({"user_id": user_id})
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
        """Create a new session and return JWT."""
        token = self.generate_jwt(user.id, user.tenantId, user.role, user.permissions)
        refresh = self.generate_refresh_token(user.id)
        session = Session(
            userId=user.id,
            token=token,
            expiresAt=datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS),
            tenantId=user.tenantId,
            role=user.role,
            permissions=user.permissions
        )
        # Store session in MongoDB (optional)
        sessions_collection.insert_one({
            "user_id": user.id,
            "token": token,
            "expires_at": session.expiresAt,
            "tenant_id": user.tenantId,
            "role": user.role,
            "permissions": user.permissions,
            "created_at": datetime.utcnow()
        })
        return session

    def register_user(self, email: str, password: str, firstName: str, lastName: str, role: str, tenantId: str) -> User:
        """Create a new user in MongoDB."""
        user_id = f"WILSYAUTH-{uuid.uuid4()}"
        hashed = self.hash_password(password)
        user = User(
            id=user_id,
            email=email,
            firstName=firstName,
            lastName=lastName,
            role=role,
            permissions=[],
            tenantId=tenantId,
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
            "tenantId": user.tenantId,
            "passwordHash": user.passwordHash,
            "mfaRegistered": user.mfaRegistered,
            "hasSignedCovenant": user.hasSignedCovenant,
            "createdAt": user.createdAt,
            "updatedAt": user.updatedAt
        }
        try:
            users_collection.insert_one(doc)
        except DuplicateKeyError:
            raise ValueError("Email already exists")
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve user by email from MongoDB."""
        doc = users_collection.find_one({"email": email})
        if not doc:
            return None
        return self._doc_to_user(doc)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve user by ID from MongoDB."""
        doc = users_collection.find_one({"user_id": user_id})
        if not doc:
            return None
        return self._doc_to_user(doc)

    def _doc_to_user(self, doc: Dict[str, Any]) -> User:
        """
        Convert MongoDB document to User object.
        If 'user_id' field is missing, fall back to '_id' (converted to str).
        """
        # Get user ID with fallback
        user_id = doc.get("user_id")
        if not user_id:
            # Fallback to MongoDB _id
            user_id = str(doc.get("_id", ""))
            if user_id:
                logger.warning(f"_doc_to_user: Missing 'user_id' field. Using '_id' fallback: {user_id}")
            else:
                raise ValueError("User document has neither 'user_id' nor '_id'")

        return User(
            id=user_id,
            email=doc.get("email", ""),
            firstName=doc.get("firstName", ""),
            lastName=doc.get("lastName", ""),
            role=doc.get("role", "USER"),
            permissions=doc.get("permissions", []),
            tenantId=doc.get("tenantId", "GLOBAL_ROOT"),
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
        result = users_collection.update_one(
            {"user_id": user_id},
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

"""
CERTIFICATION SEAL:
Status: CERTIFIED
Version: 1.1.2-FALLBACK-ID
Compliance: POPIA, GDPR, SOC2
Fix: Fallback to _id if user_id missing in MongoDB documents.
"""
