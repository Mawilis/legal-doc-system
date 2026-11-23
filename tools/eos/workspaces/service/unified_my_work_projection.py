"""TITLE: WILSY OS Unified My Work Read Projection
VERSION: v1.4.0-SOURCE-PREDECESSOR-READINESS
AUTHORITY: Wilsy OS Core Governance.
EPITOME: Deterministically compose independently admitted EOS source work while
         preserving source identity, tenant scope and visibility provenance.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/workspaces/service/unified_my_work_projection.py
COLLABORATION / OWNERSHIP: unified_my_work_router admits Legal, Operations,
                           Intelligence, CRM and HR through their own authorities.
CERTIFICATION / UPDATE DATE: 2026-11-23.
CHANGELOG: v1.4.0-SOURCE-PREDECESSOR-READINESS
         projects only source-attested Projects readiness and predecessor
         counts; no new command permission or cross-task visibility.
CHANGELOG: v1.3.2-SOURCE-TAXONOMY-SOVEREIGN-CHANGELOG
         restores the historical HR admission version and revalidates the
         sovereign source-backed audience contract without changing IAM.
CHANGELOG: v1.3.1-LEGACY-SOURCE-REVISION-COMPATIBILITY
         leaves preexisting source revision formats untouched when no audited
         audience evidence is provided. A claimed audience always requires
         current exact integer source revision and source-owned evidence.
CHANGELOG: v1.3.0-SOURCE-GOVERNED-WORK-AUDIENCE-PROJECTION
         exposes only independently source-attested current audience metadata,
         returns UNCLASSIFIED without evidence, and rejects foreign, stale or
         unsupported taxonomy claims. No regex/title/role classification.
CHANGELOG: v1.2.0-PROJECTS-AUTHORIZED-WORK-PROJECTION includes independently admitted
         exact-participant project tasks, preserving project/due-date source
         coordinates and blocked visibility without inventing due-at instants.
CHANGELOG: v1.2.0-PROJECTS-AUTHORIZED-WORK-PROJECTION accepts only the sanitized,
           independently admitted HR action envelope supplied by the existing
           headcount and hiring source owners. It never reads personnel
           collections or introduces HR command authority.
           v1.0.1-SOURCE-IDENTITY-TYPE-NARROWING makes the existing identity
           validation explicit so static analysis proves source-key types;
           adds the complete sovereign header, API contract and end seal.
           v1.0.0-UNIFIED-MY-WORK-PROJECTION established source-owned aggregation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: In-memory projection only; no logging, storage,
                          secrets, network calls or cross-tenant lookup.
TENANT BOUNDARY: Every included envelope and explicit row tenant must match
                 the authenticated caller's tenant. No directory is enumerated.
AUTHORITY BOUNDARY: Only pre-admitted source payloads are consumed. This module
                    creates no visibility, assignment, command or IAM authority.
TRANSACTION / IDEMPOTENCY BOUNDARY: Source adapters own independent reads and
                    transactions. Sorting and deduplication are deterministic;
                    this module owns no persistence or durable command replay.
FINANCIAL AUTHORITY BOUNDARY: No financial execution or settlement authority;
                              Kennel EOS remains exclusive.
FAIL-CLOSED POSTURE: Malformed, foreign or divergent source evidence rejects.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Iterable, Mapping

from tools.eos.workspaces.service.work_audience_policy import evaluate_work_audience

VERSION = "v1.4.0-SOURCE-PREDECESSOR-READINESS"
SCHEMA = "WILSY-OS-UNIFIED-MY-WORK/V1"

_SOURCE_ORDER = ("LEGAL", "OPERATIONS", "INTELLIGENCE", "CRM", "HR", "PROJECTS")
_PRIORITY = {"CRITICAL": 0, "HIGH": 1, "NORMAL": 2, "LOW": 3}
_TERMINAL = frozenset({"COMPLETED", "CANCELLED"})


class UnifiedMyWorkProjectionError(ValueError):
    """Structured pure-projection rejection; grants no authority or mutation.

    The stable code identifies malformed, foreign or divergent source evidence
    without disclosing another tenant\'s existence or any persisted record.
    """

    def __init__(self, code: str) -> None:
        """Bind the stable source-validation code without logging source data."""
        self.code = code
        super().__init__(code)


def _instant(value: object, code: str) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as error:
            raise UnifiedMyWorkProjectionError(code) from error
    else:
        raise UnifiedMyWorkProjectionError(code)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise UnifiedMyWorkProjectionError(code)
    return parsed.astimezone(timezone.utc)


def _source_items(
    source: str,
    payload: Mapping[str, Any] | None,
    tenant_id: str,
) -> Iterable[tuple[str, Mapping[str, Any]]]:
    if payload is None:
        return ()
    if not isinstance(payload, Mapping) or payload.get("tenant_id") != tenant_id:
        raise UnifiedMyWorkProjectionError("SOURCE_TENANT_MISMATCH")
    if source in {"OPERATIONS", "INTELLIGENCE", "CRM", "HR", "PROJECTS"}:
        items = payload.get("items")
        if not isinstance(items, (list, tuple)):
            raise UnifiedMyWorkProjectionError("SOURCE_ITEMS_INVALID")
        return tuple((source, item) for item in items)
    if source == "LEGAL":
        # Legal's canonical read model separates assigned and supervised rows.
        # Both lists are already filtered by the Legal service's visibility rules.
        assigned = payload.get("assigned_work_items", ())
        supervised = payload.get("supervised_work_items", ())
        if not isinstance(assigned, (list, tuple)) or not isinstance(supervised, (list, tuple)):
            raise UnifiedMyWorkProjectionError("SOURCE_ITEMS_INVALID")
        return tuple(("LEGAL_ASSIGNED", item) for item in assigned) + tuple(
            ("LEGAL_SUPERVISED", item) for item in supervised
        )
    raise UnifiedMyWorkProjectionError("SOURCE_UNSUPPORTED")


def build_unified_my_work(
    *,
    tenant_id: str,
    principal_id: str,
    now: datetime,
    legal: Mapping[str, Any] | None = None,
    operations: Mapping[str, Any] | None = None,
    intelligence: Mapping[str, Any] | None = None,
    crm: Mapping[str, Any] | None = None,
    hr: Mapping[str, Any] | None = None,
    projects: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Compose authorized source projections without becoming an authority.

    A source may be omitted only when its caller intentionally did not request
    that source. An included source must identify the exact authenticated tenant.
    Work identity is namespaced by source so unrelated registries cannot collide.

    Collaboration: unified_my_work_router supplies current, independently
    authorized source payloads. Tenant/principal identities scope this read
    projection and do not establish membership or permissions. Source-owned
    transactions remain independent; no global atomic snapshot is implied.
    The function neither starts nor changes transactions, writes audit/outbox
    evidence, executes commands nor promises durable idempotency. It preserves
    source provenance, rejects invalid evidence with UnifiedMyWorkProjectionError,
    and returns only a presentation snapshot. Financial execution remains EOS.
    """
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        raise UnifiedMyWorkProjectionError("TENANT_ID_INVALID")
    if not isinstance(principal_id, str) or not principal_id.strip():
        raise UnifiedMyWorkProjectionError("PRINCIPAL_ID_INVALID")
    instant = _instant(now, "AS_OF_INVALID")
    if instant is None:
        raise UnifiedMyWorkProjectionError("AS_OF_INVALID")

    payloads = {
        "LEGAL": legal,
        "OPERATIONS": operations,
        "INTELLIGENCE": intelligence,
        "CRM": crm,
        "HR": hr,
        "PROJECTS": projects,
    }
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    visibility: dict[tuple[str, str], set[str]] = {}

    for source in _SOURCE_ORDER:
        payload = payloads[source]
        if payload is None:
            continue
        for provenance, raw in _source_items(source, payload, tenant_id):
            if not isinstance(raw, Mapping):
                raise UnifiedMyWorkProjectionError("SOURCE_ITEM_INVALID")
            # Payload-level tenant binding is necessary but not sufficient:
            # reject any row that carries a conflicting tenant coordinate.
            # Rows without tenant_id remain valid only because the source
            # adapter is responsible for exact-tenant filtering before return.
            if "tenant_id" in raw and raw.get("tenant_id") != tenant_id:
                raise UnifiedMyWorkProjectionError("SOURCE_ITEM_TENANT_MISMATCH")
            item_id = raw.get("work_item_id")
            title = raw.get("title")
            status = raw.get("status")
            priority = raw.get("priority", "NORMAL")
            if (
                not isinstance(item_id, str) or not item_id.strip()
                or not isinstance(title, str) or not title.strip()
                or not isinstance(status, str) or not status.strip()
                or not isinstance(priority, str) or not priority.strip()
            ):
                raise UnifiedMyWorkProjectionError("SOURCE_ITEM_IDENTITY_INVALID")
            if source == "PROJECTS" and (
                not isinstance(raw.get("project_id"), str)
                or not raw["project_id"].startswith("prj-")
                or not isinstance(raw.get("owner_principal_id"), str)
                or raw["owner_principal_id"] != principal_id
                or status not in {"OPEN", "IN_PROGRESS", "BLOCKED"}
                or (
                    raw.get("due_date") is not None and (
                        not isinstance(raw["due_date"], str)
                        or len(raw["due_date"]) != 10
                    )
                )
            ):
                raise UnifiedMyWorkProjectionError("PROJECTS_SOURCE_ITEM_INVALID")
            if source == "PROJECTS":
                total = raw.get("dependency_total")
                remaining = raw.get("dependency_remaining")
                readiness = raw.get("dependency_readiness")
                if (type(total) is not int or not 0 <= total <= 25
                    or type(remaining) is not int or not 0 <= remaining <= total
                    or readiness != ("WAITING" if remaining else "READY")):
                    raise UnifiedMyWorkProjectionError("PROJECTS_DEPENDENCY_EVIDENCE_INVALID")
            if status in _TERMINAL:
                continue
            if priority not in _PRIORITY:
                raise UnifiedMyWorkProjectionError("SOURCE_PRIORITY_INVALID")
            due_at = _instant(raw.get("due_at"), "SOURCE_DUE_AT_INVALID")
            classification = evaluate_work_audience(
                tenant_id=tenant_id, source=source, record_id=item_id,
                source_revision=(raw.get("revision")
                                 if raw.get("audience_evidence") is not None else None),
                evidence=raw.get("audience_evidence"),
            )
            key = (source, item_id)
            candidate = {
                "source": source,
                "work_item_id": item_id,
                "source_key": f"{source}:{item_id}",
                "audience": classification.audience.value,
                "audience_evidence_ref": classification.source_evidence_ref,
                "audience_source_revision": classification.source_revision,
                "critical_gate": classification.critical_gate,
                "title": title,
                "description": raw.get("description", ""),
                "status": status,
                "priority": priority,
                "kind": raw.get("kind", "TASK"),
                "due_at": due_at.isoformat() if due_at else None,
                "owner_principal_id": raw.get("owner_principal_id"),
                "created_by_principal_id": raw.get("created_by_principal_id"),
                "updated_at": raw.get("updated_at"),
                "is_overdue": due_at is not None and due_at < instant,
                "action_authority": "SOURCE_SERVICE_ONLY",
                "completion_route": None,
                "approval_authority": None,
                "project_id": raw.get("project_id") if source == "PROJECTS" else None,
                "due_date": raw.get("due_date") if source == "PROJECTS" else None,
                "dependency_readiness": readiness if source == "PROJECTS" else None,
                "dependency_total": total if source == "PROJECTS" else None,
                "dependency_remaining": remaining if source == "PROJECTS" else None,
            }
            previous = merged.get(key)
            if previous is not None:
                # Divergent copies from the same source are not silently merged.
                comparable = ("title", "status", "priority", "due_at",
                              "audience", "audience_evidence_ref",
                              "audience_source_revision", "critical_gate",
                              "dependency_readiness", "dependency_total",
                              "dependency_remaining")
                if any(previous[field] != candidate[field] for field in comparable):
                    raise UnifiedMyWorkProjectionError("SOURCE_ITEM_DIVERGENCE")
            else:
                merged[key] = candidate
            visibility.setdefault(key, set()).add(provenance)

    rows = []
    for key, item in merged.items():
        item["visibility_provenance"] = sorted(visibility[key])
        rows.append(item)

    def ordering(item: Mapping[str, Any]) -> tuple[Any, ...]:
        due = _instant(item["due_at"], "SOURCE_DUE_AT_INVALID")
        return (
            0 if item["is_overdue"] else 1,
            _PRIORITY[item["priority"]],
            due or datetime.max.replace(tzinfo=timezone.utc),
            _SOURCE_ORDER.index(item["source"]),
            item["work_item_id"],
        )

    rows.sort(key=ordering)
    overdue_count = sum(1 for item in rows if item["is_overdue"])
    return {
        "schema": SCHEMA,
        "version": VERSION,
        "tenant_id": tenant_id,
        "principal_id": principal_id,
        "as_of": instant.isoformat(),
        "items": rows,
        "summary": {
            "active_count": len(rows),
            "overdue_count": overdue_count,
            # Do not emit zero-count entries for sources that were not
            # admitted; an omitted source is not equivalent to an empty queue.
            "source_counts": {
                source: sum(1 for item in rows if item["source"] == source)
                for source in _SOURCE_ORDER
                if payloads[source] is not None
            },
        },
        "authority": {
            "permits_assignment": False,
            "permits_completion": False,
            "permits_approval": False,
            "permits_confidential_matter_access": False,
            "commands_owned_by": "SOURCE_SERVICES",
        },
    }


__all__ = ["SCHEMA", "VERSION", "UnifiedMyWorkProjectionError", "build_unified_my_work"]

# ARTIFACT: unified_my_work_projection.py
# VERSION: v1.4.0-SOURCE-PREDECESSOR-READINESS
# AUTHORITY BOUNDARY: Read projection of independently admitted source work only.
# TENANT POSTURE: Exact envelope and explicit item tenant binding; no cross-tenant lookup.
# FAIL-CLOSED POSTURE: Malformed, foreign and divergent source evidence rejects.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
