"""
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No credentials or personal information exposed by this metadata repair.
TENANT BOUNDARY: Exact tenant scope, membership and entitlements remain server-governed.
AUTHORITY BOUNDARY: No new IAM, admission, session or business execution authority is created.
FINANCIAL AUTHORITY BOUNDARY: No financial execution; Kennel EOS remains exclusive.
TITLE: WILSY OS Authenticated Unified My Work Source Aggregation
VERSION: v1.6.0-CRM-CORE-OPTIONAL-SOURCE
AUTHORITY: WILSY OS Python EOS; canonical source registries own business truth.
EPITOME: Compose only independently authenticated and entitled module work in
         exact tenant scope, fan out independent source-owned reads without
         serial latency, and expose safe per-source timing only when the
         dedicated My Work diagnostic switch is explicitly enabled.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/unified_my_work_router.py
COLLABORATION / OWNERSHIP: TenantAuthorizationHTTP owns current IAM;
         Legal Operations, CRM, tenant module and HR source services own reads,
         index assurance, transactions and durable state; projection owns shape.
CERTIFICATION / UPDATE DATE: 2026-11-17
CHANGELOG: v1.6.0-CRM-CORE-OPTIONAL-SOURCE treats explicitly verified
           absence of tenant CRM Core entitlement as an omitted optional CRM
           source, preserving independently entitled Operations, Intelligence,
           Legal and HR work. CRM entitlement outages and all other source
           errors continue to fail closed; no phantom work is displayed.
CHANGELOG: v1.5.0-TRACE-CORRELATED-TIMING adds the existing request's
           validated diagnostic trace reference to opt-in, privacy-safe source,
           projection, and route timing; it does not change source reads.
           v1.3.0-SCOPED-SAFE-SOURCE-TIMING uses only
           v1.4.0-HR-SOURCE-OWNED-ACTIONS admits headcount and offer read and
           action capabilities independently, then consumes only their internal
           non-sensitive, source-owned action projections. It creates no HR
           permission, candidate visibility, employee lifecycle task or command.
           v1.3.0-SCOPED-SAFE-SOURCE-TIMING uses only
           WILSY_MY_WORK_TIMING=1 for source timing so the broader model-debug
           flag cannot activate unrelated diagnostic logging. Per-source timing
           and Mongo transport classification remain PII-free.
           v1.2.0-BOUNDED-PARALLEL-SOURCE-READS executes only admitted,
           independent source read transactions concurrently and awaits every
           source result before response. Existing source index assurance,
           snapshot transactions, exact IAM, tenant isolation, fail-closed
           errors and source-owned authority remain unchanged.
           v1.1.0-NONBLOCKING-SOURCE-READ-TRANSACTIONS moved synchronous Mongo
           reads to the request threadpool without blocking ASGI.
           v1.0.0 composed independent module work.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Timing diagnostics contain no tokens, tenant IDs,
         principal IDs, personal data, work bodies, URI or Mongo error message.
TENANT BOUNDARY: Exact authenticated principal, tenant and independently
         admitted source IAM are required for every read.
AUTHORITY BOUNDARY: Read-only aggregator; no work creation, approval or grants.
TRANSACTION / IDEMPOTENCY BOUNDARY: Each source retains its own index assurance
         and caller-owned source transaction; no cross-source transaction,
         global snapshot or write authority is introduced.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes finances.
FAIL-CLOSED POSTURE: Any admitted source outage or malformed projection rejects
         the aggregate; no outage becomes fabricated empty or cleared work.
"""
from __future__ import annotations

import asyncio
import logging
import os
import re
import ssl
import time
from collections.abc import Callable, Iterable, Mapping
from datetime import datetime, timezone
from typing import Any, cast

from fastapi import APIRouter, Depends, Header, HTTPException
from pymongo.errors import ConnectionFailure, PyMongoError
from starlette.concurrency import run_in_threadpool

from tools.eos.api.tenant_authorization_http import (
    OptionalTenantAuthorization,
    TenantAuthorizationContext,
)
from tools.eos.auth.authentication import (
    current_request_timing_correlation,
    get_current_identity,
)
from tools.eos.workspaces.service.unified_my_work_projection import (
    UnifiedMyWorkProjectionError,
    build_unified_my_work,
)

from tools.eos.api import legal_operations_router as legal_source
from tools.eos.api import headcount_requisition_router as headcount_source
from tools.eos.api import hiring_lifecycle_router as hiring_source
from tools.eos.api import owner_commercial_workspace_router as crm_source
from tools.eos.api import tenant_module_workspace_router as module_source

