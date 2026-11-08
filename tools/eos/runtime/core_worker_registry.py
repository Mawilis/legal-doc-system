"""Canonical worker registrations for production-owned EOS handlers.

Only handlers with an explicit Python implementation and declared authority
boundary are registered here. This module does not start workers or schedulers.
"""
from __future__ import annotations

from typing import Any

from .compliance_scan_worker import (
    ComplianceScanWorker,
    provision_compliance_scan_indexes,
)
from .worker_registry import EngineWorkerRegistry

CLIENT_COLLECTION = "clients"
COMPLIANCE_FINDINGS_COLLECTION = "eos_compliance_findings"
NOTIFICATION_OUTBOX_COLLECTION = "eos_notification_outbox"


def build_core_worker_registry(*, database: Any, mongo_client: Any) -> EngineWorkerRegistry:
    """Register tenant-scoped compliance scanning against the kernel DB graph."""
    if database is None or mongo_client is None:
        raise RuntimeError("EOS_KERNEL_DATABASE_NOT_READY")
    if getattr(database, "client", None) is not mongo_client:
        raise RuntimeError("EOS_WORKER_DATABASE_CLIENT_MISMATCH")

    registry = EngineWorkerRegistry()
    registry.register_worker(
        ComplianceScanWorker(
            clients=database[CLIENT_COLLECTION],
            findings=database[COMPLIANCE_FINDINGS_COLLECTION],
            notification_outbox=database[NOTIFICATION_OUTBOX_COLLECTION],
            tasks=database["eos_runtime_tasks"],
            mongo_client=mongo_client,
        )
    )
    return registry


def provision_core_worker_indexes(*, database: Any) -> None:
    """Provision indexes explicitly during a governed deployment migration."""
    if database is None:
        raise RuntimeError("EOS_KERNEL_DATABASE_NOT_READY")
    provision_compliance_scan_indexes(
        clients=database[CLIENT_COLLECTION],
        findings=database[COMPLIANCE_FINDINGS_COLLECTION],
        notification_outbox=database[NOTIFICATION_OUTBOX_COLLECTION],
    )


__all__ = [
    "CLIENT_COLLECTION",
    "COMPLIANCE_FINDINGS_COLLECTION",
    "NOTIFICATION_OUTBOX_COLLECTION",
    "build_core_worker_registry",
    "provision_core_worker_indexes",
]
