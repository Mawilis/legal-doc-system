"""HTTP transport for the tenant-neutral global-principal login journey.

Global routes are additive. Legacy tenant-bound endpoints remain mounted and
unchanged while global session currentness is migrated and certified.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, StrictStr
from pymongo.errors import PyMongoError

from tools.eos.auth.authentication import get_current_identity
from tools.eos.auth.global_principal_mfa_enrollment_service import (
    CHALLENGE_COLLECTION as GLOBAL_PRINCIPAL_MFA_ENROLLMENT_CHALLENGE_COLLECTION,
    FACTOR_COLLECTION as GLOBAL_PRINCIPAL_MFA_ENROLLMENT_FACTOR_COLLECTION,
    GlobalPrincipalMfaEnrollmentCodeRejected,
    GlobalPrincipalMfaEnrollmentRejected,
    GlobalPrincipalMfaEnrollmentService,
    GlobalPrincipalMfaEnrollmentUnavailable,
)
from tools.eos.auth.global_principal_mfa_legacy_migration_service import (
    LEGACY_FACTOR_COLLECTION as LEGACY_MFA_FACTOR_COLLECTION,
    GLOBAL_FACTOR_COLLECTION as GLOBAL_MIGRATED_MFA_FACTOR_COLLECTION,
    GlobalPrincipalMfaLegacyMigrationCodeRejected,
    GlobalPrincipalMfaLegacyMigrationRejected,
    GlobalPrincipalMfaLegacyMigrationService,
    GlobalPrincipalMfaLegacyMigrationUnavailable,
)

from tools.eos.auth.global_principal_mfa_session_transition import (
    GlobalPrincipalMfaSessionTransition,
)
from tools.eos.auth.global_principal_totp_verifier import (
    COLLECTION as GLOBAL_PRINCIPAL_MFA_FACTOR_COLLECTION,
    GlobalPrincipalFactorRejected,
    GlobalPrincipalFactorUnavailable,
)
from tools.eos.auth.global_principal_session_authority import (
    GlobalPrincipalSessionAuthority,
    GlobalPrincipalSessionError,
    GlobalPrincipalSessionRejected,
    GlobalPrincipalSessionUnavailable,
)
from tools.eos.auth.membership_selection_challenge import (
    MembershipSelectionChallengeRejected,
    MembershipSelectionChallengeService,
    MembershipSelectionChallengeUnavailable,
)
from tools.eos.auth.membership_selection_projection import (
    MembershipSelectionProjectionError,
    build_membership_selection_page,
)
from tools.eos.auth.principal_authentication_rate_limit import (
    PrincipalAuthenticationRateLimit,
    PrincipalAuthenticationRateLimited,
    PrincipalAuthenticationRateLimitUnavailable,
)
from tools.eos.auth.principal_credential_authentication import (
    GlobalPrincipalAuthenticationUnavailable,
    authenticate_global_principal,
)
from tools.eos.auth.principal_credential_repository import (
    COLLECTION as PRINCIPAL_CREDENTIAL_COLLECTION,
    PrincipalCredentialRepository,
    PrincipalCredentialRepositoryError,
)
from tools.eos.auth.global_principal_system_session_authority import (
    CHALLENGE_COLLECTION as SYSTEM_MFA_CHALLENGE_COLLECTION,
    SESSION_COLLECTION as SYSTEM_SESSION_COLLECTION,
    GlobalPrincipalSystemMfaChallengeService,
    GlobalPrincipalSystemSessionAuthority,
    GlobalPrincipalSystemSessionRejected,
    GlobalPrincipalSystemSessionUnavailable,
)
from tools.eos.system_services.eos_authorizer import (
    SystemServicesAuthorizationError,
    SystemServicesAuthorizationUnavailable,
)
from tools.eos.kernel.db import get_client, get_database

router = APIRouter(prefix="/auth/global", tags=["Global Principal Authentication"])


class GlobalCredentialRequest(BaseModel):
    email: StrictStr
    password: StrictStr


class GlobalMembershipSelectionRequest(BaseModel):
    selection_challenge: StrictStr
    tenant_id: StrictStr
    business_role: StrictStr

class GlobalMembershipOptionsRequest(BaseModel):
    selection_challenge: StrictStr
    after_tenant_id: StrictStr | None = None


class GlobalMfaEnrollmentStartRequest(BaseModel):
    email: StrictStr
    password: StrictStr


class GlobalMfaEnrollmentConfirmRequest(BaseModel):
    enrollment_challenge: StrictStr
    code: StrictStr


class GlobalMfaLegacyMigrationRequest(BaseModel):
    email: StrictStr
    password: StrictStr
    code: StrictStr


class GlobalMfaVerificationRequest(BaseModel):
    mfa_challenge: StrictStr
    code: StrictStr


class GlobalRefreshRequest(BaseModel):
    refresh_token: StrictStr


def _require_ready(request: Request, state_name: str) -> None:
    if getattr(request.app.state, state_name, False) is not True:
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE")


def _begin_transaction() -> tuple[Any, Any]:
    client = get_client()
    database = get_database()
    if client is None or database is None:
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE")
    session = client.start_session()
    try:
        session.start_transaction()
    except Exception:
        session.end_session()
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    return session, database


def _abort_if_active(session: Any) -> None:
    marker = getattr(session, "in_transaction", False)
    active = marker() if callable(marker) else marker
    if active is True:
        session.abort_transaction()


def _rate_limit_or_http(rate_gate: PrincipalAuthenticationRateLimit, email: str, source: str, now: datetime) -> None:
    try:
        rate_gate.require_allowed(email=email, source_address=source, observed_at=now)
    except PrincipalAuthenticationRateLimited as error:
        raise HTTPException(
            status_code=429,
            detail="Too many unsuccessful authentication attempts. Try again later.",
            headers={"Retry-After": str(error.retry_after_seconds)},
        ) from None
    except PrincipalAuthenticationRateLimitUnavailable:
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None


def _record_failure(rate_gate: PrincipalAuthenticationRateLimit, email: str, source: str, now: datetime) -> None:
    try:
        rate_gate.record_failure(email=email, source_address=source, observed_at=now)
    except PrincipalAuthenticationRateLimitUnavailable:
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None


def _membership_payload(page: Any) -> list[dict[str, Any]]:
    return [
        {
            "tenant_id": membership.tenant_id,
            "membership_revision": membership.membership_revision,
            "capacities": [
                {
                    "business_role": capacity.business_role,
                    "workspace_id": capacity.workspace_id,
                    "capacity_revision": capacity.business_role_revision,
                }
                for capacity in membership.capacities
            ],
        }
        for membership in page.memberships
    ]


@router.post("/login")
async def global_login(payload: GlobalCredentialRequest, request: Request) -> dict[str, Any]:
    """Verify tenant-neutral credentials and issue a one-time membership selector."""
    _require_ready(request, "global_principal_auth_indexes_ready")
    _require_ready(request, "global_principal_mfa_factor_indexes_ready")
    if getattr(request.app.state, "global_principal_totp_verifier", None) is None:
        raise HTTPException(status_code=503, detail="GLOBAL_MFA_KEY_SERVICE_UNAVAILABLE")
    now = datetime.now(timezone.utc)
    peer = request.client
    if peer is None or not isinstance(peer.host, str) or not peer.host:
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE")
    source = peer.host
    rate_gate = PrincipalAuthenticationRateLimit()
    _rate_limit_or_http(rate_gate, payload.email, source, now)
    try:
        principal = authenticate_global_principal(
            email=payload.email,
            password=payload.password,
        )
    except GlobalPrincipalAuthenticationUnavailable:
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    if principal is None:
        _record_failure(rate_gate, payload.email, source, now)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    try:
        rate_gate.record_success(email=payload.email, observed_at=now)
    except PrincipalAuthenticationRateLimitUnavailable:
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    if principal.mfa_enabled is not True:
        raise HTTPException(status_code=409, detail="GLOBAL_MFA_ENROLLMENT_REQUIRED")

    session, database = _begin_transaction()
    try:
        factor = database[GLOBAL_PRINCIPAL_MFA_FACTOR_COLLECTION].find_one(
            {
                "principal_id": principal.principal_id,
                "status": "ACTIVE",
                "credential_revision": principal.credential_revision,
            },
            projection={"principal_id": 1},
            session=session,
        )
        if not isinstance(factor, dict) or factor.get("principal_id") != principal.principal_id:
            _abort_if_active(session)
            raise HTTPException(status_code=409, detail="GLOBAL_MFA_FACTOR_MIGRATION_REQUIRED")
        page = build_membership_selection_page(
            principal_id=principal.principal_id,
            session=session,
        )
        if not page.memberships:
            _require_ready(request, "global_principal_system_session_indexes_ready")
            if (
                getattr(request.app.state, "system_services_authority_ready", False) is not True
                or getattr(request.app.state, "system_services_case_indexes_ready", False) is not True
            ):
                _abort_if_active(session)
                raise HTTPException(status_code=503, detail="SYSTEM_AUTHORITY_UNAVAILABLE")
            authorizer = getattr(request.app.state, "system_services_authorizer", None)
            if authorizer is None:
                _abort_if_active(session)
                raise HTTPException(status_code=503, detail="SYSTEM_AUTHORITY_UNAVAILABLE")
            try:
                authorizer.require(
                    principal_id=principal.principal_id,
                    permission_id="system_services:queue:read",
                    session=session,
                )
            except SystemServicesAuthorizationError:
                _abort_if_active(session)
                raise HTTPException(status_code=403, detail="No eligible workspace is assigned to this principal.") from None
            except SystemServicesAuthorizationUnavailable:
                _abort_if_active(session)
                raise HTTPException(status_code=503, detail="SYSTEM_AUTHORITY_UNAVAILABLE") from None
            challenge_token, expires_at = GlobalPrincipalSystemMfaChallengeService(
                collection=database[SYSTEM_MFA_CHALLENGE_COLLECTION],
            ).issue(
                principal_id=principal.principal_id,
                credential_revision=principal.credential_revision,
                session=session,
                now=now,
            )
            session.commit_transaction()
            return {
                "status": "MFA_REQUIRED",
                "scope": "SYSTEM",
                "mfa_challenge": challenge_token,
                "expires_at": expires_at.isoformat(),
                "workspace_id": "SYSTEM_SERVICES",
            }
        challenge = MembershipSelectionChallengeService().issue_membership_selection_challenge(
            principal_id=principal.principal_id,
            credential_revision=principal.credential_revision,
            session=session,
            now=now,
        )
        session.commit_transaction()
        return {
            "status": "MEMBERSHIP_SELECTION_REQUIRED",
            "selection_challenge": challenge.challenge_token,
            "expires_at": challenge.expires_at.isoformat(),
            "memberships": _membership_payload(page),
            "next_cursor": page.next_cursor,
        }
    except (MembershipSelectionChallengeRejected, MembershipSelectionProjectionError, GlobalPrincipalSystemSessionRejected):
        _abort_if_active(session)
        raise HTTPException(status_code=401, detail="Membership selection is unavailable") from None
    except (MembershipSelectionChallengeUnavailable, GlobalPrincipalSystemSessionUnavailable, PyMongoError):
        _abort_if_active(session)
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    except Exception:
        _abort_if_active(session)
        raise
    finally:
        session.end_session()


@router.post("/membership-options")
async def membership_options(payload: GlobalMembershipOptionsRequest, request: Request) -> dict[str, Any]:
    """Return the next bounded page only to a holder of the live selection challenge."""
    _require_ready(request, "global_principal_auth_indexes_ready")
    session, _database = _begin_transaction()
    try:
        challenge = MembershipSelectionChallengeService().get_selection_challenge_context(
            selection_challenge_token=payload.selection_challenge,
            session=session,
        )
        page = build_membership_selection_page(
            principal_id=challenge.principal_id,
            after_tenant_id=payload.after_tenant_id,
            session=session,
        )
        session.commit_transaction()
        return {
            "status": "MEMBERSHIP_SELECTION_REQUIRED",
            "memberships": _membership_payload(page),
            "next_cursor": page.next_cursor,
        }
    except (MembershipSelectionChallengeRejected, MembershipSelectionProjectionError):
        _abort_if_active(session)
        raise HTTPException(status_code=401, detail="Membership selection is invalid or expired") from None
    except (MembershipSelectionChallengeUnavailable, PyMongoError):
        _abort_if_active(session)
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    except Exception:
        _abort_if_active(session)
        raise
    finally:
        session.end_session()


@router.post("/select-membership")
async def select_membership(payload: GlobalMembershipSelectionRequest, request: Request) -> dict[str, Any]:
    """Consume the selector and bind MFA to one explicit tenant/business capacity."""
    _require_ready(request, "global_principal_auth_indexes_ready")
    _require_ready(request, "global_principal_session_indexes_ready")
    session, _database = _begin_transaction()
    try:
        challenge = MembershipSelectionChallengeService().select_membership_and_issue_mfa_challenge(
            selection_challenge_token=payload.selection_challenge,
            tenant_id=payload.tenant_id,
            business_role=payload.business_role,
            session=session,
        )
        session.commit_transaction()
        return {
            "status": "MFA_REQUIRED",
            "mfa_challenge": challenge.challenge_token,
            "expires_at": challenge.expires_at.isoformat(),
            "tenant_id": challenge.tenant_id,
            "business_role": challenge.business_role,
            "workspace_id": challenge.workspace_id,
        }
    except MembershipSelectionChallengeRejected:
        _abort_if_active(session)
        raise HTTPException(status_code=401, detail="Membership selection is invalid or expired") from None
    except (MembershipSelectionChallengeUnavailable, PyMongoError):
        _abort_if_active(session)
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    except Exception:
        _abort_if_active(session)
        raise
    finally:
        session.end_session()


@router.post("/verify-mfa")
async def verify_global_mfa(payload: GlobalMfaVerificationRequest, request: Request) -> dict[str, Any]:
    """Verify principal TOTP and atomically consume challenge plus issue scoped session."""
    _require_ready(request, "global_principal_auth_indexes_ready")
    _require_ready(request, "global_principal_session_indexes_ready")
    _require_ready(request, "global_principal_mfa_factor_indexes_ready")
    verifier = getattr(request.app.state, "global_principal_totp_verifier", None)
    if verifier is None:
        raise HTTPException(status_code=503, detail="GLOBAL_MFA_KEY_SERVICE_UNAVAILABLE")
    now = datetime.now(timezone.utc)
    peer = request.client
    if peer is None or not isinstance(peer.host, str) or not peer.host:
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE")
    source = peer.host
    is_system_challenge = payload.mfa_challenge.startswith("sysmfa_")
    if is_system_challenge:
        _require_ready(request, "global_principal_system_session_indexes_ready")
    session, database = _begin_transaction()
    try:
        if is_system_challenge:
            system_challenge_service = GlobalPrincipalSystemMfaChallengeService(
                collection=database[SYSTEM_MFA_CHALLENGE_COLLECTION],
            )
            factor_context = system_challenge_service.get_factor_context(
                payload.mfa_challenge,
                session=session,
                now=now,
            )
            challenge_service = None
        else:
            challenge_service = MembershipSelectionChallengeService()
            system_challenge_service = None
            factor_context = challenge_service.get_mfa_challenge_factor_context(
                mfa_challenge_token=payload.mfa_challenge,
                session=session,
                now=now,
            )

        credential = PrincipalCredentialRepository.get_by_principal(
            factor_context.principal_id,
            session=session,
        )
        rate_gate = PrincipalAuthenticationRateLimit()
        _rate_limit_or_http(rate_gate, credential.normalized_email, source, now)
        verified = verifier.verify(
            principal_id=factor_context.principal_id,
            credential_revision=factor_context.credential_revision,
            code=payload.code,
            session=session,
            now=now,
        )
        if not verified:
            _abort_if_active(session)
            _record_failure(rate_gate, credential.normalized_email, source, now)
            raise HTTPException(status_code=401, detail="Invalid authenticator code")

        if is_system_challenge:
            assert system_challenge_service is not None
            system_challenge_service.consume(
                payload.mfa_challenge,
                principal_id=factor_context.principal_id,
                credential_revision=factor_context.credential_revision,
                session=session,
                now=now,
            )
            receipt = GlobalPrincipalSystemSessionAuthority(
                sessions=database[SYSTEM_SESSION_COLLECTION],
                authorizer=getattr(request.app.state, "system_services_authorizer", None),
            ).issue_after_mfa(
                factor_context.principal_id,
                factor_context.credential_revision,
                session=session,
                now=now,
            )
            session.commit_transaction()
            rate_gate.record_success(email=credential.normalized_email, observed_at=now)
            return {
                "status": "AUTHENTICATED",
                "scope": "SYSTEM",
                "access_token": receipt.access_token,
                "token_type": "Bearer",
                "access_expires_at": receipt.access_expires_at.isoformat(),
                "principal_id": receipt.principal_id,
                "workspace_id": "SYSTEM_SERVICES",
            }

        assert challenge_service is not None
        transition = GlobalPrincipalMfaSessionTransition(
            challenge_service=challenge_service,
            session_authority=GlobalPrincipalSessionAuthority(),
        )
        receipt = transition.complete_after_verified_factor(
            mfa_challenge_token=payload.mfa_challenge,
            session=session,
            now=now,
        )
        session.commit_transaction()
        rate_gate.record_success(email=credential.normalized_email, observed_at=now)
        return {
            "status": "AUTHENTICATED",
            "access_token": receipt.access_token,
            "refresh_token": receipt.refresh_token,
            "token_type": "Bearer",
            "access_expires_at": receipt.access_expires_at.isoformat(),
            "refresh_expires_at": receipt.refresh_expires_at.isoformat(),
            "principal_id": receipt.principal_id,
            "tenant_id": receipt.tenant_id,
            "business_role": receipt.business_role,
            "workspace_id": receipt.workspace_id,
        }
    except HTTPException:
        _abort_if_active(session)
        raise
    except (MembershipSelectionChallengeRejected, GlobalPrincipalSystemSessionRejected):
        _abort_if_active(session)
        raise HTTPException(status_code=401, detail="MFA challenge is invalid or expired") from None
    except (
        GlobalPrincipalFactorRejected,
        GlobalPrincipalSessionRejected,
    ):
        _abort_if_active(session)
        raise HTTPException(status_code=401, detail="MFA challenge or authenticator code is invalid") from None
    except (
        GlobalPrincipalFactorUnavailable,
        MembershipSelectionChallengeUnavailable,
        GlobalPrincipalSessionUnavailable,
        GlobalPrincipalSystemSessionUnavailable,
        PrincipalCredentialRepositoryError,
        PyMongoError,
    ):
        _abort_if_active(session)
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    except Exception:
        _abort_if_active(session)
        raise
    finally:
        session.end_session()


@router.post("/refresh")
async def refresh_global_session(payload: GlobalRefreshRequest, request: Request) -> dict[str, Any]:
    """Rotate one opaque global refresh bearer in a caller-owned transaction."""
    _require_ready(request, "global_principal_session_indexes_ready")
    session, _database = _begin_transaction()
    try:
        receipt = GlobalPrincipalSessionAuthority().rotate_refresh_token(
            payload.refresh_token,
            session=session,
        )
        session.commit_transaction()
        return {
            "status": "REFRESHED",
            "access_token": receipt.access_token,
            "refresh_token": receipt.refresh_token,
            "token_type": "Bearer",
            "access_expires_at": receipt.access_expires_at.isoformat(),
            "refresh_expires_at": receipt.refresh_expires_at.isoformat(),
        }
    except GlobalPrincipalSessionRejected:
        _abort_if_active(session)
        raise HTTPException(status_code=401, detail="Refresh credential is invalid or expired") from None
    except (GlobalPrincipalSessionUnavailable, PyMongoError):
        _abort_if_active(session)
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    except Exception:
        _abort_if_active(session)
        raise
    finally:
        session.end_session()


@router.post("/logout")
async def logout_global_session(
    identity: Any = Depends(get_current_identity),
) -> dict[str, str]:
    """Revoke the exact global tenant or tenant-neutral SYSTEM session."""
    reference = getattr(identity, "session_reference", None)
    principal_id = getattr(identity, "identity_id", None)
    tenant_id = getattr(identity, "tenant_id", None)
    if (
        isinstance(reference, str)
        and reference.startswith("WILSYS-SYSTEM-SESSION-")
        and isinstance(principal_id, str)
        and tenant_id == "SYSTEM"
    ):
        session, database = _begin_transaction()
        try:
            revoked = GlobalPrincipalSystemSessionAuthority(
                sessions=database[SYSTEM_SESSION_COLLECTION],
            ).revoke(
                principal_id=principal_id,
                session_reference=reference,
                session=session,
            )
            if not revoked:
                _abort_if_active(session)
                raise HTTPException(status_code=401, detail="Session is no longer current")
            session.commit_transaction()
            return {"status": "SIGNED_OUT"}
        except HTTPException:
            _abort_if_active(session)
            raise
        except (GlobalPrincipalSystemSessionRejected, GlobalPrincipalSystemSessionUnavailable, PyMongoError):
            _abort_if_active(session)
            raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
        finally:
            session.end_session()

    if (
        not isinstance(reference, str)
        or not reference.startswith("WILSYGLOBALSESSION-")
        or not isinstance(principal_id, str)
        or not isinstance(tenant_id, str)
    ):
        raise HTTPException(status_code=409, detail="A global principal session is required")
    session, _database = _begin_transaction()
    try:
        revoked = GlobalPrincipalSessionAuthority().revoke_session(
            principal_id=principal_id,
            tenant_id=tenant_id,
            session_reference=reference,
            session=session,
        )
        if not revoked:
            _abort_if_active(session)
            raise HTTPException(status_code=401, detail="Session is no longer current")
        session.commit_transaction()
        return {"status": "SIGNED_OUT"}
    except HTTPException:
        _abort_if_active(session)
        raise
    except GlobalPrincipalSessionError:
        _abort_if_active(session)
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    except PyMongoError:
        _abort_if_active(session)
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    except Exception:
        _abort_if_active(session)
        raise
    finally:
        session.end_session()


@router.post("/mfa/enrollment/start")
async def start_global_mfa_enrollment(
    payload: GlobalMfaEnrollmentStartRequest,
    request: Request,
) -> dict[str, Any]:
    """Authenticate the principal and issue one encrypted, short-lived TOTP setup challenge."""
    _require_ready(request, "global_principal_auth_indexes_ready")
    _require_ready(request, "global_principal_mfa_enrollment_indexes_ready")
    kms = getattr(request.app.state, "global_principal_mfa_kms_envelope", None)
    if kms is None:
        raise HTTPException(status_code=503, detail="GLOBAL_MFA_KEY_SERVICE_UNAVAILABLE")
    now = datetime.now(timezone.utc)
    peer = request.client
    if peer is None or not isinstance(peer.host, str) or not peer.host:
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE")
    source = peer.host
    rate_gate = PrincipalAuthenticationRateLimit()
    _rate_limit_or_http(rate_gate, payload.email, source, now)
    try:
        principal = authenticate_global_principal(email=payload.email, password=payload.password)
    except GlobalPrincipalAuthenticationUnavailable:
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    if principal is None:
        _record_failure(rate_gate, payload.email, source, now)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    try:
        rate_gate.record_success(email=payload.email, observed_at=now)
    except PrincipalAuthenticationRateLimitUnavailable:
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None

    session, database = _begin_transaction()
    try:
        service = GlobalPrincipalMfaEnrollmentService(
            kms=kms,
            challenge_collection=database[GLOBAL_PRINCIPAL_MFA_ENROLLMENT_CHALLENGE_COLLECTION],
            factor_collection=database[GLOBAL_PRINCIPAL_MFA_ENROLLMENT_FACTOR_COLLECTION],
            legacy_factor_collection=database[LEGACY_MFA_FACTOR_COLLECTION],
            credential_collection=database[PRINCIPAL_CREDENTIAL_COLLECTION],
        )
        receipt = service.issue(
            principal_id=principal.principal_id,
            credential_revision=principal.credential_revision,
            session=session,
            now=now,
        )
        session.commit_transaction()
        return {
            "status": "MFA_ENROLLMENT_REQUIRED",
            "enrollment_challenge": receipt.challenge_token,
            "expires_at": receipt.expires_at.isoformat(),
            "provisioning_uri": receipt.provisioning_uri,
            "secret": receipt.secret,
        }
    except GlobalPrincipalMfaEnrollmentRejected as error:
        _abort_if_active(session)
        status = 409 if str(error) in {
            "GLOBAL_MFA_RECOVERY_REQUIRED",
            "GLOBAL_MFA_ENROLLMENT_ALREADY_PENDING",
        } else 401
        raise HTTPException(status_code=status, detail=str(error)) from None
    except GlobalPrincipalMfaEnrollmentUnavailable:
        _abort_if_active(session)
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    except PyMongoError:
        _abort_if_active(session)
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    except Exception:
        _abort_if_active(session)
        raise
    finally:
        session.end_session()


@router.post("/mfa/enrollment/confirm")
async def confirm_global_mfa_enrollment(
    payload: GlobalMfaEnrollmentConfirmRequest,
    request: Request,
) -> dict[str, Any]:
    """Confirm possession of the new TOTP factor and atomically activate it."""
    _require_ready(request, "global_principal_mfa_enrollment_indexes_ready")
    kms = getattr(request.app.state, "global_principal_mfa_kms_envelope", None)
    if kms is None:
        raise HTTPException(status_code=503, detail="GLOBAL_MFA_KEY_SERVICE_UNAVAILABLE")
    session, database = _begin_transaction()
    try:
        service = GlobalPrincipalMfaEnrollmentService(
            kms=kms,
            challenge_collection=database[GLOBAL_PRINCIPAL_MFA_ENROLLMENT_CHALLENGE_COLLECTION],
            factor_collection=database[GLOBAL_PRINCIPAL_MFA_ENROLLMENT_FACTOR_COLLECTION],
        )
        completion = service.confirm(
            challenge_token=payload.enrollment_challenge,
            code=payload.code,
            session=session,
            now=datetime.now(timezone.utc),
        )
        session.commit_transaction()
        return {
            "status": "MFA_ENROLLED",
            "principal_id": completion.principal_id,
            "credential_revision": completion.credential_revision,
            "next_step": "SIGN_IN_AGAIN",
        }
    except GlobalPrincipalMfaEnrollmentCodeRejected as error:
        # Invalid codes are the one failure path whose attempt counter must commit.
        session.commit_transaction()
        raise HTTPException(status_code=401, detail=str(error)) from None
    except GlobalPrincipalMfaEnrollmentRejected as error:
        _abort_if_active(session)
        status = 409 if str(error) == "GLOBAL_MFA_ENROLLMENT_ATTEMPTS_EXHAUSTED" else 401
        raise HTTPException(status_code=status, detail=str(error)) from None
    except GlobalPrincipalMfaEnrollmentUnavailable:
        _abort_if_active(session)
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    except PyMongoError:
        _abort_if_active(session)
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    except Exception:
        _abort_if_active(session)
        raise
    finally:
        session.end_session()


@router.post("/mfa/migrate-legacy")
async def migrate_legacy_global_mfa_factor(
    payload: GlobalMfaLegacyMigrationRequest,
    request: Request,
) -> dict[str, Any]:
    """Migrate only an existing factor after password and legacy-TOTP proof."""
    _require_ready(request, "global_principal_auth_indexes_ready")
    _require_ready(request, "global_principal_mfa_factor_indexes_ready")
    kms = getattr(request.app.state, "global_principal_mfa_kms_envelope", None)
    if kms is None:
        raise HTTPException(status_code=503, detail="GLOBAL_MFA_KEY_SERVICE_UNAVAILABLE")
    now = datetime.now(timezone.utc)
    peer = request.client
    if peer is None or not isinstance(peer.host, str) or not peer.host:
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE")
    source = peer.host
    rate_gate = PrincipalAuthenticationRateLimit()
    _rate_limit_or_http(rate_gate, payload.email, source, now)
    try:
        principal = authenticate_global_principal(email=payload.email, password=payload.password)
    except GlobalPrincipalAuthenticationUnavailable:
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    if principal is None:
        _record_failure(rate_gate, payload.email, source, now)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    session, database = _begin_transaction()
    try:
        service = GlobalPrincipalMfaLegacyMigrationService(
            kms=kms,
            legacy_factor_collection=database[LEGACY_MFA_FACTOR_COLLECTION],
            factor_collection=database[GLOBAL_MIGRATED_MFA_FACTOR_COLLECTION],
            credential_collection=database[PRINCIPAL_CREDENTIAL_COLLECTION],
        )
        receipt = service.migrate(
            principal_id=principal.principal_id,
            credential_revision=principal.credential_revision,
            code=payload.code,
            session=session,
            now=now,
        )
        session.commit_transaction()
        try:
            rate_gate.record_success(email=payload.email, observed_at=now)
        except PrincipalAuthenticationRateLimitUnavailable:
            raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
        return {
            "status": "MFA_FACTOR_MIGRATED",
            "principal_id": receipt.principal_id,
            "credential_revision": receipt.credential_revision,
            "next_step": "SIGN_IN_AGAIN",
        }
    except GlobalPrincipalMfaLegacyMigrationCodeRejected:
        _abort_if_active(session)
        _record_failure(rate_gate, payload.email, source, now)
        raise HTTPException(status_code=401, detail="Invalid authenticator code") from None
    except GlobalPrincipalMfaLegacyMigrationRejected as error:
        _abort_if_active(session)
        status = 409 if str(error) in {
            "GLOBAL_MFA_MIGRATION_LEGACY_FACTOR_NOT_UNIQUE",
            "GLOBAL_MFA_MIGRATION_FACTOR_ALREADY_CURRENT",
            "GLOBAL_MFA_ENROLLMENT_REQUIRED",
        } else 401
        raise HTTPException(status_code=status, detail=str(error)) from None
    except GlobalPrincipalMfaLegacyMigrationUnavailable:
        _abort_if_active(session)
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    except PyMongoError:
        _abort_if_active(session)
        raise HTTPException(status_code=503, detail="GLOBAL_AUTHENTICATION_UNAVAILABLE") from None
    except HTTPException:
        _abort_if_active(session)
        raise
    except Exception:
        _abort_if_active(session)
        raise
    finally:
        session.end_session()


__all__ = ["router"]
