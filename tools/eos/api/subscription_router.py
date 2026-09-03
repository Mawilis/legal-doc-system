"""TITLE: WILSY OS Subscription HTTP Authority Router.
VERSION: v1.1.2-CURRENT-SUBSCRIPTION-AUTHORITY
AUTHORITY: FastAPI composition of current Python identity, tenant membership,
permission and SubscriptionRegistry authorities.
EPITOME: Retires direct X-Tenant-ID-to-registry forwarding. Every subscription
HTTP operation first resolves current authenticated identity, exact ACTIVE
tenant membership and current ACTIVE role assignment granting the required
canonical subscription permission.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/subscription_router.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-03.
CHANGELOG:
    v1.1.2-CURRENT-SUBSCRIPTION-AUTHORITY closes FastAPI dependency-source collision by renaming only
    the metrics route's internal tenant path parameter; external URL semantics
    are unchanged and the canonical get_current_tenant_identity X-Tenant-ID
    header dependency remains untouched.
    v1.1.1-CURRENT-SUBSCRIPTION-AUTHORITY closes the bounded registry-result typing defect by admitting
    only string business error codes into HTTP status mapping; non-string or
    absent error metadata remains an unknown bounded client failure.
    v1.1.0-CURRENT-SUBSCRIPTION-AUTHORITY removes raw tenant-header registry
    authority; introduces canonical subscription:read/subscription:manage
    permission dependencies; forwards only the tenant admitted by Python
    membership authority; bounds persistence errors; preserves all existing
    subscription HTTP lifecycle routes.
    v1.0.3-ALIGNED forwarded tenant_id_header directly from X-Tenant-ID.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: Transport claims never grant access. Registry
diagnostics and repository internals are not reflected to clients. Persistence
unavailability is explicit and bounded.
TENANT BOUNDARY: X-Tenant-ID remains request context only and is consumed by
get_current_tenant_identity inside RequirePermission. Only its membership-
validated SovereignIdentity.tenant_id may reach SubscriptionRegistry.
AUTHORITY BOUNDARY: Owns HTTP composition only. Authentication, membership,
role assignments, permission policy and subscription persistence retain their
existing canonical owners.
FINANCIAL AUTHORITY BOUNDARY: Subscription state is commercial lifecycle truth,
not payment authorization, release, execution or settlement. Kennel EOS remains
the exclusive financial execution authority.
"""

from __future__ import annotations

import logging
from typing import Any, NoReturn

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    Path,
    Query,
    Request,
    status,
)

from tools.eos.auth.authorization import RequirePermission
from tools.eos.auth.identity import SovereignIdentity
from tools.eos.saas.billing.subscription_registry import (
    SubscriptionRegistry,
    SubscriptionRegistryError,
)
from tools.eos.saas.domain.subscription import SubscriptionStatus

from .responses import format_response


VERSION = "v1.1.2-CURRENT-SUBSCRIPTION-AUTHORITY"

SUBSCRIPTION_READ_PERMISSION = "subscription:read"
SUBSCRIPTION_MANAGE_PERMISSION = "subscription:manage"

SUBSCRIPTION_READ_AUTHORITY = RequirePermission(
    SUBSCRIPTION_READ_PERMISSION
)
SUBSCRIPTION_MANAGE_AUTHORITY = RequirePermission(
    SUBSCRIPTION_MANAGE_PERMISSION
)

logger = logging.getLogger(
    "WilsyOS.API.SubscriptionRouter"
)

subscription_router = APIRouter(
    prefix="/api/subscriptions",
    tags=["Subscription Management"],
)


def _authorized_tenant_id(
    identity: SovereignIdentity,
) -> str:
    """Return only membership-admitted tenant scope or fail closed."""
    tenant_id = identity.tenant_id

    if (
        not isinstance(tenant_id, str)
        or not tenant_id
        or tenant_id != tenant_id.strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error":
                    "SUBSCRIPTION_AUTHORITY_UNAVAILABLE"
            },
        )

    return tenant_id


def _raise_registry_failure(
    error: SubscriptionRegistryError,
) -> NoReturn:
    """Translate persistence authority failure without leaking diagnostics."""
    logger.error(
        "[SUBSCRIPTION_REGISTRY_FAILURE] %s",
        type(error).__name__,
    )

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "error":
                "SUBSCRIPTION_PERSISTENCE_UNAVAILABLE"
        },
    ) from error


