"""TITLE: WILSY OS Authorised Daily Attention Feed Projection
VERSION: v1.0.0-AUTHORISED-ATTENTION-ITEMS
AUTHORITY: WILSY OS Core Governance; source EOS registries remain canonical.
EPITOME: Present independently authorized My Work rows as deterministic,
         cursor-paginated attention obligations without inventing commands.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/workspaces/service/attention_feed_projection.py
COLLABORATION / OWNERSHIP: unified_my_work_router admits each source and owns
         its source transaction; attention_router exposes read-only HTTP;
         the browser presents only validated, bounded attention projections.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: v1.0.0-AUTHORISED-ATTENTION-ITEMS establishes the first
           AttentionItem contract, deterministic due/priority triage,
           session-bound cursor, source-coverage truth and calendar readback.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Minimal list metadata, no disclosure of confidential
         source detail, no credentials, no locally durable queue or PII logging.
TENANT BOUNDARY: Validated exact-tenant/principal My Work projection; cursor
         binds tenant, principal, timestamp, filters and source identities.
AUTHORITY BOUNDARY: Source entitlements and record visibility are checked by
         the existing independently authorized EOS source readers. READ ONLY.
TRANSACTION / IDEMPOTENCY BOUNDARY: No persistence, actions, audit or new
         transactions; callers own real source service transaction boundaries.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS alone owns financial execution.
FAIL-CLOSED POSTURE: Invalid source, foreign scope, malformed row or cursor
         rejects the entire feed; no invented emptiness or synthetic authority.
"""
from __future__ import annotations

import base64
import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Mapping

SCHEMA = "WILSY-OS-ATTENTION-FEED/V1"
SOURCE_ORDER = ("LEGAL", "OPERATIONS", "INTELLIGENCE", "CRM")
PRIORITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "NORMAL": 2, "LOW": 3}
VIEWS = frozenset({"active", "overdue", "due_today", "high_priority"})
MAX_PAGE = 100


class AttentionFeedError(ValueError):
    """Stable read-projection rejection; no tenant or work-item detail is disclosed."""

    def __init__(self, code: str) -> None:
        """Create one stable error code without logging the rejected payload."""
        self.code = code
        super().__init__(code)


def _instant(value: object) -> datetime:
    if not isinstance(value, str):
        raise AttentionFeedError("ATTENTION_TIMESTAMP_INVALID")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise AttentionFeedError("ATTENTION_TIMESTAMP_INVALID") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise AttentionFeedError("ATTENTION_TIMESTAMP_INVALID")
    return parsed.astimezone(timezone.utc)


def _cursor_fingerprint(
    *, tenant_id: str, principal_id: str, as_of: str, view: str,
    sources: tuple[str, ...], query: str,
) -> str:
    """Bind an offset to the reverified EOS session and selected read surface."""
    payload = json.dumps(
        [tenant_id, principal_id, as_of, view, sources, query],
        ensure_ascii=True, separators=(",", ":"),
    )
    return hashlib.sha3_512(payload.encode("utf-8")).hexdigest()[:32]


def _decode_cursor(value: str | None, fingerprint: str) -> int:
    if value is None:
        return 0
    if not isinstance(value, str) or len(value) > 256:
        raise AttentionFeedError("ATTENTION_CURSOR_INVALID")
    try:
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        decoded = json.loads(raw)
    except (ValueError, TypeError, UnicodeError) as error:
        raise AttentionFeedError("ATTENTION_CURSOR_INVALID") from error
    if (
        not isinstance(decoded, list) or len(decoded) != 2
        or type(decoded[0]) is not int or decoded[0] < 0
        or decoded[0] > 1000000 or decoded[1] != fingerprint
    ):
        raise AttentionFeedError("ATTENTION_CURSOR_INVALID")
    return decoded[0]


def _encode_cursor(offset: int, fingerprint: str) -> str:
    raw = json.dumps([offset, fingerprint], separators=(",", ":"))
    return base64.urlsafe_b64encode(raw.encode("ascii")).decode("ascii").rstrip("=")