router = APIRouter(prefix="/my-work", tags=["My Work"])
logger = logging.getLogger("WilsyOS.API.UnifiedMyWork")

_LEGAL_READ = OptionalTenantAuthorization(
    "legal_operations:productive_work:read", "legal_productive_work_read"
)
_OPERATIONS_READ = OptionalTenantAuthorization(
    "operations:work_item:read", "operations_work_item_read"
)
_INTELLIGENCE_READ = OptionalTenantAuthorization(
    "intelligence:work_item:read", "intelligence_work_item_read"
)
_CRM_READ = OptionalTenantAuthorization("crm:work_item:read", "crm_work_item_read")
_HEADCOUNT_READ = OptionalTenantAuthorization(
    "hr:headcount_requisition:read", "hr_headcount_requisition_read",
    platform_employer_permission_id="platform_employer:headcount_requisition:read",
    platform_employer_operation="platform_employer_headcount_requisition_read",
)
_HEADCOUNT_SUBMIT = OptionalTenantAuthorization(
    "hr:headcount_requisition:create", "hr_headcount_requisition_create",
    platform_employer_permission_id="platform_employer:headcount_requisition:create",
    platform_employer_operation="platform_employer_headcount_requisition_create",
)
_HEADCOUNT_DECIDE = OptionalTenantAuthorization(
    "hr:headcount_requisition:decide", "hr_headcount_requisition_decide",
    platform_employer_permission_id="platform_employer:headcount_requisition:decide",
    platform_employer_operation="platform_employer_headcount_requisition_decide",
)
_OFFER_READ = OptionalTenantAuthorization(
    "hr:hiring_offer:read", "hr_hiring_offer_read",
    platform_employer_permission_id="platform_employer:hiring_offer:read",
    platform_employer_operation="platform_employer_hiring_offer_read",
)
_OFFER_SUBMIT = OptionalTenantAuthorization(
    "hr:hiring_offer:submit", "hr_hiring_offer_submit",
    platform_employer_permission_id="platform_employer:hiring_offer:submit",
    platform_employer_operation="platform_employer_hiring_offer_submit",
)
_OFFER_DECIDE = OptionalTenantAuthorization(
    "hr:hiring_offer:decide", "hr_hiring_offer_decide",
    platform_employer_permission_id="platform_employer:hiring_offer:decide",
    platform_employer_operation="platform_employer_hiring_offer_decide",
)
_OFFER_SEND = OptionalTenantAuthorization(
    "hr:hiring_offer:send", "hr_hiring_offer_send",
    platform_employer_permission_id="platform_employer:hiring_offer:send",
    platform_employer_operation="platform_employer_hiring_offer_send",
)

_TRANSPORT_FAILURE_TYPES = (
    ConnectionFailure,
    ssl.SSLError,
    TimeoutError,
    ConnectionError,
    OSError,
)


def _diagnostics_enabled() -> bool:
    """Return whether scoped, safe My Work timing was explicitly enabled."""
    return os.getenv("WILSY_MY_WORK_TIMING", "").strip() == "1"


def _exception_chain(error: BaseException) -> Iterable[BaseException]:
    """Yield a bounded cause/context chain for transport failure classification."""
    pending = [error]
    visited: set[int] = set()
    while pending and len(visited) < 16:
        current = pending.pop()
        if id(current) in visited:
            continue
        visited.add(id(current))
        yield current
        cause = current.__cause__
        context = current.__context__
        if cause is not None:
            pending.append(cause)
        if context is not None:
            pending.append(context)


def _failure_classification(error: BaseException) -> str:
    """Classify transport, driver, HTTP and application failures without data."""
    chain = tuple(_exception_chain(error))
    if any(isinstance(item, _TRANSPORT_FAILURE_TYPES) for item in chain):
        return "MONGO_TRANSPORT_FAILURE"
    if any(isinstance(item, PyMongoError) for item in chain):
        return "MONGO_DRIVER_FAILURE"
    if isinstance(error, HTTPException):
        return "SOURCE_HTTP_FAILURE"
    return "APPLICATION_FAILURE"


def _safe_error_type(error: BaseException) -> str:
    """Return only a bounded exception class identifier for structured logs."""
    name = type(error).__name__
    return name if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]{0,79}", name) else "UNKNOWN"


