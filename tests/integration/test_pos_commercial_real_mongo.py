"""WILSY OS M9 durable POS certificate.
TITLE: Six-scenario durable POS certificate
VERSION: v1.0.0-M9
AUTHORITY: Wilsy OS Core Governance
PURPOSE: Certify six production M9 POS commercial graphs against governed real Mongo.
EPITOME: Tenant-scoped commercial persistence without payment execution.
ABSOLUTE CANONICAL PATH: tests/integration/test_pos_commercial_real_mongo.py
COLLABORATION / OWNERSHIP: Python EOS POS certification.
CERTIFICATION / UPDATE DATE: 2026-09-06
CHANGELOG: v1.0.0-M9 replaces shell scenarios with production registry paths.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic identifiers; no payment secrets.
TENANT BOUNDARY: Every query binds tenant and location.
AUTHORITY BOUNDARY: Commercial POS only; Kennel owns execution.
FINANCIAL AUTHORITY BOUNDARY: No paid, settled, provider, or execution truth.
TRANSACTION BOUNDARY: One certificate-owned client and explicit collections.
FAIL-CLOSED DECLARATION: Missing URI and corruption fail explicitly; no skips.
"""
import os, uuid
import pytest
from pymongo import MongoClient
from tools.eos.saas.domain.pos_commercial import POSLineItem, POSSale, POSStatus, POSTenderType
from tools.eos.saas.billing.pos_commercial_registry import POSSaleRegistry, POSRegistryError
from tools.eos.saas.billing.pos_commercial_orchestration import finalize_sale, create_return, create_refund_intent, record_cash_tender, create_tender_intent
URI=os.environ.get('TEST_VENDOR_MONGO_URI','').strip()
@pytest.fixture(scope='module')
def runtime():
 if not URI: raise RuntimeError('TEST_VENDOR_MONGO_URI is required')
 client=MongoClient(URI); client.admin.command('ping'); db=client[f'm9_pos_{uuid.uuid4().hex}']; col=db['sales']; POSSaleRegistry.ensure_indexes(col)
 yield client, col; client.close()
def sale(tenant='tenant-a', location='loc-a', sale_id=None, price=100): return POSSale(tenant,location,sale_id or f'sale-{uuid.uuid4().hex}','ZAR',(POSLineItem('p1','SKU-1','Widget',2,price,10,20,'ZAR'),),POSStatus.OPEN,f'idem-{uuid.uuid4().hex}')
def test_rm_pos01_canonical_sale(runtime):
 _, col=runtime; s=sale(); out=finalize_sale(s,col); hydrated=POSSaleRegistry.get(s.tenant_id,s.location_id,s.sale_id,col); assert out==hydrated and hydrated.total_minor==210 and hydrated.status is POSStatus.COMPLETED_COMMERCIAL
def test_rm_pos02_tenant_location_isolation(runtime):
 _, col=runtime; s=sale(); finalize_sale(s,col)
 with pytest.raises(POSRegistryError): POSSaleRegistry.get('other',s.location_id,s.sale_id,col)
 with pytest.raises(POSRegistryError): POSSaleRegistry.get(s.tenant_id,'other',s.sale_id,col)
 assert col.count_documents({'tenant_id':'other'})==0
def test_rm_pos03_identical_replay(runtime):
 _, col=runtime; s=sale(sale_id='replay',price=125); s=POSSale(s.tenant_id,s.location_id,s.sale_id,s.currency,s.lines,s.status,'fixed-idem'); a=finalize_sale(s,col); b=finalize_sale(s,col); assert a.fingerprint==b.fingerprint and col.count_documents({'sale_id':'replay'})==1
def test_rm_pos04_divergent_replay(runtime):
 _, col=runtime; s=sale(sale_id='conflict'); finalize_sale(s,col); divergent=POSSale(s.tenant_id,s.location_id,s.sale_id,s.currency,(POSLineItem('p1','SKU-1','Widget',2,999,0,0,'ZAR'),),POSStatus.OPEN,'idem-conflict')
 with pytest.raises(POSRegistryError): finalize_sale(divergent,col)
def test_rm_pos05_return_refund_intent(runtime):
 _, col=runtime; s=sale(sale_id='return'); persisted=finalize_sale(s,col); ret=create_return(persisted,'SKU-1',1,'customer-return','r1','ri'); refund=create_refund_intent(persisted,100,'returned SKU-1','f1','fi'); assert ret.tenant_id==refund.tenant_id==s.tenant_id and refund.amount_minor<=s.total_minor
 with pytest.raises(ValueError): create_return(persisted,'SKU-1',2,'too much','r2','ri2',(ret,))
def test_rm_pos06_cash_electronic_boundary(runtime):
 _, col=runtime; s=finalize_sale(sale(sale_id='tender'),col); cash=record_cash_tender(s,250,'operator','2026-09-06T00:00:00Z'); intent=create_tender_intent(s,POSTenderType.CARD,s.total_minor,'card-idem'); assert cash.change_due_minor==40 and intent.requested_amount_minor==s.total_minor; assert not hasattr(intent,'paid') and not hasattr(intent,'settled') and not hasattr(intent,'provider_success')
# ARTIFACT: test_pos_commercial_real_mongo.py
# VERSION: v1.0.0-M9
# AUTHORITY BOUNDARY: Commercial POS only.
# FAIL-CLOSED POSTURE: No execution or settlement fabrication.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
