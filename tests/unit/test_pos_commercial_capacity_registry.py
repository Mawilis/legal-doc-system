from tools.eos.saas.billing.pos_commercial_capacity_registry import (
    POSCommercialCapacityRegistry, POSCommercialCapacityError,
)


def test_capacity_registry_exposes_revision_guarded_return_and_refund_reservations():
    assert callable(POSCommercialCapacityRegistry.ensure_indexes)
    assert callable(POSCommercialCapacityRegistry.reserve_return)
    assert callable(POSCommercialCapacityRegistry.reserve_refund)


def test_capacity_registry_requires_caller_owned_transaction_before_business_access():
    class NoTransaction:
        def in_transaction(self):
            return False

    try:
        POSCommercialCapacityRegistry.reserve_refund(
            sale=object(), amount_minor=1, idempotency_key="i",
            collection=object(), session=NoTransaction(),
        )
    except POSCommercialCapacityError as error:
        assert str(error) == "POS_CAPACITY_LIVE_CALLER_SESSION_REQUIRED"
    else:
        raise AssertionError("capacity registry must reject absent caller transaction")
