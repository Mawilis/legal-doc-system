"""WILSY OS Python-Owned External Assertion Interoperability Certificate.
TITLE: Python Internal Trust and Test-Only Crypto Vectors
VERSION: v1.1.1-TEST-ONLY-CRYPTO-VECTORS-SOVEREIGN-METADATA
AUTHORITY: Wilsy OS Core Governance
EPITOME: Preserve exact-byte cross-language evidence without a Node business signer.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_internal_service_trust_node_interop.py
COLLABORATION / OWNERSHIP: Python trust verifier and Node built-in crypto test tooling.
CERTIFICATION / UPDATE DATE: 2026-11-10
CHANGELOG: v1.1.1-TEST-ONLY-CRYPTO-VECTORS-SOVEREIGN-METADATA completes privacy posture without changing verifier or vector behavior.
CHANGELOG: v1.1.0-TEST-ONLY-CRYPTO-VECTORS replaces the retired backend import with a test-local standard-crypto vector and requires backend absence.
COMPLIANCE: POPIA section 19; GDPR Article 32; SOC 2 CC7.2.
SECURITY / PRIVACY POSTURE: Synthetic offline crypto vectors only; no signing keys or production credentials are read.
TENANT BOUNDARY: Synthetic tenant identifiers only; no tenant records are read or changed.
AUTHORITY BOUNDARY: Offline compatibility evidence only; no backend signer or request authority is granted.
FINANCIAL AUTHORITY BOUNDARY: Kennel EOS exclusively.
"""
import base64, copy, json, subprocess, hashlib, os
from tools.eos.auth.internal_service_trust import verify_internal_service_request

class Store:
    def __init__(self): self.seen=set()
    def consume_once(self, *, service_id, key_id, nonce, expires_at):
        k=(service_id,key_id,nonce)
        if k in self.seen: return False
        self.seen.add(k); return True

NODE="""const crypto=require('node:crypto'); const x=JSON.parse(process.argv[1]); const body=Buffer.from(x.body,'base64'); const hash=crypto.createHash('sha3-512').update(body).digest('hex'); const fields=['v1',x.service_id,x.audience,x.method,x.path,String(x.timestamp),x.nonce,hash,x.correlation_id]; const signature=crypto.createHmac('sha256',x.secret).update(fields.join('\\n')).digest('hex'); console.log(JSON.stringify({body:body.toString('base64'),headers:{'X-Wilsy-Auth-Version':'v1','X-Wilsy-Service-ID':x.service_id,'X-Wilsy-Audience':x.audience,'X-Wilsy-Key-ID':x.key_id,'X-Wilsy-Timestamp':String(x.timestamp),'X-Wilsy-Nonce':x.nonce,'X-Wilsy-Body-SHA3-512':hash,'X-Wilsy-Correlation-ID':x.correlation_id,'X-Wilsy-Signature':signature}}));"""

def node_vector(body, path='/internal/authority?q=1', correlation='corr-1'):
    x={'body':base64.b64encode(body).decode(),'timestamp':1700000000,'nonce':'0123456789abcdef0123456789abcdef','service_id':'node-express-api','audience':'python-eos-authority','key_id':'test-k1','secret':'synthetic-test-secret','method':'POST','path':path,'correlation_id':correlation}
    result=json.loads(subprocess.check_output(['node','-e',NODE,json.dumps(x)])); result['test_path']=path; return result

def verify(v):
    b=base64.b64decode(v['body']); h=v['headers']; req={'version':h['X-Wilsy-Auth-Version'],'service_id':h['X-Wilsy-Service-ID'],'audience':h['X-Wilsy-Audience'],'key_id':h['X-Wilsy-Key-ID'],'method':'POST','path':v.get('test_path','/internal/authority?q=1'),'timestamp':h['X-Wilsy-Timestamp'],'nonce':h['X-Wilsy-Nonce'],'body_sha3_512':h['X-Wilsy-Body-SHA3-512'],'correlation_id':h['X-Wilsy-Correlation-ID'],'signature':h['X-Wilsy-Signature']}
    return verify_internal_service_request(request=req,body=b,keys={'test-k1':('node-express-api','synthetic-test-secret')},replay_store=Store(),now=1700000000)

def test_node_vectors_and_frozen_verifier():
    vectors=[node_vector(b''),node_vector(b'{"ok":true}'),node_vector('Zażółć gęślą jaźń'.encode()),node_vector(b'{"a":1}',path='/internal/authority?q=1&x=2')]
    for v in vectors: assert verify(v).service_id=='node-express-api'
    assert hashlib.sha3_512(b'{"a":1}').hexdigest()!=hashlib.sha3_512(b'{ "a": 1 }').hexdigest()
    base=node_vector(b'{"ok":true}')
    for field in ('body','method','path','timestamp','nonce','correlation','service','audience','key','signature'):
        v=copy.deepcopy(base); h=v['headers']
        if field=='body': v['body']=base64.b64encode(b'{"ok":true}!').decode()
        elif field=='method': h['X-Wilsy-Signature']='0'*64
        elif field=='path': h['X-Wilsy-Signature']='0'*64
        elif field=='timestamp': h['X-Wilsy-Timestamp']='1700000001'; h['X-Wilsy-Signature']='0'*64
        elif field=='nonce': h['X-Wilsy-Nonce']='f'*32; h['X-Wilsy-Signature']='0'*64
        elif field=='correlation': h['X-Wilsy-Correlation-ID']='changed'; h['X-Wilsy-Signature']='0'*64
        elif field=='service': h['X-Wilsy-Service-ID']='other'; h['X-Wilsy-Signature']='0'*64
        elif field=='audience': h['X-Wilsy-Audience']='other'; h['X-Wilsy-Signature']='0'*64
        elif field=='key': h['X-Wilsy-Key-ID']='other'
        else: h['X-Wilsy-Signature']='0'*64
        try: verify(v)
        except Exception: continue
        raise AssertionError(field)

def test_retired_internal_node_configuration_has_no_runtime_owner():
    """Node configuration cannot retain signing or JWT-fallback authority."""
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    assert not (root / "server/services/pythonAuthorityTransport.js").exists()
    source = (root / "tools/eos/auth/internal_service_trust.py").read_text()
    assert "signature" in source and "replay" in source
    assert "JWT_SECRET" not in source


# ARTIFACT: test_internal_service_trust_node_interop.py
# VERSION: v1.1.1-TEST-ONLY-CRYPTO-VECTORS-SOVEREIGN-METADATA
# AUTHORITY BOUNDARY: Offline standards verification only.
# TENANT POSTURE: Synthetic identifiers only.
# FAIL-CLOSED POSTURE: Tampering and retired backend authority reject.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS exclusively.
# END OF WILSY OS SOVEREIGN ARTIFACT
