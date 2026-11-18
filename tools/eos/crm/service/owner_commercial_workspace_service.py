"""TITLE: WILSY OS CRM Owner Commercial Workspace Service
VERSION: v1.7.0-DIRECT-SAVED-DRAFT-CREATION
AUTHORITY: WILSY OS Python EOS CRM source service.
EPITOME: Enforce independent customer CRM Core or exact WILSY company-owner authority for tenant-exact work
         reads, creation, completion and canonical work-detail readback.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/crm/service/owner_commercial_workspace_service.py
COLLABORATION / OWNERSHIP: CRM source domain, owner work registry and
         authenticated owner commercial workspace router.
CERTIFICATION / UPDATE DATE: 2026-11-17
CHANGELOG: v1.7.0-DIRECT-SAVED-DRAFT-CREATION preserves deterministic
           create replay while admitting a direct DRAFT initial status;
           source task becomes active only on explicit audited transition.
CHANGELOG: v1.6.0-OWNER-DRAFT-PROGRESS-COMMANDS adds exact-owner
           Draft/Open/In Progress transitions and saved-draft reads through
           existing CRM commercial and IAM boundaries, without grants.
CHANGELOG: v1.5.0-OWNER-ONLY-AUDITED-CANCEL delegates exact-owner
           terminal cancellation to the CRM registry under the same CRM
           UPDATE IAM and immutable Founder/customer entitlement admission.
           Neither foreign assignments nor permanent deletion is enabled.
CHANGELOG: v1.4.0-COMPANY-OWNER-WORK-CONTINUITY preserves the existing
           WILSY company Headquarters CRM-owned task queue without inventing
           crm.core in the historical Founder subscription. The exception is
           exact WILSY company tenant plus one canonical ACTIVE Founder
           subscription classified as perpetual by the already-governed
           subscription-term policy. Existing HTTP read/create/update/complete
           IAM, exact tenant registry, CAS and audit remain mandatory; other
           tenants still require independent active CRM Core entitlement.
           Ambiguous/malformed Founder or CRM evidence rejects; no grants,
           records, subscriptions or financial authority are changed.
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

from datetime import datetime, timezone
from dataclasses import replace
from hashlib import sha3_256
from typing import Any

from tools.eos.crm.domain.owner_commercial_work_item import (
    OwnerCommercialWorkItem, OwnerWorkKind, OwnerWorkPriority, OwnerWorkStatus,
)
from tools.eos.crm.persistence.owner_commercial_work_registry import (
    OwnerCommercialWorkRegistry,
)
from tools.eos.crm.domain.crm_core_entitlement import CrmCoreEntitlementState
from tools.eos.crm.service.crm_core_entitlement_resolver import (
    CrmCoreEntitlementResolverError, resolve_crm_core_entitlement,
)
from tools.eos.saas.billing.subscription_registry import (
    SubscriptionRegistry, SubscriptionRegistryError,
)
from tools.eos.saas.billing.subscription_term_policy import (
    SubscriptionTermKind, SubscriptionTermPolicyError, evaluate_subscription_term,
)
from tools.eos.saas.domain.subscription import SubscriptionStatus
from tools.eos.auth.workspace_bootstrap_projection import WILSY_COMPANY_TENANT_ID


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
        """Verify product CRM Core or the exact company's existing owner-work plane.

        IAM must first authorize the precise task command under the caller's
        active tenant membership and business capacity. This method supplies
        only commercial admission, never permission possession. Customer tenants
        require an active crm.core subscription feature; the WILSY company's
        legacy owner-task queue instead admits its exact canonical ACTIVE
        perpetual Founder subscription without rewriting historical features.
        All reads use the caller-owned transaction, no fallback on uncertainty.
        """
        try:
            entitlement = resolve_crm_core_entitlement(
                tenant_id, self._subscriptions, session,
            )
        except (CrmCoreEntitlementResolverError, SubscriptionRegistryError) as error:
            raise OwnerCommercialWorkspaceError("OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE") from error
        if entitlement is not None:
            if (
                entitlement.tenant_id != tenant_id
                or entitlement.lifecycle_state is not CrmCoreEntitlementState.ACTIVE
            ):
                raise OwnerCommercialWorkspaceError("OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE")
            return
        if tenant_id != WILSY_COMPANY_TENANT_ID:
            raise OwnerCommercialWorkspaceError("OWNER_WORK_CRM_NOT_ENTITLED")
        try:
            subscriptions = SubscriptionRegistry.list_entities(
                tenant_id, collection=self._subscriptions, session=session,
            )
            active = tuple(
                record for record in subscriptions
                if record.status is SubscriptionStatus.ACTIVE
            )
            if len(active) != 1:
                raise OwnerCommercialWorkspaceError("OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE")
            decision = evaluate_subscription_term(
                active[0], evaluated_at=datetime.now(timezone.utc),
            )
        except (SubscriptionRegistryError, SubscriptionTermPolicyError) as error:
            raise OwnerCommercialWorkspaceError("OWNER_WORK_CRM_ENTITLEMENT_UNAVAILABLE") from error
        if (
            active[0].tenant_id != tenant_id
            or decision.kind is not SubscriptionTermKind.PERPETUAL_PLATFORM_OWNER
            or decision.eligible is not True
        ):
            raise OwnerCommercialWorkspaceError("OWNER_WORK_CRM_NOT_ENTITLED")

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

    def cancel(
        self, *, tenant_id: str, work_item_id: str,
        actor_principal_id: str, reason: str, expected_updated_at: datetime,
        idempotency_key: str, now: datetime, session: Any,
    ) -> OwnerCommercialWorkItem:
        """Cancel an owned task under CRM UPDATE IAM and commercial admission.

        Source ownership is independently enforced in the registry. The
        cancellation and immutable audit event share the caller transaction;
        absent or foreign tasks never become deletions or false successes.
        """
        self._require_entitlement(tenant_id, session)
        return self._registry.cancel(
            tenant_id=tenant_id, work_item_id=work_item_id,
            actor_principal_id=actor_principal_id, reason=reason,
            expected_updated_at=expected_updated_at,
            idempotency_key=idempotency_key, now=now, session=session,
        )

    def transition_status(
        self, *, tenant_id: str, work_item_id: str,
        actor_principal_id: str, target_status: OwnerWorkStatus,
        expected_updated_at: datetime, idempotency_key: str,
        now: datetime, session: Any,
    ) -> OwnerCommercialWorkItem:
        """Change owner task state under CRM UPDATE permission and entitlement."""
        self._require_entitlement(tenant_id, session)
        return self._registry.transition_status(
            tenant_id=tenant_id, work_item_id=work_item_id,
            actor_principal_id=actor_principal_id,
            target_status=target_status, expected_updated_at=expected_updated_at,
            idempotency_key=idempotency_key, now=now, session=session,
        )

    def drafts_for_owner(
        self, *, tenant_id: str, owner_principal_id: str, session: Any,
    ) -> tuple[dict[str, object], ...]:
        """Return only persisted drafts owned by the authenticated principal."""
        self._require_entitlement(tenant_id, session)
        return tuple(item.to_dict() for item in self._registry.drafts_for_owner(
            tenant_id=tenant_id, owner_principal_id=owner_principal_id,
            session=session,
        ))

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
        initial_status: OwnerWorkStatus = OwnerWorkStatus.OPEN,
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
            initial_status=initial_status,
        )
        # A retry with the same tenant/key reconstructs the identical domain
        # value, allowing the registry fingerprint to prove exact replay.
        item = replace(item, work_item_id=stable_id)
        return self._registry.create_or_replay(
            item, idempotency_key=idempotency_key, session=session,
        )


__all__ = ["OwnerCommercialWorkspaceError", "OwnerCommercialWorkspaceService"]

# ARTIFACT: tools/eos/crm/service/owner_commercial_workspace_service.py
# VERSION: v1.7.0-DIRECT-SAVED-DRAFT-CREATION
# AUTHORITY BOUNDARY: Existing CRM HTTP IAM, entitlement and tenant-owned registry.
# TENANT POSTURE: Exact tenant lookup; foreign record existence is not disclosed.
# FAIL-CLOSED POSTURE: Denied, unavailable and absent source records remain explicit.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
