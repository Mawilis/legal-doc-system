"""WILSY OS — M11E2D5R3A direct settlement-bridge certificate.
TITLE: Settlement Observation to Platform Settlement Evidence Certificate
VERSION: v1.1.0-M11E2D5R3A-DIRECT-R2
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Durable observation provenance and full-settlement firewall certificate.
ABSOLUTE CANONICAL PATH: tests/unit/test_settlement_observation_to_platform_settlement_evidence.py
COLLABORATION / OWNERSHIP: Kennel EOS settlement-evidence certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.1.0-M11E2D5R3A-DIRECT-R2 completes direct bridge behavior coverage.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: opaque synthetic references; no provider calls or credentials.
TENANT BOUNDARY: every bridge lookup and assertion is tenant-scoped.
AUTHORITY BOUNDARY: durable observation and execution registries only.
FINANCIAL AUTHORITY BOUNDARY: evidence derivation only; no paid or settled mutation.
TRANSACTION BOUNDARY: caller-owned active Mongo transaction is mandatory.
FAIL-CLOSED DECLARATION: missing session, drift, corruption, and partial settlement reject.
"""
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock, patch
import pytest
from tools.eos.kennel.domain.financial_execution import FinancialExecutionStatus
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformExecutionStatus
from tools.eos.kennel.orchestration.settlement_observation_to_platform_settlement_evidence import SettlementObservationBridgeError, bridge_settlement_observation_to_platform_evidence

NOW = datetime(2026, 9, 7, 10, 0, tzinfo=timezone.utc)
SESSION = Mock(in_transaction=True)

def _records(amount=100, source_id="gt", source_fp="g" * 128):
    observation = SimpleNamespace(tenant_id="tenant-a", observation_id="obs-1", execution_truth_id="gt", provider_name="provider-a", provider_execution_reference="exec-1", settlement_reference="settle-1", provider_settlement_evidence_reference="evidence-1", settled_amount_minor=amount, currency="ZAR", payment_destination_reference="dest-1", settled_at=NOW, fingerprint="f" * 128)
    generic = SimpleNamespace(tenant_id="tenant-a", execution_fact_id="gt", fingerprint="g" * 128, execution_status=FinancialExecutionStatus.EXECUTED, provider="provider-a", provider_execution_reference="exec-1", executed_amount_minor=100, currency="ZAR", payment_destination_reference="dest-1")
    platform = SimpleNamespace(tenant_id="tenant-a", execution_status=PlatformExecutionStatus.EXECUTED, source_financial_execution_truth_id=source_id, source_financial_execution_truth_fingerprint=source_fp, executed_amount_minor=100, provider="provider-a", provider_execution_reference="exec-1", currency="ZAR", payment_destination_reference="dest-1", platform_invoice_id="inv-1", execution_request_id="req-1", execution_command_id="cmd-1", release_authorization_id="auth-1")
    return observation, generic, platform

def _run(observation, generic, platform):
    base = "tools.eos.kennel.orchestration.settlement_observation_to_platform_settlement_evidence."
    with patch(base + "FinancialSettlementObservationRegistry.get", return_value=observation) as obs_get, patch(base + "FinancialExecutionFactRegistry.get", return_value=generic) as gen_get, patch(base + "PlatformBillingFinancialExecutionTruthRegistry.get", return_value=platform) as plat_get, patch(base + "PlatformBillingFinancialSettlementEvidenceRegistry.create", side_effect=lambda value, *_a, **_k: value) as create:
        result = bridge_settlement_observation_to_platform_evidence("tenant-a", "obs-1", "pt-1", observation_collection=Mock(), generic_truth_collection=Mock(), platform_truth_collection=Mock(), evidence_collection=Mock(), session=SESSION, created_at=NOW)
    obs_get.assert_called_once(); gen_get.assert_called_once(); plat_get.assert_called_once(); create.assert_called_once()
    return result

