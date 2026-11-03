"""EOS orchestration for the tenant owner's commercial work queue.

HTTP/IAM admission occurs before this service. This service independently
requires exact active crm.core subscription truth before exposing or mutating
the commercial workspace. It does not read or mutate Legal matters.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from tools.eos.crm.domain.owner_commercial_work_item import (
    OwnerCommercialWorkItem, OwnerWorkKind, OwnerWorkPriority,
)
from tools.eos.crm.persistence.owner_commercial_work_registry import (
    OwnerCommercialWorkRegistry,
)
from tools.eos.crm.service.crm_core_entitlement_resolver import (
    CrmCoreEntitlementResolverError, resolve_crm_core_entitlement,
)


class OwnerCommercialWorkspaceError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class OwnerCommercialWorkspaceService:
    """Compose active CRM entitlement with tenant-owned commercial work."""

    __slots__ = ("_registry", "_subscriptions")

    def __init__(self, registry: OwnerCommercialWorkRegistry, subscription_collection: Any) -> None:
        if not isinstance(registry, OwnerCommercialWorkRegistry):
            raise OwnerCommercialWorkspaceError("OWNER_WORK_REGISTRY_REQUIRED")
        if subscription_collection is None:
            raise OwnerCommercialWorkspaceError("OWNER_WORK_SUBSCRIPTIONS_REQUIRED")
        self._registry = registry
        self._subscriptions = subscription_collection

    def _require_entitlement(self, tenant_id: str, session: Any) -> None:
        try:
            entitlement = resolve_crm_core_entitlement(
                tenant_id, self._subscriptions, session,
            )
        except CrmCoreEntitlementResolverError as error:
            raise OwnerCommercialWorkspaceError("OWNER_WORK_ENTITLEMENT_UNAVAILABLE") from error
        if entitlement is None or entitlement.tenant_id != tenant_id:
            raise OwnerCommercialWorkspaceError("OWNER_WORK_CRM_CORE_NOT_ENTITLED")

    def daily_queue(self, *, tenant_id: str, now: datetime, session: Any):
        self._require_entitlement(tenant_id, session)
        return self._registry.daily_queue(
            tenant_id=tenant_id, now=now, session=session,
        )

    def create(
        self, *, tenant_id: str, principal_id: str, title: str,
        description: str, kind: OwnerWorkKind, priority: OwnerWorkPriority,
        due_at: datetime | None, source_type: str | None, source_id: str | None,
        idempotency_key: str, now: datetime, session: Any,
    ) -> OwnerCommercialWorkItem:
        self._require_entitlement(tenant_id, session)
        item = OwnerCommercialWorkItem.create(
            tenant_id=tenant_id, title=title, description=description,
            kind=kind, priority=priority, owner_principal_id=principal_id,
            due_at=due_at, source_type=source_type, source_id=source_id, now=now,
        )
        return self._registry.create_or_replay(
            item, idempotency_key=idempotency_key, session=session,
        )


__all__ = ["OwnerCommercialWorkspaceError", "OwnerCommercialWorkspaceService"]
