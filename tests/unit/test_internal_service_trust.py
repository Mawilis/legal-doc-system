"""WILSY OS Internal Service Trust Unit Certification
VERSION: v1.0.0-WILSY-INTERNAL-SERVICE-TRUST
AUTHORITY: Certifies Python internal-service trust cryptographic semantics only.
ABSOLUTE CANONICAL PATH: /Users/wilsonkhanyezi/legal-doc-system/tests/unit/test_internal_service_trust.py
"""
import hashlib, hmac
import pytest
from tools.eos.auth.internal_service_trust import *

class Store:
    def __init__(self): self.seen = set()
    def consume_once(self, *, service_id, key_id, nonce, expires_at):
        key = (service_id, key_id, nonce)
        if key in self.seen: return False
        self.seen.add(key); return True

def make():
    body = b'{"ok":true}'
    req = {"version":"v1","service_id":"node-express-api","audience":"python-eos-authority","key_id":"test-k1","method":"POST","path":"/internal/authority","timestamp":"1700000000","nonce":"0123456789abcdef0123456789abcdef","body_sha3_512":body_sha3_512(body),"correlation_id":"corr-1"}
    raw = canonical_request(version=req["version"], service_id=req["service_id"], audience=req["audience"], method=req["method"], path=req["path"], timestamp=req["timestamp"], nonce=req["nonce"], body_sha3_512_value=req["body_sha3_512"], correlation_id=req["correlation_id"])
    req["signature"] = hmac.new(b"synthetic-test-secret", raw, hashlib.sha256).hexdigest()
    return req, body

def test_valid_and_replay():
    req, body = make(); store = Store()
    result = verify_internal_service_request(request=req, body=body, keys={"test-k1": ("node-express-api", "synthetic-test-secret")}, replay_store=store, now=1700000000)
    assert result.service_id == "node-express-api" and result.protocol_version == "v1"
    with pytest.raises(InternalServiceTrustReplayError): verify_internal_service_request(request=req, body=body, keys={"test-k1": ("node-express-api", "synthetic-test-secret")}, replay_store=store, now=1700000000)

@pytest.mark.parametrize("field,value", [("audience","wrong"),("service_id","wrong"),("method","post"),("nonce","A"*32),("path","https://bad")])
def test_tamper_fails(field, value):
    req, body = make(); req[field] = value
    with pytest.raises(InternalServiceTrustError): verify_internal_service_request(request=req, body=body, keys={"test-k1": ("node-express-api", "synthetic-test-secret")}, replay_store=Store(), now=1700000000)

def test_empty_body_digest_and_missing_store():
    assert body_sha3_512(b"") == hashlib.sha3_512(b"").hexdigest()
    req, body = make()
    with pytest.raises(InternalServiceTrustConfigurationError): verify_internal_service_request(request=req, body=body, keys={"test-k1": ("node-express-api", "synthetic-test-secret")}, replay_store=None, now=1700000000)

@pytest.mark.parametrize("field,value", [
    ("nonce", "a" * 31), ("nonce", "g" * 32), ("nonce", "A" * 32),
    ("body_sha3_512", "A" * 128), ("body_sha3_512", "a" * 127), ("body_sha3_512", "g" * 128),
    ("signature", "A" * 64), ("signature", "a" * 63), ("signature", "g" * 64),
])
def test_shape_negatives(field, value):
    req, body = make(); req[field] = value
    with pytest.raises(InternalServiceTrustError): verify_internal_service_request(request=req, body=body, keys={"test-k1": ("node-express-api", "synthetic-test-secret")}, replay_store=Store(), now=1700000000)

@pytest.mark.parametrize("field", ["version", "service_id", "audience", "key_id", "method", "path", "timestamp", "nonce", "body_sha3_512", "correlation_id"])
@pytest.mark.parametrize("newline", ["\n", "\r"])
def test_newline_injection_rejected(field, newline):
    req, body = make(); req[field] = req[field] + newline + "x"
    with pytest.raises(InternalServiceTrustError): verify_internal_service_request(request=req, body=body, keys={"test-k1": ("node-express-api", "synthetic-test-secret")}, replay_store=Store(), now=1700000000)

