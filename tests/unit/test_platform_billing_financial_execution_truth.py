"""TITLE: Platform execution truth certificate. VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION."""
from datetime import datetime, timezone
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import *
from tools.eos.kennel.domain.platform_billing_financial_execution_command import PlatformBillingFinancialExecutionCommand
def test_platform_truth_excludes_payable_and_preserves_platform_fields():
 c=PlatformBillingFinancialExecutionCommand('t','c','r','a','i','a'*128,100,'ZAR','dest','k','p','basis',datetime(2026,1,1,tzinfo=timezone.utc)); v=PlatformBillingFinancialExecutionTruth.from_command(c,provider='P',provider_execution_reference='x',execution_status=PlatformExecutionStatus.EXECUTED,executed_at=datetime(2026,1,1,tzinfo=timezone.utc),provider_evidence_reference='e',created_at=datetime(2026,1,1,tzinfo=timezone.utc)); assert v.platform_invoice_id=='i' and not hasattr(v,'payable_id')
# WILSY OS SOVEREIGN ARTIFACT STRUCTURE
# TITLE: R3F0 Platform Billing Financial Execution Truth and Settlement Evidence
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY: Wilsy OS Core Governance / Kennel EOS
# PURPOSE: Durable, tenant-scoped platform execution and settlement evidence.
# EPITOME: Canonical platform financial truth without provider execution or money movement.
# ABSOLUTE CANONICAL PATH: tests/unit/test_platform_billing_financial_execution_truth.py
# COLLABORATION / OWNERSHIP: Kennel EOS platform financial domain; R3F0 certificates.
# CERTIFICATION / UPDATE DATE: 2026-09-06; structural remediation.
# CHANGELOG: v1.1.0-R3F0-STRUCTURAL-REMEDIATION complete sovereign metadata alignment.
# COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
# SECURITY / PRIVACY POSTURE: Tenant isolation; UUID synthetic tests; no raw secrets.
# TENANT BOUNDARY: Every read, write, replay, and certificate assertion is tenant-scoped.
# AUTHORITY BOUNDARY: Kennel EOS is exclusive financial execution authority.
# FINANCIAL AUTHORITY BOUNDARY: Evidence only; no provider call, settlement inference, or paid state.
# TRANSACTION BOUNDARY: Caller-owned Mongo session propagates through durable operations.
# FAIL-CLOSED DECLARATION: Invalid authority, provenance, persistence, or hydration fails closed.
# BEGIN SOVEREIGN HEADER SEAL
# END SOVEREIGN HEADER SEAL

# ARTIFACT: tests/unit/test_platform_billing_financial_execution_truth.py
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY BOUNDARY: Certification evidence only.
# TENANT POSTURE: Tenant-scoped synthetic fixtures.
# FAIL-CLOSED POSTURE: Failures are surfaced; no skips.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT

# ARTIFACT: tests/unit/test_platform_billing_financial_execution_truth.py
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY BOUNDARY: Certification evidence only.
# TENANT POSTURE: Tenant-scoped synthetic fixtures.
# FAIL-CLOSED POSTURE: Assertion failures are surfaced; no skips.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