def _raise_unexpected(
    operation: str,
    error: Exception,
) -> NoReturn:
    """Translate unexpected router failure into bounded HTTP evidence."""
    logger.error(
        "[SUBSCRIPTION_ROUTER_%s_FAILURE] %s",
        operation,
        type(error).__name__,
    )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error":
                "SUBSCRIPTION_OPERATION_FAILED"
        },
    ) from error


def _raise_result_failure(
    result: dict[str, Any],
    *,
    default_error: str,
) -> NoReturn:
    """Translate bounded registry business failures without raw diagnostics."""
    raw_value = result.get("error")
    raw = (
        raw_value
        if isinstance(raw_value, str)
        else ""
    )

    mapping: dict[str, tuple[int, str]] = {
        "Subscription not found": (
            status.HTTP_404_NOT_FOUND,
            "SUBSCRIPTION_NOT_FOUND",
        ),
        "SUBSCRIPTION_TENANT_SCOPE_MISMATCH": (
            status.HTTP_403_FORBIDDEN,
            "SUBSCRIPTION_TENANT_SCOPE_MISMATCH",
        ),
        "SUBSCRIPTION_IDEMPOTENCY_CONFLICT": (
            status.HTTP_409_CONFLICT,
            "SUBSCRIPTION_IDEMPOTENCY_CONFLICT",
        ),
        "SUBSCRIPTION_ID_COLLISION": (
            status.HTTP_409_CONFLICT,
            "SUBSCRIPTION_ID_COLLISION",
        ),
    }

    status_code, error_code = mapping.get(
        raw,
        (
            status.HTTP_400_BAD_REQUEST,
            default_error,
        ),
    )

    raise HTTPException(
        status_code=status_code,
        detail={"error": error_code},
    )


def _response(
    request: Request,
    *,
    data: dict[str, Any],
    message: str,
    execution_id: str,
    status_code: int | None = None,
) -> Any:
    """Return the existing bounded response envelope."""
    kwargs: dict[str, Any] = {
        "data": data,
        "message": message,
        "execution_id": getattr(
            request.state,
            "execution_id",
            execution_id,
        ),
    }

    if status_code is not None:
        kwargs["status_code"] = status_code

    return format_response(**kwargs)


@subscription_router.get("")
async def list_subscriptions(
    request: Request,
    identity: SovereignIdentity = Depends(
        SUBSCRIPTION_READ_AUTHORITY
    ),
    filter_status: str | None = Query(
        None,
        description=(
            "Filter by status "
            "(active, trial, paused, cancelled, expired)"
        ),
    ),
    plan: str | None = Query(
        None,
        description="Filter by plan tier",
    ),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> Any:
    """List subscriptions only inside membership-authorized tenant scope."""
    tenant_id = _authorized_tenant_id(
        identity
    )

    status_enum = None

    if filter_status is not None:
        try:
            status_enum = SubscriptionStatus(
                filter_status.lower()
            )
        except ValueError as error:
            raise HTTPException(
                status_code=
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "INVALID_STATUS",
                    "valid": [
                        item.value
                        for item
                        in SubscriptionStatus
                    ],
                },
            ) from error

    try:
        result = SubscriptionRegistry.list(
            tenant_id_header=tenant_id,
            status=status_enum,
            plan=plan,
            page=page,
            limit=limit,
        )
    except SubscriptionRegistryError as error:
        _raise_registry_failure(error)
    except Exception as error:
        _raise_unexpected("LIST", error)

    return _response(
        request,
        data={
            "subscriptions": [
                item.to_dict()
                for item in result["items"]
            ],
            "total": result["total"],
            "page": page,
            "limit": limit,
            "pages": result["pages"],
        },
        message="Subscriptions retrieved successfully.",
        execution_id="SUB-LIST",
    )


@subscription_router.get("/{subscription_id}")
async def get_subscription(
    request: Request,
    subscription_id: str = Path(
        ...,
        description="Subscription ID",
    ),
    identity: SovereignIdentity = Depends(
        SUBSCRIPTION_READ_AUTHORITY
    ),
) -> Any:
    """Read one subscription only inside authorized tenant scope."""
    tenant_id = _authorized_tenant_id(
        identity
    )

    try:
        subscription = SubscriptionRegistry.get(
            subscription_id,
            tenant_id_header=tenant_id,
        )
    except SubscriptionRegistryError as error:
        _raise_registry_failure(error)
    except Exception as error:
        _raise_unexpected("GET", error)

    if subscription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "SUBSCRIPTION_NOT_FOUND",
                "subscription_id":
                    subscription_id,
            },
        )

    return _response(
        request,
        data={
            "subscription":
                subscription.to_dict()
        },
        message="Subscription retrieved successfully.",
        execution_id="SUB-GET",
    )


