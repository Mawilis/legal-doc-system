"""TITLE: Platform Billing Financial Execution Truth Recording
VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
AUTHORITY: Kennel EOS / Wilsy OS Core Governance
EPITOME: Trusted R3D-to-platform execution evidence boundary.
ABSOLUTE CANONICAL PATH: tools/eos/kennel/orchestration/platform_billing_financial_execution_truth_recording.py
"""
from __future__ import annotations
from datetime import datetime
from typing import Optional
from pymongo.collection import Collection
from pymongo.client_session import ClientSession
from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import PlatformBillingFinancialExecutionRequestRegistry
from tools.eos.kennel.orchestration.platform_billing_financial_execution_command_issuance import issue_platform_billing_financial_execution_command
from tools.eos.kennel.domain.platform_billing_financial_execution_truth import PlatformBillingFinancialExecutionTruth, PlatformExecutionStatus
from tools.eos.kennel.registry.platform_billing_financial_execution_truth_registry import PlatformBillingFinancialExecutionTruthRegistry

def record_platform_billing_financial_execution_truth(tenant_id:str, execution_request_id:str, *, request_collection:Collection, truth_collection:Collection, provider:str, provider_execution_reference:str, execution_status:PlatformExecutionStatus, executed_at:datetime|None, provider_evidence_reference:str, created_at:datetime, session:Optional[ClientSession]=None)->PlatformBillingFinancialExecutionTruth:
    """Hydrate durable R3D and reconstruct R3E internally before persistence."""
    request=PlatformBillingFinancialExecutionRequestRegistry.get(tenant_id,execution_request_id,request_collection,session=session)
    command=issue_platform_billing_financial_execution_command(tenant_id,execution_request_id,collection=request_collection,issued_at=created_at)
    truth=PlatformBillingFinancialExecutionTruth.from_command(command,provider=provider,provider_execution_reference=provider_execution_reference,execution_status=execution_status,executed_at=executed_at,provider_evidence_reference=provider_evidence_reference,created_at=created_at)
    return PlatformBillingFinancialExecutionTruthRegistry.create(truth,truth_collection,session=session)

# ARTIFACT: platform_billing_financial_execution_truth_recording.py
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY BOUNDARY: Kennel platform execution evidence only; no settlement.
# END OF WILSY OS SOVEREIGN ARTIFACT
# WILSY OS SOVEREIGN ARTIFACT STRUCTURE
# TITLE: R3F0 Platform Billing Financial Execution Truth and Settlement Evidence
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY: Wilsy OS Core Governance / Kennel EOS
# PURPOSE: Durable, tenant-scoped platform execution and settlement evidence.
# EPITOME: Canonical platform financial truth without provider execution or money movement.
# ABSOLUTE CANONICAL PATH: tools/eos/kennel/orchestration/platform_billing_financial_execution_truth_recording.py
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

# ARTIFACT: tools/eos/kennel/orchestration/platform_billing_financial_execution_truth_recording.py
# VERSION: v1.1.0-R3F0-STRUCTURAL-REMEDIATION
# AUTHORITY BOUNDARY: Certification evidence only.
# TENANT POSTURE: Tenant-scoped synthetic fixtures.
# FAIL-CLOSED POSTURE: Failures are surfaced; no skips.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