def _timed_source_read(source: str, reader: Callable[[], Any]) -> Any:
    """Run one source read and emit privacy-safe timing when diagnostics are on.

    The measured interval includes the source adapter's existing index
    assurance, transaction start/read/commit, and source projection. The source
    transaction and all authorization decisions remain owned by that adapter.
    """
    started_ns = time.perf_counter_ns()
    outcome = "OK"
    error: BaseException | None = None
    try:
        result = reader()
        if result is None:
            outcome = "OMITTED_NOT_ENTITLED"
        return result
    except Exception as caught:
        error = caught
        outcome = _failure_classification(caught)
        logger.error(
            "MY_WORK_SOURCE_FAILURE source=%s outcome=%s error_type=%s",
            source,
            outcome,
            _safe_error_type(caught),
        )
        raise
    finally:
        if _diagnostics_enabled():
            duration_ms = (time.perf_counter_ns() - started_ns) / 1_000_000
            logger.info(
                "MY_WORK_SOURCE_TIMING trace_id=%s source=%s outcome=%s duration_ms=%.3f error_type=%s",
                current_request_timing_correlation(),
                source,
                outcome,
                duration_ms,
                _safe_error_type(error) if error is not None else "NONE",
            )


def _assert_context(
    context: TenantAuthorizationContext | None,
    *,
    tenant_id: str,
    principal_id: str,
) -> None:
    if context is not None and (
        context.tenant_id != tenant_id
        or context.identity.identity_id != principal_id
    ):
        raise HTTPException(status_code=503, detail="MY_WORK_AUTHORIZATION_CONTEXT_INCONSISTENT")


def _read_legal(*, tenant_id: str, principal_id: str) -> dict[str, Any]:
    def read(session: Any, database: Any) -> Any:
        return legal_source._productive_work_service(database).project(
            tenant_id=tenant_id,
            principal_id=principal_id,
            as_of=datetime.now(timezone.utc),
            session=session,
        )

    projection = legal_source._productive_work_projection_transaction(read)
    payload = legal_source._productive_work_payload(projection)
    return {
        "tenant_id": tenant_id,
        "assigned_work_items": payload["assigned_work_items"],
        "supervised_work_items": payload["supervised_work_items"],
    }


def _read_module(slug: str, *, tenant_id: str) -> dict[str, Any] | None:
    product_id, workspace_key, collection_name, _operation_prefix = (
        module_source._PRODUCTS[slug]
    )

    def read(service: Any, session: Any) -> dict[str, Any]:
        readback = service.read_workspace(
            tenant_id=tenant_id,
            now=datetime.now(timezone.utc),
            session=session,
        )
        return {
            "tenant_id": tenant_id,
            "product_id": product_id.value,
            "workspace_key": workspace_key,
            **readback,
            "items": list(readback["items"]),
        }

    try:
        return module_source._transaction(product_id, collection_name, read)
    except HTTPException as error:
        if error.status_code == 403 and error.detail == "MODULE_WORK_PRODUCT_NOT_ENTITLED":
            return None
        raise


def _read_crm(*, tenant_id: str) -> dict[str, Any] | None:
    def read(service: Any, session: Any) -> dict[str, Any]:
        queue = service.daily_queue(
            tenant_id=tenant_id,
            now=datetime.now(timezone.utc),
            session=session,
        )
        return {"tenant_id": tenant_id, "items": list(queue)}

    try:
        return crm_source._transaction(read)
    except HTTPException as error:
        if error.status_code == 403 and error.detail == "OWNER_WORK_CRM_NOT_ENTITLED":
            return None
        raise


def _read_hr(
    *,
    tenant_id: str,
    principal_id: str,
    headcount_read: TenantAuthorizationContext | None,
    headcount_submit: TenantAuthorizationContext | None,
    headcount_decide: TenantAuthorizationContext | None,
    offer_read: TenantAuthorizationContext | None,
    offer_submit: TenantAuthorizationContext | None,
    offer_decide: TenantAuthorizationContext | None,
    offer_send: TenantAuthorizationContext | None,
) -> dict[str, Any] | None:
    """Read only safe HR action projections after independent IAM admission.

    The aggregate does not query HR collections. Each owning router runs its
    own snapshot transaction and returns only opaque action identities and
    lifecycle labels. A granted action permission without the corresponding
    read permission is intentionally ignored; a denied source is omitted, and
    an admitted source with no actionable records remains verified-empty.
    """
    items: list[dict[str, Any]] = []
    admitted = False
    if headcount_read is not None:
        admitted = True
        headcount = headcount_source._project_my_work(
            tenant_id=tenant_id,
            principal_id=principal_id,
            may_submit=headcount_submit is not None,
            may_decide=headcount_decide is not None,
        )
        items.extend(_safe_hr_items(headcount, tenant_id=tenant_id))
    if offer_read is not None:
        admitted = True
        offers = hiring_source._project_my_work(
            tenant_id=tenant_id,
            principal_id=principal_id,
            may_submit=offer_submit is not None,
            may_decide=offer_decide is not None,
            may_send=offer_send is not None,
            now=datetime.now(timezone.utc),
        )
        items.extend(_safe_hr_items(offers, tenant_id=tenant_id))
    return {"tenant_id": tenant_id, "items": items} if admitted else None


