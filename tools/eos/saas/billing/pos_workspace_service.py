"""Authenticated-context POS commercial workspace service.

The caller supplies authenticated principal/tenant context and a requested
location selector. This service independently resolves active POS entitlement
and the principal's durable location assignment in the caller transaction
before every read or command. The location selector never proves authority.
"""
from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

from tools.eos.saas.domain.pos_commercial import (
    POSLineItem, POSSale, POSStatus, POSTenderType,
)
from tools.eos.saas.domain.pos_location_assignment import POSLocationAssignmentStatus
from tools.eos.saas.billing.pos_commercial_registry import POSSaleRegistry
from tools.eos.saas.billing.pos_commercial_evidence_registry import (
    POSCommercialEvidenceRegistry,
)
from tools.eos.saas.billing.pos_location_assignment_registry import (
    POSLocationAssignmentRegistry, POSLocationAssignmentNotFound,
)
from tools.eos.saas.billing.pos_commercial_orchestration import (
    create_tender_intent, record_cash_tender, create_return, create_refund_intent,
)
from tools.eos.saas.entitlement.product_catalogue import TenantProductId
from tools.eos.saas.entitlement.tenant_product_entitlement_composer import derive_tenant_product_entitlement_id
from tools.eos.saas.domain.tenant_product_entitlement import TenantProductEntitlementState
from tools.eos.saas.entitlement.tenant_product_entitlement_registry import (
    get_current, TenantProductEntitlementRegistryError,
    TenantProductEntitlementRegistryNotFoundError,
)


