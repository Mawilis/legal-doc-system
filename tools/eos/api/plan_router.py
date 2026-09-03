"""TITLE: WILSY OS Plan HTTP Authority Router.
VERSION: v1.2.0-EXACT-TENANT-REGISTRY-SCOPE
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Binds private Plan catalogue HTTP access to exact current tenant
permission authority before PlanRegistry access.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/plan_router.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi / Wilsy Core Engineering.
CERTIFICATION/UPDATE DATE: 2026-09-03.
CHANGELOG:
    v1.2.0-EXACT-TENANT-REGISTRY-SCOPE opts private list/get/update/archive into
    PlanRegistry exact-tenant scope so tenantless/global catalogue truth
    cannot cross the authenticated private tenant boundary.
    v1.1.2-PLAN-HTTP-RESPONSE-BOUNDARY extends fail-closed evidence handling across the complete
    institutional response-formatting and JSON serialization boundary.
    v1.1.1-PLAN-HTTP-AUTHORITY-HARDENING bounds Plan-not-found responses, contains
    evidence serialization failure as persistence-unavailable, closes
    setup/failure diagnostic edges, and adopts the current HTTP 422
    Starlette status constant.
    v1.1.0-PLAN-HTTP-AUTHORITY replaces raw transport-header forwarding with
    RequirePermission plan:read/plan:manage, membership-admitted tenant scope,
    pre-Registry body-tenant containment, bounded persistence failures, and
    non-leaking private catalogue semantics.
    v1.0.1-FIXED added response_model=None for HTTP 204 archive responses.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No credential, role, permission, tenant, catalogue,
or persistence diagnostics are logged or returned as authority evidence.
TENANT BOUNDARY: Every route derives scope only from SovereignIdentity returned
by RequirePermission after exact ACTIVE membership and role-assignment proof.
Caller tenant fields are never sovereign authority and cannot redirect writes.
AUTHORITY BOUNDARY: This router owns HTTP admission and error translation only.
PlanRegistry owns catalogue persistence; PlanEntity owns commercial value truth.
FINANCIAL AUTHORITY BOUNDARY: Plan management is commercial catalogue authority
only. It cannot approve, release, execute, settle, transfer, collect, or infer
payment. Kennel EOS remains the exclusive financial execution authority.
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

from .responses import format_response
from tools.eos.auth.authorization import (
    RequirePermission,
)
from tools.eos.auth.identity import (
    SovereignIdentity,
)
from tools.eos.saas.billing.plan_registry import (
    PlanRegistry,
)
from tools.eos.saas.domain.plan import (
    PlanTiers,
)


VERSION = "v1.2.0-EXACT-TENANT-REGISTRY-SCOPE"

PLAN_READ_PERMISSION = "plan:read"
PLAN_MANAGE_PERMISSION = "plan:manage"

PLAN_READ_AUTHORITY = RequirePermission(
    PLAN_READ_PERMISSION
)

PLAN_MANAGE_AUTHORITY = RequirePermission(
    PLAN_MANAGE_PERMISSION
)

_CREATE_REQUIRED_FIELDS = (
    "name",
    "price",
    "currency",
    "billingFrequency",
    "planType",
    "idempotencyKey",
)

_TENANT_PAYLOAD_FIELDS = (
    "tenantId",
    "tenant_id",
)

logger = logging.getLogger(
    "WilsyOS.API.PlanRouter"
)

plan_router = APIRouter(
    prefix="/api/plans",
    tags=["Plan Management"],
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
            status_code=
                status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "error":
                    "PLAN_AUTHORITY_UNAVAILABLE"
            },
        )

    return tenant_id


def _tenant_scope_mismatch() -> NoReturn:
    """Reject body-directed cross-tenant scope before Registry access."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error":
                "PLAN_TENANT_SCOPE_MISMATCH"
        },
    )