def _safe_hr_items(
    payload: Mapping[str, object],
    *,
    tenant_id: str,
) -> list[dict[str, Any]]:
    """Validate the internal HR source envelope before aggregate composition.

    HR owners already construct this envelope inside their snapshot reads, but
    the aggregate retains a fail-closed boundary so a malformed source owner
    cannot become a partial queue, a synthetic empty result, or an unchecked
    type escape. Item semantics remain validated again by the shared projection.
    """
    if payload.get("tenant_id") != tenant_id:
        raise HTTPException(status_code=503, detail="MY_WORK_HR_SOURCE_SCOPE_INVALID")
    raw_items = payload.get("items")
    if (
        not isinstance(raw_items, list)
        or not all(isinstance(item, dict) for item in raw_items)
    ):
        raise HTTPException(status_code=503, detail="MY_WORK_HR_SOURCE_INVALID")
    return cast(list[dict[str, Any]], raw_items)


def _build_result(
    *,
    tenant_id: str,
    principal_id: str,
    legal: dict[str, Any] | None,
    operations: dict[str, Any] | None,
    intelligence: dict[str, Any] | None,
    crm: dict[str, Any] | None,
    hr: dict[str, Any] | None,
) -> dict[str, Any]:
    """Validate and compose completed independent source snapshots."""
    started_ns = time.perf_counter_ns()
    outcome = "OK"
    try:
        result = build_unified_my_work(
            tenant_id=tenant_id,
            principal_id=principal_id,
            now=datetime.now(timezone.utc),
            legal=legal,
            operations=operations,
            intelligence=intelligence,
            crm=crm,
            hr=hr,
        )
    except UnifiedMyWorkProjectionError as error:
        outcome = "INVALID_SOURCE_PROJECTION"
        logger.error("MY_WORK_PROJECTION_FAILURE outcome=%s", outcome)
        raise HTTPException(
            status_code=503,
            detail="MY_WORK_SOURCE_PROJECTION_INVALID",
        ) from error
    finally:
        if _diagnostics_enabled():
            logger.info(
                "MY_WORK_PROJECTION_TIMING trace_id=%s outcome=%s duration_ms=%.3f",
                current_request_timing_correlation(),
                outcome,
                (time.perf_counter_ns() - started_ns) / 1_000_000,
            )

    result["sources_included"] = [
        source for source, payload in (
            ("LEGAL", legal),
            ("OPERATIONS", operations),
            ("INTELLIGENCE", intelligence),
            ("CRM", crm),
            ("HR", hr),
        ) if payload is not None
    ]
    result["authority"]["permits_source_commands"] = False
    result["authority"]["source_read_transactions"] = "INDEPENDENT_OWNER_BOUNDARIES"
    return result


