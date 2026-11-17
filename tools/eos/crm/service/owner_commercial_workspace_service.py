"""TITLE: WILSY OS CRM Owner Commercial Workspace Service
VERSION: v1.3.0-INDEPENDENT-CRM-CORE-ADMISSION
AUTHORITY: WILSY OS Python EOS CRM source service.
EPITOME: Enforce independent CRM Core subscription entitlement and tenant-exact owner work
         reads, creation, completion and canonical work-detail readback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/crm/service/owner_commercial_workspace_service.py
COLLABORATION / OWNERSHIP: CRM source domain, owner work registry and
         authenticated owner commercial workspace router.
CERTIFICATION / UPDATE DATE: 2026-11-17
CHANGELOG: v1.3.0-INDEPENDENT-CRM-CORE-ADMISSION separates CRM work
           admission from the unrelated Legal product entitlement and uses the
           canonical CRM Core resolver in the caller-owned session. Founder
           subscription term alone cannot grant CRM Core or alter stored
           subscription features; missing/ambiguous CRM evidence fails closed.
CHANGELOG: v1.2.0-ENTITLED-AUDITED-WORK-EDIT routes existing-tenant
           source edits and revision history through the same mandatory active
           CRM subscription/entitlement gate; HTTP owns separate read/edit IAM,
           registry owns exact CAS, audit and caller-owned transaction.
CHANGELOG: v1.1.0-TENANT-SCOPED-WORK-DETAIL-READ adds a strictly tenant-scoped,
           entitlement-gated work item read for existing and completed work.
           Existing source create, complete and queue behavior is unchanged.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2; ISO 27001.
SECURITY / PRIVACY POSTURE: No IAM grants, credentials or additional PII.
TENANT BOUNDARY: Every record lookup scopes tenant_id before revealing existence.
AUTHORITY BOUNDARY: HTTP IAM checks precede the service; subscription admission
                    and source registry remain mandatory; no new command authority.
TRANSACTION / IDEMPOTENCY BOUNDARY: Caller-owned Mongo session; read-only
                                   addition, no new idempotency semantics.
FINANCIAL AUTHORITY BOUNDARY: No financial execution, Kennel EOS exclusively.
FAIL-CLOSED POSTURE: Ineligible tenant, unavailable source or absent work item
                     is not converted into a successful empty work record.
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
from tools.eos.crm.domain.crm_core_entitlement import CrmCoreEntitlementState
from tools.eos.crm.service.crm_core_entitlement_resolver import (
    CrmCoreEntitlementResolverError, resolve_crm_core_entitlement,
)
from tools.eos.saas.billing.subscription_registry import SubscriptionRegistryError


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
            raise OwnerCommercialWorkspaceError("OWNER_WORK_CRM_ENTITLEMENT_DEPENDENCIES_REQUIRED")
        self._registry = registry
        self._subscriptions = subscription_collection
        self._entitlement_history = entitlement_history_collection
        self._entitlement_current = entitlement_current_collection

    def _require_entitlement(self, tenant_id: str, session: Any) -> None:
        """Require active CRM Core evidence for an already IAM-admitted tenant.

        The caller owns the transaction and exact tenant scope; the resolver
        reads canonical subscription truth inside the same session. Neither
        Legal product availability nor the perpetual Founder term independently
        authorizes CRM work. No subscription or work record is mutated.
        """
        try:
            entitlement = resolve_crm_core_entitlement(
                tenant_id, self._subscriptions, session,
            )
        except (CrmCoreEntitlementResolverError, SubscriptionRegistryError) as error:
            raise OwnerCommercialWorkspaceError("OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE") from error
        if entitlement is None:
            raise OwnerCommercialWorkspaceError("OWNER_WORK_CRM_NOT_ENTITLED")
        if (
            entitlement.tenant_id != tenant_id
            or entitlement.lifecycle_state is not CrmCoreEntitlementState.ACTIVE
        ):
            raise OwnerCommercialWorkspaceError("OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE")

    def read_work_item(
        self, *, tenant_id: str, work_item_id: str, session: Any,
    ) -> OwnerCommercialWorkItem:
        """Return a persisted CRM work record under exact current tenant scope.

        HTTP IAM must already permit CRM work read. The service independently
        checks active entitlement and delegates the tenant-prefixed lookup to
        the existing source registry. Completed work retains only source-stored
        completion evidence; this method does not fabricate an audit ledger,
        actor identity, or reverse a terminal transition. Caller owns the
        read transaction; no mutation or idempotency key is involved.
        """
        self._require_entitlement(tenant_id, session)
        return self._registry.get(
            tenant_id=tenant_id, work_item_id=work_item_id, session=session,
        )

    def daily_queue(self, *, tenant_id: str, now: datetime, session: Any):
        self._require_entitlement(tenant_id, session)
        return self._registry.daily_queue(
            tenant_id=tenant_id, now=now, session=session,
        )

    def revise(
        self, *, tenant_id: str, work_item_id: str,
        actor_principal_id: str, title: str, description: str,
        priority: OwnerWorkPriority, due_at: datetime | None,
        expected_updated_at: datetime, idempotency_key: str,
        now: datetime, session: Any,
    ) -> OwnerCommercialWorkItem:
        """Revise one active commercial task under current CRM entitlement.

        HTTP must independently authorize the exact CRM edit permission and
        authenticated actor. The registry owns tenant CAS, idempotent replay,
        immutable edit history, and atomic Mongo writes. No assignment,
        inferred history, cross-tenant or financial authority is established.
        """
        self._require_entitlement(tenant_id, session)
        return self._registry.revise(
            tenant_id=tenant_id, work_item_id=work_item_id,
            actor_principal_id=actor_principal_id, title=title,
            description=description, priority=priority, due_at=due_at,
            expected_updated_at=expected_updated_at,
            idempotency_key=idempotency_key, now=now, session=session,
        )

    def revision_history(
        self, *, tenant_id: str, work_item_id: str,
        session: Any,
    ) -> tuple[dict[str, object], ...]:
        """Read persisted edit evidence for one own-tenant CRM work record.

        HTTP must independently authorize the CRM work-item read permission.
        No unrecorded legacy events are fabricated, and caller owns the read
        transaction. Neither role assignment nor financial authority changes.
        """
        self._require_entitlement(tenant_id, session)
        return self._registry.revision_history(
            tenant_id=tenant_id, work_item_id=work_item_id, session=session,
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

# ARTIFACT: tools/eos/crm/service/owner_commercial_workspace_service.py
# VERSION: v1.3.0-INDEPENDENT-CRM-CORE-ADMISSION
# AUTHORITY BOUNDARY: Existing CRM HTTP IAM, entitlement and tenant-owned registry.
# TENANT POSTURE: Exact tenant lookup; foreign record existence is not disclosed.
# FAIL-CLOSED POSTURE: Denied, unavailable and absent source records remain explicit.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
