# -*- coding: utf-8 -*-
"""Canonical package boundary for FG171C event-driven runtime scheduling.

TITLE: WILSY OS FG171C Event-Driven Scheduler Package
VERSION: v1.0.0-WILSY-FG171C-EVENT-DRIVEN-SCHEDULER
AUTHORITY: Wilsy OS Core Governance
EPITOME: Provides the reachable FG171C task-start scheduler contract at tools.eos.runtime.scheduler without conflating the distinct FG233D recurring-maintenance scheduler.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/runtime/scheduler/__init__.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder & Chief Architect); Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.0 establishes the first sovereign package contract, restores reachable EventDrivenScheduler imports, removes implicit tenant-default authority, aligns TASK_STARTED construction with scheduler_events.py, and publishes through RuntimeEventBus.publish_async().
COMPLIANCE: Explicit tenant scope; no persistence or transaction ownership; POPIA section 19, GDPR Article 32, and SOC 2 CC7.2 tenant-isolation posture.
SECURITY / PRIVACY POSTURE: Stores no credentials or durable authority; transient task material is defensively copied into immutable event metadata.
TENANT BOUNDARY: tenant_id must be explicitly supplied and valid; no default tenant, cross-tenant lookup, membership inference, or tenant authorization occurs here.
AUTHORITY BOUNDARY: Owns task-start scheduling only. Authentication, principal authority, tenant authorization, request/correlation trust, worker execution, and higher-level kernel execution authority remain external.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial execution authority.

Epitome:
    This package is the canonical reachable import boundary for the FG171C
    event-driven scheduler:

        from tools.eos.runtime.scheduler import EventDrivenScheduler

    FG171C task dispatch is intentionally distinct from the FG233D recurring
    maintenance capability implemented by runtime_scheduler_engine.py. This
    package does not merge their semantics or silently re-export the FG233D
    singleton.

    Scheduler-event execution identity is task-scoped: execution_id equals the
    resolved task_id, matching current kernel scheduler-event producers. That
    identity is not the higher-level KEXEC identity owned by the canonical
    Engineering Kernel runner.

Collaboration & Ownership:
    Founder & Chief Architect: Wilson Khanyezi (Wilsy (Pty) Ltd)
    Engineering Collaboration: Wilsy OS Core Engineering
    File Path: tools/eos/runtime/scheduler/__init__.py
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from ..scheduler_events import (
    RuntimeEventBus,
    RuntimeEventTypeEnum,
    TaskStartedEventDTO,
)

VERSION = "v1.0.0-WILSY-FG171C-EVENT-DRIVEN-SCHEDULER"

logger = logging.getLogger("WilsyOS.Runtime.Scheduler")

_FORBIDDEN_TENANT_REFERENCES = frozenset(
    {
        "unknown",
        "none",
        "null",
        "tenant-default",
    }
)


class SchedulerAuthorityError(ValueError):
    """Fail closed when FG171C scheduling lacks valid explicit tenant scope.

    Authority boundary:
        This error reports invalid scheduler ingress only. It does not
        authenticate a principal, authorize tenant membership, grant
        permissions, or create financial authority.

    Tenant posture:
        Missing, blank, and forbidden compatibility tenant references are
        rejected before a TASK_STARTED event is emitted.
    """


class EventDrivenScheduler:
    """Create and asynchronously publish tenant-scoped TASK_STARTED events.

    Authority:
        The scheduler owns task-start event construction only. Tenant authority
        must be established by an upstream trusted boundary.

    Mutation:
        Caller-supplied task payload dictionaries are defensively copied into
        immutable TaskStartedEventDTO metadata.

    Persistence and transactions:
        None. This scheduler owns no persistence session, database transaction,
        durable retry, idempotency record, worker registry, or settlement state.

    Capability separation:
        This FG171C scheduler performs per-task event initiation. It is not the
        FG233D RuntimeSchedulerEngine used for recurring monitoring and
        maintenance scheduling.

    Financial boundary:
        None. Kennel EOS remains the exclusive financial execution authority.
    """

    def __init__(self, event_bus: RuntimeEventBus) -> None:
        """Bind this scheduler to an explicit caller-owned runtime event bus.

        Construction performs no subscription, persistence, authority lookup,
        worker dispatch, or financial operation.
        """
        self.event_bus = event_bus
        self._is_active = True
        logger.info("FG171C EventDrivenScheduler initialized")

    async def schedule_task(
        self,
        engine_name: str,
        task_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Publish one contract-valid TASK_STARTED event.

        Args:
            engine_name:
                Explicit worker-routing name. Routing metadata grants no
                authentication, tenant, permission, or financial authority.
            task_id:
                Optional task-scoped execution identity. When absent, a fresh
                scheduler task identifier is generated.
            session_id:
                Optional runtime grouping reference. When absent, a fresh
                scheduler-local session reference is generated; it grants no
                authority and is not a kernel KEXEC identity.
            tenant_id:
                Required tenant reference. The Optional annotation preserves
                source compatibility with legacy callers, while absence, blank
                values, and forbidden sentinels fail closed.
            payload:
                Optional transient task material copied into event metadata.

        Returns:
            The resolved task identifier. The emitted scheduler event uses the
            same value for task_id and execution_id.

        Raises:
            SchedulerAuthorityError:
                The tenant reference is absent, blank, or forbidden.

        Tenant boundary:
            Outer whitespace is removed from the explicit tenant reference.
            No tenant identifier is invented, substituted, authorized, or
            persisted by this scheduler.

        Idempotency:
            No durable idempotency claim is made. Omitting task_id creates a new
            task identity on every invocation.

        Financial boundary:
            Scheduling is not approval, release authorization, execution,
            payment, or settlement.
        """
        if tenant_id is None:
            raise SchedulerAuthorityError("SCHEDULER_TENANT_ID_REQUIRED")

        resolved_tenant_id = tenant_id.strip()
        if (
            not resolved_tenant_id
            or resolved_tenant_id.casefold() in _FORBIDDEN_TENANT_REFERENCES
        ):
            raise SchedulerAuthorityError("SCHEDULER_TENANT_ID_INVALID")

        resolved_task_id = task_id or f"task-{uuid.uuid4().hex[:8]}"
        resolved_session_id = session_id or f"sess-{uuid.uuid4().hex[:8]}"
        resolved_payload = dict(payload or {})

        task_event = TaskStartedEventDTO(
            execution_id=resolved_task_id,
            event_type=RuntimeEventTypeEnum.TASK_STARTED.value,
            message=f"Task {resolved_task_id} started",
            session_id=resolved_session_id,
            tenant_id=resolved_tenant_id,
            task_id=resolved_task_id,
            engine_name=engine_name,
            metadata=resolved_payload,
        )

        logger.info(
            "Scheduling task [%s] on engine [%s] for tenant [%s]",
            resolved_task_id,
            engine_name,
            resolved_tenant_id,
        )

        await self.event_bus.publish_async(
            RuntimeEventTypeEnum.TASK_STARTED,
            task_event,
        )
        return resolved_task_id

    async def shutdown(self) -> None:
        """Mark this scheduler inactive without mutating shared runtime state.

        Shutdown does not tear down the caller-owned event bus, cancel workers,
        flush persistence, close transactions, or exercise financial authority.
        """
        self._is_active = False
        logger.info("FG171C EventDrivenScheduler shut down")


__all__ = [
    "VERSION",
    "EventDrivenScheduler",
    "SchedulerAuthorityError",
]


# ARTIFACT: scheduler/__init__.py
# VERSION: v1.0.0-WILSY-FG171C-EVENT-DRIVEN-SCHEDULER
# AUTHORITY BOUNDARY: FG171C task-start scheduling only; authentication, tenant authorization, request/correlation trust, worker execution, FG233D recurring scheduling, and higher-level KEXEC authority remain external
# TENANT POSTURE: explicit validated tenant required; no tenant-default fallback, synthesis, persistence, membership inference, or cross-tenant authority
# FAIL-CLOSED POSTURE: absent, blank, and forbidden tenant references raise SchedulerAuthorityError before event emission
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains the exclusive financial execution authority
# END OF WILSY OS SOVEREIGN ARTIFACT
