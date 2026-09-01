# -*- coding: utf-8 -*-
"""Canonical public export boundary for the Wilsy OS runtime package.

TITLE: WILSY OS Runtime Canonical Export Boundary
VERSION: v1.0.0-WILSY-RUNTIME-CANONICAL-EXPORTS
AUTHORITY: Wilsy OS Core Governance
EPITOME: Preserves the established tools.eos.runtime public surface by re-exporting each runtime contract from its single canonical dedicated module.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/runtime/__init__.py
COLLABORATION / OWNERSHIP: Wilson Khanyezi (Founder & Chief Architect); Wilsy OS Core Engineering
CERTIFICATION/UPDATE DATE: 2026-09-01
CHANGELOG: v1.0.0 removes stale duplicate event, scheduler, bus, and bridge implementations and establishes this package initializer as an import/export boundary only.
COMPLIANCE: Delegates tenant-sensitive runtime behavior to the canonical scheduler and bridge under POPIA section 19, GDPR Article 32, and SOC 2 CC7.2 isolation requirements.
SECURITY / PRIVACY POSTURE: Owns no credentials, personal information processing, authentication decision, authorization decision, logging, telemetry, or executable fallback behavior.
TENANT BOUNDARY: Owns no tenant lookup, tenant authorization, tenant default, tenant substitution, or cross-tenant behavior; explicit fail-closed tenant enforcement remains delegated to the canonical scheduler and bridge.
AUTHORITY BOUNDARY: Owns no authentication, tenant authorization, KEXEC authority, persistence, transaction, idempotency, worker execution, or operational authority; it exposes canonical contracts without altering them.
FINANCIAL AUTHORITY BOUNDARY: None. Kennel EOS remains the exclusive financial execution authority.

Institutional contract:
    This initializer exists solely to preserve stable root-package imports while
    ensuring that every exported symbol is identical to the object defined by
    its canonical dedicated module. It creates no wrapper, alias implementation,
    fallback, state, event, side effect, tenant scope, or authority.

Canonical relationships:
    Pipeline lifecycle symbols are supplied by pipeline_status,
    pipeline_statistics, pipeline_result, and pipeline_manager. Event contracts
    and the event bus are supplied by scheduler_events. Task-start scheduling is
    supplied by scheduler, and worker event orchestration is supplied by
    scheduler_bridge.

Fail-closed posture:
    Tenant and authority validation is neither weakened nor reproduced here.
    Callers receive the already-canonical EventDrivenScheduler and
    WorkerEventBridge directly, so their explicit tenant requirements and
    authority boundaries remain the only runtime behavior.
"""
from __future__ import annotations

from .pipeline_manager import PipelineManager
from .pipeline_result import PipelineResult
from .pipeline_statistics import PipelineStatistics
from .pipeline_status import PipelineStatus, PipelineStatusValidator
from .scheduler import EventDrivenScheduler
from .scheduler_bridge import WorkerEventBridge
from .scheduler_events import (
    ArtifactPublishedEventDTO,
    RuntimeEventBus,
    RuntimeEventTypeEnum,
    TaskCompletedEventDTO,
    TaskStartedEventDTO,
)

__all__ = [
    "PipelineStatus",
    "PipelineStatusValidator",
    "PipelineStatistics",
    "PipelineResult",
    "PipelineManager",
    "RuntimeEventTypeEnum",
    "ArtifactPublishedEventDTO",
    "TaskStartedEventDTO",
    "TaskCompletedEventDTO",
    "EventDrivenScheduler",
    "RuntimeEventBus",
    "WorkerEventBridge",
]


# ARTIFACT: tools/eos/runtime/__init__.py
# VERSION: v1.0.0-WILSY-RUNTIME-CANONICAL-EXPORTS
# AUTHORITY BOUNDARY: import/export only; no authentication, tenant authorization, KEXEC authority, persistence, transactions, idempotency, worker execution, or operational authority
# TENANT POSTURE: no tenant default, synthesis, lookup, substitution, or authorization; canonical scheduler and bridge retain explicit fail-closed enforcement
# FAIL-CLOSED POSTURE: no duplicate implementation, wrapper, fallback, invented tenant scope, or invented authority
# FINANCIAL EXECUTION AUTHORITY: none; Kennel EOS remains the exclusive financial execution authority
# END OF WILSY OS SOVEREIGN ARTIFACT
