"""TITLE: Wilsy OS Authentication Router.
VERSION: v1.0.14-VERIFY-TOKEN-PROJECTION
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Canonical authentication HTTP endpoints, including bounded token verification,
MFA setup and verification, login, discovery, and logout.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/auth_router.py
COLLABORATION / OWNERSHIP: Authentication service and FastAPI server consume this router;
credential and identity authorities remain in tools.eos.auth.
CERTIFICATION/UPDATE DATE: 2026-08-29.
CHANGELOG:
  v1.0.14-VERIFY-TOKEN-PROJECTION: Canonical GET + POST /auth/verify-token share one
  handler and the get_current_identity authority dependency; the public projection is
  bounded to success, status, user.id, and user.email with no tenant, role, permission,
  or credential response projection.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY/PRIVACY POSTURE: Raw credentials and database documents are never returned;
verify-token is limited to governed public fields; authentication failure remains
fail-closed through get_current_identity.
TENANT BOUNDARY: verify-token does not certify tenant membership; tenant context remains
the responsibility of a separate downstream authority.
AUTHORITY BOUNDARY: This router exposes authentication HTTP endpoints only. It does not
own credential truth, principal lifecycle authority, tenant membership, governed role
assignment, authorization, or financial execution.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""

from __future__ import annotations

VERSION = "v1.0.14-VERIFY-TOKEN-PROJECTION"

from fastapi import APIRouter, Depends, HTTPException, status
import logging
import traceback
import os
from typing import Any, Optional

from pymongo.errors import PyMongoError

from ..saas.domain.auth import AuthRequest, VerifyOTPRequest, DiscoverRequest, AuthResponse
from ..saas.auth.auth_registry import get_auth_registry
from ..saas.tenancy.tenant_registry import TenantRegistry
from ..auth.authentication import get_current_identity
from ..auth.identity import SovereignIdentity

# ─── Logging Discipline (Mandate §2.6) ──────────────────────────────────
logger = logging.getLogger(__name__)
DEBUG_MODE = os.getenv("WILSY_MODEL_DEBUG", "0") == "1"

def broadcast_telemetry(
    tenant_id: str,
    category: str,
    event: str,
    source: str,
    metadata: Optional[dict] = None,
) -> None:
    """Telemetry logging – always info level."""
    if metadata is None:
        metadata = {}
    logger.info(f"[TELEMETRY] {tenant_id} | {category} | {event} | {source} | {metadata}")


def _log_error(exc: Exception, context: str, tenant_id: str = "GLOBAL_ROOT") -> None:
    """Log errors with full traceback if debug mode is enabled."""
    if DEBUG_MODE:
        logger.error(f"[ERROR] {context} | tenant: {tenant_id} | {exc}\n{traceback.format_exc()}")
    else:
        logger.error(f"[ERROR] {context} | tenant: {tenant_id} | {exc}")


def _tenant_id_from_user(user: Any) -> str:
    """Safe tenant id for error telemetry (never unbound)."""
    if user is None:
        return "GLOBAL_ROOT"
    return getattr(user, "tenantId", None) or getattr(user, "tenant_id", None) or "GLOBAL_ROOT"


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/verify-token")
@router.post("/verify-token")
async def _verify_token(identity: SovereignIdentity = Depends(get_current_identity)) -> dict[str, object]:
    """Return a bounded public projection for a current active identity."""
    return {"success": True, "status": "VERIFIED", "user": {"id": identity.identity_id, "email": identity.email}}


# ─── LOGIN ──────────────────────────────────────────────────────────────────
@router.post("/login", response_model=AuthResponse)
async def login(request: AuthRequest):
    try:
        auth_registry = get_auth_registry(None)
        user = auth_registry.authenticate(request.email, request.password)
        if not user:
            broadcast_telemetry(
                "GLOBAL_ROOT", "AUTH", "LOGIN_FAILED", "auth_router", {"email": request.email}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        # If MFA not registered, generate a setup QR code
        if not user.mfaRegistered:
            qr_uri = auth_registry.get_otp_uri(user.id, user.email)
            temp_token = auth_registry.generate_jwt(
                user.id, user.tenantId, user.role, user.permissions
            )
            broadcast_telemetry(
                user.tenantId, "AUTH", "MFA_SETUP_REQUIRED", "auth_router", {"userId": user.id}
            )
            return AuthResponse(
                status="MFA_SETUP",
                requiresMFA=True,
                mfaSetup=True,
                qrCode=qr_uri,
                tempToken=temp_token,
            )

        broadcast_telemetry(
            user.tenantId, "AUTH", "MFA_CHALLENGE_REQUIRED", "auth_router", {"userId": user.id}
        )

        temp_token = auth_registry.generate_jwt(
            user.id, user.tenantId, user.role, user.permissions
        )
        return AuthResponse(
            status="MFA_REQUIRED",
            requiresMFA=True,
            tempToken=temp_token,
        )
    except PyMongoError as e:
        _log_error(e, "LOGIN_DB_ERROR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during login. Please try again later.",
        )
    except HTTPException:
        raise
    except Exception as e:
        _log_error(e, "LOGIN_UNEXPECTED_ERROR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during login.",
        )


# ─── VALIDATE MFA SETUP ──────────────────────────────────────────────────
@router.post("/validate-mfa-setup", response_model=AuthResponse)
async def validate_mfa_setup(request: VerifyOTPRequest):
    """
    Validates the OTP entered during MFA setup and marks the user as MFA registered.
    This endpoint is called by the frontend after the user scans the QR code and enters the 6-digit code.
    """
    user: Any = None
    try:
        auth_registry = get_auth_registry(None)

        # 1. Retrieve user by email
        user = auth_registry.get_user_by_email(request.email)
        if not user:
            broadcast_telemetry(
                "GLOBAL_ROOT", "AUTH", "MFA_SETUP_USER_NOT_FOUND", "auth_router", {"email": request.email}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        # The setup endpoint accepts the same compatibility aliases as normal
        # verification, then narrows them to a concrete string before TOTP use.
        setup_code: str = request.code or request.otp or ""
        if not setup_code.isdigit() or len(setup_code) != 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enter the current six-digit code from your authenticator app.",
            )

        # 2. Verify OTP code against the stored secret
        if not auth_registry.verify_otp(user.id, setup_code):
            broadcast_telemetry(
                user.tenantId, "AUTH", "MFA_SETUP_OTP_INVALID", "auth_router", {"userId": user.id}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP code"
            )

        # 3. Mark user as MFA registered
        auth_registry.update_user(user.id, mfaRegistered=True)

        # 4. Create a session (so the user is automatically logged in after setup)
        session = auth_registry.create_session(user)

        broadcast_telemetry(
            user.tenantId, "AUTH", "MFA_SETUP_SUCCESS", "auth_router", {"userId": user.id}
        )

        user_data = {
            "id": user.id,
            "email": user.email,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "role": user.role,
            "permissions": user.permissions,
            "tenantId": user.tenantId,
            "tenantAlias": None,
            "mfaRegistered": True,
            "hasSignedCovenant": user.hasSignedCovenant,
        }

        return AuthResponse(
            status="AUTHENTICATED",
            token=session.token,
            user=user_data,
            refreshToken="dummy-refresh-token",
        )

    except PyMongoError as e:
        _log_error(e, "MFA_SETUP_DB_ERROR", tenant_id=_tenant_id_from_user(user))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during MFA setup. Please try again later.",
        )
    except HTTPException:
        raise
    except Exception as e:
        _log_error(e, "MFA_SETUP_UNEXPECTED_ERROR", tenant_id=_tenant_id_from_user(user))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during MFA setup.",
        )


# ─── VERIFY OTP (and alias) ──────────────────────────────────────────────
@router.post("/verify-otp", response_model=AuthResponse)
@router.post("/verify-3fa", response_model=AuthResponse)
async def verify_otp(request: VerifyOTPRequest):
    user: Any = None
    try:
        auth_registry = get_auth_registry(None)

        # Get the code from either field (frontend sends "code" or "otp")
        code = request.code or request.otp

        # Explicitly check None to satisfy type checker
        if code is None:
            broadcast_telemetry(
                "GLOBAL_ROOT",
                "AUTH",
                "OTP_MISSING",
                "auth_router",
                {"email": request.email},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing OTP code.",
            )

        if not code.isdigit() or len(code) != 6:
            broadcast_telemetry(
                "GLOBAL_ROOT",
                "AUTH",
                "OTP_MALFORMED",
                "auth_router",
                {"email": request.email},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Enter the current six-digit code from your authenticator app.",
            )

        # Verify against the persisted TOTP secret enrolled in Google Authenticator
        user = auth_registry.get_user_by_email(request.email)
        if not user:
            broadcast_telemetry(
                "GLOBAL_ROOT",
                "AUTH",
                "OTP_USER_NOT_FOUND",
                "auth_router",
                {"email": request.email},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
            )

        if not user.mfaRegistered:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="MFA enrollment is incomplete. Scan the QR code and validate setup first.",
            )

        if not auth_registry.verify_otp(user.id, code):
            broadcast_telemetry(
                user.tenantId,
                "AUTH",
                "OTP_INVALID",
                "auth_router",
                {"userId": user.id},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authenticator code. Check your device time and enter the newest code.",
            )

        session = auth_registry.create_session(user)
        broadcast_telemetry(
            user.tenantId, "AUTH", "LOGIN_SUCCESS", "auth_router", {"userId": user.id}
        )

        user_data = {
            "id": user.id,
            "email": user.email,
            "firstName": user.firstName,
            "lastName": user.lastName,
            "role": user.role,
            "permissions": user.permissions,
            "tenantId": user.tenantId,
            "tenantAlias": None,
            "mfaRegistered": user.mfaRegistered,
            "hasSignedCovenant": user.hasSignedCovenant,
        }

        return AuthResponse(
            status="AUTHENTICATED",
            token=session.token,
            user=user_data,
            refreshToken="dummy-refresh-token",
        )

    except PyMongoError as e:
        _log_error(e, "OTP_VERIFICATION_DB_ERROR", tenant_id=_tenant_id_from_user(user))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during OTP verification. Please try again later.",
        )
    except HTTPException:
        raise
    except Exception as e:
        _log_error(e, "OTP_VERIFICATION_UNEXPECTED_ERROR", tenant_id=_tenant_id_from_user(user))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during OTP verification.",
        )


# ─── DISCOVER ──────────────────────────────────────────────────────────────
@router.post("/discover")
async def discover(request: DiscoverRequest):
    try:
        tenant = None
        if hasattr(TenantRegistry, "get_tenant_by_alias"):
            tenant = TenantRegistry.get_tenant_by_alias(request.alias)
        elif hasattr(TenantRegistry, "get"):
            tenant = TenantRegistry.get(request.alias)

        if not tenant:
            if request.alias.lower() == "wilsy":
                fallback = {
                    "tenant_id": "WILSY",
                    "alias": "wilsy",
                    "name": "Wilsy Sovereign Shard",
                    "region": "GLOBAL",
                    "plan": "ENTERPRISE",
                    "status": "ACTIVE",
                }
                broadcast_telemetry(
                    fallback["tenant_id"],
                    "AUTH",
                    "DISCOVER_SUCCESS",
                    "auth_router",
                    {"alias": request.alias},
                )
                return {"success": True, "tenant": fallback}
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found"
            )

        broadcast_telemetry(
            tenant.tenant_id,
            "AUTH",
            "DISCOVER_SUCCESS",
            "auth_router",
            {"alias": request.alias},
        )
        return {
            "success": True,
            "tenant": {
                "tenantId": tenant.tenant_id,
                "alias": tenant.tenant_id,
                "name": tenant.organization.organization_name,
                "region": tenant.organization.regions[0]
                if tenant.organization.regions
                else "GLOBAL",
                "plan": tenant.organization.plan.value
                if hasattr(tenant.organization.plan, "value")
                else str(tenant.organization.plan),
                "status": tenant.status,
            },
        }
    except PyMongoError as e:
        _log_error(e, "DISCOVER_DB_ERROR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during tenant discovery. Please try again later.",
        )
    except HTTPException:
        raise
    except Exception as e:
        _log_error(e, "DISCOVER_UNEXPECTED_ERROR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during discovery.",
        )


# ─── LOGOUT ────────────────────────────────────────────────────────────────
@router.post("/logout")
async def logout():
    broadcast_telemetry("GLOBAL_ROOT", "AUTH", "LOGOUT", "auth_router", {})
    return {"status": "success", "message": "Logged out"}


# ARTIFACT: auth_router.py
# VERSION: v1.0.14-VERIFY-TOKEN-PROJECTION
# AUTHORITY BOUNDARY: Authentication HTTP routing and bounded projections only;
# credential, principal, tenant, authorization, and financial authorities remain separate.
# TENANT POSTURE: verify-token never certifies tenant membership; tenant context is downstream.
# FAIL-CLOSED POSTURE: Authentication failures remain fail-closed through get_current_identity.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
