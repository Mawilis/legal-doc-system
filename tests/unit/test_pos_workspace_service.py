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