@subscription_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_subscription(
    request: Request,
    payload: dict[str, Any] = Body(
        ...,
        description="Subscription creation payload",
    ),
    identity: SovereignIdentity = Depends(
        SUBSCRIPTION_MANAGE_AUTHORITY
    ),
) -> Any:
    """Create subscription truth only for the authorized tenant."""
    tenant_id = _authorized_tenant_id(
        identity
    )

    required = (
        "tenantId",
        "planId",
        "plan",
        "amount",
        "currency",
        "billingFrequency",
        "startDate",
        "idempotencyKey",
    )

    for field_name in required:
        if field_name not in payload:
            raise HTTPException(
                status_code=
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "MISSING_FIELD",
                    "field": field_name,
                },
            )

    try:
        result = SubscriptionRegistry.create(
            payload,
            tenant_id_header=tenant_id,
        )
    except SubscriptionRegistryError as error:
        _raise_registry_failure(error)
    except Exception as error:
        _raise_unexpected("CREATE", error)

    if not result.get("success"):
        _raise_result_failure(
            result,
            default_error=
                "SUBSCRIPTION_CREATE_FAILED",
        )

    subscription = result["subscription"]

    return _response(
        request,
        data={
            "subscription":
                subscription.to_dict()
        },
        message="Subscription created successfully.",
        execution_id="SUB-CREATE",
        status_code=status.HTTP_201_CREATED,
    )


@subscription_router.put("/{subscription_id}")
async def update_subscription(
    request: Request,
    subscription_id: str = Path(
        ...,
        description="Subscription ID",
    ),
    payload: dict[str, Any] = Body(
        ...,
        description="Update fields",
    ),
    identity: SovereignIdentity = Depends(
        SUBSCRIPTION_MANAGE_AUTHORITY
    ),
) -> Any:
    """Update bounded commercial fields after current manage authority."""
    tenant_id = _authorized_tenant_id(
        identity
    )

    try:
        result = SubscriptionRegistry.update(
            subscription_id,
            payload,
            tenant_id_header=tenant_id,
        )
    except SubscriptionRegistryError as error:
        _raise_registry_failure(error)
    except Exception as error:
        _raise_unexpected("UPDATE", error)

    if not result.get("success"):
        _raise_result_failure(
            result,
            default_error=
                "SUBSCRIPTION_UPDATE_FAILED",
        )

    return _response(
        request,
        data={
            "subscription":
                result["subscription"].to_dict()
        },
        message="Subscription updated successfully.",
        execution_id="SUB-UPDATE",
    )


@subscription_router.delete(
    "/{subscription_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def archive_subscription(
    request: Request,
    subscription_id: str = Path(
        ...,
        description="Subscription ID",
    ),
    identity: SovereignIdentity = Depends(
        SUBSCRIPTION_MANAGE_AUTHORITY
    ),
) -> None:
    """Archive subscription lifecycle truth after manage authorization."""
    del request

    tenant_id = _authorized_tenant_id(
        identity
    )

    try:
        success = SubscriptionRegistry.archive(
            subscription_id,
            tenant_id_header=tenant_id,
        )
    except SubscriptionRegistryError as error:
        _raise_registry_failure(error)
    except Exception as error:
        _raise_unexpected("ARCHIVE", error)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "SUBSCRIPTION_NOT_FOUND",
                "subscription_id":
                    subscription_id,
            },
        )

    return None


@subscription_router.post("/{subscription_id}/pause")
async def pause_subscription(
    request: Request,
    subscription_id: str = Path(...),
    payload: dict[str, Any] = Body(...),
    identity: SovereignIdentity = Depends(
        SUBSCRIPTION_MANAGE_AUTHORITY
    ),
) -> Any:
    """Pause subscription only after current manage authorization."""
    tenant_id = _authorized_tenant_id(identity)

    try:
        result = SubscriptionRegistry.pause(
            subscription_id,
            tenant_id_header=tenant_id,
            pause_reason=payload.get(
                "pauseReason"
            ),
            pause_until=payload.get(
                "pauseUntil"
            ),
        )
    except SubscriptionRegistryError as error:
        _raise_registry_failure(error)
    except Exception as error:
        _raise_unexpected("PAUSE", error)

    if not result.get("success"):
        _raise_result_failure(
            result,
            default_error="PAUSE_FAILED",
        )

    return _response(
        request,
        data={
            "subscription":
                result["subscription"].to_dict()
        },
        message="Subscription paused successfully.",
        execution_id="SUB-PAUSE",
    )