class POSWorkspaceServiceError(RuntimeError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class POSWorkspaceService:
    """Compose exact POS entitlement, location authority and durable M9 evidence."""

    __slots__ = (
        "_sales", "_evidence", "_capacity", "_entitlement_history", "_entitlement_current",
        "_location_current",
    )

    def __init__(self, *, sales_collection: Any, evidence_collection: Any,
                 capacity_collection: Any, entitlement_history_collection: Any,
                 entitlement_current_collection: Any,
                 location_assignment_current_collection: Any):
        dependencies = (
            sales_collection, evidence_collection, capacity_collection,
            entitlement_history_collection, entitlement_current_collection,
            location_assignment_current_collection,
        )
        if any(value is None for value in dependencies):
            raise POSWorkspaceServiceError("POS_WORKSPACE_DEPENDENCIES_REQUIRED")
        self._sales = sales_collection
        self._evidence = evidence_collection
        self._capacity = capacity_collection
        self._entitlement_history = entitlement_history_collection
        self._entitlement_current = entitlement_current_collection
        self._location_current = location_assignment_current_collection

    def _admit(self, *, tenant_id: str, principal_id: str, location_id: str, session: Any):
        if session is None or not callable(getattr(session, "in_transaction", None)) or session.in_transaction() is not True:
            raise POSWorkspaceServiceError("POS_WORKSPACE_ACTIVE_TRANSACTION_REQUIRED")
        try:
            entitlement_id = derive_tenant_product_entitlement_id(tenant_id, TenantProductId.POS)
            entitlement = get_current(
                tenant_id, entitlement_id, self._entitlement_history,
                self._entitlement_current, session=session,
            )
        except TenantProductEntitlementRegistryNotFoundError as error:
            raise POSWorkspaceServiceError("POS_PRODUCT_NOT_ENTITLED") from error
        except (TenantProductEntitlementRegistryError, ValueError, TypeError) as error:
            raise POSWorkspaceServiceError("POS_ENTITLEMENT_AUTHORITY_UNAVAILABLE") from error
        if (
            entitlement.tenant_id != tenant_id
            or entitlement.product_id is not TenantProductId.POS
            or entitlement.lifecycle_state is not TenantProductEntitlementState.ACTIVE
        ):
            raise POSWorkspaceServiceError("POS_PRODUCT_NOT_ENTITLED")
        try:
            assignment = POSLocationAssignmentRegistry.resolve(
                tenant_id, location_id, principal_id,
                self._location_current, session=session,
            )
        except POSLocationAssignmentNotFound as error:
            raise POSWorkspaceServiceError("POS_LOCATION_ACCESS_DENIED") from error
        except Exception as error:
            raise POSWorkspaceServiceError("POS_LOCATION_AUTHORITY_UNAVAILABLE") from error
        if assignment.status is not POSLocationAssignmentStatus.ACTIVE:
            raise POSWorkspaceServiceError("POS_LOCATION_ACCESS_DENIED")
        return entitlement, assignment

    def create_sale(self, *, tenant_id: str, principal_id: str, location_id: str,
                    sale_id: str, currency: str, lines: tuple[POSLineItem, ...],
                    idempotency_key: str, session: Any) -> POSSale:
        self._admit(tenant_id=tenant_id, principal_id=principal_id, location_id=location_id, session=session)
        sale = POSSale(
            tenant_id, location_id, sale_id, currency, tuple(lines),
            POSStatus.COMPLETED_COMMERCIAL, idempotency_key,
        )
        try:
            return POSSaleRegistry.create(sale, self._sales, session=session)
        except Exception as error:
            raise POSWorkspaceServiceError("POS_SALE_PERSISTENCE_OR_REPLAY_CONFLICT") from error

    def _sale(self, *, tenant_id: str, principal_id: str, location_id: str, sale_id: str, session: Any) -> POSSale:
        self._admit(tenant_id=tenant_id, principal_id=principal_id, location_id=location_id, session=session)
        try:
            return POSSaleRegistry.get(tenant_id, location_id, sale_id, self._sales, session=session)
        except Exception as error:
            raise POSWorkspaceServiceError("POS_SALE_NOT_FOUND_OR_CORRUPT") from error

    def read_sale(self, *, tenant_id: str, principal_id: str, location_id: str, sale_id: str, session: Any) -> dict:
        sale = self._sale(tenant_id=tenant_id, principal_id=principal_id, location_id=location_id, sale_id=sale_id, session=session)
        try:
            evidence = POSCommercialEvidenceRegistry.list_sale_evidence(
                tenant_id=tenant_id, location_id=location_id, sale_id=sale_id,
                collection=self._evidence, session=session,
            )
        except Exception as error:
            raise POSWorkspaceServiceError("POS_EVIDENCE_READ_UNAVAILABLE") from error
        return {
            "tenant_id": tenant_id, "location_id": location_id,
            "sale": sale.to_dict(), "commercial_evidence": list(evidence),
            "financial_state": "NOT_ASSERTED_BY_POS",
        }

    def record_tender(self, *, tenant_id: str, principal_id: str, location_id: str,
                      sale_id: str, tender_type: POSTenderType, amount_minor: int,
                      idempotency_key: str, evidence_id: str, session: Any) -> dict:
        sale = self._sale(tenant_id=tenant_id, principal_id=principal_id, location_id=location_id, sale_id=sale_id, session=session)
        intent = create_tender_intent(sale, tender_type, amount_minor, idempotency_key)
        return POSCommercialEvidenceRegistry.record_evidence(
            sale=sale, evidence=intent, evidence_id=evidence_id,
            idempotency_key=idempotency_key, collection=self._evidence, session=session,
        )

    def record_cash(self, *, tenant_id: str, principal_id: str, location_id: str,
                    sale_id: str, cash_received_minor: int, idempotency_key: str,
                    evidence_id: str, session: Any, occurred_at: datetime | None = None) -> dict:
        sale = self._sale(tenant_id=tenant_id, principal_id=principal_id, location_id=location_id, sale_id=sale_id, session=session)
        cash = record_cash_tender(
            sale, cash_received_minor, principal_id,
            (occurred_at or datetime.now(timezone.utc)).isoformat(),
        )
        return POSCommercialEvidenceRegistry.record_evidence(
            sale=sale, evidence=cash, evidence_id=evidence_id,
            idempotency_key=idempotency_key, collection=self._evidence, session=session,
        )

    def create_return(self, *, tenant_id: str, principal_id: str, location_id: str,
                      sale_id: str, sku: str, quantity: int, reason: str,
                      return_id: str, idempotency_key: str, session: Any) -> dict:
        sale = self._sale(tenant_id=tenant_id, principal_id=principal_id, location_id=location_id, sale_id=sale_id, session=session)
        history = POSCommercialEvidenceRegistry.list_sale_evidence(
            tenant_id=tenant_id, location_id=location_id, sale_id=sale_id,
            collection=self._evidence, session=session,
        )
        prior_returns = tuple(
            SimpleNamespace(**{"sku": row["evidence"]["sku"], "quantity": row["evidence"]["quantity"]})
            for row in history if row["evidence_type"] == "RETURN_INTENT"
        )
        intent = create_return(sale, sku, quantity, reason, return_id, idempotency_key, prior_returns)
        return POSCommercialEvidenceRegistry.record_evidence(
            sale=sale, evidence=intent, evidence_id=return_id,
            idempotency_key=idempotency_key, collection=self._evidence, session=session,
        )

    def create_refund(self, *, tenant_id: str, principal_id: str, location_id: str,
                      sale_id: str, amount_minor: int, basis: str, refund_intent_id: str,
                      idempotency_key: str, session: Any) -> dict:
        sale = self._sale(tenant_id=tenant_id, principal_id=principal_id, location_id=location_id, sale_id=sale_id, session=session)
        intent = create_refund_intent(sale, amount_minor, basis, refund_intent_id, idempotency_key)
        return POSCommercialEvidenceRegistry.record_evidence(
            sale=sale, evidence=intent, evidence_id=refund_intent_id,
            idempotency_key=idempotency_key, collection=self._evidence, session=session,
        )


__all__ = ["POSWorkspaceService", "POSWorkspaceServiceError"]
