"""Real-Mongo certification for authenticated PayShap evidence ingestion.

VERSION: v1.0.0-KENNEL-PAYSHAP-WEBHOOK-EVIDENCE-MONGO-CERT
"""
from __future__ import annotations
import hashlib,hmac,json,os
from datetime import datetime,timezone
from typing import Generator
from uuid import uuid4
import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from tools.eos.kennel.evidence.payshap_evidence_store import PayShapEvidenceRegistry,PayShapEvidenceReplayConflictError,PayShapEvidenceCorruptionError
from tools.eos.kennel.evidence.payshap_webhook_ingestion import ingest_webhook,PayShapWebhookError

def sign(p:dict,secret="secret")->str:return hmac.new(secret.encode(),json.dumps(p,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode(),hashlib.sha256).hexdigest()
@pytest.fixture()
def col()->Generator[Collection,None,None]:
 uri=os.environ.get("TEST_VENDOR_MONGO_URI")
 if not uri: raise RuntimeError("TEST_VENDOR_MONGO_URI required")
 c=MongoClient(uri,serverSelectionTimeoutMS=5000); db=c[f"payshap_evidence_{uuid4().hex}"]; x=db["kennel_payshap_provider_evidence"]; PayShapEvidenceRegistry.ensure_indexes(x)
 try: yield x
 finally: c.drop_database(db.name); c.close()
def payload(**kw:object)->dict:return {"event_id":"event-1","reference":"ref-1","status":"PENDING","amount":"10.00","currency":"ZAR","tenant_id":"tenant-a",**kw}
def test_valid_and_exact_replay(col:Collection)->None:
 p=payload(); r=ingest_webhook(p,sign(p),"secret",col); q=ingest_webhook(p,sign(p),"secret",col); assert not r.is_replay and q.is_replay and r.evidence_id==q.evidence_id and col.count_documents({})==1
def test_authentication_fail_closed(col:Collection)->None:
 p=payload()
 for sig in ("", "bad", sign(p,"other")):
  with pytest.raises(PayShapWebhookError): ingest_webhook(p,sig,"secret",col)
def test_divergent_event_replay_rejected(col:Collection)->None:
 p=payload(); ingest_webhook(p,sign(p),"secret",col); q=payload(status="ACCEPTED")
 with pytest.raises(PayShapEvidenceReplayConflictError): ingest_webhook(q,sign(q),"secret",col)
def test_status_amount_currency_and_timestamp(col:Collection)->None:
 p=payload(status="ACCEPTED",provider_timestamp=datetime(2026,1,1,tzinfo=timezone.utc).isoformat(),amount="10.50"); r=ingest_webhook(p,sign(p),"secret",col); row=col.find_one({}); assert r.provider_status.value=="ACCEPTED" and row is not None and row["amount_minor"]==1050
def test_unknown_paid_not_settled(col:Collection)->None:
 p=payload(status="PAID"); r=ingest_webhook(p,sign(p),"secret",col); assert r.provider_status.value=="UNKNOWN"
def test_tenant_scoping(col:Collection)->None:
 p=payload(); ingest_webhook(p,sign(p),"secret",col); q=payload(tenant_id="tenant-b"); r=ingest_webhook(q,sign(q),"secret",col); assert r.tenant_id=="tenant-b" and col.count_documents({})==2
def test_malformed_inputs_rejected(col:Collection)->None:
 for p in (payload(amount="bad"),payload(currency="US"),payload(provider_timestamp="bad")):
  with pytest.raises(PayShapWebhookError): ingest_webhook(p,sign(p),"secret",col)
def test_caller_owned_transaction(col:Collection)->None:
 client=col.database.client; p=payload()
 with client.start_session() as s:
  s.start_transaction(); ingest_webhook(p,sign(p),"secret",col,session=s); assert col.count_documents({},session=s)==1; s.abort_transaction()
 assert col.count_documents({})==0
def test_corruption_fails_closed(col:Collection)->None:
 p=payload(); ingest_webhook(p,sign(p),"secret",col); col.update_one({}, {"$set":{"provider_status":"BROKEN"}})
 with pytest.raises(PayShapEvidenceCorruptionError): PayShapEvidenceRegistry.get("tenant-a","event-1",col)

# ARTIFACT: test_payshap_webhook_evidence_mongo.py
# VERSION: v1.0.0-KENNEL-PAYSHAP-WEBHOOK-EVIDENCE-MONGO-CERT
# END OF WILSY OS SOVEREIGN ARTIFACT