@subscription_router.post("/{subscription_id}/resume")
async def resume_subscription(
    request: Request,
    subscription_id: str = Path(...),
    payload: dict[str, Any] = Body(...),
    identity: SovereignIdentity = Depends(
        SUBSCRIPTION_MANAGE_AUTHORITY
    ),
) -> Any:
    """Resume subscription only after current manage authorization."""
    tenant_id = _authorized_tenant_id(identity)

    try:
        result = SubscriptionRegistry.resume(
            subscription_id,
            tenant_id_header=tenant_id,
            metadata=payload.get(
                "metadata",
                {},
            ),
        )
    except SubscriptionRegistryError as error:
        _raise_registry_failure(error)
    except Exception as error:
        _raise_unexpected("RESUME", error)

    if not result.get("success"):
        _raise_result_failure(
            result,
            default_error="RESUME_FAILED",
        )

    return _response(
        request,
        data={
            "subscription":
                result["subscription"].to_dict()
        },
        message="Subscription resumed successfully.",
        execution_id="SUB-RESUME",
    )


@subscription_router.post("/{subscription_id}/cancel")
async def cancel_subscription(
    request: Request,
    subscription_id: str = Path(...),
    payload: dict[str, Any] = Body(...),
    identity: SovereignIdentity = Depends(
        SUBSCRIPTION_MANAGE_AUTHORITY
    ),
) -> Any:
    """Cancel subscription without creating financial execution truth."""
    tenant_id = _authorized_tenant_id(identity)

    try:
        result = SubscriptionRegistry.cancel(
            subscription_id,
            tenant_id_header=tenant_id,
            cancel_reason=payload.get(
                "cancelReason"
            ),
            cancel_at_period_end=payload.get(
                "cancelAtPeriodEnd",
                True,
            ),
        )
    except SubscriptionRegistryError as error:
        _raise_registry_failure(error)
    except Exception as error:
        _raise_unexpected("CANCEL", error)

    if not result.get("success"):
        _raise_result_failure(
            result,
            default_error="CANCEL_FAILED",
        )

    return _response(
        request,
        data={
            "subscription":
                result["subscription"].to_dict()
        },
        message="Subscription cancelled successfully.",
        execution_id="SUB-CANCEL",
    )


@subscription_router.post("/{subscription_id}/upgrade")
async def upgrade_subscription(
    request: Request,
    subscription_id: str = Path(...),
    payload: dict[str, Any] = Body(...),
    identity: SovereignIdentity = Depends(
        SUBSCRIPTION_MANAGE_AUTHORITY
    ),
) -> Any:
    """Upgrade subscription commercial truth after manage authorization."""
    tenant_id = _authorized_tenant_id(identity)

    try:
        result = SubscriptionRegistry.upgrade(
            subscription_id,
            tenant_id_header=tenant_id,
            upgrade_data=payload,
        )
    except SubscriptionRegistryError as error:
        _raise_registry_failure(error)
    except Exception as error:
        _raise_unexpected("UPGRADE", error)

    if not result.get("success"):
        _raise_result_failure(
            result,
            default_error="UPGRADE_FAILED",
        )

    return _response(
        request,
        data={
            "subscription":
                result["subscription"].to_dict()
        },
        message="Subscription upgraded successfully.",
        execution_id="SUB-UPGRADE",
    )


@subscription_router.post("/{subscription_id}/downgrade")
async def downgrade_subscription(
    request: Request,
    subscription_id: str = Path(...),
    payload: dict[str, Any] = Body(...),
    identity: SovereignIdentity = Depends(
        SUBSCRIPTION_MANAGE_AUTHORITY
    ),
) -> Any:
    """Downgrade subscription commercial truth after manage authorization."""
    tenant_id = _authorized_tenant_id(identity)

    try:
        result = SubscriptionRegistry.downgrade(
            subscription_id,
            tenant_id_header=tenant_id,
            downgrade_data=payload,
        )
    except SubscriptionRegistryError as error:
        _raise_registry_failure(error)
    except Exception as error:
        _raise_unexpected("DOWNGRADE", error)

    if not result.get("success"):
        _raise_result_failure(
            result,
            default_error="DOWNGRADE_FAILED",
        )

    return _response(
        request,
        data={
            "subscription":
                result["subscription"].to_dict()
        },
        message="Subscription downgraded successfully.",
        execution_id="SUB-DOWNGRADE",
    )


