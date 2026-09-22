"""TITLE: Wilsy OS Authentication Router.
VERSION: v1.8.0-R10E72-PRODUCTION-RECOVERY-ORIGIN-BINDING
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Canonical authentication HTTP endpoints, including bounded token verification,
MFA setup and verification, password-recovery request and reset completion, login,
discovery, and logout.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/auth_router.py
COLLABORATION / OWNERSHIP: Authentication service and FastAPI server consume this router;
credential and identity authorities remain in tools.eos.auth.
CERTIFICATION/UPDATE DATE: 2026-08-29.
CHANGELOG:
  v1.8.0-R10E72-PRODUCTION-RECOVERY-ORIGIN-BINDING: Resolves the trusted public
  recovery-link origin only from server-owned deployment configuration, preferring
  WILSY_PUBLIC_APP_ORIGIN and then established WILSY_PUBLIC_APP_URL, CLIENT_URL,
  FRONTEND_URL, or APP_URL aliases. Request Host remains excluded and the recovery
  service still validates HTTPS/origin shape fail closed.
  v1.7.0-R10E22-RECOVERY-CONTACT-VERIFICATION-HTTP: Adds authenticated recovery-contact verification
  request and capability-authorized completion routes. The request route derives
  the address only from current durable principal state, uses a separate
  namespaced recovery rate budget, and returns no raw verification material.
  Completion accepts only tenant selector + single-use verification capability,
  atomically establishes verified-contact authority, returns no session/token,
  and leaves password-reset authority unchanged.
  v1.6.0-R10E8-PASSWORD-RECOVERY-REQUEST-HTTP: Adds one unauthenticated, enumeration-safe
  password-recovery request route backed exclusively by the R10E Python
  verified-contact, rate-limit, issuance, and delivery chain. The adapter uses
  server-owned UTC time, configured trusted origin/SMTP capability, generic 202
  acceptance for absent or internal delivery outcomes, bounded 429 throttling,
  and returns no principal, contact, capability, token, or delivery truth.
  v1.5.0-R10D4-PASSWORD-RESET-HTTP-ADAPTER: Exposes the certified R10D1
  password-reset transaction through one unauthenticated transport route. The
  adapter forwards only the tenant selector, recovery capability, and proposed
  password, leaves capability/policy/persistence authority to the service,
  returns no session or token, and preserves the existing PRE_AUTH and full
  access routing topology.
  v1.4.0-R10C2F8R-EXPLICIT-PREAUTH-ROUTER: The three current MFA/3FA
  challenge issuers now use the explicit PRE_AUTH AuthRegistry seam. The
  canonical tenant-source semantics, ACCESS issuance, verifier behavior,
  durable revision enforcement, session/refresh authority, reset authority,
  and Node authority remain unchanged.
  v1.3.0-R1D-B0F-B3B-CANONICAL-TENANT-SOURCE: Discovery uses the shared
  canonical ACTIVE tenant resolver when available, so aliases cannot select
  duplicate, inactive, or malformed tenant truth.
  v1.2.0-TENANT-IDENTITY-PROJECTION: Discovery now returns only durable
  legal-name and verification fields when present on the authoritative tenant
  entity; no client-side identity inference is required.
  v1.1.1-AUTHORITATIVE-MFA-RECONCILIATION: TenantRegistry database-unavailable
  discovery failures now translate to the bounded HTTP 5xx contract.
  v1.1.0-AUTHORITATIVE-MFA-RECONCILIATION: Existing OTP secrets now enter an
  explicit reconciliation challenge without QR disclosure; MFA enrollment is
  durably re-read before session issuance; tenant discovery has no fallback.
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

VERSION = "v1.7.0-R10E22-RECOVERY-CONTACT-VERIFICATION-HTTP"

from fastapi import APIRouter, Depends, HTTPException, Response, status
from datetime import datetime, timezone
from functools import lru_cache
import logging
import traceback
import os
from pydantic import BaseModel, Field, StrictStr
from typing import Any, Optional

from pymongo.errors import PyMongoError

from ..saas.domain.auth import AuthRequest, VerifyOTPRequest, DiscoverRequest, AuthResponse
from ..saas.auth.auth_registry import get_auth_registry
from ..saas.auth.password_reset_service import (
    PasswordResetCode,
    PasswordResetService,
    PasswordResetServiceError,
)
from ..saas.auth.password_blocklist import PwnedPasswordBlocklistChecker
from ..saas.auth.password_recovery_contact_registry import VerifiedRecoveryContactRegistry
from ..saas.auth.password_recovery_contact_verification_email_delivery import (
    RecoveryContactVerificationEmailDelivery,
)
from ..saas.auth.password_recovery_contact_verification_registry import (
    RecoveryContactVerificationRegistry,
)
from ..saas.auth.password_recovery_contact_verification_request_service import (
    RecoveryContactVerificationRequestError,
    RecoveryContactVerificationRequestService,
)
from ..saas.auth.password_recovery_contact_verification_service import (
    RecoveryContactVerificationCode,
    RecoveryContactVerificationService,
    RecoveryContactVerificationServiceError,
)
from ..saas.auth.password_recovery_email_delivery import PasswordRecoveryEmailDelivery
from ..saas.auth.password_recovery_rate_limit import PasswordRecoveryRateLimit
from ..saas.auth.password_recovery_registry import PasswordRecoveryCapabilityRegistry
from ..saas.auth.password_recovery_request_service import (
    PasswordRecoveryRequestRateLimitedError,
    PasswordRecoveryRequestService,
    PasswordRecoveryRequestServiceError,
)
from ..saas.tenancy.tenant_registry import TenantRegistry, TenantRegistryError
from ..auth.authentication import get_current_identity
from ..auth.identity import SovereignIdentity
from ..auth.workspace_bootstrap_projection import (
    WorkspaceBootstrapProjectionError,
    build_workspace_bootstrap_projection,
)

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


def _log_error(exc: Exception, context: str, tenant_id: str = "unresolved") -> None:
    """Log errors with full traceback if debug mode is enabled."""
    if DEBUG_MODE:
        logger.error(f"[ERROR] {context} | tenant: {tenant_id} | {exc}\n{traceback.format_exc()}")
    else:
        logger.error(f"[ERROR] {context} | tenant: {tenant_id} | {exc}")


def _tenant_id_from_user(user: Any) -> str:
    """Safe tenant id for error telemetry (never unbound)."""
    if user is None:
        return "unresolved"
    return getattr(user, "tenantId", None) or getattr(user, "tenant_id", None) or "unresolved"


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/verify-token")
@router.post("/verify-token")
async def _verify_token(identity: SovereignIdentity = Depends(get_current_identity)) -> dict[str, object]:
    """Return a bounded public projection for a current active identity."""
    return {"success": True, "status": "VERIFIED", "user": {"id": identity.identity_id, "email": identity.email}}


def _workspace_bootstrap_http_error(
    error: WorkspaceBootstrapProjectionError,
) -> HTTPException:
    """Translate bounded workspace-composition failure without leaking authority state."""
    code = str(error)
    unavailable = {
        "WORKSPACE_BOOTSTRAP_MEMBERSHIP_AUTHORITY_UNAVAILABLE",
        "WORKSPACE_BOOTSTRAP_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE",
        "WORKSPACE_BOOTSTRAP_TENANT_UNAVAILABLE",
    }
    if code in unavailable:
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Workspace authority is unavailable.",
        )
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Workspace access denied.",
    )


@router.get("/workspace-bootstrap")
async def workspace_bootstrap(
    identity: SovereignIdentity = Depends(get_current_identity),
) -> dict[str, object]:
    """Return one server-owned workspace projection after current authority checks."""
    try:
        projection = build_workspace_bootstrap_projection(identity=identity)
    except WorkspaceBootstrapProjectionError as error:
        raise _workspace_bootstrap_http_error(error) from error

    tenant = projection.tenant
    organization = getattr(tenant, "organization", None)

    tenant_name = (
        getattr(organization, "organization_name", None)
        if organization is not None
        else None
    )
    legal_name = (
        getattr(organization, "legal_name", None)
        if organization is not None
        else None
    )
    tenant_status = getattr(tenant, "status", None)
    tenant_status = getattr(tenant_status, "value", tenant_status)

    return {
        "status": "READY",
        "user": {
            "id": projection.principal_id,
            "email": projection.email,
        },
        "workspace": {
            "tenantId": projection.tenant_id,
            "businessRole": projection.business_role,
            "membershipRevision": projection.membership_revision,
            "businessRoleRevision": projection.business_role_revision,
            "tenant": {
                "tenantId": projection.tenant_id,
                "name": tenant_name,
                "legalName": legal_name,
                "status": tenant_status,
            },
        },
    }


# ─── PASSWORD RECOVERY REQUEST ─────────────────────────────────────────────
class PasswordRecoveryStartRequest(BaseModel):
    """Bounded unauthenticated input for recovery initiation.

    The browser supplies only the selected tenant lookup value and email lookup
    value. It cannot assert principal identity, verification status, capability
    identity, token material, expiry, delivery channel, or password authority.
    """

    tenant_id: StrictStr = Field(..., min_length=1, max_length=256)
    email: StrictStr = Field(..., min_length=3, max_length=320)

    class Config:
        """Reject caller-supplied recovery authority fields."""

        extra = "forbid"


def _configured_password_recovery_origin() -> str:
    """Return one server-owned public app origin without trusting request Host.

    The dedicated recovery setting has precedence. Existing production app URL
    aliases are accepted only as deployment configuration and are still subject
    to the recovery service's strict HTTPS/origin validation. An explicitly set
    empty higher-precedence value is returned unchanged so misconfiguration fails
    closed instead of silently falling through to another alias.
    """

    for name in (
        "WILSY_PUBLIC_APP_ORIGIN",
        "WILSY_PUBLIC_APP_URL",
        "CLIENT_URL",
        "FRONTEND_URL",
        "APP_URL",
    ):
        if name in os.environ:
            return os.environ[name]
    return ""


@lru_cache(maxsize=1)
def _password_recovery_request_service() -> PasswordRecoveryRequestService:
    """Build and index the canonical recovery-request chain once per process.

    Configuration is server-owned. The public application origin is never
    derived from request Host, and SMTP credentials are loaded only by the
    transport adapter. Index creation remains outside transaction callbacks.
    """

    contact_registry = VerifiedRecoveryContactRegistry()
    capability_registry = PasswordRecoveryCapabilityRegistry()
    rate_limit = PasswordRecoveryRateLimit()
    contact_registry.ensure_indexes()
    capability_registry.ensure_indexes()
    rate_limit.ensure_indexes()
    origin = _configured_password_recovery_origin()
    return PasswordRecoveryRequestService(
        contact_registry=contact_registry,
        capability_registry=capability_registry,
        auth_registry=get_auth_registry(None),
        rate_limit_gate=rate_limit,
        delivery_adapter=PasswordRecoveryEmailDelivery.from_environment(),
        public_reset_origin=origin,
    )


@router.post("/request-password-reset", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(request: PasswordRecoveryStartRequest) -> dict[str, str]:
    """Accept one password-recovery request without exposing account existence.

    Missing/stale verified contact, delivery failure, and capability issuance
    failure are never projected to the caller because doing so would create an
    existence oracle. Operational failures are logged using stable code-only
    context and the response remains the same generic acceptance. A uniformly
    applied rate-limit rejection may return 429.
    """

    try:
        service = _password_recovery_request_service()
        service.request_password_reset(
            tenant_id=request.tenant_id,
            email=request.email,
            observed_at=datetime.now(timezone.utc),
        )
    except PasswordRecoveryRequestRateLimitedError:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password recovery requests. Please try again later.",
        ) from None
    except PasswordRecoveryRequestServiceError as error:
        _log_error(
            RuntimeError(error.code),
            "PASSWORD_RECOVERY_REQUEST_INTERNAL",
            tenant_id=request.tenant_id,
        )
    except Exception:
        _log_error(
            RuntimeError("PASSWORD_RECOVERY_REQUEST_UNEXPECTED_ERROR"),
            "PASSWORD_RECOVERY_REQUEST_UNEXPECTED_ERROR",
            tenant_id=request.tenant_id,
        )
    return {
        "status": "accepted",
        "message": "If recovery is available for this account, instructions will be sent.",
    }


# ─── RECOVERY CONTACT VERIFICATION ─────────────────────────────────────────
class RecoveryContactVerificationCompleteRequest(BaseModel):
    """Capability-only input for recovery-contact verification completion."""

    tenant_id: StrictStr = Field(..., min_length=1, max_length=256)
    verification_token: StrictStr = Field(..., min_length=1, max_length=4096)

    class Config:
        """Reject browser-supplied principal, address, or contact authority."""

        extra = "forbid"


@lru_cache(maxsize=1)
def _recovery_contact_verification_request_service(
) -> RecoveryContactVerificationRequestService:
    """Build authenticated recovery-contact verification issuance once/process."""

    verification_registry = RecoveryContactVerificationRegistry()
    contact_registry = VerifiedRecoveryContactRegistry()
    rate_limit = PasswordRecoveryRateLimit(
        namespace="recovery-contact-verification",
    )
    verification_registry.ensure_indexes()
    contact_registry.ensure_indexes()
    rate_limit.ensure_indexes()
    return RecoveryContactVerificationRequestService(
        verification_registry=verification_registry,
        contact_registry=contact_registry,
        auth_registry=get_auth_registry(None),
        rate_limit_gate=rate_limit,
        delivery_adapter=RecoveryContactVerificationEmailDelivery.from_environment(),
        public_origin=os.environ.get("WILSY_PUBLIC_APP_ORIGIN", ""),
    )


@lru_cache(maxsize=1)
def _recovery_contact_verification_completion_service(
) -> RecoveryContactVerificationService:
    """Build completion composition and ensure its durable indexes once/process."""

    verification_registry = RecoveryContactVerificationRegistry()
    contact_registry = VerifiedRecoveryContactRegistry()
    verification_registry.ensure_indexes()
    contact_registry.ensure_indexes()
    return RecoveryContactVerificationService(
        verification_registry=verification_registry,
        contact_registry=contact_registry,
        auth_registry=get_auth_registry(None),
    )


@router.post(
    "/recovery-contact/request-verification",
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_recovery_contact_verification(
    identity: SovereignIdentity = Depends(get_current_identity),
) -> dict[str, str]:
    """Issue verification only for the current durable principal email.

    The route accepts no email or tenant body fields. ACCESS authentication
    supplies selectors only; the service re-reads durable principal/email truth.
    """

    try:
        result = _recovery_contact_verification_request_service().request_verification(
            identity=identity,
            observed_at=datetime.now(timezone.utc),
        )
    except RecoveryContactVerificationRequestError as error:
        if error.code == "RECOVERY_CONTACT_VERIFICATION_RATE_LIMITED":
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many recovery-email verification requests. Please try again later.",
            ) from None
        _log_error(
            RuntimeError(error.code),
            "RECOVERY_CONTACT_VERIFICATION_REQUEST_FAILED",
            tenant_id=identity.tenant_id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recovery email verification is temporarily unavailable.",
        ) from None
    return {"status": result.status}


@router.post(
    "/recovery-contact/verify",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def complete_recovery_contact_verification(
    request: RecoveryContactVerificationCompleteRequest,
) -> Response:
    """Consume one email-control capability and establish verified contact truth.

    The route is intentionally unauthenticated so a single-use verification
    link can complete across devices. The capability is bound durably to exact
    tenant/principal/address digests and produces no login session or JWT.
    """

    try:
        _recovery_contact_verification_completion_service().verify_contact(
            tenant_id=request.tenant_id,
            verification_token=request.verification_token,
        )
    except RecoveryContactVerificationServiceError as error:
        if error.code in {
            RecoveryContactVerificationCode.INVALID_REQUEST,
            RecoveryContactVerificationCode.VERIFICATION_INVALID,
            RecoveryContactVerificationCode.VERIFICATION_REPLAYED,
            RecoveryContactVerificationCode.PRINCIPAL_MISMATCH,
            RecoveryContactVerificationCode.EMAIL_CHANGED,
        }:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recovery email verification link is invalid or expired.",
            ) from None
        _log_error(
            RuntimeError(error.code.value),
            "RECOVERY_CONTACT_VERIFICATION_COMPLETE_FAILED",
            tenant_id=request.tenant_id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recovery email verification is temporarily unavailable.",
        ) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─── PASSWORD RESET COMPLETION ─────────────────────────────────────────────
class PasswordResetRequest(BaseModel):
    """Bounded transport input for unauthenticated reset completion.

    The request carries only a tenant lookup selector, the transient recovery
    capability, and the proposed password. Durable capability binding,
    password policy, hashing, credential revision, revocation, and transaction
    ownership remain in ``PasswordResetService``. Strict strings prevent
    coercion of structured or numeric authority fields into transport values;
    the bounds limit request size without reproducing password policy.
    """

    tenant_id: StrictStr = Field(..., min_length=1, max_length=256)
    recovery_token: StrictStr = Field(..., min_length=1, max_length=4096)
    new_password: StrictStr = Field(..., min_length=1, max_length=4096)

    class Config:
        """Reject browser-supplied authority fields not owned by this adapter."""

        extra = "forbid"


def _password_reset_http_error(error: PasswordResetServiceError) -> HTTPException:
    """Map service outcomes to privacy-bounded client/server responses.

    Recovery lifecycle states intentionally share one client-visible response,
    while policy rejection is client-correctable without exposing checker
    details. Persistence, hashing, transaction, and unexpected failures remain
    bounded server errors with no exception text or durable-state disclosure.
    """

    if error.code in {
        PasswordResetCode.INVALID_REQUEST,
        PasswordResetCode.RECOVERY_INVALID,
        PasswordResetCode.RECOVERY_REPLAYED,
    }:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset request is invalid or expired.",
        )
    if error.code is PasswordResetCode.POLICY_REJECTED:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The new password does not meet password requirements.",
        )
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Password reset is temporarily unavailable.",
    )


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def complete_password_reset(request: PasswordResetRequest) -> Response:
    """Complete one recovery-authorized password reset without auto-login.

    The route is intentionally unauthenticated: the durable recovery
    capability, not an access JWT or browser identity claim, is the reset
    authority. Exactly one certified service call performs the caller-owned
    transaction. A successful reset returns no token, session, revision, hash,
    or capability projection; the user must authenticate through normal login
    and MFA afterward.
    """

    try:
        service = PasswordResetService(
            blocklist_checker=PwnedPasswordBlocklistChecker(),
        )
        service.reset_password(
            tenant_id=request.tenant_id,
            recovery_token=request.recovery_token,
            new_password=request.new_password,
            context_terms=None,
        )
    except PasswordResetServiceError as error:
        raise _password_reset_http_error(error) from None
    except Exception:
        # Never render exception text: provider, database, and transaction
        # failures may carry secret-bearing or durable-state diagnostics.
        _log_error(RuntimeError("PASSWORD_RESET_UNEXPECTED_ERROR"), "PASSWORD_RESET_UNEXPECTED_ERROR")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Password reset is temporarily unavailable.",
        ) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ─── LOGIN ──────────────────────────────────────────────────────────────────
@router.post("/login", response_model=AuthResponse, response_model_exclude_none=True)
async def login(request: AuthRequest):
    try:
        auth_registry = get_auth_registry(None)
        user = auth_registry.authenticate(request.email, request.password)
        if not user:
            broadcast_telemetry(
                "unresolved", "AUTH", "LOGIN_FAILED", "auth_router", {"email": request.email}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        existing_otp_secret = auth_registry.get_otp_secret(user.id)

        # A durable secret with a missing enrollment flag is reconciliation, not
        # first-time setup.  Never call get_otp_uri() in this branch: that would
        # disclose or rotate an already-established provisioning secret.
        if not user.mfaRegistered and existing_otp_secret:
            broadcast_telemetry(
                user.tenantId, "AUTH", "MFA_RECONCILIATION_REQUIRED", "auth_router", {"userId": user.id}
            )
            return AuthResponse(
                status="MFA_RECONCILIATION_REQUIRED",
                requiresMFA=True,
                mfaSetup=False,
                qrCode=None,
                tempToken=auth_registry.generate_pre_auth_jwt(
                    user.id, user.tenantId, user.role, user.permissions
                ),
            )

        # Only a user with no durable OTP secret may enter first-time setup.
        if not user.mfaRegistered:
            qr_uri = auth_registry.get_otp_uri(user.id, user.email)
            temp_token = auth_registry.generate_pre_auth_jwt(
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

        temp_token = auth_registry.generate_pre_auth_jwt(
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
@router.post("/validate-mfa-setup", response_model=AuthResponse, response_model_exclude_none=True)
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
                "unresolved", "AUTH", "MFA_SETUP_USER_NOT_FOUND", "auth_router", {"email": request.email}
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

        # 3. Mark user as MFA registered and prove the durable write before any
        # session/token is issued.  This is the same path used for legacy users.
        updated_user = auth_registry.update_user(user.id, mfaRegistered=True)
        if updated_user is None or not updated_user.mfaRegistered:
            raise PyMongoError("MFA enrollment persistence could not be confirmed")
        updated_user = auth_registry.get_user_by_id(updated_user.id)
        if updated_user is None or not updated_user.mfaRegistered:
            raise PyMongoError("MFA enrollment durable re-read failed")

        # 4. Create a session (so the user is automatically logged in after setup)
        session = auth_registry.create_session(updated_user)

        broadcast_telemetry(
            updated_user.tenantId, "AUTH", "MFA_SETUP_SUCCESS", "auth_router", {"userId": updated_user.id}
        )

        user_data = {
            "id": updated_user.id,
            "email": updated_user.email,
            "firstName": updated_user.firstName,
            "lastName": updated_user.lastName,
            "role": updated_user.role,
            "permissions": updated_user.permissions,
            "tenantId": updated_user.tenantId,
            "tenantAlias": None,
            "mfaRegistered": updated_user.mfaRegistered,
            "hasSignedCovenant": updated_user.hasSignedCovenant,
        }

        return AuthResponse(
            status="AUTHENTICATED",
            token=session.token,
            user=user_data,
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
@router.post("/verify-otp", response_model=AuthResponse, response_model_exclude_none=True)
@router.post("/verify-3fa", response_model=AuthResponse, response_model_exclude_none=True)
async def verify_otp(request: VerifyOTPRequest):
    user: Any = None
    try:
        auth_registry = get_auth_registry(None)

        # Get the code from either field (frontend sends "code" or "otp")
        code = request.code or request.otp

        # Explicitly check None to satisfy type checker
        if code is None:
            broadcast_telemetry(
                "unresolved",
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
                "unresolved",
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
                "unresolved",
                "AUTH",
                "OTP_USER_NOT_FOUND",
                "auth_router",
                {"email": request.email},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
            )

        if not user.mfaRegistered and not auth_registry.get_otp_secret(user.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="MFA enrollment is incomplete. Complete authenticator setup first.",
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

        if not user.mfaRegistered:
            updated_user = auth_registry.update_user(user.id, mfaRegistered=True)
            if updated_user is None or not updated_user.mfaRegistered:
                raise PyMongoError("MFA reconciliation persistence could not be confirmed")
            user = auth_registry.get_user_by_id(updated_user.id)
            if user is None or not user.mfaRegistered:
                raise PyMongoError("MFA reconciliation durable re-read failed")

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
        tenant: Any = None
        canonical_resolver = getattr(TenantRegistry, "resolve_canonical_tenant", None)
        if callable(canonical_resolver):
            tenant = canonical_resolver(request.alias, allow_alias=True)
        elif hasattr(TenantRegistry, "get_tenant_by_alias"):
            tenant = TenantRegistry.get_tenant_by_alias(request.alias)
        elif hasattr(TenantRegistry, "get"):
            tenant = TenantRegistry.get(request.alias)

        if not tenant:
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
        tenant_projection: dict[str, Any] = {
            "tenantId": tenant.tenant_id,
            "alias": tenant.alias or request.alias,
            "name": tenant.organization.organization_name,
            "region": tenant.organization.regions[0]
            if tenant.organization.regions
            else "GLOBAL",
            "plan": tenant.organization.plan.value
            if hasattr(tenant.organization.plan, "value")
            else str(tenant.organization.plan),
            "status": tenant.status,
        }
        legal_name = getattr(tenant.organization, "legal_name", None)
        if isinstance(legal_name, str) and legal_name.strip():
            tenant_projection["legalName"] = legal_name.strip()
        verified = getattr(tenant, "verified", None)
        if isinstance(verified, bool):
            tenant_projection["verified"] = verified

        return {
            "success": True,
            "tenant": tenant_projection,
        }
    except PyMongoError as e:
        _log_error(e, "DISCOVER_DB_ERROR")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error during tenant discovery. Please try again later.",
        )
    except TenantRegistryError as e:
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
    broadcast_telemetry("unresolved", "AUTH", "LOGOUT", "auth_router", {})
    return {"status": "success", "message": "Logged out"}


# ARTIFACT: auth_router.py
# VERSION: v1.8.0-R10E72-PRODUCTION-RECOVERY-ORIGIN-BINDING
# AUTHORITY BOUNDARY: Authentication/recovery/contact-verification HTTP routing and bounded projections only;
# credential, contact-verification, recovery, tenant, authorization, and financial truth remain separate.
# TENANT POSTURE: recovery request uses tenant only as a lookup scope; no caller tenant authority.
# FAIL-CLOSED POSTURE: auth fails closed; recovery initiation is enumeration-safe generic acceptance.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
