"""WILSY OS M11E1 receivable-to-statement certificate.
TITLE: Commercial Receivable Statement Integration Certificate
VERSION: v1.0.0-M11E1
AUTHORITY: Wilsy OS Core Governance
EPITOME: Certifies integer open-item projection from canonical receivable truth.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_commercial_receivable_statement_integration.py
COLLABORATION / OWNERSHIP: M11E1 statement integration owner.
CERTIFICATION / UPDATE DATE: 2026-09-07
CHANGELOG: v1.0.0-M11E1 establishes receivable-native statement entrypoint.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers only.
TENANT BOUNDARY: Statement and receivable tenant must match.
AUTHORITY BOUNDARY: Read-only statement projection.
FINANCIAL AUTHORITY BOUNDARY: No payment, settlement, or execution.
TRANSACTION BOUNDARY: Pure unit test.
FAIL-CLOSED DECLARATION: Mixed family and statement scope reject.
"""
from datetime import datetime, timezone
import pytest
from tools.eos.saas.domain.commercial_receivable import CommercialReceivable, ReceivableFamily, ReceivableStatus
from tools.eos.saas.domain.commercial_statement import StatementFamily, StatementLedgerKind, StatementActivityKind
from tools.eos.saas.billing.commercial_statement_engine import generate_receivable_commercial_statement, CommercialStatementError
def r(f): return CommercialReceivable('t',f,'r','i','ZAR',1000,0,275,'a'*128,ReceivableStatus.OPEN)
def test_platform_and_client_open_items_preserve_integer_balance():
 now=datetime(2026,1,1,tzinfo=timezone.utc)
 for f,l in ((ReceivableFamily.PLATFORM,StatementLedgerKind.PLATFORM),(ReceivableFamily.CLIENT,StatementLedgerKind.CLIENT)):
  s=generate_receivable_commercial_statement(tenant_id='t',ledger_kind=l,family=StatementFamily.OPEN_ITEM,account_id='acct',currency='ZAR',as_of=now,receivables=(r(f),)); assert s.activities[0].amount_minor==275 and s.activities[0].kind is StatementActivityKind.RECEIVABLE_BALANCE
def test_cross_lane_and_family_reject():
 with pytest.raises(CommercialStatementError): generate_receivable_commercial_statement(tenant_id='t',ledger_kind=StatementLedgerKind.CLIENT,family=StatementFamily.OPEN_ITEM,account_id='acct',currency='ZAR',as_of=datetime(2026,1,1,tzinfo=timezone.utc),receivables=(r(ReceivableFamily.PLATFORM),))
# ARTIFACT: test_commercial_receivable_statement_integration.py
# VERSION: v1.0.0-M11E1
# AUTHORITY BOUNDARY: Read-only statement projection.
# TENANT POSTURE: Explicit tenant scope.
# FAIL-CLOSED POSTURE: Cross-lane inputs reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
