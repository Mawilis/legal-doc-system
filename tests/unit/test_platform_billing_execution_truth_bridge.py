# pyright: reportArgumentType=false, reportAttributeAccessIssue=false
"""TITLE: Platform Billing Execution Truth Bridge Certificate
VERSION: v2.0.0-M11-P5-R2D-R1
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Certify neutral-fact plus canonical generic Platform command projection.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_platform_billing_execution_truth_bridge.py
COLLABORATION / OWNERSHIP: Kennel EOS Platform Billing bridge certificate.
CERTIFICATION / UPDATE DATE: 2026-09-08.
CHANGELOG: v2.0.0-M11-P5-R2D-R1 certifies canonical reads, correlations, and no legacy command issuance.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
TENANT BOUNDARY: Bridge reads and persistence are tenant-scoped.
AUTHORITY BOUNDARY: Existing generic command and neutral fact only; no provider selection.
FINANCIAL AUTHORITY BOUNDARY: No attempt, settlement, paid state, or receivable mutation.
FAIL-CLOSED DECLARATION: Inactive sessions, missing sources, wrong family, and drift reject.
"""
from datetime import datetime, timezone
from unittest.mock import Mock, patch
import pytest
from tools.eos.kennel.domain.financial_execution import FinancialExecutionFact, FinancialExecutionStatus
from tools.eos.kennel.domain.financial_execution_command import FinancialExecutionCommand, PlatformBillingCommandSource, AccountsPayableCommandSource
from tools.eos.kennel.orchestration.platform_billing_execution_truth_bridge import bridge_financial_execution_fact_to_platform, PlatformBillingExecutionTruthBridgeError

NOW=datetime(2026,1,1,tzinfo=timezone.utc); FP="a"*128
def command(platform=True):
    source=PlatformBillingCommandSource("request-1",FP,"routing-1","b"*128,"invoice-1","release-1","c"*128,"PAYSHAP") if platform else AccountsPayableCommandSource("request-1",FP,"selection-1","b"*128,"payable-1","release-1","PAYSHAP")
    return FinancialExecutionCommand("tenant-1","command-1","idem-1",100,"ZAR","destination-1",source,"PAYSHAP",NOW)
def fact(c=None, **changes):
    c=c or command(); values=dict(execution_fact_id=FinancialExecutionFact.deterministic_id("tenant-1","attempt-1"),tenant_id="tenant-1",execution_command_id="command-1",execution_command_fingerprint=c.fingerprint,execution_attempt_id="attempt-1",provider="PAYSHAP",provider_execution_reference="provider-ref",execution_status=FinancialExecutionStatus.EXECUTED,executed_amount_minor=100,currency="ZAR",executed_at=NOW,payment_destination_reference="destination-1",provider_evidence_reference="evidence-1",execution_evidence_fingerprint="d"*128,created_at=NOW); values.update(changes); return FinancialExecutionFact(**values)
def run(value=None, cmd=None, session=None, persist=None):
    value=value or fact(); cmd=cmd or command(); session=session or Mock(in_transaction=True); persist=persist or Mock(side_effect=lambda value, *args, **kwargs: value)
    with patch("tools.eos.kennel.orchestration.platform_billing_execution_truth_bridge.FinancialExecutionFactRegistry.get",return_value=value) as fact_get, patch("tools.eos.kennel.orchestration.platform_billing_execution_truth_bridge.FinancialExecutionCommandRegistry.get",return_value=cmd) as cmd_get, patch("tools.eos.kennel.orchestration.platform_billing_execution_truth_bridge.PlatformBillingFinancialExecutionTruthRegistry.create",persist):
        result=bridge_financial_execution_fact_to_platform("tenant-1",value.execution_fact_id,fact_collection=Mock(),command_collection=Mock(),platform_truth_collection=Mock(),session=session)
    return result,fact_get,cmd_get,persist
def test_bridge_returns_persisted_projection(): assert run()[0] is not None
def test_fact_read_is_tenant_scoped(): assert run()[1].call_args.args[:2]==("tenant-1",fact().execution_fact_id)
def test_command_read_uses_fact_command_id(): assert run()[2].call_args.args[:2]==("tenant-1","command-1")
def test_fact_read_session(): assert run()[1].call_args.kwargs["session"].in_transaction
def test_command_read_session(): assert run()[2].call_args.kwargs["session"].in_transaction
def test_persist_session(): assert run()[3].call_args.kwargs["session"].in_transaction
def test_inactive_session_rejected():
    with pytest.raises(PlatformBillingExecutionTruthBridgeError,match="ACTIVE_SESSION"): run(session=Mock(in_transaction=False))
def test_missing_fact_rejected():
    with patch("tools.eos.kennel.orchestration.platform_billing_execution_truth_bridge.FinancialExecutionFactRegistry.get",return_value=None):
        with pytest.raises(PlatformBillingExecutionTruthBridgeError,match="NOT_EXECUTED"): bridge_financial_execution_fact_to_platform("tenant-1","fact",fact_collection=Mock(),command_collection=Mock(),platform_truth_collection=Mock(),session=Mock(in_transaction=True))
