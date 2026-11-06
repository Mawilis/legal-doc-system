import pytest

from tools.eos.saas.billing.pos_workspace_service import (
    POSWorkspaceService, POSWorkspaceServiceError,
)


def service():
    return POSWorkspaceService(
        sales_collection=object(),
        evidence_collection=object(),
        capacity_collection=object(),
        entitlement_history_collection=object(),
        entitlement_current_collection=object(),
        location_assignment_current_collection=object(),
    )


def test_pos_workspace_requires_all_durable_authority_dependencies():
    with pytest.raises(POSWorkspaceServiceError) as error:
        POSWorkspaceService(
            sales_collection=object(), evidence_collection=object(),
            capacity_collection=object(), entitlement_history_collection=object(), entitlement_current_collection=object(),
            location_assignment_current_collection=None,
        )
    assert error.value.code == "POS_WORKSPACE_DEPENDENCIES_REQUIRED"


def test_pos_workspace_rejects_missing_caller_transaction_before_business_access():
    with pytest.raises(POSWorkspaceServiceError) as error:
        service().create_sale(
            tenant_id="tenant-a", principal_id="principal-a", location_id="browser-selected-store",
            sale_id="sale-1", currency="ZAR", lines=(), idempotency_key="sale-idem",
            session=None,
        )
    assert error.value.code == "POS_WORKSPACE_LIVE_CALLER_SESSION_REQUIRED"


def test_pos_workspace_translates_invalid_cash_tender_into_validation_error(monkeypatch):
    monkeypatch.setattr(POSWorkspaceService, "_sale", lambda *args, **kwargs: object())

    def reject_insufficient_cash(*args, **kwargs):
        raise ValueError("M9_CASH_INSUFFICIENT")

    monkeypatch.setattr(
        "tools.eos.saas.billing.pos_workspace_service.record_cash_tender",
        reject_insufficient_cash,
    )
    with pytest.raises(POSWorkspaceServiceError) as error:
        service().record_cash(
            tenant_id="tenant-a",
            principal_id="principal-a",
            location_id="store-a",
            sale_id="sale-a",
            cash_received_minor=1,
            idempotency_key="cash-idem",
            evidence_id="cash-evidence",
            session=object(),
        )
    assert error.value.code == "POS_CASH_TENDER_INVALID"
