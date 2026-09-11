"""TITLE: Platform Billing Financial Execution Command Issuance
VERSION: v1.0.0-KENNEL-PLATFORM-BILLING-FINANCIAL-EXECUTION-COMMAND-ISSUANCE
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Hydrate durable R3D and issue one Kennel platform command.
EPITOME: Trusted ingress; no provider transport or settlement.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tools/eos/kennel/orchestration/platform_billing_financial_execution_command_issuance.py
COLLABORATION / OWNERSHIP: Kennel EOS platform ingress owner.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 establishes durable R3D-to-command conversion.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No caller-supplied economic authority.
TENANT BOUNDARY: Registry hydration binds tenant and request identifiers.
AUTHORITY BOUNDARY: Durable R3D is the sole source of authority.
FINANCIAL AUTHORITY BOUNDARY: Command creation only; Kennel executes later.
TRANSACTION BOUNDARY: Pure issuance; no persistence or transaction lifecycle.
FAIL-CLOSED POSTURE: Missing or corrupt R3D aborts issuance.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any
from pymongo.collection import Collection
from tools.eos.saas.billing.platform_billing_financial_execution_request_registry import PlatformBillingFinancialExecutionRequestRegistry
from tools.eos.kennel.domain.platform_billing_financial_execution_command import PlatformBillingFinancialExecutionCommand

def issue_platform_billing_financial_execution_command(tenant_id: str, execution_request_id: str, *, collection: Collection, issued_at: datetime) -> PlatformBillingFinancialExecutionCommand:
    request = PlatformBillingFinancialExecutionRequestRegistry.get(tenant_id, execution_request_id, collection)
    return PlatformBillingFinancialExecutionCommand.from_request(request, created_at=issued_at.astimezone(timezone.utc))

# ARTIFACT: platform_billing_financial_execution_command_issuance.py
# VERSION: v1.0.0-KENNEL-PLATFORM-BILLING-FINANCIAL-EXECUTION-COMMAND-ISSUANCE
# AUTHORITY BOUNDARY: Durable R3D-derived command only; no execution.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