def _bind_create_tenant(
    payload: dict[str, Any],
    tenant_id: str,
) -> dict[str, Any]:
    """Normalize create payload to the one authorized tenant."""
    safe = dict(payload)

    for field_name in _TENANT_PAYLOAD_FIELDS:
        if (
            field_name in safe
            and safe[field_name] != tenant_id
        ):
            _tenant_scope_mismatch()

    safe.pop(
        "tenant_id",
        None,
    )

    safe["tenantId"] = tenant_id

    return safe


def _strip_update_tenant(
    payload: dict[str, Any],
    tenant_id: str,
) -> dict[str, Any]:
    """Validate tenant aliases then remove tenant ownership from mutation data."""
    safe = dict(payload)

    for field_name in _TENANT_PAYLOAD_FIELDS:
        if (
            field_name in safe
            and safe[field_name] != tenant_id
        ):
            _tenant_scope_mismatch()

    safe.pop(
        "tenantId",
        None,
    )

    safe.pop(
        "tenant_id",
        None,
    )

    return safe


def _validate_create_payload(
    payload: dict[str, Any],
) -> None:
    """Validate only exact HTTP-visible PlanRegistry input vocabulary."""
    for field_name in _CREATE_REQUIRED_FIELDS:
        if field_name not in payload:
            raise HTTPException(
                status_code=
                    status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "error":
                        "MISSING_FIELD",
                    "field":
                        field_name,
                },
            )

    raw_plan_type = payload.get(
        "planType"
    )

    if not isinstance(
        raw_plan_type,
        str,
    ):
        raise HTTPException(
            status_code=
                status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "error":
                    "INVALID_PLAN_TYPE"
            },
        )

    try:
        PlanTiers(
            raw_plan_type.upper()
        )
    except ValueError as error:
        raise HTTPException(
            status_code=
                status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "error":
                    "INVALID_PLAN_TYPE",
                "valid": [
                    item.value
                    for item in PlanTiers
                ],
            },
        ) from error


def _raise_persistence_failure(
    operation: str,
    error: Exception,
) -> NoReturn:
    """Translate unexpected Registry failure without leaking diagnostics."""
    logger.error(
        "[PLAN_PERSISTENCE_FAILURE]"
        " operation=%s type=%s",
        operation,
        type(error).__name__,
    )

    raise HTTPException(
        status_code=
            status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "error":
                "PLAN_PERSISTENCE_UNAVAILABLE"
        },
    ) from error


def _create_conflict(
    error_text: str,
) -> bool:
    """Recognize only observed deterministic catalogue-conflict results."""
    return (
        error_text
        == "Duplicate plan catalogue key"
        or (
            error_text.startswith(
                "Idempotency key '"
            )
            and error_text.endswith(
                "' already exists"
            )
        )
        or (
            error_text.startswith(
                "Plan ID '"
            )
            and error_text.endswith(
                "' already exists"
            )
        )
    )


def _raise_result_failure(
    result: dict[str, Any],
    *,
    operation: str,
) -> NoReturn:
    """Map only explicit known result contracts; unknown results become 503."""
    raw_error = result.get(
        "error"
    )

    error_text = (
        raw_error
        if isinstance(
            raw_error,
            str,
        )
        else ""
    )

    if operation == "CREATE":
        missing_prefix = (
            "Missing required field: "
        )

        if error_text.startswith(
            missing_prefix
        ):
            field_name = error_text[
                len(
                    missing_prefix
                ):
            ]

            if (
                field_name
                in _CREATE_REQUIRED_FIELDS
            ):
                raise HTTPException(
                    status_code=
                        status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail={
                        "error":
                            "MISSING_FIELD",
                        "field":
                            field_name,
                    },
                )

        if error_text.startswith(
            "Invalid planType: "
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "error":
                        "INVALID_PLAN_TYPE"
                },
            )

        if error_text.startswith(
            "Invalid billingFrequency: "
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "error":
                        "INVALID_BILLING_FREQUENCY"
                },
            )

        if _create_conflict(
            error_text
        ):
            raise HTTPException(
                status_code=
                    status.HTTP_409_CONFLICT,
                detail={
                    "error":
                        "PLAN_CATALOGUE_CONFLICT"
                },
            )

    if (
        operation == "UPDATE"
        and error_text
        == "Plan not found"
    ):
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail={
                "error":
                    "PLAN_NOT_FOUND"
            },
        )

    logger.error(
        "[PLAN_REGISTRY_RESULT_FAILURE]"
        " operation=%s",
        operation,
    )

    raise HTTPException(
        status_code=
            status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={
            "error":
                "PLAN_PERSISTENCE_UNAVAILABLE"
        },
    )