def test_freshness_boundaries_and_versions():
    req, body = make()
    keys = {"test-k1": ("node-express-api", "synthetic-test-secret"), "test-k0": ("node-express-api", "synthetic-test-secret")}
    assert verify_internal_service_request(request=req, body=body, keys=keys, replay_store=Store(), now=1700000030).protocol_version == "v1"
    req2, body2 = make(); req2["timestamp"] = "1700000031"
    raw2 = canonical_request(version=req2["version"], service_id=req2["service_id"], audience=req2["audience"], method=req2["method"], path=req2["path"], timestamp=req2["timestamp"], nonce=req2["nonce"], body_sha3_512_value=req2["body_sha3_512"], correlation_id=req2["correlation_id"])
    req2["signature"] = hmac.new(b"synthetic-test-secret", raw2, hashlib.sha256).hexdigest()
    with pytest.raises(InternalServiceTrustFreshnessError): verify_internal_service_request(request=req2, body=body2, keys=keys, replay_store=Store(), now=1700000000)
    req3, body3 = make(); req3["timestamp"] = "1699999969"
    raw3 = canonical_request(version=req3["version"], service_id=req3["service_id"], audience=req3["audience"], method=req3["method"], path=req3["path"], timestamp=req3["timestamp"], nonce=req3["nonce"], body_sha3_512_value=req3["body_sha3_512"], correlation_id=req3["correlation_id"])
    req3["signature"] = hmac.new(b"synthetic-test-secret", raw3, hashlib.sha256).hexdigest()
    with pytest.raises(InternalServiceTrustFreshnessError): verify_internal_service_request(request=req3, body=body3, keys=keys, replay_store=Store(), now=1700000000)
    req4, body4 = make(); req4["version"] = "v2"
    with pytest.raises(InternalServiceTrustMalformedRequestError): verify_internal_service_request(request=req4, body=body4, keys=keys, replay_store=Store(), now=1700000000)

def test_rotation_and_configuration_fail_closed():
    req, body = make(); previous = hmac.new(b"synthetic-test-secret", canonical_request(version=req["version"], service_id=req["service_id"], audience=req["audience"], method=req["method"], path=req["path"], timestamp=req["timestamp"], nonce=req["nonce"], body_sha3_512_value=req["body_sha3_512"], correlation_id=req["correlation_id"]), hashlib.sha256).hexdigest(); req["key_id"] = "test-k0"; req["signature"] = previous
    with pytest.raises(InternalServiceTrustConfigurationError): verify_internal_service_request(request=req, body=body, keys={}, replay_store=Store(), now=1700000000)
    with pytest.raises(InternalServiceTrustConfigurationError): verify_internal_service_request(request=req, body=body, keys={"retired": ("node-express-api", "synthetic-test-secret")}, replay_store=Store(), now=1700000000)
    with pytest.raises(InternalServiceTrustAuthenticationError): verify_internal_service_request(request=req, body=body, keys={"test-k0": ("node-express-api", "")}, replay_store=Store(), now=1700000000)

def test_result_and_errors_are_minimal():
    req, body = make(); result = verify_internal_service_request(request=req, body=body, keys={"test-k1": ("node-express-api", "synthetic-test-secret")}, replay_store=Store(), now=1700000000)
    assert set(result.__dataclass_fields__) == {"service_id", "audience", "key_id", "correlation_id", "verified_at", "protocol_version"}
    assert not hasattr(result, "roles") and not hasattr(result, "tenant_id")
    req["signature"] = "bad"
    with pytest.raises(InternalServiceTrustError) as caught: verify_internal_service_request(request=req, body=body, keys={"test-k1": ("node-express-api", "SYNTHETIC_SECRET_DO_NOT_LEAK_9A7C")}, replay_store=Store(), now=1700000000)
    assert "SYNTHETIC_SECRET_DO_NOT_LEAK_9A7C" not in str(caught.value) and "bad" not in str(caught.value)

# ARTIFACT: test_internal_service_trust.py
# VERSION: v1.0.0-WILSY-INTERNAL-SERVICE-TRUST
# AUTHORITY BOUNDARY: Unit certification only; no user authorization.
# TENANT POSTURE: No tenant membership authority.
# FAIL-CLOSED POSTURE: Invalid trust input denies.
# FINANCIAL EXECUTION AUTHORITY: Kennel EOS remains exclusive.
# END OF WILSY OS SOVEREIGN ARTIFACT
