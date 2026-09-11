"""WILSY OS — M11E2D3R4 obsolete recorder certificate.
TITLE: Obsolete Platform Execution Recorder Fail-Closed Certificate
VERSION: v1.0.0-M11E2D3R4
AUTHORITY: Wilsy OS Core Governance / Kennel EOS
EPITOME: Proves the retired recorder cannot manufacture execution truth.
ABSOLUTE CANONICAL PATH: tests/unit/test_platform_billing_financial_execution_truth_recording.py
COLLABORATION / OWNERSHIP: Kennel EOS compatibility-boundary certificate owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11E2D3R4 adds direct fail-closed authority proof.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: no provider calls or persisted financial truth.
TENANT BOUNDARY: synthetic tenant inputs remain isolated.
AUTHORITY BOUNDARY: obsolete recorder authority is none.
FINANCIAL AUTHORITY BOUNDARY: canonical D3 bridge exclusively owns platform truth.
TRANSACTION BOUNDARY: no transaction or persistence is reached.
FAIL-CLOSED DECLARATION: caller assertions always raise before construction.
"""
from datetime import datetime, timezone
from unittest.mock import Mock
import pytest
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformExecutionStatus

def test_obsolete_recorder_fails_closed_before_authority_or_persistence():
 from tools.eos.kennel.orchestration.platform_billing_financial_execution_truth_recording import record_platform_billing_financial_execution_truth
 with pytest.raises(RuntimeError, match="M11E2D3R2_CANONICAL_RECORDING_RETIRED"):
  record_platform_billing_financial_execution_truth("t", "r", request_collection=Mock(), truth_collection=Mock(), provider="caller", provider_execution_reference="caller-ref", execution_status=PlatformExecutionStatus.EXECUTED, executed_at=datetime.now(timezone.utc), provider_evidence_reference="caller-evidence", created_at=datetime.now(timezone.utc))
# WILSY OS SOVEREIGN ARTIFACT STRUCTURE
# TITLE: M11E2D3R4 Obsolete Platform Execution Recorder Certificate
# VERSION: v1.0.0-M11E2D3R4
# AUTHORITY: Wilsy OS Core Governance / Kennel EOS
# PURPOSE: Durable, tenant-scoped platform execution and settlement evidence.
# EPITOME: Canonical platform financial truth without provider execution or money movement.
# ABSOLUTE CANONICAL PATH: tests/unit/test_platform_billing_financial_execution_truth_recording.py
# COLLABORATION / OWNERSHIP: Kennel EOS platform financial domain; R3F0 certificates.
# CERTIFICATION / UPDATE DATE: 2026-09-07; direct fail-closed certificate.
# CHANGELOG: v1.0.0-M11E2D3R4 adds direct fail-closed authority proof.
# COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
# SECURITY / PRIVACY POSTURE: Tenant isolation; UUID synthetic tests; no raw secrets.
# TENANT BOUNDARY: Every read, write, replay, and certificate assertion is tenant-scoped.
# AUTHORITY BOUNDARY: Kennel EOS is exclusive financial execution authority.
# FINANCIAL AUTHORITY BOUNDARY: Evidence only; no provider call, settlement inference, or paid state.
# TRANSACTION BOUNDARY: Caller-owned Mongo session propagates through durable operations.
# FAIL-CLOSED DECLARATION: Invalid authority, provenance, persistence, or hydration fails closed.
# BEGIN SOVEREIGN HEADER SEAL
# END SOVEREIGN HEADER SEAL

# ARTIFACT: tests/unit/test_platform_billing_financial_execution_truth_recording.py
# VERSION: v1.0.0-M11E2D3R4
# AUTHORITY BOUNDARY: Certification evidence only.
# TENANT POSTURE: Tenant-scoped synthetic fixtures.
# FAIL-CLOSED POSTURE: Failures are surfaced; no skips.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