def test_d5_requires_caller_owned_transaction_before_any_authority_read():
    with pytest.raises(SettlementObservationBridgeError, match="ACTIVE_SESSION_REQUIRED"):
        bridge_settlement_observation_to_platform_evidence("t", "o", "p", observation_collection=Mock(), generic_truth_collection=Mock(), platform_truth_collection=Mock(), evidence_collection=Mock(), created_at=NOW, session=None)

def test_d5_reads_durable_observation_and_never_accepts_in_memory_authority():
    with patch("tools.eos.kennel.orchestration.settlement_observation_to_platform_settlement_evidence.FinancialSettlementObservationRegistry.get") as observation_get:
        with pytest.raises(Exception):
            bridge_settlement_observation_to_platform_evidence("t", "o", "p", observation_collection=Mock(), generic_truth_collection=Mock(), platform_truth_collection=Mock(), evidence_collection=Mock(), created_at=NOW, session=SESSION)
        observation_get.assert_called_once()

def test_d5_full_durable_chain_preserves_provenance_and_settlement_facts():
    observation, generic, platform = _records(); evidence = _run(observation, generic, platform)
    assert evidence.source_financial_settlement_observation_id == observation.observation_id
    assert evidence.source_financial_settlement_observation_fingerprint == observation.fingerprint
    assert (evidence.settlement_reference, evidence.provider_settlement_evidence_reference, evidence.settled_amount_minor, evidence.currency, evidence.settled_at) == ("settle-1", "evidence-1", 100, "ZAR", NOW)
    assert observation.execution_truth_id == generic.execution_fact_id == platform.source_financial_execution_truth_id
    assert generic.fingerprint == platform.source_financial_execution_truth_fingerprint

@pytest.mark.parametrize("source_id,source_fp", [("wrong", "g" * 128), ("gt", "x" * 128)])
def test_d5_wrong_source_identity_or_fingerprint_fails_closed(source_id, source_fp):
    observation, generic, platform = _records(source_id=source_id, source_fp=source_fp)
    with pytest.raises(SettlementObservationBridgeError, match="GENERIC_PLATFORM_PROVENANCE_MISMATCH"):
        _run(observation, generic, platform)

@pytest.mark.parametrize("amount", [99, 101])
def test_d5_partial_or_over_settlement_fails_closed_without_persistence(amount):
    observation, generic, platform = _records(amount=amount)
    with patch("tools.eos.kennel.orchestration.settlement_observation_to_platform_settlement_evidence.PlatformBillingFinancialSettlementEvidenceRegistry.create") as create:
        with pytest.raises(SettlementObservationBridgeError): _run(observation, generic, platform)
        create.assert_not_called()

def test_d5_identical_replay_has_identical_evidence_identity():
    observation, generic, platform = _records()
    assert _run(observation, generic, platform).fingerprint == _run(observation, generic, platform).fingerprint

def test_d5_corrupt_durable_settlement_observation_rejects_before_downstream_authority():
    base = "tools.eos.kennel.orchestration.settlement_observation_to_platform_settlement_evidence."
    with patch(base + "FinancialSettlementObservationRegistry.get", side_effect=RuntimeError("M11E2D4_SETTLEMENT_OBSERVATION_INVALID")) as observation_get, patch(base + "FinancialExecutionFactRegistry.get") as generic_get:
        with pytest.raises(RuntimeError, match="SETTLEMENT_OBSERVATION_INVALID"):
            bridge_settlement_observation_to_platform_evidence("tenant-a", "obs-1", "pt-1", observation_collection=Mock(), generic_truth_collection=Mock(), platform_truth_collection=Mock(), evidence_collection=Mock(), session=SESSION, created_at=NOW)
    observation_get.assert_called_once()
    generic_get.assert_not_called()

# ARTIFACT: tests/unit/test_settlement_observation_to_platform_settlement_evidence.py
# VERSION: v1.1.0-M11E2D5R3A-DIRECT-R2
# AUTHORITY BOUNDARY: certificate only; no financial authority.
# TENANT POSTURE: tenant-scoped synthetic durable fixtures.
# FAIL-CLOSED POSTURE: authority drift and non-full settlement reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
