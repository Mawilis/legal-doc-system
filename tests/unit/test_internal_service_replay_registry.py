"""WILSY OS Internal Service Replay Registry Unit Certification
VERSION: v1.0.0-WILSY-INTERNAL-SERVICE-REPLAY
"""
from datetime import datetime, timezone
import pytest
from pymongo.errors import DuplicateKeyError, PyMongoError
from tools.eos.auth.internal_service_replay_registry import *

class C:
    def __init__(self, error=None): self.calls=[]; self.error=error
    def create_index(self, *a, **k): self.calls.append((a,k)); return k.get('name')
    def insert_one(self, d):
        self.calls.append(('insert',d))
        if self.error: raise self.error

def test_insert_document_and_duplicate():
    c=C(); r=InternalServiceReplayRegistry(c, now=datetime(2026,1,1,tzinfo=timezone.utc)); assert r.consume_once(service_id='s',key_id='k',nonce='n',expires_at=1700000000) is True; assert isinstance(c.calls[-1][1]['expires_at'],datetime); assert set(c.calls[-1][1])=={'service_id','key_id','nonce','expires_at','created_at'}  # type: ignore[arg-type]
    c.error=DuplicateKeyError('duplicate'); assert r.consume_once(service_id='s',key_id='k',nonce='n',expires_at=1700000000) is False

def test_infrastructure_and_input_fail_closed():
    with pytest.raises(ReplayRegistryError): InternalServiceReplayRegistry(C(PyMongoError('down'))).consume_once(service_id='s',key_id='k',nonce='n',expires_at=1)  # type: ignore[arg-type]
    with pytest.raises(ReplayRegistryConfigurationError): InternalServiceReplayRegistry(C()).consume_once(service_id='',key_id='k',nonce='n',expires_at=1)  # type: ignore[arg-type]

def test_indexes_exact():
    c=C(); InternalServiceReplayRegistry.ensure_indexes(c); assert c.calls[0][1]['name']=='internal_service_replay_identity_unique' and c.calls[0][1]['unique'] is True; assert c.calls[1][1]['name']=='internal_service_replay_expiry_ttl' and c.calls[1][1]['expireAfterSeconds']==0  # type: ignore[arg-type]

# ARTIFACT: test_internal_service_replay_registry.py
# VERSION: v1.0.0-WILSY-INTERNAL-SERVICE-REPLAY
# END OF WILSY OS SOVEREIGN ARTIFACT
