"""TITLE: Commercial Statement Engine Certificate
VERSION: v1.0.0-M7
AUTHORITY: Wilsy OS Core Governance
EPITOME: Deterministic statement arithmetic certificate.
ABSOLUTE CANONICAL PATH: tests/unit/test_commercial_statement_engine.py
COLLABORATION / OWNERSHIP: SaaS Billing statement certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M7 adds engine certificate.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No secrets.
TENANT BOUNDARY: Explicit tenant/account filters.
AUTHORITY BOUNDARY: Commercial evidence projection only.
FINANCIAL AUTHORITY BOUNDARY: No settlement creation.
TRANSACTION BOUNDARY: Read-only.
FAIL-CLOSED DECLARATION: Mixed currency rejects.
"""
from datetime import datetime,timezone
import pytest
from tools.eos.saas.billing.commercial_statement_engine import build_statement,CommercialStatementError,invoice_activity,generate_commercial_statement
from tools.eos.saas.domain.billing import ClientInvoice
def _aged(days):
 as_of=datetime(2026,2,1,tzinfo=timezone.utc); due=as_of.replace(day=1)-__import__('datetime').timedelta(days=days)
 return generate_commercial_statement(tenant_id='t',ledger_kind=StatementLedgerKind.CLIENT,family=StatementFamily.OPEN_ITEM,account_id='c',currency='ZAR',as_of=as_of,invoices=(ClientInvoice.from_dict({'tenant_id':'t','invoice_id':str(days),'customer_id':'c','status':'open','total':10.0,'amount':10.0,'outstanding_amount':10.0,'currency':'ZAR','line_items':[{'description':'x','amount':10.0}],'issued_at':due,'due_at':due}),))
@pytest.mark.parametrize('days,bucket',[(-1,'CURRENT'),(0,'CURRENT'),(1,'1_30'),(30,'1_30'),(31,'31_60'),(60,'31_60'),(61,'61_90'),(90,'61_90'),(91,'91_120'),(120,'91_120'),(121,'120_PLUS')])
def test_aging_boundaries(days,bucket):
 s=_aged(days); assert s.aging is not None; assert s.aging[bucket]==1000 and sum(s.aging.values())==1000 and sum(v>0 for v in s.aging.values())==1
from tools.eos.saas.domain.commercial_statement import *
def test_balance_and_ordering():
 t=datetime(2026,1,1,tzinfo=timezone.utc); a=(CommercialStatementActivity('t',StatementLedgerKind.PLATFORM,'p','b','invoice',t,'ZAR',-20,StatementActivityKind.SETTLEMENT),CommercialStatementActivity('t',StatementLedgerKind.PLATFORM,'p','a','invoice',t,'ZAR',100,StatementActivityKind.INVOICE_CHARGE)); s=build_statement(tenant_id='t',ledger_kind=StatementLedgerKind.PLATFORM,family=StatementFamily.BALANCE_FORWARD,account_id='p',currency='ZAR',as_of=t,activities=a); assert s.closing_balance_minor==80 and [x.source_id for x in s.activities]==['a','b']
def test_mixed_currency_rejected():
 t=datetime(2026,1,1,tzinfo=timezone.utc); a=CommercialStatementActivity('t',StatementLedgerKind.CLIENT,'c','a','invoice',t,'ZAR',1,StatementActivityKind.INVOICE_CHARGE); b=CommercialStatementActivity('t',StatementLedgerKind.CLIENT,'c','b','invoice',t,'USD',1,StatementActivityKind.INVOICE_CHARGE)
 with pytest.raises(CommercialStatementError): build_statement(tenant_id='t',ledger_kind=StatementLedgerKind.CLIENT,family=StatementFamily.TRANSACTION,account_id='c',currency='ZAR',as_of=t,activities=(a,b))
def test_cross_lane_source_rejected():
 t=datetime(2026,1,1,tzinfo=timezone.utc)
 with pytest.raises(CommercialStatementError, match='M7_PLATFORM_SOURCE_REQUIRED'):
  invoice_activity(object(),ledger_kind=StatementLedgerKind.PLATFORM,account_id='p',effective_at=t)
 with pytest.raises(CommercialStatementError, match='M7_CLIENT_SOURCE_REQUIRED'):
  invoice_activity(object(),ledger_kind=StatementLedgerKind.CLIENT,account_id='c',effective_at=t)
# ARTIFACT: test_commercial_statement_engine.py
# VERSION: v1.0.0-M7
# END OF WILSY OS SOVEREIGN ARTIFACT