def build_attention_feed(
    projection: Mapping[str, Any], *, view: str = "active",
    sources: tuple[str, ...] = (), query: str = "",
    cursor: str | None = None, limit: int = 50,
) -> dict[str, Any]:
    """Transform one already-authorized EOS aggregate to a read-only feed.

    The caller MUST obtain projection through read_my_work with the current
    authenticated bearer and exact X-Tenant-ID. No client-chosen identity or
    entitlement enters this function. Source services retain all reads,
    transactions, audit, completion, assignment and financial commands.
    Cursor is not an authentication token; revalidation occurs on every call.
    """
    if (
        not isinstance(projection, Mapping)
        or projection.get("schema") != "WILSY-OS-UNIFIED-MY-WORK/V1"
        or not isinstance(projection.get("tenant_id"), str)
        or not projection["tenant_id"]
        or not isinstance(projection.get("principal_id"), str)
        or not projection["principal_id"]
        or not isinstance(projection.get("items"), list)
        or not isinstance(projection.get("summary"), Mapping)
        or not isinstance(projection.get("sources_included"), list)
    ):
        raise AttentionFeedError("ATTENTION_SOURCE_PROJECTION_INVALID")
    if view not in VIEWS or not isinstance(query, str) or len(query) > 200:
        raise AttentionFeedError("ATTENTION_FILTER_INVALID")
    if type(limit) is not int or not 1 <= limit <= MAX_PAGE:
        raise AttentionFeedError("ATTENTION_PAGE_LIMIT_INVALID")
    as_of = _instant(projection.get("as_of"))
    admitted = tuple(projection["sources_included"])
    if len(set(admitted)) != len(admitted) or any(
        type(s) is not str or s not in SOURCE_ORDER for s in admitted
    ):
        raise AttentionFeedError("ATTENTION_SOURCE_COVERAGE_INVALID")
    if len(set(sources)) != len(sources) or any(s not in admitted for s in sources):
        raise AttentionFeedError("ATTENTION_SOURCE_NOT_AUTHORIZED")
    source_counts = projection["summary"].get("source_counts")
    if not isinstance(source_counts, Mapping) or set(source_counts) != set(admitted):
        raise AttentionFeedError("ATTENTION_SOURCE_COVERAGE_INVALID")
    rows = projection["items"]
    if (
        type(projection["summary"].get("active_count")) is not int
        or projection["summary"]["active_count"] != len(rows)
        or type(projection["summary"].get("overdue_count")) is not int
    ):
        raise AttentionFeedError("ATTENTION_SOURCE_PROJECTION_INVALID")
    counts_by_source = {source: 0 for source in admitted}
    checked: set[str] = set()
    normalized = []
    overdue = 0
    for row in rows:
        if not isinstance(row, Mapping):
            raise AttentionFeedError("ATTENTION_ITEM_INVALID")
        source = row.get("source")
        source_id = row.get("work_item_id")
        identity = row.get("source_key")
        priority = row.get("priority")
        title = row.get("title")
        if (
            source not in admitted or type(source_id) is not str or not source_id
            or identity != f"{source}:{source_id}" or identity in checked
            or priority not in PRIORITY_ORDER
            or type(title) is not str or not title.strip()
            or type(row.get("is_overdue")) is not bool
            or row.get("action_authority") != "SOURCE_SERVICE_ONLY"
            or (
                "tenant_id" in row
                and row["tenant_id"] != projection["tenant_id"]
            )
        ):
            raise AttentionFeedError("ATTENTION_ITEM_INVALID")
        checked.add(identity)
        counts_by_source[source] += 1
        due = _instant(row["due_at"]) if row.get("due_at") is not None else None
        is_overdue = due is not None and due < as_of
        if row["is_overdue"] != is_overdue:
            raise AttentionFeedError("ATTENTION_ITEM_INVALID")
        overdue += int(is_overdue)
        # Ranking is deterministic *rules*, not AI inference or SLA evidence.
        # SLA/assignee/action authority not present in sources remains null.
        days = (due - as_of).total_seconds() / 86400 if due is not None else None
        score = 80 if is_overdue else 0
        score += (35, 25, 10, 0)[PRIORITY_ORDER[priority]]
        if days is not None and days >= 0:
            score += 30 if days <= 1 else 15 if days <= 3 else 0
        score = min(100, score)
        normalized.append({
            "id": identity,
            "tenantId": projection["tenant_id"],
            "sourceModule": source,
            "sourceType": str(row.get("kind") or "TASK"),
            "sourceRecordId": source_id,
            "title": title,
            "summary": str(row.get("description") or "")[:240],
            "priority": priority,
            "urgencyScore": score,
            "whyRanked": (
                "Overdue source deadline" if is_overdue else
                "High source priority" if priority in {"CRITICAL", "HIGH"} else
                "Due within 24 hours" if days is not None and 0 <= days <= 1 else
                "Authorised active work"
            ),
            "dueAt": due.isoformat() if due else None,
            "slaBreachAt": None,
            "assigneeId": row.get("owner_principal_id"),
            "requesterId": row.get("created_by_principal_id"),
            "status": row.get("status"),
            "actionHints": ["OPEN"],
            "deepLink": "/my-work",
            "authzScope": "SOURCE_SERVICE_ONLY",
            "updatedAt": row.get("updated_at"),
            "isOverdue": is_overdue,
        })
    if (
        overdue != projection["summary"]["overdue_count"]
        or any(counts_by_source[s] != source_counts[s] for s in admitted)
    ):
        raise AttentionFeedError("ATTENTION_SOURCE_COUNTS_INVALID")
    selected = set(sources) if sources else set(admitted)
    selected_rows = [item for item in normalized if item["sourceModule"] in selected]
    utc_day = as_of.date()
    counts = {
        "active": len(selected_rows),
        "overdue": sum(bool(x["isOverdue"]) for x in selected_rows),
        "dueToday": sum(
            x["dueAt"] is not None and _instant(x["dueAt"]).date() == utc_day
            for x in selected_rows
        ),
        "highPriority": sum(x["priority"] in {"CRITICAL", "HIGH"} for x in selected_rows),
    }
    filtered = [
        x for x in selected_rows
        if (view == "active"
            or (view == "overdue" and x["isOverdue"])
            or (view == "due_today" and x["dueAt"] is not None
                and _instant(x["dueAt"]).date() == utc_day)
            or (view == "high_priority" and x["priority"] in {"CRITICAL", "HIGH"}))
        and (not query or query.casefold() in " ".join((
            x["title"], x["summary"], x["sourceRecordId"], x["sourceModule"]
        )).casefold())
    ]
    filtered.sort(key=lambda x: (
        -x["urgencyScore"],
        x["dueAt"] or "9999-12-31T23:59:59+00:00",
        SOURCE_ORDER.index(x["sourceModule"]),
        x["sourceRecordId"],
    ))
    fingerprint = _cursor_fingerprint(
        tenant_id=projection["tenant_id"], principal_id=projection["principal_id"],
        as_of=projection["as_of"], view=view, sources=sources, query=query,
    )
    offset = _decode_cursor(cursor, fingerprint)
    if offset > len(filtered):
        raise AttentionFeedError("ATTENTION_CURSOR_INVALID")
    page = filtered[offset:offset + limit]
    next_cursor = (
        _encode_cursor(offset + limit, fingerprint)
        if offset + limit < len(filtered) else None
    )
    return {
        "schema": SCHEMA,
        "tenantId": projection["tenant_id"],
        "principalId": projection["principal_id"],
        "syncedAt": as_of.isoformat(),
        "view": view,
        "items": page,
        "counts": counts,
        "sources": [
            {"moduleId": s, "state": "ok" if counts_by_source[s] else "empty",
             "count": counts_by_source[s]}
            for s in admitted
        ],
        "coverage": {
            "admittedSources": list(admitted),
            "notRepresentedSources": ["FINANCE", "PEOPLE"],
            "completeEnterpriseCoverage": False,
        },
        "filteredTotal": len(filtered),
        "nextCursor": next_cursor,
        "authority": {
            "commandsOwnedBy": "SOURCE_SERVICES",
            "attentionCommandsEnabled": False,
            "sourceReadTransactions": "INDEPENDENT_OWNER_BOUNDARIES",
        },
    }


__all__ = ["SCHEMA", "SOURCE_ORDER", "AttentionFeedError", "build_attention_feed"]

# ARTIFACT: tools/eos/workspaces/service/attention_feed_projection.py
# VERSION: v1.0.0-AUTHORISED-ATTENTION-ITEMS
# AUTHORITY BOUNDARY: Exact previously admitted EOS source projection; read only.
# TENANT POSTURE: Exact caller tenant/principal and bounded source-dependent cursor.
# FAIL-CLOSED POSTURE: Invalid source, scope, counts, dates and cursor reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