@router.get("")
async def read_my_work(
    tenant_id: str | None = Header(default=None, alias="X-Tenant-ID"),
    identity: Any = Depends(get_current_identity),
    legal_context: TenantAuthorizationContext | None = Depends(_LEGAL_READ),
    operations_context: TenantAuthorizationContext | None = Depends(_OPERATIONS_READ),
    intelligence_context: TenantAuthorizationContext | None = Depends(_INTELLIGENCE_READ),
    crm_context: TenantAuthorizationContext | None = Depends(_CRM_READ),
    headcount_read_context: TenantAuthorizationContext | None = Depends(_HEADCOUNT_READ),
    headcount_submit_context: TenantAuthorizationContext | None = Depends(_HEADCOUNT_SUBMIT),
    headcount_decide_context: TenantAuthorizationContext | None = Depends(_HEADCOUNT_DECIDE),
    offer_read_context: TenantAuthorizationContext | None = Depends(_OFFER_READ),
    offer_submit_context: TenantAuthorizationContext | None = Depends(_OFFER_SUBMIT),
    offer_decide_context: TenantAuthorizationContext | None = Depends(_OFFER_DECIDE),
    offer_send_context: TenantAuthorizationContext | None = Depends(_OFFER_SEND),
) -> dict[str, Any]:
    """Return an exact-scope aggregate from separately admitted source reads.

    Source snapshots stay independent: concurrent execution adds no global
    transaction or cross-source atomicity claim. The route awaits all admitted
    reads and fails closed if any one source fails. No work or IAM is mutated.
    """
    request_started_ns = time.perf_counter_ns()
    if not isinstance(tenant_id, str) or not tenant_id or tenant_id != tenant_id.strip():
        raise HTTPException(status_code=403, detail="TENANT_SCOPE_REQUIRED")

    principal_id = identity.identity_id
    contexts = (
        legal_context,
        operations_context,
        intelligence_context,
        crm_context,
        headcount_read_context,
        headcount_submit_context,
        headcount_decide_context,
        offer_read_context,
        offer_submit_context,
        offer_decide_context,
        offer_send_context,
    )
    for context in contexts:
        _assert_context(context, tenant_id=tenant_id, principal_id=principal_id)

    # A partial source set is valid, but a tenant scope with no independently
    # authorized source is not a workspace. Foreign tenant identifiers never
    # produce a successful empty view.
    if not any(context is not None for context in contexts):
        raise HTTPException(status_code=403, detail="MY_WORK_NO_AUTHORIZED_SOURCE")

    # Each admitted source keeps its own transaction and IAM context. Running
    # those independent read-only transactions concurrently removes the serial
    # sum of their network and index-assurance latency. return_exceptions=True
    # makes gather await every source before the route chooses the first error
    # in canonical source order; no late source read is abandoned after failure.
    source_reads: list[tuple[str, Callable[[], Any]]] = []
    if legal_context is not None:
        source_reads.append((
            "LEGAL",
            lambda: _read_legal(tenant_id=tenant_id, principal_id=principal_id),
        ))
    if operations_context is not None:
        source_reads.append((
            "OPERATIONS",
            lambda: _read_module("operations", tenant_id=tenant_id),
        ))
    if intelligence_context is not None:
        source_reads.append((
            "INTELLIGENCE",
            lambda: _read_module("intelligence", tenant_id=tenant_id),
        ))
    if crm_context is not None:
        source_reads.append(("CRM", lambda: _read_crm(tenant_id=tenant_id)))
    if headcount_read_context is not None or offer_read_context is not None:
        source_reads.append((
            "HR",
            lambda: _read_hr(
                tenant_id=tenant_id,
                principal_id=principal_id,
                headcount_read=headcount_read_context,
                headcount_submit=headcount_submit_context,
                headcount_decide=headcount_decide_context,
                offer_read=offer_read_context,
                offer_submit=offer_submit_context,
                offer_decide=offer_decide_context,
                offer_send=offer_send_context,
            ),
        ))

    source_results = await asyncio.gather(
        *(
            run_in_threadpool(_timed_source_read, source, reader)
            for source, reader in source_reads
        ),
        return_exceptions=True,
    )
    payloads: dict[str, dict[str, Any] | None] = {
        "LEGAL": None,
        "OPERATIONS": None,
        "INTELLIGENCE": None,
        "CRM": None,
        "HR": None,
    }
    first_error: BaseException | None = None
    for (source, _reader), result in zip(source_reads, source_results):
        if isinstance(result, BaseException):
            if first_error is None:
                first_error = result
        else:
            payloads[source] = result
    if first_error is not None:
        if _diagnostics_enabled():
            logger.info(
                "MY_WORK_REQUEST_TIMING trace_id=%s outcome=SOURCE_FAILURE duration_ms=%.3f admitted_sources=%d",
                current_request_timing_correlation(),
                (time.perf_counter_ns() - request_started_ns) / 1_000_000,
                len(source_reads),
            )
        raise first_error

    result = await run_in_threadpool(
        _build_result,
        tenant_id=tenant_id,
        principal_id=principal_id,
        legal=payloads["LEGAL"],
        operations=payloads["OPERATIONS"],
        intelligence=payloads["INTELLIGENCE"],
        crm=payloads["CRM"],
        hr=payloads["HR"],
    )
    if _diagnostics_enabled():
        logger.info(
            "MY_WORK_REQUEST_TIMING trace_id=%s outcome=OK duration_ms=%.3f admitted_sources=%d",
            current_request_timing_correlation(),
            (time.perf_counter_ns() - request_started_ns) / 1_000_000,
            len(source_reads),
        )
    return result


__all__ = ["router", "read_my_work"]


# ARTIFACT: tools/eos/api/unified_my_work_router.py
# VERSION: v1.6.0-CRM-CORE-OPTIONAL-SOURCE
# AUTHORITY BOUNDARY: Authenticated source reads only; no commands.
# TENANT POSTURE: Exact IAM source admission required.
# FAIL-CLOSED POSTURE: Any admitted source failure rejects the aggregate.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
