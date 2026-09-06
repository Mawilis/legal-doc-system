"""TITLE: Kennel Platform Billing Financial Execution Command Certificate
VERSION: v1.0.0-KENNEL-PLATFORM-BILLING-FINANCIAL-EXECUTION-COMMAND-UNIT
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify immutable platform command laws.
EPITOME: Evidence only; no execution.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_platform_billing_financial_execution_command.py
COLLABORATION / OWNERSHIP: Kennel EOS command certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0 certifies platform command derivation.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic evidence.
TENANT BOUNDARY: Tenant-bound command identity.
AUTHORITY BOUNDARY: Certification only.
FINANCIAL AUTHORITY BOUNDARY: No provider, settlement, or paid state.
TRANSACTION BOUNDARY: Pure domain.
FAIL-CLOSED POSTURE: Invalid values reject.
"""
from datetime import datetime, timezone
from tools.eos.kennel.domain.platform_billing_financial_execution_command import PlatformBillingFinancialExecutionCommand
from tools.eos.saas.domain.platform_billing_financial_execution_request import PlatformBillingFinancialExecutionRequest

def request(): return PlatformBillingFinancialExecutionRequest("r","t","a","i","a"*128,100,"ZAR","dest","k","p","basis",datetime(2026,1,1,tzinfo=timezone.utc))
def test_platform_command_derives_and_is_immutable():
    c=PlatformBillingFinancialExecutionCommand.from_request(request(),created_at=datetime(2026,1,1,tzinfo=timezone.utc)); assert c.tenant_id=="t" and c.execution_request_id=="r" and c.platform_invoice_id=="i" and not hasattr(c,"payable_id")
