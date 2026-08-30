"""WILSY OS Node/Python Internal Service Trust Interoperability Certification.
TITLE: WILSY OS Node/Python Trust Interoperability
VERSION: v1.0.0-WILSY-NODE-PYTHON-INTEROP
AUTHORITY: Python-owned cross-language certification.
"""
import base64, copy, json, subprocess, hashlib, os
from tools.eos.auth.internal_service_trust import verify_internal_service_request

class Store:
    def __init__(self): self.seen=set()
    def consume_once(self, *, service_id, key_id, nonce, expires_at):
        k=(service_id,key_id,nonce)
        if k in self.seen: return False
        self.seen.add(k); return True

NODE="""import('./server/services/pythonAuthorityTransport.js').then(m=>{const x=JSON.parse(process.argv[1]);const v=m.signServiceAssertion({...x,body:Buffer.from(x.body,'base64')});console.log(JSON.stringify({...v,body:v.body.toString('base64')}))})"""
def node_vector(body, path='/internal/authority?q=1', correlation='corr-1'):
    x={'body':base64.b64encode(body).decode(),'timestamp':1700000000,'nonce':'0123456789abcdef0123456789abcdef','service_id':'node-express-api','audience':'python-eos-authority','key_id':'test-k1','secret':'synthetic-test-secret','method':'POST','path':path,'correlation_id':correlation}
    result=json.loads(subprocess.check_output(['node','--input-type=module','-e',NODE,json.dumps(x)])); result['test_path']=path; return result

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

def test_internal_config_fails_closed_and_ignores_jwt_fallbacks():
    script="""import('./server/services/pythonAuthorityTransport.js').then(m=>{try{console.log(JSON.stringify(m.resolveInternalAuthConfig(JSON.parse(process.argv[1]))))}catch(e){console.log(JSON.stringify({error:e.message}))}})"""
    base={'JWT_SECRET':'fake-jwt','WILSY_JWT_SECRET':'fake-wilsy'}
    for missing in ('WILSY_INTERNAL_AUTH_SERVICE_ID','WILSY_INTERNAL_AUTH_AUDIENCE','WILSY_INTERNAL_AUTH_KEY_ID','WILSY_INTERNAL_AUTH_SECRET'):
        env={**base,'WILSY_INTERNAL_AUTH_SERVICE_ID':'s','WILSY_INTERNAL_AUTH_AUDIENCE':'a','WILSY_INTERNAL_AUTH_KEY_ID':'k','WILSY_INTERNAL_AUTH_SECRET':'secret'}; env.pop(missing)
        out=json.loads(subprocess.check_output(['node','--input-type=module','-e',script,json.dumps(env)])); assert 'error' in out
    env={**base,'WILSY_INTERNAL_AUTH_SERVICE_ID':'s','WILSY_INTERNAL_AUTH_AUDIENCE':'a','WILSY_INTERNAL_AUTH_KEY_ID':'k','WILSY_INTERNAL_AUTH_SECRET':'internal'}
    out=json.loads(subprocess.check_output(['node','--input-type=module','-e',script,json.dumps(env)])); assert out['service_id']=='s' and out['secret']=='internal'

# ARTIFACT: test_internal_service_trust_node_interop.py
# VERSION: v1.0.0-WILSY-NODE-PYTHON-INTEROP
# END OF WILSY OS SOVEREIGN ARTIFACT
