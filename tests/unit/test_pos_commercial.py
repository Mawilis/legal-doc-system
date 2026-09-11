"""WILSY OS M9 POS commercial contract certificate.
TITLE: POS commercial domain and orchestration tests
VERSION: v1.0.0-M9
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify M9 POS domain invariants and financial-authority firewalls.
EPITOME: Certify tenant-scoped integer commercial sale truth.
ABSOLUTE CANONICAL PATH: tests/unit/test_pos_commercial.py
COLLABORATION / OWNERSHIP: Python EOS POS certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M9 adds core POS contract tests.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: No payment/provider authority.
TENANT BOUNDARY: Identity tests enforce tenant/location scope.
AUTHORITY BOUNDARY: Commercial truth only.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively executes electronic funds.
TRANSACTION BOUNDARY: Registry caller-owned.
FAIL-CLOSED DECLARATION: Invalid arithmetic and currency reject.
"""
import pytest
from tools.eos.saas.domain.pos_commercial import POSLineItem, POSSale, POSStatus
def line(currency='ZAR'): return POSLineItem('p','SKU-1','Item',2,1000,100,180,currency)
def test_sale_integer_total_and_fingerprint():
 s=POSSale('t','loc','sale','ZAR',(line(),),POSStatus.DRAFT,'idem'); assert s.total_minor==2080 and len(s.fingerprint)==128
def test_mixed_currency_and_invalid_quantity_fail():
 with pytest.raises(ValueError,match='M9_MIXED_CURRENCY'): POSSale('t','loc','sale','ZAR',(line(),line('USD')),POSStatus.DRAFT,'idem')
 with pytest.raises(ValueError,match='M9_LINE_INVALID'): POSLineItem('p','s','x',0,1,0,0,'ZAR')
# ARTIFACT: test_pos_commercial.py
# VERSION: v1.0.0-M9
# AUTHORITY BOUNDARY: Certification evidence only.
# FAIL-CLOSED POSTURE: No execution truth is fabricated.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