@plan_router.get("")
async def list_plans(
    request: Request,
    identity: SovereignIdentity = Depends(
        PLAN_READ_AUTHORITY
    ),
    active: bool | None = Query(
        None,
        description="Filter by active status",
    ),
    plan_type: str | None = Query(
        None,
        description="Filter by canonical Plan tier",
    ),
    page: int = Query(
        1,
        ge=1,
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
    ),
) -> Any:
    """List only catalogue truth inside the current authorized tenant."""
    tenant_id = _authorized_tenant_id(
        identity
    )

    plan_type_enum = None

    if plan_type is not None:
        try:
            plan_type_enum = PlanTiers(
                plan_type.upper()
            )
        except ValueError as error:
            raise HTTPException(
                status_code=
                    status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail={
                    "error":
                        "INVALID_PLAN_TYPE",
                    "valid": [
                        item.value
                        for item in PlanTiers
                    ],
                },
            ) from error

    try:
        result = PlanRegistry.list(
            tenant_id=tenant_id,
            exact_tenant=True,
            active=active,
            plan_type=plan_type_enum,
            page=page,
            limit=limit,
        )
    except Exception as error:
        _raise_persistence_failure(
            "LIST",
            error,
        )

    try:
        response_data = {
            "plans": [
                plan.to_dict()
                for plan
                in result["items"]
            ],
            "total":
                result["total"],
            "page":
                page,
            "limit":
                limit,
            "pages":
                result["pages"],
        }
    except Exception as error:
        _raise_persistence_failure(
            "LIST_EVIDENCE",
            error,
        )

    try:
        return format_response(
            data=response_data,
            message=
                "Plans retrieved successfully.",
            execution_id=getattr(
                request.state,
                "execution_id",
                "PLAN-LIST",
            ),
        )
    except Exception as error:
        _raise_persistence_failure(
            "LIST_RESPONSE",
            error,
        )


@plan_router.get("/{plan_id}")
async def get_plan(
    request: Request,
    plan_id: str = Path(
        ...,
        description="Plan ID",
    ),
    identity: SovereignIdentity = Depends(
        PLAN_READ_AUTHORITY
    ),
) -> Any:
    """Read one Plan only inside current authorized tenant scope."""
    tenant_id = _authorized_tenant_id(
        identity
    )

    try:
        plan = PlanRegistry.get(
            plan_id,
            tenant_id=tenant_id,
            exact_tenant=True,
        )
    except Exception as error:
        _raise_persistence_failure(
            "GET",
            error,
        )

    if plan is None:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail={
                "error":
                    "PLAN_NOT_FOUND"
            },
        )

    try:
        plan_data = (
            plan.to_dict()
        )
    except Exception as error:
        _raise_persistence_failure(
            "GET_EVIDENCE",
            error,
        )

    try:
        return format_response(
            data={
                "plan":
                    plan_data
            },
            message=
                "Plan retrieved successfully.",
            execution_id=getattr(
                request.state,
                "execution_id",
                "PLAN-GET",
            ),
        )
    except Exception as error:
        _raise_persistence_failure(
            "GET_RESPONSE",
            error,
        )


