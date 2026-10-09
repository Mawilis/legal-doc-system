"""TITLE: WILSY OS Tenant Branding Management HTTP Boundary.
VERSION: v1.1.0-L10-P2C7-D21B-GOVERNED-ASSET-UPLOAD
AUTHORITY: Wilsy OS Core Governance
EPITOME: Exposes authenticated, tenant-derived branding management projections
         and immutable profile/asset commands without moving branding truth into
         the browser or creating commercial, subscription, IAM, or Kennel power.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/tenant_branding_router.py
COLLABORATION / OWNERSHIP: D21B1-D21B8 domains and registries own canonical
                            entitlement, profile, selection, asset, and workspace
                            truth; this module owns HTTP translation and caller-
                            owned Mongo transaction mechanics.
CERTIFICATION / UPDATE DATE: 2026-09-29
CHANGELOG: v1.1.0-L10-P2C7-D21B-GOVERNED-ASSET-UPLOAD adds bounded multipart
           logo/favicon admission and exact D21B5B profile descriptor resolution
           while preserving server-owned tenant, entitlement, and authority fields.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Exact allow-lists, active entitlement revalidation,
                             strict tenant correlation, bounded media bytes,
                             and fail-closed error mapping.
TENANT BOUNDARY: Tenant scope is derived from authenticated SovereignIdentity;
                 caller-supplied tenant selectors are ignored and never become
                 authorization evidence.
AUTHORITY BOUNDARY: HTTP composition only. D21B registries remain canonical;
                    no IAM, subscription, plan, payment, URL, or public asset
                    authority is created.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively owns financial execution.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Final
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse

from tools.eos.api.responses import format_response
from tools.eos.auth.authentication import get_current_identity, get_principal_authority_repository
from tools.eos.auth.authorization import get_role_assignment_repository as get_auth_role_repository
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.auth.tenant_access import get_tenant_membership_repository
from tools.eos.auth.tenant_authorization import (
    TenantAuthorizationReason,
    authorize_tenant_operation,
)
from tools.eos.api.tenant_authorization_http import get_role_assignment_repository as get_tenant_role_repository
from tools.eos.saas.billing import tenant_branding_entitlement_registry as entitlement_registry
from tools.eos.saas.billing import tenant_branding_asset_registry as asset_registry
from tools.eos.saas.billing import tenant_branding_profile_registry as profile_registry
from tools.eos.saas.billing.tenant_branding_vas_policy import (
    TenantBrandingVASPolicyError,
    get_tenant_branding_vas_policy,
)
from tools.eos.saas.domain.tenant_branding_asset import (
    MAX_ASSET_BYTES,
    SAFE_MEDIA_TYPES,
    TenantBrandingAssetError,
    TenantBrandingAssetKind,
    content_fingerprint,
    register_tenant_branding_asset,
)
from tools.eos.saas.domain.tenant_branding_entitlement import TenantBrandingEntitlementState
from tools.eos.saas.domain.tenant_branding_profile import approve_tenant_branding_profile
from tools.eos.saas.domain.tenant_branding_profile_selection import select_tenant_branding_profile
from tools.eos.kernel.db import get_client, get_database


VERSION: Final[str] = "v1.1.0-L10-P2C7-D21B-GOVERNED-ASSET-UPLOAD"
router = APIRouter(prefix="/tenant-branding", tags=["Tenant Branding"])
_READ_PERMISSION = "tenant_branding:read"
_PROFILE_PERMISSION = "tenant_branding:profile:manage"


class BrandingAuthorization:
    """Resolve authenticated own-tenant authority without trusting a selector."""

    def __init__(self, permission_id: str, operation: str, *, allow_denied: bool = False) -> None:
        self.permission_id = permission_id
        self.operation = operation
        self.allow_denied = allow_denied

    async def __call__(
        self,
        identity: SovereignIdentity = Depends(get_current_identity),
        principal_repository: Any = Depends(get_principal_authority_repository),
        membership_repository: Any = Depends(get_tenant_membership_repository),
        business_role_repository: Any = Depends(get_tenant_role_repository),
        role_assignment_repository: Any = Depends(get_auth_role_repository),
    ) -> Any:
        decision = authorize_tenant_operation(
            principal_id=identity.identity_id,
            tenant_id=identity.tenant_id,
            permission_id=self.permission_id,
            operation=self.operation,
            principal_repository=principal_repository,
            membership_repository=membership_repository,
            business_role_repository=business_role_repository,
            role_assignment_repository=role_assignment_repository,
        )
        if decision.authorized and decision.reason is TenantAuthorizationReason.AUTHORIZED:
            return True if self.allow_denied else identity
        unavailable = {
            TenantAuthorizationReason.PRINCIPAL_AUTHORITY_UNAVAILABLE,
            TenantAuthorizationReason.MEMBERSHIP_AUTHORITY_UNAVAILABLE,
            TenantAuthorizationReason.TENANT_BUSINESS_ROLE_AUTHORITY_UNAVAILABLE,
            TenantAuthorizationReason.ROLE_ASSIGNMENT_AUTHORITY_UNAVAILABLE,
        }
        if decision.reason in unavailable:
            raise HTTPException(status_code=503, detail={"code": "TENANT_AUTHORITY_UNAVAILABLE"})
        if self.allow_denied:
            return False
        raise HTTPException(status_code=403, detail={"code": "TENANT_BRANDING_AUTHORIZATION_DENIED"})


def _collection(database: Any, name: str) -> Any:
    if database is None:
        raise RuntimeError("BRANDING_PERSISTENCE_UNAVAILABLE")
    return database.get_collection(name)


def _digest(payload: object) -> str:
    return hashlib.sha3_512(
        json.dumps(payload, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _enum_value(value: object) -> str:
    return str(getattr(value, "value", value))


def _transaction(callback: Any) -> Any:
    client = get_client()
    database = get_database()
    if client is None or database is None:
        raise RuntimeError("BRANDING_PERSISTENCE_UNAVAILABLE")
    with client.start_session() as session:
        session.start_transaction()
        try:
            result = callback(session, database)
            session.commit_transaction()
            return result
        except Exception:
            if bool(getattr(session, "in_transaction", False)):
                session.abort_transaction()
            raise


def _read_transaction(callback: Any) -> Any:
    client = get_client()
    database = get_database()
    if client is None or database is None:
        raise RuntimeError("BRANDING_PERSISTENCE_UNAVAILABLE")
    with client.start_session() as session:
        session.start_transaction()
        try:
            result = callback(session, database)
            session.abort_transaction()
            return result
        except Exception:
            if bool(getattr(session, "in_transaction", False)):
                session.abort_transaction()
            raise


def _current_entitlement(tenant_id: str, database: Any, session: Any) -> Any:
    rows = list(_collection(database, entitlement_registry.CURRENT_COLLECTION).find({"tenant_id": tenant_id}, session=session).limit(2))
    if len(rows) != 1:
        raise entitlement_registry.TenantBrandingEntitlementRegistryNotFoundError("D21B2B_SINGLE_CURRENT_ENTITLEMENT_REQUIRED")
    entitlement_id = rows[0].get("entitlement_id")
    current = entitlement_registry.get_current(
        tenant_id,
        entitlement_id,
        _collection(database, entitlement_registry.HISTORY_COLLECTION),
        _collection(database, entitlement_registry.CURRENT_COLLECTION),
        session=session,
    )
    if current.lifecycle_state is not TenantBrandingEntitlementState.ACTIVE:
        raise entitlement_registry.TenantBrandingEntitlementRegistryNotFoundError("D21B2B_ACTIVE_ENTITLEMENT_REQUIRED")
    return current


def _asset_capability(kind: TenantBrandingAssetKind) -> str:
    """Return the exact D21B1 capability required for one closed asset kind."""
    if kind is TenantBrandingAssetKind.LOGO:
        return "tenant.brand.logo.v1"
    if kind is TenantBrandingAssetKind.FAVICON:
        return "tenant.brand.favicon.v1"
    raise TenantBrandingAssetError("D21B5A_ASSET_KIND_INVALID")


def _resolve_profile_asset(
    *,
    payload: dict[str, Any],
    reference_key: str,
    fingerprint_key: str,
    kind: TenantBrandingAssetKind,
    tenant_id: str,
    database: Any,
    session: Any,
) -> Any:
    """Resolve one client-supplied descriptor through D21B5B in the transaction."""
    reference = payload.get(reference_key)
    fingerprint = payload.get(fingerprint_key)
    if reference is None and fingerprint is None:
        return None
    if not isinstance(reference, str) or not isinstance(fingerprint, str):
        raise HTTPException(status_code=422, detail={"code": "BRANDING_ASSET_DESCRIPTOR_REQUIRED"})
    return asset_registry.resolve(
        tenant_id,
        reference,
        expected_content_fingerprint=fingerprint,
        expected_kind=kind,
        collection=_collection(database, asset_registry.COLLECTION),
        session=session,
    )


def _profile_projection(
    current: Any,
    entitlement: Any,
    *,
    can_manage_profile: bool | None = None,
    can_manage_assets: bool | None = None,
) -> dict[str, Any]:
    profile = current.profile if current is not None else None
    return {
        "entitlement": None if entitlement is None else {
            "entitlementId": entitlement.entitlement_id,
            "brandingTier": _enum_value(entitlement.branding_tier),
            "lifecycleState": _enum_value(entitlement.lifecycle_state),
            "lifecycleRevision": entitlement.lifecycle_revision,
            "fingerprint": entitlement.fingerprint,
        },
        "profile": None if profile is None else {
            "profileId": profile.profile_id,
            "profileLabel": profile.profile_label,
            "profileFingerprint": profile.fingerprint,
            "brandingTier": _enum_value(profile.branding_entitlement.branding_tier),
            "primaryColor": profile.primary_color,
            "secondaryColor": profile.secondary_color,
            "accentColor": profile.accent_color,
            "emailDisplayName": profile.email_display_name,
            "logo": None if profile.logo_asset_reference is None else {"reference": profile.logo_asset_reference, "contentFingerprint": profile.logo_asset_fingerprint, "kind": "LOGO"},
            "favicon": None if profile.favicon_asset_reference is None else {"reference": profile.favicon_asset_reference, "contentFingerprint": profile.favicon_asset_fingerprint, "kind": "FAVICON"},
        },
        "selection": None if current is None else {"selectionId": current.pointer.selection_id, "selectionRevision": current.pointer.selection_revision},
        "capabilities": {
            "canRead": True,
            "canManageProfile": entitlement is not None if can_manage_profile is None else can_manage_profile,
            "canManageAsset": entitlement is not None if can_manage_assets is None else can_manage_assets,
            "canManageAssets": entitlement is not None if can_manage_assets is None else can_manage_assets,
            "trustMarkRequired": True,
        },
    }


def _map_error(error: BaseException) -> HTTPException:
    code = str(getattr(error, "code", "BRANDING_MANAGEMENT_FAILED"))
    if "NOT_FOUND" in code or "MISSING" in code:
        return HTTPException(status_code=404, detail={"code": code})
    if "CONFLICT" in code or "RETRY" in code or "CURRENT" in code:
        return HTTPException(status_code=409, detail={"code": code})
    if "INPUT" in code or "INVALID" in code or "REQUIRED" in code or "ENTITLED" in code:
        return HTTPException(status_code=422, detail={"code": code})
    return HTTPException(status_code=503, detail={"code": code})


async def _json_allowlist(request: Request, allowed: set[str]) -> dict[str, Any]:
    try:
        payload = await request.json()
    except Exception as error:
        raise HTTPException(status_code=422, detail={"code": "BRANDING_JSON_REQUIRED"}) from error
    if not isinstance(payload, dict):
        raise HTTPException(status_code=422, detail={"code": "BRANDING_OBJECT_REQUIRED"})
    unexpected = set(payload) - allowed - {"timestamp"}
    if unexpected:
        raise HTTPException(status_code=422, detail={"code": "BRANDING_FIELD_NOT_ALLOWED", "fields": sorted(unexpected)})
    return {key: payload[key] for key in allowed if key in payload}


@router.get("", dependencies=[Depends(BrandingAuthorization(_READ_PERMISSION, "tenant_branding_read"))])
async def get_tenant_branding(
    identity: SovereignIdentity = Depends(get_current_identity),
    can_manage_profile: bool = Depends(BrandingAuthorization(_PROFILE_PERMISSION, "tenant_branding_profile_manage", allow_denied=True)),
    can_manage_assets: bool = Depends(BrandingAuthorization("tenant_branding:asset:manage", "tenant_branding_asset_manage", allow_denied=True)),
) -> JSONResponse:
    """Return fresh own-tenant D21B2/D21B4 browser-safe branding truth."""
    try:
        def read(session: Any, database: Any) -> dict[str, Any]:
            entitlement = _current_entitlement(identity.tenant_id, database, session)
            try:
                current = profile_registry.get_current(
                    identity.tenant_id,
                    _collection(database, profile_registry.PROFILE_COLLECTION),
                    _collection(database, profile_registry.SELECTION_COLLECTION),
                    _collection(database, profile_registry.CURRENT_COLLECTION),
                    session=session,
                )
            except profile_registry.TenantBrandingProfileRegistryCurrentPointerMissingError:
                current = None
            return _profile_projection(
                current,
                entitlement,
                can_manage_profile=can_manage_profile,
                can_manage_assets=can_manage_assets,
            )
        return format_response(_read_transaction(read), message="Tenant branding authority loaded.")
    except HTTPException:
        raise
    except Exception as error:
        raise _map_error(error) from error


@router.post("/profiles")
async def create_tenant_branding_profile(
    request: Request,
    identity: SovereignIdentity = Depends(BrandingAuthorization(_PROFILE_PERMISSION, "tenant_branding_profile_manage")),
) -> JSONResponse:
    """Approve one immutable profile and select it only when no current exists."""
    payload = await _json_allowlist(
        request,
        {
            "profile_label",
            "primary_color",
            "secondary_color",
            "accent_color",
            "email_display_name",
            "logo_asset_reference",
            "logo_asset_fingerprint",
            "favicon_asset_reference",
            "favicon_asset_fingerprint",
        },
    )
    label = payload.get("profile_label")
    if not isinstance(label, str) or not label.strip():
        raise HTTPException(status_code=422, detail={"code": "BRANDING_PROFILE_LABEL_REQUIRED"})
    try:
        def write(session: Any, database: Any) -> dict[str, Any]:
            entitlement = _current_entitlement(identity.tenant_id, database, session)
            logo = _resolve_profile_asset(
                payload=payload,
                reference_key="logo_asset_reference",
                fingerprint_key="logo_asset_fingerprint",
                kind=TenantBrandingAssetKind.LOGO,
                tenant_id=identity.tenant_id,
                database=database,
                session=session,
            )
            favicon = _resolve_profile_asset(
                payload=payload,
                reference_key="favicon_asset_reference",
                fingerprint_key="favicon_asset_fingerprint",
                kind=TenantBrandingAssetKind.FAVICON,
                tenant_id=identity.tenant_id,
                database=database,
                session=session,
            )
            profile_id = f"brand-profile-{uuid4().hex}"
            evidence = {"tenant_id": identity.tenant_id, "profile_id": profile_id, "fields": {key: payload.get(key) for key in sorted(payload)}}
            profile = approve_tenant_branding_profile(
                entitlement=entitlement,
                profile_id=profile_id,
                profile_label=label.strip(),
                source_evidence_reference=f"entitlement:{entitlement.entitlement_id}",
                source_evidence_fingerprint=entitlement.fingerprint,
                approved_at=_now(),
                approval_evidence_reference=f"http:tenant-branding-profile:{profile_id}",
                approval_evidence_fingerprint=_digest(evidence),
                **{key: payload[key] for key in ("primary_color", "secondary_color", "accent_color", "email_display_name") if key in payload},
                logo_asset_reference=None if logo is None else logo.asset.asset_reference,
                logo_asset_fingerprint=None if logo is None else logo.asset.content_fingerprint,
                favicon_asset_reference=None if favicon is None else favicon.asset.asset_reference,
                favicon_asset_fingerprint=None if favicon is None else favicon.asset.content_fingerprint,
            )
            persisted = profile_registry.persist_profile(profile, _collection(database, profile_registry.PROFILE_COLLECTION), session=session)
            try:
                profile_registry.get_current(identity.tenant_id, _collection(database, profile_registry.PROFILE_COLLECTION), _collection(database, profile_registry.SELECTION_COLLECTION), _collection(database, profile_registry.CURRENT_COLLECTION), session=session)
                selected = None
            except profile_registry.TenantBrandingProfileRegistryCurrentPointerMissingError:
                selection_id = f"brand-selection-{uuid4().hex}"
                selection = select_tenant_branding_profile(profile=persisted, current_entitlement=entitlement, selection_id=selection_id, selection_revision=1, selected_at=_now(), selection_evidence_reference=f"http:tenant-branding-selection:{selection_id}", selection_evidence_fingerprint=_digest({"tenant_id": identity.tenant_id, "selection_id": selection_id, "profile_fingerprint": persisted.fingerprint}))
                selected = profile_registry.persist_selection_and_advance_current(selection, _collection(database, profile_registry.PROFILE_COLLECTION), _collection(database, profile_registry.SELECTION_COLLECTION), _collection(database, profile_registry.CURRENT_COLLECTION), session=session)
            return {"profileId": persisted.profile_id, "profileFingerprint": persisted.fingerprint, "selected": selected is not None}
        return format_response(_transaction(write), status_code=201, message="Tenant branding profile approved.")
    except HTTPException:
        raise
    except Exception as error:
        raise _map_error(error) from error


@router.post("/assets/{kind}")
async def upload_tenant_branding_asset(
    kind: str,
    file: UploadFile = File(...),
    identity: SovereignIdentity = Depends(BrandingAuthorization("tenant_branding:asset:manage", "tenant_branding_asset_manage")),
) -> JSONResponse:
    """Admit one bounded immutable logo/favicon through D21B5B."""
    try:
        try:
            asset_kind = TenantBrandingAssetKind(kind.upper())
        except (TypeError, ValueError) as error:
            raise HTTPException(status_code=422, detail={"code": "D21B5A_ASSET_KIND_INVALID"}) from error
        media_type = (file.content_type or "").split(";", 1)[0].strip().lower()
        if media_type not in SAFE_MEDIA_TYPES:
            raise HTTPException(status_code=422, detail={"code": "D21B5A_MEDIA_TYPE_UNSUPPORTED"})
        content = await file.read(MAX_ASSET_BYTES + 1)
        if not isinstance(content, bytes) or not content or len(content) > MAX_ASSET_BYTES:
            raise HTTPException(status_code=422, detail={"code": "D21B5A_CONTENT_LENGTH_INVALID"})
        digest = content_fingerprint(content)
        asset_reference = f"asset:{identity.tenant_id}:{asset_kind.value.lower()}:{uuid4().hex}"
        source_reference = f"http:tenant-branding-asset-upload:{asset_reference}"
        source_fingerprint = _digest(
            {
                "tenant_id": identity.tenant_id,
                "asset_reference": asset_reference,
                "asset_kind": asset_kind.value,
                "media_type": media_type,
                "content_length": len(content),
                "content_fingerprint": digest,
            }
        )

        def write(session: Any, database: Any) -> dict[str, Any]:
            entitlement = _current_entitlement(identity.tenant_id, database, session)
            policy = get_tenant_branding_vas_policy(entitlement.branding_tier)
            if not policy.permits(_asset_capability(asset_kind)):
                raise HTTPException(status_code=422, detail={"code": "D21B5A_ASSET_NOT_ENTITLED"})
            asset = register_tenant_branding_asset(
                tenant_id=identity.tenant_id,
                asset_reference=asset_reference,
                asset_kind=asset_kind,
                media_type=media_type,
                content=content,
                source_evidence_reference=source_reference,
                source_evidence_fingerprint=source_fingerprint,
                registered_at=_now(),
            )
            resolved = asset_registry.create_or_replay(
                asset,
                content,
                _collection(database, asset_registry.COLLECTION),
                session=session,
            )
            return {
                "reference": resolved.asset.asset_reference,
                "contentFingerprint": resolved.asset.content_fingerprint,
                "mediaType": resolved.asset.media_type,
                "kind": getattr(resolved.asset.asset_kind, "value", resolved.asset.asset_kind),
                "contentLength": resolved.asset.content_length,
            }

        return format_response(_transaction(write), status_code=201, message="Tenant branding asset admitted.")
    except (TenantBrandingAssetError, TenantBrandingVASPolicyError) as error:
        raise HTTPException(status_code=422, detail={"code": str(error)}) from error
    except HTTPException:
        raise
    except Exception as error:
        raise _map_error(error) from error


@router.post("/profiles/{profile_id}/select")
async def select_tenant_branding_profile_route(
    profile_id: str,
    identity: SovereignIdentity = Depends(BrandingAuthorization(_PROFILE_PERMISSION, "tenant_branding_profile_manage")),
) -> JSONResponse:
    """Advance the immutable tenant current-profile pointer server-side."""
    try:
        def write(session: Any, database: Any) -> dict[str, Any]:
            entitlement = _current_entitlement(identity.tenant_id, database, session)
            profile = profile_registry.get_profile(identity.tenant_id, profile_id, _collection(database, profile_registry.PROFILE_COLLECTION), session=session)
            try:
                current = profile_registry.get_current(identity.tenant_id, _collection(database, profile_registry.PROFILE_COLLECTION), _collection(database, profile_registry.SELECTION_COLLECTION), _collection(database, profile_registry.CURRENT_COLLECTION), session=session)
                prior = current.selection
                revision = prior.selection_revision + 1
            except profile_registry.TenantBrandingProfileRegistryCurrentPointerMissingError:
                prior = None
                revision = 1
            selection_id = f"brand-selection-{uuid4().hex}"
            selection = select_tenant_branding_profile(profile=profile, current_entitlement=entitlement, selection_id=selection_id, selection_revision=revision, selected_at=_now(), selection_evidence_reference=f"http:tenant-branding-selection:{selection_id}", selection_evidence_fingerprint=_digest({"tenant_id": identity.tenant_id, "selection_id": selection_id, "profile_id": profile.profile_id}), prior_selection=prior)
            result = profile_registry.persist_selection_and_advance_current(selection, _collection(database, profile_registry.PROFILE_COLLECTION), _collection(database, profile_registry.SELECTION_COLLECTION), _collection(database, profile_registry.CURRENT_COLLECTION), session=session)
            return {"selectionId": result.current.selection.selection_id, "selectionRevision": result.current.selection.selection_revision, "profileId": result.current.selection.profile_id}
        return format_response(_transaction(write), message="Tenant branding profile selected.")
    except Exception as error:
        raise _map_error(error) from error


__all__ = ["VERSION", "router"]

# ARTIFACT: tenant_branding_router.py
# VERSION: v1.1.0-L10-P2C7-D21B-GOVERNED-ASSET-UPLOAD
# AUTHORITY BOUNDARY: authenticated tenant-branding HTTP composition only
# TENANT POSTURE: tenant derives from SovereignIdentity; caller selectors are not authority
# FAIL-CLOSED POSTURE: authorization, entitlement, profile, selection and asset failures deny or unavailable
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
