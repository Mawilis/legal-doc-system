"""Deterministic aggregation and projection of overdue EOS platform invoices.

This evaluator produces collection-workflow projection only. It does not mutate
subscriptions, entitlements, access controls, invoices, payments, or settlement.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from typing import Any

from .platform_dunning_registry import (
    PlatformDunningRegistry,
    PlatformDunningRegistryError,
)


TERMINAL_INVOICE_STATUSES = frozenset({"paid", "void", "cancelled", "canceled", "refunded"})
STATE_ORDER = {
    "ACTIVE": 0,
    "WARNING": 1,
    "CRITICAL": 2,
    "SUSPENDED_READONLY": 3,
    "TERMINATED": 4,
}
DEFAULT_POLICY = {
    "reminder_day": 3,
    "warning_day": 7,
    "critical_day": 10,
    "suspension_day": 14,
    "collections_day": 21,
    "termination_day": 30,
}


class PlatformDunningEvaluationError(RuntimeError):
    """Invalid source evidence or policy prevents dunning evaluation."""


def _utc(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def normalize_policy(value: dict[str, Any] | None) -> dict[str, int]:
    source = value or DEFAULT_POLICY
    result: dict[str, int] = {}
    for key, fallback in DEFAULT_POLICY.items():
        raw = source.get(key, fallback)
        if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
            raise PlatformDunningEvaluationError("PLATFORM_DUNNING_POLICY_INVALID")
        result[key] = raw
    if list(result.values()) != sorted(result.values()):
        raise PlatformDunningEvaluationError("PLATFORM_DUNNING_POLICY_NOT_MONOTONIC")
    return result


def policy_fingerprint(policy: dict[str, int]) -> str:
    return hashlib.sha3_512(
        json.dumps(policy, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def state_for_days(days_overdue: int, policy: dict[str, int]) -> str:
    if days_overdue >= policy["termination_day"]:
        return "TERMINATED"
    if days_overdue >= policy["suspension_day"]:
        return "SUSPENDED_READONLY"
    if days_overdue >= policy["critical_day"]:
        return "CRITICAL"
    if days_overdue >= policy["warning_day"]:
        return "WARNING"
    return "ACTIVE"


def aggregate_overdue_invoices(
    invoices: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    *,
    tenant_id: str,
    now: datetime,
) -> dict[str, dict[str, Any]]:
    """Return one deterministic maximum-overdue evidence group per subscription."""
    if not isinstance(now, datetime) or now.tzinfo is None:
        raise PlatformDunningEvaluationError("PLATFORM_DUNNING_NOW_MUST_BE_AWARE")
    instant = now.astimezone(timezone.utc)
    grouped: dict[str, dict[str, Any]] = {}
    for invoice in invoices:
        if not isinstance(invoice, dict):
            raise PlatformDunningEvaluationError("PLATFORM_DUNNING_INVOICE_INVALID")
        invoice_tenant = invoice.get("tenant_id") or invoice.get("tenantId")
        if invoice_tenant != tenant_id:
            continue
        status = str(invoice.get("status") or "").strip().lower()
        if status in TERMINAL_INVOICE_STATUSES:
            continue
        due_at = _utc(invoice.get("due_at") or invoice.get("dueAt"))
        if due_at is None or due_at > instant:
            continue
        subscription_id = str(invoice.get("subscription_id") or invoice.get("subscriptionId") or "").strip()
        invoice_id = str(invoice.get("invoice_id") or invoice.get("invoiceId") or "").strip()
        if not subscription_id or not invoice_id:
            raise PlatformDunningEvaluationError("PLATFORM_DUNNING_INVOICE_IDENTITY_INVALID")
        days = max(0, (instant.date() - due_at.date()).days)
        group = grouped.setdefault(subscription_id, {"invoice_ids": set(), "days_overdue": 0})
        group["invoice_ids"].add(invoice_id)
        group["days_overdue"] = max(group["days_overdue"], days)
    return {
        subscription_id: {
            "invoice_ids": tuple(sorted(group["invoice_ids"])),
            "days_overdue": group["days_overdue"],
        }
        for subscription_id, group in sorted(grouped.items())
    }


def evaluate_platform_dunning(
    *,
    tenant_id: str,
    invoices: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    policy: dict[str, Any] | None,
    projection_collection: Any,
    now: datetime,
    dry_run: bool = False,
    subscription_id: str | None = None,
    session: Any = None,
) -> dict[str, Any]:
    """Aggregate once per subscription and CAS-write projection; never touch lifecycle."""
    if not isinstance(tenant_id, str) or not tenant_id.strip() or tenant_id != tenant_id.strip():
        raise PlatformDunningEvaluationError("PLATFORM_DUNNING_TENANT_REQUIRED")
    normalized = normalize_policy(policy)
    groups = aggregate_overdue_invoices(invoices, tenant_id=tenant_id, now=now)
    if subscription_id:
        groups = {key: value for key, value in groups.items() if key == subscription_id}
    policy_fp = policy_fingerprint(normalized)
    transitions: list[dict[str, Any]] = []
    for current_subscription, evidence in groups.items():
        target_state = state_for_days(evidence["days_overdue"], normalized)
        existing = PlatformDunningRegistry.get(
            tenant_id, current_subscription, projection_collection, session=session
        )
        current_state = existing["state"] if existing else "ACTIVE"
        if existing is None and target_state == "ACTIVE":
            # Below the first escalation threshold there is no dunning
            # projection transition to persist.
            continue
        if STATE_ORDER[target_state] < STATE_ORDER[current_state]:
            continue
        if target_state == current_state and existing is not None:
            same_evidence = (
                existing["invoice_ids"] == list(evidence["invoice_ids"])
                and existing["days_overdue"] == evidence["days_overdue"]
                and existing["policy_fingerprint"] == policy_fp
            )
            if same_evidence:
                continue
        candidate = {
            "tenant_id": tenant_id,
            "subscription_id": current_subscription,
            "from_state": current_state,
            "state": target_state,
            "invoice_ids": list(evidence["invoice_ids"]),
            "days_overdue": evidence["days_overdue"],
            "expected_revision": existing["revision"] if existing else 0,
            "policy_fingerprint": policy_fp,
        }
        if not dry_run:
            persisted = PlatformDunningRegistry.transition(
                tenant_id=tenant_id,
                subscription_id=current_subscription,
                state=target_state,
                invoice_ids=evidence["invoice_ids"],
                days_overdue=evidence["days_overdue"],
                policy_fingerprint=policy_fp,
                expected_revision=candidate["expected_revision"],
                collection=projection_collection,
                evaluated_at=now,
                session=session,
            )
            candidate["revision"] = persisted["revision"]
            candidate["transition_fingerprint"] = persisted["transition_fingerprint"]
        transitions.append(candidate)
    return {
        "success": True,
        "tenant_id": tenant_id,
        "dry_run": dry_run,
        "evaluated_subscriptions": len(groups),
        "transition_count": len(transitions),
        "transitions": transitions,
        "subscription_lifecycle_mutated": False,
    }


__all__ = [
    "PlatformDunningEvaluationError",
    "aggregate_overdue_invoices",
    "evaluate_platform_dunning",
    "normalize_policy",
    "policy_fingerprint",
    "state_for_days",
]