@plan_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
async def create_plan(
    request: Request,
    payload: dict[str, Any] = Body(
        ...,
        description="Plan creation payload",
    ),
    identity: SovereignIdentity = Depends(
        PLAN_MANAGE_AUTHORITY
    ),
) -> Any:
    """Create Plan truth only inside current authorized tenant scope."""
    tenant_id = _authorized_tenant_id(
        identity
    )

    safe_payload = _bind_create_tenant(
        payload,
        tenant_id,
    )

    _validate_create_payload(
        safe_payload
    )

    try:
        result = PlanRegistry.create(
            safe_payload,
            tenant_id=tenant_id,
        )
    except Exception as error:
        _raise_persistence_failure(
            "CREATE",
            error,
        )

    if not result.get(
        "success"
    ):
        _raise_result_failure(
            result,
            operation="CREATE",
        )

    try:
        plan = result["plan"]
        plan_data = (
            plan.to_dict()
        )
    except Exception as error:
        _raise_persistence_failure(
            "CREATE_EVIDENCE",
            error,
        )

    try:
        return format_response(
            data={
                "plan":
                    plan_data
            },
            message=
                "Plan created successfully.",
            execution_id=getattr(
                request.state,
                "execution_id",
                "PLAN-CREATE",
            ),
            status_code=
                status.HTTP_201_CREATED,
        )
    except Exception as error:
        _raise_persistence_failure(
            "CREATE_RESPONSE",
            error,
        )


@plan_router.put("/{plan_id}")
async def update_plan(
    request: Request,
    plan_id: str = Path(
        ...,
        description="Plan ID",
    ),
    payload: dict[str, Any] = Body(
        ...,
        description="Plan update payload",
    ),
    identity: SovereignIdentity = Depends(
        PLAN_MANAGE_AUTHORITY
    ),
) -> Any:
    """Update bounded Plan truth only inside current authorized tenant scope."""
    tenant_id = _authorized_tenant_id(
        identity
    )

    safe_payload = _strip_update_tenant(
        payload,
        tenant_id,
    )

    try:
        result = PlanRegistry.update(
            plan_id,
            safe_payload,
            tenant_id=tenant_id,
            exact_tenant=True,
        )
    except Exception as error:
        _raise_persistence_failure(
            "UPDATE",
            error,
        )

    if not result.get(
        "success"
    ):
        _raise_result_failure(
            result,
            operation="UPDATE",
        )

    try:
        plan = result["plan"]
        plan_data = (
            plan.to_dict()
        )
    except Exception as error:
        _raise_persistence_failure(
            "UPDATE_EVIDENCE",
            error,
        )

    try:
        return format_response(
            data={
                "plan":
                    plan_data
            },
            message=
                "Plan updated successfully.",
            execution_id=getattr(
                request.state,
                "execution_id",
                "PLAN-UPDATE",
            ),
        )
    except Exception as error:
        _raise_persistence_failure(
            "UPDATE_RESPONSE",
            error,
        )


@plan_router.delete(
    "/{plan_id}",
    status_code=
        status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def archive_plan(
    request: Request,
    plan_id: str = Path(
        ...,
        description="Plan ID",
    ),
    identity: SovereignIdentity = Depends(
        PLAN_MANAGE_AUTHORITY
    ),
) -> None:
    """Archive Plan lifecycle truth only after current manage authority."""
    del request

    tenant_id = _authorized_tenant_id(
        identity
    )

    try:
        success = PlanRegistry.archive(
            plan_id,
            tenant_id=tenant_id,
            exact_tenant=True,
        )
    except Exception as error:
        _raise_persistence_failure(
            "ARCHIVE",
            error,
        )

    if not success:
        raise HTTPException(
            status_code=
                status.HTTP_404_NOT_FOUND,
            detail={
                "error":
                    "PLAN_NOT_FOUND"
            },
        )

    return None


__all__ = [
    "VERSION",
    "PLAN_READ_PERMISSION",
    "PLAN_MANAGE_PERMISSION",
    "plan_router",
]


# ARTIFACT: tools/eos/api/plan_router.py
# VERSION: v1.2.0-EXACT-TENANT-REGISTRY-SCOPE
# AUTHORITY BOUNDARY: exact current permission admission plus bounded HTTP translation only
# TENANT POSTURE: membership-admitted identity tenant exclusively scopes private catalogue access
# FAIL-CLOSED POSTURE: raw projections, scope mismatch, unknown Registry failures and evidence outages deny
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains exclusive
# END OF WILSY OS SOVEREIGN ARTIFACT
