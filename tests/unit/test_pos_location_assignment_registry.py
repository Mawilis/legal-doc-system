from tools.eos.saas.billing.pos_location_assignment_registry import (
    POSLocationAssignmentRegistry, POSLocationAssignmentRegistryError,
)


def test_registry_exposes_transaction_bound_issue_resolve_and_revoke():
    assert callable(POSLocationAssignmentRegistry.ensure_indexes)
    assert callable(POSLocationAssignmentRegistry.issue)
    assert callable(POSLocationAssignmentRegistry.resolve)
    assert callable(POSLocationAssignmentRegistry.revoke)


def test_registry_requires_caller_owned_active_transaction():
    class NoTransaction:
        def in_transaction(self):
            return False

    try:
        POSLocationAssignmentRegistry.resolve("t", "l", "p", object(), session=NoTransaction())
    except POSLocationAssignmentRegistryError as error:
        assert str(error) == "POS_LOCATION_LIVE_CALLER_SESSION_REQUIRED"
    else:
        raise AssertionError("registry must reject absent caller transaction")
