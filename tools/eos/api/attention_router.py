"""TITLE: WILSY OS Daily Attention Authenticated HTTP Read Surface
VERSION: v1.0.0-EOS-SOURCE-AUTHORISED-FEED
AUTHORITY: WILSY OS Core Governance; canonical source EOS service authority.
EPITOME: Serve cursor-bounded attention feeds, counts, source coverage and
         deadline calendar from the existing independently authorised My Work.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/api/attention_router.py
COLLABORATION / OWNERSHIP: unified_my_work_router.read_my_work authorizes
         source reads and tenant/principal admission; attention_feed_projection
         normalizes read-only items; no second source/task registry is created.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: v1.0.0-EOS-SOURCE-AUTHORISED-FEED establishes GET /attention/feed,
           /attention/counts, /attention/calendar, /attention/sources/health.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No unauthorised partial queue, no credentials or
         work bodies in logs, no source actions offered as executable HTTP.
TENANT BOUNDARY: Every endpoint depends on revalidated canonical read_my_work
         including current bearer, tenant header and module/record authority.
AUTHORITY BOUNDARY: Source services exclusively own task/approval commands;
         these GET endpoints cannot create, alter or acknowledge work.
TRANSACTION / IDEMPOTENCY BOUNDARY: All reads use source-owned transactions;
         no cross-source transaction or durable idempotency is claimed.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes finances.
FAIL-CLOSED POSTURE: Unauthorized, malformed or unavailable source rejects;
         no false successful zero-queue, no partial source health inference.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from tools.eos.api.unified_my_work_router import read_my_work
from tools.eos.workspaces.service.attention_feed_projection import (
    AttentionFeedError,
    build_attention_feed,
)

router = APIRouter(prefix="/attention", tags=["Daily Attention"])


def _project(
    source: dict[str, Any], *, view: str = "active",
    sources: str | None = None, q: str = "",
    cursor: str | None = None, limit: int = 50,
) -> dict[str, Any]:
    """Validate requested scope and adapt one freshly authorised read.

    Source services own transactions and all business command authorization.
    An explicitly chosen unknown/denied module rejects without disclosing
    whether that module exists for another tenant.
    """
    chosen = tuple(v.strip().upper() for v in sources.split(",")) if sources else ()
    if any(not v for v in chosen):
        raise HTTPException(status_code=422, detail="ATTENTION_SOURCE_FILTER_INVALID")
    try:
        return build_attention_feed(
            source, view=view, sources=chosen, query=q,
            cursor=cursor, limit=limit,
        )
    except AttentionFeedError as error:
        if error.code == "ATTENTION_SOURCE_NOT_AUTHORIZED":
            raise HTTPException(status_code=403, detail="ATTENTION_SOURCE_NOT_AUTHORIZED") from error
        if error.code in {
            "ATTENTION_FILTER_INVALID", "ATTENTION_PAGE_LIMIT_INVALID",
            "ATTENTION_CURSOR_INVALID",
        }:
            raise HTTPException(status_code=422, detail=error.code) from error
        raise HTTPException(status_code=503, detail=error.code) from error


@router.get("/feed")
async def attention_feed(
    source: dict[str, Any] = Depends(read_my_work),
    view: Literal["active", "overdue", "due_today", "high_priority"] = "active",
    sources: str | None = Query(default=None, max_length=200),
    q: str = Query(default="", max_length=200),
    cursor: str | None = Query(default=None, max_length=256),
    limit: int = Query(default=50, ge=1, le=100),
) -> dict[str, Any]:
    """Read the bounded queue; the dependency rechecks EOS bearer and tenant."""
    return _project(source, view=view, sources=sources, q=q,
                    cursor=cursor, limit=limit)


@router.get("/counts")
async def attention_counts(
    source: dict[str, Any] = Depends(read_my_work),
    sources: str | None = Query(default=None, max_length=200),
) -> dict[str, Any]:
    """Return checked-source counts; no cached or invented enterprise totals."""
    result = _project(source, sources=sources, limit=1)
    return {
        "schema": result["schema"],
        "tenantId": result["tenantId"],
        "principalId": result["principalId"],
        "syncedAt": result["syncedAt"],
        "counts": result["counts"],
        "coverage": result["coverage"],
    }


@router.get("/calendar")
async def attention_calendar(
    source: dict[str, Any] = Depends(read_my_work),
    from_at: datetime = Query(alias="from"),
    to_at: datetime = Query(alias="to"),
    sources: str | None = Query(default=None, max_length=200),
) -> dict[str, Any]:
    """Return due work inside caller's period from the same authorized feed.

    Date bounds are aware and limited to 31 days. No meeting integration or
    cross-module calendar event is inferred from an absent source adapter.
    """
    if (
        from_at.tzinfo is None or to_at.tzinfo is None
        or from_at >= to_at
        or (to_at - from_at).total_seconds() > 31 * 86400
    ):
        raise HTTPException(status_code=422, detail="ATTENTION_CALENDAR_RANGE_INVALID")
    # Read the complete authorised snapshot through bounded pages; no
    # alternate unfiltered data authority is introduced.
    snapshot = _project(source, sources=sources, limit=100)
    items = list(snapshot["items"])
    cursor = snapshot["nextCursor"]
    while cursor is not None:
        page = _project(source, sources=sources, cursor=cursor, limit=100)
        items.extend(page["items"])
        cursor = page["nextCursor"]
    due_items = [
        item for item in items
        if item["dueAt"] is not None
        and from_at <= datetime.fromisoformat(item["dueAt"]) < to_at
    ]
    return {
        "schema": snapshot["schema"],
        "tenantId": snapshot["tenantId"],
        "principalId": snapshot["principalId"],
        "syncedAt": snapshot["syncedAt"],
        "items": due_items,
        "coverage": snapshot["coverage"],
        "sourceReadTransactions": "INDEPENDENT_OWNER_BOUNDARIES",
    }


@router.get("/sources/health")
async def attention_source_health(
    source: dict[str, Any] = Depends(read_my_work),
) -> dict[str, Any]:
    """Expose admitted-source read evidence, not unverified module readiness.

    An unavailable source read fails through the dependency instead of being
    silently labelled empty, healthy or absent.
    """
    snapshot = _project(source, limit=1)
    return {
        "schema": snapshot["schema"],
        "tenantId": snapshot["tenantId"],
        "principalId": snapshot["principalId"],
        "syncedAt": snapshot["syncedAt"],
        "sources": snapshot["sources"],
        "coverage": snapshot["coverage"],
    }


__all__ = ["router", "attention_feed", "attention_counts",
           "attention_calendar", "attention_source_health"]

# ARTIFACT: tools/eos/api/attention_router.py
# VERSION: v1.0.0-EOS-SOURCE-AUTHORISED-FEED
# AUTHORITY BOUNDARY: Authenticated source-owned reads; no attention commands.
# TENANT POSTURE: Exact tenant/principal read_my_work dependency each request.
# FAIL-CLOSED POSTURE: No inferred health, entitlement, access or cleared queue.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
