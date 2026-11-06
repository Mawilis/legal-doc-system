"""Tenant module work queue orchestration over exact D22B2 entitlement truth.

Each product receives its own registry collection and exact product entitlement.
The service never treats module availability as IAM or business-role authority.
"""
from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from hashlib import sha3_256
from typing import Any

from tools.eos.saas.entitlement.product_catalogue import TenantProductId, get_tenant_product
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import derive_tenant_product_entitlement_id
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    TenantProductEntitlementRegistryError,
    TenantProductEntitlementRegistryNotFoundError,
    get_current,
)
from tools.eos.saas.domain.tenant_product_entitlement import TenantProductEntitlementState
from tools.eos.workspaces.domain.tenant_module_work_item import (
    TenantModuleWorkItem, ModuleWorkKind, ModuleWorkPriority,
)
from tools.eos.workspaces.persistence.tenant_module_work_registry import (
    TenantModuleWorkRegistry,
)


class TenantModuleWorkspaceError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class TenantModuleWorkspaceService:
    """Compose one exact product entitlement with its isolated tenant work queue."""

    __slots__ = ("_registry", "_product_id", "_history", "_current")

    def __init__(
        self, registry: TenantModuleWorkRegistry, product_id: TenantProductId,
        history_collection: Any, current_collection: Any,
    ) -> None:
        if not isinstance(registry, TenantModuleWorkRegistry):
            raise TenantModuleWorkspaceError("MODULE_WORK_REGISTRY_REQUIRED")
        if product_id not in {TenantProductId.OPERATIONS, TenantProductId.INTELLIGENCE}:
            raise TenantModuleWorkspaceError("MODULE_WORK_PRODUCT_UNSUPPORTED")
        if history_collection is None or current_collection is None:
            raise TenantModuleWorkspaceError("MODULE_WORK_ENTITLEMENT_DEPENDENCIES_REQUIRED")
        self._registry, self._product_id = registry, product_id
        self._history, self._current = history_collection, current_collection

    def _require_product(self, tenant_id: str, session: Any) -> None:
        try:
            descriptor = get_tenant_product(self._product_id)
            entitlement_id = derive_tenant_product_entitlement_id(tenant_id, self._product_id)
            entitlement = get_current(
                tenant_id, entitlement_id, self._history, self._current, session=session,
            )
        except TenantProductEntitlementRegistryNotFoundError as error:
            raise TenantModuleWorkspaceError("MODULE_WORK_PRODUCT_NOT_ENTITLED") from error
        except (TenantProductEntitlementRegistryError, ValueError, TypeError) as error:
            raise TenantModuleWorkspaceError("MODULE_WORK_ENTITLEMENT_UNAVAILABLE") from error
        if (
            descriptor.product_id is not self._product_id
            or entitlement.tenant_id != tenant_id
            or entitlement.entitlement_id != entitlement_id
            or entitlement.product_id is not self._product_id
            or entitlement.lifecycle_state is not TenantProductEntitlementState.ACTIVE
        ):
            raise TenantModuleWorkspaceError("MODULE_WORK_PRODUCT_NOT_ENTITLED")

    def daily_queue(self, *, tenant_id: str, now: datetime, session: Any):
        self._require_product(tenant_id, session)
        return self._registry.daily_queue(tenant_id=tenant_id, now=now, session=session)

    def create(
        self, *, tenant_id: str, principal_id: str, title: str, description: str,
        kind: ModuleWorkKind, priority: ModuleWorkPriority, due_at: datetime | None,
        source_type: str | None, source_id: str | None, idempotency_key: str,
        now: datetime, session: Any,
    ) -> TenantModuleWorkItem:
        self._require_product(tenant_id, session)
        if not isinstance(idempotency_key, str) or not idempotency_key or idempotency_key != idempotency_key.strip():
            raise TenantModuleWorkspaceError("MODULE_WORK_IDEMPOTENCY_KEY_INVALID")
        stable_id = "tmw_" + sha3_256(
            (tenant_id + "\0" + self._product_id.value + "\0" + idempotency_key).encode("utf-8")
        ).hexdigest()[:32]
        item = TenantModuleWorkItem.create(
            tenant_id=tenant_id, title=title, description=description, kind=kind,
            priority=priority, created_by_principal_id=principal_id, due_at=due_at,
            source_type=source_type, source_id=source_id, now=now,
        )
        return self._registry.create_or_replay(
            replace(item, work_item_id=stable_id), idempotency_key=idempotency_key,
            session=session,
        )

    def complete(
        self, *, tenant_id: str, work_item_id: str, completion_note: str,
        now: datetime, session: Any,
    ) -> TenantModuleWorkItem:
        self._require_product(tenant_id, session)
        return self._registry.complete(
            tenant_id=tenant_id, work_item_id=work_item_id,
            completion_note=completion_note, now=now, session=session,
        )


__all__ = ["TenantModuleWorkspaceError", "TenantModuleWorkspaceService"]