@subscription_router.post("/{subscription_id}/reactivate")
async def reactivate_subscription(
    request: Request,
    subscription_id: str = Path(...),
    payload: dict[str, Any] = Body(...),
    identity: SovereignIdentity = Depends(
        SUBSCRIPTION_MANAGE_AUTHORITY
    ),
) -> Any:
    """Reactivate cancelled subscription after current manage authority."""
    tenant_id = _authorized_tenant_id(identity)

    try:
        result = SubscriptionRegistry.reactivate(
            subscription_id,
            tenant_id_header=tenant_id,
            metadata=payload.get(
                "metadata",
                {},
            ),
        )
    except SubscriptionRegistryError as error:
        _raise_registry_failure(error)
    except Exception as error:
        _raise_unexpected(
            "REACTIVATE",
            error,
        )

    if not result.get("success"):
        _raise_result_failure(
            result,
            default_error="REACTIVATE_FAILED",
        )

    return _response(
        request,
        data={
            "subscription":
                result["subscription"].to_dict()
        },
        message="Subscription reactivated successfully.",
        execution_id="SUB-REACTIVATE",
    )


@subscription_router.get("/{subscription_id}/audit")
async def get_subscription_audit(
    request: Request,
    subscription_id: str = Path(...),
    identity: SovereignIdentity = Depends(
        SUBSCRIPTION_READ_AUTHORITY
    ),
) -> Any:
    """Read subscription audit evidence only after current read authority."""
    tenant_id = _authorized_tenant_id(identity)

    try:
        audit = SubscriptionRegistry.get_audit(
            subscription_id,
            tenant_id_header=tenant_id,
        )
    except SubscriptionRegistryError as error:
        _raise_registry_failure(error)
    except Exception as error:
        _raise_unexpected("AUDIT", error)

    if audit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "SUBSCRIPTION_NOT_FOUND"
            },
        )

    return _response(
        request,
        data={"audit": audit},
        message="Subscription audit retrieved successfully.",
        execution_id="SUB-AUDIT",
    )


@subscription_router.get("/metrics/{requested_tenant_id}")
async def get_subscription_metrics(
    request: Request,
    requested_tenant_id: str = Path(
        ...,
        description="Tenant ID",
    ),
    identity: SovereignIdentity = Depends(
        SUBSCRIPTION_READ_AUTHORITY
    ),
) -> Any:
    """Read metrics only when path tenant equals membership-admitted tenant."""
    authorized_tenant = _authorized_tenant_id(
        identity
    )

    if requested_tenant_id != authorized_tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error":
                    "SUBSCRIPTION_TENANT_SCOPE_MISMATCH"
            },
        )

    try:
        metrics = SubscriptionRegistry.get_metrics(
            authorized_tenant
        )
    except SubscriptionRegistryError as error:
        _raise_registry_failure(error)
    except Exception as error:
        _raise_unexpected("METRICS", error)

    return _response(
        request,
        data={"metrics": metrics},
        message="Subscription metrics retrieved successfully.",
        execution_id="SUB-METRICS",
    )


__all__ = [
    "VERSION",
    "SUBSCRIPTION_READ_PERMISSION",
    "SUBSCRIPTION_MANAGE_PERMISSION",
    "subscription_router",
]

# ARTIFACT: tools/eos/api/subscription_router.py
# VERSION: v1.1.2-CURRENT-SUBSCRIPTION-AUTHORITY
# AUTHORITY BOUNDARY: HTTP composition only; identity, membership, role assignment, permission policy and persistence retain canonical ownership
# TENANT POSTURE: only membership-admitted SovereignIdentity.tenant_id reaches SubscriptionRegistry; raw X-Tenant-ID is never registry authority
# FAIL-CLOSED POSTURE: missing or invalid identity, membership, role, permission or persistence authority never becomes subscription access
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively
# END OF WILSY OS SOVEREIGN ARTIFACT
