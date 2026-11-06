"""EOS orchestration for the tenant owner's commercial work queue.

HTTP/IAM admission occurs before this service. This service independently
requires exact active crm.core subscription truth before exposing or mutating
the commercial workspace. It does not read or mutate Legal matters.
"""
from __future__ import annotations

from datetime import datetime
from dataclasses import replace
from hashlib import sha3_256
from typing import Any

from tools.eos.crm.domain.owner_commercial_work_item import (
    OwnerCommercialWorkItem, OwnerWorkKind, OwnerWorkPriority,
)
from tools.eos.crm.persistence.owner_commercial_work_registry import (
    OwnerCommercialWorkRegistry,
)
from tools.eos.saas.entitlement.legal_commercial_context_projection import (
    LegalCommercialContextProjectionError, resolve_legal_commercial_context,
)


class OwnerCommercialWorkspaceError(RuntimeError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class OwnerCommercialWorkspaceService:
    """Compose active CRM entitlement with tenant-owned commercial work."""

    __slots__ = ("_registry", "_subscriptions", "_entitlement_history", "_entitlement_current")

    def __init__(
        self, registry: OwnerCommercialWorkRegistry, subscription_collection: Any,
        entitlement_history_collection: Any, entitlement_current_collection: Any,
    ) -> None:
        if not isinstance(registry, OwnerCommercialWorkRegistry):
            raise OwnerCommercialWorkspaceError("OWNER_WORK_REGISTRY_REQUIRED")
        if any(value is None for value in (
            subscription_collection, entitlement_history_collection,
            entitlement_current_collection,
        )):
            raise OwnerCommercialWorkspaceError("OWNER_WORK_LEGAL_ENTITLEMENT_DEPENDENCIES_REQUIRED")
        self._registry = registry
        self._subscriptions = subscription_collection
        self._entitlement_history = entitlement_history_collection
        self._entitlement_current = entitlement_current_collection

    def _require_entitlement(self, tenant_id: str, session: Any) -> None:
        try:
            context = resolve_legal_commercial_context(
                tenant_id, self._subscriptions, self._entitlement_history,
                self._entitlement_current, session=session,
            )
        except LegalCommercialContextProjectionError as error:
            raise OwnerCommercialWorkspaceError("OWNER_WORK_LEGAL_ENTITLEMENT_UNAVAILABLE") from error
        if context.tenant_id != tenant_id or context.product_available is not True or context.subscription_status is None:
            raise OwnerCommercialWorkspaceError("OWNER_WORK_LEGAL_NOT_ENTITLED")

    def daily_queue(self, *, tenant_id: str, now: datetime, session: Any):
        self._require_entitlement(tenant_id, session)
        return self._registry.daily_queue(
            tenant_id=tenant_id, now=now, session=session,
        )

    def complete(
        self, *, tenant_id: str, work_item_id: str, completion_note: str,
        now: datetime, session: Any,
    ) -> OwnerCommercialWorkItem:
        self._require_entitlement(tenant_id, session)
        return self._registry.complete(
            tenant_id=tenant_id, work_item_id=work_item_id,
            completion_note=completion_note, now=now, session=session,
        )

    def create(
        self, *, tenant_id: str, principal_id: str, title: str,
        description: str, kind: OwnerWorkKind, priority: OwnerWorkPriority,
        due_at: datetime | None, source_type: str | None, source_id: str | None,
        idempotency_key: str, now: datetime, session: Any,
    ) -> OwnerCommercialWorkItem:
        self._require_entitlement(tenant_id, session)
        if not isinstance(idempotency_key, str) or not idempotency_key or idempotency_key != idempotency_key.strip():
            raise OwnerCommercialWorkspaceError("OWNER_WORK_IDEMPOTENCY_KEY_INVALID")
        stable_id = "owk_" + sha3_256(
            (tenant_id + "\\0" + idempotency_key).encode("utf-8")
        ).hexdigest()[:32]
        item = OwnerCommercialWorkItem.create(
            tenant_id=tenant_id, title=title, description=description,
            kind=kind, priority=priority, owner_principal_id=principal_id,
            due_at=due_at, source_type=source_type, source_id=source_id, now=now,
        )
        # A retry with the same tenant/key reconstructs the identical domain
        # value, allowing the registry fingerprint to prove exact replay.
        item = replace(item, work_item_id=stable_id)
        return self._registry.create_or_replay(
            item, idempotency_key=idempotency_key, session=session,
        )


__all__ = ["OwnerCommercialWorkspaceError", "OwnerCommercialWorkspaceService"]
