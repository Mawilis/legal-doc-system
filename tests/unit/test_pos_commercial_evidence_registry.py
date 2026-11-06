from tools.eos.saas.billing.pos_commercial_evidence_registry import (
    POSCommercialEvidenceRegistry, POSCommercialEvidenceRegistryError,
)


def test_evidence_registry_exposes_durable_append_only_operations():
    assert callable(POSCommercialEvidenceRegistry.ensure_indexes)
    assert callable(POSCommercialEvidenceRegistry.record_evidence)
    assert callable(POSCommercialEvidenceRegistry.list_sale_evidence)


def test_evidence_registry_requires_caller_owned_active_transaction():
    class NoTransaction:
        def in_transaction(self):
            return False

    try:
        POSCommercialEvidenceRegistry.list_sale_evidence(
            tenant_id="t", location_id="l", sale_id="s",
            collection=object(), session=NoTransaction(),
        )
    except POSCommercialEvidenceRegistryError as error:
        assert str(error) == "POS_EVIDENCE_ACTIVE_TRANSACTION_REQUIRED"
    else:
        raise AssertionError("evidence registry must reject absent caller transaction")