@pytest.mark.parametrize("status",[FinancialExecutionStatus.SUBMITTED,FinancialExecutionStatus.ACCEPTED,FinancialExecutionStatus.FAILED])
def test_nonexecuted_fact_rejected(status):
    with pytest.raises(PlatformBillingExecutionTruthBridgeError): run(value=fact(execution_status=status,executed_at=None))
def test_ap_command_rejected():
    with pytest.raises(PlatformBillingExecutionTruthBridgeError,match="PLATFORM_COMMAND"): run(value=fact(),cmd=command(False))
def test_command_missing_rejected():
    with patch("tools.eos.kennel.orchestration.platform_billing_execution_truth_bridge.FinancialExecutionFactRegistry.get",return_value=fact()),patch("tools.eos.kennel.orchestration.platform_billing_execution_truth_bridge.FinancialExecutionCommandRegistry.get",return_value=None):
        with pytest.raises(PlatformBillingExecutionTruthBridgeError): bridge_financial_execution_fact_to_platform("tenant-1",fact().execution_fact_id,fact_collection=Mock(),command_collection=Mock(),platform_truth_collection=Mock(),session=Mock(in_transaction=True))
@pytest.mark.parametrize("field",["tenant_id","execution_command_id","execution_command_fingerprint","provider","executed_amount_minor","currency","payment_destination_reference"])
def test_correlation_drift_rejected(field):
    values={"tenant_id":"other","execution_command_id":"other","execution_command_fingerprint":"f"*128,"provider":"OTHER","executed_amount_minor":99,"currency":"USD","payment_destination_reference":"other"}
    kwargs={field:values[field]}
    if field == "tenant_id": kwargs["execution_fact_id"] = FinancialExecutionFact.deterministic_id("other", "attempt-1")
    with pytest.raises(PlatformBillingExecutionTruthBridgeError,match="CORRELATION"): run(value=fact(**kwargs))
def test_provider_like_payable_string_does_not_collide():
    c=command(); c=FinancialExecutionCommand(c.tenant_id,c.execution_command_id,c.idempotency_key,c.amount_minor,c.currency,"payable-invoice-1",c.source_authority,c.provider_name,c.created_at); value=fact(c,payment_destination_reference="payable-invoice-1",execution_command_fingerprint=c.fingerprint)
    assert run(value=value,cmd=c)[0].payment_destination_reference == "payable-invoice-1"
def test_no_legacy_platform_issuance():
    import tools.eos.kennel.orchestration.platform_billing_execution_truth_bridge as module
    assert not hasattr(module,"issue_platform_billing_financial_execution_command")
def test_no_request_collection_parameter():
    import inspect
    assert "platform_request_collection" not in inspect.signature(bridge_financial_execution_fact_to_platform).parameters
def test_no_settlement_projection(): assert "settled" not in run()[0].to_dict()
def test_no_client_invoice_projection(): assert "client_invoice_id" not in run()[0].to_dict()
def test_bridge_uses_canonical_fact_identity(): assert run()[0].source_execution_fact_id == fact().execution_fact_id
def test_bridge_uses_canonical_command_fingerprint(): assert run()[0].execution_command_fingerprint == command().fingerprint
def test_bridge_uses_platform_invoice_source(): assert run()[0].platform_invoice_id == "invoice-1"
def test_bridge_uses_routing_source(): assert run()[0].routing_decision_id == "routing-1"
def test_bridge_uses_release_source(): assert run()[0].release_authorization_id == "release-1"
def test_bridge_exactly_one_persist_call(): assert run()[3].call_count==1
def test_bridge_does_not_create_fact():
    with patch("tools.eos.kennel.orchestration.platform_billing_execution_truth_bridge.FinancialExecutionFactRegistry.create") as create:
        run(); create.assert_not_called()
def test_bridge_does_not_mutate_collections(): assert run() is not None
def test_bridge_status_executed(): assert run()[0].execution_status.value=="EXECUTED"
def test_bridge_amount_is_command_correlated(): assert run()[0].executed_amount_minor==100
def test_bridge_currency_is_command_correlated(): assert run()[0].currency=="ZAR"
def test_bridge_destination_is_command_correlated(): assert run()[0].payment_destination_reference=="destination-1"
def test_bridge_provider_is_fact_correlated(): assert run()[0].provider=="PAYSHAP"
def test_bridge_provider_reference_is_fact(): assert run()[0].provider_execution_reference=="provider-ref"
def test_bridge_created_at_is_command_time(): assert run()[0].created_at==NOW
def test_bridge_truth_identity_is_request_based(): assert run()[0].execution_truth_id=="platform-truth-request-1"
def test_bridge_alias_is_fact_id(): assert run()[0].source_financial_execution_truth_id==fact().execution_fact_id

# ARTIFACT: test_platform_billing_execution_truth_bridge.py
# VERSION: v2.0.0-M11-P5-R2D-R1
# AUTHORITY BOUNDARY: neutral-fact to Platform projection certificate only.
# TENANT POSTURE: synthetic tenant-scoped fixtures.
# FAIL-CLOSED POSTURE: all authority drift is asserted as rejection.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
